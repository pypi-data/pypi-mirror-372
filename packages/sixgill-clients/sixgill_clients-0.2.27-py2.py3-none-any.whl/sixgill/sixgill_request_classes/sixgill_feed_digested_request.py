from sixgill.sixgill_request_classes.sixgill_base_post_auth_request import SixgillBasePostAuthRequest


class SixgillFeedDigestedRequest(SixgillBasePostAuthRequest):
    end_point = None
    method = 'POST'

    def __init__(self, channel_id, access_token, feed_steam):
        super(SixgillFeedDigestedRequest, self).__init__(channel_id, access_token)
        self.end_point = '{}/ioc/ack'.format(feed_steam)

