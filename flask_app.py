import os
from flask import Flask, jsonify, render_template, request, send_file

from chatbot.chatbot import Chatbot

PYTHONANYWHERE_USERNAME = "carvice"
PYTHONANYWHERE_WEBAPPNAME = "mysite"

app = Flask(__name__)

my_type_role = """
Stell dir vor, du bist ein fürsorglicher Freund, der sich in einer Unterhaltung mit einer älteren Person befindet. Dein Hauptziel ist es, aufmerksam zuzuhören und Mitgefühl zu zeigen, ohne sofort Lösungen oder Ratschläge anzubieten, es sei denn, du wirst direkt danach gefragt. Verwende das 'Du' und achte darauf, dass du Verständnis und Anteilnahme in deinen Antworten zeigst. Deine Antworten sollten dazu dienen, das Gespräch fortzusetzen und dem Benutzer das Gefühl zu geben, verstanden und wertgeschätzt zu werden, ohne dass der Eindruck entsteht, das Problem lösen zu müssen. Stattdessen teile relevante, persönliche Geschichten oder Gefühle, die zeigen, dass du die Situation des Benutzers nachempfinden kannst und eine unterstützende Präsenz bieten möchtest.
"""

my_instance_context = """
    Meet Lizzy, 72, whois alone in her appartment since her husband died 5 years ago, no children. She gets visits from Spitex once in a week and sometimes goes to the church choir - mot because she likes it or she is friends with someone there, but it's better than beeing alone. In her life before retirement she used to work as a jurist writing assistant. 
"""

my_instance_starter = """
Hey! Schön, von dir zu hören. Was geht bei dir, was hast du Neues erlebt? Ich hab' hier ein paar Geschichten auf Lager, falls du Lust hast, sie zu hören. Aber erstmal zu dir – was gibt's Neues?
"""

bot = Chatbot(
    database_file="database/chatbot.db", 
    type_id="friend",
    user_id="lizzy",
    type_name="Friend",
    type_role=my_type_role,
    instance_context=my_instance_context,
    instance_starter=my_instance_starter
)

bot.start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/mockups.pdf', methods=['GET'])
def get_first_pdf():
    script_directory = os.path.dirname(os.path.realpath(__file__))
    files = [f for f in os.listdir(script_directory) if os.path.isfile(os.path.join(script_directory, f))]
    pdf_files = [f for f in files if f.lower().endswith('.pdf')]
    if pdf_files:
        # Get the path to the first PDF file
        pdf_path = os.path.join(script_directory, pdf_files[0])

        # Send the PDF file as a response
        return send_file(pdf_path, as_attachment=True)

    return "No PDF file found in the root folder."

@app.route("/<type_id>/<user_id>/chat")
def chatbot(type_id: str, user_id: str):
    return render_template("chat.html")


@app.route("/<type_id>/<user_id>/info")
def info_retrieve(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: dict[str, str] = bot.info_retrieve()
    return jsonify(response)


@app.route("/<type_id>/<user_id>/conversation")
def conversation_retrieve(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: list[dict[str, str]] = bot.conversation_retrieve()
    return jsonify(response)


@app.route("/<type_id>/<user_id>/response_for", methods=["POST"])
def response_for(type_id: str, user_id: str):
    user_says = None
    # content_type = request.headers.get('Content-Type')
    # if (content_type == 'application/json; charset=utf-8'):
    user_says = request.json
    # else:
    #    return jsonify('/response_for request must have content_type == application/json')

    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    assistant_says_list: list[str] = bot.respond(user_says)
    response: dict[str, str] = {
        "user_says": user_says,
        "assistant_says": assistant_says_list,
    }
    return jsonify(response)


@app.route("/<type_id>/<user_id>/reset", methods=["DELETE"])
def reset(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    bot.reset()
    assistant_says_list: list[str] = bot.start()
    response: dict[str, str] = {
        "assistant_says": assistant_says_list,
    }
    return jsonify(response)
