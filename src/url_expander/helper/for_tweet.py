import asyncio
import re

from concord import Agent
from discord import Message, RawReactionActionEvent, Thread
from discord.channel import TextChannel, VoiceChannel
from discord.ext.commands import Bot  # type: ignore [reportMissingTypeStubs]

regex_message_url = r"(?!<)https://(twitter|x).com(?!>)/(?P<body>\S+)"
DELETE_REACTION_EMOJI = "\U0001f5d1"
WAITING_TIME = 1


class TwitterUrlExpander:
    """TwitterUrlExpander

    以下の変換を行ったメッセージをリポストすることで、X(Twitter)のembeddingをvxtwitterから取得する。
    "https://(twitter|x).com/<body>" -> "https://vxtwitter.com/<body>"

    Args:
        bot (Agent): BOTのコア部分となるAgentクラス。
    """

    def __init__(self, agent: Agent) -> None:
        self.agent = agent

    async def on_message(self, message: Message) -> None:
        """X(Twitter)のmessage urlからembedを作成してポストする。

        デコレータ `@Cog.listener()` を使用しているため、
        `on_message` メソッドは `discord.ext.commands.Bot` クラスの
        インスタンスメソッドとして定義されている。

        Args:
            message (Message): メッセージ

        Returns:
            None
        """
        if message.is_system():
            return
        if message.author.bot:
            return
        await self._expander(message=message)

    async def on_raw_reaction_add(self, payload: RawReactionActionEvent) -> None:
        """メッセージに付与されたリアクションを削除する。

        デコレータ `@Cog.listener()` を使用しているため、
        `on_raw_reaction_add` メソッドは `discord.ext.commands.Bot` クラスの
        インスタンスメソッドとして定義されている。

        Args:
            payload (RawReactionActionEvent): リアクションのイベント

        Returns:
            None
        """
        await self._delete_expander(bot=self.agent.bot, payload=payload)

    async def _delete_expander(self, bot: Bot, payload: RawReactionActionEvent) -> None:
        if str(payload.emoji) != DELETE_REACTION_EMOJI:  # other emoji
            return
        if bot.user is None:  # bot.user is None
            return
        if payload.user_id == bot.user.id:  # user who added emoji is bot
            return
        channel = bot.get_channel(payload.channel_id)
        if isinstance(channel, (TextChannel, VoiceChannel, Thread)):
            message = await channel.fetch_message(payload.message_id)
            if message.author.id != bot.user.id:  # not bot message on which emoji is sticking
                return
            if len(message.embeds) == 0:  # message has already any embeddings (maybe vxtwitter?)
                return
            await message.delete()
        else:
            msg = f"Unknown channel type: {channel}"
            raise TypeError(msg)

    async def _expander(self, message: Message) -> None:
        urls = await self._extract_urls(message)
        for url in urls:
            sent_message = await message.channel.send(url)
            await sent_message.add_reaction(DELETE_REACTION_EMOJI)

    async def _extract_urls(self, message: Message) -> list[str]:
        contents: list[str] = []
        await asyncio.sleep(WAITING_TIME)
        if len(message.embeds) > 0:
            return []
        for ids in re.finditer(regex_message_url, message.content):
            url = "https://vxtwitter.com/" + ids["body"]
            contents.append(url)
        return contents
