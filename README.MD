# Dealabs Api Notifications

[![Tests](https://github.com/thomasync/dealabs-api-notifications/actions/workflows/python-package.yml/badge.svg)](https://github.com/thomasync/dealabs-api-notifications/actions/workflows/python-package.yml)

## Envoi des notifications sur téléphone pour les erreurs de prix Dealabs (via pushover)

1. Créer un compte sur [PushOver](https://pushover.net/)
2. Générer une [application](https://pushover.net/apps/build)
3. Renommer le fichier **.env.example** en **.env**
4. Remplir les valeurs _PUSHOVER_TOKEN_ et _PUSHOVER_USER_
5. Sur l'application : Settings -> Advanced Settings -> Auto-open URLs

Exemple de la commande:

```python
pip install -r requirements.txt

# python3 main.py [refresh_seconds] [minimum_discount] [free_products] [expire_notification] [open_dealabs] [priority_only_first] [free_products_priority]
python3 main.py 60 90 0 0 1 1 0
```

Optionnel dans le fichier .env:

- _REFRESH_SECONDS_ : Actualiser la recherche des deals toutes les x seconds (60s par défaut)
- _MIN_DISCOUNT_ : Représente le pourcentage minimum pour déclencher la notification (90% par défaut)
- _FREE_PRODUCTS_ : Capturer également les produits gratuits (Désactivé par défaut)
- _EXPIRE_NOTIFICATION_ : Prévient de l'expiration des tokens PushOver la veille pour les modifier (attention c'est basé sur la date de modification du fichier **.env**) (Désactivé par défaut)
- _OPEN_DEALABS_ : Au click sur la notification ouvrir Dealabs, au lieu du site du deal (Activé par défaut)
- _PRIORITY_ONLY_FIRST_ : Notifier uniquement en priorité a l'apparition du deal et pas à chaque mise à jour (Activé par défaut)
- _FREE_PRODUCTS_PRIORITY_ : Envoi également les notifications des produits gratuit en priorité (Désactivé par défaut)

---

🚨 Attention : **PushOver** n'est gratuit qu'un mois, il faut soit refaire un compte et changer les tokens une fois par mois, soit payer 5,99€ définitivement.

---

## Utilisation de la librairie de façon indépendante

1. Déplacer le dossier **dealabs** dans votre projet
2. Importer la classe Dealabs: `from dealabs import Dealabs`
3. Instanciez: `dealabs = Dealabs()`

### Exemples

#### Récuperer les deals avec au minimum 80% de réduction et sans les produits gratuits

```python
from dealabs import Dealabs
dealabs = Dealabs(80, 0)
deals = dealabs.getDeals()
```

#### Récuperer les deals avec au minimum 80% de réduction, avec les produits gratuits mais ne pas ajouter ceux en cours de modération

```python
from dealabs import Dealabs
dealabs = Dealabs(80, 1)
deals = dealabs.getDeals(False)
```

#### Récuper un deal depuis son id

```python
from dealabs import Dealabs
dealabs = Dealabs()
deal = dealabs.getDeal(2497616)
print(deal.json())
```

#### Récuper un deal depuis son url

```python
from dealabs import Dealabs
dealabs = Dealabs()
deal = dealabs.getDealFromUrl("2497616")
print(deal.json())
```

## [CHANGELOG](https://github.com/thomasync/dealabs-api-notifications/blob/main/CHANGELOG.MD)

2023 - [@thomasync](https://github.com/thomasync)
