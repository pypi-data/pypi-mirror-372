from sixgill.sixgill_base_client import SixgillBaseClient
from sixgill.sixgill_request_classes.sixgill_unfiltered_field_enrich_request import SixgillUnfilteredFieldEnrichRequest
from sixgill.sixgill_request_classes.sixgill_unfiltered_ioc_enrich_request import SixgillUnfilteredIOCEnrichRequest


class SixgillUnfilteredEnrichClient(SixgillBaseClient):

    def __init__(self, client_id, client_secret, channel_id, logger=None, session=None,
                 verify=False, num_of_attempts=5):
        super(SixgillUnfilteredEnrichClient, self).__init__(client_id=client_id, client_secret=client_secret,
                                                            channel_id=channel_id, logger=logger, session=session,
                                                            verify=verify, num_of_attempts=num_of_attempts)

    def enrich_postid(self, sixgill_field_value, limit=50, from_date=None, to_date=None, skip=0):
        """This method queries the enrich end point based on the sixgill post id and returns the result set

        Arguments:
            sixgill_field_value - parameter value of the 'sixgill_field_value - post id'
            skip - No. of indicators which need to be skipped while returning the result set
            limit - No. of indicators to be return
            from_date -
            to_date -
        Returns:
            enrich_data -- Returns the list of result set
        """
        return self._enrich_feed("post_id", sixgill_field_value, limit, from_date, to_date, skip)

    def enrich_actor(self, sixgill_field_value, limit=50, from_date=None, to_date=None, skip=0):
        """This method queries the enrich end point based on the sixgill actor and returns the result set

        Arguments:
            sixgill_field_value - parameter value of the 'sixgill_field_value -  - post actor'
            skip - No. of indicators which need to be skipped while returning the result set
            limit - No. of indicators to be return
            from_date -
            to_date -
        Returns:
            enrich_data -- Returns the list of result set
        """
        return self._enrich_feed("actor", sixgill_field_value, limit, from_date, to_date, skip)

    def enrich_ioc(self, ioc_type, ioc_value, skip=0, limit=50, from_date=None, to_date=None):
        """This method queries the enrich end point based on the sixgill actor and returns the result set

        Arguments:
            ioc_type - parameter value of the 'ioc_type - ip, url, domain, hash'
            ioc_value - parameter value of the 'ioc_value'
            skip - No. of indicators which need to be skipped while returning the result set
            limit - No. of indicators to be return
            from_date -
            to_date -
        Returns:
            enrich_data -- Returns the list of result set
        """
        enrich_feed = self._send_request(
            SixgillUnfilteredIOCEnrichRequest(self.channel_id, self._get_access_token(), ioc_type, ioc_value,
                                              from_date, to_date, skip, limit))
        enrich_data = enrich_feed.get("items")
        return enrich_data

    def _enrich_feed(self, sixgill_field, sixgill_field_value, limit, from_date, to_date, skip):
        """This method queries the enrich end point based on the sixgill actor or sixgill post id and returns the result set

        Arguments:
            sixgill_field - parameter value of the 'sixgill_field'
            sixgill_field_value - parameter value of the 'sixgill_field_value'
            limit - No. of indicators to be return
            from_date -
            to_date -
            skip - No. of indicators which need to be skipped while returning the result set
        Returns:
            enrich_data -- Returns the list of result set
        """
        enrich_feed = self._send_request(
            SixgillUnfilteredFieldEnrichRequest(self.channel_id, self._get_access_token(), sixgill_field,
                                                sixgill_field_value, from_date, to_date, skip, limit))
        enrich_data = enrich_feed.get("items")
        return enrich_data
