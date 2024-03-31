from utils.exceptions import NotFoundError


class RecordNotFoundError(NotFoundError):
    def __str__(self):
        return 'Record not found.'


class ReadRecordDenied(PermissionError):
    def __str__(self):
        return 'Author does not have read_records permission.'


class InsertRecordDenied(PermissionError):
    def __str__(self):
        return 'Author does not have insert_records permission.'


class UpdateRecordDenied(PermissionError):
    def __str__(self):
        return 'Author does not have update_records permission.'


class DeleteRecordDenied(PermissionError):
    def __str__(self):
        return 'Author does not have delete_records permission.'
