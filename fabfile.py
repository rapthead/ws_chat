# -*- coding: utf-8 -*-
from contextlib import contextmanager
from fabric.api import run, env, cd, task, prefix, local

env.hosts = ['nnm@cubie']
env.proj_path = '/home/nnm/projects/ws_chat/'
env.venv_path = '/home/nnm/.virtualenvs/ws_chat/'


@contextmanager
def virtualenv():
    """
    Runs commands within the project's virtualenv.
    """
    with cd(env.venv_path):
        with prefix("source %s/bin/activate" % env.venv_path):
            yield


@contextmanager
def project():
    """
    Runs commands within the project's directory.
    """
    with virtualenv():
        with cd(env.proj_path):
            yield


@task
def deploy():
    local('git push cubie master:local_master')
    with project():
        run('git merge local_master')
        # run('./manage.py migrate musicdb')
        run('./manage.py collectstatic --noinput')
        # run('pip install -r requirements.txt')
    run('supervisorctl restart ws_chat:*')
