#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import click

from .admin import admin


@admin.group(help="""Add, import, export users.""")
def users():
    pass


@users.command(help='Import users to keycloak from a JSON file.', name='import')
@click.argument('PATH_TO_USERS_FILE', type=str, nargs=1)
def import_command(path_to_users_file):
    import datetime
    import json

    from nomad import datamodel, infrastructure, utils

    with open(path_to_users_file) as f:
        users = json.load(f)

    logger = utils.get_logger(__name__)

    for user_dict in users:
        try:
            password = user_dict.pop('password')
            user_dict['created'] = datetime.datetime.fromtimestamp(
                user_dict['created'] / 1000
            )
            user = datamodel.User(**user_dict)
            infrastructure.user_management.add_user(
                user, bcrypt_password=password, invite=False
            )
            print(f'Imported {user.name}')
        except Exception as e:
            logger.error('could not import user', exc_info=e)
