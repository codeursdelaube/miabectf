import sys

from app.core.config import get_settings


def main() -> int:
    if get_settings().app_env == "production":
        print("seed-dev refuse de s'exécuter en production.", file=sys.stderr)
        return 1
    print("Aucune donnée de développement à créer pour le moment.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
