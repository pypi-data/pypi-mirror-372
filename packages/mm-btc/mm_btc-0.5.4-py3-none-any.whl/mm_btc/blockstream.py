from collections.abc import Sequence

from mm_http import HttpResponse, http_request
from mm_result import Result
from mm_web3 import random_proxy
from pydantic import BaseModel

MAINNET_BASE_URL = "https://blockstream.info/api"
TESTNET_BASE_URL = "https://blockstream.info/testnet/api"

# ERROR_INVALID_ADDRESS = "INVALID_ADDRESS"
# ERROR_INVALID_NETWORK = "INVALID_NETWORK"

ERROR_400_BAD_REQUEST = "400 Bad Request"

type Proxy = str | Sequence[str] | None


class Mempool(BaseModel):
    count: int
    vsize: int
    total_fee: int
    fee_histogram: list[tuple[float, int]]


class Address(BaseModel):
    class ChainStats(BaseModel):
        funded_txo_count: int
        funded_txo_sum: int
        spent_txo_count: int
        spent_txo_sum: int
        tx_count: int

    class MempoolStats(BaseModel):
        funded_txo_count: int
        funded_txo_sum: int
        spent_txo_count: int
        spent_txo_sum: int
        tx_count: int

    chain_stats: ChainStats
    mempool_stats: MempoolStats


class Utxo(BaseModel):
    class Status(BaseModel):
        confirmed: bool
        block_height: int
        block_hash: str
        block_time: int

    txid: str
    vout: int
    status: Status
    value: int


class BlockstreamClient:
    def __init__(self, testnet: bool = False, timeout: float = 5, proxies: Proxy = None, attempts: int = 1) -> None:
        self.testnet = testnet
        self.timeout = timeout
        self.proxies = proxies
        self.attempts = attempts
        self.base_url = TESTNET_BASE_URL if testnet else MAINNET_BASE_URL

    async def get_address(self, address: str) -> Result[Address]:
        result: Result[Address] = Result.err("not started yet")
        for _ in range(self.attempts):
            res = await self._request(f"/address/{address}")
            try:
                if res.status_code == 400:
                    return res.to_result_err("400 Bad Request")
                return res.to_result_ok(Address(**res.parse_json_body()))
            except Exception as e:
                result = res.to_result_err(e)
        return result

    async def get_confirmed_balance(self, address: str) -> Result[int]:
        return (await self.get_address(address)).chain(
            lambda a: Result.ok(a.chain_stats.funded_txo_sum - a.chain_stats.spent_txo_sum)
        )

    async def get_utxo(self, address: str) -> Result[list[Utxo]]:
        result: Result[list[Utxo]] = Result.err("not started yet")
        for _ in range(self.attempts):
            res = await self._request(f"/address/{address}/utxo")
            try:
                return res.to_result_ok([Utxo(**out) for out in res.parse_json_body()])
            except Exception as e:
                result = res.to_result_err(e)
        return result

    async def get_mempool(self) -> Result[Mempool]:
        result: Result[Mempool] = Result.err("not started yet")
        for _ in range(self.attempts):
            res = await self._request("/mempool")
            try:
                return res.to_result_ok(Mempool(**res.parse_json_body()))
            except Exception as e:
                result = res.to_result_err(e)
        return result

    async def _request(self, url: str) -> HttpResponse:
        return await http_request(f"{self.base_url}{url}", timeout=self.timeout, proxy=random_proxy(self.proxies))
