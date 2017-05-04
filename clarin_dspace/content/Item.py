import logging
from pprint import pformat
import os
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder


class Item(object):
    """DSpace item representation. Holds name, id & handle; methods to add bitstreams"""

    def __init__(self, name, item_id, handle, parent=None):
        """Constructor for Item"""
        self.name = name
        self.id_ = item_id
        self.handle = handle
        self.parent = parent

    def add_bitstream(self, data_file_path):
        """Upload file located at data_file_path to item"""
        # get file name; used as the bitstream name & for format detection
        data_file_name = os.path.basename(data_file_path)
        url = self.get_api_url() + '/items/' + str(self.id_) + '/bitstreams?name=' + data_file_name
        # With this encoder the file should not be read in memory, but streamed right away
        encoder = MultipartEncoder([('filename', open(data_file_path, 'rb'))])
        # Make sure we don't modify parent's headers with added content type
        request_headers = self.get_request_headers().copy()
        request_headers['Content-Type'] = encoder.content_type
        response = requests.post(url, data=encoder, headers=request_headers)
        logging.debug(pformat(response))
        response.raise_for_status()
        bitstream = response.json()
        logging.info(logging.info('Created bitstream with name "%s" and id "%s"',
                                  data_file_name, bitstream['id']))
        logging.debug(pformat(bitstream))

    def replace_metadata_field(self, json_metadata_entry_array):
        """MetadataEntry is {key, value, lang} object. PUT clears all the values mapped to the
        key in item and adds those from the MetadataEntry."""
        url = self.get_api_url() + '/items/' + str(self.id_) + '/metadata'
        response = requests.put(url, json=json_metadata_entry_array,
                                headers=self.get_request_headers())
        logging.debug(pformat(response))
        response.raise_for_status()
        logging.info('Successfully replaced metadata on item %s.', self.id_)

    def update_identifier(self, handle):
        """Replace all dc.identifier.uri with the supplied handle"""
        self.replace_metadata_field([{'key': 'dc.identifier.uri', 'value': handle,
                                      'language': None}])

    def get_request_headers(self):
        """Return prepared request headers with access token and accept method. Fetched from
        parent."""
        return self.parent.get_request_headers()

    def get_api_url(self):
        """Return /rest api endpoint url. Fetched from parent."""
        return self.parent.get_api_url()
