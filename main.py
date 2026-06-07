import discord
from discord.ext import commands
import random
import json
import os
from discord.ui import View

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "data.json"

default_data = {
    "subjects": ["校長", "AI", "宇宙人"],
    "actions": ["爆発した", "課金した", "消えた"],
    "places": ["学校", "異世界"]
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return default_data

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

recent = []
RECENT_LIMIT = 5


class Menu(View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="ネタ生成", style=discord.ButtonStyle.primary)
    async def gen(self, interaction: discord.Interaction, button):
        s = random.choice(data["subjects"])
        a = random.choice(data["actions"])
        p = random.choice(data["places"])
        await interaction.response.send_message(f"{p}で{s}が{a}。")

    @discord.ui.button(label="一覧", style=discord.ButtonStyle.success)
    async def list_btn(self, interaction: discord.Interaction, button):
        await interaction.response.send_message("subjects / actions / places")


@bot.event
async def on_ready():
    print(f"{bot.user} 起動したぜ")


@bot.command()
async def menu(ctx):
    await ctx.send("メニュー👇", view=Menu())


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content

    # ネタ生成
    if content.startswith("ネタ考えて"):
        try:
            parts = content.split(" ")
            count = int(parts[1]) if len(parts) > 1 else 1

            if count > 20:
                await message.channel.send("出力できないよ～ぴえん上限20だよ")
                return

            results = []

            for _ in range(count):
                for _ in range(50):
                    s = random.choice(data["subjects"])
                    a = random.choice(data["actions"])
                    p = random.choice(data["places"])
                    result = f"{p}で{s}が{a}。"

                    if result not in recent:
                        break

                results.append(result)
                recent.append(result)

                if len(recent) > RECENT_LIMIT:
                    recent.pop(0)

            await message.channel.send("\n\n".join(results))

        except:
            await message.channel.send("使い方：ネタ考えて 5")

    # 追加
    elif content.startswith("追加しろ"):
        try:
            parts = content.split(" ")
            category = parts[1]
            items = parts[2:]

            if category in data:
                for item in items:
                    if item not in data[category]:
                        data[category].append(item)

                save_data(data)
                await message.channel.send("追加したぜ")

        except:
            await message.channel.send("使い方：追加しろ subjects 校長")

    # 削除
    elif content.startswith("削除して"):
        try:
            parts = content.split(" ")
            category = parts[1]
            items = parts[2:]

            if category in data:
                for item in items:
                    if item in data[category]:
                        data[category].remove(item)

                save_data(data)
                await message.channel.send("削除したぜ")

        except:
            await message.channel.send("使い方：削除して subjects 校長")

    # 一覧
    elif content.startswith("一覧見せて"):
        try:
            parts = content.split(" ")
            category = parts[1]

            if category in data:
                items = data[category][-20:]
                await message.channel.send("\n".join(items) if items else "空")

        except:
            await message.channel.send("使い方：一覧見せて subjects")

    await bot.process_commands(message)


bot.run(os.getenv("DISCORD_TOKEN"))