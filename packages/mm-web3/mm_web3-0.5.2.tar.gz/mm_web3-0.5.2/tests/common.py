import eth_utils
from eth_account import Account

TEST_ETH_PRIVATE_KEYS = {
    "0xB630F2b4980cf98Cf956A5E3663d3596cF802Fb8": "0x40e9bae075a3e3c587cccbda8fb7586b8b3fb2bb53669283adaf2ee41e56fc28",
    "0x0dBcBFb8F189e5364eF98c0Aa977f6854E32E26e": "0xe459bc004d18007a0218f93a18c301bbca411b2a6b89c2e405956598a1951836",
    "0xE77d179D074987c154033a3d7E34BdDd81C6c241": "0xa1a3abf8bb63322966aef18b956e02bbcf8d39fd3e59828f9582ea06ade58423",
    "0xbe2a25ccbc4e7a47f2589B61D3677Bc233bc4EC3": "0x1d33a9c4e6df23becfa72d9d596c91f3a6baa3b6407cb31fb683bc8a2dbe4071",
    "0x02F5ceF52949f6Ebf84361929Ebd93a6AFc3bAEC": "0x8883570deeee160e1af6a128c5c357ea6ece641065e69833ea4ae30a7d56e9f1",
}


def eth_private_to_address(private_key: str) -> str:
    """Convert Ethereum private key to address."""
    account = Account.from_key(private_key)
    return account.address


def eth_is_valid_address(address: str) -> bool:
    """Check if the given Ethereum address is valid."""
    return eth_utils.address.is_address(address)
