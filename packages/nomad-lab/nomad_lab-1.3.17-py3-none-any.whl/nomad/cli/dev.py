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

import json
import os
import sys
from typing import Any, cast

import click
from pint import Unit
from pint.errors import UndefinedUnitError

from nomad.config import config
from nomad.metainfo.elasticsearch_extension import schema_separator

from .cli import cli


@cli.group(help='Commands related to the nomad source code.')
def dev():
    pass


@dev.command(
    help='Runs tests and linting of the nomad python source code. Useful before committing code.'
)
@click.option('--skip-tests', help='Do no tests, just do code checks.', is_flag=True)
@click.option(
    '-x', '--exitfirst', help='Stop testing after first failed test case.', is_flag=True
)
def qa(skip_tests: bool, exitfirst: bool):
    os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    ret_code = 0

    if not skip_tests:
        click.echo('Run tests ...')
        ret_code += os.system(
            'python -m pytest -sv%s tests' % ('x' if exitfirst else '')
        )
    click.echo('Run code style and lint checks ...')
    ret_code += os.system('python -m ruff nomad tests')
    click.echo('Run code formatting checks ...')
    ret_code += os.system('python -m ruff format nomad tests')
    click.echo('Run static type checks ...')
    ret_code += os.system('python -m mypy nomad tests')

    sys.exit(ret_code)


@dev.command(
    help='Runs tests and linting of the nomad gui source code. Useful before committing code.'
)
@click.option('--skip-tests', help='Do no tests, just do code checks.', is_flag=True)
def gui_qa(skip_tests: bool):
    os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../gui')))
    ret_code = 0

    if not skip_tests:
        click.echo('Run gui testing ...')
        ret_code += os.system('yarn run test')
    click.echo('Run gui code linting ...')
    ret_code += os.system('yarn run lint')

    sys.exit(ret_code)


@dev.command(help='Export an API model in JSON schema.')
@click.argument('model')
def api_model(model):
    import importlib
    import json

    def remove_null_types(data):
        """
        Recursively removes dictionary entries with { "type": "null" } from the input dictionary.
        This is done so that the schemas are compatible with the ones we created using pydantic v1

        Args:
            data (dict or list): Input dictionary or list to process

        Returns:
            dict or list: Processed dictionary/list with null type entries removed
        """
        if isinstance(data, dict):
            processed_dict = {}
            for key, value in data.items():
                if isinstance(value, dict | list):
                    processed_value = remove_null_types(value)

                    # Only add the key if the processed value is not a "type": "null" dictionary
                    if not (
                        isinstance(processed_value, dict)
                        and processed_value.get('type') == 'null'
                    ):
                        processed_dict[key] = processed_value
                else:
                    processed_dict[key] = value
            return processed_dict

        elif isinstance(data, list):
            return [
                remove_null_types(item)
                for item in data
                if not (isinstance(item, dict) and item.get('type') == 'null')
            ]

        return data

    if model in [
        'nomad.app.v1.models.graph.GraphRequest',
        'nomad.app.v1.models.graph.GraphResponse',
    ]:
        from nomad.app.v1.models.graph.graph_models import Graph
        from nomad.app.v1.models.graph.utils import (
            generate_request_model,
            generate_response_model,
        )

        sys.modules['nomad.app.v1.models.graph.utils'].ref_prefix = '#/definitions'
        sys.modules['nomad.app.v1.models.graph.utils'].graph_model_export = True

        if model == 'nomad.app.v1.models.graph.GraphRequest':
            model = generate_request_model(Graph)
        else:
            model = generate_response_model(Graph)

        schema = remove_null_types(model.model_json_schema())
        print(json.dumps(schema, indent=2))
    else:
        pkg, cls = model.rsplit('.', 1)
        importlib.import_module(pkg)
        model = getattr(sys.modules[pkg], cls)
        schema = remove_null_types(model.model_json_schema())
        print(json.dumps(schema, indent=2))


