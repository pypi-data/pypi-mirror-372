from async_substrate_interface.sync_substrate import SubstrateInterface, Keypair
from bittensor.core.chain_data import MetagraphInfo
from bittensor.core.settings import version_as_int, SS58_FORMAT, TYPE_REGISTRY
from bittensor.utils import networking as net
from scalecodec.types import GenericCall

from bittensor_drand.bittensor_drand import get_encrypted_commit

__all__ = ["SubtensorWrapper"]


class SubtensorWrapper:
    U16_MAX = 65535
    AXON_FIELDS = (
        "alpha_stake",
        "block_at_registration",
        ("coldkeys", "coldkey"),
        "consensus",
        "dividends",
        "emission",
        ("hotkeys", "hotkey"),
        ("identities", "identity"),
        ("incentives", "incentive"),
        "last_update",
        "pruning_score",
        "rank",
        "tao_stake",
        "total_stake",
        "trust",
    )

    def __init__(self, ws_endpoint: str):
        self.api = SubstrateInterface(
            url=ws_endpoint,
            ss58_format=SS58_FORMAT,
            type_registry=TYPE_REGISTRY,
            use_remote_preset=True,
            chain_name="Bittensor",
        )

    def __enter__(self):
        self.api.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.api.close()
        self.api.get_parent_block_hash.cache_clear()
        self.api.get_block_runtime_info.cache_clear()
        self.api.get_block_runtime_version_for.cache_clear()
        self.api.supports_rpc_method.cache_clear()
        self.api.get_block_hash.cache_clear()

    def _submit_call(
        self,
        signer: Keypair,
        call: GenericCall,
        wait_for_inclusion=True,
        wait_for_finalization=False,
    ) -> tuple[bool, dict | None]:
        extrinsic = self.api.create_signed_extrinsic(call=call, keypair=signer)
        response = self.api.submit_extrinsic(
            extrinsic=extrinsic,
            wait_for_inclusion=wait_for_inclusion,
            wait_for_finalization=wait_for_finalization,
        )
        if wait_for_inclusion or wait_for_finalization:
            if response.is_success:
                return True, None

            return False, response.error_message

        return True, None

    def get_metagraph(self, net_uid: int, block_hash=None):
        query = self.api.runtime_call(
            "SubnetInfoRuntimeApi",
            "get_metagraph",
            params=[net_uid],
            block_hash=block_hash,
        )
        if query.value is None:
            return None
        return MetagraphInfo.from_dict(query.value)

    def get_axons(self, net_uid: int, block_hash=None):
        axons = []
        metagraph = self.get_metagraph(net_uid, block_hash)
        for i, x in enumerate(metagraph.axons):
            axon = {"info": x}
            axon["info"]["ip"] = net.int_to_ip(axon["info"]["ip"])
            for key in self.AXON_FIELDS:
                if not isinstance(key, str):
                    key, axon_key = key
                else:
                    axon_key = key
                try:
                    axon[axon_key] = getattr(metagraph, key)[i]
                except KeyError:
                    if key != "identities":
                        raise
                    axon[axon_key] = None
            axons.append(axon)
        return axons

    def get_served_axon(self, net_uid: int, axon_hotkey: str) -> dict | None:
        axon: dict = self.api.query("SubtensorModule", "Axons", [net_uid, axon_hotkey])
        if axon is None:
            return None
        axon["ip"] = net.int_to_ip(axon["ip"])
        return axon

    def get_uid(
        self, net_uid: int, axon_hotkey: str, block_hash: str | None = None
    ) -> int | None:
        result = self.api.query(
            "SubtensorModule", "Uids", [net_uid, axon_hotkey], block_hash=block_hash
        )
        if result is not None:
            return result.value
        return None

    def get_last_update(
        self, net_uid: int, block_hash: str | None = None
    ) -> list[int] | None:
        result = self.api.query(
            "SubtensorModule", "LastUpdate", [net_uid], block_hash=block_hash
        )
        if result:
            return result.value
        return None

    def serve_axon(
        self,
        signer: Keypair,
        net_uid: int,
        ip: str,
        port: int,
        wait_for_inclusion=True,
        wait_for_finalization=False,
    ) -> tuple[bool, dict | None]:
        already_serving = self.get_served_axon(net_uid, signer.ss58_address)
        if already_serving is not None:
            if already_serving["ip"] == ip and already_serving["port"] == port:
                return True, None
            current_block = self.api.get_block_number(
                self.api.get_chain_finalised_head()
            )
            min_diff = self.api.query(
                "SubtensorModule", "ServingRateLimit", [net_uid]
            ).value
            diff = abs(current_block - already_serving["block"])
            if diff < min_diff:
                return False, {"name": "RateLimit", "blocks": abs(diff - min_diff)}

        call_params = {
            "version": version_as_int,
            "ip": net.ip_to_int(ip),
            "port": port,
            "ip_type": net.ip_version(ip),
            "netuid": net_uid,
            "protocol": 4,
            "placeholder1": 0,
            "placeholder2": 0,
        }
        call = self.api.compose_call("SubtensorModule", "serve_axon", call_params)
        return self._submit_call(
            signer,
            call,
            wait_for_inclusion=wait_for_inclusion,
            wait_for_finalization=wait_for_finalization,
        )

    def get_tempo_and_commit_reveal_period(self, net_uid: int) -> tuple[int, int]:
        tempo = self.api.query(
            module="SubtensorModule",
            storage_function="Tempo",
            params=[net_uid],
        )
        commit_reveal_period = self.api.query(
            module="SubtensorModule",
            storage_function="RevealPeriodEpochs",
            params=[net_uid],
        )
        return tempo.value, commit_reveal_period.value

    def set_weights(
        self,
        signer: Keypair,
        net_uid: int,
        scores: dict[int, float | int],
        wait_for_inclusion=True,
        wait_for_finalization=False,
    ) -> tuple[bool, dict | None]:
        uid = self.get_uid(net_uid, signer.ss58_address)
        if uid is None:
            return False, {"name": "UnregisteredAxon"}
        last_update = self.get_last_update(net_uid)
        last_set_weights_block = last_update[uid]
        min_diff = self.api.query(
            "SubtensorModule", "WeightsSetRateLimit", [net_uid]
        ).value
        current_block = self.api.get_block_number(self.api.get_chain_finalised_head())
        diff = abs(current_block - last_set_weights_block)
        if diff < min_diff:
            return False, {"name": "RateLimit", "blocks": abs(diff - min_diff)}

        max_score = max(scores.values()) or 1
        normalized_scores = {
            k: int((v / max_score) * self.U16_MAX) for k, v in scores.items()
        }
        call = self.api.compose_call(
            "SubtensorModule",
            "set_weights",
            {
                "dests": list(normalized_scores.keys()),
                "weights": list(normalized_scores.values()),
                "netuid": net_uid,
                "version_key": version_as_int,
            },
        )
        return self._submit_call(
            signer,
            call,
            wait_for_inclusion=wait_for_inclusion,
            wait_for_finalization=wait_for_finalization,
        )

    def commit_weights(
        self,
        signer: Keypair,
        net_uid: int,
        weights: dict[int, int | float],
        period: int | None = None,
        commit_reveal_version: int = 4,
        block_time: int | float = 12,
        wait_for_inclusion=True,
        wait_for_finalization=False,
    ):
        tempo, commit_reveal_period = self.get_tempo_and_commit_reveal_period(net_uid)
        current_block = self.api.get_block_number(self.api.get_chain_finalised_head())
        max_weight = max(weights.values()) or 1
        normalized_weights = {
            k: int((v / max_weight) * self.U16_MAX) for k, v in weights.items()
        }
        flat_uids, flat_weights = zip(*normalized_weights.items())

        commit_for_reveal, reveal_round = get_encrypted_commit(
            flat_uids,
            flat_weights,
            version_as_int,
            tempo,
            current_block,
            net_uid,
            commit_reveal_period,
            block_time,
            signer.public_key,
        )

        call = self.api.compose_call(
            call_module="SubtensorModule",
            call_function="commit_timelocked_weights",
            call_params={
                "netuid": net_uid,
                "commit": commit_for_reveal,
                "reveal_round": reveal_round,
                "commit_reveal_version": commit_reveal_version,
            },
        )

        extrinsic = self.api.create_signed_extrinsic(
            call=call, keypair=signer, era={"period": period} if period else None
        )
        try:
            receipt = self.api.submit_extrinsic(
                extrinsic,
                wait_for_inclusion=wait_for_inclusion,
                wait_for_finalization=wait_for_finalization,
            )
            return receipt.is_success, receipt.error_message
        except Exception as e:
            return False, str(e)

    def set_identity(
        self,
        signer: Keypair,
        name: str,
        description: str,
        wait_for_inclusion=True,
        wait_for_finalization=False,
    ):
        state = self.api.query("SubtensorModule", "IdentitiesV2", [signer.ss58_address])
        if state and state["description"] == description and state["name"] == name:
            return
        call = self.api.compose_call(
            "SubtensorModule",
            "set_identity",
            {
                "name": name,
                "url": b"",
                "image": b"",
                "discord": b"",
                "description": description,
                "additional": b"",
                "github_repo": b"",
            },
        )

        return self._submit_call(
            signer,
            call,
            wait_for_inclusion=wait_for_inclusion,
            wait_for_finalization=wait_for_finalization,
        )
