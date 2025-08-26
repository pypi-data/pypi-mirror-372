from sixgill.sixgill_request_classes.sixgill_base_request import SixgillBaseRequest


class SixgillAuthRequest(SixgillBaseRequest):
    end_point = 'auth/token'
    method = 'POST'

    def __init__(self, client_id, client_secret, channel_id):
        super(SixgillAuthRequest, self).__init__(channel_id, data={})

        self.request.headers['Content-Type'] = 'application/x-www-form-urlencoded'
        self.request.data['client_id'] = client_id
        self.request.data['client_secret'] = client_secret
        self.request.data['grant_type'] = 'client_credentials'
