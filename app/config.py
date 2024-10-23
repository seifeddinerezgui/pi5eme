from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "mysql+pymysql://root:@localhost/pi5eme"
    secret_key: str = "v2bGTpi1z0IQiDXh3mu3E2RdXbjPUhlpFfr0uEoN1Ks" # No default value; must be set in .env
    algorithm: str = "HS256"
    access_token_expire_minutes: float = 30
    refresh_token_expire_minutes: int = 60*24



# Instantiate settings


settings = Settings()

print(f"Database URL: {settings.database_url}")
print(f"Secret Key: {settings.secret_key}")

