import logging


class Constants:
    """provides shared constants for logging"""

    DEFAULT_LOG_LEVEL = logging.INFO
    DEFAULT_LOG_AT_LEVEL = "INFO"

    LOG_AT_LEVEL = "log_at_level"
    LOG_LEVEL = "log_level"
    LOGGER_ERROR = "logger_error"

    ACTION_DURATION = "action_duration"
    ACTION_FIELD = "action"
    ACTION_STATUS = "action_status"
    ACTION_RESULT = "action_result"

    # The function executed successfully and completed the happy path
    STATUS_SUCCEEDED = "succeeded"
    # The function executed successfully but an expected error was thrown (e.g. a validation exception)
    STATUS_ERROR = "error"
    # The function raised an unexpected exception
    STATUS_FAILED = "failed"

    LOG_REFERENCE_FIELD = "log_reference"
    LOG_REFERENCE_ON_ERR_FIELD = "log_reference_on_error"
    LOG_CORRELATION_ID_FIELD = "internal_id"
    TIMESTAMP_FIELD = "timestamp"
    TRACEBACK_FIELD = "traceback"
    EXCEPTION_FIELD = "exception"
    LOG_INFO = "log_info"
    STACK_INFO = "stack_info"

    MESSAGE_TYPE_FIELD = "message_type"
    REASON_FIELD = "reason"
    EXPECTED_ERRORS = "expected_errors"
    ERROR_LEVELS = "error_levels"
    REDACT_FIELDS = "redact_fields"
    DONT_REDACT = "dont_redact"

    EXC_INFO = "exc_info"

    ERROR_INFO_FIELD = "error_info"
    CALLER_INFO_FIELD = "caller_info"
    ERROR_FIELD = "error"
    ERROR_TYPE = "type"
    ERROR_FULLY_QUALIFIED_TYPE = "fq_type"
    ERROR_PROPERTIES_FIELD = "props"
    ERROR_ARGS = "args"
    INCLUDE_TRACEBACK = "include_traceback"
