from pyrogram import Client, filters,enums
from datetime import datetime, timedelta
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
        "I'm Pdisk Downloader bot. Just send me link and get the video\n⚠️Note :`I can upload upto 2GB`\n`if files are greater than 2GB I'll provide direct download link`\nCreated by @yssprojects",
        reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="Join Channel ❤️",url="https://t.me/yssprojects")
                    ],
                    [
                        InlineKeyboardButton("🔎 Search Files", switch_inline_query_current_chat="")
                    ]
                ]
            )
        )


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
            if 'file_name' in file:
                pass
            else:
                details = await get_details(f"seshu/{id}")
                file_name = await filenam(details['title'])
                size = details['size']
                osize = details['osize']
                file['file_size'] = size
                file['file_name'] = file_name
                file['file_size_bytes'] = osize
                mycol.update_one({'_id': id}, {'$set': file})

            if os.path.exists(f"{id}.mp4"):
                current_time_utc = datetime.utcnow()
                ist_offset = timedelta(hours=5, minutes=30)
                current_time_ist = current_time_utc + ist_offset
                time_with_seconds = current_time_ist.strftime("%Y-%m-%d %H:%M:%S")
                await query_callback.message.edit_text(f"✋`Stop someone is downloading the video please try again using try now button`\nUpdated at {time_with_seconds}",
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
                file_name,total_size,size = await download(id,query_callback)
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
                mycol.insert_one({"_id":id,"file_id":document.document.file_id,"file_name":file_name, "file_size_bytes":total_size,"file_size":size})
                time.sleep(3)
                try:
                  await bot.send_document(document=document_id,chat_id=DUMP_ID,caption=f"Downloaded By [{chat_id}](tg://user?id={chat_id})")
                except:
                  pass

@bot.on_inline_query()
async def inline(bot, query_inline):
    text = str(query_inline.query).lower()
    results = mycol.find()
    data = [i for i in results if 'file_name' in i]
    matches = [item for item in data if text in item['file_name'].lower()]
    results = []
    if matches:
        length = min(len(matches), 50)
        for i in range(length):
            results.append(
                InlineQueryResultCachedDocument(
                title=matches[i]['file_name'],
                document_file_id = matches[i]['file_id'],
                description = matches[i]['file_size'],
                caption=f"`{matches[i]['file_name']}`\n\n{matches[i]['file_size']}\n@yssprojects"
                )
            )
    else:
        results.append(
            InlineQueryResultDocument(
            title="No Video Found",
            document_url="https://i.ibb.co/28LJjt3/thumb.jpg",
            description="Join @yssprojects",
            thumb_url="https://i.ibb.co/28LJjt3/thumb.jpg"
            )
        )
    await bot.answer_inline_query(query_inline.id,results)

if __name__ == "__main__":
  myclient = pymongo.MongoClient(DATABASE_URL)
  mydb = myclient["iseshu"]
  mycol = mydb["files"]
  bot.run()
