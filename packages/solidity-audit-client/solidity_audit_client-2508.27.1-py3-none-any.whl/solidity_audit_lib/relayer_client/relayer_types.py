import pydantic

from solidity_audit_lib.messaging import SignedMessage, MedalRequestsMessage

__all__ = [
    "RelayerMessage",
    "RegisterParams",
    "RegisterMessage",
    "MinerStorage",
    "ValidatorStorage",
    "StorageMessage",
    "TaskModel",
    "PerformAuditMessage",
    "AxonInfo",
    "ResultModel",
    "TopMinersMessage",
]


class RelayerMessage(SignedMessage):
    network_id: int
    subnet_uid: int


class RegisterParams(pydantic.BaseModel):
    uid: int
    type: str
    ip: str
    port: int


class RegisterMessage(RelayerMessage):
    uid: int
    type: str
    ip: str
    port: int


class MinerStorage(SignedMessage):
    collection_id: int


class ValidatorStorage(SignedMessage):
    last_validation: int
    scores: dict[str, list[float | int]]
    hotkeys: dict[str, str]


class StorageMessage(RelayerMessage):
    storage: dict


class TaskModel(SignedMessage):
    uid: int
    contract_code: str
    validator_version: str | None = None


class PerformAuditMessage(RelayerMessage):
    task: TaskModel


class TopMinersMessage(RelayerMessage):
    miners: list[MedalRequestsMessage]


class AxonInfo(pydantic.BaseModel):
    uid: int
    ip: str
    port: int
    hotkey: str | None = None
    coldkey: str | None = None
    is_alive: bool = True


class ResultModel(pydantic.BaseModel):
    success: bool
    error: str | None = None
    result: dict | None = None
