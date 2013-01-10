#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import sys, os
sys.path.pop(0)
sys.path.insert(0, os.getcwd())

from exi.app import app
from flask.ext.script import Manager, Server

from exi.scripts import CleanPyc, PopulateDB, ResetDB, UserAddRole, UserRemoveRole, CreateRole, CreateUser
# from exi.scripts import ClearActivationKeys, ResetDB, PopulateDB

from flask_pymongo_security.script import CreateUserCommand , AddRoleCommand, RemoveRoleCommand, ActivateUserCommand, DeactivateUserCommand

manager = Manager(app)
manager.add_command("runserver", Server())
manager.add_command("clean_pyc", CleanPyc())
manager.add_command("populate_db", PopulateDB())
manager.add_command("reset_db", ResetDB())
manager.add_command('add_user_role', UserAddRole())
manager.add_command('remove_user_role', UserRemoveRole())
manager.add_command('create_role', CreateRole())
manager.add_command('create_user', CreateUser())
manager.add_command('secure_create_user', CreateUserCommand())
manager.add_command('activate_user', ActivateUserCommand())
manager.add_command('deactivate_user', DeactivateUserCommand())

# manager.add_command("clear_old_keys", ClearActivationKeys())

# manager.add_command('deactivate_user', DeactivateUserCommand())

if __name__ == "__main__":
    manager.run()