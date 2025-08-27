class TezaursError(Exception):
    """Vispārīga kļūda ar Tezaurs API."""

class TezaursJSONError(TezaursError):
    """Kļūda JSON parsēšanā."""

class TezaursNetworkError(TezaursError):
    """Tīkla kļūda, piekļūstot Tezaurs API."""

class TezaursTypeError(TezaursError):
    """Nepareizs parametra tips Tezaurs API wrapperī."""