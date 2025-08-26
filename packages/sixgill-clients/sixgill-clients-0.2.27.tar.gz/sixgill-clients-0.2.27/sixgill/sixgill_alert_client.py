import traceback

from sixgill.sixgill_base_client import SixgillBaseClient
from sixgill.sixgill_request_classes.sixgill_alerts_digested_request import SixgillAlertsDigestedRequest
from sixgill.sixgill_request_classes.sixgill_alerts_request import SixgillAlertsRequest
from sixgill.sixgill_constants import VALID_STATUS_CODES
from sixgill.sixgill_utils import streamify


class SixgillAlertClient(SixgillBaseClient):

    def __init__(self, client_id, client_secret, channel_id, logger=None, bulk_size=1000, session=None, verify=False,
                 num_of_attempts=5):
        super(SixgillAlertClient, self).__init__(client_id, client_secret, channel_id, logger, bulk_size, session,
                                                 verify, num_of_attempts)
        self.digested_ids = []

    @staticmethod
    def _get_item_id(item):
        return item.get('id', "")

    def get_alerts_bulk(self, include_delivered_items=False, skip=0, sort_by=None,
                        sort_order=None, is_read=None, severity=None, threat_level=None,
                        threat_type=None):
        return self._send_request(SixgillAlertsRequest(self.channel_id, self._get_access_token(),
                                                       include_delivered_items, self.bulk_size, skip, sort_by,
                                                       sort_order, is_read, severity, threat_level, threat_type))

    def _mark_as_digested(self, digested_ids):
        return self._send_request(SixgillAlertsDigestedRequest(self.channel_id, self._get_access_token(),
                                                               digested_ids))

    def mark_digested_item(self, item):
        try:
            doc_id = self._get_item_id(item)

        except Exception as e:
            self.logger.error('Failed extracting doc_id: {}, message {}, traceback: {}'.format(item, e,
                                                                                               traceback.format_exc()))
            raise

        self.digested_ids.append(doc_id)
        self.logger.debug('Marked id: {} as digested'.format(doc_id))

    def commit_digested_items(self, force=False):
        if (len(self.digested_ids) >= self.bulk_size or force) and len(self.digested_ids) > 0:
            try:
                response = self._mark_as_digested(self.digested_ids)

            except Exception as e:
                self.logger.error('Failed marking items as digested {}, traceback: {}'.format(e,
                                                                                              traceback.format_exc()))
                raise

            if response.get("status") in VALID_STATUS_CODES:
                self.digested_ids = []

            self.logger.info('{}'.format(response.get("message")))

    @streamify
    def get_alert(self, sort_by=None, sort_order=None, is_read=None, severity=None,
                  threat_level=None, threat_type=None):
        """
        This function is wrapped using a streamify decorator,
        which creates an iterator out of the list and returns item by item until server has nothing to return

        :param sort_by: One of the following [date, alert_name, severity, threat_level]
        :param sort_order: One of the following [asc, desc]
        :param is_read: Filter alerts that were read or unread. One of the following[read, unread]
        :param severity: Filter by alert severity. One of the following[low, med, high]
        :param threat_level: Filter by alert threat level. One of the following[imminent, emerging]
        :param threat_type: Filter by field threat type
        :return: list of alerts
        """
        self.commit_digested_items(force=True)
        return self.get_alerts_bulk(sort_by=sort_by, sort_order=sort_order, is_read=is_read, severity=severity,
                                    threat_level=threat_level, threat_type=threat_type)
