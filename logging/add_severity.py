import logging

# https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry#logseverity
SEVERITY_LEVELS = {
    "DEBUG": 100,
    "INFO": 200,
    "WARNING": 400,
    "ERROR": 500,
    "CRITICAL": 600,
}


class AddGaeSeverityLevel(logging.Filter):
    def filter(self, record):
        record.severity = SEVERITY_LEVELS[record.levelname]
        return True
