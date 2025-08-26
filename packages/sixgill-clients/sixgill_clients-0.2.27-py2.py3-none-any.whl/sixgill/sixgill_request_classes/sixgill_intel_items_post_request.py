from sixgill.sixgill_request_classes.sixgill_base_post_auth_request import SixgillBasePostAuthRequest


class SixgillIntelItemsPostRequest(SixgillBasePostAuthRequest):
    end_point = None
    method = 'POST'

    def __init__(self, channel_id, access_token, query, date_range, filters, highlight, partial_content, results_size,
                 scroll, sort, sort_type, safe_content_size, from_value, custom_highlight_start_tag,
                 custom_highlight_end_tag, recent_items):
        super(SixgillIntelItemsPostRequest, self).__init__(channel_id, access_token)

        self.end_point = 'intel/intel_items'
        self.request.headers['Content-Type'] = 'application/json'
        self.request.json = {'query': query}
        json_dict = {'date_range': date_range, 'filters': filters, 'highlight': highlight,
                     'partial_content': partial_content, 'results_size': results_size, 'scroll': scroll, 'sort': sort,
                     'sort_type': sort_type, 'safe_content_size': safe_content_size, 'from': from_value,
                     'custom_highlight_start_tag': custom_highlight_start_tag,
                     'custom_highlight_end_tag': custom_highlight_end_tag, 'recent_items': recent_items}
        filtered_json_dict = {key: value for key, value in json_dict.items() if value is not None}

        self.request.json.update(**filtered_json_dict)
