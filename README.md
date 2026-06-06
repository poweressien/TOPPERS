# 🏆 TOPPERS – Gamified Learning & Rewards Platform

A full-stack Django + DRF platform combining competitive quizzes, live challenges,
airtime rewards, referrals, leaderboards, and achievements — built for the Nigerian market.

---

## ⚡ Quick Start (Local Development)

### 1. Clone & set up environment

```bash
git clone https://github.com/YOUR_USERNAME/toppers.git
cd toppers_project

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env — at minimum set SECRET_KEY and DATABASE_URL
```

### 3. Create PostgreSQL database

```sql
CREATE USER toppers_user WITH PASSWORD 'password';
CREATE DATABASE toppers_db OWNER toppers_user;
GRANT ALL PRIVILEGES ON DATABASE toppers_db TO toppers_user;
```

### 4. Run migrations & seed data

```bash
python manage.py migrate
python manage.py create_admin       # Creates admin / Admin@1234
python manage.py seed_data          # Seeds categories + sample questions
```

### 5. Start the server

```bash
# Django dev server (HTTP only — no WebSocket)
python manage.py runserver

# With WebSocket support (Channels / Daphne)
daphne -p 8000 toppers.routing:application
```

Visit: http://localhost:8000/admin/

---

## 🗂️ Project Structure

```
toppers_project/
├── manage.py
├── requirements.txt
├── .env.example
├── toppers/                  # Django project config
│   ├── settings/
│   │   ├── base.py           # Shared settings
│   │   ├── development.py    # Dev overrides (DEBUG=True)
│   │   └── production.py     # Prod hardening
│   ├── urls.py               # Root URL conf
│   ├── routing.py            # ASGI + Channels routing
│   └── celery.py             # Celery app
└── apps/
    ├── accounts/             # Users, auth, referrals
    ├── quiz/                 # Categories, questions, answers
    ├── games/                # Game sessions, lifelines, daily challenges
    ├── rewards/              # Points, achievements, airtime redemption
    ├── leaderboards/         # Global / weekly / monthly boards
    ├── challenges/           # Live 1v1 challenge mode + WebSocket
    ├── notifications/        # In-app notifications
    └── advertisements/       # Rewarded ads system
```

---

## 🎮 Game Modes

| Mode           | Questions | Description                              |
|----------------|-----------|------------------------------------------|
| Classic        | 15        | Millionaire-style, escalating difficulty |
| Daily Challenge| 10        | One per day, streak tracking             |
| Survival       | Unlimited | Play until you get one wrong             |
| Speed          | Many      | Answer as many as possible in 60 seconds |
| Live Challenge | 10        | Real-time 1v1 battle via WebSocket       |

---

## 💡 Lifeline System

| Lifeline       | Effect                                   |
|----------------|------------------------------------------|
| 50:50          | Removes 2 wrong answers                  |
| Phone a Friend | AI-powered confidence hint               |
| Ask the Audience | Simulated community vote              |
| Skip           | Skip question, no penalty               |
| Second Chance  | One retry on a wrong answer             |

---

## 💰 Points & Airtime

| Difficulty | Points per Question |
|------------|---------------------|
| Easy       | 10                  |
| Medium     | 25                  |
| Hard       | 50                  |
| Expert     | 100                 |

**Conversion rate:** 1,000 points = ₦50 airtime (configurable via `.env`)  
**Minimum redemption:** 2,000 points = ₦100  
**Supported networks:** MTN, Airtel, Glo, 9Mobile

---

## 📡 API Endpoints

### Auth  `/api/v1/auth/`
```
POST  register/              Register new user
POST  login/                 JWT login
POST  logout/                Blacklist refresh token
POST  token/refresh/         Refresh access token
POST  change-password/       Change password
GET   referral/<code>/validate/   Validate referral code
```

### Users  `/api/v1/users/`
```
GET/PATCH  me/               Profile (read / update)
GET        me/stats/         Detailed stats
GET        me/referrals/     Referral dashboard
GET        <username>/       Public profile
```

### Quiz  `/api/v1/quiz/`
```
GET  categories/             All top-level categories
GET  categories/<slug>/      Category detail
GET  questions/              List questions (filter: difficulty, category)
GET  questions/random/       Random questions (?count=&difficulty=&category=)
GET  questions/classic-set/  15-question Millionaire set
```

