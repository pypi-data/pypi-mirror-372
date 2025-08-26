from sixgill.sixgill_base_client import SixgillBaseClient
from sixgill.sixgill_request_classes.sixgill_organization_assets_get_request import SixgillOrganizationAssetsGetRequest
from sixgill.sixgill_request_classes.sixgill_organization_assets_post_request import SixgillOrganizationAssetsPostRequest
from sixgill.sixgill_request_classes.sixgill_organization_assets_put_request import SixgillOrganizationAssetsPutRequest


class SixgillOrganizationAssetsClient(SixgillBaseClient):

    def __init__(self, client_id, client_secret, channel_id, logger=None, session=None, verify=False,
                 num_of_attempts=5):
        super(SixgillOrganizationAssetsClient, self).__init__(client_id=client_id, client_secret=client_secret,
                                                           channel_id=channel_id, logger=logger,
                                                           session=session, verify=verify,
                                                           num_of_attempts=num_of_attempts)

    def get_organization_assets(self, organization_id=None, upgraded_assets=False):
        return self._send_request(
            SixgillOrganizationAssetsGetRequest(channel_id=self.channel_id, access_token=self._get_access_token(), 
                                    upgraded_assets=upgraded_assets, organization_id=organization_id))

    def create_organization_assets(self, json_body, organization_id=None, upgraded_assets=False):
        return self._send_request(
            SixgillOrganizationAssetsPostRequest(channel_id=self.channel_id, access_token=self._get_access_token(),
                                                     json_body=json_body,
                                                     organization_id=organization_id, upgraded_assets=upgraded_assets))
    
    def update_organization_assets(self, json_body, organization_id=None, upgraded_assets=False):
        return self._send_request(
            SixgillOrganizationAssetsPutRequest(channel_id=self.channel_id, access_token=self._get_access_token(),
                                                     json_body=json_body,
                                                     organization_id=organization_id, upgraded_assets=upgraded_assets))