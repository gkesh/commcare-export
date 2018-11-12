class DataExportException(Exception):
    message = None


class LongFieldsException(DataExportException):
    def __init__(self, long_fields, max_length):
        self.long_fields = long_fields
        self.max_length = max_length

    @property
    def message(self):
        message = ''
        for table, headers in self.long_fields.items():
            message += (
                'Table "{}" has field names longer than the maximum allowed for this database ({}):\n'.format(
                table, self.max_length
            ))
            for header in headers:
                message += '    {}\n'.format(header)

        message += '\nPlease adjust field names to be within the maximum length limit of {}'.format(self.max_length)
        return message


class MissingColumnException(DataExportException):
    def __init__(self, errors_by_sheet):
        self.errors_by_sheet = errors_by_sheet

    @property
    def message(self):
        lines = [
            'Table "{}" is missing required columns: "{}"'.format(
                sheet, '", "'.join(missing_cols)
            ) for sheet, missing_cols in self.errors_by_sheet.items()
        ]
        return '\n'.join(lines)
