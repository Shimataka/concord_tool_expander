# URL Expander

Discordボット用のURL展開ツール。DiscordのメッセージURLとX(Twitter)のURLを自動的に展開してembedを作成します。

## 機能

### Discord URL Expander

- DiscordのメッセージURLを検出して自動的にembedを作成
- メッセージの内容、添付ファイル、既存のembedを展開
- 🗑️リアクションで投稿を削除可能

### Twitter URL Expander

- X(Twitter)のURLをvxtwitter.comに変換してembedを作成
- 🗑️リアクションで投稿を削除可能

## インストール

```bash
# 依存関係のインストール
pip install git+https://github.com/Shimataka/concord_tool_expander.git
```

## 使用方法

### 基本的な使用方法

```python
import asyncio
from pathlib import Path
from concord import Agent

# Agentの初期化
config_and_log_dirpath = Path(__file__).parent
agent = Agent(utils_dirpath=config_and_log_dirpath)
asyncio.run(agent.run())
```

### ツールの設定

`tools/expander/__tool__.py`を作成して以下のように設定：

```python
from concord import Agent
from discord import Message, RawReactionActionEvent
from discord.ext.commands import Cog

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
```

### 設定ファイル

`configs/bot.ini`でボットの設定：

```ini
[Discord.Bot]
name = YourBotName
description = Your bot description

[Discord.API]
token = YOUR_BOT_TOKEN

[Discord.DefaultChannel]
dev_channel = CHANNEL_ID
log_channel = CHANNEL_ID
```

## 実行例

```bash
# 基本的な使用例
python examples/ex00_basic_usage/main.py --bot-name testbot --tool-directory-paths tools
```

## 対応URL形式

### Discord

- `https://discord.com/channels/<guild>/<channel>/<message>`
- `https://ptb.discord.com/channels/<guild>/<channel>/<message>`
- `https://canary.discord.com/channels/<guild>/<channel>/<message>`

### X(Twitter)

- `https://twitter.com/<body>`
- `https://x.com/<body>`

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。
