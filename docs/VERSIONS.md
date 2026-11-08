# Versions retenues

Relevé du 2026-11-08 (`npm view`, `pip index versions`, API GitHub et Docker Hub). Les versions sont à figer dans les fichiers de verrouillage en phase 1.

## Frontend

| Paquet | Version | Compatibilité vérifiée (dépendances pairs) |
|---|---|---|
| next | 16.4.5 | Node >= 20.9.0, React ^19 |
| react, react-dom | 19.3.1 | |
| tailwindcss | 4.3.5 | |
| daisyui | 5.7.50 | |
| motion | 14.10.1 | React ^19, pair `remix` optionnel |
| lucide-react | 1.70.0 | React ^19 |
| react-hook-form | 7.91.0 | React ^19 |
| zod | 4.6.7 | |
| @hookform/resolvers | 7.0.3 | react-hook-form ^7.55, zod ^4 |
| @tanstack/react-query | 5.107.1 | React ^19 |
| @supabase/ssr | 0.12.7 | supabase-js ^2.114 |
| @supabase/supabase-js | 2.119.0 | |
| next-intl | 4.14.9 | next ^16, React ^19 |
| vitest | 5.1.0 | vite ^6.4, ^7 ou ^8 ; @types/node ^22 ou >= 24 |
| @playwright/test | 1.65.0 | next demande ^1.51.1 |
| typescript | 7.0.2 | **À valider**, voir ci-dessous |

## Backend (cible Python 3.12)

| Paquet | Version |
|---|---|
| fastapi | 0.162.2 |
| pydantic | 2.14.3 |
| pydantic-settings | 2.16.2 |
| sqlalchemy | 2.1.8 |
| alembic | 1.20.1 |
| asyncpg | 0.32.0 |
| pyjwt | 2.15.1 |
| httpx | 0.28.1 |
| cryptography | 50.0.2 |
| redis (client) | 8.1.0 |
| uv | 0.13.7 |
| ruff | 0.17.4 |
| mypy | 2.4.1 |
| pytest | 9.2.0 |
| pytest-asyncio | 1.4.1.post1 |

## Infrastructure

| Élément | Version | État |
|---|---|---|
| CTFd (image `ctfd/ctfd`) | 3.8.9 | Tag présent sur Docker Hub, à figer |
| Node.js (Docker) | LTS courante | Numéro à fixer au moment du Dockerfile |
| Supabase CLI | Non relevée | Non installé, API injoignable lors du relevé |
| Redis (serveur) | Non relevée | À fixer dans docker-compose |

## Restant à confirmer en phase 1

Le réseau a coupé pendant ces vérifications, elles ne sont donc **pas** acquises :

- **Python 3.12** : `pip index` a filtré les versions avec le Python 3.14 local. La preuve sera un `uv lock --python 3.12` réussi.
- **vite** : version non relevée. Choisir la dernière version compatible avec vitest 5.1.
- **TypeScript 7.0.2** : Next.js demande au moins 5.1, mais la compatibilité de la 7 avec Next.js et ESLint n'est pas établie. Si le typecheck échoue, se replier sur la dernière version antérieure compatible.

## Convention confirmée dans la doc Next.js 16

`proxy.ts` remplace `middleware.ts`, fonction exportée `proxy`, runtime Node.js uniquement. Node 20.9 minimum. `params` et `searchParams` sont exclusivement asynchrones.

## Machine de développement

| Outil | État |
|---|---|
| Node.js | 25.2.1 (version impaire, sans support long terme) |
| Python | 3.14.2, uv installera 3.12 |
| Docker | **Non installé**, requis dès la phase 1 |
| uv | **Non installé**, requis dès la phase 1 |
| Supabase CLI | **Non installé**, requis dès la phase 1 |
