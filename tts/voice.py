import aiohttp
from discord.ext import commands
from lib import normal #Embedを作る自作関数(非公開)

import db, views, asyncio, os, re, importlib

from discord import Message, FFmpegPCMAudio, Member, VoiceState

from dotenv import load_dotenv

load_dotenv()


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tts_user: db.tts.User = db.tts.User()
        self.tts_manage: db.tts.Manage = db.tts.Manage()
        self.tts_setting: db.tts.Setting = db.tts.Setting()
        self.tts_auto_delete: db.tts.Auto_Delete = db.tts.Auto_Delete()

        importlib.reload(views)

        self.base_url: str = "https://api.voicetext.jp/v1/tts"
        self.api: str = os.environ.get("VOICE_TEXT_WEB_API") #https://cloud.voicetext.jp/webapi/api_keys/new

        self.speaker_to_jp: dict[str, str] = {
            "show": "男性1",
            "takeru": "男性2",
            "haruka": "女性1",
            "hikari": "女性2",
            "santa": "サンタ",
            "bear": "凶暴な熊",
        }

        self.emotion_to_jp: dict[str, str] = {
            "happiness": "喜",
            "anger": "怒",
            "sadness": "悲",
        }

        self.speakers: tuple[str, ...] = (
            "show",
            "takeru",
            "haruka",
            "hikari",
            "santa",
            "bear",
        )

        self.emotions: tuple[str, ...] = ("happiness", "anger", "sadness")

    @commands.Cog.listener("on_voice_state_update")
    async def on_bot_remove(
        self, member: Member, before: VoiceState, after: VoiceState
    ):
        "VCからBOTを覗いて、誰も居なくなったときに、自動退出する"
        if (before.channel and after.channel) and (
            before.channel.id == after.channel.id
        ):
            return

        if not before.channel:
            return

        members = [member for member in before.channel.members if not member.bot] #VC内のメンバー一覧からBOTを覗いて、新しいリストを作成する

        if members:
            return

        if not member.guild.voice_client:
            return
        await member.guild.voice_client.disconnect(force=True)


    @commands.Cog.listener("on_voice_state_update")
    async def on_auto_delete(
        self, member: Member, before: VoiceState, after: VoiceState
    ):
        """
        自動削除をする
        """
        if (before.channel and after.channel) and (
            before.channel.id == after.channel.id
        ):
            return

        if not before.channel:
            return

        if not member.guild.voice_client:
            return

        if member not in member.guild.voice_client.channel.members:
            return

        if not (auto_delete_data := await self.tts_auto_delete.fetch(member.id)):
            return

        if not auto_delete_data.enable:
            return

        if not (data := await self.tts_manage.fetch(member.guild.id, self.bot.user.id)):
            return

        text = self.bot.get_channel(data.text_id)

        if not text:
            return

        voice = self.bot.get_channel(data.voice_id)

        if not voice:
            return

        if voice.id != before.channel.id:
            return

        def check(mes: Message):
            if mes.author.id != member.id:
                return False

            if mes.channel.id != text.id:
                return False

            return mes.created_at > data.joined_at

        await text.purge(check=check, limit=None)

    @commands.Cog.listener("on_message")
    async def on_send_menu(self, mes: Message):
        """
        メンションされたときに読み上げメニューを送信する
        """
        if mes.author.bot:
            return

        if mes.guild is None:
            return

        if mes.content not in [f"<@{self.bot.user.id}>", f"<@!{self.bot.user.id}>"]:
            return

        if not mes.mentions:
            return

        if mes.mentions[0].id != self.bot.user.id:
            return

        #ctxが必要なので無理やり作る
        ctx = await self.bot.get_context(mes)

        view = views.tts.Tts_Menu(ctx)

        embed = normal(
            desc="下記のボタンから各操作を行えます\n**BOTに再起動が入ると反応しなくなるので、その時は再度メンションしてください**"
        )

        view.message = await mes.channel.send(embeds=[embed], view=view)

    @commands.Cog.listener("on_message")
    async def on_tts(self, mes: Message):
        """
        読み上げを開始する
        
        読み上げ無い内容
        
        ・ミニ🦈のコマンド
        ・BOTが送信したメッセージ(設定次第)

        ・メンションを名前に変換する(設定次第)
        ・DM内は読まない
        
        """
        
        #いろいろ条件を確認する
        if not mes.guild:
            return

        if (
            main_data := await self.tts_manage.fetch(mes.guild.id, self.bot.user.id)
        ) is None:
            return

        if not main_data:
            return

        if not (voice := self.bot.get_channel(main_data.voice_id)):
            return

        if not (text := self.bot.get_channel(main_data.text_id)):
            return

        if text.id != mes.channel.id:
            return

        if mes.guild.me not in voice.members:
            return
        
        #設定データを取得
        if not (setting_data := await self.tts_setting.fetch(mes.guild.id)) is None:
            await self.tts_setting.insert(mes.guild.id)
            setting_data = await self.tts_setting.fetch(mes.guild.id)

        #BOTのメッセージ読み上げがオフで送信者がBOTだったら、読まない
        if not setting_data.read_bot:
            if mes.author.bot:
                return

        #送信されたメッセージがミニ🦈のコマンドか確認するために、ctxを無理矢理作る
        ctx = await self.bot.get_context(mes)

        if ctx.command:
            return

        #メンションを読み上げるか確認して、読み上げるように設定されてたらメンションを名前に変換する
        if setting_data.read_mention:
            mes.content = self.replace_mention(mes)

        #ユーザーの読み上げ音声設定を取得
        if not (user_data := await self.tts_user.fetch(mes.author.id, 1)):
            await self.tts_user.insert(mes.author.id, 1)
            user_data = await self.tts_user.fetch(mes.author.id, 1)

        #APIに渡すパラメータの設定
        read_prm = {
            "text": mes.content,
            "speaker": user_data.speaker,
            "pitch": user_data.pitch,
            "speed": user_data.speed,
            "volume": user_data.volume,
        }

        if user_data.speaker != "show":
            read_prm["emotion"] = user_data.emotion
            read_prm["emotion_level"] = user_data.emotion_level

        prms = {
            "url": self.base_url,
            "params": read_prm,
            "auth": aiohttp.BasicAuth(self.api),
        }

        #再生する音声ファイルを入れておくためのフォルダーを作成
        if not os.path.isdir("voices"):
            os.mkdir("voices")
        #さらにチャンネルIDのフォルダーを作る
        if not os.path.isdir(f"voices/{mes.channel.id}"):
            os.mkdir(f"voices/{mes.channel.id}")
        #wavファイルを作成
        await self.save_wav_file(mes, **prms)

        #読み上げ中だったら終わるまで待機
        #エラーは握りつぶす
        try:
            while mes.guild.voice_client.is_playing():
                await asyncio.sleep(1)
        except:
            return

        #再生
        self.play(mes)

    async def save_wav_file(self, mes: Message, **prms):
        """
        wavファイルを作成
        
        apiから得たデータを基にする
        
        ファイル名はメッセージIDに
        
        /voices/{channel_id}/{message_id}.wav
        """
        fp_voice_file = f"voices/{mes.channel.id}/{mes.id}.wav"
        async with aiohttp.ClientSession() as session:
            async with session.post(**prms) as resp:
                if resp.status != 200:
                    d = await resp.json()
                    print(d)

                    return await mes.channel.send("エラーが発生しました。")

                with open(fp_voice_file, "wb") as f:
                    f.write(await resp.read())
    
    def play(self, mes: Message):
        """
        再生
        
        再生が終わったら、作成したwavファイルを削除する
        """
        fp_voice_file = f"voices/{mes.channel.id}/{mes.id}.wav"
        mes.guild.voice_client.play(
            FFmpegPCMAudio(fp_voice_file), after=lambda _: os.remove(fp_voice_file)
        )

    def replace_mention(self, mes: Message):
        """
        メンションを名前に変換
        """
        for m in re.finditer(r"<@&(?P<role_id>[0-9]+)>", mes.content, re.MULTILINE):
            g = m.groups()[0]
            for w in g.splitlines():
                mes.content = mes.content.replace(
                    g, mes.guild.get_role(int(w)).name
                ).replace("@&", "")
        # ユーザー
        for m in re.finditer(r"<@!?(?P<user_id>[0-9]+)>", mes.content, re.MULTILINE):
            g = m.groups()[0]
            for w in g.splitlines():
                mes.content = mes.content.replace(
                    g, mes.guild.get_member(int(w)).display_name
                ).replace("@", "")
        # チャンネル
        for m in re.finditer(r"<#(?P<channel_id>[0-9]+)>", mes.content, re.MULTILINE):
            g = m.groups()[0]
            for w in g.splitlines():
                mes.content = mes.content.replace(
                    g, mes.guild.get_channel(int(w)).name
                ).replace("#", "")

        return mes.content


async def setup(bot):
    await bot.add_cog(Voice(bot))
