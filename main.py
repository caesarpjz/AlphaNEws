from bs4 import BeautifulSoup

import time
import json 
import requests
import urllib

TOKEN = "822357869:AAFVpW8itlJTLPlZ8_RpTNrba0AD4x2m_RQ"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

# ========================================== NEWS RETRIEVAL ==================================================

def getNYNews():
    page_link = 'https://www.nytimes.com/'
    page_response = requests.get(page_link, timeout=5)

    page_content = BeautifulSoup(page_response.content, "html.parser")

    headlines = []

    for a in page_content.findAll("a"):
        if len(a.findAll("div")) > 0 and len(a.findAll("span")) > 0:
            if len(a.findAll("span", {"class":"credit"})) <= 0:
                headline_title = a.find("div").text
                headline_link = page_link + str(a["href"])
                headlines.append({"title":headline_title, "link":headline_link})

    return headlines

def getVoxNews():
    page_link = 'https://www.vox.com/'
    page_response = requests.get(page_link, timeout=5)

    page_content = BeautifulSoup(page_response.content, "html.parser")

    headlines = []

    count = 0
    for a in page_content.findAll("a", {"data-analytics-link":"article"}):
        link = a["href"]
        title = a.text
        headlines.append({"title":title, "link":link})
        count = count + 1
        if count == 8:
            break

    return headlines

def getBBCNews():
    page_link = 'https://www.bbc.com/'
    page_response = requests.get(page_link, timeout=5)

    page_content = BeautifulSoup(page_response.content, "html.parser")

    headlines = []

    count = 0
    for a in page_content.findAll("a", {"class":"media__link"}):
        link = page_link + a["href"][1:]
        title = a.text[3:].strip()
        headlines.append({"title":title, "link":link})
        count = count + 1
        if count == 10:
            break

    return headlines

def getDailyMailNews():
    page_link = 'https://www.dailymail.co.uk/'
    page_response = requests.get(page_link, timeout=5)

    page_content = BeautifulSoup(page_response.content, "html.parser")

    headlines = []

    count = 0
    for a in page_content.findAll("a", {"itemprop":"url"}):
        link = page_link + a["href"][1:]
        title = a.text
        headlines.append({"title":title, "link":link})
        count = count + 1
        if count == 10:
            break

    return headlines

# ========================================== END ==================================================

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)

def echo_all(updates):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            send_message(text, chat)
        except Exception as e:
            print(e)

def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)
    
def news_text(headlines):
    print(headlines)
    message = ""
    for headline in headlines:
        message = message + headline["title"] + "\n"
        message = message + headline["link"] + "\n\n"

    return message

def replyAll(updates):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            reply(text, chat)
        except Exception as e:
            print(e)

def reply(text, chat):
    if text == '/start':
        send_message("Welcome to the Alpha bot! Please type 'New York Times', 'Vox', 'BBC' or 'Daily Mail' for today's top news!", chat)
    elif text == 'New York Times':
        send_message(news_text(getNYNews()), chat)
    elif text == 'Vox':
        send_message(news_text(getVoxNews()), chat)
    elif text == 'BBC':
        send_message(news_text(getBBCNews()), chat)
    elif text == 'Daily Mail':
        send_message(news_text(getDailyMailNews()), chat)
    else:
        send_message("Error message, please try again!", chat)

def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            replyAll(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()