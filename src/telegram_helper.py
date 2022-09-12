from operator import indexOf
import re
import os
import csv
import json
import traceback

from telebot.async_telebot import AsyncTeleBot

from config import TELEGRAM_TOKEN
from exceptions import *
from functions import *

bot=AsyncTeleBot(token=TELEGRAM_TOKEN)

chat={}

#START COMMAND, SIMPLE TEXT
@bot.message_handler(func=lambda message:message.text.lower().split("@")[0]=="/start")
async def welcome_and_explanation(message):

    cid=message.chat.id

    #START MSG
    await bot.send_message(cid, 'Hi, im Jarvis!\nI will help you with anything you need :)\n\nType /help to see all the commands')

#HELP COMMAND WITH ALL THE COMMANDS
@bot.message_handler(func=lambda message:message.text.lower().split("@")[0]=="/help")
async def help_commands(message):
    #HELP MSG
    await bot.send_message(message.chat.id, 'The commands are:\n-/start  - To start the bot\n-/help - To see the commands\n-/game_price - See a game price, parameters: NAME\n-/track_list - To see all games in track list\n-/track_list_add - To add a game into the waitlist, parameters: NAME\n-/track_list_remove - To remove a game from tracklist, parameters: NAME')

@bot.message_handler(func=lambda message:message.text.lower().split("@")[0].split(" ")[0]=="/game_price")
async def search_game(message):
    #Variables

    cid=message.chat.id
    msg=message.text

    try:
        #Manage error
        if len(msg.split(" "))<2:
            raise missingParameters("Missing parameters look help section for more details")
        
        #name of the game to search
        game_name=" ".join(msg.split(" ")[1:])
    

        #Iterate over all data files and get the game with price
        txt=''
        for file in os.listdir('../PriceTrackerV2/data'):
            txt+='\n'
            with open("../PriceTrackerV2/data"+f"/{file}", 'r', encoding='utf8') as read_file:
                file_csv=csv.reader(read_file)

                for row in file_csv:
                    
                    if game_name.lower() in row[0].lower():

                        if 'PS4' in file:
                            streamstop_price=f"Pro: {round((((float(row[1])*0.50))+(((float(row[1])*0.50)*0.52)))*1.6, 2)}"
                        elif 'PC' in file or 'Steam' in file:
                            streamstop_price=f"{round((float(row[1])+(float(row[1])*0.25))*1.6, 2)}"
                        elif 'XBX' in file:
                            streamstop_price=f"{round(float(((float(row[1])-(float(row[1])*0.40))+((float(row[1])-(float(row[1])*0.40)))*0.56)*1.6), 2)}"

                        #ADD WEBSITE NAME
                        website=''
                        if file=='PS4.csv':
                            website='Official Website PS4'
                        elif file=='XBX.csv':
                            website='Official Website XBX'


                        if cid==123:
                            txt+=f"\nName: {row[0]} Original price: {row[1]} StreamStop Price: {streamstop_price} Earn:NPR {streamstop_price-float(row[1])} Website: {website if website!='' else file.replace('.csv', '')}"
                        else:
                            txt+=f"\nName: {row[0]} Price: NPR {streamstop_price} Website: {website if website!='' else file.replace('.csv', '')}"
        
                
        await bot.send_message(cid, f'This are the prices for that game!\n{txt}')

    except Exception as e:
        print(e)

@bot.message_handler(commands=['track_list'])
async def track_list(message):
    print("TRACK_LIST COMMAND EXECUTED")

    cid=message.chat.id
    msg=message.text

    try:
        with open('src\DatabaseTracking.json', encoding='utf8') as f:
            data=json.load(f)
            games=data['games']
            f.close()

        txt=''
        if cid==123:
            for game in games:
                txt+=f"Name: {game['name'] + ' ' +game['platform']} Original Price: NPR {game['original_price']} StreamStop price: NPR {game['streamstop_price']} Earn: NPR {float(game['streamstop_price'])-float(game['original_price'])} Website: {game['website']}\n\n"
        else:
            for game in games:
                txt+=f"Name: {game['name'] + ' ' +game['platform']} Price: NPR {game['streamstop_price']} Website: {game['website']}\n\n"
        await bot.send_message(cid, f"List of games on tracking:\n\n{txt}")

    except Exception as e:
        print(e)
        await bot.send_message(cid, "You don't have a track list yet, or an error has occured")

