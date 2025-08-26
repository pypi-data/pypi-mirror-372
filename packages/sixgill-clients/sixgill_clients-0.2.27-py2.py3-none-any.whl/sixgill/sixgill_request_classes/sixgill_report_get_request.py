from sixgill.sixgill_request_classes.sixgill_base_post_auth_request import SixgillBasePostAuthRequest


class SixgillReportGetRequest(SixgillBasePostAuthRequest):
    end_point = None
    method = 'GET'

    def __init__(self, channel_id, access_token, report_id):
        super(SixgillReportGetRequest, self).__init__(channel_id, access_token)

        self.end_point = 'reports/report/{}'.format(report_id)