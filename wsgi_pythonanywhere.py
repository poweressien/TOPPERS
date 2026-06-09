# ═══════════════════════════════════════════════════════════════
#  PASTE THIS INTO YOUR PYTHONANYWHERE WSGI FILE
#  Web tab → click the WSGI configuration file link → select all → paste
#
#  IMPORTANT: Replace 'yourusername' with your actual PA username
#             Replace 'toppers' with your actual project folder name
# ═══════════════════════════════════════════════════════════════

import os
import sys

# ── Add project to Python path ────────────────────────────────
path = '/home/yourusername/toppers'   # ← CHANGE THIS
if path not in sys.path:
    sys.path.insert(0, path)

# ── Point to production settings ─────────────────────────────
os.environ['DJANGO_SETTINGS_MODULE'] = 'toppers.settings.production'

# ── Load the app ─────────────────────────────────────────────
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
