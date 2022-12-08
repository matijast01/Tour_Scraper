import requests
import selectorlib
import ssl
import smtplib
import time
import sqlite3

# INSERT INTO events VALUES('Tigers', 'Tiger City', '10.10.2077')
# SELECT * FROM events WHERE date='5.5.2089'
# DELETE FROM events WHERE date='15.12.2076'

URL = "http://programmer100.pythonanywhere.com/tours/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML,\
     like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

connection = sqlite3.connect("data.db")


def scrape(url):
    """Scrape the page source from the URL"""
    response = requests.get(url, headers=HEADERS)
    source = response.text
    return source


def extract(source):
    extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
    value = extractor.extract(source)["tours"]
    return value


def store(extracted_local):
    row_local = extracted_local.split(',')
    row_local = [item.strip() for item in row_local]
    cursor = connection.cursor()
    cursor.execute("INSERT INTO events VALUES(?,?,?)", row_local)
    connection.commit()


def send_email(extracted_local):
    host = "smtp.gmail.com"
    port = 465

    message = f"""\
Subject: Hey, new event was found!
    
your script has found a new event which you haven't seen before!
{extracted_local}
"""

    username = "EMAIL"
    password = "PASSWORD"
    receiver = "EMAIL"

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(username, password)
        server.sendmail(username, receiver, message)
    print("Email was sent!")


def read(extracted_local):
    row_local = extracted_local.split(',')
    row_local = [item.strip() for item in row_local]
    band, city, date = row_local
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM events WHERE band=? AND city=? AND date=?", (band, city, date))
    rows = cursor.fetchall()
    return rows


if __name__ == "__main__":
    while True:
        scraped = scrape(URL)
        extracted = extract(scraped)
        print(extracted)
        if extracted != "No upcoming tours":
            row = read(extracted)
            if not row:
                send_email(extracted)
                store(extracted)
        time.sleep(2)
