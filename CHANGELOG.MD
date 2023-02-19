# Changelog

Toutes les modifications notable de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère à [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.1] - 2023-02-19

### Corrigé

- La blacklist ne prenait pas en compte le nom du marchant

## [3.1.0] - 2023-01-28

### Ajouté

- Ajout d'un fichier blacklist.txt où chaque ligne correspond à des mots bannis du titre

### Corrigé

- Correction des tests getDeals() qui n'étaient pas correctement typé

## [3.0.1] - 2023-01-24

### Ajouté

- Ajout du fichiers requirements.txt pour les dépendances
- Ajout de Github Actions

## [3.0.0] - 2023-01-24

### Modifié

- Refactoring pour déplacer la logique métier dans la classe Dealabs et Deal
- Déplacement des outils et de gestion dans la classe Utils
- Repo renommé en dealabs-api-notifications

### Ajouté

- Ajout des tests pour vérifier la classe Dealabs et Deals ainsi que l'accès à l'api soit toujours fonctionnel
- Ajout du paramètre _FREE_PRODUCTS_PRIORITY_ pour pouvoir afficher les notifications des produits gratuits de façon non prioritaire et se concentrer sur les erreurs de prix

## [2.1.0] - 2023-01-21

### Ajouté

- Ajout du paramètre _PRIORITY_ONLY_FIRST_ pour notifier uniquement en priorité a l'apparition du deal et pas à chaque mise à jour
- Les deals envoyés sont en cache dans un fichier send.json

## [2.0.2] - 2023-01-21

### Corrigé

- Les deals designés comme locaux, mais de type nationaux n'étaient pas récupérés

## [2.0.1] - 2023-01-20

### Corrigé

- Catch les erreurs lors de la récupération des redirections d'urls dans getFinalUrl()

## [2.0.0] - 2023-01-19

### Modifié

- Refactoring complet pour tout inclure dans un module
- La récupération passe désormais par graphQL et plus l'api interne
- Les images ne sont plus récupérées via l'api des images, mais le CDN public

### Ajouté

- Ajout de la fonctionnalité _OPEN_DEALABS_ qui permet de choisir d'ouvrir l'application dealabs ou le site du deal
- Il est maintenant possible d'inclure le module pour l'utiliser directement en python
- Le point d'entrée (main.py) accepte maintenant des arguments [refresh_seconds] [minimum_discount] [free_products] [expire_notification] [open_dealabs]
- Retour du getDeal()

## [1.0.7] - 2023-01-18

### Ajouté

- Ajout du paramètre _FREE_PRODUCTS_ pour capturer les produits gratuits

## [1.0.6] - 2023-01-16

### Corrigé

- Changement de l'ordre des paramètres pour correspondre a l'oauth_signature

## [1.0.5] - 2023-01-16

### Modifié

- La requete pour récupérer les deals contient maintenant un compte fictif, ce qui permet de récupérer les deals plus rapidement

## [1.0.4] - 2023-01-15

### Modifié

- Refactorisation du code
- Ajout de timeouts à chaque requete

### Supprimé

- getProduct() a été supprimé car il ne fonctionnait pas, et était sécurisé avec un oauth_signature

## [1.0.3] - 2023-01-14

### Corrigé

- Ajout du prix, réduction, marchand et les groupes du deals au hash

## [1.0.2] - 2023-01-14

### Modifié

- Génération d'un hash au lieu de prendre l'id du deal, sinon les modifications ultérieures à la création du deal n'étaient pas prises en compte

## [1.0.1] - 2023-01-13

### Ajouté

- Ajout de la fonctionalité permettant d'être prevenu lorsque les tokens pushOver vont expirer

## [1.0.0] - 2023-01-13

Création du projet
