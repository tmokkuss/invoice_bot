import datetime
import pygsheets
import schedule

gs = pygsheets.authorize(service_file='green-webbing-377413-45aa6ca00d62.json')
sh = gs.open('AliceK Pay')
wk1 = sh.sheet1


async def get_the_users():
    users_list = [int(user_id) for user_id in wk1.get_col(3) if user_id != '' and user_id != 'USER_ID:']
    return users_list


async def get_the_info(message):
    today = datetime.datetime.now().strftime("%d.%m.%Y")
    for i in wk1.find(f'{message.chat.id}'):
        list_data = [data for data in wk1.get_row(i.address[0]) if data != '']
        if list_data[0] == today:
            return list_data
    return None


async def get_the_date(message):
    for i in wk1.find(f'{message.chat.id}'):
        list_data = [data for data in wk1.get_row(i.address[0]) if data != '']
        return list_data


async def get_the_date_after_call(callback):
    for i in wk1.find(f'{callback.message.chat.id}'):
        list_data = [data for data in wk1.get_row(i.address[0]) if data != '']
        return list_data



