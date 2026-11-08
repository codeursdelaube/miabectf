# MIABÉ CTF — Contexte permanent pour Claude Code

> Ce fichier est relu automatiquement à chaque session. Il contient les règles. La spécification fonctionnelle complète est dans `docs/SPEC.md`. L'avancement est dans `docs/PROGRESS.md`.

## 1. Mission

Plateforme publique de compétitions CTF née au Togo, ouverte à l'international.
- **Portail MIABÉ** (ce repo) : comptes, profils, événements, inscriptions, équipes, classements, notifications, administration, audit.
- **Moteur CTFd** (une instance par événement) : challenges, flags, soumissions, scoring.
- **FastAPI** orchestre : il est la seule source de logique métier et le seul à parler à CTFd.

## 2. Règles de travail (non négociables)

1. **Une phase à la fois.** Suivre `docs/PROGRESS.md`. Ne jamais commencer la phase suivante sans mon feu vert.
2. **Vérifier avant d'écrire.** Avant d'utiliser une lib ou une API : vérifier la version (`npm view <pkg> version`, `pip index versions <pkg>`) et la doc officielle (WebFetch). Ne jamais inventer un endpoint, une option ou une signature. Si un doute subsiste : le dire et écrire une ADR.
3. **"Terminé" = prouvé.** Une tâche est terminée seulement si : typecheck OK, lint OK, tests OK, et vérification manuelle effectuée. Montrer la commande exécutée et son résultat. Sinon : marquer `PARTIEL` ou `NON TESTÉ` dans PROGRESS.md.
4. **Ne jamais prétendre** qu'une fonctionnalité marche sans l'avoir exécutée.
5. **Commits atomiques** (Conventional Commits) à chaque sous-tâche verte. Jamais de commit avec tests rouges.
6. **Identifiants manquants** (Supabase, CTFd, SMTP, Google OAuth) : ajouter la variable à `.env.example`, coder derrière une interface, utiliser un fake dans les tests, noter `BLOQUÉ : <variable>` dans PROGRESS.md, et **continuer**.
7. **Demander avant** : ajouter une dépendance hors stack ci-dessous, changer l'architecture, supprimer des fichiers, modifier une migration déjà appliquée (en créer une nouvelle à la place).
8. **Fin de session obligatoire** : mettre à jour PROGRESS.md (fait / partiel / bloqué / prochaine étape), commit, puis résumé en 10 lignes max + liste des commandes que je dois lancer moi-même.

## 3. Stack (versions stables vérifiées en phase 0, figées ensuite)

### Frontend (`frontend/`)
- Next.js 16+ App Router, React, TypeScript `strict`.
- **Next.js 16 : `middleware.ts` est remplacé par `proxy.ts`** — vérifier dans la doc officielle et suivre la convention en vigueur. `params`/`searchParams` sont asynchrones.
- Tailwind CSS v4 (config CSS-first, pas de `tailwind.config.js`) + DaisyUI 5 via `@plugin "daisyui"` dans le CSS global. **Pas de shadcn/ui.**
- `motion` (import depuis `motion/react`), `lucide-react` (aucun emoji dans l'UI).
- `react-hook-form` + `zod` + `@hookform/resolvers`, `@tanstack/react-query` v5.
- `@supabase/ssr` + `@supabase/supabase-js` (auth et upload Storage uniquement).
- `next-intl` (français par défaut, structure prête pour l'anglais).
- Tests : Vitest + Testing Library ; E2E : Playwright.

### Backend (`backend/`)
- Python 3.12, FastAPI, Pydantic v2, `pydantic-settings`.
- SQLAlchemy 2 (async) + `asyncpg`, Alembic.
- `httpx` (client CTFd + Supabase), `PyJWT[crypto]` (vérification JWT Supabase via JWKS), `cryptography` (chiffrement des tokens CTFd).
- Redis pour rate limiting et cache classement.
- Outils : `uv`, `ruff`, `mypy`, `pytest`, `pytest-asyncio`.

### Infra
- Supabase CLI en local (`supabase start`), Docker Compose (backend, frontend, redis, CTFd local de dev), Nginx + HTTPS en prod.
- `Makefile` à la racine : `make dev`, `make test`, `make lint`, `make migrate`, `make seed-dev`.

## 4. Règles d'architecture

- **Le frontend ne lit/écrit jamais les tables métier directement.** Supabase JS sert uniquement à l'auth (session) et aux uploads via URL signée fournie par le backend. Tout le reste passe par FastAPI avec `Authorization: Bearer <access_token Supabase>`.
- **FastAPI vérifie le JWT** Supabase (JWKS / clés asymétriques ; repli sur le secret legacy seulement si la doc l'impose) et charge le rôle depuis `profiles`.
- **Rôles** : `participant`, `organizer`, `admin`, `super_admin` dans `profiles.role`. Modifiables uniquement par le backend. Les policies RLS interdisent à un utilisateur de modifier `role`, `is_suspended` et tout champ privilégié.
- **Le backend applique toutes les autorisations lui-même.** RLS = défense en profondeur, pas la seule barrière. Le contrôle frontend = confort UX uniquement.
- **Couches backend** : `api/` (routers, minces) → `services/` (logique) → `repositories/` (accès DB) → `models/`. Aucune requête SQL dans un router.
- **Source de vérité du schéma : Alembic** (tables, index, contraintes, policies RLS via `op.execute`, trigger `auth.users` → `profiles`). Le schéma `auth` appartient à Supabase.
- **Isolation des événements** : toute requête sur des données d'événement filtre par `event_id`. Un organisateur n'accède qu'aux événements de `event_organizers`. Tests dédiés obligatoires.
- **CTFd** : accès uniquement via `app/integrations/ctfd/` (interface `CTFdClient` + implémentation HTTP + `FakeCTFdClient` pour les tests). Tokens admin CTFd chiffrés en base (clé Fernet en env), jamais renvoyés par l'API, jamais loggés.
- **Les flags ne transitent jamais vers le frontend et ne sont jamais loggés.**
- **Dates** : `timestamptz` en UTC en base ; affichage via `Intl` dans le fuseau de l'événement (défaut `Africa/Lome`).
- **Données fictives** : autorisées uniquement via `make seed-dev` (marquées, jamais exécutées en prod). Statistiques publiques = vraies données ou zéro.

## 5. Conventions

- UI en français ; identifiants de code, routes API et commits en anglais.
- Chaque composant de données gère : chargement (skeleton), erreur, vide, succès.
- Accessibilité : labels, focus visibles, navigation clavier, contrastes AA, `aria-*` pertinents.
- Mobile-first ; tableaux → cartes empilées sur petit écran.
- Pas de bouton sans action, pas de lien sans destination (sinon : désactivé + tooltip « Bientôt disponible »).

## 6. Économie de contexte (abonnement Pro)

- Ne lire que les fichiers nécessaires à la tâche en cours.
- Pas de sous-agents sauf demande explicite.
- PROGRESS.md doit permettre de reprendre après `/clear` sans rien relire d'autre que CLAUDE.md, SPEC.md (section concernée) et PROGRESS.md.
