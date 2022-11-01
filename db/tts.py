from . import models
from .base import session_scope

from datetime import datetime
import numpy as np

__all__ = ("User", "Manage", "Auto_Delete", "Setting")


class User:
    """
    ユーザーの声の設定
    ・複数のパターン作成できるように
    ・設定番号を付ける
    
    """
    def __init__(self) -> None:
        self.table = "tts.tts_user"

        self.speakers: tuple[str, ...] = (
            "show",
            "takeru",
            "haruka",
            "hikari",
            "santa",
            "bear",
        )

        self.emotions: tuple[str, ...] = ("happiness", "anger", "sadness")

    async def fetch(self, user_id: int, number: int = 1) -> models.tts.User:
        """
        データーベースからユーザーのデータを取得する
        
        Parameters:
        -----------
        user_id : int
            データを取得するユーザーのID
        
        number: int
            設定番号
            
        Returns:
        -----------
        models.tts.User
        """
        
        async with session_scope() as pool:
            data = await pool.fetchrow(
                f"select * from {self.table} where user_id = $1 and number = $2",
                user_id,
                number,
            )

            if data:
                return models.tts.User(**data)

    async def insert(self, user_id: int, number: int = 1):
        """
        データーベースにユーザーのデータを登録する
        
        それぞれのパラメータをランダムに取得
        パラメータの範囲:
            https://cloud.voicetext.jp/webapi/docs/api
        
        
        Parameters:
        -----------
        user_id : int
            データを登録するユーザーのID
        
        number: int
            登録する設定番号
            
        Returns:
        -----------
        None
        """
        
        speaker = np.random.choice(self.speakers)
        emotion = np.random.choice(self.emotions)
        emotion_level = np.random.randint(1, 5)
        pitch = np.random.randint(50, 201)
        speed = np.random.randint(50, 201)
        volume = 100

        async with session_scope() as pool:
            await pool.execute(
                f"""insert into {self.table} 
                (user_id, number, speaker, emotion, emotion_level, pitch, speed, volume) 
                values 
                ($1, $2, $3, $4, $5, $6, $7, $8)""",
                user_id,
                number,
                speaker,
                emotion,
                emotion_level,
                pitch,
                speed,
                volume,
            )

    """
    以下それぞれのパラメータを変更する(めんどくさいので略)
    
    
    Parameters:
    -----------
    パラメータ: Any(適時)
        変更するパラメータの値
    
    user_id : int
        データを登録するユーザーのID
    
    number: int
        登録する設定番号
        
    Returns:
    -----------
    None
    """
    

    async def update_speaker(self, speaker: str, user_id: int, number: int = 1):
        async with session_scope() as pool:
            await pool.execute(
                f"""update {self.table} set speaker = $1 where user_id = $2 and number = $3""",
                speaker,
                user_id,
                number,
            )

    async def update_emotion(self, emotion: str, user_id: int, number: int = 1):
        async with session_scope() as pool:
            await pool.execute(
                f"""update {self.table} set emotion = $1 where user_id = $2 and number = $3""",
                emotion,
                user_id,
                number,
            )

    async def update_emotion_level(
        self, emotion_level: int, user_id: int, number: int = 1
    ):
        async with session_scope() as pool:
            await pool.execute(
                f"""update {self.table} set emotion_level = $1 where user_id = $2 and number = $3""",
                emotion_level,
                user_id,
                number,
            )

    async def update_pitch(self, pitch: int, user_id: int, number: int = 1):
        async with session_scope() as pool:
            await pool.execute(
                f"""update {self.table} set pitch = $1 where user_id = $2 and number = $3""",
                pitch,
                user_id,
                number,
            )

    async def update_speed(self, speed: int, user_id: int, number: int = 1):
        async with session_scope() as pool:
            await pool.execute(
                f"""update {self.table} set speed = $1 where user_id = $2 and number = $3""",
                speed,
                user_id,
                number,
            )

    async def update_volume(self, volume: int, user_id: int, number: int = 1):
        async with session_scope() as pool:
            await pool.execute(
                f"""update {self.table} set volume = $1 where user_id = $2 and number = $3""",
                volume,
                user_id,
                number,
            )


