# -*- coding: utf-8 -*-

import posixpath
import re
import os

from fabric.api import (task, env, run, local, roles, cd, execute, hide, puts,
    settings, sudo, )
from fabric.contrib.console import confirm

#------------------------------------------------------------------------------
# Common settings
#------------------------------------------------------------------------------

env.project_name = 'il2ec'
env.requirements_file = 'requirements.pip'
env.languages = ('en', 'ru', )
env.logs = {
    'uwsgi' : "/var/log/supervisor/uwsgi/uwsgi.err",
    'nginx' : "/var/log/nginx/error.log",
    'celeryd': "/var/log/celery/w1.log",

    # Platform-dependent, must be redefined
    'web': None,
    'commander': None,
}

#------------------------------------------------------------------------------
# Tasks which set up deployment platforms
#------------------------------------------------------------------------------

@task
def staging():
    """
    Use the staging deployment environment.
    """
    server = 'il2events.servegame.com'
    env.roledefs = {
        'commander': [server],
        'db': [server],
        'web': [server],
    }
    env.user = 'il2ec-dev'
    env.system_users = {server: env.user}
    env.virtualenv_dir = \
        '/home/{user}/.virtualenvs/{project_name}'.format(**env)
    env.project_dir = '/home/{user}/projects/{project_name}'.format(**env)
    env.project_conf = '{project_name}.settings.staging'.format(**env)
    env.key_filename = 'ssh/staging_key'
    calculate_paths()


@task
def vagrant():
    """
    Use the local development environment under Vagrant.
    """
    server = 'localhost:2210' # See SSH port in Vagrantfile
    env.roledefs = {
        'commander': [server],
        'db': [server],
        'web': [server],
    }
    env.user = 'vagrant'
    env.system_users = {server: env.user}
    env.virtualenv_dir = '/var/virtualenvs/{project_name}'.format(**env)
    env.project_dir = '{virtualenv_dir}/src/{project_name}'.format(**env)
    env.project_conf = '{project_name}.settings.vagrant'.format(**env)
    env.key_filename = '~/.vagrant.d/insecure_private_key'
    calculate_paths()


def calculate_paths():
    env.project_root = os.path.join(env.project_dir, env.project_name)
    env.apps_root = os.path.join(env.project_root, 'apps')

    log_base = '{virtualenv_dir}/var/log/{project_name}'.format(**env)
    env.logs.update({
        'web': '{0}-web.log'.format(log_base),
        'commander': '{0}-daemon.log'.format(log_base),
    })

#------------------------------------------------------------------------------
# Publishing tasks
#------------------------------------------------------------------------------

@task
@roles('web', 'db')
def update(action='check'):
    """
    Update reload project on remote machine.

    Set environment before running this command. Emample:
        fab staging update
    """
    pull_project()
    execute(messages_compile)
    execute(reload_all)


@task
@roles('web', 'db')
def build(force=False):
    """
    IRREVESIBLY DESTROYS ALL DATA ON REMOTE MACHINE.

    Update and recreate project on remote machine.

    Set environment before running this command. Emample:
        fab staging build
    """
    if not (force or confirm("WARNING. This command will destroy all data on "
                             "remote machine. Continue?")):
        return
    pull_project()
    execute(reincarnate, force=True)


#------------------------------------------------------------------------------
# Actual tasks
#------------------------------------------------------------------------------

@task
@roles('web', 'db')
def incarnate():
    puts('Initializing database...')
    execute(syncdb)
    puts('Compiling translations...')
    execute(messages_compile)
    puts('Creating default superuser...')
    execute(dj, "create_superuser")
    puts('Creating test users...')
    execute(dj, "create_test_users")
    puts('Restarting services...')
    execute(restart)


@task
@roles('web', 'db')
def reincarnate(force=False):
    """
    IRREVESIBLY DESTROYS ALL DATA.

    Recreates existing environment, resets database, deletes uploaded content
    and clears compiled static.
    """
    if not (force or confirm("WARNING. This command will destroy all data. "
                             "Continue?")):
        return
    puts('Cleaning static and uploads...')
    run("rm -rf {virtualenv_dir}/var/static/*".format(**env))
    run("rm -rf {virtualenv_dir}/var/uploads/*".format(**env))

    puts('Stopping Celery...')
    celeryd('stop')
    execute(purge_celery, force=True)

    puts('Destroying database...')
    execute(reset_db, "noinput")
    execute(incarnate)

    puts('Starting Celery...')
    celeryd('start')


@task
@roles('db')
def syncdb(sync=True, migrate=True):
    """
    Creates the database tables for all apps in INSTALLED_APPS whose tables
    have not already been created.
    """
    dj('syncdb --migrate --noinput')


@task
@roles('db')
def flush_db(noinput=False, no_initial_data=False):
    """
    Returns the database to the state it was in immediately after syncdb was
    executed.
    """
    ensure_noinput = "--noinput" if noinput else ""
    ensure_no_initial_data = "--no-initial-data" if no_initial_data else ""
    dj("flush {0} {1}".format(ensure_noinput, ensure_no_initial_data))


@task
@roles('db')
def reset_db(noinput=None):
    """
    Destroys database completely.
    """
    ensure_noinput = "--noinput" if noinput else ""
    dj("reset_db --router=default {0}".format(ensure_noinput))


@task
@roles('web', 'db', 'commander')
def purge_celery(force=False):
    """
    Deletes all background tasks from the Celery task queue.
    """
    ensure_force = "-f" if force else ""
    execute(dj, "celery purge {force}".format(force=ensure_force))