### Games  `/api/v1/games/`
```
POST  sessions/              Start a new game session
GET   sessions/<id>/         Session detail + questions
POST  sessions/<id>/answer/  Submit answer for current question
POST  sessions/<id>/use-lifeline/  Use a lifeline
POST  sessions/<id>/abandon/ Abandon session
GET   sessions/history/      Completed sessions
GET   lifelines/             User's lifeline inventory
GET   daily-status/          Daily game count + challenge status
```

### Rewards  `/api/v1/rewards/`
```
GET   points/                Balance + naira equivalent
GET   transactions/          Full transaction history
POST  daily-bonus/           Claim daily login bonus
GET   achievements/          All platform achievements
GET   achievements/mine/     User's earned achievements
POST  airtime/redeem/        Redeem points for airtime
GET   airtime/history/       Redemption history
```

### Leaderboards  `/api/v1/leaderboards/`
```
GET  global/                 All-time global ranking
GET  weekly/                 This week's ranking
GET  monthly/                This month's ranking
```

### Challenges  `/api/v1/challenges/`
```
POST  /                      Send a challenge
GET   /                      My challenges (sent + received)
POST  <id>/accept/           Accept incoming challenge
POST  <id>/decline/          Decline challenge
POST  <id>/submit-score/     Submit final score
GET   <id>/results/          Challenge results
GET   pending/               Pending incoming challenges
```

### Notifications  `/api/v1/notifications/`
```
GET   /                      All notifications
GET   unread/                Unread count
POST  read-all/              Mark all as read
POST  <id>/read/             Mark one as read
```

### Ads  `/api/v1/ads/`
```
GET   /                      Active advertisements
POST  <id>/view/             Record ad view + claim reward
```

---

## 🔌 WebSocket (Live Challenge)

```
ws://localhost:8000/ws/challenge/<challenge_id>/
```

**Events sent by client:**
```json
{ "type": "answer_submitted", "question_id": "...", "is_correct": true, "score": 50 }
{ "type": "challenge_complete", "final_score": 250, "correct": 8 }
```

**Events received from server:**
```json
{ "type": "player_joined", "username": "..." }
{ "type": "answer_update", "username": "...", "score": 50, "is_correct": true }
{ "type": "player_finished", "username": "...", "final_score": 250 }
```

---

## ⚙️ Management Commands

```bash
python manage.py seed_data       # Seed categories + questions + achievements
python manage.py create_admin    # Create default admin user
python manage.py migrate         # Run DB migrations
python manage.py collectstatic   # Collect static files (production)
```

---

## 🚀 Celery (Async Tasks)

```bash
# Start worker
celery -A toppers worker -l info

# Start beat scheduler (periodic tasks)
celery -A toppers beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

---

## 🚢 Deployment (PythonAnywhere)

1. Upload project, install requirements in virtualenv
2. Set `DJANGO_SETTINGS_MODULE=toppers.settings.production`
3. Add all env vars to PythonAnywhere's environment
4. Run `python manage.py collectstatic && python manage.py migrate`
5. Set WSGI file to point to `toppers/wsgi.py`

> **Note:** PythonAnywhere free tier doesn't support WebSockets. For live challenges,
> upgrade to a paid plan or deploy to Railway / Render / VPS instead.

---

## 🔐 Default Admin Credentials

```
URL:      http://localhost:8000/admin/
Username: admin
Password: Admin@1234
```
⚠️ **Change the password immediately** — especially in production.

---

## 📦 Tech Stack

| Layer         | Technology                                  |
|---------------|---------------------------------------------|
| Backend       | Django 4.2 + Django REST Framework          |
| Auth          | JWT (SimpleJWT) + Google OAuth (allauth)    |
| Database      | PostgreSQL                                  |
| Real-time     | Django Channels + Redis                     |
| Async Tasks   | Celery + Redis                              |
| Payments      | Paystack API                                |
| Airtime       | VTPass API                                  |
| Hosting       | PythonAnywhere / Railway / Render           |

---

Built with ❤️ for the Nigerian market. Let's make learning rewarding.
