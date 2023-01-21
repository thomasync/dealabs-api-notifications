# Dealabs Price Error Notifications

## Envoi des notifications sur téléphone pour les erreurs de prix Dealabs (via pushover)

1. Créer un compte sur [PushOver](https://pushover.net/)
2. Générer une [application](https://pushover.net/apps/build)
3. Renommer le fichier **.env.example** en **.env**
4. Remplir les valeurs _PUSHOVER_TOKEN_ et _PUSHOVER_USER_
5. Sur l'application : Settings -> Advanced Settings -> Auto-open URLs

Exemple de la commande:

```
# python3 main.py [refresh_seconds] [minimum_discount] [free_products] [expire_notification] [open_dealabs] [priority_only_first]
python3 main.py 60 90 0 0 1 1
```

Optionnel dans le fichier .env:

- _REFRESH_SECONDS_ : Actualiser la recherche des deals toutes les x seconds (60s par défaut)
- _MIN_DISCOUNT_ : Représente le pourcentage minimum pour déclencher la notification (90% par défaut)
- _FREE_PRODUCTS_ : Capturer également les produits gratuits (Désactivé par défaut)
- _EXPIRE_NOTIFICATION_ : Prévient de l'expiration des tokens PushOver la veille pour les modifier (attention c'est basé sur la date de modification du fichier **.env**) (Désactivé par défaut)
- _OPEN_DEALABS_ : Au click sur la notification ouvrir Dealabs, au lieu du site du deal (Activé par défaut)
- _PRIORITY_ONLY_FIRST_ : Notifier uniquement en priorité a l'apparition du deal et pas à chaque mise à jour (Activé par défaut)

---

🚨 Attention : **PushOver** n'est gratuit qu'un mois, il faut soit refaire un compte et changer les tokens une fois par mois, soit payer 5,99€ définitivement.

---

2023 - [@thomasync](https://github.com/thomasync)
