from __future__ import annotations

from typing import Any

import eth_utils
import rlp
from eth_account import Account
from eth_typing import HexStr
from pydantic import BaseModel
from rlp.sedes import Binary, big_endian_int, binary
from web3 import Web3


class SignedTx(BaseModel):
    tx_hash: str
    raw_tx: str


class RPLTransaction(rlp.Serializable):  # type: ignore[misc]
    fields = [  # noqa: RUF012
        ("nonce", big_endian_int),
        ("gas_price", big_endian_int),
        ("gas", big_endian_int),
        ("to", Binary.fixed_length(20, allow_empty=True)),
        ("value", big_endian_int),
        ("data", binary),
        ("v", big_endian_int),
        ("r", big_endian_int),
        ("s", big_endian_int),
    ]

    @staticmethod
    def new_tx(
        *,
        nonce: int,
        gas_price: int,
        gas: int,
        v: int,
        r: str,
        s: str,
        data: str | None = None,
        value: int | None = None,
        to: str | None = None,
    ) -> RPLTransaction:
        if to:
            to = eth_utils.to_bytes(hexstr=HexStr(to))  # type:ignore[assignment]
        if data:
            data = eth_utils.to_bytes(hexstr=HexStr(data))  # type:ignore[assignment]
        if not value:
            value = 0
        return RPLTransaction(nonce, gas_price, gas, to, value, data, v, int(r, 16), int(s, 16))


class DecodedRawTx(BaseModel):
    tx_hash: str
    from_: str
    to: str | None
    nonce: int
    gas: int
    gas_price: int
    value: int
    data: str
    chain_id: int
    r: str
    s: str
    v: int


def encode_raw_tx_with_signature(
    *,
    nonce: int,
    gas_price: int,
    gas: int,
    v: int,
    r: str,
    s: str,
    data: str | None = None,
    value: int | None = None,
    to: str | None = None,
) -> str:
    tx = RPLTransaction.new_tx(nonce=nonce, gas_price=gas_price, gas=gas, v=v, r=r, s=s, data=data, value=value, to=to)
    return Web3.to_hex(rlp.encode(tx))


def sign_legacy_tx(
    *,
    nonce: int,
    gas_price: int,
    gas: int,
    private_key: str,
    chain_id: int,
    data: str | None = None,
    value: int | None = None,
    to: str | None = None,
) -> SignedTx:
    tx: dict[str, Any] = {"gas": gas, "gasPrice": gas_price, "nonce": nonce, "chainId": chain_id}
    if to:
        tx["to"] = Web3.to_checksum_address(to)
    if value:
        tx["value"] = value
    if data:
        tx["data"] = data

    signed = Account.sign_transaction(tx, private_key)
    return SignedTx(tx_hash=eth_utils.to_hex(signed.hash), raw_tx=eth_utils.to_hex(signed.raw_transaction))


def sign_tx(
    *,
    nonce: int,
    max_fee_per_gas: int,
    max_priority_fee_per_gas: int,
    gas: int,
    private_key: str,
    chain_id: int,
    data: str | None = None,
    value: int | None = None,
    to: str | None = None,
) -> SignedTx:
    tx: dict[str, Any] = {
        "type": "0x2",
        "gas": gas,
        "maxFeePerGas": max_fee_per_gas,
        "maxPriorityFeePerGas": max_priority_fee_per_gas,
        "nonce": nonce,
        "chainId": chain_id,
    }
    if value:
        tx["value"] = value
    if data:
        tx["data"] = data
    if to:
        tx["to"] = Web3.to_checksum_address(to)

    signed = Account.sign_transaction(tx, private_key)
    return SignedTx(tx_hash=signed.hash.to_0x_hex(), raw_tx=signed.raw_transaction.to_0x_hex())


def decode_raw_tx(raw_tx: str) -> DecodedRawTx:
    tx: Any = rlp.decode(eth_utils.to_bytes(hexstr=HexStr(raw_tx)), RPLTransaction)
    tx_hash = Web3.to_hex(eth_utils.keccak(eth_utils.to_bytes(hexstr=HexStr(raw_tx))))
    from_ = Account.recover_transaction(raw_tx)
    to = Web3.to_checksum_address(tx.to) if tx.to else None
    data = Web3.to_hex(tx.data)
    r = hex(tx.r)
    s = hex(tx.s)
    chain_id = (tx.v - 35) // 2 if tx.v % 2 else (tx.v - 36) // 2
    return DecodedRawTx(
        tx_hash=tx_hash,
        from_=from_,
        to=to,
        data=data,
        chain_id=chain_id,
        r=r,
        s=s,
        v=tx.v,
        gas=tx.gas,
        gas_price=tx.gas_price,
        value=tx.value,
        nonce=tx.nonce,
    )
