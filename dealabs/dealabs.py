from .utils import Utils
import time
import requests
import os
import json
import hashlib
import re


class Dealabs:

    def __init__(self, minimum_discount=90, free_products=0, expire_notification=0, open_dealabs=1, priority_only_first=1, free_products_priority=0):
        self.minimum_discount = minimum_discount
        self.free_products = free_products
        self.expire_notification = expire_notification
        self.open_dealabs = open_dealabs
        self.priority_only_first = priority_only_first
        self.free_products_priority = free_products_priority
        self.refresh_seconds = 0
        self.setBlacklist()

    # Définir les tokens pushOver
    def setPushOver(self, token, user):
        self.token = token
        self.user = user

    # Définir une liste de deals à exclure
    def setBlacklist(self, blacklist=[]):
        if blacklist:
            self.blacklist = blacklist
        else:
            self.blacklist = Utils.getBlackListFile()

    # Vérifier les deals toutes les x secondes
    def watch(self, refresh_seconds):
        self.refresh_seconds = refresh_seconds
        Utils.log("[Start] Watching deals ({}s | min: {}% | free: {} | expire: {} | open_dealabs: {} | priority_only_first: {} | free_products_priority: {})".format(refresh_seconds, self.minimum_discount, self.free_products, self.expire_notification, self.open_dealabs, self.priority_only_first, self.free_products_priority))
        while True:
            if self.expire_notification and hasattr(self, 'token') and hasattr(self, 'user'):
                Utils.expireNotification(self.token, self.user, self.refresh_seconds)

            for deal in self.getDeals():
                sendNotification = False

                # Si le deal est nouveau
                if deal.getHash() not in Utils.getDealsViewed():
                    Utils.addDealViewed(deal.getHash())
                else:
                    continue

                # Si le deal est déactivé ou local
                if deal.isDeactivated() or deal.isLocal():
                    continue

                # Si le deal est une erreur de prix
                if deal.isError():
                    sendNotification = True

                # Si le produit est gratuit
                elif self.free_products and deal.isFree():
                    sendNotification = True

                # Si la réduction est supérieure à x%
                elif deal.reductionIsMoreThan(self.minimum_discount):
                    sendNotification = True

                # Si le deal remplit les critères
                if sendNotification:
                    if hasattr(self, 'token') and hasattr(self, 'user'):
                        Utils.sendNotification(self.token, self.user, deal, self.open_dealabs, self.priority_only_first, self.free_products_priority)
                    else:
                        Utils.log("[Not Send] {}".format(deal.formatTitle(True)))
                else:
                    Utils.log("[Ignored] {}".format(deal.formatTitle(True)))

            time.sleep(refresh_seconds)

    # Récupérer les deals récents
    def getDeals(self, getInModeration=True):
        threads = self._getThreads()
        deals = []

        if getInModeration:
            lastThreadId = int(threads[len(threads)-1]['threadId'])
            for i in range(1, 4):
                deal = self.getDeal(lastThreadId + i, True)
                if deal:
                    deals.append(deal)

        for deal in threads:
            deal = Deal(deal, False, self.blacklist)
            deals.append(deal)

        deals.sort(key=lambda x: x.updatedAt)

        return deals

    # Récupère un deal depuis son id
    def getDeal(self, id, inModeration=False):
        thread = self._getThread(id)
        if thread:
            return Deal(thread, inModeration)
        else:
            return None

    # Récupère un deal depuis son url
    def getDealFromUrl(self, url, inModeration=False):
        id = re.findall(r'\d+$', url)[0]
        return self.getDeal(id, inModeration)

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

    # Requête qui récupère les deals depuis dealabs
    def _getThreads(self, cookiesFromCache=True, retryDeals=0):
        timestamp = str(round(time.time()))
        json_data = [{
            'query': "query getThreads" + timestamp + " {threads(filter: {threadId: null}) { " + self._getProperties() + " }}"
        }]
        response = requests.post('https://www.dealabs.com/graphql', headers={
            'user-agent': 'Dealabs/612302 CFNetwork/1120 Darwin/19.0.0'
        }, cookies=self.getCookies(cookiesFromCache), json=json_data)
        try:
            threads = response.json()[0]['data']['threads']
        except:
            if retryDeals < 2:
                return self._getThreads(False, retryDeals + 1)
            else:
                return []

        threads.sort(key=lambda x: x['threadId'])
        return threads

    # Requête qui récupère un deal depuis dealabs
    def _getThread(self, id, cookiesFromCache=True, retryDeals=0):
        timestamp = str(round(time.time()))
        json_data = [{
            'query': "query additionalInfo" + timestamp + "($threadId: ID!) { thread(threadId: {eq: $threadId}) { " + self._getProperties() + " }}",
            'variables': {
                'threadId': id
            }
        }]
        response = requests.post('https://www.dealabs.com/graphql', headers={
            'user-agent': 'Dealabs/612302 CFNetwork/1120 Darwin/19.0.0'
        }, cookies=self.getCookies(cookiesFromCache), json=json_data)
        try:
            return response.json()[0]['data']['thread']
        except:
            if retryDeals < 2:
                return self._getThread(id, False, retryDeals + 1)
            else:
                return {}


