from sixgill.sixgill_request_classes.sixgill_base_post_auth_request import SixgillBasePostAuthRequest


class SixgillFieldEnrichRequest(SixgillBasePostAuthRequest):
    end_point = None
    method = 'POST'

    def __init__(self, channel_id, access_token, sixgill_field, sixgill_field_value, skip=0):
        super(SixgillFieldEnrichRequest, self).__init__(channel_id, access_token)
        self.end_point = 'ioc/enrich'
        self.request.headers['Content-Type'] = 'application/json'
        self.request.json = {'sixgill_field': sixgill_field, 'sixgill_field_value': sixgill_field_value, 'skip': skip}
