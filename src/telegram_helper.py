import re
import os
import csv
import json
import traceback

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery
from telebot.asyncio_handler_backends import State, StatesGroup

from config import TELEGRAM_TOKEN
from exceptions import *
from functions import *
from keyboards import *

bot=AsyncTeleBot(token=TELEGRAM_TOKEN)

chat={}

class MyStates(StatesGroup):
    name=State()
    name_add=State()
    name_remove=State()
    name_edit_menu=State()


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

#OPEN MENU
@bot.message_handler(func=lambda message:message.text.lower().split("@")[0]=='/menu')
async def open_menu(message):
    cid=message.chat.id
    chat[cid]={}
    markup=start_menu()

    msg=await bot.send_message(message.chat.id, 'Choice a option!', reply_markup=markup)
    chat[cid]["mid"]=msg.id

@bot.callback_query_handler(func=lambda x: True)
async def handle_buttons(call):
    try:
        cid=call.message.chat.id
        data=call.data
       
        
        if data=="track_list":
            await track_list(call.message)
        elif data=='menu':
            markup=start_menu() 
            await bot.edit_message_text('Choice an option!',cid, call.message.id, reply_markup=markup)
        elif data=="track_list_add":
            await track_list_add(call)
        elif data=="track_list_remove":
            await track_list_remove(call)
        elif data=='show':
            await show_reminders(call)
        elif data=="game_price":
            await search_game(call)
        elif data.split(" ")[0]=='edit_message':
            chat[cid]['edit_message_menu']=data.split(" ")[1:]
            await bot.send_message(call.message.chat.id, f"Write the new changes to {data.split(' ')[-1]}")
            await bot.set_state(call.from_user.id, MyStates.name_edit_menu, call.message.chat.id)
        else:
            pass
    except Exception as e:
        print(traceback.format_exc())

@bot.message_handler(func=lambda message:message.text.lower().split("@")[0].split(" ")[0]=="/game_price")
async def search_game(message):
    

    if not isinstance(message, CallbackQuery):
        
        #Variables
        cid=message.chat.id
        msg=message.text

        try:
            #Manage error
            if len(msg.split(" "))<2:
                if msg=='/game_price':
                    raise missingParameters("Missing parameters look help section for more details")
            
            #name of the game to search
            if len(msg.split(" "))>=2 and msg.split(" ")[0].lower()=='/game_price':
                game_name=" ".join(msg.split(" ")[1:])
            else:
                game_name=msg
        
            #Iterate over all data files and get the game with price
            txt=''
            for file in os.listdir('../PriceTrackerV2/data'):
                
                with open("../PriceTrackerV2/data"+f"/{file}", 'r', encoding='utf8') as read_file:
                    file_csv=csv.reader(read_file)

                    for row in file_csv:
                        
                        if game_name.lower() in row[0].lower():

                            if 'ps4' in file.lower():
                                streamstop_price=f"Pro: {round((((float(row[1])*0.50))+(((float(row[1])*0.50)*0.52)))*1.6, 2)}"
                            elif 'pc' in file.lower() or 'steam' in file.lower():
                                streamstop_price=f"{round((float(row[1])+(float(row[1])*0.25))*1.6, 2)}"
                            elif 'xbx' in file.lower():
                                streamstop_price=f"{round(float(((float(row[1])-(float(row[1])*0.40))+((float(row[1])-(float(row[1])*0.40)))*0.56)*1.6), 2)}"

                            #ADD WEBSITE NAME
                            website=''
                            if file=='PS4.csv':
                                website='Official Website PS4'
                            elif file=='XBX.csv':
                                website='Official Website XBX'


                            if cid==123:
                                txt+=f"――――――――――――――――――――――\nName: <b>{row[0]}</b> \nOriginal price: <b>{row[1]}</b> \nStreamStop Price: <b>{streamstop_price}</b> \nEarn:<b>NPR {streamstop_price-float(row[1])} \nWebsite: <b>{website if website!='' else file.replace('.csv', '')}</b>\n"
                            else:
                                txt+=f"――――――――――――――――――――――\nName: <b>{row[0]}</b> \nPrice: NPR <b>{streamstop_price}</b> \nWebsite: <b>{website if website!='' else file.replace('.csv', '')}</b>\n"
                            
                            break

            markup=start_menu()
            await bot.send_message(cid, f'This are the prices for that game!\n{txt}', reply_markup=markup, parse_mode='HTML')

        except Exception as e:
            print(e)

    else:

        #Variables
        cid=message.message.chat.id

        try:
            await bot.set_state(message.from_user.id, MyStates.name, cid)
            await bot.send_message(cid, "Hey! Can you specify the name of the game?")
        except Exception as e:
            print(e)

