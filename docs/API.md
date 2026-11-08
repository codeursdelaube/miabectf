# API REST

Préfixe : `/api/v1`. Authentification : `Authorization: Bearer <access_token Supabase>`. Rôles : **P** public, **U** connecté non suspendu, **I** inscrit à l'événement, **O** organisateur de l'événement ou admin, **A** admin ou plus, **S** super_admin.

Sauf mention contraire, les routes supposent l'option A de l'ADR 001. Aucune route ne reçoit de flag.

## Public

| Méthode | Chemin | Rôle | Résumé |
|---|---|---|---|
| GET | `/health` | P | État du service |
| GET | `/stats` | P | Compétitions, participants, résolutions, équipes (zéro si vide) |
| GET | `/events` | P | Liste filtrable par statut, paginée |
| GET | `/events/{slug}` | P | Détail d'un événement publié |
| GET | `/events/{slug}/leaderboard` | P | Classement par `type=individual\|team` |
| GET | `/leaderboard` | P | Classement général agrégé |
| GET | `/partners` | P | Partenaires visibles |
| GET | `/usernames/{username}/availability` | P | Disponibilité, avec rate limit |

## Compte

| Méthode | Chemin | Rôle | Résumé |
|---|---|---|---|
| GET | `/me` | U | Profil courant |
| PATCH | `/me` | U | Champs non privilégiés uniquement |
| POST | `/me/avatar/upload-url` | U | URL signée, type et taille contrôlés |
| GET | `/me/dashboard` | U | Résumé de l'accueil participant |
| GET | `/me/events` | U | En cours, à venir, terminées |
| GET | `/me/teams` | U | Équipes par événement |
| GET | `/me/notifications` | U | Liste paginée |
| POST | `/me/notifications/{id}/read` | U | Marquer comme lue |
| POST | `/me/notifications/read-all` | U | Tout marquer comme lu |

## Inscriptions et équipes

| Méthode | Chemin | Rôle | Résumé |
|---|---|---|---|
| POST | `/events/{id}/registrations` | U | S'inscrire |
| DELETE | `/events/{id}/registrations/me` | I | Se désinscrire |
| POST | `/events/{id}/teams` | I | Créer une équipe |
| GET | `/events/{id}/teams/me` | I | Mon équipe |
| POST | `/events/{id}/teams/join` | I | Rejoindre par code |
| PATCH | `/teams/{id}` | Capitaine | Renommer |
| POST | `/teams/{id}/invitations` | Capitaine | Générer un code, rate limit |
| DELETE | `/teams/{id}/invitations/{invitation_id}` | Capitaine | Révoquer |
| DELETE | `/teams/{id}/members/{user_id}` | Capitaine | Retirer un membre |
| POST | `/teams/{id}/leave` | Membre | Quitter |
| POST | `/teams/{id}/captain` | Capitaine | Transférer le rôle |

## Jeu

| Méthode | Chemin | Rôle | Résumé |
|---|---|---|---|
| GET | `/events/{id}/challenges` | I | Catalogue en lecture seule pendant `live`, filtres catégorie, difficulté, résolu |
| GET | `/events/{id}/play` | I | URL de l'instance CTFd |

## SSO CTFd

| Méthode | Chemin | Appelant | Résumé |
|---|---|---|---|
| POST | `/ctfd-sso/{event_id}/codes` | U (page portail) | Émet un code à usage unique de 60 s après vérification de l'accès |
| POST | `/ctfd-sso/{event_id}/token` | Serveur CTFd, secret client | Échange le code contre un token opaque |
| GET | `/ctfd-sso/{event_id}/user` | Serveur CTFd, token opaque | Renvoie `id`, `name`, `email`, `team` |

## Administration et organisateurs

| Méthode | Chemin | Rôle | Résumé |
|---|---|---|---|
| GET | `/admin/stats` | A | Statistiques globales |
| GET | `/admin/events` | O | Filtré sur ses événements pour un organisateur |
| POST | `/admin/events` | A | Créer |
| GET, PATCH | `/admin/events/{id}` | O | Lire, modifier |
| DELETE | `/admin/events/{id}` | A | Uniquement en `draft` |
| POST | `/admin/events/{id}/transitions` | O | Transition validée et auditée |
| PUT | `/admin/events/{id}/instance` | A | Associer une instance |
| POST | `/admin/events/{id}/instance/test` | O | Tester la connexion |
| POST | `/admin/events/{id}/sync` | O | Relancer la synchronisation |
| GET | `/admin/events/{id}/challenges` | O | Vue CTFd et statistiques |
| GET | `/admin/events/{id}/submissions` | O | Soumissions, sans la valeur soumise |
| GET | `/admin/events/{id}/results.csv` | O | Export CSV |
| POST | `/admin/events/{id}/results/publish` | O | Publier les résultats |
| POST | `/admin/events/{id}/leaderboard/freeze` | O | Geler |
| POST | `/admin/events/{id}/leaderboard/unfreeze` | O | Dégeler |
| GET, POST | `/admin/events/{id}/organizers` | A | Lister, assigner |
| DELETE | `/admin/events/{id}/organizers/{user_id}` | A | Retirer |
| GET | `/admin/users` | A | Recherche et filtres |
| GET | `/admin/users/{id}` | A | Profil et historique |
| PATCH | `/admin/users/{id}/role` | A | Changer le rôle ; **S** pour tout ce qui touche `super_admin` |
| POST | `/admin/users/{id}/suspend` | A | Suspendre |
| POST | `/admin/users/{id}/unsuspend` | A | Rétablir |
| GET, POST | `/admin/partners` | A | Lister, créer |
| PATCH, DELETE | `/admin/partners/{id}` | A | Modifier, supprimer |
| GET | `/admin/audit-logs` | A | Lecture seule, filtres |

## Format des erreurs

```json
{ "error": { "code": "EVENT_NOT_OPEN", "message": "…", "request_id": "…" } }
```

Rate limiting Redis : authentification, invitations, disponibilité de username et endpoints publics.