def get_gui_artifacts_js() -> str:
    from nomad.datamodel import all_metainfo_packages
    from nomad.parsing.parsers import code_metadata

    all_metainfo_packages = all_metainfo_packages()
    unit_list_json, prefixes_json = _generate_units_json()
    code_metadata = json.loads(json.dumps(code_metadata, sort_keys=True))

    artifactsDict = {
        'searchQuantities': _generate_search_quantities(),
        'metainfo': _generate_metainfo(all_metainfo_packages),
        'parserMetadata': code_metadata,
        'northTools': {k: v.dict() for k, v in config.north.tools.filtered_items()},
        'unitList': unit_list_json,
        'unitPrefixes': prefixes_json,
    }

    return f'window.nomadArtifacts = {json.dumps(artifactsDict, indent=2)};\n'


@dev.command(help=('Generates all python-based GUI artifacts into javascript code.'))
def gui_artifacts():
    print(get_gui_artifacts_js())


def _generate_metainfo(all_metainfo_packages):
    return all_metainfo_packages.m_to_dict(
        with_meta=True, with_def_id=config.process.write_definition_id_to_archive
    )


@dev.command(help='Generates a JSON with all metainfo.')
def metainfo():
    from nomad.datamodel import all_metainfo_packages

    export = all_metainfo_packages()
    print(json.dumps(_generate_metainfo(export), indent=2))


def _generate_search_quantities():
    # Currently only quantities with "entry_type" are included.
    from nomad.datamodel import EntryArchive
    from nomad.metainfo.elasticsearch_extension import Elasticsearch, entry_type

    def to_dict(search_quantity, section=False, repeats=False):
        if section:
            keys = ['name', 'description', 'nested', 'repeats']
            metadict = search_quantity.sub_section.m_to_dict(with_meta=True)
            instanceMeta = search_quantity.m_to_dict(with_meta=True)
            metadict['name'] = instanceMeta['name']
            metadict['repeats'] = repeats or instanceMeta.get('repeats')
            es_annotations = search_quantity.m_get_annotations(
                Elasticsearch, as_list=True
            )
            nested = any(x.nested for x in es_annotations)
            metadict['nested'] = nested
        else:
            keys = [
                'name',
                'description',
                'type',
                'unit',
                'shape',
                'aliases',
                'aggregatable',
                'dynamic',
                'repeats',
            ]
            metadict = search_quantity.definition.m_to_dict(with_meta=True)
            # UI needs to know whether the quantity can be used in
            # aggregations or not.
            metadict['aggregatable'] = search_quantity.aggregatable
            metadict['dynamic'] = search_quantity.dynamic
            metadict['repeats'] = search_quantity.repeats
            if search_quantity.dynamic:
                splitted = search_quantity.qualified_name.split(schema_separator, 1)
                if len(splitted) == 2:
                    metadict['schema'] = splitted[1]
                    keys.append('schema')

        result = {}
        for key in keys:
            val = metadict.get(key)
            if val is not None:
                result[key] = val
        return result

    export = {}

    # Add quantities
    for search_quantity in entry_type.quantities.values():
        isSuggestion = search_quantity.annotation.suggestion
        if not isSuggestion:
            export[search_quantity.qualified_name] = to_dict(search_quantity)

    # Add suggestion flag
    for suggestion in entry_type.suggestions.keys():
        export[suggestion]['suggestion'] = True

    # Add section definitions
    def get_sections(m_def, prefix=None, repeats=False):
        for sub_section_def in m_def.all_sub_sections.values():
            name = sub_section_def.name
            full_name = f'{prefix}.{name}' if prefix else name
            info = to_dict(sub_section_def, True, repeats)
            repeats_child = info.get('repeats', repeats)
            export[full_name] = info
            get_sections(sub_section_def.sub_section, full_name, repeats_child)

    get_sections(EntryArchive.results.sub_section, 'results')

    return export


@dev.command(help='Generates a JSON with all search quantities.')
def search_quantities():
    from nomad.datamodel import all_metainfo_packages

    all_metainfo_packages()
    print(json.dumps(_generate_search_quantities(), indent=2))


@dev.command(
    help='Generates a JSON file that compiles all the parser metadata from each parser project.'
)
def parser_metadata():
    from nomad.parsing.parsers import code_metadata

    print(json.dumps(code_metadata, indent=2, sort_keys=True))


