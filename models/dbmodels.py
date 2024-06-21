from datetime import datetime
from pydantic import Field
from typing import Optional, List
from beanie import Document, init_beanie
import random


def random_key():
    return "".join(random.choices('qwertyuiopasdfghjklzxcvbnm1234567890', k=9))


class Quote(Document):
    quote: str
    author: str
    tags: List[str]


class AllowedGroup(Document):
    clan_id: int
    clan_name: str
    quiz: Optional[bool] = False
    chess: Optional[bool] = False
    gid: Optional[str] = ''


class RankLevel(Document):
    user_id: int
    clan_id: int
    level: int
    user_name: str
    first_name: str
    last_name: str
    exp: int


class ChessGame(Document):
    gid: str = Field(default_factory=random_key)
    clan_id: int
    p1: int
    p2: int
    gameover: Optional[bool] = False
    winner: Optional[int] = -1
    fen: Optional[str] = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    moves: Optional[List[str]] = []
    winner: Optional[str] = 'None'
    time: datetime = Field(default_factory=datetime.now)
    overtime: datetime = Field(default_factory=datetime.now)


MODELS = [AllowedGroup, RankLevel, ChessGame]


async def connectdb(db):
    await init_beanie(database=db, document_models=MODELS)
    print("Connected To Database")
