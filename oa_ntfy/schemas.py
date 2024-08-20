from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Set, Optional
from pydantic import (
    Field,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    gmail_label_id: str = Field()
    db_path: str = Field(default="db.json")
    sleep_time: float = Field(default=60.0)
    ntfy_topic_name: str = Field()
    ntfy_protected_topic: bool = Field(default=False)
    ntfy_bearer_token: Optional[str] = Field(default=None)
    position_open_regex: str = Field(
        default="Bot:\s*(.*?)Symbol:\s*(.*?)Strategy:\s*(.*?)Position:\s*(.*?)Expiration:\s*(.*?)Quantity:\s*(.*?)Cost:\s*(.*?)Price:\s*(.*)"
    )
    position_closed_regex: str = Field(
        default="Bot:\s*(.*?)Symbol:\s*(.*?)Strategy:\s*(.*?)Position:\s*(.*?)Expiration:\s*(.*?)Quantity:\s*(.*?)Close Price\*:\s*(.*?)Profit/Loss:\s*(.*)"
    )


@dataclass
class OATrade:
    bot: str
    symbol: str
    strategy: str
    position: str
    expiration: datetime
    quantity: int


@dataclass
class OATradeOpened(OATrade):
    cost: float
    price: float

    def __str__(self):
        return f"Position opened by {self.bot}: {self.quantity} {self.symbol} {self.strategy}"


@dataclass
class OATradeClosed(OATrade):
    close_price: float
    profit_loss: float

    def __str__(self):
        return f"Position closed by {self.bot}: {self.quantity} {self.symbol} {self.strategy}"


class NtfyNotificationFormat(Enum):
    plaintext = "plaintext"
    markdown = "markdown"


@dataclass
class NtfyNotification:
    text: str
    title: str
    format: NtfyNotificationFormat
