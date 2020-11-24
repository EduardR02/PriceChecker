import http.cookiejar as cookielib
import smtplib
import ast
import ssl
from email.message import EmailMessage
import requests
from lxml import html
import mechanize
from inscriptis import get_text

website_links = ["https://www.amazon.de/Sony-WH-1000XM4-Cancelling-Headphones-Schnellladefunktion-Schwarz/dp"
                 "/B08C7KG5LP/ref=sr_1_1?__mk_de_DE=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=YLONNIKC7TMC&dchild=1"
                 "&keywords=wh+1000mx4&qid=1605230500&sprefix=wh+%2Caps%2C184&sr=8-1",
                 "https://geizhals.de/sony-wh-1000xm4-schwarz-a2346364.html?t=alle&plz=&va=b&vl=de&hloc=de&v=e"
                 "&togglecountry=set"]


def get_prices():
    # this is not that good, it's better to use to xpath method
    global website_links

    cj = cookielib.CookieJar()
    br = mechanize.Browser()
    br.set_cookiejar(cj)
    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    br.addheaders = [('User-agent',
                      "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 "
                      "Safari/537.36")]

    prices = []
    for website in website_links:
        br.open(website)
        x = get_text(br.response().read().decode(encoding="utf8", errors="ignore")).split(" ")
        for k, j in enumerate(x):
            if "€" in j:
                prices.append(x[k - 1:k + 2])
                break
    br.close()
    return prices


def get_prices_by_xpath():
    with open("dict_file.txt", "r") as f:
        website_links_dict = ast.literal_eval(f.read())

    prices = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}
    for website in website_links_dict.items():
        page = requests.get(website[1][0], headers=headers)
        root = html.fromstring(page.text)
        xpath = website[1][1] + "/text()"
        result = root.xpath(xpath)
        prices.append(result)
    return prices


def send_email(prices):
    with open("text.txt") as fp:
        # Create a text/plain message
        prices = "\n".join(str(x) + " €" for x in prices)
        prices += "\n\nCustom Message"
        msg = EmailMessage()
        msg.set_content(fp.read() + "\n" + prices)

    sender = "sender_email"
    psw = "your_psw"
    receiver = "receiver-email"
    msg['Subject'] = "Subject"
    msg['From'] = sender
    msg['To'] = receiver
    context = ssl.create_default_context()
    try:
        s = smtplib.SMTP(host="smtp.gmail.com", port=587)
        s.starttls(context=context)
        s.login(sender, psw)
        s.send_message(msg)
        s.quit()
        del msg
        print("success")

    except Exception as e:
        print(e)


def format_nicely(s):
    j = []
    for v in s:
        j.append("".join(v))
    for v, s in enumerate(j):
        k = ""
        for b in s:
            if b.isdigit():
                k += b
            elif b == ",":
                j[v] = int(k)
                break
        j[v] = int(k)
    j.sort()
    return j


if __name__ == "__main__":
    print("Prices:")
    n = format_nicely(get_prices_by_xpath())
    for i in n:
        print(i, "€")
    if n[0] < 300:
        print("sending email")
        send_email(n)
