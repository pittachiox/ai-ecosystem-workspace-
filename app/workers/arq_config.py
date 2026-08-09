from __future__ import annotations

from arq import create_pool
from arq.connections import RedisSettings

from app.core.config import settings
from app.workers.nontimeseries_worker import preprocess_images, predict_image_class, train_nontimeseries_model
from app.workers.timeseries_worker import forecast_timeseries, resample_timeseries, train_timeseries_model


class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    queue_name = settings.arq_redis_queue_name
    functions = [
        resample_timeseries,
        train_timeseries_model,
        forecast_timeseries,
        preprocess_images,
        train_nontimeseries_model,
        predict_image_class,
    ]


async def startup(ctx):
    ctx['app_state'] = {"started": True}


async def shutdown(ctx):
    ctx['app_state'] = {"stopped": True}
