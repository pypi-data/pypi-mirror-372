class AddressService:
    ADDRESS_TYPES = ["service", "invoice", "delivery", "other"]

    def __init__(self, env, address):
        """
        TODO: Please, remove the `or "-"` when the data had been fixed.
        """
        self.street = address.street or "-"
        self.zip_code = address.zip or "-"
        self.city = address.city or "-"
        self.country = address.country_id.name or env.ref("base.es").name
        self.state = address.state_id.name or "-"

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__hash__() == other.__hash__()

    def _normalized_dict(self):
        normalized_dict = {}
        for k, v in self.__dict__.items():
            normalized_dict[k] = v.lower().strip()
        return normalized_dict

    def __hash__(self):
        return hash(str(self._normalized_dict()))
