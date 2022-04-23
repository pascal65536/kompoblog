import os
import time
import json
from xml.sax.handler import property_lexical_handler
import settings
import requests
import datetime


def digital_divisor(number, radix=10):
    if number == 0:
        return [0]
    ret_lst = list()
    for n in range(100, -1, -1):
        divizor = radix ** n
        num = number // divizor
        number = number - num * divizor
        if num != 0 or len(ret_lst) > 0:
            ret_lst.append(num)
    return ret_lst


def num2str(num):
    num_lst = digital_divisor(num + settings.SALT, radix=len(settings.CODE_STR))
    ret = ""
    for num in num_lst:
        ret += settings.CODE_STR[num]
    return ret


def str2num(str):
    ret = settings.SALT * -1
    for n, ch in enumerate(str[::-1]):
        ret += len(settings.CODE_STR) ** n * settings.CODE_STR.find(ch)
    return ret


def get_poll(message_json):
    """"
    Добудем опрос
    """
    poll_id = message_json.get("poll", None)
    return poll_id


def get_sticker(message_json):
    """"
    Добудем стикер
    """
    sticker_id = message_json.get("sticker", dict()).get("file_id", None)
    return sticker_id


def get_chat_id(message_json):
    """"
    Добудем чат id
    """
    return message_json["chat"]["id"]


def get_sender_id(message_json):
    """"
    Добудем id отправителя
    """
    return message_json["from"]["id"]


def get_photo(message_json):
    """"
    Добудем фото
    """
    # {'file_id': 'AgACAgIAAxkBAAJsumJjsgJzjSO4ys9Xv25eZkpu3xDDAAIyuDEbA-8gS9iwDYVw52FDAQADAgADeQADJAQ',
    # 'file_unique_id': 'AQADMrgxGwPvIEt-', 'file_size': 94565, 'width': 900, 'height': 600}

    photo_ret = None
    for photo in message_json.get("photo", []):
        if not photo_ret:
            photo_ret = photo["file_id"]
            return photo_ret
    return photo_ret


def get_text(message_json):
    """"
    Добудем текст
    """
    return message_json.get("text", "")


def get_date(message_json):
    """"
   Добудем дату
   """
    epochtime = message_json["date"]
    local_datetime = datetime.datetime.fromtimestamp(epochtime)
    datetime_str = local_datetime.strftime("%Y-%m-%d")
    return datetime_str


def get_sender_name(message_json):
    """"
    Добудем имя отвечающего
    """
    full_name_lst = [
        message_json.get("from", {}).get("first_name"),
        message_json.get("from", {}).get("last_name"),
        message_json.get("from", {}).get("username"),
    ]
    return " ".join([x for x in full_name_lst if x is not None])


def main(upd=dict()):
    if not upd:
        return False

    if not upd["update_id"]:
        return False

    if upd["message"]:
        message = upd["message"]
        photo_id = get_photo(message)
        sticker_id = get_sticker(message)
        poll_dct = get_poll(message)
        text_lst = [
            f"<b>Отправитель: {get_sender_name(message)}</b>",
            f"<i>Дата: {get_date(message)}</i>",
            f"Сообщение: {get_text(message)}",
            f"<code>Отправитель ID: {get_sender_id(message)}</code>",
            f"<code>Чат ID: {get_chat_id(message)}</code>",
        ]

        # Напишем в чат
        text = "Спасибо за Ваше обращение! Ожидайте ответа"
        try:
            if text_lst:
                text = "\n".join(text_lst)
            key = "sendMessage"
            url = f"https://api.telegram.org/bot{settings.token}/{key}?chat_id={settings.chat_id}&text={text}&parse_mode=html"
            if poll_dct:
                key = "sendPoll"
                url = f"https://api.telegram.org/bot{settings.token}/{key}?chat_id={settings.chat_id}&question={poll_dct.get('question')}&options={json.dumps(poll_dct.get('options'))}"
            elif sticker_id:
                key = "sendSticker"
                url = f"https://api.telegram.org/bot{settings.token}/{key}?chat_id={settings.chat_id}&sticker={sticker_id}"
            elif photo_id:
                key = "sendPhoto"
                url = f"https://api.telegram.org/bot{settings.token}/{key}?chat_id={settings.chat_id}&photo={photo_id}&caption={text}&mime_type=multipart/form-data&parse_mode=html"
            _ = requests.get(url=url).json()
            print(url)
        except Exception as e:
            print("Ошибка в `sendMessage`")
            time.sleep(settings.timeout)

    return True


