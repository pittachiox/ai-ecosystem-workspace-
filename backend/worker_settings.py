from arq import create_pool
from arq.connections import RedisSettings

from core.config import settings


def simple_work(ctx, data):
    print("Processing job data:", data)
    return {"status": "done", "data": data}


class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    queue_name = settings.arq_redis_queue_name
    functions = [simple_work]


async def main():
    redis = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    job = await redis.enqueue_job("simple_work", {"message": "Hello ARQ!"})
    print("Enqueued job id:", job.job_id)
    await redis.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
