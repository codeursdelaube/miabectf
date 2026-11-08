# ADR 001 — Intégration CTFd : jeu sur l'instance ou dans le portail

- **Statut** : proposé, en attente de validation (décision D1 de `PROGRESS.md`).
- **Date** : 2026-11-08.
- **Version étudiée** : CTFd 3.8.9 (dernière release, 2026-10-22).

Sources : documentation officielle lorsqu'elle répond, sinon code source au tag `3.8.9`. Rien n'a encore été exécuté contre une instance réelle : chaque comportement ci-dessous reste à prouver par le test d'intégration de la phase 6.

## 1. Vérification des hypothèses de SPEC.md §7

| # | Hypothèse | Verdict | Constat | Source |
|---|---|---|---|---|
| 1 | API REST `/api/v1`, authentification par token admin | **Confirmée, à préciser** | En-tête `Authorization: Token <valeur>`. Tout utilisateur peut avoir un token, seules les actions de gestion exigent un admin. La doc dit `Content-Type: application/json` requis seulement avec un corps JSON, mais le code ignore le token si `request.is_json` est faux : **le client doit envoyer ce header aussi sur les GET**. | [Getting started](https://docs.ctfd.io/docs/api/getting-started/), [initialization L341-367](https://github.com/CTFd/CTFd/blob/3.8.9/CTFd/utils/initialization/__init__.py#L341-L367) |
| 2 | Endpoints users, teams, challenges, flags, hints, files, submissions, scoreboard, config | **Confirmée** | Tous présents, plus tags, topics, awards, tokens, notifications, brackets. | [Redoc](https://docs.ctfd.io/docs/api/redoc/) |
| 3 | Mode utilisateurs/équipes réglé par instance | **Confirmée** | Changer le mode fait perdre soumissions et historiques : le mode doit être verrouillé dès qu'une instance est associée. | [User modes](https://docs.ctfd.io/docs/settings/user-modes) |
| 4 | Soumission avec token admin attribuée au participant | **Non documentée, infirmée par le code** | `POST /challenges/attempt` ne lit aucun identifiant de participant : la soumission va au propriétaire du token (`get_current_user()`). Avec un token admin, elle serait donc créditée au compte admin. | [challenges.py L646-697](https://github.com/CTFd/CTFd/blob/3.8.9/CTFd/api/v1/challenges.py#L646-L697) |
| 5 | Authentification unique portail ↔ CTFd | **Doc contradictoire, code favorable** | La doc réserve le SSO aux offres Hosted/Enterprise. Le code open source contient pourtant un flux OAuth *authorization code* dont les trois endpoints sont configurables (voir §4). Aucun plugin nécessaire d'après le code. | [Single sign-on](https://docs.ctfd.io/docs/settings/single-sign-on), [auth.py L518-675](https://github.com/CTFd/CTFd/blob/3.8.9/CTFd/auth.py#L518-L675) |
| 6a | Gel natif du scoreboard | **Confirmée** | Les soumissions après le gel sont enregistrées mais masquées. `GET /scoreboard` appelle `get_standings()` sans `admin=True` : même un token admin y lit la vue gelée. | [Competition times](https://docs.ctfd.io/docs/settings/competition-times), [scores L50-53](https://github.com/CTFd/CTFd/blob/3.8.9/CTFd/utils/scores/__init__.py#L50-L53), [scoreboard.py L27-29](https://github.com/CTFd/CTFd/blob/3.8.9/CTFd/api/v1/scoreboard.py#L27-L29) |
| 6b | Règle de départage native | **Confirmée, doc imprécise** | La doc parle de l'ID de résolution le plus bas. Le tri réel est : score décroissant, date de dernière résolution croissante, puis ID croissant. Le portail doit reprendre l'ordre renvoyé par CTFd sans le recalculer. | [Scoring](https://docs.ctfd.io/docs/scoring/overview), [scores L97-101](https://github.com/CTFd/CTFd/blob/3.8.9/CTFd/utils/scores/__init__.py#L97-L101) |

Autres points utiles :

- Le classement CTFd est mis en cache 60 s côté CTFd ([scoreboard.py L27](https://github.com/CTFd/CTFd/blob/3.8.9/CTFd/api/v1/scoreboard.py#L27)).
- La limite native est de 10 tentatives incorrectes par minute par défaut, réglable ([challenges.py L735](https://github.com/CTFd/CTFd/blob/3.8.9/CTFd/api/v1/challenges.py#L735)).
- CTFd n'a pas de champ « difficulté » dans les ressources documentées. Convention proposée : un tag `difficulty:easy|medium|hard`.

## 2. Pistes examinées pour l'option B (jeu dans le portail)

| Piste | Résultat | Raison |
|---|---|---|
| B1 — `POST /challenges/attempt` avec le token admin | **Impossible** | Attribution au compte admin (hypothèse 4). |
| B2 — `POST /submissions` admin avec `user_id` et `type=correct` | **Rejetée** | L'endpoint écrit directement la ligne sans vérifier le flag ni passer par `chal_class.solve` ([submissions.py L117-148](https://github.com/CTFd/CTFd/blob/3.8.9/CTFd/api/v1/submissions.py#L117-L148)). Le portail devrait lire les flags et réimplémenter leur validation. La doc elle-même renvoie vers `attempt`. |
| B3 — Un token CTFd par participant | **Rejetée en V1** | `POST /tokens` crée un token uniquement pour l'appelant ([tokens.py L85-95](https://github.com/CTFd/CTFd/blob/3.8.9/CTFd/api/v1/tokens.py#L85-L95)). Il faudrait se connecter à la place de chaque participant, donc gérer leurs mots de passe CTFd et simuler le formulaire de login. |
| B4 — Plugin CTFd « soumission pour le compte de » | **Possible, reporté en V2** | Attribution correcte, mais code à maintenir et à installer sur chaque instance, à revalider à chaque version de CTFd. |

## 3. Comparaison

| Critère | A — Jeu sur l'instance | B — Jeu dans le portail (via B4) |
|---|---|---|
| Faisable sans modifier CTFd | Oui | Non |
| Attribution des soumissions | Native | Dépend d'un plugin maison |
| Scoring, anti-bruteforce, gel | Natifs | Natifs, mais re-routés par FastAPI |
| Exposition des flags au portail | Aucune | Transit par FastAPI |
| IP réelle dans les journaux CTFd | Oui | Non, sans configuration de proxy supplémentaire |
| UX | Deux sites, rendus transparents par le SSO | Un seul site |

## 4. Recommandation : option A avec SSO portail → CTFd

Le participant joue sur `event-xxxx.miabectf.tg` et n'a pas de second mot de passe : le portail agit comme fournisseur OAuth de l'instance.

Contrat exigé par le code de CTFd ([auth.py L518-675](https://github.com/CTFd/CTFd/blob/3.8.9/CTFd/auth.py#L518-L675)) :

1. CTFd redirige vers `OAUTH_AUTHORIZATION_ENDPOINT?response_type=code&client_id=…&scope=…&state=…`. L'URL étant construite avec un `?` fixe, l'endpoint configuré **ne doit pas contenir de query string** : l'événement est donc porté par le chemin. Aucun `redirect_uri` n'est envoyé, le portail le déduit de l'instance (`<base_url>/redirect`).
2. CTFd échange le code en POST `application/x-www-form-urlencoded` sur `OAUTH_TOKEN_ENDPOINT`, avec un délai de 5 s, et attend `access_token`.
3. CTFd lit `OAUTH_API_ENDPOINT` et attend `id`, `name`, `email`, plus `team.id` et `team.name` en mode équipe si l'utilisateur n'a pas encore d'équipe.

Conséquences de conception :

- `oauth_id` est un **entier unique** côté CTFd ([models L398](https://github.com/CTFd/CTFd/blob/3.8.9/CTFd/models/__init__.py#L398), [L624](https://github.com/CTFd/CTFd/blob/3.8.9/CTFd/models/__init__.py#L624)). Les UUID du portail ne conviennent pas : `profiles` et `teams` portent un `sso_id` entier.
- CTFd retrouve l'utilisateur **par email** ([L595](https://github.com/CTFd/CTFd/blob/3.8.9/CTFd/auth.py#L595)) : un changement d'email doit être resynchronisé.
- Avec les inscriptions CTFd fermées, seuls les comptes pré-synchronisés peuvent entrer ([L607-622](https://github.com/CTFd/CTFd/blob/3.8.9/CTFd/auth.py#L607-L622)). L'inscription au portail devient ainsi le seul accès à l'événement.
- Le portail refuse le SSO à un participant sans équipe synchronisée en mode équipe.
- Comme les endpoints SSO ne sont pas une API publique documentée de CTFd, la version de l'image est **figée** et le flux couvert par un test d'intégration.

**Plan de repli** si le test de phase 6 échoue : option A sans SSO, avec comptes créés via `POST /users` et identifiants envoyés par CTFd (`?notify=true`, [users.py L176](https://github.com/CTFd/CTFd/blob/3.8.9/CTFd/api/v1/users.py#L176)).

## 5. Impacts sur la spécification

- Le portail n'expose **aucune route de soumission de flag**. Les vérifications et messages de SPEC §7 (« Si option B ») sont assurés par CTFd.
- Les tests « soumission de flag » de SPEC §13 ne s'appliquent plus au portail. Ils sont remplacés par des tests de synchronisation, de SSO et de lecture du classement.
- « Invalidation du cache après résolution » (SPEC §8) n'est pas réalisable tel quel, le portail n'étant pas informé des résolutions. Le classement utilise un TTL Redis court (15 s proposé) et du polling pendant `live`, avec un retard maximal d'environ 75 s en cumulant le cache CTFd.
- L'interface `CTFdClient` reste découplée pour permettre B4 en V2 sans toucher aux services.
