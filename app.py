from flask import Flask, render_template, request, url_for, flash, redirect, session
from werkzeug.exceptions import abort
import bot
import json


application = Flask(__name__)
application.config.from_pyfile("app.config")


@application.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@application.route("/<string:botname>", methods=("GET", "POST"))
def index(botname):
    print("." * 80)
    print(botname)

    if request.method == "POST":
        text = request.get_data().decode("utf-8")
        if text:
            # bot.main(json.loads(text))
            bot.main(botname)
        return {"statusCode": 200}

    if request.method == "GET":
        return render_template("404.html"), 404


if __name__ == "__main__":
    application.run(host="0.0.0.0")
