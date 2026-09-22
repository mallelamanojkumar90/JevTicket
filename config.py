from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


DEFAULT_JEV_API_URL = "https://api.typesafe.ai/v1/systemone"
DEFAULT_JEV_MODEL = "jev-latest"


@dataclass(frozen=True)
class Settings:
    typesafe_api_key: str | None
    typesafe_default_model: str = DEFAULT_JEV_MODEL


def load_settings() -> Settings:
    load_dotenv()

    return Settings(
        typesafe_api_key=os.getenv("TYPESAFE_API_KEY") or os.getenv("JEV_API_KEY"),
        typesafe_default_model=os.getenv("TYPESAFE_DEFAULT_MODEL", DEFAULT_JEV_MODEL),
    )
