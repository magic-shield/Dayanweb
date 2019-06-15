from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db
from info.models import *

app = create_app("develop")

# Integrated flask-script
manager = Manager(app)

# Integrated flask-migrate
Migrate(app, db)
manager.add_command("db", MigrateCommand)


@manager.option("-n", "--username", dest="username")
@manager.option("-p", "--password", dest="password")
def createsuperuser(username, password):
    if not all([username, password]):
        print("参数不完整")

    user = User()
    user.nick_name = username
    user.mobile = username
    user.password = password
    user.is_admin = 1

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
    print("成功添加管理员")


if __name__ == '__main__':
    manager.run()