@bot.message_handler(commands=['track_list_add'])
async def track_list_add(message):
    
    cid=message.chat.id
    msg=message.text
    pmts=msg.split(" ")[1:]

    try:
        if len(pmts)<1:
            raise missingParameters("There are parameters missing, please refer to help section")

        game_name=" ".join(pmts)

        #GET DATA OF TRACKING FILE
        with open('src\DatabaseTracking.json', encoding='utf8') as f:
            data=json.load(f)
            f.close()

        #Iterate over all data files
        for file in os.listdir('../PriceTrackerV2/data'):

            #ADD WEBSITE NAME
            website=''
            if file=='PS4.csv':
                website='Official Website PS4'
            elif file=='XBX.csv':
                website='Official Website XBX'

            #CHECKING ALL DATABASES OF PRICES
            with open("../PriceTrackerV2/data"+f"/{file}", 'r', encoding='utf8') as read_file:
                file_csv=csv.reader(read_file)
             
                for row in file_csv:
                    print(row)
                    if game_name in row[0].lower():
            
                        if 'PS4' in file:
                            streamstop_price=f"Pro: {round((((float(row[1])*0.50))+(((float(row[1])*0.50)*0.52)))*1.6, 2)} Plus: {round(((float(row[1])-((float(row[1])*0.25)))+(((float(row[1])-((float(row[1])*0.25)))*0.30)))*1.6, 2)}"
                        elif 'PC' in file or 'Steam' in file:
                            streamstop_price=f"{round((float(row[1])+(float(row[1])*0.25))*1.6, 2)}"
                        elif 'XBX' in file:
                            streamstop_price=f"{round(float(((float(row[1])-(float(row[1])*0.40))+((float(row[1])-(float(row[1])*0.40)))*0.56)*1.6), 2)}"

                        #ADD THE NEW GAME TO THE TRACKING DATABASE
                        game={
                            'name':re.sub('[^A-Za-z0-9 ]+', '', row[0]),
                            'original_price':row[1],
                            'streamstop_price':streamstop_price,
                            'platform':file.replace('.csv', '').replace('Allkeys', ''),
                            'website':website if website!='' else file.replace('.csv','')
                        }


                        data['games'].append(game)
                        break
                read_file.close()

        #WRITE NEW DATA TO TRACKING FILE
        with open('src\DatabaseTracking.json', 'w', encoding='utf8') as f:
            print(data)
            json.dump(data, f)
            f.close()

        await track_list(message)

    except Exception as e:
        print(traceback.format_exc())
        await bot.send_message(cid, e)

@bot.message_handler(commands=['track_list_remove'])
async def track_list_remove(message):
    cid = message.chat.id
    msg = message.text
    pmts = msg.split(" ")[1:]

    try:
        if len(pmts)<1:
            raise missingParameters("There are parameters missing, please refer help section")
        
        game_name=pmts[1]

        with open('src/DatabaseTracking.json') as f:
            data=json.load(f)
            f.close()
        
        for game in data['games']:
            if game_name.lower() in game['name'].lower():
                del data['games'][data['games'].index(game)]
                break

        with open('src/DatabaseTracking.json', 'w', encoding='utf8') as f:
            json.dump(data, f)
            f.close()

        await track_list(message)

    except Exception as e:
        await bot.send_message(cid, e)

# @bot.message_handler(commands=['send_email'])
# async def send_email(message):
#     cid=message.chat.id
#     msg=message.text
#     pmts=msg.split(" ")[1:]

#     try:
#         if len(msg)<1:
#             raise missingParameters("There are missing parameters, refer help section")
        


#     except:


# #SET A REMINDER
# @bot.message_handler(func=lambda message:message.text.lower().split("@")[0].split(" ")[0]=="/set_reminder")
# async def set_reminder(message):
    # try:
    #     #async DEFINING VARIABLES
    #     cid=message.chat.id
    #     msg=message.text

    #     #ONLY ACCEPT 2 PARAMETERS
    #     if len(msg.split(" "))<=2:
    #         raise missingParameters()
        
    #     note=msg.split('"')[1]
    #     date=msg.split('"')[2]

    #     task=asyncio.create_task(reminderAlarm(note, date))



            
    # except missingParameters as e:
    #     await bot.send_message(cid, "This command need 2 parameters. 1.Note 2.Datetime")
    # except unknownDatetime as e:
    #     await bot.send_message(cid, f"{e}\n Example: Year-Month-Day Hour:Minutes:Seconds")