class Deal:
    def __init__(self, deal_json, is_from_moderation=False, blacklist=[]):
        self._formatFields(deal_json, is_from_moderation, blacklist)
        self._formatPrices()

    def isError(self):
        isError = False
        if self.groups and any(group['id'] == 2201 for group in self.groups):
            isError = True
        elif re.search(r'erreur', self.title, re.IGNORECASE):
            isError = True
        elif re.search(r'erreur', self.description, re.IGNORECASE):
            isError = True

        return isError

    def isFree(self):
        isFree = False
        if self.groups and any(group['id'] == 17 for group in self.groups):
            isFree = True
        elif re.search(r'gratuit', self.title, re.IGNORECASE):
            isFree = True
        elif self.price == 0 and self.nextBestPrice:
            isFree = True

        return isFree

    def isLocal(self):
        isLocal = self._isLocal
        if self._isLocal and self._selectedLocations and self._selectedLocations['isNational']:
            isLocal = False

        return isLocal

    def isDeactivated(self):
        isDeactivated = False
        self.blacklist = Utils.getBlackListFile()
        search = self.title.lower()
        if self.merchant:
            search += ' - ' + self.merchant.lower()

        if self.type != 1:
            isDeactivated = True

        elif self.status == 'Deactivated' and (not self.price or self.price == 0):
            isDeactivated = True

        elif self._blacklist and any(blacklist.lower() in search for blacklist in self._blacklist):
            isDeactivated = True

        return isDeactivated

    def isAddedInModeration(self):
        return self._addedModeration

    def formatTitle(self, addTitle=False):
        if addTitle:
            deal_title = "{} - ".format(self.title)
        else:
            deal_title = ""

        deal_title += (self.merchant if self.merchant else "Dealabs")

        if self.isFree():
            deal_title += " (Gratuit)"
        else:
            if self.priceDiscount:
                deal_title += " -{}%".format(int(self.priceDiscount))

            if self.price:
                deal_title += " ({}".format(Utils.formatPrice(self.price))
                if self.nextBestPrice:
                    deal_title += " / {}".format(Utils.formatPrice(self.nextBestPrice))
                deal_title += ")"

        return deal_title

    def reductionIsMoreThan(self, reduction):
        return self.priceDiscount and self.priceDiscount >= reduction

    def getHash(self):
        hash_content = "{}{}{}{}{}{}".format(self.title, self.description, str(self.price), str(self.updatedAt), str(self.status), str(self.priceDiscount))
        if self.groups and len(self.groups) > 0:
            hash_content += ''.join(str(group['id']) for group in self.groups)

        return hashlib.md5(hash_content.encode('utf-8')).hexdigest()

    def json(self):
        dict = json.loads(json.dumps(self, default=lambda o: o.__dict__))
        dict['isLocal'] = self.isLocal()
        dict['isError'] = self.isError()
        dict['isFree'] = self.isFree()
        dict['isDeactivated'] = self.isDeactivated()

        return {k: v for k, v in dict.items() if not k.startswith('_')}

    def _formatPrices(self):
        if self.price and self.nextBestPrice:
            self.priceReduction = round(self.nextBestPrice - self.price, 2)
            self.priceDiscount = round(self.priceReduction / self.nextBestPrice * 100, 2)
        else:
            self.priceReduction = None
            self.priceDiscount = None

    def _formatFields(self, deal_json, is_from_moderation=False, blacklist=[]):
        privates = ['mainImage', 'selectedLocations', 'isLocal', 'groups', 'merchant']
        for key in deal_json:
            if key in privates:
                setattr(self, '_' + key, deal_json[key])
            else:
                if key == 'threadId':
                    setattr(self, 'id', int(deal_json[key]))
                elif key == 'threadTypeId':
                    setattr(self, 'type', int(deal_json[key]))
                else:
                    setattr(self, key, deal_json[key])

        self._blacklist = blacklist

        if self._mainImage:
            self.image = 'https://static-pepper.dealabs.com/' + self._mainImage['path'] + '/' + self._mainImage['name'] + '.jpg'
        else:
            self.image = None

        groups = []
        if self._groups:
            for group in self._groups:
                groups.append({
                    'id': int(group['threadGroupId']),
                    'name': group['threadGroupName']
                })
        self.groups = groups

        locations = []
        if self._selectedLocations and "locations" in self._selectedLocations:
            for location in self._selectedLocations["locations"]:
                locations.append({
                    'id': int(location['id']),
                    'name': location['name']
                })

        self.locations = locations

        self.merchant = self._merchant["merchantName"] if self._merchant else None
        self.redirectUrl = 'https://www.dealabs.com/visit/threadmain/' + str(self.id)
        self._addedModeration = is_from_moderation