def get_gui_config() -> str:
    """Create a simplified and stripped version of the nomad.yaml contents that
    is used by the GUI.
    """
    from nomad.config import config

    config.load_plugins()

    # We need to sort the plugin entry point information, because otherwise the
    # artifacts tests will fail.
    def _sort_dict(d):
        if isinstance(d, dict):
            return {k: _sort_dict(v) for k, v in sorted(d.items())}
        if isinstance(d, list):
            return [_sort_dict(v) for v in d]
        return d

    # We save a single list of enabled entry points
    plugins = _sort_dict(config.plugins.dict(exclude_unset=True))
    entry_points = [
        entry_point.dict_safe()
        for entry_point in config.plugins.entry_points.filtered_values()
    ]
    plugins['entry_points'] = entry_points

    data = {
        'appBase': config.ui.app_base,
        'northBase': config.ui.north_base,
        'keycloakBase': config.keycloak.public_server_url,
        'keycloakRealm': config.keycloak.realm_name,
        'keycloakClientId': config.keycloak.client_id,
        'debug': False,
        'encyclopediaBase': config.services.encyclopedia_base
        if config.services.encyclopedia_base
        else None,
        'oasis': config.oasis.is_oasis,
        'version': config.meta.beta if config.meta.beta else {},
        'globalLoginRequired': config.oasis.allowed_users is not None,
        'servicesUploadLimit': config.services.upload_limit,
        'appTokenMaxExpiresIn': config.services.app_token_max_expires_in,
        'uploadMembersGroupSearchEnabled': config.services.upload_members_group_search_enabled,
        'ui': config.ui.dict(exclude_none=True) if config.ui else {},
        'plugins': plugins,
        'dataciteEnabled': config.datacite.enabled,
        'resourcesEnabled': config.resources.enabled,
        'termsOfServiceURL': config.oasis.terms_of_service_url,
        'footerLinks': [link.dict() for link in config.meta.footer_links],
        'description': config.meta.description,
    }

    return f'window.nomadEnv = {json.dumps(data, indent=2)}'


@dev.command(help='Generates the GUI development .env file based on NOMAD config.')
def gui_env():
    from nomad.config import config

    print(f'REACT_APP_BACKEND_URL={config.ui.app_base}')


@dev.command(help='Generates the GUI development config JS file based on NOMAD config.')
def gui_config():
    print(get_gui_config())


@dev.command(
    help=(
        'Updates parser`s README files by combining a general template with  '
        'a parser`s metadata YAML file.'
    )
)
@click.option(
    '--parser', help='Only updated the README of the given parsers subdirctory.'
)
def update_parser_readmes(parser):
    import re
    from glob import glob

    import yaml

    os.chdir(os.path.join(os.path.dirname(__file__), '../..'))

    # filenames
    local_fn = 'README.md'
    generic_fn = './README.parsers.md'
    parser_path = './dependencies/parsers/'

    # Open general template
    with open(generic_fn) as generic:  # read only
        generic_contents = generic.read()

    # Replace the comment at the top of the gereral template
    generic_contents = re.sub(
        rf'\*\*\*Note:\*\* This is a general README file for NOMAD parsers, '
        rf'consult the README of specific parser projects for more detailed '
        rf'information!\*\n\n',
        '',
        generic_contents,
    )

    def open_metadata(path):
        # read local yaml metadata file
        with open(path) as metadata_f:
            try:
                metadata = yaml.load(metadata_f, Loader=yaml.SafeLoader)
            except Exception as e:
                print(f'Error reading metadata.yaml: {e}')
                metadata = None
        return metadata

    def replace(metadata, contents, path):
        # replace placelder in contents with metadata values
        for key in metadata.keys():
            replace = metadata.get(key)
            if replace is None:
                continue
            print(f'\tReplacing {key} with {replace}')
            contents = re.sub(rf'\${key}\$', replace, contents)

        # save file
        with open(path, 'w') as f:
            f.write(contents.strip())
            f.write('\n')

    for local_readme in sorted(glob(f'{parser_path}/*/{local_fn}')):
        parser_dir = os.path.dirname(local_readme)
        project_name = os.path.basename(parser_dir)
        print(f'Working on {parser_dir}')

        contents = generic_contents
        # if metadata file under the parser directory exists, it is a single parser project
        single = os.path.isfile(os.path.join(parser_dir, 'metadata.yaml'))

        if single:
            metadata = open_metadata(os.path.join(parser_dir, 'metadata.yaml'))
            # git path is given by nomad-parser-codename
            metadata['gitPath'] = f'nomad-parser-{project_name}'
            parser_header, parser_specs = '', ''
        else:
            # replace header for the single parser with that for a group of parsers
            parser_header_re = r'(\nThis is a NOMAD parser[\s\S]+?Archive format\.\n)'
            parser_header = re.search(parser_header_re, contents).group(1)
            group_header = 'This is a collection of the NOMAD parsers for the following $codeName$ codes:\n\n$parserList$'
            contents = re.sub(parser_header_re, group_header, contents)
            # remove individual parser specs
            parser_specs_re = (
                r'(For \$codeLabel\$ please provide[\s\S]+?\$tableOfFiles\$)\n\n'
            )
            parser_specs = re.search(parser_specs_re, contents).group(1)
            contents = re.sub(parser_specs_re, '', contents)
            metadata = dict(
                gitPath=f'{project_name}-parsers',
                parserGitUrl=f'https://github.com/nomad-coe/{project_name}-parsers.git',
                parserSpecific='',
            )
        if metadata.get('codeName', '').strip() == '':
            metadata['codeName'] = project_name
        if 'preamble' not in metadata:
            metadata['preamble'] = ''

        # if this is a group of parser, find all individdual parsers and write the
        # parser specs
        parser_list = ''
        for index, local_metadata in enumerate(
            sorted(glob(f'{parser_dir}/*/*/metadata.yaml'))
        ):
            metadata_parser = open_metadata(local_metadata)
            # contents is simply the parser header and specs
            contents_parser = f'{parser_header}\n{parser_specs}'
            replace(
                metadata_parser,
                contents_parser,
                os.path.join(os.path.dirname(local_metadata), local_fn),
            )
            # add the codename to the list of parsers for the group header
            codelabel = metadata_parser.get(
                'codeLabel', os.path.basename(os.path.dirname(local_metadata))
            )
            codeurl = metadata_parser.get('codeUrl', '')
            parser_list = rf'{parser_list}{index + 1}. [{codelabel}]({codeurl})\n'
        metadata['parserList'] = parser_list.strip()

        # Find & Replace Parser`s metadata on its README file
        replace(metadata, contents, local_readme)


