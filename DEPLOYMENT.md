# LearnHub — Production Deployment Guide (Phase 8)

This app is already environment-driven — locally it just works with SQLite +
local file storage, and in production it automatically switches to
PostgreSQL + Cloudinary + HTTPS-enforced security **based on environment
variables alone**. No code changes needed to go live.

This has been verified locally:
- ✅ `python manage.py check --deploy` → **0 issues** with `DEBUG=False` + a real secret key
- ✅ `DATABASE_URL` correctly parses into a working PostgreSQL connection
- ✅ Cloudinary storage backend loads cleanly when `USE_CLOUDINARY=True`
- ✅ `collectstatic` works correctly with Whitenoise (131 files collected, compressed & hashed for cache-busting)

---

## 1. Choose a host: Railway or Render

Both are simple, affordable (or free-tier) options that support Django + PostgreSQL out of the box. Config files for both are already included:

- `railway.json` — for [Railway](https://railway.app)
- `render.yaml` — for [Render](https://render.com)

**Railway (recommended, easiest):**
1. Push this project to a GitHub repo
2. On Railway: New Project → Deploy from GitHub repo
3. Add a PostgreSQL database (Railway → "+ New" → Database → PostgreSQL) — it auto-injects `DATABASE_URL`
4. Add the environment variables listed in section 3 below (Railway → your service → Variables)
5. Railway auto-detects `railway.json` and runs migrations + starts Gunicorn automatically

**Render:**
1. Push this project to a GitHub repo
2. On Render: New → Blueprint → connect your repo → it reads `render.yaml` automatically
3. Add the remaining environment variables (Cloudinary, Razorpay) in the Render dashboard

## 2. Database: PostgreSQL

Locally the app uses SQLite automatically (zero config). In production, just set:

```
DATABASE_URL=postgres://user:password@host:5432/dbname
```

Both Railway and Render generate this for you automatically when you attach a PostgreSQL database — you don't need to construct it by hand.

## 3. Required environment variables

Copy `.env.example` to `.env` as a reference (do NOT commit `.env` — it's already in `.gitignore`). Set these in your hosting platform's dashboard:

| Variable | Required | Notes |
|---|---|---|
| `SECRET_KEY` | ✅ | Generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | ✅ | Set to `False` |
| `ALLOWED_HOSTS` | ✅ | Your domain(s), comma-separated, e.g. `learnhub.com,www.learnhub.com` |
| `CSRF_TRUSTED_ORIGINS` | ✅ | Full URLs with scheme, e.g. `https://learnhub.com,https://www.learnhub.com` |
| `DATABASE_URL` | ✅ | Auto-provided by Railway/Render when you attach PostgreSQL |
| `USE_CLOUDINARY` | ✅ | Set to `True` (see section 4 — required so uploads survive redeploys) |
| `CLOUDINARY_CLOUD_NAME` / `CLOUDINARY_API_KEY` / `CLOUDINARY_API_SECRET` | ✅ (if using Cloudinary) | From your Cloudinary dashboard |
| `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET` | ✅ | Use **Live Mode** keys (not Test Mode) for real payments |
| `TIME_ZONE` | optional | Defaults to `Asia/Kolkata` |

## 4. Media storage: why Cloudinary is required in production

Platforms like Railway/Render/Heroku use **ephemeral disks** — anything saved to `/media` (course videos, PDFs, thumbnails, generated certificates) is **permanently deleted every time you redeploy**. This app already ships with Cloudinary integration wired in via `django-cloudinary-storage`, so this is a one-time setup:

1. Sign up free at [cloudinary.com](https://cloudinary.com) (free tier is generous — 25 GB storage/bandwidth)
2. From your Cloudinary dashboard, copy: Cloud Name, API Key, API Secret
3. Set `USE_CLOUDINARY=True` + the three Cloudinary variables above
4. That's it — every `ImageField`/`FileField` upload (thumbnails, lesson videos, PDFs, certificates) automatically routes to Cloudinary instead of local disk

## 5. Domain & SSL

- Point your domain's DNS to your Railway/Render app (both give you a CNAME target in their dashboard)
- Both platforms **auto-provision free SSL certificates** (Let's Encrypt) once your domain is connected — no manual certificate setup needed
- This app already sets `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, and HSTS headers automatically whenever `DEBUG=False` — so once your domain + SSL is active, all traffic is force-redirected to HTTPS

## 6. First-time setup after deploying

Once deployed, run these once (Railway/Render both give you a shell/console tab, or run via their CLI):

```bash
python manage.py migrate
python manage.py createsuperuser
```

Then log into `/admin/` with your superuser to:
- Add Categories
- Approve your first Teacher account(s)
- Approve courses as they're submitted

## 7. Local production-mode testing (optional, before deploying)

You can simulate production settings locally before deploying, to catch config issues early:

```bash
export DEBUG=False
export ALLOWED_HOSTS=localhost,127.0.0.1
export SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
export CSRF_TRUSTED_ORIGINS=http://localhost:8000

python manage.py check --deploy   # should report 0 issues
python manage.py collectstatic --noinput
python manage.py runserver
```

## 8. Going further (post-launch hardening)

Not required to launch, but worth doing as you grow:
- **Error monitoring**: add [Sentry](https://sentry.io) (`pip install sentry-sdk`) to get notified of production errors
- **Email**: currently uses Django's console email backend (prints to logs) — switch to a real provider (SendGrid, Amazon SES, Resend) for password-reset emails etc.
- **Backups**: enable automatic PostgreSQL backups (both Railway and Render support this from their dashboard)
- **Rate limiting**: consider `django-ratelimit` on login/signup endpoints to prevent abuse
- **Custom video streaming**: if lesson videos get large, consider moving from Cloudinary to a dedicated video host (e.g. Cloudinary's own video transformations, Bunny Stream, or Mux) for adaptive streaming instead of raw file downloads
