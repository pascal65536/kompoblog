from flask import Flask, render_template, request, url_for, flash, redirect, session
from werkzeug.exceptions import abort
import bot
import json


application = Flask(__name__)
application.config.from_pyfile("app.config")


@application.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@application.route("/1001674663399", methods=("GET", "POST"))
def bottle():
    if request.method in "POST":
        text = request.get_data().decode("utf-8")
        if text:
            bot.main(json.loads(text))
        return {"statusCode": 200}

    if request.method == "GET":
        return render_template("404.html"), 404


@application.route("/", methods="GET")
def index():
    return render_template("404.html"), 404


if __name__ == "__main__":
    application.run(host="0.0.0.0")
