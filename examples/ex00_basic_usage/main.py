"""00_basic_usage

このサンプルでは、ExpanderToolsを使用して、
- Discordのmessage urlからembedを作成してポストする。
- X(Twitter)のmessage urlからembedを作成してポストする。
の2つの機能を使用します。

```bash
examples/ex00_basic_usage$ python main.py --bot-name testbot --tool-directory-paths tools
```
"""

import asyncio
from pathlib import Path

from concord import Agent

if __name__ == "__main__":
    config_and_log_dirpath = Path(__file__).parent
    agent = Agent(utils_dirpath=config_and_log_dirpath)
    asyncio.run(agent.run())
