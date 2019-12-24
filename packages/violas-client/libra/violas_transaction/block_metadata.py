from libra.block_metadata import BlockMetadata

from libra.violas_transaction import ViolasBase, ViolasTransactionInfo, ViolasContractEvent

class ViolasBlockMetadata(ViolasBase):
    def __init__(self, metadata:BlockMetadata, version, info, events=[] ):
        self.id = self.int_list_to_hex(metadata.id)
        self.timestamp_usec = metadata.timestamp_usec
        self.previous_block_votes = {}
        for key, value in metadata.previous_block_votes.items():
            self.previous_block_votes[key.hex()] = self.int_list_to_hex(value)
        self.proposer = self.int_list_to_hex(metadata.proposer)

        self.version = version
        self.info = ViolasTransactionInfo(info)
        self.success = info.major_status == 4001
        self.events = [ ViolasContractEvent(e)for e in events ]

    def get_index(self):
        return 2

    def get_version(self):
        return self.version

    def get_info(self):
        return self.info