# if "message" in upd:
# if not get_text(upd):
# continue
# # Напишем автору, что его ссылка опубликована
# try:
# key = "sendMessage"
# text = "Спасибо за Ваше обращение! Ожидайте ответа"
# if get_text(upd) == "/start":
# text = f"Здравствуйте, {get_sender_name(upd)}!\n\nНапишите свой вопрос и вам ответят в ближайшее время."
# sender_id = get_sender_id(upd)
# url = f"https://api.telegram.org/bot{settings.token}/{key}?chat_id={sender_id}&text={text}&parse_mode=html"
# _ = requests.get(url=url).json()
# except Exception as e:
# print("Ошибка в `sendMessage`")
# time.sleep(timeout)

# if get_text(upd) == "/start":
# continue
# # Напишем в скрытый канал
# try:
# key = "sendMessage"
# sender_id = get_sender_id(upd)
# text = f"{num2str(sender_id)}\n{get_sender_name(upd)}:\n{get_text(upd)}"
# url = f"https://api.telegram.org/bot{settings.token}/{key}?chat_id={settings.chat_id}&text={text}&parse_mode=html"
# _ = requests.get(url=url).json()
# except Exception as e:
# print("Ошибка в `sendMessage`")
# time.sleep(timeout)

# elif "channel_post" in upd:
# if "reply_to_message" not in upd["channel_post"]:
# continue
# sender_chat = upd["channel_post"]["sender_chat"]["id"]
# if str(sender_chat) != settings.chat_id:
# continue
# vopros = upd["channel_post"]["reply_to_message"]["text"]
# otvet = upd["channel_post"]["text"]
# title = upd["channel_post"]["sender_chat"]["title"]
# # Напишем автору из чата
# try:
# key = "sendMessage"
# text = f"<b>{title}:</b> {otvet}"
# sender_id = str2num(vopros.split("\n")[0])
# url = f"https://api.telegram.org/bot{settings.token}/{key}?chat_id={sender_id}&text={text}&parse_mode=html"
# _ = requests.get(url=url).json()
# except Exception as e:
# print("Ошибка в `sendMessage`")
# time.sleep(timeout)

# else:
# print("Странно")


