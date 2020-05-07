#!/usr/bin/env python
"""This module is a Telegram bot that scraps and send CompTrain WODs"""

from datetime import datetime
import logging
import os
import sys
from time import sleep
import sqlite3
from sqlite3 import Error
import bs4
import requests
import schedule
import telegram




LOGGER = logging.getLogger("logger")
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

if "DEBUG" in os.environ:
    LOGGER.setLevel(logging.DEBUG)
    LOGGER.debug("DEBUG MODE")
else:
    LOGGER.setLevel(logging.INFO)


def clean_nested(item):
    """
    Clean nested HTLM item
    """
    if item.em:
        for i in item.em.find_all("strong"):
            i.parent.unwrap()
    if item.strong:
        for i in item.strong.find_all("em"):
            i.parent.unwrap()

    return item


def clean_html(item):
    """
    Clean HTML scrapped content
    """
    cleaned_item = clean_nested(item)

    buff = ""
    for element in cleaned_item(text=lambda text: isinstance(text, bs4.Comment)):
        element.extract()
    # Replace br with \n
    for br_element in cleaned_item.find_all("br"):
        LOGGER.debug("Removing br tag %s", br_element)
        br_element.extract()
    for span_element in cleaned_item.find_all("span"):
        LOGGER.debug("Removing span tag %s", span_element)
        span_element.unwrap()
    if cleaned_item.name == "p":
        cleaned_item.name = "br"
        cleaned_item.attrs = {}
        buff += str(cleaned_item)
    if cleaned_item.name == "h2":
        cleaned_item.string = cleaned_item.string.upper()
        cleaned_item.name = "strong"
        cleaned_item.attrs = {}
        buff += f"\n\n{cleaned_item}\n\n"

    buff = buff.replace("<br>", "")
    buff = buff.replace("</br>", "\n\n")

    return buff


def get_page(page_context):
    """
    Scrape CompTrain page
    """
    user_agent = ("Mozilla/5.0 (X11; Linux x86_64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/74.0.3729.131 Safari/537.36"
                 )

    headers = {
        "User-Agent": user_agent
    }

    allowed_contexts = ["wod", "home-gym"]
    if page_context in allowed_contexts:
        wod_page = "https://comptrain.co/" + page_context
    else:
        print("Invalid WOD value: allowed values are 'wod' or 'home-gym'")
        sys.exit(1)

    scrapped_page = requests.get(wod_page, headers=headers)
    scrapped_page.raise_for_status()  # if error it will stop the program
    return scrapped_page.text


def parse_page(page_source):
    """
    Parse text for foods
    """
    soup = bs4.BeautifulSoup(page_source, "html.parser")

    return soup


def parse_wod_date(scrapped_page: bs4.BeautifulSoup):
    """
    Find latest published WOD date
    """
    wod_date = scrapped_page.findAll("div", {"class": "wod-date"}, limit=1)[0].h5.get_text()

    return wod_date




def parse_wod_content(scrapped_page: bs4.BeautifulSoup, wod_date: str, wod_type: slice, html_class: str):
    """
    Parse WOD infos
    """

    my_divs = scrapped_page.findAll("div", {"class": html_class}, limit=2)[wod_type]
    sections = my_divs[0].find_all(["p", "h2", "h3"])

    strong_wod_date = f"<strong>{wod_date.upper()}</strong>\n\n"
    buff = f"{strong_wod_date}"
    for item in sections:
        if not item.has_attr("style") or item.name == "h2" or item.name == "h3":
            buff = "%s%s" % (buff, clean_html(item))

    return buff


def send_message(token, chat_id, message):
    """
    Send a Telegram message
    """
    bot = telegram.Bot(token=token)

    bot.send_message(
        chat_id=chat_id, text=message, parse_mode="html", disable_notification=True
    )

    LOGGER.info("Sending msg: %s", message)


