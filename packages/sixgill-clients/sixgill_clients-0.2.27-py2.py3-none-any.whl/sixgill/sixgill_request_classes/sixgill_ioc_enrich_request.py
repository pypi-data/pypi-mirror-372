from sixgill.sixgill_request_classes.sixgill_base_post_auth_request import SixgillBasePostAuthRequest


class SixgillIOCEnrichRequest(SixgillBasePostAuthRequest):
    end_point = None
    method = 'POST'

    def __init__(self, channel_id, access_token, ioc_type, ioc_value, skip=0):
        super(SixgillIOCEnrichRequest, self).__init__(channel_id, access_token)
        self.end_point = 'ioc/enrich'
        self.request.headers['Content-Type'] = 'application/json'
        self.request.json = {'ioc_type': ioc_type, 'ioc_value': ioc_value, 'skip': skip}
