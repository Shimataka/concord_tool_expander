import re

from concord import Agent
from discord import Asset, DefaultAvatar, Embed, Message, RawReactionActionEvent, Thread
from discord.channel import TextChannel, VoiceChannel
from discord.ext.commands import Bot  # type: ignore [reportMissingTypeStubs]

regex_message_url = (
    r"(?!<)https://(ptb.|canary.)?discord(app)?.com/"
    r"channels/(?P<guild>[0-9]{17,20})/(?P<channel>[0-9]{17,20})/(?P<message>[0-9]{17,20})(?!>)"
)
DELETE_REACTION_EMOJI = "\U0001f5d1"


class DiscordUrlExpander:
    """DiscordUrlExpander

    Discordのmessage urlからembedを作成してポストする。
    "https://discord.com/channel/<guild>/<channel>/<message>"

    Args:
        bot (Agent): BOTのコア部分となるAgentクラス。
    """

    def __init__(self, agent: Agent) -> None:
        self.agent = agent

    async def on_message(self, message: Message) -> None:
        """Discordのmessage urlからembedを作成してポストする。

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
        extracted_messages = await self._extract_messages(message)

        for target_message in extracted_messages:
            sent_messages: list[Message] = []
            if (len(target_message.content) != 0) or (len(target_message.attachments)):
                sent_message = await message.channel.send(embed=make_embed(target_message))
                sent_messages.append(sent_message)

            for attachment in target_message.attachments[1:]:
                embed = Embed()
                embed.set_image(url=attachment.proxy_url)
                sent_attachment_message = await message.channel.send(embed=embed)
                sent_messages.append(sent_attachment_message)

            for embed in target_message.embeds:
                sent_embed_message = await message.channel.send(embed=embed)
                sent_messages.append(sent_embed_message)

            if len(sent_messages) == 0:
                continue
            top_message = sent_messages[0]
            await top_message.add_reaction(DELETE_REACTION_EMOJI)
            top_embed = top_message.embeds[0]
            top_embed.set_author(
                name=getattr(top_embed.author, "name", None),
                icon_url=getattr(top_embed.author, "icon_url", None),
                url=make_jump_url(message, target_message, sent_messages),
            )
            await top_message.edit(embed=top_embed)

    async def _extract_messages(self, message: Message) -> list[Message]:
        messages: list[Message] = []
        for ids in re.finditer(regex_message_url, message.content):
            if message.guild is None:
                continue
            if message.guild.id != int(ids["guild"]):
                continue
            channel = message.guild.get_channel_or_thread(int(ids["channel"]))
            if not isinstance(channel, (TextChannel, VoiceChannel, Thread)):
                continue
            fetched_message = await channel.fetch_message(int(ids["message"]))
            messages.append(fetched_message)
        return messages


def make_embed(message: Message) -> Embed:
    embed = Embed(
        description=message.content,
        timestamp=message.created_at,
    )
    embed.set_author(
        name=message.author.display_name,
        icon_url=message.author.avatar or f"{Asset.BASE}/embed/avatars/{DefaultAvatar.red}.png",
        url=message.jump_url,
    )
    if isinstance(message.channel, (TextChannel, VoiceChannel)) and (message.guild is not None):
        embed.set_footer(
            text=message.channel.name,
            icon_url=message.guild.icon or f"{Asset.BASE}/embed/avatars/{DefaultAvatar.red}.png",
        )
    if message.attachments and message.attachments[0].proxy_url:
        embed.set_image(url=message.attachments[0].proxy_url)
    return embed


def make_jump_url(
    base_message: Message,
    expand_message: Message,
    extra_messages: list[Message],
) -> str:
    extra = ",".join([str(i.id) for i in extra_messages])
    url = f"{expand_message.jump_url}"
    url += f"?base_aid={expand_message.author.id}"
    url += f"&aid={base_message.author.id}"
    url += f"&extra={extra}"
    return url
