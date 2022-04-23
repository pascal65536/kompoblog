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
        text = request.get_json(force=True)
    except Exception as e:
        print(f'index: {e=}')
    finally:
        text = f'{request.get_data()}\n{request.headers}\n{request.method}'

    url = f'https://api.telegram.org/bot{settings.token}/sendMessage?parse_mode=html&text={text}&chat_id={settings.chat_id}'
    res = requests.post(url)
    return {'statusCode': 200}
    

if __name__ == "__main__":
   application.run(host='0.0.0.0')
