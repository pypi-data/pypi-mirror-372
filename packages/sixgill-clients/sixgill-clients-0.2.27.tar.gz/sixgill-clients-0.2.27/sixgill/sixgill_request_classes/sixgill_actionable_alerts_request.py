from collections import OrderedDict

from sixgill.sixgill_request_classes.sixgill_base_post_auth_request import SixgillBasePostAuthRequest


class SixgillActionableAlertsGetRequest(SixgillBasePostAuthRequest):
    end_point = 'alerts/actionable-alert'
    method = 'GET'

    def __init__(self, channel_id, access_token, fetch_size, offset, from_date, to_date, sort_by,
                 sort_order, is_read, threat_level, threat_type, organization_id):
        super(SixgillActionableAlertsGetRequest, self).__init__(channel_id, access_token)

        params = OrderedDict(**{
            "fetch_size": fetch_size,
            "offset": offset,
            "from_date": from_date,
            "to_date": to_date,
            "sort_by": sort_by,
            "sort_order": sort_order,
            "is_read": is_read,
            "threat_level": threat_level,
            "threat_type": threat_type,
            "organization_id": organization_id
        })
        self.request.params = OrderedDict(**{k: v for k, v in params.items() if v is not None})
