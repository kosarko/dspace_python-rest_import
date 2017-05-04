import logging
from pprint import pformat
import requests
from clarin_dspace.content.Community import Community


class Repository(object):
    """Represent and access repository content"""

    def __init__(self, base_url):
        """Constructor for Repository
        base_url: The repository url up to /rest or /xmlui
        """
        self.base_url = base_url
        self.api_url = base_url + '/rest'
        self.token = None
        self.request_headers = None

    def login(self, email, password):
        """Obtain access token for user with provided email and password"""
        response = requests.post(self.get_api_url() + '/login', json={'email': email,
                                                                      'password': password})
        logging.debug(pformat(response))
        response.raise_for_status()
        logging.info("User successfully logged in")
        self.token = response.text
        self.request_headers = {'rest-dspace-token': self.token, 'Accept': 'application/json'}

    def login_status(self):
        """Returns the json of /rest/status; usually for debugging"""
        response = requests.get(self.get_api_url() + '/status', headers=self.get_request_headers())
        logging.debug(pformat(response))
        response.raise_for_status()
        return response.json()

    def find_community_by_name(self, community_name):
        """Fetch all communities and do exact match on the name.
        Return Community object"""
        url = self.get_api_url() + '/communities'
        response = requests.get(url, headers=self.get_request_headers())
        logging.debug(pformat(response))
        response.raise_for_status()
        communities = {community['name']: community['id'] for community in response.json()}
        logging.debug(pformat(communities))
        if community_name in communities:
            return Community(community_name, communities[community_name], self)
        else:
            logging.info('Community "%s" not found', community_name)

    def create_community(self, community_name):
        """Create a community as the logged in user, no check whether the give name exists"""
        url = self.get_api_url() + '/communities'
        response = requests.post(url, json={'name': community_name},
                                 headers=self.get_request_headers())
        logging.debug(pformat(response))
        response.raise_for_status()
        community = response.json()
        logging.info('Created community with name "%s" and id "%s"', community_name,
                     community['id'])
        return Community(community_name, community['id'], self)

    def find_or_create_community(self, community_name):
        """Search for community by name and if fail create new one with that name"""
        community = self.find_community_by_name(community_name)
        return community if community else self.create_community(community_name)

    def logout(self):
        """Invalidate the access token"""
        response = requests.post(self.get_api_url() + '/logout', headers=self.get_request_headers())
        logging.debug(pformat(response))
        response.raise_for_status()
        logging.info("User successfully logged out")

    def get_request_headers(self):
        """Returns request headers created in login; contains access token and accept json"""
        return self.request_headers

    def get_api_url(self):
        """Get the /rest endpoint url"""
        return self.api_url
