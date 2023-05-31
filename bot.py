from pyrogram import Client, filters,enums
from pyrogram.types import *
from helper import get_details,convert_size
from download import download,upload
from helper import filenam
from os import environ
import pymongo
import time
import os


API_ID = environ.get('API_ID')
API_HASH = environ.get('API_HASH')
BOT_TOKEN = environ.get('BOT_TOKEN')
DUMP_ID = environ.get('DUMP_ID')
DATABASE_URL = environ.get('DATABASE_URL')
bot = Client('pdisk bot',
             api_id=API_ID,
             api_hash=API_HASH,
             bot_token=BOT_TOKEN,
             workers=50,
             sleep_threshold=10)



@bot.on_message(filters.command('start') & filters.private)
async def start(bot, message):
    await message.reply(
        f"**Hi {message.chat.first_name}!**\n\n"
        "I'm Pdisk Downloader bot. Just send me link and get the video\n⚠️Note :`I can upload upto 2GB`\n`if files are greater than 2GB I'll provide direct download link`\nCreated by @yssprojects")


@bot.on_message(filters.regex(r'https?://pdisk\.pro/[^\s]+') & filters.private)
async def link_handler(bot, message):
    link = message.matches[0].group(0)
    chat_id = message.chat.id
    await bot.send_chat_action(chat_id, enums.ChatAction.TYPING)
    data = await get_details(url=link)
    if data['osize'] < 2147483648:
        await message.reply(
            f"**Title**: `{await filenam(data['title'])}`\n**Size**: `{data['size']}`\n**Created Time**: `{data['created_time']}`",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="📥 Download Video",callback_data=f"download-{data['id']}")
                    ]
                ]
            )
        )
    else:
        await message.reply(
            f"**Title**: `{data['title']}`\n**Size**: `{data['size']}`\n**Created Time**: `{data['created_time']}`",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="📥 Download Video",url=data['link'])
                    ]
                ]
            )
        )


@bot.on_callback_query()
async def callback(client, query_callback):
    global last_time,elapse_time
    if "download-" in query_callback.data:
        id = query_callback.data.split("-")[-1]
        chat_id = query_callback.from_user.id
        file = mycol.find_one({"_id": id})
        if file:
            file_id = file['file_id']
            await bot.send_document(document=file_id,chat_id=chat_id,caption="Join @yssprojects")
            await query_callback.message.delete()
        else:
            if os.path.exists(f"{id}.mp4"):
                await query_callback.message.edit_text(f"✋`Stop someone is downloading the video please try again using try now button`\nUpdated at {time.localtime()}",
                                                       reply_markup=InlineKeyboardMarkup(
                                                            [
                                                                [
                                                                    InlineKeyboardButton(text="📥 Download Video",callback_data=f"download-{id}")
                                                                ]
                                                            ]
                                                       )
                                                       )
            else:
                await query_callback.message.edit_text("`📥 Downloading Please Wait...`")
                file_name,total_size = await download(id,query_callback)
                await query_callback.message.edit_text("`Uploading to telegram...`")
                start_time = time.time()
                document = await bot.send_document(chat_id=chat_id,
                                        document=f"{id}.mp4",
                                        file_name=f"{file_name.replace(' mp4','')}.mp4",
                                        force_document=True,
                                        progress=upload,
                                        thumb = open("thumb.jpg","rb"),
                                        caption="Join @yssprojects",
                                        progress_args=(file_name,query_callback.message.id,chat_id,start_time,id,bot))
                await query_callback.message.delete()
                os.remove(f"{id}.mp4")
                document_id = document.document.file_id
                document = await bot.send_document(document=document_id,chat_id=DUMP_ID,caption=f"Downloaded By [{chat_id}](tg://user?id={chat_id})")
                mycol.insert_one({"_id":id,"file_id":document.document.file_id})
        

if __name__ == "__main__":
  myclient = pymongo.MongoClient(DATABASE_URL)
  mydb = myclient["iseshu"]
  mycol = mydb["files"]
  bot.run()
