from sixgill.sixgill_request_classes.sixgill_base_post_auth_request import SixgillBasePostAuthRequest


class SixgillOrganizationAssetsPutRequest(SixgillBasePostAuthRequest):
    end_point = None
    method = 'PUT'

    def __init__(self, channel_id, access_token, json_body, organization_id=None, upgraded_assets=False):
        super(SixgillOrganizationAssetsPutRequest, self).__init__(channel_id, access_token)
        self.end_point = 'assets/organization'
        self.request.params["upgraded_assets"] = upgraded_assets
        self.request.json = json_body
        if organization_id:
            self.request.params['organization_id'] = organization_id