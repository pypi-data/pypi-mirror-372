from sixgill.sixgill_request_classes.sixgill_base_post_auth_request import SixgillBasePostAuthRequest


class SixgillReportGetHTMLRequest(SixgillBasePostAuthRequest):
    end_point = None
    method = 'GET'

    def __init__(self, channel_id, access_token, report_id, html_format):
        super(SixgillReportGetHTMLRequest, self).__init__(channel_id, access_token)

        self.end_point = 'reports/report/{}/html'.format(report_id)
        self.request.params['html_format'] = html_format