@bot.message_handler(state=MyStates.name)
async def handle_menu_game_price(message):
    await search_game(message)

@bot.message_handler(func=lambda message:message.text.lower().split("@")[0].split(" ")[0]=="/track_list_remove")
async def track_list_remove(message):


    if not isinstance(message, CallbackQuery):
        cid = message.chat.id
        msg = message.text
        

        try:
            if msg=='/track_list_remove':
                raise missingParameters("Missing parameters look help section for more details")
            
            #name of the game to search
            if len(msg.split(" "))>=2 and msg.split(" ")[0].lower()=='/track_list_remove':
                game_name=" ".join(msg.split(" ")[1:])
            else:
                game_name=msg

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
    else:
        cid=message.message.chat.id

        await bot.set_state(message.from_user.id, MyStates.name_remove, cid)
        await bot.send_message(cid, "Hey! Can you specify the name of the game?")

@bot.message_handler(state=MyStates.name_remove)
async def handler_name_remove_track_list(message):
    await track_list_remove(message)

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
                txt+=f"――――――――――――――――――――――\nName: <b>{game['name'] + ' ' +game['platform']}</b> \nOriginal Price: <b>NPR {game['original_price']}</b> \nStreamStop price: <b>NPR {game['streamstop_price']}</b> \nEarn: <b>NPR {float(game['streamstop_price'])-float(game['original_price'])}</b> \nWebsite: <b>{game['website']}</b>\n"
        else:
            for game in games:
                txt+=f"――――――――――――――――――――――\nName: <b>{game['name'] + ' ' +game['platform']}</b> \nPrice: <b>NPR {game['streamstop_price']}</b> \nWebsite: <b>{game['website']}</b>\n"
        markup=start_menu()
        
        try:

            if chat[cid]["mid"]!=None:
                await bot.edit_message_text(chat_id=cid, message_id=chat[cid]["mid"], text=f"List of games on tracking:\n\n{txt}", reply_markup=markup, parse_mode='HTML')
            else:
                await bot.send_message(cid, f"List of games on tracking:\n\n{txt}", parse_mode='HTML')
        except:
            await bot.send_message(cid, f"List of games on tracking:\n\n{txt}", parse_mode='HTML')
        

    except Exception as e:
        print(e)
        await bot.send_message(cid, "You don't have a track list yet, or an error has occured")

@bot.message_handler(commands=['track_list_add'])
async def track_list_add(message):
    

    if not isinstance(message, CallbackQuery):
        cid=message.chat.id
        msg=message.text

        try:
            if msg.lower()=='/track_list_add':
                raise missingParameters("Missing parameters look help section for more details")

            #name of the game to search
            if len(msg.split(" "))>=2 and msg.split(" ")[0].lower()=='/track_list_add':
                game_name=" ".join(msg.split(" ")[1:])
            else:
                game_name=msg

            print(game_name)

            #GET DATA OF TRACKING FILE
            with open('src\DatabaseTracking.json', encoding='utf8') as f:
                data=json.load(f)
                

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
                      
                        if game_name.lower() in row[0].lower():
                
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
                            print(data)
                            break
                    

            #WRITE NEW DATA TO TRACKING FILE
            with open('src\DatabaseTracking.json', 'w', encoding='utf8') as f:
                print(data)
                json.dump(data, f)
                f.close()

            await track_list(message)

        except Exception as e:
            print(traceback.format_exc())
            await bot.send_message(cid, e)

    else:
        cid=message.message.chat.id
        await bot.set_state(message.from_user.id, MyStates.name_add, cid)
        await bot.send_message(cid, "Hey! Can you specify the name of the game?")

@bot.message_handler(state=MyStates.name_add)
async def handler_name_track_list_add(message):
    await track_list_add(message)

