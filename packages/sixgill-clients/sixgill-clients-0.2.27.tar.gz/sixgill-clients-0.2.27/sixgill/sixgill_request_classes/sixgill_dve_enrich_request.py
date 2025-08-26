from sixgill.sixgill_request_classes.sixgill_base_post_auth_request import SixgillBasePostAuthRequest


class SixgillDVEEnrichRequest(SixgillBasePostAuthRequest):
    end_point = None
    method = 'GET'

    def __init__(self, channel_id, access_token, cve_id):
        super(SixgillDVEEnrichRequest, self).__init__(channel_id, access_token)
        self.end_point = 'dve_enrich/{}'.format(cve_id)
