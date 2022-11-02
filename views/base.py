from discord import VoiceChannel, ui, VoiceChannel, Role, Member
from discord.ext import commands
from typing import Optional
from enums import Emoji

import discord


class BaseView(ui.View):
    def __init__(
        self, timeout: Optional[int] = None, pushed_user: Optional[Member] = None
    ):
        super().__init__(timeout=timeout)

        self.pushed_user = pushed_user
        self.message: discord.Message | None = None

    def try_int(self, mes):
        try:
            return int(mes)
        except:
            return

    async def interaction_check(self, inter):
        if self.pushed_user is None:
            return True

        return (
            inter.user.id == self.pushed_user.id and self.message.id == inter.message.id
        )

    async def response_send_message(self, inter, mes, **kwrags):

        inter_m = await inter.response.send_message(mes, **kwrags)

        m = await inter_m.original_message()

        return m

    async def wait_input_modal(
        self, inter: discord.Interaction, announce: str, timeout: int | None = None
    ) -> str:
        """
        モーダルウインドウを送信

        Parameters
        ----------
        inter: discord.Interaction
            Interaction

        announce: str
            アナウンスメッセージ

            出力メッセージ

            announce


        timeout: int | None
            timeout時間

        Returns
        -------
        str

        """

        bm = await inter.channel.send(announce)

        def check(m: discord.Message):
            return m.author.id == inter.user.id and m.channel.id == inter.channel.id

        m = await inter.client.wait_for("message", check=check, timeout=timeout)

        return m

    async def wait_input_message(
        self,
        inter: discord.Interaction,
        announce: str,
        timeout: int | None = None,
        is_delete: bool = False,
    ) -> str:
        """
        文字列を指定

        Parameters
        ----------
        inter: discord.Interaction
            Interaction

        announce: str
            アナウンスメッセージ

            出力メッセージ

            announce


        timeout: int | None
            timeout時間

        Returns
        -------
        str

        """

        if is_delete:
            announce = announce + "\n削除するときは、「削除」と入力してください"

        bm = await inter.channel.send(announce)

        def check(m: discord.Message):
            return m.author.id == inter.user.id and m.channel.id == inter.channel.id

        m = await inter.client.wait_for("message", check=check, timeout=timeout)

        await bm.delete()
        await m.delete()

        if is_delete and m.content in ["削除", "「削除」", "`削除`", "[削除]"]:
            return

        return m.content

    async def wait_input_text_channel(
        self, inter: discord.Interaction, announce: str, timeout: int | None = None
    ) -> discord.TextChannel:
        """
        テキストチャンネルを指定

        Parameters
        ----------
        inter: discord.Interaction
            Interaction

        announce: str
            アナウンスメッセージ

            出力メッセージ

            announce
            \n`名前・ID・メンション`のいずれかで入力してください。


        timeout: int | None
            timeout時間

        Returns
        -------
        discord.CategoryChannel


        """

        bm = await inter.channel.send(announce + "\n`名前・ID・メンション`のいずれかで入力してください。")
        ctx = await inter.client.get_context(bm)

        def check(m: discord.Message):
            return m.author.id == inter.user.id and m.channel.id == inter.channel.id

        m = await inter.client.wait_for("message", check=check, timeout=timeout)

        await bm.delete()
        await m.delete()

        converter = commands.TextChannelConverter()

        channel = await converter.convert(ctx, m.content)

        return channel

    async def wait_input_voice_channel(
        self, inter: discord.Interaction, announce: str, timeout: int | None = None
    ) -> discord.VoiceChannel:
        """
        ボイスチャンネルを指定

        Parameters
        ----------
        inter: discord.Interaction
            Interaction

        announce: str
            アナウンスメッセージ

            出力メッセージ

            announce
            \n`名前・ID・メンション`のいずれかで入力してください。


        timeout: int | None
            timeout時間

        Returns
        -------
        discord.VoiceChannel


        """

        bm = await inter.channel.send(announce + "\n`名前・ID・メンション`のいずれかで入力してください。")
        ctx = await inter.client.get_context(bm)

        def check(m: discord.Message):
            return m.author.id == inter.user.id and m.channel.id == inter.channel.id

        m = await inter.client.wait_for("message", check=check, timeout=timeout)

        await bm.delete()
        await m.delete()

        converter = commands.VoiceChannelConverter()

        channel = await converter.convert(ctx, m.content)

        return channel

    async def wait_input_category_channel(
        self, inter: discord.Interaction, announce: str, timeout: int | None = None
    ) -> discord.CategoryChannel:
        """
        カテゴリーチャンネルを指定

        Parameters
        ----------
        inter: discord.Interaction
            Interaction

        announce: str
            アナウンスメッセージ

            出力メッセージ

            announce
            \n`名前・ID`のいずれかで入力してください。


        timeout: int | None
            timeout時間

        Returns
        -------
        discord.CategoryChannel


        """
        bm = await inter.channel.send(announce + "\n`名前・ID`のいずれかで入力してください。")
        ctx = await inter.client.get_context(bm)

        def check(m: discord.Message):
            return m.author.id == inter.user.id and m.channel.id == inter.channel.id

        m = await inter.client.wait_for("message", check=check, timeout=timeout)

        await bm.delete()
        await m.delete()

        converter = commands.CategoryChannelConverter()

        channel = await converter.convert(ctx, m.content)

        return channel

    async def wait_input_role(
        self, inter: discord.Interaction, announce: str, timeout: int | None = None
    ) -> discord.Role:
        """
        ロールを指定

        Parameters
        ----------
        inter: discord.Interaction
            Interaction

        announce: str
            アナウンスメッセージ

            出力メッセージ

            announce
            \n`名前・ID・メンション`のいずれかで入力してください。


        timeout: int | None
            timeout時間

        Returns
        -------
        discord.Role


        """
        bm = await inter.channel.send(announce + "\n`名前・ID・メンション`のいずれかで入力してください。")
        ctx = await inter.client.get_context(bm)

        def check(m: discord.Message):
            return m.author.id == inter.user.id and m.channel.id == inter.channel.id

        m = await inter.client.wait_for("message", check=check, timeout=timeout)

        await bm.delete()
        await m.delete()

        converter = commands.RoleConverter()

        role = await converter.convert(ctx, m.content)

        return role

    async def wait_select_tick(
        self, inter: discord.Interaction, announce: str, timeout: int | None = None
    ) -> bool:
        """
        丸罰を選択

        Parameters
        ----------
        inter: discord.Interaction
            Interaction

        announce: str
            アナウンスメッセージ

            出力メッセージ

            announce
            \n`名前・ID・メンション`のいずれかで入力してください。


        timeout: int | None
            timeout時間

        Returns
        -------
        bool


        """
        view = Select_Tick(inter.user.id)

        bm = await inter.channel.send(announce, view=view)

        await view.wait()

        await bm.delete()

        view.stop()

        return view.value


class Select_Tick(discord.ui.View):
    def __init__(self, author_id: int, timeout: Optional[float] = None):
        super().__init__(timeout=timeout)
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.author_id

    @discord.ui.button(label=str(Emoji.OK), style=discord.ButtonStyle.green)
    async def ok(self, inter, _):
        await inter.response.defer()

        self.value = True
        self.stop()

    @discord.ui.button(label=str(Emoji.NO), style=discord.ButtonStyle.gray)
    async def no(self, inter, _):
        await inter.response.defer()

        self.value = False
        self.stop()