#SET A REMINDER
@bot.message_handler(func=lambda message:message.text.lower().split("@")[0].split(" ")[0]=="/set_reminder")
async def set_reminder(message):
    try:
        #async DEFINING VARIABLES
        cid=message.chat.id
        msg=message.text

        #ONLY ACCEPT 2 PARAMETERS
        if len(msg.split(" "))<=2:
            raise missingParameters()
    
        title=msg.split('"')[1]
        txt=msg.split('"')[3]
        datetime=msg.split('"')[4].strip()

        if re.search("([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2})", datetime.strip()) == None:
            raise unknownDatetime("The correct format of datetime is YYYY-MM-DD HH:MM")

        with open('src\DatabaseTracking.json', encoding='utf8') as f:
            data=json.load(f)
            f.close()

        data["reminders"].append({"title":title, "msg":txt, "datetime":datetime})

        with open('src\DatabaseTracking.json', 'w', encoding='utf8') as f:
                json.dump(data, f)
                f.close()

        await bot.send_message(cid, "Reminder has been saved!")
            
    except missingParameters as e:
        await bot.send_message(cid, "This command need 2 parameters. 1.Note 2.Datetime")
    except unknownDatetime as e:
        await bot.send_message(cid, e)

@bot.message_handler(func=lambda message:message.text.lower().split("@")[0].split(" ")[0]=="/show_reminders")
async def show_reminders(message):
    
    if isinstance(message, CallbackQuery):
        message=message.message
        
  
    cid=message.chat.id

    with open('src\DatabaseTracking.json', encoding='utf8') as f:
        data=json.load(f)
        f.close()
    
    if len(data["reminders"])==0:
        await bot.send_message(message.chat.id, "There is no reminders yet")
        return
    bt0=InlineKeyboardButton("TITLE", callback_data='a')
    bt01=InlineKeyboardButton("NOTE", callback_data='a')
    bt02=InlineKeyboardButton("DATETIME", callback_data='a')
    txt='Here are all the reminders, tap a cell to edit it: '
    keyboard=InlineKeyboardMarkup(row_width=3)
    keyboard.row(bt0, bt01, bt02)
    for reminder in data["reminders"]:
        bt1=InlineKeyboardButton(reminder["title"], callback_data=f'edit_message {data["reminders"].index(reminder)} title')
        bt2=InlineKeyboardButton(reminder["msg"], callback_data=f'edit_message {data["reminders"].index(reminder)} msg')
        bt3=InlineKeyboardButton(reminder["datetime"], callback_data=f'edit_message {data["reminders"].index(reminder)} datetime')
        keyboard.row(bt1, bt2, bt3)
    bt4=InlineKeyboardButton("Return", callback_data="menu")
    keyboard.row(bt4)
    try:

        if chat[message.chat.id]["mid"]!=None:
            await bot.edit_message_text(chat_id=cid, message_id=chat[cid]["mid"], text=f"List of games on tracking:\n\n{txt}", reply_markup=keyboard, parse_mode='HTML')
        else:
            await bot.send_message(message.chat.id, txt, reply_markup=keyboard)
    except:
        await bot.send_message(message.chat.id, txt, reply_markup=keyboard)
    
@bot.message_handler(func=lambda message:message.text.lower().split("@")[0].split(" ")[0]=="/edit_message")
async def edit_message(message):
    try:
        if len(message.text.split(" "))<4:
            raise missingParameters('The correct format is /edit_message title column_to_edit "changes"')
        if message.text.count('"')!=2:
            raise missingParameters('Changes must be under quotes, ex: "Changes"')

        title=message.text.split(" ")[1]
        column=message.text.split(" ")[2]
        changes=message.text.split('"')[1].strip()

        print(changes)

        with open('src\DatabaseTracking.json', encoding='utf8') as f:
            data=json.load(f)
            f.close()
        
        found=False
        for reminder in data["reminders"]:
            if title in reminder["title"]:
                reminder[column]=changes
                found=True
        
        if found==False:
            await bot.send_message(message.chat.id, "The reminder wasnt found!")
            return

        with open('src\DatabaseTracking.json', 'w', encoding='utf8') as f:
                    json.dump(data, f)
                    f.close()

        await bot.send_message(message.chat.id, "Changes saved!")
    except missingParameters as e:
        await bot.send_message(message.chat.id, e)

@bot.message_handler(state=MyStates.name_edit_menu)
async def edit_message_menu(message):
    cid=message.chat.id
    pos=chat[cid]['edit_message_menu'][0]
    column=chat[cid]['edit_message_menu'][1]
    with open('src\DatabaseTracking.json', encoding='utf8') as f:
        data=json.load(f)
        f.close()

    data["reminders"][int(pos)][column]=message.text

    with open('src\DatabaseTracking.json', 'w', encoding='utf8') as f:
                json.dump(data, f)
                f.close()

    await bot.send_message(cid, "Changes saved!")
    
