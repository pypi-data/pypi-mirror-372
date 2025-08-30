⚠️ **ATTENTION : Cette librairie est expérimentale. Ne pas utiliser en production. Aucun support ni garantie.**

# DRF-SSO

Librairie permettant de mettre en oeuvre du SSO sur une app full-stack utilisant Django Rest Framework comme backend.

## Technologies SSO supportées

- CAS - Supporté
- SAMLv2 - Supporté (Pas encore toutes les features (SLS, Relay, Vérification des ID req/response))
- OAuth - Supporté
- OIDC - Supporté

## Configuration

La configuration de ce paquet pourra se faire de deux manières différentes : 

- Dossier de configuration avec fichiers JSON (et éventuellement certificats x509 pour le SAML)
- Installation dans settings.py

## Intégration avec le frontend

La librairie exposera des vues effectuant des redirections vers les services SSO pour la connexion.
Elle gérera la récupération des attributs utilisateurs sur les Identity Provider et lancera une méthode callback avec ces derniers en paramètres.
Le développeur devra définir comment compléter ses fichers utilisateurs à partir des attributs.
Ensuite un callback frontend sera appelé avec un handover token (Jeton JWT de très courte durée).
Ce callback devra être implémenté de manière à effectuer une requête POST sur un endpoint exposé par la librairie afin d'échanger l'handover token pour
les jetons JWT d'accès et de rafraîchissement concernant l'utilisateur venant de se connecter.