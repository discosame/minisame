from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass
class User:
    id: int
    user_id: int
    number: int
    speaker: Literal["show", "takeru", "haruka", "hikari", "bear", "santa"]
    emotion: Literal["happiness", "anger", "sadness"]
    emotion_level: int
    pitch: int
    speed: int
    volume: int


@dataclass
class Manage:
    id: int
    server_id: int
    bot_id: int
    voice_id: int
    text_id: int
    joined_at: datetime


@dataclass
class Auto_Delete:
    id: int
    user_id: int
    enable: bool


@dataclass
class Setting:
    id: int
    server_id: int
    read_bot: bool
    read_mention: bool
    enable_dict: bool
    auto_remove: bool
