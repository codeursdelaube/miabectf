# MIABÉ CTF — Prompts par phase pour Claude Code

## Mise en place (une seule fois)

1. Crée le dossier `MIABE-CTF/`, fais `git init`.
2. Place `CLAUDE.md` à la racine et `SPEC.md` dans `docs/SPEC.md`.
3. Lance `claude` dans `MIABE-CTF/`.
4. Une phase = une session. Entre deux phases : `/clear`. Si la session devient longue : `/compact`.
5. Pour les phases 0 et 6, active le **plan mode** (Shift+Tab) avant d'envoyer le prompt, valide le plan, puis laisse coder.

---

## PHASE 0 — Analyse, recherche et architecture (plan mode)

```
Lis CLAUDE.md et docs/SPEC.md. Ne code rien dans cette phase, sauf la création des fichiers de documentation ci-dessous.

1. Vérifie les dernières versions stables et leur compatibilité : next, react, tailwindcss, daisyui, motion, lucide-react, react-hook-form, zod, @tanstack/react-query, @supabase/ssr, next-intl, vitest, playwright, fastapi, pydantic, sqlalchemy, alembic, asyncpg, pyjwt. Vérifie aussi dans la doc officielle Next.js 16 la convention proxy.ts vs middleware.ts, et dans la doc Supabase la méthode actuelle de vérification des JWT côté serveur (JWKS / clés asymétriques).
2. Étudie la documentation officielle de CTFd (API REST v1) et vérifie une par une les hypothèses de la section 7 de SPEC.md. Pour chaque hypothèse : confirmée / infirmée / non documentée, avec lien vers la source.
3. Crée :
   - docs/ARCHITECTURE.md : schéma (Mermaid) portail / FastAPI / Supabase / Redis / CTFd, flux d'auth, flux d'inscription et de synchronisation CTFd, flux de soumission.
   - docs/adr/001-ctfd-integration.md : option A vs B, ce que la doc confirme, ta recommandation argumentée.
   - docs/adr/002-auth-and-roles.md : vérification JWT, stockage des rôles, RLS.
   - docs/adr/003-schema-ownership.md : Alembic comme source de vérité, trigger profiles.
   - docs/DATA_MODEL.md : tables, colonnes, types, contraintes, index, policies RLS.
   - docs/API.md : liste des routes REST (méthode, chemin, rôle requis, résumé).
   - docs/ROUTES.md : arborescence des pages Next.js et leur protection.
   - docs/PROGRESS.md : checklist de toutes les phases 1 à 9 avec cases à cocher.
   - docs/VERSIONS.md : versions retenues.
4. Termine par la liste des décisions sur lesquelles j'ai besoin de trancher. Attends ma validation avant toute phase suivante.
```

## PHASE 1 — Initialisation

```
Lis CLAUDE.md, docs/PROGRESS.md, docs/VERSIONS.md, docs/adr/.
Objectif : squelette fonctionnel des deux applications.

- frontend/ : Next.js 16 (App Router, TS strict, src non utilisé, alias @/), Tailwind v4 + DaisyUI 5 avec thèmes miabe-dark/miabe-light, motion, lucide-react, next-intl (fr), TanStack Query provider, Vitest + Playwright configurés, ESLint. Structure : app/, components/, features/, hooks/, lib/, services/, types/, messages/, public/, styles/.
- backend/ : FastAPI avec structure app/{api,core,models,schemas,services,repositories,integrations,middleware}, config pydantic-settings, logging structuré, gestion d'erreurs centralisée, route GET /api/v1/health, SQLAlchemy async, Alembic initialisé, pytest configuré, ruff + mypy.
- Racine : docker-compose.yml (backend, frontend, redis, ctfd de dev), .env.example (toutes les variables, aucune valeur réelle, commentées), .gitignore, Makefile (dev, test, lint, migrate, seed-dev), README.md minimal.
- Supabase local via Supabase CLI (supabase init).

Définition de terminé : `make lint` et `make test` passent ; le frontend affiche une page avec le thème DaisyUI ; /api/v1/health répond 200 ; /docs OpenAPI s'affiche. Montre les sorties. Mets à jour PROGRESS.md, commit.
```

## PHASE 2 — Base de données, auth backend, rôles

```
Lis CLAUDE.md, docs/PROGRESS.md, docs/DATA_MODEL.md, docs/adr/002 et 003.

- Modèles SQLAlchemy + migrations Alembic pour toutes les tables de DATA_MODEL.md, avec contraintes, index, policies RLS et trigger auth.users → profiles.
- Vérification JWT Supabase (dépendance FastAPI get_current_user), chargement du rôle, dépendances require_role(...) et require_event_access(event_id).
- Endpoints profil : GET/PATCH /me (champs non privilégiés uniquement), vérification username.
- Rate limiting Redis générique (dépendance réutilisable).
- Journal d'audit : service + écriture dans audit_logs.
- Tests : JWT valide/expiré/forgé, un participant ne peut pas changer son rôle (API et RLS), suspension bloque l'accès.

Définition de terminé : migrations appliquées sur Supabase local, tests verts, sorties montrées. PROGRESS.md + commit.
```

## PHASE 3 — Design system et pages publiques

```
Lis CLAUDE.md, docs/PROGRESS.md, docs/SPEC.md sections 2 et 3.

- Design system : tokens des thèmes, typographie, logo SVG MIABÉ CTF, composants réutilisables (Button, Card, Badge statut, Skeleton, EmptyState, ErrorState, Modal, PageTransition, SectionReveal, DataTable responsive → cartes sur mobile).
- Header responsive + menu mobile, footer, sélecteur de thème.
- Page d'accueil complète (hero, stats, compétitions filtrables, catégories, aperçu classement, communauté).
- Pages /competitions, /competitions/[slug], /leaderboard, /about, /rules, /privacy, /terms, /contact.
- Backend : endpoints publics GET stats, GET events (filtres par statut), GET events/{slug}, GET leaderboard (vide tant que CTFd n'est pas branché, état vide propre).
- Les données viennent toutes de l'API. Aucune statistique inventée.

Définition de terminé : pages vérifiées à 375px, 768px et 1440px (captures Playwright), navigation clavier testée, aucun lien mort (test Playwright qui parcourt tous les liens). PROGRESS.md + commit.
```

