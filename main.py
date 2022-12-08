import requests
import selectorlib
import ssl
import smtplib
import time

URL = "http://programmer100.pythonanywhere.com/tours/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML,\
     like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


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
    with open("data.txt", "a") as file:
        file.write(extracted_local + "\n")


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


def read():
    with open("data.txt", "r") as file:
        return file.read()


if __name__ == "__main__":
    while True:
        scraped = scrape(URL)
        extracted = extract(scraped)
        print(extracted)
        content = read()
        if extracted != "No upcoming tours":
            if extracted not in content:
                send_email(extracted)
                store(extracted)
        time.sleep(2)
