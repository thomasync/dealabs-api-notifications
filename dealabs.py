import requests
import json
import os
import datetime
import time
from dotenv import load_dotenv
import hashlib

load_dotenv()

# Check if env variables are set
if os.getenv("PUSHOVER_TOKEN") is None:
    print("PUSHOVER_TOKEN not found")
    exit(1)

if os.getenv("PUSHOVER_USER") is None:
    print("PUSHOVER_USER not found")
    exit(1)

refresh_seconds = int(os.getenv("REFRESH_SECONDS")
                      ) if os.getenv("REFRESH_SECONDS") else 60

min_discount = int(os.getenv("MIN_DISCOUNT")) if os.getenv(
    "MIN_DISCOUNT") else 80


def getProducts():
    headers = {
        'Host': 'www.dealabs.com',
        'accept': '*/*',
        'pepper-json-format': 'thread=list,user=list,badge=none,group=ids,type=light,image=light, message=with_code, formatted_text=parsed',
        'pepper-include-counters': 'unread_alerts,unread_dealbot_newsletters',
        'accept-language': 'fr-FR;q=1, en-FR;q=0.9',
        'authorization': 'OAuth oauth_consumer_key="540475e198c64",oauth_nonce="F6AC8C80-217F-4560-8508-DA11517CA23B",oauth_signature="pwuAg4zar0fBEiSittDSa%2FM2LMw%3D",oauth_signature_method="HMAC-SHA1",oauth_timestamp="1673622310",oauth_version="1.0"',
        'user-agent': 'com.dealabs.apps.ios/612302/6.12.3 (iPhone; iOS 13.2.2; Scale/3.00)',
        'pepper-hardware-id': 'F9E2DA43-1418-45EE-BDEC-6BCAFFBE2A40',
    }

    params = {
        'criteria': '{\n  "whereabouts" : "deals",\n  "group" : null,\n  "merchant" : null,\n  "query" : null,\n  "event" : null,\n  "location_ids" : null,\n  "show_clearance" : true,\n  "tab" : "new",\n  "user" : null\n}',
        'limit': '20',
        'page': '1',
    }

    response = requests.get('https://www.dealabs.com/rest_api/v2/thread',
                            params=params, headers=headers)

    return response.json()['data']


def getProduct(id):
    headers = {
        'Host': 'www.dealabs.com',
        'accept': '*/*',
        'pepper-json-format': 'badge=userbadge,thread=full,user=list,merchant=full,type=full,image=full,thread_update=full,group=ids,comment=list, message=with_code, formatted_text=parsed',
        'authorization': 'OAuth oauth_consumer_key="540475e198c64",oauth_nonce="0FBA85A2-22F9-4F34-B522-A3227250DFAE",oauth_signature="0P1Tz2osW6CpErp0kvNqETr%2BQNY%3D",oauth_signature_method="HMAC-SHA1",oauth_timestamp="1673626382",oauth_version="1.0"',
        'pepper-hardware-id': 'F9E2DA43-1418-45EE-BDEC-6BCAFFBE2A40',
        'user-agent': 'com.dealabs.apps.ios/612302/6.12.3 (iPhone; iOS 13.2.2; Scale/3.00)',
        'accept-language': 'fr-FR;q=1, en-FR;q=0.9',
    }

    response = requests.get(
        'https://www.dealabs.com/rest_api/v2/thread/' + str(id), headers=headers)

    return response.json()['data']


def getDealsViewed():
    try:
        with open('deals.json', 'r') as f:
            deals = json.load(f)
    except:
        deals = []

    return deals


def addDealViewed(hash):
    dealsViewed = getDealsViewed()
    dealsViewed.append(hash)
    with open('deals.json', 'w') as f:
        json.dump(dealsViewed, f)


def log(message):
    print("[{}] {}".format(datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"), message))


def getImage(url):
    headers = {
        'Host': 'static-pepper.dealabs.com',
        'accept': 'image/*',
        'user-agent': 'Dealabs/612302 CFNetwork/1120 Darwin/19.0.0',
        'accept-language': 'fr-fr',
    }

    response = requests.get(
        url,
        headers=headers,
    )
    return response.content


def sendNotification(title, merchant, image, price_formatted, price_original_formatted, discount, url):
    notif_title = (merchant if merchant else "Dealabs")

    if discount:
        notif_title += " -{}%".format(discount)

    if price_formatted:
        notif_title += " ({}".format(price_formatted)
        if price_original_formatted:
            notif_title += " / {}".format(price_original_formatted)
        notif_title += ")"

    notif_message = title

    log("[Send] {}".format(notif_title))

    # Post to Pushover
    requests.post("https://api.pushover.net/1/messages.json", data={
        "token": os.getenv("PUSHOVER_TOKEN"),
        "user": os.getenv("PUSHOVER_USER"),
        "title": notif_title,
        "message": notif_message,
        "url": url,
        "url_title": "Voir sur Dealabs",
        "priority": 1
    }, files={
        "attachment": ("image.jpg", getImage(image), "image/jpeg")
    })


def expireNotification():
    send_notification = True if os.getenv("EXPIRE_NOTIFICATION") and os.getenv(
        "EXPIRE_NOTIFICATION") == "1" else False

    delta_time = int(datetime.datetime.now().timestamp() -
                     os.path.getmtime('.env'))

    if send_notification and delta_time > 29 * 24 * 60 * 60 and delta_time < 29 * 24 * 60 * 60 + refresh_seconds:
        requests.post("https://api.pushover.net/1/messages.json", data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "title": "🚨 Expiration PushOver",
            "message": "Attention vos tokens expirent demain !",
            "priority": 1
        })


while True:
    expireNotification()
    for product in getProducts():
        id = product['thread_id']
        title = product['title']
        date_submitted = product['submitted']
        date_created = product['created']
        local = product['local']

        price = product['price'] if "price" in product else None
        price_formatted = product['price_display'] if "price_display" in product else None
        price_original = product['next_best_price'] if "next_best_price" in product else None
        price_original_formatted = product['next_best_price_display'] if "next_best_price_display" in product else None

        discount = product['price_discount'] if "price_discount" in product else None

        image = product['icon_detail_url'] if "icon_detail_url" in product else None
        merchant = product['merchant']['name'] if "merchant" in product else None
        url = product['deal_uri']

        groups = product['group_ids']

        title_hashed = hashlib.md5(title.encode('utf-8')).hexdigest()

        # Si le deal a déjà été vu
        if title_hashed not in getDealsViewed():
            addDealViewed(title_hashed)
            pass
        else:
            continue

        # Si le deal n'est pas sur internet
        if local:
            continue

        # Si le deal contient "erreur" dans le titre ou fait parti du groupe "Erreur de prix"
        if "erreur" in title.lower() or "erreur" in url or 2201 in groups:
            sendNotification(title, merchant, image,
                             price_formatted, price_original_formatted, discount, url)
            continue

        # Si la réduction est supérieure à x%
        if discount and discount >= min_discount:
            sendNotification(title, merchant, image, price_formatted,
                             price_original_formatted, discount, url)
            continue

        # Si la description du deal contient "erreur"
        try:
            product = getProduct(id)
            if "erreur" in product['description'].lower():
                sendNotification(title, merchant, image, price_formatted,
                                 price_original_formatted, discount, url)
                continue
        except:
            pass

        log("[Ignored] {}".format(title))

    # Toutes les x secondes
    time.sleep(refresh_seconds)
