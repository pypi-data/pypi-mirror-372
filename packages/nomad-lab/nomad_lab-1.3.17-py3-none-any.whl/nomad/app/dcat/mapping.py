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

from rdflib import RDF, BNode, Graph, Literal, URIRef
from rdflib.namespace import DCAT, FOAF, RDF, Namespace
from rdflib.namespace import DCTERMS as DCT

from nomad.config import config
from nomad.datamodel import User

from .common import url

VCARD = Namespace('http://www.w3.org/2006/vcard/ns#')
HYDRA = Namespace('http://www.w3.org/ns/hydra/core#')


def get_optional_entry_prop(entry, name):
    try:
        value = entry
        segments = name.split('.')
        for segment in segments:
            value = value[segment]

        return value
    except (KeyError, AttributeError):
        return 'unavailable'


class Mapping:
    def __init__(self):
        self.g = Graph()
        self.g.bind('rdf', RDF)
        self.g.bind('dcat', DCAT)
        self.g.bind('dct', DCT)
        self.g.bind('vcard', VCARD)
        self.g.bind('foaf', FOAF)
        self.g.bind('hydra', HYDRA)

        self.persons = {}

    def map_catalog(self, entries, total: int, after: str, modified_since, slim=True):
        def uri_ref(after):
            kwargs = dict()
            if after is not None:
                kwargs['after'] = after
            if modified_since is not None:
                kwargs['modified_since'] = modified_since.strftime('%Y-%m-%d')
            return URIRef(url('catalog', **kwargs))

        after = after.strip() if after else None

        catalog = uri_ref(after=None)
        self.g.add((catalog, RDF.type, DCAT.Catalog))
        last_entry = None
        for entry in entries:
            self.g.add((catalog, DCT.dataset, self.map_entry(entry, slim=slim)))
            last_entry = entry

        hydra_collection = uri_ref(after)
        self.g.add((hydra_collection, RDF.type, HYDRA.Collection))
        self.g.add((hydra_collection, HYDRA.totalItems, Literal(total)))
        self.g.add((hydra_collection, HYDRA.first, uri_ref('')))
        if last_entry is not None:
            self.g.add((hydra_collection, HYDRA.next, uri_ref(last_entry['entry_id'])))

        self.g.add((hydra_collection, RDF.type, HYDRA.collection))

        for person in self.persons.values():
            self.g.add((catalog, DCT.creator, person))

    def map_entry(self, entry: dict, slim=False):
        dataset = URIRef(url('datasets', entry['entry_id']))

        self.g.add((dataset, RDF.type, DCAT.Dataset))
        self.g.add((dataset, DCT.identifier, Literal(entry['entry_id'])))
        self.g.add((dataset, DCT.issued, Literal(entry['upload_create_time'])))
        self.g.add((dataset, DCT.modified, Literal(entry['last_processing_time'])))
        self.g.add(
            (
                dataset,
                DCT.title,
                Literal(
                    get_optional_entry_prop(
                        entry, 'results.material.chemical_formula_descriptive'
                    )
                ),
            )
        )
        if 'comment' in entry:
            self.g.add(
                (
                    dataset,
                    DCT.description,
                    Literal(get_optional_entry_prop(entry, 'comment')),
                )
            )

        if slim:
            return dataset

        self.g.add(
            (
                dataset,
                DCAT.landingPage,
                URIRef(
                    '{}/entry/id/{}/{}'.format(
                        config.gui_url(), entry['upload_id'], entry['entry_id']
                    )
                ),
            )
        )

        self.g.add(
            (
                dataset,
                DCT.license,
                URIRef('https://creativecommons.org/licenses/by/4.0/legalcode'),
            )
        )
        self.g.add(
            (dataset, DCT.language, URIRef('http://id.loc.gov/vocabulary/iso639-1/en'))
        )

        self.g.add(
            (dataset, DCT.publisher, self.map_user(entry['main_author']['user_id']))
        )
        try:
            for author in entry['authors']:
                self.g.add((dataset, DCT.creator, self.map_user(author['user_id'])))
        except (KeyError, AttributeError):
            pass
        self.g.add(
            (
                dataset,
                DCAT.contactPoint,
                self.map_contact(entry['main_author']['user_id']),
            )
        )

        self.g.add((dataset, DCAT.distribution, self.map_distribution(entry, 'api')))
        self.g.add((dataset, DCAT.distribution, self.map_distribution(entry, 'json')))
        self.g.add((dataset, DCAT.distribution, self.map_distribution(entry, 'raw')))

        if 'datasets' in entry:
            for nomad_dataset in entry['datasets']:
                self.g.add(
                    (dataset, DCAT.distribution, self.map_nomad_dataset(nomad_dataset))
                )

        return dataset

    def map_user(self, user_id: str):
        person = self.persons.get(user_id)
        if person is not None:
            return person

        user = User.get(user_id)
        person = BNode()

        self.g.add((person, RDF.type, FOAF.Person))
        self.g.add((person, FOAF.givenName, Literal(user.first_name)))
        self.g.add((person, FOAF.familyName, Literal(user.last_name)))
        self.g.add((person, FOAF.nick, Literal(user.username)))
        self.g.add((person, FOAF.mbox, URIRef(f'mailto:{user.email}')))

        self.persons[user.user_id] = person

        return person

    def map_contact(self, user_id: str):
        person = self.persons.get(user_id)
        if person is None:
            person = self.map_user(user_id)

        user = User.get(user_id)
        self.g.add((person, RDF.type, VCARD.Individual))
        self.g.add((person, VCARD.givenName, Literal(user.first_name)))
        self.g.add((person, VCARD.familyName, Literal(user.last_name)))
        self.g.add((person, VCARD.nickName, Literal(user.username)))
        self.g.add((person, VCARD.hasEmail, Literal(user.email)))
        self.g.add(
            (
                person,
                VCARD.organization,
                Literal(get_optional_entry_prop(user, 'affiliation')),
            )
        )

        return person

    def map_distribution(self, entry: dict, dist_kind):
        if dist_kind == 'api':
            # Distribution over API
            dist = BNode()
            self.g.add((dist, RDF.type, DCAT.Distribution))
            self.g.add((dist, DCT.title, Literal(f'{entry["entry_id"]}_metadata')))
            self.g.add(
                (
                    dist,
                    DCAT.mediaType,
                    URIRef(
                        'https://www.iana.org/assignments/media-types/application/json'
                    ),
                )
            )
            self.g.add(
                (
                    dist,
                    DCAT.accessURL,
                    URIRef(
                        f'${config.api_url()}/v1/entries/{entry["entry_id"]}/archive/download'
                    ),
                )
            )
        elif dist_kind == 'json':
            # Distribution as JSON
            dist = BNode()
            self.g.add((dist, RDF.type, DCAT.Distribution))
            self.g.add((dist, DCT.title, Literal(f'{entry["entry_id"]}_archive')))
            self.g.add(
                (
                    dist,
                    DCAT.mediaType,
                    URIRef(
                        'https://www.iana.org/assignments/media-types/application/json'
                    ),
                )
            )
            self.g.add(
                (
                    dist,
                    DCAT.accessURL,
                    URIRef(
                        f'${config.api_url()}/v1/entries/{entry["entry_id"]}/archive/download'
                    ),
                )
            )
        elif dist_kind == 'raw':
            # Distribution of the raw data
            dist = BNode()
            self.g.add((dist, RDF.type, DCAT.Distribution))
            self.g.add((dist, DCT.title, Literal(f'{entry["entry_id"]}_raw_files')))
            self.g.add(
                (
                    dist,
                    DCAT.accessURL,
                    URIRef(f'${config.api_url()}/v1/entries/{entry["entry_id"]}/raw'),
                )
            )
            self.g.add(
                (
                    dist,
                    DCAT.mediaType,
                    URIRef(
                        'https://www.iana.org/assignments/media-types/application/zip'
                    ),
                )
            )

        return dist

    def map_nomad_dataset(self, dataset: dict):
        dist = BNode()
        self.g.add((dist, RDF.type, DCAT.Distribution))

        id_literal = dataset['dataset_id']
        try:
            id_literal = dataset['doi']
        except KeyError:
            pass
        self.g.add((dist, DCT.identifier, Literal(id_literal)))
        self.g.add((dist, DCT.title, Literal(dataset['dataset_name'])))
        self.g.add(
            (
                dist,
                DCT.accessURL,
                URIRef(f'{config.gui_url()}/dataset/id/{dataset["dataset_id"]}'),
            )
        )

        return dist