if __name__ == "__main__":
    print("." * 80)

    text = {
        "update_id": 123883529,
        "message": {
            "message_id": 27830,
            "from": {
                "id": 157917304,
                "is_bot": False,
                "first_name": "Сергей",
                "last_name": "Пахтусов",
                "username": "pascal65536",
                "language_code": "ru",
            },
            "chat": {
                "id": 157917304,
                "first_name": "Сергей",
                "last_name": "Пахтусов",
                "username": "pascal65536",
                "type": "private",
            },
            "date": 1650699763,
            "text": "222",
        },
    }
    bot_command = {
        "update_id": 123883530,
        "message": {
            "message_id": 27832,
            "from": {
                "id": 157917304,
                "is_bot": False,
                "first_name": "Сергей",
                "last_name": "Пахтусов",
                "username": "pascal65536",
                "language_code": "ru",
            },
            "chat": {
                "id": 157917304,
                "first_name": "Сергей",
                "last_name": "Пахтусов",
                "username": "pascal65536",
                "type": "private",
            },
            "date": 1650699770,
            "text": "/weather",
            "entities": [{"offset": 0, "length": 8, "type": "bot_command"}],
        },
    }
    photo = {
        "update_id": 123883531,
        "message": {
            "message_id": 27834,
            "from": {
                "id": 157917304,
                "is_bot": False,
                "first_name": "Сергей",
                "last_name": "Пахтусов",
                "username": "pascal65536",
                "language_code": "ru",
            },
            "chat": {
                "id": 157917304,
                "first_name": "Сергей",
                "last_name": "Пахтусов",
                "username": "pascal65536",
                "type": "private",
            },
            "date": 1650700802,
            "photo": [
                {
                    "file_id": "AgACAgIAAxkBAAJsumJjsgJzjSO4ys9Xv25eZkpu3xDDAAIyuDEbA-8gS9iwDYVw52FDAQADAgADcwADJAQ",
                    "file_unique_id": "AQADMrgxGwPvIEt4",
                    "file_size": 1468,
                    "width": 90,
                    "height": 60,
                },
                {
                    "file_id": "AgACAgIAAxkBAAJsumJjsgJzjSO4ys9Xv25eZkpu3xDDAAIyuDEbA-8gS9iwDYVw52FDAQADAgADbQADJAQ",
                    "file_unique_id": "AQADMrgxGwPvIEty",
                    "file_size": 21127,
                    "width": 320,
                    "height": 213,
                },
                {
                    "file_id": "AgACAgIAAxkBAAJsumJjsgJzjSO4ys9Xv25eZkpu3xDDAAIyuDEbA-8gS9iwDYVw52FDAQADAgADeQADJAQ",
                    "file_unique_id": "AQADMrgxGwPvIEt-",
                    "file_size": 94565,
                    "width": 900,
                    "height": 600,
                },
                {
                    "file_id": "AgACAgIAAxkBAAJsumJjsgJzjSO4ys9Xv25eZkpu3xDDAAIyuDEbA-8gS9iwDYVw52FDAQADAgADeAADJAQ",
                    "file_unique_id": "AQADMrgxGwPvIEt9",
                    "file_size": 115209,
                    "width": 800,
                    "height": 533,
                },
            ],
        },
    }
    sticker = {
        "update_id": 123883535,
        "message": {
            "message_id": 27842,
            "from": {
                "id": 157917304,
                "is_bot": False,
                "first_name": "Сергей",
                "last_name": "Пахтусов",
                "username": "pascal65536",
                "language_code": "ru",
            },
            "chat": {
                "id": 157917304,
                "first_name": "Сергей",
                "last_name": "Пахтусов",
                "username": "pascal65536",
                "type": "private",
            },
            "date": 1650702147,
            "sticker": {
                "width": 512,
                "height": 512,
                "emoji": "💭",
                "set_name": "NBstickeriaDMB",
                "is_animated": False,
                "is_video": False,
                "thumb": {
                    "file_id": "AAMCAgADGQEAAmzCYmO3Q2PyzqtWBfENQ32A--t7C2wAAkYFAAIqVRgC_DHRnP4EzPwBAAdtAAMkBA",
                    "file_unique_id": "AQADRgUAAipVGAJy",
                    "file_size": 6734,
                    "width": 128,
                    "height": 128,
                },
                "file_id": "CAACAgIAAxkBAAJswmJjt0Nj8s6rVgXxDUN9gPvrewtsAAJGBQACKlUYAvwx0Zz-BMz8JAQ",
                "file_unique_id": "AgADRgUAAipVGAI",
                "file_size": 49192,
            },
        },
    }
    smile = {
        "update_id": 123883536,
        "message": {
            "message_id": 27844,
            "from": {
                "id": 157917304,
                "is_bot": False,
                "first_name": "Сергей",
                "last_name": "Пахтусов",
                "username": "pascal65536",
                "language_code": "ru",
            },
            "chat": {
                "id": 157917304,
                "first_name": "Сергей",
                "last_name": "Пахтусов",
                "username": "pascal65536",
                "type": "private",
            },
            "date": 1650702185,
            "text": "😱",
        },
    }
    poll = {
        "update_id": 123883538,
        "message": {
            "message_id": 27848,
            "from": {
                "id": 157917304,
                "is_bot": False,
                "first_name": "Сергей",
                "last_name": "Пахтусов",
                "username": "pascal65536",
                "language_code": "ru",
            },
            "chat": {
                "id": 157917304,
                "first_name": "Сергей",
                "last_name": "Пахтусов",
                "username": "pascal65536",
                "type": "private",
            },
            "date": 1650706345,
            "poll": {
                "id": "5411224494456963621",
                "question": "Goal",
                "options": [
                    {"text": "Г", "voter_count": 0},
                    {"text": "О", "voter_count": 0},
                    {"text": "Л", "voter_count": 0},
                ],
                "total_voter_count": 0,
                "is_closed": False,
                "is_anonymous": True,
                "type": "regular",
                "allows_multiple_answers": False,
            },
        },
    }
    location = {
        "update_id": 123883539,
        "message": {
            "message_id": 27850,
            "from": {
                "id": 157917304,
                "is_bot": False,
                "first_name": "Сергей",
                "last_name": "Пахтусов",
                "username": "pascal65536",
                "language_code": "ru",
            },
            "chat": {
                "id": 157917304,
                "first_name": "Сергей",
                "last_name": "Пахтусов",
                "username": "pascal65536",
                "type": "private",
            },
            "date": 1650706358,
            "location": {"latitude": 56.051352, "longitude": 92.977345},
        },
    }
    link = {
        "update_id": 123883541,
        "message": {
            "message_id": 27854,
            "from": {
                "id": 157917304,
                "is_bot": False,
                "first_name": "Сергей",
                "last_name": "Пахтусов",
                "username": "pascal65536",
                "language_code": "ru",
            },
            "chat": {
                "id": 157917304,
                "first_name": "Сергей",
                "last_name": "Пахтусов",
                "username": "pascal65536",
                "type": "private",
            },
            "date": 1650710591,
            "text": "https://www.gornovosti.ru/news/aktualno/item/86286831-30c6-4100-8bd4-68ab26b275b1/\nGornovosti нашли автора таинственных кругов на острове Татышев",
            "entities": [{"offset": 0, "length": 82, "type": "url"}],
        },
    }
    chat_text = {
        "update_id": 123883550,
        "message": {
            "message_id": 7,
            "from": {
                "id": 1087968824,
                "is_bot": True,
                "first_name": "Group",
                "username": "GroupAnonymousBot",
            },
            "sender_chat": {
                "id": -1001674663399,
                "title": "По3.14здим",
                "type": "supergroup",
            },
            "chat": {"id": -1001674663399, "title": "По3.14здим", "type": "supergroup"},
            "date": 1650713185,
            "text": "Привет",
        },
    }
    chat_bot_command = {
        "update_id": 123883551,
        "message": {
            "message_id": 8,
            "from": {
                "id": 1087968824,
                "is_bot": True,
                "first_name": "Group",
                "username": "GroupAnonymousBot",
            },
            "sender_chat": {
                "id": -1001674663399,
                "title": "По3.14здим",
                "type": "supergroup",
            },
            "chat": {"id": -1001674663399, "title": "По3.14здим", "type": "supergroup"},
            "date": 1650713211,
            "text": "/start@pascal65536_bot",
            "entities": [{"offset": 0, "length": 22, "type": "bot_command"}],
        },
    }
    new_chat_photo = {
        "update_id": 123883549,
        "message": {
            "message_id": 6,
            "from": {
                "id": 1087968824,
                "is_bot": True,
                "first_name": "Group",
                "username": "GroupAnonymousBot",
            },
            "sender_chat": {
                "id": -1001674663399,
                "title": "По3.14здим",
                "type": "supergroup",
            },
            "chat": {"id": -1001674663399, "title": "По3.14здим", "type": "supergroup"},
            "date": 1650713153,
            "new_chat_photo": [
                {
                    "file_id": "AgACAgIAAx0CY9FV5wADBmJj4kFj1z4uygLqFnBEmU_NwNp-AAJVwDEbY90ZSxplkfN3WUPqAQADAgADYQADJAQ",
                    "file_unique_id": "AQADVcAxG2PdGUsAAQ",
                    "file_size": 10606,
                    "width": 160,
                    "height": 160,
                },
                {
                    "file_id": "AgACAgIAAx0CY9FV5wADBmJj4kFj1z4uygLqFnBEmU_NwNp-AAJVwDEbY90ZSxplkfN3WUPqAQADAgADYgADJAQ",
                    "file_unique_id": "AQADVcAxG2PdGUtn",
                    "file_size": 26056,
                    "width": 320,
                    "height": 320,
                },
                {
                    "file_id": "AgACAgIAAx0CY9FV5wADBmJj4kFj1z4uygLqFnBEmU_NwNp-AAJVwDEbY90ZSxplkfN3WUPqAQADAgADYwADJAQ",
                    "file_unique_id": "AQADVcAxG2PdGUsB",
                    "file_size": 68701,
                    "width": 640,
                    "height": 640,
                },
            ],
        },
    }
    chat_photo = {
        "update_id": 123883552,
        "message": {
            "message_id": 9,
            "from": {
                "id": 1087968824,
                "is_bot": True,
                "first_name": "Group",
                "username": "GroupAnonymousBot",
            },
            "sender_chat": {
                "id": -1001674663399,
                "title": "По3.14здим",
                "type": "supergroup",
            },
            "chat": {"id": -1001674663399, "title": "По3.14здим", "type": "supergroup"},
            "date": 1650715335,
            "photo": [
                {
                    "file_id": "AgACAgIAAx0CY9FV5wADCWJj6sYCWSVIpGdYDiAFMzLjUY6vAAKOujEbAAEcGUu4lCT2Jo-5IAEAAwIAA3MAAyQE",
                    "file_unique_id": "AQADjroxGwABHBlLeA",
                    "file_size": 1625,
                    "width": 90,
                    "height": 90,
                },
                {
                    "file_id": "AgACAgIAAx0CY9FV5wADCWJj6sYCWSVIpGdYDiAFMzLjUY6vAAKOujEbAAEcGUu4lCT2Jo-5IAEAAwIAA20AAyQE",
                    "file_unique_id": "AQADjroxGwABHBlLcg",
                    "file_size": 23536,
                    "width": 320,
                    "height": 320,
                },
                {
                    "file_id": "AgACAgIAAx0CY9FV5wADCWJj6sYCWSVIpGdYDiAFMzLjUY6vAAKOujEbAAEcGUu4lCT2Jo-5IAEAAwIAA3gAAyQE",
                    "file_unique_id": "AQADjroxGwABHBlLfQ",
                    "file_size": 110985,
                    "width": 800,
                    "height": 800,
                },
                {
                    "file_id": "AgACAgIAAx0CY9FV5wADCWJj6sYCWSVIpGdYDiAFMzLjUY6vAAKOujEbAAEcGUu4lCT2Jo-5IAEAAwIAA3kAAyQE",
                    "file_unique_id": "AQADjroxGwABHBlLfg",
                    "file_size": 163906,
                    "width": 1024,
                    "height": 1024,
                },
            ],
        },
    }

    rez = main(poll)
    print(rez)
