# Python Meme Fetcher

A simple Python module to fetch random memes from Reddit using the [Meme API](https://meme-api.com/).

## Prerequisites

- Python 3.9+
- [Requests](https://pypi.org/project/requests/) library

## Setup

You can clone the repo through this: 

```bash
git clone https://github.com/Madhav703/python-memes.git


1: Open the required directory:

```bash
cd python-memes
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

Or install directly from PyPI

```bash
pip install python-memes
```

## Usage

```python
from memes import MemeFetcher

# Fetch from any subreddit
mf = MemeFetcher("dankmemes")
meme = mf.get_meme()

if "error" in meme:
    print("Error:", meme["error"])
else:
    print("Title:", meme["title"])
    print("Subreddit:", meme["subreddit"])
    print("URL:", meme["url"])
```

## Discord.py Usage

```python

import discord
from discord.ext import commands
from memes import MemeFetcher

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def meme(ctx):
    mf = MemeFetcher()
    meme = mf.get_meme()

    if "error" in meme:
        await ctx.send(f"⚠️ {meme['error']}")
        return

    embed = discord.Embed(
        title=meme["title"],
        description=f"From r/{meme['subreddit']}",
        color=discord.Color.random()
    )
    embed.set_image(url=meme["url"])
    await ctx.send(embed=embed)

bot.run("YOUR_BOT_TOKEN")

```

## Notes

- Always fetches a random meme from Reddit.

- If the API is down or unreachable, the function returns an error dictionary.

- Requires an active internet connection.

## Troubleshooting

- `requests.exceptions.ConnectionError` → check your internet connection.

- Timeout errors → API might be down; try again later.

- Ensure you have installed the requests package properly.

## Contributing

- Fork this repository and make your changes.

- Run tests to ensure everything works.

- Submit a pull request with a clear description.

## License

- This project is licensed under the MIT License – see the LICENSE
 file for details.

## Facing any Issues?

- You can open an issue on the GitHub repo
.