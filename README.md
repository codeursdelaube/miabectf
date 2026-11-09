# MIABÉ CTF

Plateforme publique de compétitions CTF née au Togo. Le portail gère les comptes, les événements, les équipes et les classements, et s'appuie sur une instance CTFd par événement.

## Démarrage

Prérequis : Node.js 20.9 ou plus, [uv](https://docs.astral.sh/uv/), Docker et le CLI Supabase.

```bash
cp .env.example .env
cd backend && uv sync && uv run uvicorn app.main:app --reload
cd frontend && npm install && npm run dev
```

- Frontend : <http://localhost:3000>
- API : <http://localhost:8000/api/v1/health>
- Documentation de l'API : <http://localhost:8000/docs>

Commandes du `Makefile` : `make dev`, `make test`, `make lint`, `make migrate`, `make seed-dev`.

La spécification et l'architecture sont dans [docs/](docs/). L'avancement est dans [docs/PROGRESS.md](docs/PROGRESS.md).
