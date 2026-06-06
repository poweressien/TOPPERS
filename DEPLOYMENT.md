# TOPPERS — Deployment Guide

## ─── Google OAuth Setup ─────────────────────────────────

### Step 1: Create Google Cloud Project
1. Go to https://console.cloud.google.com/
2. Create a new project → name it "TOPPERS"
3. Go to **APIs & Services → OAuth consent screen**
4. Choose **External**, fill in app name "TOPPERS", support email
5. Add scopes: `email`, `profile`, `openid`
6. Save

### Step 2: Create OAuth Credentials
1. Go to **APIs & Services → Credentials**
2. Click **Create Credentials → OAuth Client ID**
3. Application type: **Web Application**
4. Name: TOPPERS Web
5. Authorised redirect URIs — add ALL of these:
   ```
   http://localhost:8000/accounts/google/login/callback/
   https://yourdomain.com/accounts/google/login/callback/
   https://yourusername.pythonanywhere.com/accounts/google/login/callback/
   ```
6. Click Create → copy **Client ID** and **Client Secret**

### Step 3: Add to .env
```
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

### Step 4: Add in Django Admin
1. Go to http://localhost:8000/admin/
2. Go to **Sites** → edit the default site
   - Domain: `localhost:8000` (dev) or `yourdomain.com` (prod)
   - Display name: TOPPERS
3. Go to **Social Applications → Add**
   - Provider: Google
   - Name: Google
   - Client ID: (paste from Step 2)
   - Secret Key: (paste from Step 2)
   - Sites: move `localhost:8000` to Chosen Sites
4. Save → Google OAuth is live ✅

---

## ─── PythonAnywhere Deployment ─────────────────────────

### Step 1: Create account
Sign up at https://www.pythonanywhere.com (free tier works for MVP)

### Step 2: Upload files
Option A — GitHub (recommended):
```bash
# In PythonAnywhere console:
git clone https://github.com/YOUR_USERNAME/toppers.git
```

Option B — Upload ZIP via Files tab, then:
```bash
cd /home/yourusername/
unzip toppers_project.zip
```

### Step 3: Create virtual environment
```bash
cd toppers_project
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Set environment variables
In PythonAnywhere → go to your web app → **Environment variables**:
```
DJANGO_SETTINGS_MODULE=toppers.settings.production
SECRET_KEY=generate-a-long-random-string
DATABASE_URL=sqlite:////home/yourusername/toppers_project/db.sqlite3
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

### Step 5: Set up the web app
1. Go to **Web tab → Add new web app**
2. Choose **Manual configuration → Python 3.11**
3. Set **Source code**: `/home/yourusername/toppers_project`
4. Set **Working directory**: `/home/yourusername/toppers_project`
5. Edit **WSGI file** — replace everything with:

```python
import os, sys
path = '/home/yourusername/toppers_project'
if path not in sys.path:
    sys.path.append(path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'toppers.settings.production'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

6. Set **Virtualenv**: `/home/yourusername/toppers_project/venv`
7. Static files:
   - URL: `/static/`   → Directory: `/home/yourusername/toppers_project/staticfiles`
   - URL: `/media/`    → Directory: `/home/yourusername/toppers_project/media`

### Step 6: Run setup commands
```bash
source venv/bin/activate
python manage.py migrate
python manage.py create_admin
python manage.py seed_data
python manage.py collectstatic --noinput
```

### Step 7: Reload
Click **Reload** in the Web tab → your site is live! 🚀

---

## ─── GitHub Push ────────────────────────────────────────

```bash
cd toppers_project
git init
git add .
git commit -m "Initial TOPPERS commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/toppers.git
git push -u origin main
```

Then on PythonAnywhere to update:
```bash
cd toppers_project
git pull origin main
python manage.py migrate
python manage.py collectstatic --noinput
# Reload web app in dashboard
```

---

## ─── Production Checklist ───────────────────────────────

- [ ] DEBUG=False in production
- [ ] SECRET_KEY is long and random (50+ chars)
- [ ] ALLOWED_HOSTS set to your domain
- [ ] HTTPS enabled (PythonAnywhere does this automatically)
- [ ] .env file is NOT committed to git
- [ ] Admin password changed from default
- [ ] Static files collected
- [ ] Google OAuth credentials added in Django admin
- [ ] Email SMTP configured for password resets
- [ ] VTPass API keys added for real airtime delivery
