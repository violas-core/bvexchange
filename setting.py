##bvexchange config
#
from tomlbase import tomlbase

class tomlopt(tomlbase):
    def __init__(self, tomlfile):
        super().__init__(tomlfile)

setting = tomlopt("bvexchange.toml")

