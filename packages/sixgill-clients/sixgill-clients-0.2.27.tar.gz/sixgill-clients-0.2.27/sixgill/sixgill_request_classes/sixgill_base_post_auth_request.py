from abc import ABCMeta
from sixgill.sixgill_request_classes.sixgill_base_request import SixgillBaseRequest


class SixgillBasePostAuthRequest(SixgillBaseRequest):
    __metaclass__ = ABCMeta

    def __init__(self, channel_id, access_token, *args, **kwargs):
        super(SixgillBasePostAuthRequest, self).__init__(channel_id, *args, **kwargs)

        self.request.headers['Content-Type'] = 'application/json'
        self.request.headers['Authorization'] = 'Bearer {}'.format(access_token)
