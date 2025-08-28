import requests

from solidity_audit_lib.messaging import KeypairType, MinerResponseMessage, MedalRequestsMessage
from solidity_audit_lib.relayer_client.relayer_types import (
    RelayerMessage, RegisterParams, RegisterMessage, MinerStorage, ValidatorStorage, StorageMessage, TaskModel,
    PerformAuditMessage, AxonInfo, ResultModel, TopMinersMessage
)


__all__ = ['RelayerClient']


class RelayerClient(object):
    class ClientError(Exception):
        pass

    def __init__(self, relayer_url: str, network_id: int, subnet_uid: int, timeout: int = 5 * 60):
        self.relayer_url = relayer_url
        self.network_id = network_id
        self.subnet_uid = subnet_uid
        self._id = 0
        self.timeout = timeout

    def _call_rpc(self, method: str, params: dict):
        self._id += 1
        result = requests.post(f'{self.relayer_url}/api/jsonrpc', json={
            "jsonrpc": "2.0", "id": self._id, "method": method, "params": params
        }, timeout=self.timeout)
        return result.json()

    def _call(self, method: str, params: dict):
        result = self._call_rpc(method, params)
        if 'error' in result:
            raise self.ClientError(result['error'])
        return result['result']

    def get_miners(self, signer: KeypairType) -> list[AxonInfo]:
        msg = RelayerMessage(network_id=self.network_id, subnet_uid=self.subnet_uid)
        msg.sign(signer)
        axons = self._call('metagraph.get_miners', msg.model_dump())
        return [AxonInfo(**x) for x in axons]

    def get_validators(self, signer: KeypairType) -> list[AxonInfo]:
        msg = RelayerMessage(network_id=self.network_id, subnet_uid=self.subnet_uid)
        msg.sign(signer)
        axons = self._call('metagraph.get_validators', msg.model_dump())
        return [AxonInfo(**x) for x in axons]

    def register_axon(self, signer: KeypairType, params: RegisterParams) -> ResultModel:
        msg = RegisterMessage(network_id=self.network_id, subnet_uid=self.subnet_uid, **params.model_dump())
        msg.sign(signer)
        return ResultModel(**self._call('relayer.register', msg.model_dump()))

    def get_storage(self, signer: KeypairType) -> ResultModel:
        msg = RelayerMessage(network_id=self.network_id, subnet_uid=self.subnet_uid)
        msg.sign(signer)
        return ResultModel(**self._call('relayer.get_hotkey_storage', msg.model_dump()))

    def set_storage(self, signer: KeypairType, storage: MinerStorage | ValidatorStorage) -> ResultModel:
        storage.sign(signer)
        msg = StorageMessage(network_id=self.network_id, subnet_uid=self.subnet_uid, storage=storage.model_dump())
        msg.sign(signer)
        return ResultModel(**self._call('relayer.set_hotkey_storage', msg.model_dump()))

    def perform_audit(self, signer: KeypairType, uid: int, code: str, validator_version: str | None = None) -> MinerResponseMessage:
        task = TaskModel(uid=uid, contract_code=code, validator_version=validator_version)
        task.sign(signer)
        msg = PerformAuditMessage(network_id=self.network_id, subnet_uid=self.subnet_uid, task=task.model_dump())
        msg.sign(signer)
        result = self._call('miner.perform_audit', msg.model_dump())
        if 'error' in result:
            raise self.ClientError(result['error'])
        return MinerResponseMessage(**result['result'])

    def set_top_miners(self, signer: KeypairType, miners: list[MedalRequestsMessage]):
        msg = TopMinersMessage(network_id=self.network_id, subnet_uid=self.subnet_uid, miners=miners)
        msg.sign(signer)
        return ResultModel(**self._call('relayer.set_top_miners', msg.model_dump()))

    def get_activation_code(self, signer: KeypairType) -> str:
        msg = RelayerMessage(network_id=self.network_id, subnet_uid=self.subnet_uid)
        msg.sign(signer)
        result = self._call('validator.get_activation_code', msg.model_dump())
        if 'error' in result:
            raise self.ClientError(result['error'])
        return result['result']
