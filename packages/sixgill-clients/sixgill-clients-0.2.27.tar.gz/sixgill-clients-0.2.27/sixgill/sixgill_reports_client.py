from sixgill.sixgill_base_client import SixgillBaseClient
from sixgill.sixgill_request_classes.sixgill_report_get_html_request import SixgillReportGetHTMLRequest
from sixgill.sixgill_request_classes.sixgill_report_get_request import SixgillReportGetRequest
from sixgill.sixgill_request_classes.sixgill_reports_get_bulk_request import SixgillReportsGetBulkRequest


class SixgillReportsClient(SixgillBaseClient):

    def __init__(self, client_id, client_secret, channel_id, logger=None, session=None, verify=False,
                 num_of_attempts=5):
        super(SixgillReportsClient, self).__init__(client_id=client_id, client_secret=client_secret,
                                                   channel_id=channel_id, logger=logger,
                                                   session=session, verify=verify,
                                                   num_of_attempts=num_of_attempts)

    def get_reports_bulk(self, limit=50, offset=0, sort_by=None,
                         sort_order=None, is_read=None, threats=None,
                         id_list=None):
        return self._send_request(
            SixgillReportsGetBulkRequest(channel_id=self.channel_id, access_token=self._get_access_token(),
                                         limit=limit, offset=offset, sort_by=sort_by,
                                         sort_order=sort_order, is_read=is_read, threats=threats,
                                         id_list=id_list))

    def get_report(self, report_id):
        return self._send_request(
            SixgillReportGetRequest(channel_id=self.channel_id, access_token=self._get_access_token(),
                                    report_id=report_id))

    def get_html_report(self, report_id, html_format):
        return self._send_request(
            SixgillReportGetHTMLRequest(channel_id=self.channel_id, access_token=self._get_access_token(),
                                        report_id=report_id, html_format=html_format))
