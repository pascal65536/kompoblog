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


def get_location(message_json):
    """"
    Добудем локацию
    """
    location = message_json.get("location", {})
    location_ret = {
        "latitude": location.get("latitude"),
        "longitude": location.get("longitude"),
    }
    if location_ret.get("latitude") and location_ret.get("longitude"):
        return location_ret
    return None


def get_document(message_json):
    """"
    Добудем документ
    """
    document = message_json.get("document", {})
    document_ret = {
        "file_id": document.get("file_id"),
        "file_name": document.get("file_name"),
        "mime_type": document.get("mime_type"),
        "caption": message_json.get("caption"),
    }
    if document_ret.get("file_id"):
        return document_ret
    return None


def get_photo(message_json):
    """"
    Добудем фото
    """
    for photo in message_json.get("photo", []):
        photo_ret = {
            "file_id": photo["file_id"],
            "caption": message_json.get("caption"),
        }
        return photo_ret
    return None


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
    Добудем имя отправителя
    """
    full_name_lst = [
        message_json.get("from", {}).get("first_name"),
        message_json.get("from", {}).get("last_name"),
        message_json.get("from", {}).get("username"),
    ]
    return " ".join([x for x in full_name_lst if x is not None])


def main(upd=dict(), bot_name=None):
    bot_name = bot_name or "pascal65536"

    token = settings.bot_dct[bot_name]["token"]
    sender_id = settings.bot_dct[bot_name]["sender_id"]
    chat_id = settings.bot_dct[bot_name]["chat_id"]

    if not upd:
        return False

    if not upd["update_id"]:
        return False

    if "my_chat_member" in upd:
        return None

    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage?parse_mode=html&text={upd}&chat_id={sender_id}"
        _ = requests.get(url=url).json()
    except Exception:
        print("Ошибка в `sendMessage`")

    if upd["message"]:
        message = upd["message"]
        document_dct = get_document(message)
        location_dct = get_location(message)
        photo_dct = get_photo(message)
        sticker_id = get_sticker(message)
        poll_dct = get_poll(message)
        text_lst = [
            f"<b>Отправитель: {get_sender_name(message)}</b>",
            f"<i>Дата: {get_date(message)}</i>",
            f"Сообщение: {get_text(message)}",
            f"<code>Отправитель ID: {get_sender_id(message)}</code>",
            f"<code>Чат ID: {get_chat_id(message)}</code>",
        ]
        print("document_dct", document_dct)
        print("location_dct", location_dct)
        print("photo_dct", photo_dct)
        print("sticker_id", sticker_id)
        print("poll_dct", poll_dct)

        # Напишем в чат
        text = "Спасибо за Ваше обращение! Ожидайте ответа"
        try:
            if text_lst:
                text = "\n".join(text_lst)
            key = "sendMessage"
            url = f"https://api.telegram.org/bot{token}/{key}?chat_id={chat_id}&text={text}&parse_mode=html"
            if location_dct:
                key = "sendLocation"
                url = f"https://api.telegram.org/bot{token}/{key}?chat_id={chat_id}&caption={text}&latitude={location_dct['latitude']}&longitude={location_dct['longitude']}&parse_mode=html"
            elif document_dct:
                key = "sendDocument"
                if text_lst:
                    text_lst[
                        2
                    ] = f"Сообщение: {document_dct['caption']} {get_text(message)}"
                    text = "\n".join(text_lst)
                url = f"https://api.telegram.org/bot{token}/{key}?chat_id={chat_id}&caption={text}&document={document_dct['file_id']}&file_name={document_dct['file_name']}&mime_type={document_dct['mime_type']}&parse_mode=html"
            elif poll_dct:
                key = "sendPoll"
                url = f"https://api.telegram.org/bot{token}/{key}?chat_id={chat_id}&question={poll_dct.get('question')}&options={json.dumps(poll_dct.get('options'))}"
            elif sticker_id:
                key = "sendSticker"
                url = f"https://api.telegram.org/bot{token}/{key}?chat_id={chat_id}&sticker={sticker_id}"
            elif photo_dct:
                key = "sendPhoto"
                if text_lst:
                    text_lst[
                        2
                    ] = f"Сообщение: {photo_dct['caption']} {get_text(message)}"
                    text = "\n".join(text_lst)
                url = f"https://api.telegram.org/bot{token}/{key}?chat_id={chat_id}&photo={photo_dct['file_id']}&caption={text}&mime_type=multipart/form-data&parse_mode=html"  #
            _ = requests.get(url=url).json()
        except Exception as e:
            print("Ошибка в `sendMessage`")
            time.sleep(settings.timeout)

    return True


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
        "update_id": 123883571,
        "message": {
            "message_id": 27906,
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
            "date": 1650739670,
            "photo": [
                {
                    "file_id": "AgACAgIAAxkBAAJtAmJkSdYKg3N3zToRyxeI4g5-zuzfAALMvDEbAoggS9UbcgzOOkvWAQADAgADcwADJAQ",
                    "file_unique_id": "AQADzLwxGwKIIEt4",
                    "file_size": 1376,
                    "width": 67,
                    "height": 90,
                },
                {
                    "file_id": "AgACAgIAAxkBAAJtAmJkSdYKg3N3zToRyxeI4g5-zuzfAALMvDEbAoggS9UbcgzOOkvWAQADAgADbQADJAQ",
                    "file_unique_id": "AQADzLwxGwKIIEty",
                    "file_size": 17070,
                    "width": 239,
                    "height": 320,
                },
                {
                    "file_id": "AgACAgIAAxkBAAJtAmJkSdYKg3N3zToRyxeI4g5-zuzfAALMvDEbAoggS9UbcgzOOkvWAQADAgADeAADJAQ",
                    "file_unique_id": "AQADzLwxGwKIIEt9",
                    "file_size": 70804,
                    "width": 597,
                    "height": 800,
                },
                {
                    "file_id": "AgACAgIAAxkBAAJtAmJkSdYKg3N3zToRyxeI4g5-zuzfAALMvDEbAoggS9UbcgzOOkvWAQADAgADeQADJAQ",
                    "file_unique_id": "AQADzLwxGwKIIEt-",
                    "file_size": 119161,
                    "width": 956,
                    "height": 1280,
                },
            ],
            "caption": "236",
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
    document = {
        "update_id": 123883564,
        "message": {
            "message_id": 27883,
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
            "date": 1650726016,
            "document": {
                "file_name": "people.json",
                "mime_type": "application/json",
                "file_id": "BQACAgIAAxkBAAJs62JkFICKtCqUghTgcYKcDsEbbiztAAIlGwACAoggSxM3ZsHzeVruJAQ",
                "file_unique_id": "AgADJRsAAgKIIEs",
                "file_size": 37276,
            },
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
    doc = {
        "update_id": 123883577,
        "message": {
            "message_id": 27945,
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
            "date": 1650741836,
            "document": {
                "file_name": "Правила жизни Катрин Денев.odt",
                "mime_type": "application/vnd.oasis.opendocument.text",
                "file_id": "BQACAgIAAxkBAAJtKWJkUkxYOkLb6282qspwK_YsXy5PAAL0HAACAoggS9ooppF3op-VJAQ",
                "file_unique_id": "AgAD9BwAAgKIIEs",
                "file_size": 23397,
            },
            "caption": "Правила жизни",
        },
    }
    spam1 = {
        "update_id": 123883594,
        "my_chat_member": {
            "chat": {
                "id": -1001117322430,
                "title": "DIY24 ♻️",
                "username": "diy24",
                "type": "channel",
            },
            "from": {
                "id": 157917304,
                "is_bot": False,
                "first_name": "Сергей",
                "last_name": "Пахтусов",
                "username": "pascal65536",
                "language_code": "ru",
            },
            "date": 1650764602,
            "old_chat_member": {
                "user": {
                    "id": 234458994,
                    "is_bot": True,
                    "first_name": "pascal65536",
                    "username": "pascal65536_bot",
                },
                "status": "left",
            },
            "new_chat_member": {
                "user": {
                    "id": 234458994,
                    "is_bot": True,
                    "first_name": "pascal65536",
                    "username": "pascal65536_bot",
                },
                "status": "administrator",
                "can_be_edited": False,
                "can_manage_chat": True,
                "can_change_info": True,
                "can_post_messages": True,
                "can_edit_messages": True,
                "can_delete_messages": True,
                "can_invite_users": True,
                "can_restrict_members": True,
                "can_promote_members": False,
                "can_manage_video_chats": True,
                "is_anonymous": False,
                "can_manage_voice_chats": True,
            },
        },
    }

    rez = main(spam1)
    print(rez)
