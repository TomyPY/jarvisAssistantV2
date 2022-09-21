from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

def start_menu():
    markup=InlineKeyboardMarkup(row_width=3)
    
    bt1=InlineKeyboardButton("Track list", callback_data='track_list')
    bt2=InlineKeyboardButton("Add to Track List", callback_data="track_list_add")
    bt3=InlineKeyboardButton("Remove from Track List", callback_data="track_list_remove")
    bt4=InlineKeyboardButton("Game price", callback_data="game_price")
    bt5=InlineKeyboardButton("Show reminders", callback_data="show")
    # bt5=InlineKeyboardButton("Close", callback_data="close")

    markup.add(bt1,bt2,bt3,bt4, bt5)

    return markup