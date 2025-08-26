import datetime

from sixgill.sixgill_base_client import SixgillBaseClient
from sixgill.sixgill_request_classes.sixgill_actionable_alerts_request import SixgillActionableAlertsGetRequest
from sixgill.sixgill_request_classes.sixgill_specific_actionable_alert_request import \
    SixgillSpecificActionableAlertGetRequest
from sixgill.sixgill_request_classes.sixgill_actionable_alert_content_request import \
    SixgillActionableAlertContentGetRequest
from sixgill.sixgill_request_classes.sixgill_actionable_alert_patch_request import SixgillActionableAlertPatchRequest
from sixgill.sixgill_request_classes.sixgill_actionable_alert_delete_request import SixgillActionableAlertsDeleteRequest
from sixgill.sixgill_utils import actionable_alert_processing

Alerts_Time_Format = "%Y-%m-%d %H:%M:%S"


class SixgillActionableAlertClient(SixgillBaseClient):

    def __init__(self, client_id, client_secret, channel_id, logger=None, session=None, verify=False,
                 num_of_attempts=5):
        super(SixgillActionableAlertClient, self).__init__(client_id=client_id, client_secret=client_secret,
                                                           channel_id=channel_id, logger=logger,
                                                           session=session, verify=verify,
                                                           num_of_attempts=num_of_attempts)

    def get_actionable_alerts_bulk(self, limit=50, offset=0, from_date=None, to_date=None, sort_by=None,
                                   sort_order=None, is_read=None, threat_level=None,
                                   threat_type=None, organization_id=None):
        """
        This method queries the actionable alerts end point and returns the actionable alerts.
        :param limit: Number of actionable alerts
        :param offset: Number of actionable alerts skipped from top
        :param from_date: format - YYYY-MM-DD HH:mm:ss
        :param to_date: format - YYYY-MM-DD HH:mm:ss
        :param sort_by: One of the following [date, alert_name, severity, threat_level]
        :param sort_order: One of the following [asc, desc]
        :param is_read: Filter alerts that were read or unread. One of the following[read, unread]
        :param threat_level: Filter by alert threat level. One of the following[imminent, emerging]
        :param threat_type: Filter by field threat type
        :param organization_id: Filter by field organization id
        :return: list of actionable alerts
        """

        # This condition is added in order to avoid double pulling alerts due to alerts api updates
        if from_date and type(from_date) is str:
            from_date = datetime.datetime.strptime(from_date, Alerts_Time_Format)
            from_date = (from_date + datetime.timedelta(seconds=1))
        raw_alerts = self._send_request(
            SixgillActionableAlertsGetRequest(channel_id=self.channel_id, access_token=self._get_access_token(),
                                              fetch_size=limit, offset=offset, from_date=from_date,
                                              to_date=to_date,
                                              sort_by=sort_by, sort_order=sort_order, is_read=is_read,
                                              threat_level=threat_level, threat_type=threat_type,
                                              organization_id=organization_id))

        return list(map(actionable_alert_processing, raw_alerts))

    def get_actionable_alert(self, actionable_alert_id, organization_id=None):
        """
        This method queries the actionable alert info end point based on the actionable alert ID.
        :param actionable_alert_id: Actionable alert ID.
        :param organization_id: Organization ID.
        :return: returns the actionable alert info
        """
        info_response = self._send_request(
            SixgillSpecificActionableAlertGetRequest(channel_id=self.channel_id, access_token=self._get_access_token(),
                                                     actionable_alert_id=actionable_alert_id,
                                                     organization_id=organization_id))

        return actionable_alert_processing(info_response)

    def get_actionable_alert_content(self, actionable_alert_id, limit=100, highlight=False, organization_id=None,
                                     aggregate_alert_id=None, fetch_only_current_item=None):
        """
        Gets actionable alert content by alert ID
        :param actionable_alert_id: actionable alert ID
        :param limit: Number of actionable alerts [Default value : 100]
        :param highlight: highlight matched text [Default value : false]
        :param organization_id: For multi-tenant
        :param aggregate_alert_id:
        :param fetch_only_current_item: returns only the specific intel item [Default value : false]
        :return: returns the actionable alert content
        """
        raw_response = self._send_request(
            SixgillActionableAlertContentGetRequest(channel_id=self.channel_id, access_token=self._get_access_token(),
                                                    actionable_alert_id=actionable_alert_id, limit=limit,
                                                    highlight=highlight, organization_id=organization_id,
                                                    aggregate_alert_id=aggregate_alert_id,
                                                    fetch_only_current_item=fetch_only_current_item))
        alert_content = raw_response.get('content', {"items": [], "total": 0})

        return alert_content

    def update_actionable_alert(self, actionable_alert_id, json_body, organization_id=None, sub_alert_indexes=None):
        """
        This method is used update the actionable alert by id.
        :param actionable_alert_id: actionable alert ID
        :param json_body: updated fields data in a json format
        :param organization_id: required for multi-tenant
        :param sub_alert_indexes: sub alert indexes to update
        :return: updated actionable alert message with status code and actionable alert ID
        """
        raw_response = self._send_request(
            SixgillActionableAlertPatchRequest(channel_id=self.channel_id, access_token=self._get_access_token(),
                                               actionable_alert_id=actionable_alert_id, organization_id=organization_id,
                                               json_body=json_body, sub_alert_indexes=sub_alert_indexes))
        return raw_response

    def delete_actionable_alert(self, actionable_alert_ids, is_read=None, threat_level=None,
                                threat_type=None, organization_id=None):
        """
        This method is used delete the actionable alert by id.
        :param actionable_alert_ids: List of actionable alert ID(s)
        :param is_read: Filter by read, Available values - unread
        :param threat_level: Filter by alert threat level. One of the following[imminent, emerging]
        :param threat_type: Filter by field threat type
        :param organization_id: required for multi-tenant
        :return: empty response with status code 200
        """

        raw_response = self._send_request(
            SixgillActionableAlertsDeleteRequest(
                channel_id=self.channel_id,
                access_token=self._get_access_token(),
                actionable_alert_ids=actionable_alert_ids,
                organization_id=organization_id,
                is_read=is_read, threat_level=threat_level,
                threat_type=threat_type
            ))
        return raw_response
