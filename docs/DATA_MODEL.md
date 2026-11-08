# Modèle de données (schéma `public`)

Conventions pour toutes les tables, sauf mention contraire :

- `id uuid PK default gen_random_uuid()`, `created_at` et `updated_at timestamptz not null default now()`, avec un trigger de mise à jour de `updated_at`.
- Les statuts sont en `text` avec contrainte `CHECK`, plus simples à faire évoluer qu'un type `ENUM`.
- Toutes les dates sont en `timestamptz`, stockées en UTC.
- RLS activé partout. Sauf mention contraire, **aucun accès** pour `anon` et `authenticated` ; seul le rôle `miabe_backend` y accède (ADR 002).

## profiles

| Colonne | Type | Contraintes |
|---|---|---|
| id | uuid | PK, FK `auth.users(id)` ON DELETE CASCADE |
| sso_id | integer | identity, unique, entier exigé par CTFd |
| username | citext | not null, unique, `CHECK` regex `^[a-z0-9_-]{3,30}$` |
| must_choose_username | boolean | not null, default false |
| full_name | text | not null, default `''` |
| bio | text | longueur max 1000 |
| avatar_path | text | chemin Storage |
| skills | text[] | not null, default `{}` |
| links | jsonb | not null, default `{}` |
| role | text | not null, default `participant`, `CHECK` sur les 4 rôles |
| is_suspended | boolean | not null, default false |
| suspended_reason | text | |

Index : `role`, `is_suspended`. Policies : `authenticated` peut lire sa ligne et modifier `full_name`, `bio`, `avatar_path`, `skills`, `links`. Trigger de protection des champs privilégiés (ADR 002). `citext` doit être activé par la première migration.

## events

| Colonne | Type | Contraintes |
|---|---|---|
| slug | text | not null, unique |
| title, description | text | not null |
| banner_path, logo_path | text | |
| rules_markdown | text | not null, default `''` |
| published_at | timestamptz | |
| registration_opens_at, starts_at, ends_at | timestamptz | `CHECK` ordre chronologique |
| timezone | text | not null, default `Africa/Lome` |
| max_participants | integer | `CHECK > 0` |
| mode | text | not null, `solo` ou `team` |
| team_size_min, team_size_max | integer | requis si `team`, `CHECK min <= max` |
| teams_locked_during_live | boolean | not null, default true |
| format | text | not null, `jeopardy` ou `training` |
| status | text | not null, default `draft`, 7 statuts de SPEC §6 |
| scoring_config, leaderboard_config | jsonb | not null, default `{}` |
| results_published_at | timestamptz | |
| created_by | uuid | FK `profiles` |

Index : `status`, `starts_at`. Suppression autorisée uniquement en `draft`, contrôlée par le service.

## event_registrations

`event_id` FK, `user_id` FK, `status` (`registered`, `cancelled`, `disqualified`). Unique (`event_id`, `user_id`). Index `user_id`.

## teams

`event_id` FK, `sso_id integer identity unique`, `name text`, `created_by` FK. Unique (`event_id`, `name`) et unique (`id`, `event_id`), cette dernière servant de cible aux clés composites.

## team_members

`team_id`, `event_id`, `user_id` FK, `role` (`captain`, `member`), `joined_at`. FK composite (`team_id`, `event_id`) vers `teams(id, event_id)`. Unique (`event_id`, `user_id`) pour garantir une équipe par utilisateur et par événement. Index unique partiel sur `team_id` où `role = 'captain'` pour garantir un seul capitaine.

## team_invitations

`team_id`, `event_id` FK composite, `code_hash text unique` (SHA-256 ; le code en clair n'est jamais stocké), `created_by` FK, `expires_at not null`, `revoked_at`, `max_uses integer not null default 1`, `used_count integer not null default 0`. Index `team_id`.

## event_organizers

`event_id` FK, `user_id` FK, `assigned_by` FK. Unique (`event_id`, `user_id`). Index `user_id`.

## event_instances

`event_id` FK unique, `base_url text not null`, `admin_token_encrypted text not null` (Fernet, jamais renvoyé ni journalisé), `sso_client_id text not null unique`, `sso_client_secret_encrypted text not null`, `status` (`unlinked`, `connected`, `error`), `ctfd_version text`, `config jsonb`, `last_checked_at`.

## ctfd_identity_map

`event_id` FK, `entity_type` (`user`, `team`), `portal_id uuid`, `ctfd_id integer` (null tant que non créé), `sync_status` (`pending`, `synced`, `failed`), `sync_attempts integer default 0`, `last_error text`, `last_synced_at`. Unique (`event_id`, `entity_type`, `portal_id`) et unique (`event_id`, `entity_type`, `ctfd_id`). Index `sync_status`.

## notifications

`user_id` FK, `event_id` FK nullable, `type text not null`, `payload jsonb not null`, `read_at`. Index (`user_id`, `read_at`, `created_at DESC`).

## audit_logs

`actor_id` FK nullable, `actor_role text`, `action text not null`, `target_type text`, `target_id text`, `event_id` nullable, `before jsonb`, `after jsonb` (secrets retirés), `ip inet`, `user_agent text`, `request_id text`, `created_at`. Pas de `updated_at`. Un trigger refuse `UPDATE` et `DELETE`. Index `actor_id`, `action`, `event_id`, `created_at DESC`.

## Tables proposées hors SPEC §11 (décisions D3 et D4)

**event_results** — instantané écrit à la publication des résultats : `event_id`, `entity_type`, `portal_id`, `rank`, `score`, `solves_count`, `last_solve_at`. Unique (`event_id`, `entity_type`, `portal_id`). Nécessaire car une instance CTFd peut être arrêtée après l'événement, alors que le classement général et les statistiques publiques doivent subsister. Ce n'est pas une copie des challenges : seul le résultat final est conservé.

**partners** — `name`, `logo_path`, `url`, `display_order`, `is_visible`. Nécessaire pour la section partenaires gérable par l'admin (SPEC §3), absente de §11.