def create_connection(db_file):
    """ Create a database connection to a SQLite database """
    db_connection = None
    try:
        db_connection = sqlite3.connect(db_file)
        print("Using sqlite version", sqlite3.version)
    except Error as error:
        print(error)

    return db_connection


def init_database(db_connection):
    """ Init a sqlite database """
    try:
        db_connection.execute('''CREATE TABLE messages
                     (date text NOT NULL)''')
    except Error as error:
        print(error)

    try:
        db_connection.execute('''CREATE UNIQUE INDEX idx_dates
                        ON messages(date)''')
    except Error as error:
        print(error)


def check_message_event(db_connection, wod_date):
    """
    Check if the current WOD publish event exists in the DB
    """

    raw_date = str(wod_date.split('//')[1].strip())
    tmp_date = datetime.strptime(raw_date, "%m.%d.%Y")
    true_date = str(tmp_date.strftime("%Y-%m-%d"))

    try:
        result = db_connection.execute("SELECT* from messages where date = ('%s')" % true_date)

    except Error as error:
        print(error)

    return result


def store_message_event(db_connection: object, wod_date: object) -> object:
    """
    Store the date of the current published WOD to avoid duplicated Telegram messages
    """

    raw_date = str(wod_date.split('//')[1].strip())
    tmp_date = datetime.strptime(raw_date, "%m.%d.%Y")
    true_date: str = str(tmp_date.strftime("%Y-%m-%d"))

    try:
        db_connection.execute("INSERT INTO messages VALUES ('%s')" % true_date)
        db_connection.execute("DELETE FROM messages where date != ('%s')" % true_date)
        db_connection.commit()

    except Error as error:
        print(error)




def main(db_connection):
    """
    Main logic
    """
    token = os.environ["TELEGRAM_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    wod_goal = os.environ["WOD"]

    if wod_goal == "home1":
        LOGGER.info("home-gym training with equipment selected")
        wod = "home-gym"
        wod_type = slice(0, 1)
        html_class = "col-md-8"
    elif wod_goal == "home2":
        LOGGER.info("home-gym training without equipment  selected")
        wod = "home-gym"
        wod_type = slice(1, 2)
        html_class = "col-md-8"
    elif wod_goal == "open":
        LOGGER.info("open training selected")
        wod = "wod"
        wod_type = slice(0, 1)
        html_class = "col-md-6"
    elif wod_goal == "games":
        LOGGER.info("games training selected")
        wod = "wod"
        wod_type = slice(1, 2)
        html_class = "col-md-6"
    else:
        print("Invalid WOD value: allowed values are 'open' or 'games' or 'home1' or 'home2'")
        sys.exit(1)

    scrapped_page = get_page(wod)
    parsed_page = parse_page(scrapped_page)
    wod_date = parse_wod_date(parsed_page)
    wod_content = parse_wod_content(parsed_page, wod_date, wod_type, html_class)
    check = check_message_event(db_connection, wod_date)

    if check.fetchone() is None:
        send_message(token, chat_id, wod_content)
        store_message_event(db_connection, wod_date)
    else:
        LOGGER.info("WOD already sent")


if __name__ == "__main__":
    LOGGER.info("Starting at %s", datetime.now())
    if "WOD" in os.environ:
        if os.environ["WOD"] in ["home1", "home2", "open", "games"]:
            DB_CONNECTION = create_connection(os.environ["WOD"] + "_" + "events.db")
            init_database(DB_CONNECTION)
            main(DB_CONNECTION)
            if not "DEBUG" in os.environ:
                schedule.every(30).minutes.do(main, DB_CONNECTION)
                LOGGER.info("Starting cronjob")
                while True:
                    logging.debug("Time %s", datetime.now())
                    schedule.run_pending()
                    sleep(30)
        else:
            LOGGER.error("Invalid WOD value")
            exit(1)
    else:
        LOGGER.error("Missing WOD parameter")
        exit(1)



