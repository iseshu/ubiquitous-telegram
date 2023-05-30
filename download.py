import os
import requests
import time
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client, filters, enums
from helper import get_details, convert_size,filenam

async def download(id, callback_query):
    data = await get_details(url=f"https://pdisk.pro/{id}")
    response = requests.get(data['link'], stream=True)
    total_size = data['osize']
    progress = 0
    last_update_time = start_time = time.time()

    # Download the file in chunks
    with open(f"{id}.mp4", "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                try:
                    f.write(chunk)
                    progress += len(chunk)
                    # Calculate the download speed and ETA
                    elapsed_time = time.time() - start_time
                    speed = progress / elapsed_time if progress > 0 else 0
                    eta = int((total_size - progress) / speed)
                    # Update the progress message every 3 seconds
                    if time.time() - last_update_time > 3:
                        try:
                            message_text = f"📥Downloading Video...\n\n`{await filenam(data['title'])}`\n\n⏳Progress : `{await convert_size(progress)}/{await convert_size(total_size)} ({progress / total_size * 100:.2f}%)`\n\n💨Speed : `{await convert_size(speed)}/s`\n\n⏱️ETA : {time.strftime('%H:%M:%S', time.gmtime(eta))}"
                            await callback_query.message.edit_text(message_text)
                        except:
                            pass
                        last_update_time = time.time()
                except:
                    pass
        f.close()
    await callback_query.message.edit_text("Download complete. Uploading to Telegram...")
    return data['title'],total_size

last_time = time.time()


async def upload(current,total,title,id,chat_id,start_time,bot):
        if round(time.time()-start_time) > 3 and current !=0:
            percentage = (current / total) * 100
            speed = current/ (time.time()-start_time)
            eta = (total - current) / speed if speed > 0 else 0
            progress_message = f"⏫ Uploading to Telegram\n\nTitle:`{await filenam(title)}`\n\n⏳Progress: `{await convert_size(current)}/{await convert_size(total)}` `({percentage:.2f}%)`\n\n"
            progress_message += f"💨Speed: `{await convert_size(speed)}/s`\n\n"
            progress_message += f"ETA: ` {time.strftime('%H:%M:%S', time.gmtime(eta))}\n`"
            await bot.edit_message_text(
             chat_id= chat_id,
             message_id = id,
             text=progress_message
            )
        else:
            pass
