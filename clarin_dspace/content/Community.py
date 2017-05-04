import logging
from pprint import pformat
import requests
from clarin_dspace.content.Collection import Collection


class Community(object):
    """DSpace community representation. Holds name & id; methods to handle collections"""

    def __init__(self, name, com_id, parent=None):
        """Constructor for Community"""
        self.name = name
        self.id_ = com_id
        self.parent = parent

    def create_collection(self, collection_name):
        """Create collection in this community with given name, no check for preexisting"""
        url = self.get_api_url() + '/communities/' + str(self.id_) + '/collections'
        response = requests.post(url, json={'name': collection_name},
                                 headers=self.get_request_headers())
        logging.debug(pformat(response))
        response.raise_for_status()
        collection = response.json()
        logging.info('Created collection with name "%s" and id "%s"', collection_name,
                     collection['id'])
        return Collection(collection_name, collection['id'], self)

    def find_collection_by_name(self, collection_name):
        """Try finding collection under this community with exactly the given name"""
        url = self.get_api_url() + '/communities/' + str(self.id_) + '/collections'
        response = requests.get(url, headers=self.get_request_headers())
        logging.debug(pformat(response))
        response.raise_for_status()
        collections = {collection['name']: collection['id'] for collection in response.json()}
        logging.debug(pformat(collections))
        if collection_name in collections:
            return Collection(collection_name, collections[collection_name], self)
        else:
            logging.info('Collection "%s" not found', collection_name)

    def find_or_create_collection(self, collection_name):
        """Search for collection by name and if fail create new one with that name"""
        collection = self.find_collection_by_name(collection_name)
        return collection if collection else self.create_collection(collection_name)

    def get_request_headers(self):
        """Return prepared request headers with access token and accept method. Fetched from
        parent."""
        return self.parent.get_request_headers()

    def get_api_url(self):
        """Return /rest api endpoint url. Fetched from parent."""
        return self.parent.get_api_url()
