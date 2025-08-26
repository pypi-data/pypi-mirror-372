import traceback

from sixgill.sixgill_base_client import SixgillBaseClient
from sixgill.sixgill_request_classes.sixgill_feed_digested_request import SixgillFeedDigestedRequest
from sixgill.sixgill_request_classes.sixgill_feed_request import SixgillFeedRequest
from sixgill.sixgill_utils import streamify, is_indicator


class SixgillFeedClient(SixgillBaseClient):

    def __init__(self, client_id, client_secret, channel_id, feed_stream, logger=None, bulk_size=1000, session=None,
                 verify=False, num_of_attempts=5):
        super(SixgillFeedClient, self).__init__(client_id, client_secret, channel_id, logger, bulk_size, session,
                                                verify, num_of_attempts)
        self.feed_stream = feed_stream

    def get_bundle(self):
        return self._send_request(SixgillFeedRequest(self.channel_id, self._get_access_token(), self.bulk_size,
                                                     self.feed_stream))

    def _mark_as_digested(self):
        return self._send_request(SixgillFeedDigestedRequest(self.channel_id, self._get_access_token(),
                                                             self.feed_stream))

    @streamify
    def get_indicator(self):
        """
        This function is wrapped using a streamify decorator,
        which creates an iterator out of the list and returns item by item until server has nothing to return
        """
        self.commit_indicators()
        indicators = self.get_bundle().get("objects", [])
        return list(filter(is_indicator, indicators))

    def commit_indicators(self):
        try:
            response = self._mark_as_digested()

        except Exception as e:
            self.logger.error('Failed submitting {}, traceback: {}'.format(e, traceback.format_exc()))
            raise

        if response <= 0:
            self.logger.info('Nothing committed')
        else:
            self.logger.info('Committed {} indicators'.format(response))
