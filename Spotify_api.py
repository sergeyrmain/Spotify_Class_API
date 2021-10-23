import base64
import requests
import datetime
from urllib.parse import urlencode

client_id = '1c15a5bfdab440ca9dd4e7914afc999c'
client_secret = '17110245804f4cf0a3a2e49c3abb20b8'


class SpotifyAPI(object):
    token_url = 'https://accounts.spotify.com/api/token'

    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.cliend_secret = client_secret

    def get_client_credentials(self):
        self.client_id = client_id
        self.cliend_secret = client_secret

        # return a base64 encoded string (NOT bytes)
        if client_id == None or client_secret == None:
            raise Exeption("Must set client_id and client_secret")
            # do alookup for a token
            # this token is for future requests
            # Client Credentials Flow
        client_creds = f"{client_id}:{client_secret}"  # -string
        client_creds_b64 = base64.b64encode(client_creds.encode())  # type -bytes
        # security
        return client_creds_b64.decode()

    def get_token_headers(self):

        client_creds_b64 = self.get_client_credentials()
        return {
            'Authorization': f"Basic {client_creds_b64}"  # the decode only decoded the bytes NOT the base64
        }

    def get_token_data(self):
        return {
            'grant_type': 'client_credentials'  # spotify request
        }

    def get_access_token(self):
        # cuse preform_auth dosent gives us the access token and if its expires we will pref auth again
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        # check if the token expired
        if expires < now:
            self.preform_auth()
            return self.get_access_token()
        elif token == None:
            self.preform_auth()
            return self.get_access_token()

        return token

    def search(self, query, search_type='artist'):
        access_token = self.get_access_token()

        headers = self.get_resource_header()
        endpoint = 'https://api.spotify.com/v1/search'
        data = urlencode({"q": query, "type": search_type.lower()})
        lookup_url = f"{endpoint}?{data}"
        r = requests.get(lookup_url, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()

    def preform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()
        r = requests.post(token_url, data=token_data, headers=token_headers)

        # chekc that the request have a valid status code
        if r.status_code not in range(200, 299):
            raise Exeption("Authentication Failed")
            return False
        data = r.json()
        now = datetime.datetime.now()  # time when request is heppening :AKA now
        access_token = data['access_token']
        expires_in = data['expires_in']  # sec
        expires = now + datetime.timedelta(seconds=expires_in)  # if we will need to "refresh" the toke we can just
        # check expires
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        # print:
        # 'access_token':
        # 'BQB_RJ6Jbg4mTHil6WTKAUcZCmfY4N6SchDApTVpDEDe8iplQn-s3lL_TyPn63fNvUpQG7qi6uoGy1ACUjA'
        # , 'token_type': 'Bearer', 'expires_in': 3600}
        return True

    def get_resource_header(self):
        access_token = self.get_access_token()

        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        return headers

    def get_resource(self, _id, resource_type='albums'):
        headers = self.get_resource_header()
        endpoint = f"https://api.spotify.com/v1/{resource_type}/{_id}"
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()

    # search by id
    def get_album(self, _id):
        return self.get_resource(_id, 'albums')

    def get_artist(self, _id):
        return self.get_resource(_id, 'artists')