from utils.exceptions import NotFoundError


class RarityNotFoundError(NotFoundError):
    def __str__(self):
        return 'Rarity not found.'


class ReadRarityDenied(PermissionError):
    def __str__(self):
        return 'Author does not have read_rarities permission.'


class InsertRarityDenied(PermissionError):
    def __str__(self):
        return 'Author does not have insert_rarities permission.'


class UpdateRarityDenied(PermissionError):
    def __str__(self):
        return 'Author does not have update_rarities permission.'


class DeleteRarityDenied(PermissionError):
    def __str__(self):
        return 'Author does not have delete_rarities permission.'