class Manage:
    """
    読み上げ状況等をデーターベースに登録
    
    """
    
    def __init__(self) -> None:
        self.table = "tts.tts_manage"

    async def fetch(self, server_id: int, bot_id: int) -> models.tts.Manage:
        """
        データーベースからデータを取得する
        
        Parameters:
        -----------
        server_id : int
            データを取得するサーバーのID
        
        bot_id: int
            ミニ🦈のID
            
        Returns:
        -----------
        models.tts.Manage
        """
        
        async with session_scope() as pool:
            data = await pool.fetchrow(
                f"select * from {self.table} where server_id = $1 and bot_id = $2",
                server_id,
                bot_id,
            )

            if data:
                return models.tts.Manage(**data)

    async def insert(self, server_id: int, bot_id: int) -> None:
        """
        データーベースにデータを登録する
        
        Parameters:
        -----------
        server_id : int
            データを取得するサーバーのID
        
        bot_id: int
            ミニ🦈のID
            
        Returns:
        -----------
        None
        """
        async with session_scope() as pool:
            await pool.execute(
                f"""insert into {self.table} 
                (server_id, bot_id) 
                values 
                ($1, $2)""",
                server_id,
                bot_id,
            )

    async def update_voice_id(self, voice_id: int, server_id: int, bot_id: int) -> None:
        async with session_scope() as pool:
            await pool.execute(
                f"""update {self.table} set voice_id = $1 where server_id = $2 and bot_id = $3""",
                voice_id,
                server_id,
                bot_id,
            )

    async def update_text_id(self, text_id: int, server_id: int, bot_id: int) -> None:
        async with session_scope() as pool:
            await pool.execute(
                f"""update {self.table} set text_id = $1 where server_id = $2 and bot_id = $3""",
                text_id,
                server_id,
                bot_id,
            )

    async def update_joined_at(
        self, joined_at: datetime, server_id: int, bot_id: int
    ) -> None:
        async with session_scope() as pool:
            await pool.execute(
                f"""update {self.table} set joined_at = $1 where server_id = $2 and bot_id = $3""",
                joined_at,
                server_id,
                bot_id,
            )


class Auto_Delete:
    """
    読み上げたメッセージを自動削除する
    ・発動タイミング -> BOTもしくはユーザーがVCから落ちた時
    ・ユーザーが落ちた時に、落ちたユーザーの読み上げたメッセージを削除する
    ・BOTが落ちた時に、VC内にいるユーザーの読み上げたメッセージを削除する
    ・保存した読み上げ開始時間から落ちた時の時間の間のメッセージ
    """
    
    def __init__(self) -> None:
        self.table = "tts.tts_auto_delete"

    async def fetch(self, user_id: int) -> models.tts.Auto_Delete:
        """
        データーベースからデータを取得する
        落ちたユーザーの自動削除がオンになってるか確認する
        
        Parameters:
        -----------
        user_id : int
            データを取得するユーザーのID
            
        Returns:
        -----------
        models.tts.Auto_Delete
        """
        
        async with session_scope() as pool:
            data = await pool.fetchrow(
                f"select * from {self.table} where user_id = $1",
                user_id,
            )

            if data:
                return models.tts.Auto_Delete(**data)

    async def insert(self, user_id: int) -> None:
        """
        データーベースにデータを登録する
        
        Parameters:
        -----------
        user_id : int
            データを取得するユーザーのID
            
        Returns:
        -----------
        None"""
        
        async with session_scope() as pool:
            await pool.execute(
                f"""insert into {self.table} 
                (user_id) 
                values 
                ($1)""",
                user_id,
            )

    async def update_auto_delete(self, auto_delete: bool, user_id: int) -> None:
        async with session_scope() as pool:
            await pool.execute(
                f"""update {self.table} set enable = $1 where user_id = $2""",
                auto_delete,
                user_id,
            )


class Setting:
    """
    正直何しようとしたのか忘れた
    
    多分読み上げの設定
    
    ・辞書機能
    ・BOTのメッセージを読み上げるか
    
    """
    def __init__(self) -> None:
        self.table = "tts.tts_setting"

    async def fetch(self, server_id: int) -> models.tts.Setting:
        """
        データーベースからデータを取得する
        サーバーの？
        
        Parameters:
        -----------
        server_id : int
            データを取得するサーバーのID
            
        Returns:
        -----------
        models.tts.Setting
        """
        async with session_scope() as pool:
            data = await pool.fetchrow(
                f"select * from {self.table} where server_id = $1",
                server_id,
            )

            if data:
                return models.tts.Setting(**data)

    async def insert(self, server_id: int) -> None:
        async with session_scope() as pool:
            await pool.execute(
                f"""insert into {self.table} 
                (server_id) 
                values 
                ($1)""",
                server_id,
            )

    async def update_read_bot(self, enable: bool, server_id: int):
        async with session_scope() as pool:
            await pool.execute(
                f"""update {self.table} set read_bot = $1 where server_id = $2""",
                enable,
                server_id,
            )

    async def update_enable_dict(self, enable: bool, server_id: int):
        async with session_scope() as pool:
            await pool.execute(
                f"""update {self.table} set enable_dict = $1 where server_id = $2""",
                enable,
                server_id,
            )

    async def update_enable_auto_remvoe(self, enable: bool, server_id: int):
        async with session_scope() as pool:
            await pool.execute(
                f"""update {self.table} set auto_remvoe = $1 where server_id = $2""",
                enable,
                server_id,
            )
