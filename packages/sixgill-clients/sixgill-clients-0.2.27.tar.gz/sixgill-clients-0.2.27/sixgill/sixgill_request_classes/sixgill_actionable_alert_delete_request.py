from sixgill.sixgill_request_classes.sixgill_base_post_auth_request import SixgillBasePostAuthRequest


class SixgillActionableAlertsDeleteRequest(SixgillBasePostAuthRequest):
    end_point = 'alerts/actionable-alert'
    method = 'DELETE'

    def __init__(self, channel_id, access_token, actionable_alert_ids, organization_id, is_read, threat_level,
                 threat_type):
        super(SixgillActionableAlertsDeleteRequest, self).__init__(channel_id, access_token)

        params = {
            "organization_id": organization_id,
            "is_read": is_read,
            "threat_level": threat_level,
            "threat_type": threat_type
        }
        self.request.params = {k: v for k, v in params.items() if v is not None}
        self.request.json = actionable_alert_ids