## PHASE 4 — Auth frontend, dashboard participant, profil

```
Lis CLAUDE.md, docs/PROGRESS.md, docs/SPEC.md sections 4 et 5.

- Pages inscription, connexion, vérification email, mot de passe oublié, réinitialisation (react-hook-form + zod), connexion Google derrière un flag d'env.
- Protection des routes via proxy.ts (ou la convention confirmée en phase 0) + vérification serveur.
- /dashboard : accueil, profil (avatar via URL d'upload signée fournie par le backend, contrôle type/taille), mes compétitions, layout avec sidebar responsive.
- Client API typé dans services/ qui ajoute le token Supabase ; hooks TanStack Query.

Définition de terminé : parcours inscription → vérification → connexion → modification du profil testé en E2E sur Supabase local (Inbucket/Mailpit pour l'email). PROGRESS.md + commit.
```

## PHASE 5 — Événements, inscriptions, équipes

```
Lis CLAUDE.md, docs/PROGRESS.md, docs/SPEC.md sections 5 et 6.

- Backend : CRUD événements (admin/organizer), machine à états avec transitions validées et auditées, tâche planifiée idempotente pour les transitions par date, inscriptions (limites, statut requis), équipes (créer, renommer, inviter par code sécurisé expirable, rejoindre, quitter, transférer capitaine, verrouillage pendant live), notifications in-app associées.
- Frontend : inscription depuis la page de l'événement, gestion d'équipe dans le dashboard, centre de notifications.
- Tests : toutes les règles métier + isolation stricte entre deux événements + organisateur limité à ses événements.

Définition de terminé : tests verts, parcours E2E inscription événement + équipe. PROGRESS.md + commit.
```

## PHASE 6 — Intégration CTFd (plan mode)

```
Lis CLAUDE.md, docs/PROGRESS.md, docs/adr/001-ctfd-integration.md, docs/SPEC.md sections 7 et 8.
Relis la doc officielle CTFd pour chaque endpoint utilisé avant de l'implémenter.

- app/integrations/ctfd/ : interface CTFdClient, implémentation httpx (timeouts, retries, erreurs typées), FakeCTFdClient pour les tests.
- Association d'une instance existante à un événement (URL + token chiffré), bouton tester la connexion.
- Synchronisation idempotente utilisateurs/équipes avec table de correspondance.
- Challenges : listing par événement avec recherche et filtres (catégorie, difficulté, résolu/non résolu), cache Redis.
- Soumission des flags selon l'option retenue dans l'ADR 001, avec toutes les vérifications et messages de SPEC.md section 7, et rate limiting.
- Classement par événement, individuel, équipes, général ; gel/dégel ; invalidation du cache après résolution.
- Tester contre l'instance CTFd du docker-compose de dev avec 3 challenges de test créés par un script.

Définition de terminé : tests unitaires (fake) + test d'intégration contre le CTFd local, avec sorties montrées. Liste explicite de ce qui n'a pas pu être testé. PROGRESS.md + commit.
```

## PHASE 7 — Administration et organisateurs

```
Lis CLAUDE.md, docs/PROGRESS.md, docs/SPEC.md section 9.

- /admin avec sidebar responsive : dashboard statistiques + graphiques, événements, utilisateurs (recherche, filtres, rôles, suspension, historique), organisateurs, challenges par événement (lecture CTFd + synchro + stats), résultats (scores, soumissions, export CSV, publication, gel), journal d'audit.
- Vue organisateur restreinte à ses événements.
- Tests de permissions pour chaque route admin (participant → 403, organizer hors périmètre → 403).

Définition de terminé : tests verts, export CSV vérifié, PROGRESS.md + commit.
```

## PHASE 8 — Durcissement sécurité

```
Lis CLAUDE.md, docs/PROGRESS.md, docs/SPEC.md section 12.

Fais un audit de sécurité du code existant et corrige : en-têtes (CSP, HSTS prod), CORS, rate limits manquants, validation des uploads, assainissement du markdown, logs contenant des données sensibles, secrets, dépendances vulnérables (npm audit, pip-audit). Rédige docs/SECURITY.md (modèle de menaces, mesures, architecture cible des challenges interactifs V2) et le script de sauvegarde.
Liste chaque problème trouvé, sa gravité et sa correction.
```

## PHASE 9 — Docker prod, Nginx, documentation finale

```
Lis CLAUDE.md, docs/PROGRESS.md.

- Dockerfiles multi-stage (utilisateur non root), docker-compose.prod.yml, configuration Nginx (reverse proxy, HTTPS via Let's Encrypt, sous-domaines event-xxxx), healthchecks.
- README.md complet : présentation, prérequis, installation, configuration Supabase, variables d'env, lancement frontend/backend, installation CTFd, déploiement Docker, commandes utiles, dépannage.
- Lance toute la suite de tests et les E2E une dernière fois.

Livrable final : tableau des fonctionnalités de SPEC.md avec statut (OK testé / partiel / bloqué / V2) et la preuve associée.
```

---

## Prompt de reprise (après une interruption ou une limite d'usage)

```
Lis CLAUDE.md et docs/PROGRESS.md. Dis-moi en 5 lignes où on en est, puis reprends la prochaine tâche non terminée de la phase en cours.
```
