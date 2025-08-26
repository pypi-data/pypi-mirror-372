import traceback
import requests
import time

from sixgill.sixgill_request_classes.sixgill_auth_request import SixgillAuthRequest
from sixgill.sixgill_exceptions import BadResponseException, AuthException
from sixgill.sixgill_utils import get_logger
from sixgill.sixgill_constants import VALID_STATUS_CODES


class SixgillBaseClient(object):

    def __init__(self, client_id, client_secret, channel_id, logger=None, bulk_size=1000, session=None, verify=False,
                 num_of_attempts=5):
        self.client_id = client_id
        self.client_secret = client_secret
        self.channel_id = channel_id
        self.logger = get_logger(self.__class__.__name__) if logger is None else logger
        self.bulk_size = bulk_size
        self.session = session if session else requests.Session()
        self.verify = verify
        self.num_of_attempts = num_of_attempts

    def get_response(self, sixgill_api_request):
        response = None

        for attempt in range(self.num_of_attempts):
            response = self.session.send(request=sixgill_api_request.prepare(), verify=self.verify)

            if response.status_code not in VALID_STATUS_CODES:
                self.logger.info('response error attempt: {}'.format(attempt + 1 / self.num_of_attempts))
                self.logger.info('status response code {}, reason {}'.format(response.status_code, response.reason))
                self.logger.info('try again in 1 sec...')
                time.sleep(1)

            else:
                return response
        return response

    def _send_request(self, sixgill_api_request):
        try:
            response = self.get_response(sixgill_api_request=sixgill_api_request)

            if response.status_code not in VALID_STATUS_CODES:
                self.logger.error('Error in API call [{}] - {}'.format(response.status_code, response.reason))
                raise BadResponseException(status_code=response.status_code, reason=response.reason, url=response.url,
                                           method=response.request.method)

            if 'html' in dict(response.headers).get('Content-Type', ''):
                return response.text

            return response.json()

        except Exception as e:
            self.logger.error('Error {}, traceback: {}'.format(e, traceback.format_exc()))
            raise

    def _get_access_token(self):
        try:
            response = self.get_response(sixgill_api_request=SixgillAuthRequest(self.client_id, self.client_secret,
                                                                                self.channel_id))

            if response.status_code not in VALID_STATUS_CODES:
                raise AuthException(status_code=response.status_code, reason=response.reason, url=response.url,
                                    method=response.request.method)

            json_response = response.json()
            return json_response.get('access_token')

        except Exception as e:
            self.logger.error('Failed getting access token: {}, traceback: {}'.format(e, traceback.format_exc()))
            raise

    def get_access_token(self):
        return self._get_access_token()
