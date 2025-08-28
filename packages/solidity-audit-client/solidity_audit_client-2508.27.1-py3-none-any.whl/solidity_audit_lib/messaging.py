import json
import time
import typing

from bittensor import Keypair as BTKeypair  # Bittensor
from pydantic import BaseModel, Field, AliasChoices, AliasGenerator, ConfigDict
from pydantic.alias_generators import to_camel, to_snake
from substrateinterface import Keypair as SubstrateKeypair

__all__ = [
    "KeypairType",
    "sign",
    "verify",
    "SignedMessage",
    "AuditBase",
    "OpenAIVulnerabilityReport",
    "VulnerabilityReport",
    "ContractTask",
    "MinerResponse",
    "MinerResponseMessage",
    "TimestampedMessage",
    "MedalRequestsMessage",
    "RelayerMaintenance",
]

KeypairType = typing.Union[BTKeypair, SubstrateKeypair]


def sign(data: bytes, keypair: KeypairType) -> typing.Tuple[str, str]:
    return "0x" + keypair.sign(data).hex(), keypair.ss58_address


def verify(data: bytes, signature: str, ss58_address: str, safe=True) -> bool:
    if not signature or not ss58_address:
        return False
    try:
        vk = SubstrateKeypair(ss58_address=ss58_address)
        return vk.verify(signature=signature, data=data)
    except Exception as e:
        if not safe:
            raise e
        return False


class SignedMessage(BaseModel):
    # TODO: make checker for JSON parse extra fields
    model_config = ConfigDict(extra="allow")

    signature: typing.Optional[str] = Field(
        default=None,
    )
    ss58_address: typing.Optional[str] = Field(
        default=None,
    )

    def to_signable(self) -> bytes:
        return json.dumps(
            self.model_dump(exclude={"signature", "ss58_address"}), sort_keys=True
        ).encode()

    def sign(self, keypair: KeypairType):
        self.signature, self.ss58_address = sign(self.to_signable(), keypair)

    def verify(self, safe=True) -> bool:
        return verify(self.to_signable(), self.signature, self.ss58_address, safe=safe)


class AuditBase(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=lambda field_name: AliasChoices(
                to_camel(field_name),
                to_snake(field_name),
            ),
            serialization_alias=to_camel,
        )
    )
    from_line: int = Field(
        ...,
        title="From Line",
        description="The starting line number of the vulnerability in the source code. The line numbers start from one.",
        serialization_alias="from",
        validation_alias=AliasChoices("from", "from_line", "fromLine"),
    )
    to_line: int = Field(
        ...,
        title="To Line",
        description="The ending line number of the vulnerability in the source code (inclusive).",
        serialization_alias="to",
        validation_alias=AliasChoices("to", "to_line", "toLine"),
    )
    vulnerability_class: str = Field(
        ...,
        title="Vulnerability Class",
        description="The category of the vulnerability. "
        "E.g. Reentrancy, Bad randomness, Forced reception, Integer overflow, Race condition, "
        "Unchecked call, Gas griefing, Unguarded function, Invalid Code, et cetera.",
    )


class OpenAIVulnerabilityReport(AuditBase):
    test_case: str | None = Field(
        None,
        title="Test Case",
        description="A code example that exploits the vulnerability.",
    )
    description: str | None = Field(
        None,
        title="Description",
        description="Human-readable vulnerability description, in markdown",
    )
    prior_art: list[str] = Field(
        default_factory=list,
        title="Prior Art",
        description="Similar vulnerabilities encountered in wild before",
    )
    fixed_lines: str | None = Field(
        None,
        title="Fixed Lines",
        description="Fixed version of the original source.",
    )


class VulnerabilityReport(OpenAIVulnerabilityReport):
    is_suggestion: bool = Field(
        False,
        title="Is Suggestion",
        description="Whether the fix is a suggestion or not",
    )


class ContractTask(SignedMessage):
    uid: int
    contract_code: str


class MinerResponse(SignedMessage):
    token_ids: list[int] = Field(default_factory=list)
    collection_id: int
    uid: int
    report: list[VulnerabilityReport]


class MinerResponseMessage(SignedMessage):
    success: bool
    result: MinerResponse | None = Field(default=None)
    error: str | None = Field(default=None)


class TimestampedMessage(SignedMessage):
    timestamp: int | None = Field(default=None)

    def sign(self, keypair: KeypairType):
        self.timestamp = int(time.time())
        super().sign(keypair)


class MedalRequestsMessage(TimestampedMessage):
    medal: typing.Literal["Gold", "Silver", "Bronze"]
    miner_ss58_hotkey: str
    score: float
    collection_id: int | None = Field(default=None)
    token_ids: list[int] = Field(default_factory=list)


class RelayerMaintenance(Exception):
    pass
