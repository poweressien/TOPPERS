#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  TOPPERS — PythonAnywhere Setup Script
#  Run this ONCE after cloning/uploading your project.
#
#  Usage:
#    cd ~/toppers          (or wherever your project is)
#    bash setup_pythonanywhere.sh
# ═══════════════════════════════════════════════════════════════

set -e  # Stop on first error

echo ""
echo "🏆 TOPPERS — PythonAnywhere Setup"
echo "═══════════════════════════════════"

# ── Step 1: Confirm we're in the right directory ──────────────
if [ ! -f "manage.py" ]; then
    echo "❌ manage.py not found. Run this script from inside your project folder."
    echo "   Try: cd ~/toppers && bash setup_pythonanywhere.sh"
    exit 1
fi
echo "✅ Project directory confirmed"

# ── Step 2: Check .env exists ─────────────────────────────────
if [ ! -f ".env" ]; then
    echo ""
    echo "❌ .env file not found!"
    echo "   Create it first:"
    echo "   cp .env.example .env && nano .env"
    echo ""
    echo "   Required values:"
    echo "   - SECRET_KEY"
    echo "   - DATABASE_URL (your MySQL URL)"
    echo "   - ALLOWED_HOSTS (your pythonanywhere domain)"
    exit 1
fi
echo "✅ .env file found"

# ── Step 3: Create virtual environment ────────────────────────
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3.11 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# ── Step 4: Activate venv ─────────────────────────────────────
source venv/bin/activate
echo "✅ Virtual environment activated"

# ── Step 5: Install requirements ──────────────────────────────
echo ""
echo "📥 Installing requirements (this may take 2–3 minutes)..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "✅ Requirements installed"

# ── Step 6: Set Django settings ───────────────────────────────
export DJANGO_SETTINGS_MODULE=toppers.settings.production
echo "✅ Using production settings"

# ── Step 7: Run migrations ────────────────────────────────────
echo ""
echo "🗃  Running migrations..."
python manage.py migrate --noinput
echo "✅ Migrations complete"

# ── Step 8: Create admin user ─────────────────────────────────
echo ""
echo "👤 Creating admin user..."
python manage.py create_admin
echo "✅ Admin user ready (username: admin, password: Admin@1234)"

# ── Step 9: Seed questions ────────────────────────────────────
echo ""
echo "🌱 Seeding categories and questions..."
python manage.py seed_data
echo "✅ Seed complete"

# ── Step 10: Collect static files ────────────────────────────
echo ""
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear
echo "✅ Static files collected to ./staticfiles/"

# ── Done ─────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════"
echo "✅ TOPPERS is ready for PythonAnywhere!"
echo "═══════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Go to PythonAnywhere → Web tab"
echo "  2. Create a web app (Manual config → Python 3.11)"
echo "  3. Set source code path: $(pwd)"
echo "  4. Set virtualenv path:  $(pwd)/venv"
echo "  5. Edit WSGI file — see DEPLOYMENT.md"
echo "  6. Set static files: URL=/static/ → Directory=$(pwd)/staticfiles"
echo "  7. Click Reload"
echo ""
echo "Admin: https://yourusername.pythonanywhere.com/admin/"
echo "Login: admin / Admin@1234  ← CHANGE THIS PASSWORD!"
echo ""
