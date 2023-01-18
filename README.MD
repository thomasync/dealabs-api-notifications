# Dealabs Price Error Notifications

## Envoi des notifications sur téléphone pour les erreurs de prix Dealabs (via pushover)

1. Créer un compte sur [PushOver](https://pushover.net/)
2. Générer une [application](https://pushover.net/apps/build)
3. Renommer le fichier **.env.example** en **.env**
4. Remplir les valeurs _PUSHOVER_TOKEN_ et _PUSHOVER_USER_
5. Sur l'application : Settings -> Advanced Settings -> Auto-open URLs

Optionnel :

- _MIN_DISCOUNT_ : Représente le pourcentage minimum pour déclencher la notification (90% par défaut)
- _FREE_PRODUCTS_ : Capturer également les produits gratuits (Désactivé par défaut)
- _REFRESH_SECONDS_ : Actualiser la recherche des deals toutes les x seconds (60s par défaut)
- _EXPIRE_NOTIFICATION_ : Prévient de l'expiration des tokens PushOver la veille pour les modifier (attention c'est basé sur la date de modification du fichier **.env**) (Désactivé par défaut)

---

🚨 Attention : **PushOver** n'est gratuit qu'un mois, il faut soit refaire un compte et changer les tokens une fois par mois, soit payer 5,99€ définitivement.

---

2023 - [@thomasync](https://github.com/thomasync)
