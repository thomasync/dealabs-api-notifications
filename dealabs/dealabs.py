from .utils import Utils
import time
import requests
import os
import json
import hashlib
import re


class Dealabs:

    def __init__(self, minimum_discount, free_products, expire_notification, open_dealabs):
        self.minimum_discount = minimum_discount
        self.free_products = free_products
        self.expire_notification = expire_notification
        self.open_dealabs = open_dealabs
        self.refresh_seconds = 0

    # Définir les tokens pushOver
    def setPushOver(self, token, user):
        self.token = token
        self.user = user

    # Vérifier les deals toutes les x secondes
    def watch(self, refresh_seconds):
        self.refresh_seconds = refresh_seconds
        Utils.log("[Start] Watching deals ({}s | min: {}% | free: {} | expire: {} | open_dealabs: {})".format(refresh_seconds, self.minimum_discount, self.free_products, self.expire_notification, self.open_dealabs))
        while True:
            if self.expire_notification and hasattr(self, 'token') and hasattr(self, 'user'):
                Utils.expireNotification(self.token, self.user, self.refresh_seconds)

            for deal in self.getDeals():
                sendNotification = False

                # Si le deal est nouveau
                if deal['hash'] not in Utils.getDealsViewed():
                    Utils.addDealViewed(deal['hash'])
                else:
                    continue

                # Si le deal est local
                if deal['isLocal']:
                    continue

                # Si le deal est une erreur de prix
                if deal['isError']:
                    sendNotification = True

                # Si le produit est gratuit
                elif self.free_products and deal['isFree']:
                    sendNotification = True

                # Si la réduction est supérieure à x%
                elif deal['priceDiscount'] and deal['priceDiscount'] >= self.minimum_discount:
                    sendNotification = True

                # Si le deal remplit les critères
                if sendNotification:
                    if hasattr(self, 'token') and hasattr(self, 'user'):
                        Utils.sendNotification(self.token, self.user, deal, self.open_dealabs)
                    else:
                        Utils.log("[Not Send] {}".format(Utils.formatDealTitle(deal, True)))
                else:
                    Utils.log("[Ignored] {}".format(Utils.formatDealTitle(deal, True)))

            time.sleep(refresh_seconds)

    # Récupérer les deals récents
    def getDeals(self, getInModeration=True, cookiesFromCache=True):
        json_data = [{
            'query': "query getThreads {threads(filter: {threadId: null}) { " + self._getProperties() + " }}"
        }]
        response = requests.post('https://www.dealabs.com/graphql', headers={
            'user-agent': 'Dealabs/612302 CFNetwork/1120 Darwin/19.0.0'
        }, cookies=self.getCookies(cookiesFromCache), json=json_data)
        try:
            threads = response.json()[0]['data']['threads']
        except:
            return self.getDeals(getInModeration, False)

        threads.sort(key=lambda x: x['threadId'])

        deals = []

        if getInModeration:
            lastThreadId = int(threads[len(threads)-1]['threadId'])
            for i in range(1, 4):
                deal = self.getDeal(lastThreadId + i)
                if deal:
                    deal["addedModeration"] = True
                    threads.append(deal)

        for deal in threads:
            # Si ce n'est pas un deal
            if deal['threadTypeId'] != 1:
                continue

            # Si le deal est désactivé et sans prix
            if deal['status'] == 'Deactivated' and (not deal['price'] or deal['price'] == 0):
                continue

            # Si le deal est local et national
            if deal['isLocal'] and deal['selectedLocations'] and deal['selectedLocations']['isNational']:
                deal['isLocal'] = False

            # Calculer le pourcentage de réduction
            if deal['price'] and deal['nextBestPrice']:
                deal['priceReduction'] = round(deal['nextBestPrice'] - deal['price'], 2)
                deal['priceDiscount'] = round(deal['priceReduction'] / deal['nextBestPrice'] * 100, 2)
            else:
                deal['priceReduction'] = None
                deal['priceDiscount'] = None

            if deal['mainImage']:
                deal['image'] = 'https://static-pepper.dealabs.com/' + deal['mainImage']['path'] + '/' + deal['mainImage']['name'] + '.jpg'
            else:
                deal['image'] = None

            deal['redirectUrl'] = 'https://www.dealabs.com/visit/threadmain/' + str(deal['threadId'])

            if "addedModeration" not in deal:
                deal["addedModeration"] = False

            hash_content = "{}{}{}{}{}{}".format(deal['title'], deal['description'], str(deal['price']), str(deal['updatedAt']), str(deal['status']), str(deal['priceDiscount']))

            if deal['groups'] and len(deal['groups']) > 0:
                hash_content += ''.join(str(group['threadGroupId']) for group in deal['groups'])

            deal['hash'] = hashlib.md5(hash_content.encode('utf-8')).hexdigest()

            # Si c'est une erreur de prix
            if deal['groups'] and any(group['threadGroupId'] == '2201' for group in deal['groups']):
                deal['isError'] = True
            elif re.search(r'erreur', deal['title'], re.IGNORECASE):
                deal['isError'] = True
            elif re.search(r'erreur', deal['description'], re.IGNORECASE):
                deal['isError'] = True
            else:
                deal['isError'] = False

            # Si c'est gratuit
            if deal['groups'] and any(group['threadGroupId'] == '17' for group in deal['groups']):
                deal['isFree'] = True
            elif re.search(r'gratuit', deal['title'], re.IGNORECASE):
                deal['isFree'] = True
            else:
                deal['isFree'] = False

            deals.append(deal)

        deals.sort(key=lambda x: x['updatedAt'])

        return deals

    # Récupère un deal depuis son id
    def getDeal(self, id):
        json_data = [{
            'query': "query additionalInfo($threadId: ID!) { thread(threadId: {eq: $threadId}) { " + self._getProperties() + " }}",
            'variables': {
                'threadId': id
            }
        }]
        response = requests.post('https://www.dealabs.com/graphql', headers={
            'user-agent': 'Dealabs/612302 CFNetwork/1120 Darwin/19.0.0'
        }, cookies=self.getCookies(), json=json_data)
        try:
            return response.json()[0]['data']['thread']
        except:
            return {}

    # Récupérer les cookies de Dealabs pour l'authentification
    def getCookies(self, fromCache=True):
        if os.path.exists(Utils.getCacheFolder() + 'cookies.json'):
            cookies = open(Utils.getCacheFolder() + 'cookies.json', 'r').read()
        else:
            cookies = None

        if cookies and fromCache:
            return json.loads(cookies)

        response = requests.get('https://www.dealabs.com/', headers={
            'authority': 'www.dealabs.com',
            'accept-language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'cache-control': 'max-age=0',
            'user-agent': 'Dealabs/612302 CFNetwork/1120 Darwin/19.0.0',
        })
        cookies = dict(response.cookies)
        open(Utils.getCacheFolder() + 'cookies.json', 'w+').write(json.dumps(cookies))

        return cookies

    # Propriétés à récupérer pour un deal
    def _getProperties(self):
        return """
            threadId,
            threadTypeId,
            title,
            description,
            price,
            nextBestPrice,
            isLocal,
            createdAt,
            publishedAt,
            updatedAt,
            status,
            mainImage {
                path,
                name
            },
            url,
            merchant {
                merchantId,
                merchantName
            },
            groups {
                threadGroupId,
                threadGroupName
            },
            selectedLocations {
                isNational,
                locations {
                    id,
                    name
                }
            }
        """
