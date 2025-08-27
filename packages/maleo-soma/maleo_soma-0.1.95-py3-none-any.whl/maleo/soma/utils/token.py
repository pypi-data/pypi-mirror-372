import jwt
from collections.abc import Iterable, Sequence
from Crypto.PublicKey.RSA import RsaKey
from datetime import timedelta
from typing import Union, overload
from maleo.soma.enums.expiration import Expiration
from maleo.soma.enums.key import RSAKeyType
from maleo.soma.schemas.token import (
    GenericCredentialPayload,
    TimestampPayload,
    GenericPayload,
    PayloadT,
    GeneralPayload,
)
from maleo.soma.types.base import BytesOrString, OptionalDatetime, OptionalString
from maleo.soma.utils.loaders.key.rsa import with_pycryptodome


@overload
def reencode(
    payload: GenericPayload,
    key: RsaKey,
) -> str: ...
@overload
def reencode(
    payload: GenericPayload,
    key: BytesOrString,
    *,
    password: OptionalString = None,
) -> str: ...
def reencode(
    payload: GenericPayload,
    key: Union[RsaKey, BytesOrString],
    *,
    password: OptionalString = None,
) -> str:
    if isinstance(key, RsaKey):
        private_key = key
    else:
        private_key = with_pycryptodome(
            RSAKeyType.PRIVATE, extern_key=key, passphrase=password
        )

    token = jwt.encode(
        payload=payload.model_dump(mode="json"),
        key=private_key.export_key(),
        algorithm="RS256",
    )

    return token


@overload
def encode(
    credential: GenericCredentialPayload,
    key: RsaKey,
    *,
    iat_dt: OptionalDatetime = None,
    exp_in: Expiration = Expiration.EXP_15MN,
) -> str: ...
@overload
def encode(
    credential: GenericCredentialPayload,
    key: BytesOrString,
    *,
    password: OptionalString = None,
    iat_dt: OptionalDatetime = None,
    exp_in: Expiration = Expiration.EXP_15MN,
) -> str: ...
def encode(
    credential: GenericCredentialPayload,
    key: Union[RsaKey, BytesOrString],
    *,
    password: OptionalString = None,
    iat_dt: OptionalDatetime = None,
    exp_in: Expiration = Expiration.EXP_15MN,
) -> str:
    timestamp = TimestampPayload.new_timestamp(iat_dt=iat_dt, exp_in=exp_in)

    payload = GenericPayload.model_validate(
        {**credential.model_dump(), **timestamp.model_dump()}
    )

    if isinstance(key, RsaKey):
        private_key = key
    else:
        private_key = with_pycryptodome(
            RSAKeyType.PRIVATE, extern_key=key, passphrase=password
        )

    token = jwt.encode(
        payload=payload.model_dump(mode="json"),
        key=private_key.export_key(),
        algorithm="RS256",
    )

    return token


def decode(
    payload_type: type[PayloadT] = GeneralPayload,
    *,
    token: str,
    key: Union[RsaKey, BytesOrString],
    audience: str | Iterable[str] | None = None,
    subject: str | None = None,
    issuer: str | Sequence[str] | None = None,
    leeway: float | timedelta = 0,
) -> PayloadT:
    payload_dict = jwt.decode(
        jwt=token,
        key=key.export_key() if isinstance(key, RsaKey) else key,
        algorithms=["RS256"],
        audience=audience,
        subject=subject,
        issuer=issuer,
        leeway=leeway,
    )

    payload = payload_type.model_validate(payload_dict)

    return payload
