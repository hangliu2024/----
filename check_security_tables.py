"""检查安全模块表结构"""
import sys
sys.path.insert(0, '.')
from app import app, db

with app.app_context():
    tables = ['classified_personnel','classified_media','security_zone','electronic_document','paper_document']
    for t in tables:
        result = db.session.execute(db.text(f'DESCRIBE {t}'))
        print(f'\n=== {t} ===')
        for r in result:
            print(f'  {r[0]:30s} {r[1]}')