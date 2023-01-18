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

free_products = int(os.getenv("FREE_PRODUCTS")) if os.getenv(
    "FREE_PRODUCTS") else 0


def getProducts():
    headers = {
        'Host': 'www.dealabs.com',
        'accept': '*/*',
        'pepper-json-format': 'thread=list,user=list,badge=none,group=ids,type=light,image=light, message=with_code, formatted_text=parsed',
        'pepper-include-counters': 'unseen_activities,unread_alerts,unseen_messages,unread_dealbot_newsletters',
        'accept-language': 'fr-FR;q=1, en-FR;q=0.9',
        'authorization': 'OAuth oauth_consumer_key="540475e198c64",oauth_nonce="0744E67A-86C8-4ABE-A975-F61FA6B8D510",oauth_signature="htd%2BLIH7ZCIDe5FnYffjmxk6ZUw%3D",oauth_signature_method="HMAC-SHA1",oauth_timestamp="1673886429",oauth_token="1d8d2000b1d11df2e5f6e9ddf33d583e50df8ab2",oauth_version="1.0"',
        'user-agent': 'com.dealabs.apps.ios/612302/6.12.3 (iPhone; iOS 13.2.2; Scale/3.00)',
        'pepper-hardware-id': 'F9E2DA43-1418-45EE-BDEC-6BCAFFBE2A40',
    }

    params = {
        'criteria': '{\n  "event" : null,\n  "tab" : "new",\n  "user" : null,\n  "merchant" : null,\n  "group" : null,\n  "query" : null,\n  "show_clearance" : true,\n  "location_ids" : null,\n  "whereabouts" : "deals"\n}',
        'limit': '20',
        'page': '1',
    }

    try:
        response = requests.get('https://www.dealabs.com/rest_api/v2/thread',
                                params=params, headers=headers, timeout=5).json()['data']
        response.reverse()
    except:
        response = []

    return response


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

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=5,
        ).content
    except:
        response = None

    return response


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

        hash_content = "{}{}{}{}{}{}".format(title, str(local), str(
            price), str(price_original), str(discount), str(merchant))
        hash_content += ''.join(str(group) for group in groups)
        hash = hashlib.md5(hash_content.encode('utf-8')).hexdigest()

        # Si le deal a déjà été vu
        if hash not in getDealsViewed():
            addDealViewed(hash)
            pass
        else:
            continue

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

        # Si c'est un produit gratuit
        if free_products and 17 in groups:
            sendNotification(title, merchant, image, price_formatted,
                             price_original_formatted, discount, url)
            continue

        log("[Ignored] {}".format(title))

    # Toutes les x secondes
    time.sleep(refresh_seconds)
