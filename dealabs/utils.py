from datetime import datetime
import requests
import os
import json
import re


class Utils:

    # Envoyer le deal par notification
    @staticmethod
    def sendNotification(token, user, deal, open_dealabs=1):
        notif_title = Utils.formatDealTitle(deal)
        urlRedirection = Utils.getFinalUrl(deal['redirectUrl'])
        addedModeration = "1" if deal['addedModeration'] else "0"
        notif_message = "<b>{}</b>\n\n\n\n{} - <a href='{}'>Voir le site</a> - <a href='{}'>Voir le deal</a>\n{}".format(Utils.formatDealTitle(deal, True), addedModeration, urlRedirection, deal['url'], Utils.removeHTML(deal['description']))

        url = deal['url'] if open_dealabs else urlRedirection

        # Post to Pushover
        response = requests.post("https://api.pushover.net/1/messages.json", data={
            "token": token,
            "user": user,
            "title": notif_title,
            "message": notif_message,
            "html": 1,
            "url": url,
            "url_title": "Voir le deal",
            "priority": 1
        }, files={
            "attachment": ("image.jpg", Utils.getImage(deal['image']), "image/jpeg")
        }).json()

        if "status" in response and response['status'] == 1:
            Utils.log("[Send] {}".format(Utils.formatDealTitle(deal, True)))
        else:
            Utils.log("[Error] {}".format(Utils.formatDealTitle(deal, True)))

    # Récuperer l'image sous forme de bytes
    @ staticmethod
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

    # Récupérer le répertoire de cache (le créer si il n'existe pas)
    @ staticmethod
    def getCacheFolder():
        if not os.path.exists('.cache'):
            os.makedirs('.cache')
        return '.cache/'

    # Récupérer les deals déjà vus
    @ staticmethod
    def getDealsViewed():
        try:
            with open(Utils.getCacheFolder() + 'deals.json', 'r') as f:
                deals = json.load(f)
        except:
            deals = []

        return deals

    # Ajouter un deal à la liste des deals vus
    @ staticmethod
    def addDealViewed(hash):
        dealsViewed = Utils.getDealsViewed()
        dealsViewed.append(hash)
        with open(Utils.getCacheFolder() + 'deals.json', 'w') as f:
            json.dump(dealsViewed, f)

    # Envoyer une notification pour prévenir que les tokens vont bientôt expirer
    @ staticmethod
    def expireNotification(token, user, refresh_seconds=0):
        try:
            delta_time = int(datetime.now().timestamp() - os.path.getmtime('.env'))
        except FileNotFoundError:
            return

        if delta_time > 29 * 24 * 60 * 60 and delta_time < 29 * 24 * 60 * 60 + refresh_seconds:
            requests.post("https://api.pushover.net/1/messages.json", data={
                "token": token,
                "user": user,
                "title": "🚨 Expiration PushOver",
                "message": "Attention vos tokens expirent demain !",
                "priority": 1
            })

    # Log dans la console
    @ staticmethod
    def log(message):
        print("[{}] {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message))

    # Formater le titre du deal pour inclure le prix
    @ staticmethod
    def formatDealTitle(deal, addTitle=False):
        if addTitle:
            deal_title = "{} - ".format(deal['title'])
        else:
            deal_title = ""

        deal_title += (deal['merchant']["merchantName"] if deal['merchant'] and "merchantName" in deal['merchant'] else "Dealabs")

        if deal['isFree']:
            deal_title += " (Gratuit)"
        else:
            if deal['priceDiscount']:
                deal_title += " -{}%".format(int(deal['priceDiscount']))

            if deal['price']:
                deal_title += " ({}".format(Utils.formatPrice(deal['price']))
                if deal['nextBestPrice']:
                    deal_title += " / {}".format(Utils.formatPrice(deal['nextBestPrice']))
                deal_title += ")"

        return deal_title

    # Formater le prix
    @ staticmethod
    def formatPrice(price):
        return "{:.2f}€" .format(price)

    # Supprimer les balises html d'une chaine de caractères
    @ staticmethod
    def removeHTML(str):
        return re.sub(re.compile('<.*?>'), '', str).strip()

    # Récupérer l'url finale (après redirections)
    @ staticmethod
    def getFinalUrl(url):
        try:
            response = requests.get(url, headers={
                'user-agent': 'Dealabs/612302 CFNetwork/1120 Darwin/19.0.0'
            }, timeout=5, allow_redirects=True)
            return response.url
        except:
            return url
