# -*- coding: utf-8 -*-

import configparser # храним конфиги для бота

try:
    from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType # для упрощения обращения к этим классам (а то длинновато выходило)
    import vk_api # сама библиотека vk_api
except:
    print('Установите необходимые модули через команду \'pip install -r requirements.txt\' перед запуском скрипта.'); exit()


'''
Методы для отправки сообщений vk_send_message_to_user и vk_send_message_to_chat

Аргументы методов:
[0] vk - обязательный, объект сессии после успешной авторизации и получения доступа к api
[1] user_id и chat_id - обязательный, id пользователя или группы, которым отправляем сообщение
[2] message - текстовое сообщение, обязателен если нет attachments
[3] attachments - вложения, список (до 10), обязателен если нет message
[4] keyboard - необязательный, объект клавиатуры в формате json
'''

def vk_send_message_to_user(vk, user_id, message, attachments = None, keyboard = None):
    vk.messages.send(user_id = int(user_id), random_id = vk_api.utils.get_random_id(), message=message, attachment = attachments, keyboard = keyboard)

def vk_send_message_to_chat(vk, chat_id, message, attachments = None, keyboard = None):
    vk.messages.send(chat_id = int(chat_id), random_id = vk_api.utils.get_random_id(), message=message, attachment = attachments, keyboard = keyboard)

'''
Переопределяем метод в классе, наследующемся от VkBotLongPoll для фикса вылета бота при длительной работе.
Почему он по дефолту вылетает в библиотеке vk_api и почему не сделать так там, для меня загадка...
'''

class MyVkLongPoll(VkBotLongPoll):
    def listen(self):
        while True:
            try: 
                for event in self.check():
                    yield event
            except Exception as e:
                pass

'''
Работаем с файлом конфигурации settings.ini, получаем оттуда данные, а именно - токен и id группы
для авторизации в социальной сети от имени группы. Токен и ID должны быть от одной и той же группы

Нетрудно догадаться, что для работы бота вам нужно вставить свои токен и id группы в settings.ini
'''

config = configparser.ConfigParser()
config.read("settings.ini", encoding="utf8") 

vk_group_token = config['VK']['token'][1:-1]
vk_group_id = int(config['VK']['group_id'][1:-1])

'''
Авторизуемся в социальной сети, используя полученные ранее токен и идентефикатор группы
Сохраняем в переменной vk объект, позволяющий работать с vk api

Подробнее о методах API социальной сети VK можно почитать в оффициальной документации:
    >>> https://vk.com/dev/methods <<<
'''

vk_session = vk_api.VkApi(token=vk_group_token)
longpoll = VkBotLongPoll(vk_session, vk_group_id)
vk = vk_session.get_api()

'''
Приготовления завершены. Начинаем слушать события в группе при помощи LongPoll API и работать с этими событиями.
Скорее всего, Вам чаще всего понадобится работать с событием MESSAGE_NEW (новое сообщение), и реагировать вы 
чаще всего будете именно на него, но если понадобится работать с другими событиями - о них вы можете почитать
по ссылке на оффициальную документацию: 
    >>> https://vk.com/dev/groups_events <<<

Для проверки события достаточно будет провести операцию сравнения event и VkBotEventType.{название события} (для
удобства чтения кода у меня они пишутся большими буквами)
'''

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW: # проверяем, то ли это событие, что нам нужно
        if event.from_user: # событие пришло от пользователя
            if event.obj.text == 'Hello World': # текст сообщения, который нам пришел
                vk_send_message_to_user(vk, event.obj.from_id, 'Бот работает и отвечает на сообщение!') # отвечаем на сообщение
                
                '''
                    event.obj.from_id - id пользователя, который отправил нам сообщение (в личке)
                    event.chat_id - id группового чата, из которого пришло сообщение (если не в личку)
                '''
