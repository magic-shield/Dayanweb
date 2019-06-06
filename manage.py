from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import app, db

# Integrated flask-script
manager = Manager(app)

# Integrated flask-migrate
Migrate(app, db)
manager.add_command("db", MigrateCommand)


@app.route('/')
def index():
    return "hello"


if __name__ == '__main__':
    app.run()
