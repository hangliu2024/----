from app import app, db
from sqlalchemy import text

with app.app_context():
    conn = db.engine.connect()
    result = conn.execute(text("SELECT COUNT(DISTINCT emp_id) FROM employees_info WHERE emp_id IS NOT NULL AND emp_id != '' AND emp_id != 'emp_id'"))
    emp_count = result.fetchone()[0]
    print(f"employees_info表员工数: {emp_count}")
    
    result = conn.execute(text("SELECT COUNT(*) FROM person_system_permission_matrix"))
    perm_count = result.fetchone()[0]
    print(f"权限矩阵表记录数: {perm_count}")
    conn.close()