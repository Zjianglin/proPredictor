#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Estimator, Dataset, Topic
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.environ.get('FLASK_CONFIG', 'default'))
manager = Manager(app)
migrate = Migrate(app, db)

def make_context_shell():
    return dict(app=app, db=db, User=User, Topic=Topic,
                Estimator=Estimator, Dataset=Dataset)

manager.add_command('shell', Shell(make_context=make_context_shell))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    manager.run()
