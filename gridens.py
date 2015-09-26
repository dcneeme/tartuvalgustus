import requests
import sys, logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger(__name__)

__version__ = '1.0'


class LuxmeterDataSender:
    """ Utility class for sending luxmeter status data to Gridens

    Instantiate a class object with your API token and organization's id.
    Then call .send() and pass it the readings (floats or ints, in Lx) as parameters.

    See the end of file for example usage.
    """

    url = 'https://app.gridens.com/api/plugins/luxmeters/%d/'
    # For local development
    # url = 'http://localhost:7100/api/plugins/luxmeters/%d/'

    def __init__(self, api_token, organization_id):
        self.api_token = api_token
        self.organization_id = organization_id

    def send(self, *readings):
        data = {
            'readings': [
                {
                    'index': i,
                    'value': value,
                }
                for i, value in enumerate(readings)
            ]
        }
        headers = {
            'Authorization': 'Token %s' % self.api_token,
        }

        log.debug('data: '+str(data))
        log.debug('headers: '+str(headers))
        
        #r = requests.post(self.url % self.organization_id, json=data, headers=headers)
        r = requests.post(self.url % self.organization_id, data, headers=headers)
        # Should we return the request object instead?
        return r.status_code == 200 # True if ok


if __name__ == '__main__':
    sender = LuxmeterDataSender(api_token='api_token', organization_id=42)
    sender.send(3.29, 3.91, 5)