@task
@roles('db')
def dbshell():
    """
    Runs the command-line client for the database engine specified in ENGINE
    setting.
    """
    dj("dbshell")


@task
@roles('web')
def collectstatic():
    """
    Collect static files from apps and other locations in a single location.
    """
    dj("collectstatic -c --noinput --verbosity 0")


@task
@roles('web')
def restart():
    """
    Clear sessions, cache, static, reload code and restart server.
    """
    execute(dj, "clear_redis")
    run("rm -rf {virtualenv_dir}/var/static/CACHE/*".format(**env))
    execute(collectstatic)
    execute(restart_uwsgi)


@task
@roles('web')
def reload():
    """
    Reloads all project code, static and restarts application server.
    """
    run("find {virtualenv_dir}/src/{project_name}/ -name '*.pyc' -exec "
        "rm -rf {{}} \\;".format(**env))
    execute(collectstatic)
    execute(restart_uwsgi)


@task
@roles('web')
def reload_all():
    """
    Reloads all project code, static, restarts application server and celery.
    """
    execute(reload)
    celeryd('restart')


@task
@roles('web', 'db')
def requirements():
    """
    Update the requirements.
    """
    run('{virtualenv_dir}/bin/pip install -r {project_dir}/requirements.pip'
        .format(**env))
    with cd('{virtualenv_dir}/src'.format(**env)):
        with hide('running', 'stdout', 'stderr'):
            dirs = []
            for path in run('ls -db1 -- */').splitlines():
                full_path = posixpath.normpath(posixpath.join(env.cwd, path))
                if full_path != env.project_dir:
                    dirs.append(path)
        if dirs:
            fix_permissions(' '.join(dirs))
    with cd(env.virtualenv_dir):
        with hide('running', 'stdout'):
            match = re.search(r'\d+\.\d+', run('bin/python --version'))
        if match:
            with cd('lib/python{0}/site-packages'.format(match.group())):
                fix_permissions()


@task
@roles('web', 'db', 'commander')
def log(service='web'):
    """
    Output log to condole.

    Optional parameters:
      service - log name to show

    Example:
      fab log:uwsgi
    """
    if service in env.logs.keys():
        sudo("tail -f {0}".format(env.logs[service]))
    else:
        print("Unknown service '{0}'!".format(service))


@task
@roles('commander')
def commander(action):
    """
    Run or stop the IL-2 DS commander.

    Arguments:

    `action` - 'run' or 'stop'.

    Example:
      fab commander:run
    """
    dj("{0}_commander".format(action))


@task
@roles('web')
def lint():
    """
    Lint Python modules.
    """
    with cd(env.project_dir):
        with settings(hide('running', 'status'), warn_only=True):
            run("{virtualenv_dir}/bin/pylint --rcfile=.pylintrc "
                "{project_name}/; echo".format(**env))


@task
@roles('web', 'db', 'commander')
def messages_make(app=None):
    """
    Create or update translations for an application or project base.
    """
    puts("Making translation files for {0}".format(app or "project base"))

    if app:
        chdir = os.path.join(env.apps_root, app)
        ignore = ''
    else:
        chdir = env.project_root
        ignore = '--ignore=apps/*'

    for language in env.languages:
        command = "makemessages -l {language} {ignore}".format(
                   language=language, ignore=ignore)
        dj(command, chdir=chdir)


@task
@roles('web', 'db', 'commander')
def messages_make_all():
    """
    Create or update translations for the whole project.
    """
    execute(messages_make)
    for app in get_applications():
        execute(messages_make, app=app)


@task
@roles('web', 'db', 'commander')
def messages_compile():
    """
    Compile translations for the whole project.
    """
    dirs = [env.project_root, ]
    dirs.extend([
        os.path.join(env.apps_root, app) for app in get_applications()
    ])
    for chdir in dirs:
        dj("compilemessages", chdir=chdir)

#------------------------------------------------------------------------------
# Helper functions
#------------------------------------------------------------------------------

def dj(command, chdir=None):
    """
    Run a Django manage.py command on the server.
    """
    with cd(chdir or env.project_dir):
        run("{virtualenv_dir}/bin/python {project_dir}/manage.py {dj_command} "
            "--settings={project_conf}".format(dj_command=command, **env))


def pull_project():
    """
    Update project to last version and update requirements.
    """
    with cd(env.project_dir):
        run('git reset --hard')
        run('git pull')
    execute(requirements)


def restart_uwsgi():
    """
    Restarts the uWSGI application server.
    """
    sudo("touch /tmp/uwsgi-touch-reload-{project_name}".format(**env))


def celeryd(action):
    """
    Applies given action to Celery deamon.
    """
    sudo("/etc/init.d/celeryd {0}".format(action))


def fix_permissions(path='.'):
    """
    Fix the file permissions.
    """
    if ' ' in path:
        full_path = '{path} (in {cwd})'.format(path=path, cwd=env.cwd)
    else:
        full_path = posixpath.normpath(posixpath.join(env.cwd, path))
    puts('Fixing {0} permissions'.format(full_path))
    with hide('running'):
        system_user = env.system_users.get(env.host)
        if system_user:
            run('chmod -R g=rX,o= -- {0}'.format(path))
            run('chgrp -R {0} -- {1}'.format(system_user, path))
        else:
            run('chmod -R go= -- {0}'.format(path))

def get_applications():
    apps_path = "{project_name}/apps".format(**env)
    root, app_dirs, files = os.walk(apps_path).next()
    app_dirs.sort()
    return app_dirs

#------------------------------------------------------------------------------
# Set the default environment.
#------------------------------------------------------------------------------

vagrant()
