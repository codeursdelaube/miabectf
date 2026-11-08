# MIABÉ CTF — Spécification fonctionnelle

> À placer dans `docs/SPEC.md`. Les sections marquées **[V2]** sont hors périmètre de la première version fonctionnelle : prévoir l'architecture, ne pas les implémenter.

## 1. Produit

- **Nom** : MIABÉ CTF. **Origine** : Togo. **Langue** : français (anglais prévu). **Gratuit** pour les participants.
- **Public** : étudiants, passionnés de cybersécurité, développeurs, pentesters, chercheurs, universités, communautés, entreprises, participants internationaux.
- **Positionnement** : une vraie plateforme technologique de compétition, pas un site institutionnel. Identité togolaise/africaine subtile, rendu international et premium.

## 2. Identité visuelle

- Thème sombre par défaut, thème clair optionnel (deux thèmes DaisyUI personnalisés : `miabe-dark`, `miabe-light`).
- Palette de départ : `#090D16` (fond), `#111827` (surfaces), `#2563EB` (primary), `#00D6A0` (accent), `#F8FAFC` (texte), `#94A3B8` (secondaire). Construire les tokens DaisyUI (primary, secondary, accent, neutral, base-100/200/300, info, success, warning, error) avec contrastes AA vérifiés.
- Logo textuel « MIABÉ CTF » en SVG, moderne, avec un symbole discret inspiré du Togo (ex. étoile ou bandes, stylisées). Pas de clichés, pas d'emojis.
- Animations Motion discrètes : transitions de page, apparition des sections, modales, cartes, feedback de soumission. Respecter `prefers-reduced-motion`.

## 3. Pages publiques

