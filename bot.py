import datetime
import pytz
import time
import telebot
import os

from expired_task import expired_task

from trello import TrelloClient

client = TrelloClient(
    api_key= os.getenv("TR_KEY"),
    api_secret=os.getenv("TR_SECRET"), 
    token = os.getenv("TR_TOKEN") 
)

TOKEN = os.getenv("TG_TOKEN")
CHAT_ID = os.getenv("TG_CHAT")
print(f'::set-output name=test_report::{TOKEN, CHAT_ID}')

bot = telebot.TeleBot(token = TOKEN)

tz = pytz.timezone('Etc/GMT+3')

def send_wake_up_neo():
    bot.send_message(CHAT_ID, "Меня разбудили и я готов раздавать пинки 🤡")

def send_normal():
   bot.send_message(CHAT_ID, "Дорова! Просроченных тасок нет! Проверяем трелло и продолжаем в том же духе")
   bot.close()

def send_kick(tasks:list[expired_task]):
    lazy_asses = extract_lazy_asses(tasks)
    
    message_text = "Дорова кожанные! Сегодня чествуем ленивые попы следующих товарищей: \n"+ lazy_asses + '\n'
    message_text += extract_discontent(tasks) + '\n Напрягитесь и закройте таски, бля.'
    bot.send_message(CHAT_ID, message_text)

def extract_lazy_asses(tasks:list[expired_task])->str:
    lazy_asses = []
    for t in tasks:
        for ass in t.members:
            lazy_asses.append(ass + '\n') 
    lazy_asses = set(lazy_asses)

    list_of_lazy_asses = ''
    for ass in lazy_asses: list_of_lazy_asses += ass
    return list_of_lazy_asses

def extract_discontent(tasks:list[expired_task])->str:
    discontent = 'Просрочены следующие таски: \n'
    for task in tasks:
        lazy_asses = ''
        for ass in task.members:
            lazy_asses += ass + ' '

        discontent += '🤡 ' + task.text + '\n   "Дата завершения:" ' + str(task.date.date()) + '\n   "Виновники:" ' + lazy_asses + '\n\n' 
    return discontent


def get_incopleted_tasks()->list[expired_task]:
    board = client.get_board("65000ad64a72119159bf8198")
    members_list =  board.get_members()
    todo_expired_cards = get_expired_tasks(board)
    return prepare_expired_tasks(members_list, todo_expired_cards)

def prepare_expired_tasks(members_list, todo_expired_cards)->list[expired_task]:
    expired_tasks = []
    for card in todo_expired_cards:
        members = [m for m in members_list if m.id in card.idMembers]
        members_full_names = []

        for m in members:
            members_full_names.append(m.full_name)

        expired_tasks.append(expired_task(card.name, card.due_date, members_full_names))
    return expired_tasks 

def get_expired_tasks(board)->list:
    todo_list_cards = board.get_list('65000ad64a72119159bf819b').list_cards()  
    todo_list_cards.extend(board.get_list('65000ad64a72119159bf819c').list_cards())

    todo_expired_cards =   [obj for obj in todo_list_cards if obj.due]
    todo_expired_cards = [obj for obj in todo_expired_cards if obj.due_date<datetime.datetime.now(tz)]
    return todo_expired_cards

def main():
    tasks = get_incopleted_tasks()
    if len(tasks) == 0: send_normal()
    else: send_kick(tasks) 

if __name__ == "__main__": 
    #send_wake_up_neo()
    while(1):
        if (((datetime.datetime.now().time().hour==8) or 
             (datetime.datetime.now().time().hour==16))  and
             datetime.datetime.now().time().minute==0) :
            main()
            time.sleep(100)
