from core.config import settings


def main():
    print("Sandbox settings values:")
    print(f"REDIS_URL={settings.redis_url}")
    print(f"ARQ_REDIS_QUEUE_NAME={settings.arq_redis_queue_name}")
    print(f"DATABASE_URL={settings.database_url}")
    print(f"LABEL_STUDIO_URL={settings.label_studio_url}")
    print(f"LABEL_STUDIO_API_KEY={settings.label_studio_api_key}")


if __name__ == "__main__":
    main()
