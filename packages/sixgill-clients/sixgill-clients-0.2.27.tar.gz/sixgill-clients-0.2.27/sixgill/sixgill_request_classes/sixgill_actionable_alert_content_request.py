from sixgill.sixgill_request_classes.sixgill_base_post_auth_request import SixgillBasePostAuthRequest


class SixgillActionableAlertContentGetRequest(SixgillBasePostAuthRequest):
    end_point = None
    method = 'GET'

    def __init__(self, channel_id, access_token, actionable_alert_id, limit, highlight, organization_id,
                 fetch_only_current_item, aggregate_alert_id=None):
        super(SixgillActionableAlertContentGetRequest, self).__init__(channel_id, access_token)

        self.end_point = 'alerts/actionable_alert_content/{}'.format(actionable_alert_id)
        self.request.params['limit'] = limit
        self.request.params['highlight'] = highlight
        self.request.params['fetch_only_current_item'] = fetch_only_current_item
        if organization_id:
            self.request.params['organization_id'] = organization_id
        if aggregate_alert_id is not None:
            self.request.params['aggregate_alert_id'] = aggregate_alert_id
