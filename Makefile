.PHONY: dev test lint migrate seed-dev db-reset

# Lance le backend et le frontend en local (Redis, CTFd et Supabase sont démarrés séparément).
dev:
	docker compose up --build

test:
	cd backend && uv run pytest
	cd frontend && npm run test

lint:
	cd backend && uv run ruff check . && uv run ruff format --check . && uv run mypy app
	cd frontend && npm run lint && npm run typecheck

migrate:
	cd backend && uv run alembic upgrade head

# Remet la base locale à zéro puis réapplique les migrations (voir ADR 003).
db-reset:
	supabase db reset
	$(MAKE) migrate

# Données fictives de développement. Le script refuse de s'exécuter en production.
seed-dev:
	cd backend && uv run python -m app.scripts.seed_dev
