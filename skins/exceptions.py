from utils.exceptions import NotFoundError


class SkinNotFoundError(NotFoundError):
    def __str__(self):
        return 'Skin not found.'


class ReadSkinDenied(PermissionError):
    def __str__(self):
        return 'Author does not have read_skins permission.'


class InsertSkinDenied(PermissionError):
    def __str__(self):
        return 'Author does not have insert_skins permission.'


class UpdateSkinDenied(PermissionError):
    def __str__(self):
        return 'Author does not have update_skins permission.'


class DeleteSkinDenied(PermissionError):
    def __str__(self):
        return 'Author does not have delete_skins permission.'
