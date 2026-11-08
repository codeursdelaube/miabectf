# ADR 002 — Authentification, rôles et RLS

- **Statut** : proposé, en attente de validation.
- **Date** : 2026-11-08.

## Contexte

Supabase Auth gère les comptes. FastAPI est la seule barrière d'autorisation métier (CLAUDE.md §4). RLS est une défense en profondeur, notamment parce que la clé publique Supabase présente dans le navigateur donne accès à l'API auto-générée du schéma `public`.

## Décision 1 — Vérification des JWT côté FastAPI

Vérification locale avec `PyJWT[crypto]` et les clés publiques du projet :

- **JWKS** : `{SUPABASE_URL}/auth/v1/.well-known/jwks.json` ([JWTs](https://supabase.com/docs/guides/auth/jwts)).
- **Algorithmes acceptés** : liste blanche `ES256`, `RS256`. `HS256` et `none` sont refusés ([Signing keys](https://supabase.com/docs/guides/auth/signing-keys)).
- **Claims contrôlés** : signature, `exp`, `aud == "authenticated"`, `iss == {SUPABASE_URL}/auth/v1`, `sub` au format UUID ([JWT fields](https://supabase.com/docs/guides/auth/jwt-fields)).
- **Cache des clés** : 10 minutes maximum. La doc indique que les caches cumulés sont purgés en 20 minutes et déconseille de garder les clés plus longtemps. Un `kid` inconnu déclenche un seul rafraîchissement, limité en fréquence pour éviter un déni de service.

**Repli pour un projet en secret partagé (HS256)** : la doc précise que le JWKS est alors vide, et recommande d'appeler `GET {SUPABASE_URL}/auth/v1/user` plutôt que de vérifier localement avec le secret. Le secret legacy n'est donc **pas** utilisé. Ce repli est activé uniquement par `SUPABASE_AUTH_MODE=remote`.

**Non vérifié** : l'algorithme utilisé par défaut par `supabase start` et le fonctionnement du JWKS en local. La page de configuration du CLI n'a pas pu être lue (délai dépassé). À établir en phase 1, avant d'écrire la dépendance `get_current_user`.

## Décision 2 — Côté Next.js

- `proxy.ts` remplace `middleware.ts`, avec une fonction exportée `proxy`, et s'exécute uniquement en runtime Node.js ([proxy](https://nextjs.org/docs/app/api-reference/file-conventions/proxy), [upgrade 16](https://nextjs.org/docs/app/guides/upgrading/version-16)).
- `supabase.auth.getClaims()` protège les pages. `getSession()` n'est jamais utilisé comme preuve d'identité côté serveur ([Next.js SSR](https://supabase.com/docs/guides/auth/server-side/nextjs)).
- `proxy.ts` sert au confort de navigation. Next.js rappelle de ne pas s'y fier seul pour les Server Functions ; ici, chaque appel de données est de toute façon autorisé par FastAPI.

## Décision 3 — Stockage et chargement des rôles

- Le rôle vit dans `profiles.role` (`participant`, `organizer`, `admin`, `super_admin`). Il n'est **pas** copié dans le JWT.
- `get_current_user` relit le profil à chaque requête : une suspension ou un changement de rôle s'applique immédiatement, sans attendre l'expiration du token.
- Dépendances FastAPI : `require_role(...)` et `require_event_access(event_id)`. Cette dernière consulte `event_organizers` pour le rôle `organizer`.
- `admin` ne peut ni modifier ni créer de `super_admin`. Le premier `super_admin` est créé par une commande CLI serveur, jamais par l'API.

## Décision 4 — RLS

- RLS activé sur **toutes** les tables du schéma `public`, sans exception.
- Droits par défaut révoqués pour `anon` et `authenticated`, puis accordés au cas par cas.
- Une seule surface directe : `authenticated` peut lire son propre profil et en modifier les colonnes non privilégiées (voir `DATA_MODEL.md`). Le frontend n'en a pas besoin selon CLAUDE.md, ces policies servent de défense en profondeur et rendent l'interdiction testable.
- Les champs privilégiés sont protégés deux fois : privilèges `UPDATE` limités aux colonnes non sensibles, et trigger `BEFORE UPDATE` refusant toute modification de `role`, `is_suspended` et `sso_id` hors rôle backend.
- `(select auth.uid())` plutôt que `auth.uid()` dans les policies, pour les performances ([RLS](https://supabase.com/docs/guides/database/postgres/row-level-security)).
- Les fonctions `SECURITY DEFINER` fixent `search_path = ''`.

## Décision 5 — Connexion du backend à Postgres

Deux rôles distincts :

| Rôle | Usage | Droits |
|---|---|---|
| `postgres` | Migrations Alembic uniquement | Propriétaire |
| `miabe_backend` | Application FastAPI | DML sur `public`, `BYPASSRLS`, aucun DDL |

Le backend applique lui-même les autorisations, d'où `BYPASSRLS` ; l'absence de DDL limite l'impact d'une injection. La clé secrète Supabase reste réservée aux opérations Storage et Admin Auth côté serveur.

## Conséquences

- Tests requis (phase 2) : JWT valide, expiré, forgé, mauvais `aud`, mauvais `iss`, `alg` non autorisé ; participant qui tente de changer son rôle via l'API **et** via PostgREST ; suspension effective à la requête suivante.
