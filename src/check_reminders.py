import datetime
import pytz
import asyncio
import json
from telebot.async_telebot import AsyncTeleBot
from config import TELEGRAM_TOKEN
import traceback

bot=AsyncTeleBot(TELEGRAM_TOKEN)

async def reminders_loop():
    
    current_sec = int(datetime.datetime.now().strftime("%S"))
    delay=0

    if current_sec!=0:
        delay=60-current_sec
    print(delay)
    

    while True:
        try:
            
            with open('src\DatabaseTracking.json', encoding='utf8') as f:
                data=json.load(f)
                f.close()


            now=datetime.datetime.now(pytz.timezone("Asia/Calcutta"))
           
            if len(data["reminders"])!=0:
            
                for reminder in data["reminders"]:
                
                
                    if datetime.datetime.strptime(reminder["datetime"], "%Y-%m-%d %H:%M")<now.replace(tzinfo=None):
                        # await bot.send_message(-1286936192, reminder["msg"])
                        print(reminder["msg"])
                        data["reminders"].pop(data["reminders"].index(reminder))
                        with open('src\DatabaseTracking.json', 'w', encoding='utf8') as f:
                            json.dump(data, f)
                            f.close()

            
                    
        except Exception as e:
            print(traceback.format_exc())
        await asyncio.sleep(10)


