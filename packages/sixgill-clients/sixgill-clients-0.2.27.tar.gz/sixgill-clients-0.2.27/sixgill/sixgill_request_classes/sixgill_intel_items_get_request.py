from sixgill.sixgill_request_classes.sixgill_base_post_auth_request import SixgillBasePostAuthRequest


class SixgillIntelItemsGetRequest(SixgillBasePostAuthRequest):
    end_point = 'intel/intel_items'
    method = 'GET'

    def __init__(self, channel_id, access_token, query, results_size, highlight, custom_highlight_start_tag,
                 custom_highlight_end_tag, recent_items):
        super(SixgillIntelItemsGetRequest, self).__init__(channel_id, access_token)

        self.request.params['query'] = query
        params_dict = {'results_size': results_size, 'highlight': highlight,
                       'custom_highlight_start_tag': custom_highlight_start_tag,
                       'custom_highlight_end_tag': custom_highlight_end_tag, 'recent_items': recent_items}
        filtered_params_dict = {param_k: param_v for param_k, param_v in params_dict.items() if param_v is not None}

        self.request.params.update(**filtered_params_dict)

