from sixgill.sixgill_base_client import SixgillBaseClient
from sixgill.sixgill_request_classes.sixgill_field_enrich_request import SixgillFieldEnrichRequest
from sixgill.sixgill_request_classes.sixgill_ioc_enrich_request import SixgillIOCEnrichRequest
from sixgill.sixgill_request_classes.sixgill_dve_enrich_request import SixgillDVEEnrichRequest
from sixgill.sixgill_request_classes.sixgill_dve_remediation_request import SixgillDVEEnrichRemediationRequest

MAX_ENRICH_SIZE = 9950

class SixgillEnrichClient(SixgillBaseClient):

    def __init__(self, client_id, client_secret, channel_id, logger=None, session=None,
                 verify=False, num_of_attempts=5):
        super(SixgillEnrichClient, self).__init__(client_id=client_id, client_secret=client_secret,
                                                  channel_id=channel_id, logger=logger, session=session,
                                                  verify=verify, num_of_attempts=num_of_attempts)

    def enrich_postid(self, sixgill_field_value, skip=0):
        """This method queries the enrich end point based on the sixgill post id and returns the result set

        Arguments:
            sixgill_field_value - parameter value of the 'sixgill_field_value - post id'
            skip - No. of indicators which need to be skipped while returning the result set
        Returns:
            enrich_data -- Returns the list of result set
        """
        return self._enrich_feed("post_id", sixgill_field_value, skip)

    def enrich_actor(self, sixgill_field_value, skip=0):
        """This method queries the enrich end point based on the sixgill actor and returns the result set

        Arguments:
            sixgill_field_value - parameter value of the 'sixgill_field_value -  - post actor'
            skip - No. of indicators which need to be skipped while returning the result set
        Returns:
            enrich_data -- Returns the list of result set
        """
        return self._enrich_feed("actor", sixgill_field_value, skip)

    def enrich_ioc(self, ioc_type, ioc_value, skip=0):
        """This method queries the enrich end point based on the sixgill actor and returns the result set

        Arguments:
            ioc_type - parameter value of the 'ioc_type - ip, url, domain, hash'
            ioc_value - parameter value of the 'ioc_value'
            skip - No. of indicators which need to be skipped while returning the result set
        Returns:
            enrich_data -- Returns the list of result set
        """
        enrich_data = []
        enrich_ioc_count = 1
        while enrich_ioc_count > 0 and skip <= MAX_ENRICH_SIZE:
            enrich_feed = self._send_request(
                SixgillIOCEnrichRequest(self.channel_id, self._get_access_token(), ioc_type,
                                        ioc_value, skip))
            items = enrich_feed.get("items")
            enrich_data.extend(items)
            skip += len(items)
            enrich_ioc_count = enrich_feed.get("total") - skip
        return enrich_data

    def enrich_dve(self, cve_id):
        """
        This method queries the cve_enrich endpoint based on the cve_id and returns the result set
        :param cve_id: parameter value of the cve_id Example: CVE-2020-1234
        :type cve_id: string
        Returns: enrich_data -- Returns the dictionary of cve enrich data
        """
        cve_enriched_data = self._send_request(
            SixgillDVEEnrichRequest(self.channel_id, self._get_access_token(), cve_id))
        return cve_enriched_data

    def enrich_dve_remediation(self, cve_id):
        """
        This method queries the cve_remediation endpoint based on the cve_id and returns the result set
        :param cve_id: parameter value of the cve_id Example: CVE-2020-1234
        :type cve_id: string
        Returns: enrich_data -- Returns the dictionary of cve remediation data
        """
        cve_enriched_data = self._send_request(
            SixgillDVEEnrichRemediationRequest(self.channel_id, self._get_access_token(), cve_id))
        return cve_enriched_data

    def _enrich_feed(self, sixgill_field, sixgill_field_value, skip):
        """This method queries the enrich end point based on the sixgill actor or sixgill post id and returns the result set

        Arguments:
            sixgill_field - parameter value of the 'sixgill_field'
            sixgill_field_value - parameter value of the 'sixgill_field_value'
            skip - No. of indicators which need to be skipped while returning the result set
        Returns:
            enrich_data -- Returns the list of result set
        """
        enrich_data = []
        enrich_count = 1
        while enrich_count > 0 and skip <= MAX_ENRICH_SIZE:
            enrich_feed = self._send_request(
                SixgillFieldEnrichRequest(self.channel_id, self._get_access_token(), sixgill_field,
                                          sixgill_field_value, skip))
            items = enrich_feed.get("items")
            enrich_data.extend(items)
            skip += len(items)
            enrich_count = enrich_feed.get("total") - skip
        return enrich_data
