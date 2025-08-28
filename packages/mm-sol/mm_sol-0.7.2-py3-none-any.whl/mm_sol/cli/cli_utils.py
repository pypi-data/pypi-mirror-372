import importlib.metadata
import time
from pathlib import Path

import mm_print
from loguru import logger
from mm_web3 import Nodes, Proxies, Web3CliConfig, random_node, random_proxy
from pydantic import BaseModel
from solders.signature import Signature

from mm_sol.utils import get_client


def get_version() -> str:
    return importlib.metadata.version("mm-sol")


class BaseConfigParams(BaseModel):
    config_path: Path
    print_config_and_exit: bool


def print_config(config: Web3CliConfig, exclude: set[str] | None = None, count: set[str] | None = None) -> None:
    data = config.model_dump(exclude=exclude)
    if count:
        for k in count:
            data[k] = len(data[k])
    mm_print.json(data)


def public_rpc_url(url: str | None) -> str:
    if not url:
        return "https://api.mainnet-beta.solana.com"

    match url.lower():
        case "mainnet":
            return "https://api.mainnet-beta.solana.com"
        case "testnet":
            return "https://api.testnet.solana.com"
        case "devnet":
            return "https://api.devnet.solana.com"

    return url


def wait_confirmation(nodes: Nodes, proxies: Proxies, signature: Signature, log_prefix: str) -> bool:
    count = 0
    while True:
        try:
            node = random_node(nodes)
            proxy = random_proxy(proxies)
            client = get_client(node, proxy=proxy)
            res = client.get_transaction(signature)
            if res.value and res.value.slot:  # check for tx error
                return True
        except Exception as e:
            logger.error(f"{log_prefix}: can't get confirmation, error={e}")
        time.sleep(1)
        count += 1
        if count > 30:
            logger.error(f"{log_prefix}: can't get confirmation, timeout")
            return False
