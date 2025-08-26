from sixgill.sixgill_base_client import SixgillBaseClient
from sixgill.sixgill_request_classes.sixgill_intel_items_get_request import SixgillIntelItemsGetRequest
from sixgill.sixgill_request_classes.sixgill_intel_items_post_request import SixgillIntelItemsPostRequest
from sixgill.sixgill_request_classes.sixgill_next_batch_intel_items_request import SixgillNextBatchIntelItemsRequest


class SixgillIntelItemsClient(SixgillBaseClient):

    def __init__(self, client_id, client_secret, channel_id, logger=None, session=None, verify=False,
                 num_of_attempts=5):
        super(SixgillIntelItemsClient, self).__init__(client_id=client_id, client_secret=client_secret,
                                                      channel_id=channel_id, logger=logger,
                                                      session=session, verify=verify,
                                                      num_of_attempts=num_of_attempts)

    def get_intel_items(self, query, results_size=None, highlight=None, custom_highlight_start_tag=None,
                        custom_highlight_end_tag=None, recent_items=None):
        """
        This method gets the list of intel items based on search query.
        :param query: A search query for requesting data.
        :param results_size: The amount of intel items in the results.(default is 50)
        :param highlight: Set to true to highlight the query string in the results.(default is False)
        :param custom_highlight_start_tag: text will mark the start of a highlighted (default is @sixgill-start-highlight@ )
        :param custom_highlight_end_tag: text will mark the end of a highlighted (default is @sixgill-end-highlight@ )
        :param recent_items: if set to true retrieve data from last 2 days.(default is False)
        :return: list of intel items
        """
        intel_items = self._send_request(
            SixgillIntelItemsGetRequest(channel_id=self.channel_id, access_token=self._get_access_token(), query=query,
                                        results_size=results_size, highlight=highlight,
                                        custom_highlight_start_tag=custom_highlight_start_tag,
                                        custom_highlight_end_tag=custom_highlight_end_tag, recent_items=recent_items))

        return intel_items.get('intel_items', [])

    def advanced_intel_items(self, query, date_range=None, filters=None, highlight=None, partial_content=None,
                             results_size=None, scroll=None, sort=None, sort_type=None, safe_content_size=False,
                             from_value=0, custom_highlight_start_tag=None, custom_highlight_end_tag=None,
                             recent_items=False):
        """
        This method gets Intel items based on search query -Advanced Variation
        :param query: A search query for requesting data.
        :param date_range: Items that were collected between two dates (UTC)
        :param filters: Options for filtering a query
        :param highlight: Set to true to highlight the query string in the results.(default is False)
        :param partial_content: Specifies the number of chars relating to the content (default is True)
        :param results_size: The amount of items in the aggregation field. Each field item in the aggregation includes an occurrence count. (default is 50)
        :param scroll: you can further filter the data fetched by this endpoint. The scroll_id is used as a value in the intel_items/next (default is True)
        :param sort: Sort the results by the field specified
        :param sort_type: Sets the sort order for the fetched results (default is desc)
        :param safe_content_size: False
        :param from_value: 0
        :param custom_highlight_start_tag:
        :param custom_highlight_end_tag:
        :param recent_items: False
        :return: list of intel items
        """

        return self._send_request(
            SixgillIntelItemsPostRequest(channel_id=self.channel_id, access_token=self._get_access_token(), query=query,
                                         date_range=date_range, filters=filters, highlight=highlight,
                                         partial_content=partial_content, results_size=results_size, scroll=scroll,
                                         sort=sort, sort_type=sort_type, safe_content_size=safe_content_size,
                                         from_value=from_value, custom_highlight_start_tag=custom_highlight_start_tag,
                                         custom_highlight_end_tag=custom_highlight_end_tag, recent_items=recent_items))

    def next_batch_intel_items(self, scroll_id, recent_items=False):
        """
        Get the next batch of intel items by a given scroll_id.
        :param scroll_id: returned from intel_items (post).
        :param recent_items:
        :return: list of intel items
        """

        return self._send_request(
            SixgillNextBatchIntelItemsRequest(channel_id=self.channel_id, access_token=self._get_access_token(),
                                              scroll_id=scroll_id, recent_items=recent_items))
