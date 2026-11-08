# Avancement MIABÉ CTF

Légende : `[x]` fait et prouvé, `[ ]` à faire. Mentions possibles : `PARTIEL`, `NON TESTÉ`, `BLOQUÉ : <variable>`.

**Phase en cours : 0, terminée, en attente de validation.** Ne pas démarrer la phase 1 sans feu vert.

## Décisions à trancher

- [ ] **D1** — Option d'intégration CTFd. Recommandation : A avec SSO (ADR 001).
- [ ] **D2** — Retirer du périmètre portail les routes et tests de soumission de flag (conséquence de D1).
- [ ] **D3** — Ajouter la table `event_results`, hors SPEC §11.
- [ ] **D4** — Ajouter la table `partners`, hors SPEC §11.
- [ ] **D5** — Règle d'agrégation du classement général. Proposition : somme des scores des événements aux résultats publiés.
- [ ] **D6** — Installer Docker Desktop, uv et le CLI Supabase sur la machine de développement.

## Phase 0 — Analyse et architecture

- [x] Versions relevées (`docs/VERSIONS.md`). PARTIEL : Python 3.12, vite et TypeScript 7 à confirmer en phase 1.
- [x] Convention `proxy.ts` vérifiée dans la doc Next.js 16.
- [x] Vérification JWT Supabase étudiée. PARTIEL : comportement de `supabase start` non vérifié.
- [x] Hypothèses CTFd vérifiées sur la doc et le code 3.8.9. NON TESTÉ sur une instance réelle.
- [x] ARCHITECTURE, ADR 001 à 003, DATA_MODEL, API, ROUTES, PROGRESS, VERSIONS rédigés.
- [ ] Validation des décisions ci-dessus.

## Phase 1 — Initialisation

- [ ] Prérequis machine installés (D6).
- [ ] Vérifications restantes de `VERSIONS.md`.
- [ ] Vérifier la signature JWT de `supabase start`.
- [ ] `frontend/` : Next.js 16, Tailwind v4, DaisyUI 5, thèmes, motion, next-intl, TanStack Query, Vitest, Playwright, ESLint.
- [ ] `backend/` : structure FastAPI, configuration, logs, erreurs, `/api/v1/health`, SQLAlchemy async, Alembic, pytest, ruff, mypy.
- [ ] Racine : docker-compose, `.env.example`, `.gitignore`, Makefile, README minimal.
- [ ] `supabase init`.
- [ ] `make lint` et `make test` passent, page thémée affichée, `/api/v1/health` 200, `/docs` affiché.

## Phase 2 — Base de données, auth backend, rôles

- [ ] Modèles et migrations, contraintes, index, RLS, trigger `profiles`.
- [ ] `get_current_user`, `require_role`, `require_event_access`.
- [ ] GET/PATCH `/me`, disponibilité du username.
- [ ] Rate limiting Redis réutilisable.
- [ ] Service d'audit.
- [ ] Tests JWT, rôle non modifiable (API et RLS), suspension.

## Phase 3 — Design system et pages publiques

- [ ] Tokens, typographie, logo SVG, composants réutilisables.
- [ ] Header, menu mobile, footer, sélecteur de thème.
- [ ] Accueil et pages publiques.
- [ ] Endpoints publics : stats, events, leaderboard.
- [ ] Captures 375, 768, 1440 px, navigation clavier, test de liens.

## Phase 4 — Auth frontend, dashboard, profil

- [ ] Pages d'authentification, Google derrière un flag.
- [ ] Protection via `proxy.ts` et vérification serveur.
- [ ] `/dashboard`, profil, avatar, mes compétitions, sidebar.
- [ ] Client API typé et hooks.
- [ ] E2E inscription → vérification → connexion → profil.

## Phase 5 — Événements, inscriptions, équipes

- [ ] CRUD, machine à états, tâche planifiée idempotente.
- [ ] Inscriptions et équipes, invitations, verrouillage pendant `live`.
- [ ] Notifications in-app.
- [ ] Frontend inscription, équipes, notifications.
- [ ] Tests des règles, isolation entre événements, périmètre organisateur.
- [ ] E2E inscription événement et équipe.

## Phase 6 — Intégration CTFd (plan mode)

- [ ] Relire la doc pour chaque endpoint utilisé.
- [ ] `CTFdClient`, implémentation httpx, `FakeCTFdClient`.
- [ ] Association d'instance et test de connexion.
- [ ] Synchronisation idempotente.
- [ ] SSO portail → CTFd (selon D1), test d'intégration réel.
- [ ] Catalogue de challenges, filtres, cache Redis.
- [ ] Classements, gel et dégel.
- [ ] Tests contre le CTFd local avec 3 challenges de test.

## Phase 7 — Administration et organisateurs

- [ ] `/admin` : statistiques, événements, utilisateurs, organisateurs, challenges, résultats, audit.
- [ ] Vue organisateur restreinte.
- [ ] Tests de permissions de chaque route, export CSV vérifié.

## Phase 8 — Durcissement sécurité

- [ ] Audit et corrections : en-têtes, CORS, rate limits, uploads, markdown, logs, secrets, dépendances.
- [ ] `docs/SECURITY.md` et script de sauvegarde.

## Phase 9 — Docker prod, Nginx, documentation

- [ ] Dockerfiles multi-stage non root, `docker-compose.prod.yml`, Nginx, healthchecks.
- [ ] README complet.
- [ ] Suite complète et E2E.
- [ ] Tableau final des fonctionnalités avec preuves.
