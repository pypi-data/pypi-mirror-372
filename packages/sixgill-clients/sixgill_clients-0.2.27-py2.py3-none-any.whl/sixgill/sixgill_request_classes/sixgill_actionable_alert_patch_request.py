from sixgill.sixgill_request_classes.sixgill_base_post_auth_request import SixgillBasePostAuthRequest


class SixgillActionableAlertPatchRequest(SixgillBasePostAuthRequest):
    end_point = None
    method = 'PATCH'

    def __init__(self, channel_id, access_token, actionable_alert_id, organization_id, json_body, sub_alert_indexes):
        super(SixgillActionableAlertPatchRequest, self).__init__(channel_id, access_token)

        self.end_point = 'alerts/actionable_alert/{}'.format(actionable_alert_id)
        self.request.params['consumer'] = channel_id
        if organization_id:
            self.request.params['organization_id'] = organization_id
        if sub_alert_indexes:
            self.request.params['sub_alert_indexes'] = sub_alert_indexes
        self.request.json = json_body
