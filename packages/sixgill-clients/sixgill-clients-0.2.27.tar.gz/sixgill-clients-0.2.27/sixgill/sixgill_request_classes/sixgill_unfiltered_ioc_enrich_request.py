from sixgill.sixgill_request_classes.sixgill_base_post_auth_request import SixgillBasePostAuthRequest


class SixgillUnfilteredIOCEnrichRequest(SixgillBasePostAuthRequest):
    end_point = None
    method = 'POST'

    def __init__(self, channel_id, access_token, ioc_type, ioc_value, from_date, to_date, skip, limit):
        super(SixgillUnfilteredIOCEnrichRequest, self).__init__(channel_id, access_token)
        self.end_point = 'unfiltered_enrichment/enrich'
        self.request.headers['Content-Type'] = 'application/json'
        self.request.json = {'ioc_type': ioc_type, 'ioc_value': ioc_value, 'skip': skip, 'limit': limit}
        if from_date:
            self.request.json.update({'from_date': from_date})
        if to_date:
            self.request.json.update({'to_date': to_date})