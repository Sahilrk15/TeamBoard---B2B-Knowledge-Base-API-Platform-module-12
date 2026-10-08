# TeamBoard — B2B Knowledge Base API Platform

A backend for a B2B knowledge-base API. Companies register, receive an API
key, authenticate with JWT, search the knowledge base, and every search is
logged for usage tracking. Platform admins can view aggregate usage stats.

## Project structure

```
teamboard/
  manage.py
  teamboard/
    settings.py
    urls.py
  api/
    models.py          # Company, KBEntry, QueryLog
    serializers.py
    views.py            # RegisterView, LoginView, KBQueryView, UsageSummaryView
    urls.py
    signals.py           # post_save on User -> auto-create Company + api_key
    permissions.py       # IsAdminUser
    apps.py               # connects signals.py in ready()
    management/commands/seed_kb.py
    migrations/
  docker-compose.yml
  .env.example
  requirements.txt
```

## How to set up the database

This project uses PostgreSQL via Docker. All credentials live in a `.env`
file (never committed — see `.gitignore`).

1. Copy the example env file and adjust if you like:
   ```
   cp .env.example .env
   ```
2. Start Postgres:
   ```
   docker compose up -d
   ```
   This starts a `postgres:16` container using the credentials from `.env`,
   exposed on `localhost:5432`.

## How to run the server

1. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate   # on Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Make sure `docker compose up -d` (above) is running so Postgres is reachable.
4. Run the server:
   ```
   python manage.py runserver
   ```
5. The API is available at `http://127.0.0.1:8000/api/`.

## How to apply migrations

```
python manage.py makemigrations
python manage.py migrate
```

A `0001_initial.py` migration is already committed under
`api/migrations/`, so `migrate` alone is enough on a fresh clone — but
running `makemigrations` first is harmless and confirms nothing drifted.

## How to seed KB entries

```
python manage.py seed_kb
```

This loads 12 sample Q&A entries across all five categories (api,
database, cloud, framework, general), with several sharing keywords
(`select_related`, `JWT`, `transaction.atomic`, etc.) so search queries
return multiple results. It's safe to re-run — it uses `get_or_create` and
won't duplicate entries.

## What each endpoint does

### `POST /api/auth/register/` — public

Registers a new company. Creates a Django `User`; a `post_save` signal
(`api/signals.py`) auto-creates the linked `Company` row and generates its
`api_key`. The view then fills in the real `company_name` and returns a
JWT access token alongside the API key. Returns 400 if the username is
already taken.

### `POST /api/auth/login/` — public

Validates credentials with Django's `authenticate()` and, on success,
returns a fresh JWT access token plus the company's `company_name` and
`api_key`. Returns 401 with a clear error message on invalid credentials.

### `POST /api/kb/query/` — requires a JWT

Searches `KBEntry.question` and `KBEntry.answer` (case-insensitive,
`icontains`, combined with `Q` objects) for the given `search` term. The
company is read from `request.user.company` — never from the request
body, since the body can't be trusted to identify who's asking. The
search and the `QueryLog` write happen inside one `transaction.atomic()`
block, and a `QueryLog` is written even when nothing matches (0 results
is still a billable query). Returns 400 if `search` is missing or blank,
401 if no token is provided.

### `GET /api/admin/usage-summary/` — requires a JWT + ADMIN role

Returns `total_queries` (via `aggregate(Count('id'))`), `active_companies`
(distinct companies with at least one `QueryLog`), and the top 5
`top_search_terms` (grouped with `.values('search_term').annotate(count=Count('id'))`).
Access is enforced by the custom `IsAdminUser` permission class
(`api/permissions.py`), which checks `request.user.company.role`, not
Django's `is_staff`/`is_superuser`. A `CLIENT` company gets 403; no token
at all gets 401 (DRF distinguishes: authentication failed vs.
authentication succeeded but not authorized).

## Design decision

**Checking `Company.role` instead of Django's built-in `is_staff` /
`is_superuser` for admin access.** Django's staff/superuser flags are
about access to the Django admin site itself, a separate concern from
"is this B2B customer's account allowed to see platform-wide usage
stats." Keeping the admin/client distinction on the `Company` model
(a business-domain field) rather than overloading Django's auth flags
means the two concerns can evolve independently, if TeamBoard later adds
more roles (e.g. `analyst`, `billing`), it's a change to `Company.Role`
and `IsAdminUser`, not to how Django auth itself works.

## Postman testing
<img width="1920" height="1024" alt="SS1" src="https://github.com/user-attachments/assets/4f1ad06d-0e32-487d-a791-43df6b332c1c" />


The submission includes a Postman collection
(`teamboard.postman_collection.json`) covering all 11 required scenarios:
register success/duplicate, login success/failure, query success/
zero-results/blank-search/no-token, and usage-summary success/403/401.
Import it into Postman, set a `base_url` variable to
`http://127.0.0.1:8000`, and run requests top to bottom (register and
login save their token to a collection variable for the later requests).
