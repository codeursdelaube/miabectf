# Architecture MIABÉ CTF

Ce document suppose l'option A de l'[ADR 001](adr/001-ctfd-integration.md) : jeu sur l'instance CTFd, avec SSO depuis le portail. Elle est en attente de validation.

## 1. Vue d'ensemble

```mermaid
flowchart LR
    B[Navigateur]
    subgraph Portail
        N[Next.js 16]
        F[FastAPI]
        R[(Redis)]
    end
    subgraph Supabase
        A[Auth]
        P[(Postgres)]
        S[Storage]
    end
    subgraph Evenement["Une instance par evenement"]
        C[CTFd]
    end

    B -->|pages| N
    B -->|session| A
    B -->|upload par URL signee| S
    B -->|Bearer JWT| F
    B -->|joue| C
    N -->|Bearer JWT| F
    F -->|JWKS| A
    F -->|SQLAlchemy| P
    F -->|URL signee| S
    F -->|rate limit, cache, codes SSO| R
    F -->|API admin par token| C
    C -->|OAuth code vers token et profil| F
```

Responsabilités :

| Composant | Rôle | Ne fait jamais |
|---|---|---|
| Next.js | Rendu, session Supabase, confort de navigation | Lire ou écrire les tables métier |
| FastAPI | Toute la logique métier et les autorisations, seul client de CTFd | Voir ou journaliser un flag |
| Supabase | Comptes, base, fichiers | Porter la logique métier |
| Redis | Rate limiting, cache court, codes SSO à usage unique, verrous | Stocker une donnée durable |
| CTFd | Challenges, flags, soumissions, scoring | Gérer les comptes en direct : inscriptions fermées |

## 2. Authentification

```mermaid
sequenceDiagram
    participant U as Navigateur
    participant N as Next.js proxy
    participant A as Supabase Auth
    participant F as FastAPI
    participant D as Postgres

    U->>A: Inscription ou connexion
    A->>D: Trigger cree profiles
    A-->>U: Session en cookies
    U->>N: Page protegee
    N->>N: getClaims, redirection si absent
    N-->>U: Page
    U->>F: Requete avec Bearer JWT
    F->>F: Verifie signature, exp, aud, iss via JWKS en cache
    F->>D: Charge role et is_suspended
    alt Suspendu ou role insuffisant
        F-->>U: 403
    else Autorise
        F-->>U: Donnees
    end
```

## 3. Inscription à un événement et synchronisation CTFd

```mermaid
sequenceDiagram
    participant U as Participant
    participant F as FastAPI
    participant D as Postgres
    participant C as CTFd

    U->>F: POST inscription
    F->>D: Verifie statut et limites, cree registration
    F->>D: Marque sync en attente, cree notification
    F-->>U: Inscription confirmee
    loop Tache de synchronisation idempotente
        F->>D: Lit les elements en attente
        F->>C: Cree ou met a jour user et team
        C-->>F: Identifiants CTFd
        F->>D: Ecrit ctfd_identity_map
    end
```

La synchronisation est idempotente grâce à `ctfd_identity_map` : un élément déjà associé est mis à jour, jamais recréé. Une erreur CTFd laisse l'élément en attente avec un compteur d'essais, sans faire échouer l'inscription.

## 4. Accès au jeu et soumission

```mermaid
sequenceDiagram
    participant U as Participant
    participant C as CTFd
    participant N as Next.js
    participant F as FastAPI
    participant R as Redis

    U->>C: Se connecter
    C-->>U: Redirection vers authorize de l'evenement
    U->>N: Page authorize avec session
    N->>F: Demande de code, Bearer JWT
    F->>F: Verifie live, inscription, sync, equipe
    F->>R: Code a usage unique, 60 s
    F-->>U: Redirection vers CTFd avec code et state
    C->>F: Echange du code contre un token
    C->>F: Lecture du profil
    F-->>C: id, name, email
    C-->>U: Session CTFd ouverte
    U->>C: Soumission de flag
    C->>C: Validation, anti-bruteforce, scoring
    C-->>U: Resultat
```

Le flag ne quitte jamais CTFd. Le portail n'a aucune route de soumission.

## 5. Classement

FastAPI lit `GET /scoreboard` et met le résultat en cache Redis (TTL 15 s proposé), en conservant l'ordre renvoyé par CTFd. Le client interroge l'API toutes les 30 s pendant `live`. Le gel s'appuie sur le réglage `freeze` de CTFd.

## 6. Transitions automatiques

Une boucle `asyncio` lancée au démarrage de FastAPI applique les transitions basées sur les dates. Un verrou Redis garantit une seule exécution entre plusieurs workers, sans dépendance ajoutée. Chaque transition n'a lieu que si le statut attendu est encore en place, ce qui la rend idempotente, et elle est auditée.

## 7. Déploiement cible

Nginx termine le HTTPS, sert `miabectf.tg` vers Next.js et FastAPI, et route `event-xxxx.miabectf.tg` vers l'instance CTFd concernée. L'image CTFd est figée en version exacte (voir [VERSIONS.md](VERSIONS.md)).