- **Header** : logo, Accueil, Compétitions, Classement, À propos, Connexion, bouton « Rejoindre une compétition ». Menu mobile.
- **Accueil** :
  - Hero — titre « L'intelligence. La technique. Le défi. » ; sous-titre « Entre dans l'univers de la cybersécurité. Résous des challenges, affronte les meilleurs talents et repousse tes limites avec MIABÉ CTF. » ; boutons « Découvrir les compétitions » et « Créer un compte » ; visuel terminal/interface de compétition (sobre, pas de science-fiction).
  - Statistiques réelles depuis l'API (compétitions, participants, challenges résolus, équipes). Zéro si vide.
  - Compétitions : cartes (bannière, nom, description, dates, durée, participants, solo/équipe, statut, bouton). Filtres : Toutes, À venir, Inscriptions ouvertes, En cours, Terminées.
  - Catégories : Web, Crypto, Forensics, Reverse, Pwn, Réseau, OSINT, Misc.
  - Aperçu du classement (top participants et équipes).
  - Communauté : esprit communautaire, scène cyber togolaise, partenaires (section vide gérable par l'admin, pas de faux partenaires).
- **Footer** : À propos, Contact, Règlement, Confidentialité, Conditions d'utilisation, réseaux sociaux (liens configurables), mention « Une initiative née au Togo ».
- Pages : `/competitions`, `/competitions/[slug]`, `/leaderboard`, `/about`, `/rules`, `/privacy`, `/terms`, `/contact`. Les pages légales contiennent un texte de base à faire relire (mentionné en tête de page dans le code, pas à l'écran).

## 4. Authentification (Supabase Auth)

- Inscription (nom complet, username unique, email, mot de passe, confirmation, acceptation des CGU), connexion, déconnexion, vérification email, mot de passe oublié, réinitialisation, sessions via `@supabase/ssr`, routes protégées.
- Connexion Google : préparée derrière un flag d'env, activée seulement si configurée.
- Après connexion → `/dashboard`.
- Username : regex stricte, unicité vérifiée côté backend, liste de mots réservés.

## 5. Espace participant (`/dashboard`)

- Accueil : « Bonjour, [nom] », mes compétitions, points, challenges résolus, position, activité récente, invitations d'équipe.
- Profil : nom, username, bio, avatar (upload Storage, type et taille contrôlés), compétences, liens, historique.
- Mes compétitions : en cours / à venir / terminées.
- Mes équipes (par événement) : créer, renommer, gérer les membres, inviter (code d'invitation aléatoire cryptographiquement sûr, expirable, révocable), rejoindre, quitter, transférer le rôle de capitaine. Règles : un utilisateur = une équipe par événement ; taille max définie par l'événement ; équipes verrouillées pendant `live` sauf réglage contraire.
- Centre de notifications.

## 6. Compétitions

Champs d'un événement : id (UUID), slug, titre, description, bannière, logo, règlement (markdown, rendu assaini), dates (publication, ouverture inscriptions, début, fin), fuseau, limite de participants, mode (`solo` | `team`), taille d'équipe min/max, format (`jeopardy`, `training`), statut, config scoring, config classement (gel), instance CTFd associée.

**Machine à états** (transitions contrôlées côté backend, chacune auditée) :
`draft → published → registration_open → upcoming → live → finished → archived`
Seul un `draft` peut être supprimé. Les transitions automatiques basées sur les dates passent par une tâche planifiée idempotente.

Chaque événement a ses propres inscriptions, équipes, challenges et classement. **Aucun mélange de données entre événements.**

## 7. Intégration CTFd

**Hypothèses à VÉRIFIER dans la doc officielle CTFd en phase 0 (ne pas les tenir pour acquises) :**
- API REST `/api/v1` avec authentification par token admin.
- Endpoints de gestion : users, teams, challenges, flags, hints, files, submissions, scoreboard, config.
- Le mode utilisateurs/équipes est un réglage de l'instance.
- Comportement de l'endpoint de tentative de flag : à quel utilisateur est attribuée une soumission faite avec un token admin ? Peut-on soumettre au nom d'un participant ?
- Options d'authentification unique entre un portail externe et CTFd (ce que propose la version open source, ce qui nécessite un plugin).
- Gel du scoreboard et règle de départage natifs.

**Décision à documenter (ADR) en phase 0**, avec deux options :
- **A — Jeu sur l'instance CTFd** : le participant joue sur `event-xxxx.miabectf.tg`. Le portail synchronise comptes/équipes et lit le scoreboard. Simple, robuste, mais UX partagée entre deux sites.
- **B — Jeu dans le portail** : le portail affiche les challenges et FastAPI relaie les soumissions. Meilleure UX, mais faisable seulement si l'API permet d'attribuer correctement la soumission au participant.
Recommander l'option la plus fiable selon ce que la doc confirme réellement.

**Dans tous les cas :**
- L'admin associe une instance CTFd existante (URL, token chiffré, statut, config). Bouton « Tester la connexion ».
- Synchronisation idempotente : utilisateurs et équipes inscrits → CTFd ; table de correspondance des identifiants.
- Lecture et cache (Redis, TTL court) des challenges et du scoreboard.
- Si option B : validation serveur uniquement, vérification événement + statut `live` + inscription + non-doublon, rate limiting par utilisateur et par challenge (ex. 10 tentatives/min, à configurer), messages : correct, incorrect, déjà résolu, compétition terminée, challenge indisponible, trop de tentatives.
- Le classement suit la règle de départage de CTFd (ne pas en inventer une autre).
- **[V2]** Provisionnement automatique d'instances CTFd.

## 8. Classement

- Général (agrégé multi-événements, règle d'agrégation documentée), individuel, équipes, par compétition.
- Ligne : position, avatar/logo, nom, points, challenges résolus, dernière résolution. Top 3 mis en évidence.
- Rafraîchissement après validation (invalidation cache) ; polling léger côté client pendant `live`.
- Gel/dégel par l'admin (aligné sur le gel CTFd).

## 9. Administration

- **Rôles** : `super_admin` (tout), `admin` (tout sauf gestion des super_admins), `organizer` (uniquement ses événements assignés).
- Dashboard : utilisateurs, compétitions (total / en cours), inscriptions, équipes, challenges, soumissions, résolutions, graphiques (lib de charts légère à valider).
- Événements : CRUD, transitions de statut, association CTFd.
- Utilisateurs : recherche, filtres, profils, rôles, suspension, historique.
- Organisateurs : assignation aux événements.
- Challenges : vue par événement depuis CTFd, synchronisation, statistiques. (L'édition des challenges se fait dans CTFd, pas de duplication.)
- Résultats : scores, soumissions, export CSV, publication, gel/dégel.
- **Journal d'audit** pour toute opération sensible (qui, quoi, cible, avant/après, IP, date). Lecture seule.

## 10. Notifications

- In-app : inscription confirmée, invitation d'équipe, début imminent, début, fin, résultats publiés.
- Architecture extensible : interface `NotificationChannel` (in-app maintenant, email via SMTP/Resend derrière une variable d'env).

## 11. Base de données (schéma `public`)

Tables : `profiles`, `events`, `event_registrations`, `teams`, `team_members`, `team_invitations`, `event_organizers`, `event_instances`, `ctfd_identity_map`, `notifications`, `audit_logs`.
Exigences : UUID, FK, index sur colonnes de filtrage, contraintes d'unicité (username, slug, une inscription par user/événement, une équipe par user/événement), `created_at`/`updated_at`, policies RLS, migrations reproductibles. Pas de tables de challenges/scores (elles vivent dans CTFd).

## 12. Sécurité

- Validation stricte des entrées (Zod + Pydantic), ORM paramétré, échappement/assainissement du markdown, en-têtes de sécurité (CSP, HSTS en prod, X-Frame-Options, Referrer-Policy), CORS restrictif.
- Rate limiting : auth, soumissions, invitations, endpoints publics.
- Uploads : types MIME vérifiés, taille max, noms régénérés, buckets avec policies.
- Secrets uniquement en variables d'env ; clé `service_role` jamais côté frontend.
- Logs structurés sans données sensibles ; audit des actions sensibles.
- Sauvegardes : script `pg_dump` + procédure documentée.
- **Challenges interactifs [V2]** : jamais sur le serveur du portail. Infra séparée, conteneurs éphémères avec limites CPU/mémoire, réseau restreint, utilisateur non privilégié, capabilities supprimées, TTL et destruction automatique, aucun accès au socket Docker. En V1 : uniquement des challenges statiques (fichiers + flags), et documentation de l'architecture cible.

## 13. Tests minimum

Inscription, connexion (JWT valide/expiré/forgé), création d'événement, transitions de statut, inscription à un événement, création/join/leave d'équipe, invitations, soumission de flag (correct/incorrect/doublon/hors délai/rate limit — avec `FakeCTFdClient`), classement, permissions par rôle, **isolation entre événements**, organisateur limité à ses événements. E2E Playwright : parcours inscription → inscription événement → équipe → classement.
