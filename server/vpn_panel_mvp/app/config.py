from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    server_ip: str
    server_port: int = 8443
    sni: str = "www.google.com"
    public_key: str
    short_id: str
    profile_name: str = "VPN"
    xray_config_path: str = "/usr/local/etc/xray/config.json"
    xray_service_name: str = "xray"
    database_url: str = "sqlite:///./data/vpn.db"
    app_host: str = "127.0.0.1"
    app_port: int = 8001
    app_secret: str = "change-me"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()