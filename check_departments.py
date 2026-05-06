from app import app
from app.models import Department

with app.app_context():
    print('所有部门:')
    for dept in Department.query.all():
        print(f'  - ID: {dept.id}, Name: {dept.name}, Level: {dept.level}, Code: {dept.code}, Parent: {dept.parent_id}')