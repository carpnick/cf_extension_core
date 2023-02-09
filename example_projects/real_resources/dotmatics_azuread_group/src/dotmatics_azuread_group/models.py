# DO NOT modify this file by hand, changes will be overwritten
from dataclasses import dataclass

from cloudformation_cli_python_lib.interface import (
    BaseModel,
    BaseResourceHandlerRequest,
)
from cloudformation_cli_python_lib.recast import recast_object
from cloudformation_cli_python_lib.utils import deserialize_list

import sys
from inspect import getmembers, isclass
from typing import (
    AbstractSet,
    Any,
    Generic,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Type,
    TypeVar,
)

T = TypeVar("T")


def set_or_none(value: Optional[Sequence[T]]) -> Optional[AbstractSet[T]]:
    if value:
        return set(value)
    return None


@dataclass
class ResourceHandlerRequest(BaseResourceHandlerRequest):
    # pylint: disable=invalid-name
    desiredResourceState: Optional["ResourceModel"]
    previousResourceState: Optional["ResourceModel"]
    typeConfiguration: Optional["TypeConfigurationModel"]


@dataclass
class ResourceModel(BaseModel):
    GroupName: Optional[str]
    GroupType: Optional[str]
    GroupDescription: Optional[str]
    GroupId: Optional[str]
    Owners: Optional[Sequence["_Owner"]]
    CredentialAppClientId: Optional[str]
    CredentialAppAPIToken: Optional[str]
    CredentialTenantId: Optional[str]
    GeneratedId: Optional[str]

    @classmethod
    def _deserialize(
        cls: Type["_ResourceModel"],
        json_data: Optional[Mapping[str, Any]],
    ) -> Optional["_ResourceModel"]:
        if not json_data:
            return None
        dataclasses = {n: o for n, o in getmembers(sys.modules[__name__]) if isclass(o)}
        recast_object(cls, json_data, dataclasses)
        return cls(
            GroupName=json_data.get("GroupName"),
            GroupType=json_data.get("GroupType"),
            GroupDescription=json_data.get("GroupDescription"),
            GroupId=json_data.get("GroupId"),
            Owners=deserialize_list(json_data.get("Owners"), Owner),
            CredentialAppClientId=json_data.get("CredentialAppClientId"),
            CredentialAppAPIToken=json_data.get("CredentialAppAPIToken"),
            CredentialTenantId=json_data.get("CredentialTenantId"),
            GeneratedId=json_data.get("GeneratedId"),
        )


# work around possible type aliasing issues when variable has same name as a model
_ResourceModel = ResourceModel


@dataclass
class Owner(BaseModel):
    OwnerType: Optional[str]
    Name: Optional[str]

    @classmethod
    def _deserialize(
        cls: Type["_Owner"],
        json_data: Optional[Mapping[str, Any]],
    ) -> Optional["_Owner"]:
        if not json_data:
            return None
        return cls(
            OwnerType=json_data.get("OwnerType"),
            Name=json_data.get("Name"),
        )


# work around possible type aliasing issues when variable has same name as a model
_Owner = Owner


@dataclass
class TypeConfigurationModel(BaseModel):

    @classmethod
    def _deserialize(
        cls: Type["_TypeConfigurationModel"],
        json_data: Optional[Mapping[str, Any]],
    ) -> Optional["_TypeConfigurationModel"]:
        if not json_data:
            return None
        return cls(
        )


# work around possible type aliasing issues when variable has same name as a model
_TypeConfigurationModel = TypeConfigurationModel


