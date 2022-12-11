import json
import os
from os import environ, path

import psycopg2
import yaml
from npqa_http import HttpClient
from invoke import task
from tenacity import retry, stop_after_delay, wait_fixed

CONNECTION_TIMEOUT = 100  # seconds

ROOT_PATH = path.dirname(path.abspath(__file__))

@task(aliases=['up [--local] [--ci] [--perf] [--m1]'],
      help={
          'local': 'This flag for switch to local server mode when running the catalog service in a local environment.',
          'ci': 'Adds some overrides for running in CI',
          'perf': 'Run wiremock for perf',
          'm1': 'Run images for Apple M1 chips'
      })
def up(context, local=False, ci=False, perf=False, m1=False):
    cats_image = None
    (compose_files, compose_services) = get_compose_files_services(m1=m1, perf=perf)

    if not local:
        if ci:
            cats_tag = environ.get('NEXT_VERSION_RAW')
            cats_image = 'artifactory.wgdp.io/wtp-docker/cats/app:{}'.format(cats_tag)
        else:
            branch_result = context.run('git branch --show-current')
            if branch_result.exited == 0:
                branch = branch_result.stdout.strip()
                commit_result = context.run('git rev-parse --short {}'.format(branch))
                if commit_result.exited == 0:
                    commit = commit_result.stdout.strip()
                    cats_image = 'freya/cats:{}_{}'.format(branch, commit)

        print('cats_image {}'.format(cats_image))

    zip_catalogs(context)
    context.run(f'docker-compose {compose_files} up -d {compose_services}')

    print('waiting for postgres')
    wait_for_postgres(ci)

    print('Waiting for clickhouse...')
    wait_for_clickhouse('http://localhost:8123')
    context.run(f'docker-compose {compose_files} up -d snitch')

    if not local:
        with open("qa-config.yaml", 'r') as stream:
            config = json.dumps(yaml.safe_load(stream))
            if ci:
                context.run("CATS_IMAGE={} CATS_CONFIG='{}' docker-compose up -d cats".format(cats_image, config))
            else:
                print("CATS_IMAGE={} CATS_CONFIG='{}' docker-compose {} up -d cats")
                context.run("CATS_IMAGE={} CATS_CONFIG='{}' docker-compose {} up cats".format(cats_image, config, compose_files))

@task
def down(context):
    context.run('docker-compose down')


def spinning_cursor():
    while True:
        for cursor in '|/-\\': yield cursor

def zip_catalogs(context):
    host_path = path.join(ROOT_PATH, 'wiremock', '__files', 'catalogs')
    print('Zip catalogs in the folder: {}'.format(host_path))

    dirs = []

    for entry in os.scandir(host_path):
        if entry.is_dir():
            print('Folder: {}'.format(entry.path[len(host_path):]))
            dirs.append(host_path + entry.path[len(host_path):])
    commands = []
    for dir in dirs:
        commands.append("rm -rf {0}.zip".format(dir))
        commands.append("cd {0}".format(dir))
        commands.append("zip -r {0}.zip *".format(dir))

    try:
        print('Executing command: {}...'.format(commands), flush=True)
        context.run(' && '.join(commands))
        return True
    except Exception as err:
        print('Couldn\'t zip folders : {}'.format(err))
        return False

spinner = spinning_cursor()


def get_compose_files_services(m1, perf):
    compose_services = 'rabbitmq zookeeper clickhouse'
    if perf:
        compose_services = f'{compose_services} wiremock_perf'
        'rabbitmq wiremock_perf zookeeper clickhouse'
    else:
        compose_services = f'postgres {compose_services} wiremock'
    compose_files = '-f docker-compose.yaml'
    if m1:
        compose_files = f'{compose_files} -f docker-compose-m1.yaml'
    else:
        compose_files = f'{compose_files} -f docker-compose.yaml'
    return compose_files, compose_services


@retry(wait=wait_fixed(1), stop=stop_after_delay(CONNECTION_TIMEOUT))
def wait_for_clickhouse(base_url):
    print('.', end='', flush=True)
    HttpClient(base_url).get(path='/', params=[('query', 'SELECT 1')])

@retry(stop=stop_after_delay(CONNECTION_TIMEOUT))
def wait_for_postgres(ci):
    if ci:
        connection = psycopg2.connect(host="127.0.0.1",
                                      port="5432",
                                      dbname="cats",
                                      user="cats",
                                      password="cats")
        connection.close()
    else:
        print('\r', end='')
        print('Connecting to the Postgres DB ... {}'.format(next(spinner)), end='', flush=True)
        connection = psycopg2.connect(host="127.0.0.1",
                                      port="5432",
                                      dbname="cats",
                                      user="cats",
                                      password="cats")
        print('\r', end='')
        print('Connecting to the Postgres DB ... done', end='\n', flush=True)
        connection.close()


