import logging


def streamify(batch_func):
    def streamify_wrapper(*args, **kwargs):
        batch = batch_func(*args, **kwargs)
        while batch:
            for indicator in batch:
                yield indicator
            batch = batch_func(*args, **kwargs)

    return streamify_wrapper


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s %(levelname)s: %(message)s [in %(filename)s:%(lineno)d]")
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.setLevel(logging.DEBUG)
    return logger


def is_darkfeed_indicator(indicator):
    return "indicator" == indicator.get("type", "")


def is_cvefeed_indicator(indicator):
    return "x-cybersixgill-com-cve-event" == indicator.get("type", "")


def is_indicator(indicator):
    return is_darkfeed_indicator(indicator) or is_cvefeed_indicator(indicator)


def actionable_alert_processing(alert):
    if 'id' not in alert:
        alert['id'] = alert.get('alert_id', '')
    if 'title' not in alert:
        alert['title'] = alert.get('alert_title', '')
    if 'es_id' in alert or "intel_item_id" in alert:
        alert['es_id'] = alert.get('es_id') or alert.get('intel_item_id')
    if 'es_item' in alert or "intel_item_content" in alert:
        alert['es_item'] = alert.get('es_item') or alert.get('intel_item_content')

    return alert
