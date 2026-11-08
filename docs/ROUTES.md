# Pages Next.js et protection

`proxy.ts` redirige selon la session pour le confort de navigation. L'autorisation réelle est faite par FastAPI à chaque appel de données. Dans Next.js 16, `params` et `searchParams` sont asynchrones.

| Chemin | Accès | Contenu |
|---|---|---|
| `/` | Public | Accueil |
| `/competitions` | Public | Liste filtrable |
| `/competitions/[slug]` | Public | Détail et inscription |
| `/competitions/[slug]/leaderboard` | Public | Classement de l'événement |
| `/leaderboard` | Public | Classement général, individuel, équipes |
| `/about`, `/rules`, `/privacy`, `/terms`, `/contact` | Public | Pages institutionnelles et légales |
| `/login`, `/register` | Invité | Redirection vers `/dashboard` si connecté |
| `/forgot-password` | Invité | Demande de réinitialisation |
| `/reset-password` | Lien email | Nouveau mot de passe |
| `/verify-email` | Lien email | Vérification |
| `/auth/callback` | Technique | Échange de code Supabase |
| `/ctfd/authorize/[eventId]` | Connecté | Point d'entrée SSO vers CTFd, l'événement est dans le chemin (ADR 001) |
| `/dashboard` | Connecté | Accueil participant |
| `/dashboard/profile` | Connecté | Profil, avatar, compétences |
| `/dashboard/competitions` | Connecté | Mes compétitions |
| `/dashboard/competitions/[id]/challenges` | Inscrit | Catalogue en lecture seule et lien vers l'instance |
| `/dashboard/teams` | Connecté | Mes équipes par événement |
| `/dashboard/notifications` | Connecté | Centre de notifications |
| `/admin` | organizer et plus | Tableau de bord |
| `/admin/events` | organizer et plus | Limité à ses événements pour un organisateur |
| `/admin/events/new` | admin et plus | Création |
| `/admin/events/[id]` | organizer et plus | Édition, transitions, instance CTFd |
| `/admin/events/[id]/challenges` | organizer et plus | Vue CTFd |
| `/admin/events/[id]/results` | organizer et plus | Scores, soumissions, CSV, publication, gel |
| `/admin/users`, `/admin/users/[id]` | admin et plus | Recherche, rôles, suspension |
| `/admin/organizers` | admin et plus | Assignations |
| `/admin/partners` | admin et plus | Partenaires |
| `/admin/audit` | admin et plus | Journal en lecture seule |

Un utilisateur dont `must_choose_username` est vrai est dirigé vers `/dashboard/profile` tant qu'il n'a pas choisi de username.
