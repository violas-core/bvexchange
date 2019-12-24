
class LegalTender:
    USD = "001"

    @classmethod
    def to_name(cls, value):
        for k, v in cls.__dict__:
            if value == v:
                return k
        return None