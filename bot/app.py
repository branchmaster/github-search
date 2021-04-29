from os import environ
from pyrogram import Client
from pyrogram.filters import command
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import request


Bot: Client = Client(
    __name__,
    api_id=int(environ.get("TELEGRAM_API_ID")),
    api_hash=environ.get("TELEGRAM_API_HASH"),
    bot_token=environ.get("BOT_TOKEN")
)


@Bot.on_message(command("start"))
async def start(client: Client, message: Message) -> None:
    await message.reply(
        "Hello, send `/search linux` to search for 'linux' on GitHub."
    )


@Bot.on_message(command("search"))
async def search(client: Client, message: Message) -> None:
    query: str = " ".join(message.text.split()[1:])
    if not query:
        await message.reply("What are you looking for?")
        return
    result, status = await request.get(
        "https://api.github.com/search/repositories?per_page=20&q="+query
    )
    if status != 200:
        await message.reply("Order error, the limit per minute must have exceeded.")
        return
    msg: Message = await message.reply("Searching...")
    text: str = ""
    for repo in result["items"]:
        text += f"Name: __{repo['name']}__\n"
        text += f"Stars: **{repo['stargazers_count']}**\n"
        text += f"`/get {repo['full_name']}`\n\n"
    if not text:
        await client.edit_message_text(
            chat_id=msg.chat.id,
            message_id=msg.message_id,
            text="I didn't find anything!"
        )
    else:
        await client.edit_message_text(
            chat_id=msg.chat.id,
            message_id=msg.message_id,
            text=text
        )

@Bot.on_message(command("get"))
async def get(client: Client, message: Message) -> None:
    try:
        repo: str = message.text.split()[1]
    except IndexError:
        await message.reply("Which repository do you want to see?")
        return
    info, status = await request.get(f"https://api.github.com/repos/{repo}")
    if status != 200:
        await message.reply("This repository does not exist!")
        return
    if info['archived']:
        archived: str = "Yes"
    else:
        archived: str = "No"
    zip_url: str = f"{info['html_url']}/archive/{info['default_branch']}.zip"
    tarball_url: str = f"{info['html_url']}/archive/{info['default_branch']}.tar.gz"
    repo_license: str = "None"
    if info['license']:
        repo_license = info['license']['name']
    text: str = f"""
Name: __{info['name']}__
Owner: **{info['owner']['login']}({info['owner']['type']})**
Language: __{info['language']}__
License: `{repo_license}`
Stars: {info['stargazers_count']}
Forks: {info['forks_count']}
Open issues: {info['open_issues_count']}
Archived: {archived}
Clone: `git clone {info['git_url']}`
Downloads: [Zip]({zip_url}), [Tarball]({tarball_url})
Description: __{info['description']}__"""
    await message.reply(
        text,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Click to visit", url=info['html_url'])]]
        )
    )
