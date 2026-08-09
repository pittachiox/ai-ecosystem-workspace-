from core.config import settings


def main():
    print("=== Testing Settings from .env ===")
    print(f"REDIS_HOST       : {settings.redis_host}")
    print(f"REDIS_PORT       : {settings.redis_port}")
    print(f"POSTGRES_USER    : {settings.postgres_user}")
    print(f"POSTGRES_PASSWORD: {settings.postgres_password}")
    print(f"POSTGRES_DB      : {settings.postgres_db}")
    print(f"POSTGRES_HOST    : {settings.postgres_host}")
    print(f"POSTGRES_PORT    : {settings.postgres_port}")
    print(f"LABEL_STUDIO_URL : {settings.label_studio_url}")
    print(f"LABEL_STUDIO_API_KEY: {settings.label_studio_api_key}")
    print("===")


if __name__ == "__main__":
    main()
