from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "mysql+pymysql://root:@localhost/pi5eme"
    secret_key: str  # No default value; must be set in .env
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"  # Specify the .env file to load environment variables
        env_file_encoding = 'utf-8'

# Instantiate settings
settings = Settings()

print(f"Database URL: {settings.database_url}")
print(f"Secret Key: {settings.secret_key}")

