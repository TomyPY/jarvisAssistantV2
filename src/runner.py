from telegram_helper import bot
from telebot.asyncio_filters import StateFilter, IsDigitFilter
import asyncio
from check_reminders import reminders_loop

async def main():

    try:
        bot.add_custom_filter(StateFilter(bot))
        bot.add_custom_filter(IsDigitFilter())
        await asyncio.gather(bot.polling(non_stop=True, timeout=40), reminders_loop())

    except Exception as e:
        print(e)

if __name__=="__main__":
    asyncio.run(main())
