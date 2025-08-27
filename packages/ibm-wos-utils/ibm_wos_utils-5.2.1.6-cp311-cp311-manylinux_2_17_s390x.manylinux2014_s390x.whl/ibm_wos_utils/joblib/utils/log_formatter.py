import re

SENSITIVE_FIELDS = ["metastore_url", "username",
                    "password", "certificate", "apikey", "delegation_token_urn", "ae.spark.remoteHadoop.delegationToken",
                    "credentials", "service_provider_credentials",
                    "access_key_id", "secret_access_key",
                    "token", "secondaryKey",
                    "client_id", "client_secret", "tenant",
                    "zen_service_broker_secret", "uid", "api_key", "scored_perturbations",
                    "training_statistics"
                    ]
MASK_STRING = "\"***\""

class SensitiveDataFormatter(object):
    """
    Custom formatter for logging to mask sensitive fields
    """

    def __init__(self, orig_formatter, fields=None):
        self.orig_formatter = orig_formatter
        self.fields = fields

    def format(self, record):
        message = self.orig_formatter.format(record)
        # Mask sensitive fields in the message
        fields_to_mask = SENSITIVE_FIELDS
        if self.fields:
            fields_to_mask = SENSITIVE_FIELDS + self.fields
        message = self.mask_sensitive_fields(message, fields_to_mask)
        return message

    def mask_sensitive_fields(self, message: str, fields_to_mask: list):
        if message and fields_to_mask:
            for field in fields_to_mask:
                if field in message:
                    # Check if log message contains sensitive fields in the format 'field': 'sensitive_value' or 'field': {sensitive_value_dict}
                    # If found, replace the value with mask characters like 'field': '***'
                    pattern = "['\"]?{}['\"]?\s*[:-=\s]\s*(['\"][^'\"]*['\"]|{{[^}}]*}})".format(
                        field)
                    matches = re.findall(pattern, message)
                    for match in matches:
                        if match:
                            if match.startswith('"'):
                                replace_str = MASK_STRING
                            else:
                                replace_str = "\'***\'"
                        message = message.replace(match, replace_str)
        return message

    def __getattr__(self, attr):
        return getattr(self.orig_formatter, attr)
