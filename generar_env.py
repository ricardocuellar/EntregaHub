from pathlib import Path
import secrets

dest = Path(__file__).resolve().parent / '.env'
content = '\n'.join([
    'DJANGO_SECRET_KEY=' + secrets.token_urlsafe(48),
    'POSTGRES_DB=entregapro',
    'POSTGRES_USER=entregapro',
    'POSTGRES_PASSWORD=' + secrets.token_urlsafe(24),
    'DEMO_PASSWORD=' + secrets.token_urlsafe(18),
    '',
])
try:
    with dest.open('x') as f:
        f.write(content)
    dest.chmod(0o600)
    print('.env creado para desarrollo local. No mostrarlo ni añadirlo a Git.')
except FileExistsError:
    print('.env ya existe; se conserva sin cambios.')
