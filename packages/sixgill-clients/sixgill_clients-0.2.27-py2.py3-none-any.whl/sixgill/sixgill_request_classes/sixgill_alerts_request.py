from sixgill.sixgill_request_classes.sixgill_base_post_auth_request import SixgillBasePostAuthRequest


class SixgillAlertsRequest(SixgillBasePostAuthRequest):
    end_point = 'alerts/feed/alerts'
    method = 'GET'

    def __init__(self, channel_id, access_token, include_delivered_items, bulk_size, skip,
                 sort_by, sort_order, is_read, severity, threat_level, threat_type):
        super(SixgillAlertsRequest, self).__init__(channel_id, access_token)

        self.request.params['include_delivered_items'] = include_delivered_items
        self.request.params['limit'] = bulk_size
        self.request.params['skip'] = skip
        self.request.params['sort_by'] = sort_by
        self.request.params['sort_order'] = sort_order
        self.request.params['is_read'] = is_read
        self.request.params['severity'] = severity
        self.request.params['threat_level'] = threat_level
        self.request.params['threat_type'] = threat_type
