from flask import Flask, render_template, request, url_for, flash, redirect, session
from werkzeug.exceptions import abort
import settings
import requests


application = Flask(__name__)
application.config.from_pyfile("app.config")


@application.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404



@application.route("/", methods=("GET", "POST"))
def index():   
    # import ipdb; ipdb.sset_trace()
    # searchword = request.args.get('key', '')    
    try:
        text = request.json()
    except Exception as e:
        print(e)
    finally:
        text = f'{request.method}\n{request.headers}'
    url = f'https://api.telegram.org/bot{settings.token}/sendMessage?parse_mode=html&text={text}&chat_id={settings.chat_id}'
    res = requests.post(url)
    return {'statusCode': 200}
    

if __name__ == "__main__":
   application.run(host='0.0.0.0')
