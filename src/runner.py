from telegram_helper import bot
import asyncio

async def main():

    try:
        await asyncio.gather(bot.infinity_polling())

    except Exception as e:
        print(e)

if __name__=="__main__":
    asyncio.run(main())
