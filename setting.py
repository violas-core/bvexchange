##bvexchange config
#
from tomlbase import tomlbase

class tomlopt(tomlbase):
    def __init__(self, tomlfile):
        super().__init__(tomlfile)

    def __getattr__(self, name):
        return None

    def type_token_filter(self, etype = None):
        supports = {}
        assert etype in (None, "swap", "map"), \
                f"etype({etype}) is invalid. valid values(None, map, swap)"
        for key, opts in self.type_opts.items():
            support_state = opts.get("support", True)
            support_etype = opts.get("etype", "swap")
            if support_state == True and etype in (None, support_etype):
                supports.update({key:opts})

        return supports

    @property
    def type_token(self):
        return self.type_token_filter()

    @property
    def type_token_swap(self):
        return self.type_token_filter("swap")

    @property
    def type_token_map(self):
        return self.type_token_filter("map")
setting = tomlopt("bvexchange.toml")

