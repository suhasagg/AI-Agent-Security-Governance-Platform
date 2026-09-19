from pydantic_settings import BaseSettings,SettingsConfigDict
class Settings(BaseSettings):
    openai_api_key:str
    openai_model:str="gpt-5.6-luna"
    database_url:str="postgresql+asyncpg://governance:governance@localhost:5432/governance"
    redis_url:str="redis://localhost:6379/0"
    java_mcp_url:str="http://localhost:8081/mcp"
    otel_exporter_otlp_endpoint:str="http://localhost:4318"
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")
settings=Settings()
