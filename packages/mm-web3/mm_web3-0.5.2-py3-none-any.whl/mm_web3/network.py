"""Network types and utilities for different blockchain networks."""

from __future__ import annotations

from enum import StrEnum, unique


@unique
class NetworkType(StrEnum):
    """Base network types (EVM, Solana, etc)."""

    EVM = "evm"
    SOLANA = "solana"
    APTOS = "aptos"
    STARKNET = "starknet"

    def lowercase_address(self) -> bool:
        """Whether addresses for this network type should be lowercase."""
        match self:
            case NetworkType.EVM:
                return True
            case NetworkType.SOLANA:
                return False
            case NetworkType.APTOS:
                return True
            case NetworkType.STARKNET:
                return True
        raise ValueError("no network found")


@unique
class Network(StrEnum):
    """Blockchain networks"""

    APTOS = "aptos"
    ARBITRUM_ONE = "arbitrum-one"
    AVAX_C = "avax-c"
    BASE = "base"
    BSC = "bsc"
    CELO = "celo"
    CORE = "core"
    ETHEREUM = "ethereum"
    FANTOM = "fantom"
    LINEA = "linea"
    OPBNB = "opbnb"
    OP_MAINNET = "op-mainnet"
    POLYGON = "polygon"
    POLYGON_ZKEVM = "polygon-zkevm"
    SCROLL = "scroll"
    SOLANA = "solana"
    STARKNET = "starknet"
    ZKSYNC_ERA = "zksync-era"
    ZORA = "zora"

    @property
    def network_type(self) -> NetworkType:
        """Get the base network type (EVM, Solana, etc)."""
        if self in self.evm_networks():
            return NetworkType.EVM
        if self in self.solana_networks():
            return NetworkType.SOLANA
        if self in self.aptos_networks():
            return NetworkType.APTOS
        if self in self.starknet_networks():
            return NetworkType.STARKNET
        raise ValueError("no network found")

    def explorer_token(self, token: str) -> str:
        """Get explorer URL for a token address."""
        match self:
            case Network.ARBITRUM_ONE:
                return f"https://arbiscan.io/token/{token}"
            case Network.AVAX_C:
                return f"https://snowtrace.io/token/{token}"
            case Network.APTOS:
                return f"https://explorer.aptoslabs.com/coin/{token}"
            case Network.BASE:
                return f"https://basescan.org/token/{token}"
            case Network.BSC:
                return f"https://bscscan.com/token/{token}"
            case Network.CELO:
                return f"https://celoscan.io/token/{token}"
            case Network.CORE:
                return f"https://scan.coredao.org/token/{token}"
            case Network.ETHEREUM:
                return f"https://etherscan.io/token/{token}"
            case Network.FANTOM:
                return f"https://ftmscan.com/token/{token}"
            case Network.LINEA:
                return f"https://lineascan.build/token/{token}"
            case Network.OPBNB:
                return f"https://opbnbscan.com/token/{token}"
            case Network.OP_MAINNET:
                return f"https://optimistic.etherscan.io/token/{token}"
            case Network.POLYGON:
                return f"https://polygonscan.com/token/{token}"
            case Network.POLYGON_ZKEVM:
                return f"https://zkevm.polygonscan.com/token/{token}"
            case Network.SCROLL:
                return f"https://scrollscan.com/token/{token}"
            case Network.SOLANA:
                return f"https://solscan.io/token/{token}"
            case Network.STARKNET:
                return f"https://voyager.online/token/{token}"
            case Network.ZKSYNC_ERA:
                return f"https://explorer.zksync.io/token/{token}"
            case Network.ZORA:
                return f"https://explorer.zora.energy/tokens/{token}"

        raise ValueError("no network found")

    def explorer_account(self, account: str) -> str:
        """Get explorer URL for an account address."""
        match self:
            case Network.ARBITRUM_ONE:
                return f"https://arbiscan.io/address/{account}"
            case Network.AVAX_C:
                return f"https://snowtrace.io/address/{account}"
            case Network.APTOS:
                return f"https://explorer.aptoslabs.com/account/{account}"
            case Network.BASE:
                return f"https://basescan.org/address/{account}"
            case Network.BSC:
                return f"https://bscscan.com/address/{account}"
            case Network.CELO:
                return f"https://celoscan.io/address/{account}"
            case Network.CORE:
                return f"https://scan.coredao.org/address/{account}"
            case Network.ETHEREUM:
                return f"https://etherscan.io/address/{account}"
            case Network.FANTOM:
                return f"https://ftmscan.com/address/{account}"
            case Network.LINEA:
                return f"https://lineascan.build/address/{account}"
            case Network.OPBNB:
                return f"https://opbnbscan.com/address/{account}"
            case Network.OP_MAINNET:
                return f"https://optimistic.etherscan.io/address/{account}"
            case Network.POLYGON:
                return f"https://polygonscan.com/address/{account}"
            case Network.POLYGON_ZKEVM:
                return f"https://zkevm.polygonscan.com/address/{account}"
            case Network.SCROLL:
                return f"https://scrollscan.com/address/{account}"
            case Network.SOLANA:
                return f"https://solscan.io/account/{account}"
            case Network.ZKSYNC_ERA:
                return f"https://explorer.zksync.io/address/{account}"
            case Network.STARKNET:
                return f"https://voyager.online/contract/{account}"
            case Network.ZORA:
                return f"https://explorer.zora.energy/address/{account}"

        raise ValueError("no network found")

    @classmethod
    def evm_networks(cls) -> list[Network]:
        """Get list of all EVM-compatible networks."""
        return [
            Network.ARBITRUM_ONE,
            Network.AVAX_C,
            Network.BASE,
            Network.BSC,
            Network.CELO,
            Network.CORE,
            Network.ETHEREUM,
            Network.FANTOM,
            Network.LINEA,
            Network.OPBNB,
            Network.OP_MAINNET,
            Network.POLYGON,
            Network.POLYGON_ZKEVM,
            Network.SCROLL,
            Network.ZKSYNC_ERA,
            Network.ZORA,
        ]

    @classmethod
    def solana_networks(cls) -> list[Network]:
        """Get list of all Solana networks."""
        return [Network.SOLANA]

    @classmethod
    def aptos_networks(cls) -> list[Network]:
        """Get list of all Aptos networks."""
        return [Network.APTOS]

    @classmethod
    def starknet_networks(cls) -> list[Network]:
        """Get list of all Starknet networks."""
        return [Network.STARKNET]
