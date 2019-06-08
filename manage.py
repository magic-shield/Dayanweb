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

if __name__ == '__main__':
    print(app.url_map)
    manager.run()
