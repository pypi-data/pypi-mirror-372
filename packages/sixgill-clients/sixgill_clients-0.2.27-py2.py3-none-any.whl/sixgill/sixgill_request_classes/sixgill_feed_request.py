from sixgill.sixgill_request_classes.sixgill_base_post_auth_request import SixgillBasePostAuthRequest


class SixgillFeedRequest(SixgillBasePostAuthRequest):
    end_point = None
    method = 'GET'

    def __init__(self, channel_id, access_token, limit, feed_steam):
        super(SixgillFeedRequest, self).__init__(channel_id, access_token)
        self.end_point = '{}/ioc'.format(feed_steam)
        self.request.params['limit'] = limit
