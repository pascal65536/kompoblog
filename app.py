from flask import Flask, render_template, request, url_for, flash, redirect, session
from werkzeug.exceptions import abort
import os
import time
import json
import settings
import requests


application = Flask(__name__)
application.config.from_pyfile("app.config")


@application.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@application.route("/", methods=("GET", "POST"))
def index():   
    try:
        text = request.get_data().decode('utf-8')
        if text:
            text = json.loads(text)
        # text = {"update_id":123883508, "message":{"message_id":27781,"from":{"id":157917304,"is_bot":false,"first_name":"\u0421\u0435\u0440\u0433\u0435\u0439","last_name":"\u041f\u0430\u0445\u0442\u0443\u0441\u043e\u0432","username":"pascal65536","language_code":"ru"},"chat":{"id":157917304,"first_name":"\u0421\u0435\u0440\u0433\u0435\u0439","last_name":"\u041f\u0430\u0445\u0442\u0443\u0441\u043e\u0432","username":"pascal65536","type":"private"},"date":1650698478,"text":"5689"}}
    except Exception as e:
        print(f'index: {e=}')
        text = f'{request.headers}\n{request.method}'
    finally:
        text = text or 'empty'
    url = f'https://api.telegram.org/bot{settings.token}/sendMessage?parse_mode=html&text={text}&chat_id={settings.chat_id}'
    res = requests.post(url)
    return {'statusCode': 200}
    

if __name__ == "__main__":
   application.run(host='0.0.0.0')
