from requests import codes


VALID_STATUS_CODES = [
    codes.ok,
    codes.created,
    codes.accepted,
    codes.non_authoritative_info,
    codes.no_content,
    codes.reset,
    codes.partial_content,
    codes.multi_status,
    codes.already_reported,
    codes.im_used
]


class FeedStream(object):
    DARKFEED = "darkfeed"
    DARKFEED_FREEMIUM = "darkfeed_freemium"
    DVEFEED = "dvefeed"