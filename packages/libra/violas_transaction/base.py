import json

def type_mapping(value):
    if isinstance(value, ViolasBase):
        value = value.to_json()
    elif isinstance(value, list):
        value = [type_mapping(v) for v in value]
    elif isinstance(value, dict):
        value = { k : type_mapping(v) for k, v in value.items() }
    return value

class ViolasBase:
    def to_json(self):
        return { k : type_mapping(v) for k, v in self.__dict__.items() }

    def __str__(self):
        return json.dumps(self.to_json())

    @staticmethod
    def int_list_to_hex(ints):
        return bytes(ints).hex()