from sixgill.sixgill_request_classes.sixgill_base_post_auth_request import SixgillBasePostAuthRequest


class SixgillSpecificActionableAlertGetRequest(SixgillBasePostAuthRequest):
    end_point = None
    method = 'GET'

    def __init__(self, channel_id, access_token, actionable_alert_id, organization_id):
        super(SixgillSpecificActionableAlertGetRequest, self).__init__(channel_id, access_token)

        self.end_point = 'alerts/actionable_alert/{}'.format(actionable_alert_id)
        if organization_id:
            self.request.params['organization_id'] = organization_id
