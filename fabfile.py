# -*- coding: utf-8 -*-

import posixpath
import re

from fabric.api import (task, env, run, local, roles, cd, execute, hide, puts,
    sudo, )
from fabric.contrib.console import confirm


env.project_name = 'il2ec'
env.repository = 'git@github.com:IL2HorusTeam/il2ds-events-commander.git'
env.local_branch = 'master'
env.remote_ref = 'origin/master'
env.requirements_file = 'requirements.pip'
env.restart_command = 'supervisorctl restart {project_name}'.format(**env)
env.restart_sudo = True
env.logs = {
    "uwsgi": "/var/log/supervisor/uwsgi/uwsgi.err",
    "nginx": "/var/log/nginx/error.log",
    "app": "",
}


#------------------------------------------------------------------------------
# Tasks which set up deployment environments
#------------------------------------------------------------------------------

# @task
# def staging():
#     """
#     Use the staging deployment environment.
#     """
#     server = 'il2ec-staging'
#     env.roledefs = {
#         'commander': [server],
#         'db': [server],
#         'web': [server],
#     }
#     env.system_users = {server: 'www-data'}
#     env.virtualenv_dir = '/srv/www/{project_name}'.format(**env)
#     env.project_dir = '{virtualenv_dir}/src/{project_name}'.format(**env)
#     env.project_conf = '{project_name}.settings.local'.format(**env)


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
    env.project_conf = '{project_name}.settings.local'.format(**env)
    env.key_filename = '~/.vagrant.d/insecure_private_key'


# Set the default environment.
vagrant()


#------------------------------------------------------------------------------
# Publishing tasks
#------------------------------------------------------------------------------

@task
@roles('web', 'db')
def push():
    """
    Push branch to the repository.
    """
    remote, dest_branch = env.remote_ref.split('/', 1)
    local('git push {remote} {local_branch}:{dest_branch}'.format(
        remote=remote, dest_branch=dest_branch, **env))


@task
def deploy(verbosity='normal'):
    """
    Full server deploy.

    Updates the repository (server-side), synchronizes the database, collects
    static files and then restarts the web service.
    """
    if verbosity == 'noisy':
        hide_args = []
    else:
        hide_args = ['running', 'stdout']
    with hide(*hide_args):
        puts('Updating repository...')
        execute(update)
        puts('Collecting static files...')
        execute(collectstatic)
        puts('Synchronizing database...')
        execute(syncdb)
        puts('Restarting web server...')
        execute(restart)


@task
@roles('web', 'db')
def update(action='check'):
    """
    Update the repository (server-side).

    By default, if the requirements file changed in the repository then the
    requirements will be updated. Use ``action='force'`` to force
    updating requirements. Anything else other than ``'check'`` will avoid
    updating requirements at all.
    """
    with cd(env.project_dir):
        remote, dest_branch = env.remote_ref.split('/', 1)
        run('git fetch {remote}'.format(remote=remote,
            dest_branch=dest_branch, **env))
        with hide('running', 'stdout'):
            changed_files = run('git diff-index --cached --name-only '
                '{remote_ref}'.format(**env)).splitlines()
        if not changed_files and action != 'force':
            # No changes, we can exit now.
            return
        if action == 'check':
            reqs_changed = env.requirements_file in changed_files
        else:
            reqs_changed = False
        run('git merge {remote_ref}'.format(**env))
        run('find -name "*.pyc" -delete')
        run('git clean -df')
        fix_permissions()
    if action == 'force' or reqs_changed:
        # Not using execute() because we don't want to run multiple times for
        # each role (since this task gets run per role).
        requirements()


#------------------------------------------------------------------------------
# Actual tasks
#------------------------------------------------------------------------------

@task
@roles('web', 'db')
def incarnate():
    execute(syncdb)
    execute(dj, "create_superuser")
    execute(restart)


@task
@roles('web', 'db')
def reincarnate(force=False):
    """
    IRREVESIBLY DESTROYS ALL DATA. Recreates existing environment, resets
    database, deletes uploaded content and clears compiled static.
    """
    if not (force or confirm("WARNING. This command will destroy all data. "
                             "Continue?")):
        return
    run("rm -rf {virtualenv_dir}/var/static/*".format(**env))
    run("rm -rf {virtualenv_dir}/var/uploads/*".format(**env))
    execute(reset_db, "noinput")
    execute(incarnate)


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
    execute(reload)


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
@roles('web', 'db')
def requirements():
    """
    Update the requirements.
    """
    run('{virtualenv_dir}/bin/pip install -r {project_dir}/requirements.pip'\
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
def log(service=None):
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
        sudo("tail -f {virtualenv_dir}/var/log/{project_name}.log"\
             .format(**env))


#------------------------------------------------------------------------------
# Helper functions
#------------------------------------------------------------------------------

def dj(command):
    """
    Run a Django manage.py command on the server.
    """
    with cd(env.project_dir):
        run('{virtualenv_dir}/bin/python manage.py {dj_command} '
            '--settings {project_conf}'.format(dj_command=command, **env))


def restart_uwsgi():
    """
    Restarts the uWSGI application server.
    """
    sudo("touch /tmp/uwsgi-touch-reload-{project_name}".format(**env))


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
