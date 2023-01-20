import os
import sys
from dealabs import Dealabs, Utils
from dotenv import load_dotenv
load_dotenv()


def help():
    print("""Usage: python3 main.py [refresh_seconds] [minimum_discount] [free_products] [expire_notification] [open_dealabs]
refresh_seconds: Nombre de secondes entre chaque rafraichissement
minimum_discount: Pourcentage minimum de réduction pour être notifié
free_products: Être notifié des produits gratuits
expire_notification: Recevoir une notification avant que les tokens pushover ne soient expirés
open_dealabs: Ouvrir dealabs au lieu du site du deal""")
    sys.exit(0)


def main(args):
    if os.getenv("PUSHOVER_TOKEN") is None:
        print("PUSHOVER_TOKEN not found in .env file")
        exit(1)

    if os.getenv("PUSHOVER_USER") is None:
        print("PUSHOVER_USER not found in .env file")
        exit(1)

    if len(args) > 0 and "h" in args[0]:
        help()

    # Prend les arguments donnés en priorité puis les variables d'environnement, sinon prend les valeurs par défaut
    if len(args) > 0:
        refresh_seconds = int(args[0])
    else:
        refresh_seconds = int(os.getenv("REFRESH_SECONDS")) if os.getenv("REFRESH_SECONDS") else 60

    if len(args) > 1:
        minimum_discount = int(args[1])
    else:
        minimum_discount = int(os.getenv("MIN_DISCOUNT")) if os.getenv("MIN_DISCOUNT") else 90

    if len(args) > 2:
        free_products = int(args[2])
    else:
        free_products = int(os.getenv("FREE_PRODUCTS")) if os.getenv("FREE_PRODUCTS") else 0

    if len(args) > 3:
        expire_notification = int(args[3])
    else:
        expire_notification = int(os.getenv("EXPIRE_NOTIFICATION")) if os.getenv("EXPIRE_NOTIFICATION") else 0

    if len(args) > 4:
        open_dealabs = int(args[4])
    else:
        open_dealabs = int(os.getenv("OPEN_DEALABS")) if os.getenv("OPEN_DEALABS") else 1

    dealabs = Dealabs(minimum_discount, free_products, expire_notification, open_dealabs)
    dealabs.setPushOver(os.getenv("PUSHOVER_TOKEN"), os.getenv("PUSHOVER_USER"))
    dealabs.watch(refresh_seconds)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass
