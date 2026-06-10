from .rotate_parser import setup_logger
from .log_param import FIELD_GROUPS, LOGGER_SCHEMAS, SECURITY_EVENTS


# =========================================================
# COMPOSER
# =========================================================

def compose_fields(*groups):

    fields = []

    for group in groups:
        fields.extend(FIELD_GROUPS.get(group, []))

    return list(dict.fromkeys(fields))


# =========================================================
# FIELDS
# =========================================================

APP_FIELDS = compose_fields(*LOGGER_SCHEMAS["APP"])

ACCESS_FIELDS = compose_fields(*LOGGER_SCHEMAS["ACCESS"])

SECURITY_FIELDS = compose_fields(*LOGGER_SCHEMAS["SECURITY"])


# =========================================================
# SECURITY LOGGER HELPER
# =========================================================

def security_event(event_name, message=None):

    event = SECURITY_EVENTS.get(event_name)

    if not event:
        security_logger.warning(f"UNKNOWN_SECURITY_EVENT: {event_name}")
        return

    security_logger.warning(
        message or event_name,
        extra=event,
    )


# =========================================================
# LOGGERS
# =========================================================

app_logger = setup_logger(
    logger_name="APP",
    fields=APP_FIELDS,
)

access_logger = setup_logger(
    logger_name="ACCESS",
    fields=ACCESS_FIELDS,
)

security_logger = setup_logger(
    logger_name="SECURITY",
    fields=SECURITY_FIELDS,
)
