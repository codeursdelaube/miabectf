# ADR 003 — Propriété du schéma et trigger `profiles`

- **Statut** : proposé, en attente de validation.
- **Date** : 2026-11-08.

## Décision 1 — Alembic est la seule source de vérité du schéma `public`

- Tables, contraintes, index, privilèges, policies RLS et triggers sont créés par Alembic, le SQL non modélisable passant par `op.execute`.
- `supabase/migrations/` reste vide. `supabase/config.toml` ne décrit que l'environnement local.
- Les schémas `auth` et `storage` appartiennent à Supabase. `env.py` les exclut de l'autogénération via `include_name`.
- Une migration déjà appliquée n'est jamais modifiée : on en crée une nouvelle.
- Chaque migration a un `downgrade`, testé par un cycle `upgrade head` → `downgrade base` → `upgrade head` en CI locale.

## Décision 2 — Détection des écarts

L'autogénération ne voit ni les policies ni les triggers. Elle est donc complétée par :

- `alembic check` pour les tables, colonnes et index ;
- des tests pytest qui interrogent `pg_policies` et `pg_trigger` et exercent réellement les policies avec les rôles `anon` et `authenticated`.

## Décision 3 — Trigger `auth.users` → `public.profiles`

Une fonction `public.handle_new_user()` en `SECURITY DEFINER`, avec `search_path = ''`, s'exécute `AFTER INSERT ON auth.users`.

Le trigger ne doit **jamais** faire échouer une inscription, car une erreur y bloquerait la création du compte :

| Cas | Comportement |
|---|---|
| `username` présent, valide et libre | Utilisé tel quel |
| Absent (Google), invalide, réservé ou déjà pris | `user_<8 hex>` généré et `must_choose_username = true` |
| `role` ou autre champ privilégié dans les métadonnées | Ignoré : `raw_user_meta_data` est contrôlé par l'utilisateur |

Le rôle vaut toujours `participant` à la création. L'interface oblige à choisir un username lorsque `must_choose_username` est vrai.

## Décision 4 — Déroulé local

`make migrate` lance `alembic upgrade head` après `supabase start`. Comme `supabase db reset` efface la base, `make migrate` doit être relancé ensuite ; le Makefile enchaîne les deux dans une cible `db-reset`.

## Points à vérifier en phase 2

- Droit du rôle de migration à créer un trigger sur `auth.users` sur le projet hébergé comme en local.
- Création du bucket `avatars` et de ses policies par migration (`storage.buckets`) ou par configuration.
- Mode de connexion : les migrations doivent utiliser une connexion directe ou un pooler de session ; le paramétrage d'`asyncpg` derrière un pooler de transaction reste à confirmer dans la doc.
