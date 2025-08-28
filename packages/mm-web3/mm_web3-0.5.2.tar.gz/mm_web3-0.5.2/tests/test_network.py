from mm_web3 import Network

NETWORKS_COUNT = 19


def test_network():
    assert len(list(Network)) == NETWORKS_COUNT
    assert (
        len(Network.evm_networks())
        + len(Network.aptos_networks())
        + len(Network.solana_networks())
        + len(Network.starknet_networks())
        == NETWORKS_COUNT
    )
