from sixgill.sixgill_request_classes.sixgill_base_post_auth_request import SixgillBasePostAuthRequest


class SixgillOrganizationAssetsGetRequest(SixgillBasePostAuthRequest):
    end_point = None
    method = 'GET'

    def __init__(self, channel_id, access_token, organization_id=None, upgraded_assets=False):
        super(SixgillOrganizationAssetsGetRequest, self).__init__(channel_id, access_token)
        self.end_point = 'assets/organization'
        self.request.params["upgraded_assets"] = upgraded_assets
        if organization_id:
            self.request.params["organization_id"] = organization_id