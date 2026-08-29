import os
import time
import json
import tarfile
import logging
from io import BytesIO

import redis
from minio import Minio
from datasets import load_dataset
from transformers import (
	AutoTokenizer,
	AutoModelForTokenClassification,
	TrainingArguments,
	Trainer,
	DataCollatorForTokenClassification,
)
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")



REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
MINIO_HOST = os.getenv("MINIO_HOST", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
minio_client = Minio(
	MINIO_HOST.replace("http://", "").replace("https://", ""),
	access_key=MINIO_ACCESS_KEY,
	secret_key=MINIO_SECRET_KEY,
	secure=False,
)


def setup_logger(job_id: str):
	log_filename = f"training_{job_id}.log"
	logger = logging.getLogger(job_id)
	logger.setLevel(logging.INFO)
	fh = logging.FileHandler(log_filename)
	fh.setLevel(logging.INFO)
	formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
	fh.setFormatter(formatter)
	if not logger.handlers:
		logger.addHandler(fh)
	return logger, log_filename


def download_dataset_from_minio(bucket: str, object_name: str, local_path: str):
	try:
		response = minio_client.get_object(bucket, object_name)
	except Exception as e:
		raise

	with open(local_path, "wb") as f:
		for d in response.stream(32 * 1024):
			f.write(d)


def compress_dir_to_tar_gz(dir_path: str, tar_path: str):
	with tarfile.open(tar_path, "w:gz") as tar:
		tar.add(dir_path, arcname=os.path.basename(dir_path))


def process_and_train(job):
	task_id = job.get("task_id")
	dataset_id = job.get("dataset_id", "conll2003")
	base_model = job.get("model_name", "bert-base-cased")
	epochs = int(job.get("epochs", 1))
	batch_size = int(job.get("batch_size", 8))

	logger, log_filename = setup_logger(task_id)
	logger.info(f"Starting job {task_id} with dataset {dataset_id} and model {base_model}")

	# download dataset
	# Determine dataset source: MinIO object or HF dataset name
	train_ds = None
	# If dataset_id looks like a MinIO path or filename, try to download
	if dataset_id.startswith("datasets/") or dataset_id.endswith(".json"):
		# extract object name
		if dataset_id.startswith("datasets/"):
			bucket = "datasets"
			object_name = dataset_id.split("/", 1)[1]
		else:
			bucket = "datasets"
			object_name = dataset_id

		local_json = f"{object_name}"
		if not minio_client.bucket_exists(bucket):
			raise RuntimeError("datasets bucket does not exist")

		logger.info(f"Downloading {object_name} from bucket {bucket}")
		download_dataset_from_minio(bucket, object_name, local_json)
		ds = load_dataset("json", data_files={"train": local_json})
		train_ds = ds["train"]
	else:
		# try to load from Hugging Face by name
		try:
			logger.info(f"Loading dataset {dataset_id} from Hugging Face")
			ds = load_dataset(dataset_id)
			if "train" in ds:
				train_ds = ds["train"]
			else:
				# try use whole dataset
				train_ds = ds
		except Exception as e:
			logger.error(f"Failed to load dataset {dataset_id}: {e}")
			raise

	# determine labels
	# Determine number of labels. Prefer explicit feature names; otherwise infer from data.
	num_labels = 0
	if hasattr(train_ds, "features") and "ner_tags" in getattr(train_ds, "features", {}):
		try:
			names = train_ds.features["ner_tags"].feature.names
			num_labels = len(names)
		except Exception:
			# fallback to inferring from values below
			pass
	# If still unknown, scan dataset to find max label value
	if not num_labels or num_labels <= 0:
		max_label = -1
		for ex in train_ds:
			labels = None
			if isinstance(ex, dict):
				labels = ex.get("ner_tags")
			else:
				# try attribute access fallback
				labels = getattr(ex, "ner_tags", None)
			if labels is None:
				continue
			# labels may be list of ints or nested
			for item in labels:
				if isinstance(item, (list, tuple)):
					for v in item:
						if isinstance(v, int) and v > max_label:
							max_label = v
				elif isinstance(item, int):
					if item > max_label:
						max_label = item
		# set num_labels (use at least 2)
		if max_label >= 0:
			num_labels = max_label + 1
	if num_labels <= 0:
		num_labels = 2

	tokenizer = AutoTokenizer.from_pretrained(base_model)

	# simple tokenization function for token classification when tokens are provided as list
	def tokenize_and_align_labels(examples):
		tokens = examples.get("tokens") or examples.get("words") or examples.get("token")
		labels = examples.get("ner_tags")
		if tokens is None:
			return {}
		tokenized_inputs = tokenizer(tokens, is_split_into_words=True, truncation=True, padding=False)
		if labels is None:
			return tokenized_inputs

		aligned_labels = []
		for i, label in enumerate(labels):
			word_ids = tokenized_inputs.word_ids(batch_index=i)
			previous_word_idx = None
			label_ids = []
			for word_idx in word_ids:
				if word_idx is None:
					label_ids.append(-100)
				elif word_idx != previous_word_idx:
					label_ids.append(label[word_idx])
				else:
					label_ids.append(-100)
				previous_word_idx = word_idx
			aligned_labels.append(label_ids)

		tokenized_inputs["labels"] = aligned_labels
		return tokenized_inputs

	logger.info("Tokenizing dataset")
	try:
		tokenized = train_ds.map(tokenize_and_align_labels, batched=True, remove_columns=train_ds.column_names)
	except Exception as e:
		logger.error(f"Tokenization failed: {e}")
		tokenized = train_ds

	model = AutoModelForTokenClassification.from_pretrained(base_model, num_labels=num_labels)

	# move model to selected device
	model.to(device)

	output_dir = f"model_{task_id}"
	training_args = TrainingArguments(
		output_dir=output_dir,
		overwrite_output_dir=True,
		num_train_epochs=epochs,
		per_device_train_batch_size=batch_size,
		save_strategy="no",
		logging_strategy="epoch",
		report_to=[],
	)

	# Use a data collator to correctly pad inputs and labels in batches
	data_collator = DataCollatorForTokenClassification(tokenizer)
	trainer = Trainer(model=model, args=training_args, train_dataset=tokenized, data_collator=data_collator)

	logger.info("Starting training")
	trainer.train()
	logger.info("Training complete, saving model")
	trainer.save_model(output_dir)

	# compress and upload
	tar_name = f"model_{task_id}_bert_token_cls.tar.gz"
	compress_dir_to_tar_gz(output_dir, tar_name)

	# upload to models bucket
	models_bucket = "models"
	if not minio_client.bucket_exists(models_bucket):
		minio_client.make_bucket(models_bucket)

	# upload tar and log
	with open(tar_name, "rb") as f:
		minio_client.put_object(models_bucket, tar_name, f, os.path.getsize(tar_name))

	with open(log_filename, "rb") as f:
		minio_client.put_object(models_bucket, log_filename, f, os.path.getsize(log_filename))

	logger.info("Uploaded model and log to MinIO")
	# return uploaded object name for status update
	return tar_name


def main_loop():
	# Blocking pop from Redis list 'train_jobs'
	while True:
		try:
			item = redis_client.blpop("train_jobs", timeout=5)
			if not item:
				continue

			# item is a tuple (list_name, job_json)
			_, job_json = item
			if isinstance(job_json, bytes):
				job_json = job_json.decode("utf-8")

			try:
				job = json.loads(job_json)
			except Exception as e:
				# invalid job payload
				continue

			task_id = job.get("task_id")
			# update status to running
			try:
				redis_client.set(f"train_job:{task_id}", json.dumps({"status": "running", "task_id": task_id, "started_at": time.time()}))
			except Exception:
				pass

			try:
				uploaded = process_and_train(job)
				# on success, process_and_train returns uploaded object name
				models_path = f"models/{uploaded}"
				redis_client.set(f"train_job:{task_id}", json.dumps({"status": "completed", "task_id": task_id, "model_uri": models_path, "completed_at": time.time()}))
			except Exception as e:
				logger, log_filename = setup_logger(task_id or "unknown")
				logger.exception(f"Job processing failed: {e}")
				try:
					redis_client.set(f"train_job:{task_id}", json.dumps({"status": "failed", "task_id": task_id, "error": str(e), "failed_at": time.time()}))
				except Exception:
					pass

		except Exception:
			time.sleep(1)


if __name__ == "__main__":
	main_loop()

