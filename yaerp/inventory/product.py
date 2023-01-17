from .exception import InventoryError


class ProductError(InventoryError):
    def __init__(self, message):
        super().__init__(message)

class Product:
    pass

# Unique things: art work, services (one time projects)
# Identical things: books, toys
# Identifiable things: cars, services (slots in time), seats on flight
