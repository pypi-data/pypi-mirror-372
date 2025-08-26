from sixgill.sixgill_request_classes.sixgill_base_post_auth_request import SixgillBasePostAuthRequest


class SixgillDVEEnrichRemediationRequest(SixgillBasePostAuthRequest):
    end_point = None
    method = 'GET'

    def __init__(self, channel_id, access_token, cve_id):
        super(SixgillDVEEnrichRemediationRequest, self).__init__(channel_id, access_token)
        self.end_point = 'dve_enrich/{}/remediation'.format(cve_id)
