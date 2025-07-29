import sys
from getpass import getpass

from src.main import app, migrate_schema
from src.models.diary import db, Auth
from src.routes.auth import simple_hash

usage = "Usage: python reset_password.py [--entry NEW] [--admin NEW]"

entry = None
admin = None
for arg in sys.argv[1:]:
    if arg.startswith('--entry'):
        entry = arg.split('=', 1)[1] if '=' in arg else None
    elif arg.startswith('--admin'):
        admin = arg.split('=', 1)[1] if '=' in arg else None

if entry is None and admin is None:
    print(usage)
    sys.exit(1)

with app.app_context():
    migrate_schema()
    auth = Auth.query.first()
    if not auth:
        auth = Auth()
        db.session.add(auth)

    if entry is not None:
        if entry == '':
            entry = getpass('New entry password: ')
        auth.password_hash = simple_hash(entry)
    if admin is not None:
        if admin == '':
            admin = getpass('New admin password: ')
        auth.admin_password_hash = simple_hash(admin)

    db.session.commit()
    print('Passwords updated.')
