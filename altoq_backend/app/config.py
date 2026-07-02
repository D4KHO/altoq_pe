from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "mysql+pymysql://root:password@localhost:3306/altoq_db"
    secret_key: str = "tu_clave_secreta_super_segura_cambiala_en_produccion"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    google_client_id: str | None = None
    gemini_api_key: str | None = None
    resend_api_key: str | None = None
    email_from: str = "onboarding@resend.dev"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
