"""检查当前迁移版本"""
import sys
from pathlib import Path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    result = db.session.execute(text('SELECT version_num FROM alembic_version'))
    version = [r[0] for r in result]
    print(f"当前迁移版本: {version}")
