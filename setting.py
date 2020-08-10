##bvexchange config
#
from tomlbase import tomlbase

class tomlopt(tomlbase):
    def __init__(self, tomlfile):
        super().__init__(tomlfile)

    @property
    def type_token(self):
        supports = {}
        for key, opts in self.type_opts.items():
            support_state = opts.get("support", "true")
            if support_state.lower() == "true":
                supports.update({key:opts})

        return supports


setting = tomlopt("bvexchange.toml")

