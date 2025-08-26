from sixgill.sixgill_request_classes.sixgill_base_post_auth_request import SixgillBasePostAuthRequest


class SixgillReportsGetBulkRequest(SixgillBasePostAuthRequest):
    end_point = 'reports/reports'
    method = 'POST'

    def __init__(self, channel_id, access_token, limit=50, offset=0, sort_by=None,
                 sort_order=None, is_read=None, threats=None, id_list=None):
        super(SixgillReportsGetBulkRequest, self).__init__(channel_id, access_token, data={})

        self.request.data['fetch_size'] = limit
        self.request.data['offset'] = offset
        self.request.data['sort_by'] = sort_by
        self.request.data['sort_order'] = sort_order
        self.request.data['is_read'] = is_read
        if threats:
            self.request.data['threat_level'] = threats
        self.request.data['id_list'] = id_list

