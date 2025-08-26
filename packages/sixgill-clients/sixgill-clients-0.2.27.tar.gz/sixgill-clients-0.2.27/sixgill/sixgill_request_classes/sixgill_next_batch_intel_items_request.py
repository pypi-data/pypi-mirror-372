from sixgill.sixgill_request_classes.sixgill_base_post_auth_request import SixgillBasePostAuthRequest


class SixgillNextBatchIntelItemsRequest(SixgillBasePostAuthRequest):
    end_point = None
    method = 'POST'

    def __init__(self, channel_id, access_token, scroll_id, recent_items):
        super(SixgillNextBatchIntelItemsRequest, self).__init__(channel_id, access_token)

        self.end_point = 'intel/intel_items/next'
        self.request.headers['Content-Type'] = 'application/json'
        self.request.json = {'scroll_id': scroll_id, 'recent_items': recent_items}
