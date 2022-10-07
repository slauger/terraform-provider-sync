#!/usr/bin/env python3

import requests
import json
import sys
import os
import re
import argparse
from subprocess import check_output
from packaging import version as version_parser

parser = argparse.ArgumentParser(description='command line arguments.')

parser.add_argument(
  '--dryrun',
  action='store_true',
  help='if set the script will only run in dry-run and will not download files',
  required=False,
  default=False,
)

parser.add_argument(
  '--config',
  metavar='<file>',
  type=str,
  help='configuration file (defaults to "providers.json")',
  default='providers.json',
  required=False,
)

args = parser.parse_args()

# load config file
with open(args.config, 'r') as f:
  config = json.load(f)

version_api = 'https://registry.terraform.io/v1/providers/{}/versions'

# mirror dir
mirror_path = '{}/registry.terraform.io'.format(config['directory'])

if not os.path.isdir(mirror_path):
  os.mkdir(mirror_path)

for provider in config['providers']:
  provider_url = config['providers'][provider]['url']

  # get all versions from the terraform api
  provider_versions = requests.get(version_api.format(provider_url)).json()

  # required later for the index.json
  versions = {}

  # path to the directory which will contain all files
  vendor_path = '{}/registry.terraform.io/{}'.format(config['directory'], provider_url.split('/')[0])
  provider_path = '{}/registry.terraform.io/{}'.format(config['directory'], provider_url)

  # parent dir
  if not os.path.isdir(vendor_path):
    os.mkdir(vendor_path)

  # child dir
  if not os.path.isdir(provider_path):
    os.mkdir(provider_path)

  # loop for the provider versions
  for version in provider_versions['versions']:
    # exclude alpha, beta and rc releases
    if not re.match('^[0-9]+\.[0-9]+\.[0-9]+$', version['version']):
      continue

    # excluded versions from config
    if 'exclude' in config['providers'][provider]:
      if version['version'] in config['providers'][provider]['exclude']:
        continue

    # honor since setting in json file
    if 'since' in config['providers'][provider]:
      if version['version'] != config['providers'][provider]['since']:
        if version_parser.parse(version['version']) < version_parser.parse(config['providers'][provider]['since']):
          continue

    versions[version['version']] = {}

    version_archive = '{}_{}_linux_amd64.zip'.format(provider, version['version'])
    archive_path    = '{}/{}'.format(provider_path, version_archive)
    archive_url     = 'https://releases.hashicorp.com/{}/{}/{}_{}_linux_amd64.zip'.format(provider, version['version'], provider, version['version'])

    if not os.path.isfile(archive_path):
      print("download {} to {}".format(archive_url, archive_path))

      # from subprocess import check_output
      if not args.dryrun:
        download = check_output([
          'curl', '-fsLo', archive_path, archive_url
        ])
    else:
      print('{} already present'.format(archive_path))
    
    content = {
      'archives': {
        'linux_amd64': {
          'url': '{}_{}_linux_amd64.zip'.format(provider, version['version']),
        }
      }
    }

    with open('{}/{}.json'.format(provider_path, version['version']), 'w') as f:
      f.write(json.dumps(content))

  # write index.json
  with open('{}/index.json'.format(provider_path), 'w') as f:
    f.write(json.dumps({'versions': versions}))

