"""ExpanderTools

Discordのmessage urlからembedを作成してポストする。
X(Twitter)のmessage urlからembedを作成してポストする。

Notes:
    - on_messageでは、message urlからembedを作成してポストする。
    - on_raw_reaction_addでは、メッセージに付与されたリアクションを削除する。
"""

from concord import Agent
from discord import Message, RawReactionActionEvent
from discord.ext.commands import Cog  # type: ignore [reportMissingTypeStubs]

from url_expander import DiscordUrlExpander, TwitterUrlExpander


class ExpanderTools(Cog):
    def __init__(self, agent: Agent) -> None:
        self.agent = agent
        self.discord_expander = DiscordUrlExpander(agent)
        self.twitter_expander = TwitterUrlExpander(agent)

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        await self.discord_expander.on_message(message)
        await self.twitter_expander.on_message(message)

    @Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent) -> None:
        await self.discord_expander.on_raw_reaction_add(payload)
        await self.twitter_expander.on_raw_reaction_add(payload)