@dev.command(help='Adds a few pieces of data to NOMAD.')
@click.option('--username', '-u', type=str, help='The main author username.')
def example_data(username: str):
    from nomad import infrastructure, utils
    from nomad.utils.exampledata import ExampleData

    infrastructure.setup()

    main_author = infrastructure.user_management.get_user(username=username)
    if main_author is None:
        print(f'The user {username} does not exist.')
        sys.exit(1)

    data = ExampleData(main_author=main_author)

    # one upload with two entries published with embargo, one shared
    upload_id = utils.create_uuid()
    data.create_upload(upload_id=upload_id, published=True, embargo_length=0)
    data.create_entry(
        entry_id=utils.create_uuid(),
        upload_id=upload_id,
        mainfile='test_content/test_embargo_entry/mainfile.json',
    )

    data.save(with_files=True, with_es=True, with_mongo=True)

    return data


def _generate_units_json() -> tuple[Any, Any]:
    from collections import defaultdict

    from pint.facets.plain import ScaleConverter

    from nomad.units import ureg

    # TODO: Check that all units are unambiguously defined, and that there are
    # no clashes. Pint will issue a warning if something is wrong with the
    # definitions.

    # Get all prefixes that are registered in Pint
    prefixes = {}
    for name, prefix in ureg._prefixes.items():
        if isinstance(prefix.converter, int):
            scale = cast(float, prefix.converter)
        elif isinstance(prefix.converter, ScaleConverter):
            scale = prefix.converter.scale
        else:
            raise Exception('Unknown prefix type.')
        prefixes[name] = {'name': name, 'value': scale, 'scientific': True}

    # Get all aliases
    aliases: dict = defaultdict(list)
    for unit in ureg._units:
        unit_name = str(unit)
        unit_long_name = ureg.get_name(unit_name)
        if unit_long_name != unit_name:
            aliases[unit_long_name].append(unit_name)

    # For each defined dimension, get the available units if there are any.
    def get_unit_data(unit_name, dimension):
        unit_long_name = ureg.get_name(unit_name)
        unit_abbreviation = ureg.get_symbol(unit_name)
        unit_label = unit_long_name.replace('_', ' ')
        unit_label = unit_label[0].upper() + unit_label[1:]

        return {
            'name': unit_long_name,
            'dimension': dimension[1:-1],
            'label': unit_label,
            'abbreviation': unit_abbreviation,
            'aliases': aliases[unit_long_name],
        }

    # For some reason, the method ureg.get_compatible_units is not returning all
    # options (https://github.com/hgrecco/pint/issues/610). This is a workaround
    # for this problem.
    dimension_def_name_map = {
        str(ureg.get_dimensionality(key)): key for key in ureg._dimensions
    }

    # Define a function to check for an SI prefix
    si_prefixes = [
        value['name'] for value in prefixes.values() if len(str(value['name'])) > 2
    ]

    def is_prefix_only(unit_base_name):
        unit = ureg.parse_units(unit_base_name)
        if len(aliases[unit_base_name]) != 0:
            return False

        # Separate the prefix and base unit
        for prefix in si_prefixes:
            if str(unit).startswith(prefix):
                # Check if the remaining part is a valid base unit
                base_unit_str = str(unit)[len(prefix) :]
                try:
                    ureg.parse_units(base_unit_str)
                    return True
                except UndefinedUnitError:
                    pass

        return False

    unit_list = []
    for unit_str in ureg._units:
        # Filter out aliases
        unit_base_name = ureg.get_name(unit_str)
        if unit_base_name != unit_str:
            continue
        # Filter out units with prefixes that do not have an alias of their own
        # (Pint defines some of the most common unit prefixes as separate units)
        if is_prefix_only(unit_str):
            continue
        # Filter out delta units
        if unit_base_name.startswith('delta_'):
            continue
        try:
            unit = getattr(ureg, unit_str)
        except UndefinedUnitError:
            continue
        if not isinstance(unit, Unit):
            continue
        if hasattr(unit, 'dimensionality'):
            dimension_name = dimension_def_name_map.get(str(unit.dimensionality))  # type: ignore[attr-defined]
            if dimension_name:
                unit_list.append(get_unit_data(unit_str, dimension_name))

    # Add kilogram as SI base unit
    unit_list.append(
        {
            'name': 'kilogram',
            'dimension': 'mass',
            'label': 'Kilogram',
            'abbreviation': 'kg',
        }
    )

    # Add the unit definition and offset that come from the Pint setup.
    dimensionless_units = []
    units = []
    for value in unit_list:
        i_unit = value['name']
        j_unit = str(ureg.Quantity(1, getattr(ureg, i_unit)).to_base_units().units)
        if i_unit != j_unit:
            # Solve the multiplication factor using 'delta'-units if an
            # offset is present (see
            # https://pint.readthedocs.io/en/0.10.1/nonmult.html) y(1) = a
            # + b -> a = y(1) - b, with delta units b = 0
            y_1 = 1 * getattr(ureg, 'delta_' + i_unit, getattr(ureg, i_unit))
            a = y_1.to(getattr(ureg, 'delta_' + j_unit, getattr(ureg, j_unit)))

            # Calculate the constant offset. Notice that the GUI unit system
            # uses a slightly different offset definition. In Pint, offset is
            # defined as:
            #
            #   y = ax + b -> y(0) = b.
            #
            # In math.js the offset c is defined as:
            #
            #   y = a(x + c) -> y(0) = ab.
            #
            # which means that a(x + c) = ax + b -> c = b / a
            b = (
                ureg.Quantity(0, getattr(ureg, i_unit))
                .to(getattr(ureg, j_unit))
                .magnitude
            )
            value['definition'] = str(a).replace('**', '^')
            value['offset'] = b / a.magnitude

        if value['dimension'] == '' and not value.get('definition'):
            dimensionless_units.append(value)
        else:
            units.append(value)

    # Pint does not contain a separate definition for the dimensionless unit, but contains
    # definitions for aliases of the dimensionless unit. In the JS version we instead have
    # an explicit dimensionless unit and add aliases to it.
    units.append(
        {
            'name': 'dimensionless',
            'dimension': 'dimensionless',
            'label': 'Dimensionless',
            'abbreviation': '',
            'aliases': [value['name'] for value in dimensionless_units],
        }
    )

    # Reorder unit list so that base dimensions come first. Units are registered
    # in the list order and base units need to be registered before derived
    # ones.
    units.sort(key=lambda x: x.get('name'))
    units.sort(key=lambda x: 0 if x.get('definition') is None else 1)

    return units, prefixes
