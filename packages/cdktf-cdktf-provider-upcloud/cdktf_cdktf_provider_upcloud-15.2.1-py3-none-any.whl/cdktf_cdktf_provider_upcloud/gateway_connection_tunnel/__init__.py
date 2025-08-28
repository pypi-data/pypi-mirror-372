r'''
# `upcloud_gateway_connection_tunnel`

Refer to the Terraform Registry for docs: [`upcloud_gateway_connection_tunnel`](https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel).
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from .._jsii import *

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class GatewayConnectionTunnel(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.gatewayConnectionTunnel.GatewayConnectionTunnel",
):
    '''Represents a {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel upcloud_gateway_connection_tunnel}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        connection_id: builtins.str,
        ipsec_auth_psk: typing.Union["GatewayConnectionTunnelIpsecAuthPsk", typing.Dict[builtins.str, typing.Any]],
        local_address_name: builtins.str,
        name: builtins.str,
        remote_address: builtins.str,
        id: typing.Optional[builtins.str] = None,
        ipsec_properties: typing.Optional[typing.Union["GatewayConnectionTunnelIpsecProperties", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel upcloud_gateway_connection_tunnel} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param connection_id: ID of the upcloud_gateway_connection resource to which the tunnel belongs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#connection_id GatewayConnectionTunnel#connection_id}
        :param ipsec_auth_psk: ipsec_auth_psk block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#ipsec_auth_psk GatewayConnectionTunnel#ipsec_auth_psk}
        :param local_address_name: Public (UpCloud) endpoint address of this tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#local_address_name GatewayConnectionTunnel#local_address_name}
        :param name: The name of the tunnel, should be unique within the connection. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#name GatewayConnectionTunnel#name}
        :param remote_address: Remote public IP address of the tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#remote_address GatewayConnectionTunnel#remote_address}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#id GatewayConnectionTunnel#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ipsec_properties: ipsec_properties block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#ipsec_properties GatewayConnectionTunnel#ipsec_properties}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcba9d47af2d640b381a57614585e17d61c78e34893161a6bcb3a0e59e4893d0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = GatewayConnectionTunnelConfig(
            connection_id=connection_id,
            ipsec_auth_psk=ipsec_auth_psk,
            local_address_name=local_address_name,
            name=name,
            remote_address=remote_address,
            id=id,
            ipsec_properties=ipsec_properties,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a GatewayConnectionTunnel resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the GatewayConnectionTunnel to import.
        :param import_from_id: The id of the existing GatewayConnectionTunnel that should be imported. Refer to the {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the GatewayConnectionTunnel to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95236e9d369f33914f666fa8076ddef4b5b620b25f4b18ec52b8822131b193aa)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putIpsecAuthPsk")
    def put_ipsec_auth_psk(self, *, psk: builtins.str) -> None:
        '''
        :param psk: The pre-shared key. This value is only used during resource creation and is not returned in the state. It is not possible to update this value. If you need to update it, delete the connection and create a new one. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#psk GatewayConnectionTunnel#psk}
        '''
        value = GatewayConnectionTunnelIpsecAuthPsk(psk=psk)

        return typing.cast(None, jsii.invoke(self, "putIpsecAuthPsk", [value]))

    @jsii.member(jsii_name="putIpsecProperties")
    def put_ipsec_properties(
        self,
        *,
        child_rekey_time: typing.Optional[jsii.Number] = None,
        dpd_delay: typing.Optional[jsii.Number] = None,
        dpd_timeout: typing.Optional[jsii.Number] = None,
        ike_lifetime: typing.Optional[jsii.Number] = None,
        phase1_algorithms: typing.Optional[typing.Sequence[builtins.str]] = None,
        phase1_dh_group_numbers: typing.Optional[typing.Sequence[jsii.Number]] = None,
        phase1_integrity_algorithms: typing.Optional[typing.Sequence[builtins.str]] = None,
        phase2_algorithms: typing.Optional[typing.Sequence[builtins.str]] = None,
        phase2_dh_group_numbers: typing.Optional[typing.Sequence[jsii.Number]] = None,
        phase2_integrity_algorithms: typing.Optional[typing.Sequence[builtins.str]] = None,
        rekey_time: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param child_rekey_time: IKE child SA rekey time in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#child_rekey_time GatewayConnectionTunnel#child_rekey_time}
        :param dpd_delay: Delay before sending Dead Peer Detection packets if no traffic is detected, in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#dpd_delay GatewayConnectionTunnel#dpd_delay}
        :param dpd_timeout: Timeout period for DPD reply before considering the peer to be dead, in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#dpd_timeout GatewayConnectionTunnel#dpd_timeout}
        :param ike_lifetime: Maximum IKE SA lifetime in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#ike_lifetime GatewayConnectionTunnel#ike_lifetime}
        :param phase1_algorithms: List of Phase 1: Proposal algorithms. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#phase1_algorithms GatewayConnectionTunnel#phase1_algorithms}
        :param phase1_dh_group_numbers: List of Phase 1 Diffie-Hellman group numbers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#phase1_dh_group_numbers GatewayConnectionTunnel#phase1_dh_group_numbers}
        :param phase1_integrity_algorithms: List of Phase 1 integrity algorithms. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#phase1_integrity_algorithms GatewayConnectionTunnel#phase1_integrity_algorithms}
        :param phase2_algorithms: List of Phase 2: Security Association algorithms. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#phase2_algorithms GatewayConnectionTunnel#phase2_algorithms}
        :param phase2_dh_group_numbers: List of Phase 2 Diffie-Hellman group numbers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#phase2_dh_group_numbers GatewayConnectionTunnel#phase2_dh_group_numbers}
        :param phase2_integrity_algorithms: List of Phase 2 integrity algorithms. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#phase2_integrity_algorithms GatewayConnectionTunnel#phase2_integrity_algorithms}
        :param rekey_time: IKE SA rekey time in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#rekey_time GatewayConnectionTunnel#rekey_time}
        '''
        value = GatewayConnectionTunnelIpsecProperties(
            child_rekey_time=child_rekey_time,
            dpd_delay=dpd_delay,
            dpd_timeout=dpd_timeout,
            ike_lifetime=ike_lifetime,
            phase1_algorithms=phase1_algorithms,
            phase1_dh_group_numbers=phase1_dh_group_numbers,
            phase1_integrity_algorithms=phase1_integrity_algorithms,
            phase2_algorithms=phase2_algorithms,
            phase2_dh_group_numbers=phase2_dh_group_numbers,
            phase2_integrity_algorithms=phase2_integrity_algorithms,
            rekey_time=rekey_time,
        )

        return typing.cast(None, jsii.invoke(self, "putIpsecProperties", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIpsecProperties")
    def reset_ipsec_properties(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpsecProperties", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="synthesizeHclAttributes")
    def _synthesize_hcl_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeHclAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="ipsecAuthPsk")
    def ipsec_auth_psk(self) -> "GatewayConnectionTunnelIpsecAuthPskOutputReference":
        return typing.cast("GatewayConnectionTunnelIpsecAuthPskOutputReference", jsii.get(self, "ipsecAuthPsk"))

    @builtins.property
    @jsii.member(jsii_name="ipsecProperties")
    def ipsec_properties(
        self,
    ) -> "GatewayConnectionTunnelIpsecPropertiesOutputReference":
        return typing.cast("GatewayConnectionTunnelIpsecPropertiesOutputReference", jsii.get(self, "ipsecProperties"))

    @builtins.property
    @jsii.member(jsii_name="operationalState")
    def operational_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operationalState"))

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @builtins.property
    @jsii.member(jsii_name="connectionIdInput")
    def connection_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionIdInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="ipsecAuthPskInput")
    def ipsec_auth_psk_input(
        self,
    ) -> typing.Optional["GatewayConnectionTunnelIpsecAuthPsk"]:
        return typing.cast(typing.Optional["GatewayConnectionTunnelIpsecAuthPsk"], jsii.get(self, "ipsecAuthPskInput"))

    @builtins.property
    @jsii.member(jsii_name="ipsecPropertiesInput")
    def ipsec_properties_input(
        self,
    ) -> typing.Optional["GatewayConnectionTunnelIpsecProperties"]:
        return typing.cast(typing.Optional["GatewayConnectionTunnelIpsecProperties"], jsii.get(self, "ipsecPropertiesInput"))

    @builtins.property
    @jsii.member(jsii_name="localAddressNameInput")
    def local_address_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "localAddressNameInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="remoteAddressInput")
    def remote_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "remoteAddressInput"))

    @builtins.property
    @jsii.member(jsii_name="connectionId")
    def connection_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectionId"))

    @connection_id.setter
    def connection_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__126516e9f2491501373dc78a2ced217cc6983515585858bddaa97a43be47c46e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f700caa4649526605c5789b4b1af9dbc420a82c8c23deedc54920d5e9b5549cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="localAddressName")
    def local_address_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "localAddressName"))

    @local_address_name.setter
    def local_address_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a349ea0021d2c6d6de75a59ca14d51e1948a94c4ed9d0daa4dfed83a20b53d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localAddressName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22991b014c3d2e71d2ea4eecdc4d72c95098523fea98fea667712a8f2f3f7dcb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="remoteAddress")
    def remote_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "remoteAddress"))

    @remote_address.setter
    def remote_address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20fc183698bb25fe3dd18b8951c12e22d0f3fcff5c932fb833788131f196f2b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "remoteAddress", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.gatewayConnectionTunnel.GatewayConnectionTunnelConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "connection_id": "connectionId",
        "ipsec_auth_psk": "ipsecAuthPsk",
        "local_address_name": "localAddressName",
        "name": "name",
        "remote_address": "remoteAddress",
        "id": "id",
        "ipsec_properties": "ipsecProperties",
    },
)
class GatewayConnectionTunnelConfig(_cdktf_9a9027ec.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection_id: builtins.str,
        ipsec_auth_psk: typing.Union["GatewayConnectionTunnelIpsecAuthPsk", typing.Dict[builtins.str, typing.Any]],
        local_address_name: builtins.str,
        name: builtins.str,
        remote_address: builtins.str,
        id: typing.Optional[builtins.str] = None,
        ipsec_properties: typing.Optional[typing.Union["GatewayConnectionTunnelIpsecProperties", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param connection_id: ID of the upcloud_gateway_connection resource to which the tunnel belongs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#connection_id GatewayConnectionTunnel#connection_id}
        :param ipsec_auth_psk: ipsec_auth_psk block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#ipsec_auth_psk GatewayConnectionTunnel#ipsec_auth_psk}
        :param local_address_name: Public (UpCloud) endpoint address of this tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#local_address_name GatewayConnectionTunnel#local_address_name}
        :param name: The name of the tunnel, should be unique within the connection. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#name GatewayConnectionTunnel#name}
        :param remote_address: Remote public IP address of the tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#remote_address GatewayConnectionTunnel#remote_address}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#id GatewayConnectionTunnel#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ipsec_properties: ipsec_properties block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#ipsec_properties GatewayConnectionTunnel#ipsec_properties}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(ipsec_auth_psk, dict):
            ipsec_auth_psk = GatewayConnectionTunnelIpsecAuthPsk(**ipsec_auth_psk)
        if isinstance(ipsec_properties, dict):
            ipsec_properties = GatewayConnectionTunnelIpsecProperties(**ipsec_properties)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6d11a79d0e62a94d31dbeeb1b1d2a1d94139d8c65e2ddf5917626ad2d4a6f99)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument connection_id", value=connection_id, expected_type=type_hints["connection_id"])
            check_type(argname="argument ipsec_auth_psk", value=ipsec_auth_psk, expected_type=type_hints["ipsec_auth_psk"])
            check_type(argname="argument local_address_name", value=local_address_name, expected_type=type_hints["local_address_name"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument remote_address", value=remote_address, expected_type=type_hints["remote_address"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument ipsec_properties", value=ipsec_properties, expected_type=type_hints["ipsec_properties"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "connection_id": connection_id,
            "ipsec_auth_psk": ipsec_auth_psk,
            "local_address_name": local_address_name,
            "name": name,
            "remote_address": remote_address,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if id is not None:
            self._values["id"] = id
        if ipsec_properties is not None:
            self._values["ipsec_properties"] = ipsec_properties

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]], result)

    @builtins.property
    def count(
        self,
    ) -> typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]], result)

    @builtins.property
    def depends_on(
        self,
    ) -> typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[_cdktf_9a9027ec.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[_cdktf_9a9027ec.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]], result)

    @builtins.property
    def connection_id(self) -> builtins.str:
        '''ID of the upcloud_gateway_connection resource to which the tunnel belongs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#connection_id GatewayConnectionTunnel#connection_id}
        '''
        result = self._values.get("connection_id")
        assert result is not None, "Required property 'connection_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ipsec_auth_psk(self) -> "GatewayConnectionTunnelIpsecAuthPsk":
        '''ipsec_auth_psk block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#ipsec_auth_psk GatewayConnectionTunnel#ipsec_auth_psk}
        '''
        result = self._values.get("ipsec_auth_psk")
        assert result is not None, "Required property 'ipsec_auth_psk' is missing"
        return typing.cast("GatewayConnectionTunnelIpsecAuthPsk", result)

    @builtins.property
    def local_address_name(self) -> builtins.str:
        '''Public (UpCloud) endpoint address of this tunnel.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#local_address_name GatewayConnectionTunnel#local_address_name}
        '''
        result = self._values.get("local_address_name")
        assert result is not None, "Required property 'local_address_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the tunnel, should be unique within the connection.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#name GatewayConnectionTunnel#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def remote_address(self) -> builtins.str:
        '''Remote public IP address of the tunnel.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#remote_address GatewayConnectionTunnel#remote_address}
        '''
        result = self._values.get("remote_address")
        assert result is not None, "Required property 'remote_address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#id GatewayConnectionTunnel#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ipsec_properties(
        self,
    ) -> typing.Optional["GatewayConnectionTunnelIpsecProperties"]:
        '''ipsec_properties block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#ipsec_properties GatewayConnectionTunnel#ipsec_properties}
        '''
        result = self._values.get("ipsec_properties")
        return typing.cast(typing.Optional["GatewayConnectionTunnelIpsecProperties"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GatewayConnectionTunnelConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.gatewayConnectionTunnel.GatewayConnectionTunnelIpsecAuthPsk",
    jsii_struct_bases=[],
    name_mapping={"psk": "psk"},
)
class GatewayConnectionTunnelIpsecAuthPsk:
    def __init__(self, *, psk: builtins.str) -> None:
        '''
        :param psk: The pre-shared key. This value is only used during resource creation and is not returned in the state. It is not possible to update this value. If you need to update it, delete the connection and create a new one. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#psk GatewayConnectionTunnel#psk}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87c835e7d7c5605931c1ca38462874908e77d68cd5b951debc157a3d43ca979a)
            check_type(argname="argument psk", value=psk, expected_type=type_hints["psk"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "psk": psk,
        }

    @builtins.property
    def psk(self) -> builtins.str:
        '''The pre-shared key.

        This value is only used during resource creation and is not returned in the state. It is not possible to update this value. If you need to update it, delete the connection and create a new one.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#psk GatewayConnectionTunnel#psk}
        '''
        result = self._values.get("psk")
        assert result is not None, "Required property 'psk' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GatewayConnectionTunnelIpsecAuthPsk(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GatewayConnectionTunnelIpsecAuthPskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.gatewayConnectionTunnel.GatewayConnectionTunnelIpsecAuthPskOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__685fc99f2c3e31478dfaba417d0029c9f025f9f6781f1b846b229190d1465d10)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="pskInput")
    def psk_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pskInput"))

    @builtins.property
    @jsii.member(jsii_name="psk")
    def psk(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "psk"))

    @psk.setter
    def psk(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c54073d7ff76d5ff3a7bb48388097398cf24b757cf5ceecdd25321fb42e85b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "psk", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[GatewayConnectionTunnelIpsecAuthPsk]:
        return typing.cast(typing.Optional[GatewayConnectionTunnelIpsecAuthPsk], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GatewayConnectionTunnelIpsecAuthPsk],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e2d2460505ab3151036fc5067cfb416cf9ea5829b3ff70c70b0eba1e32b0f6f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.gatewayConnectionTunnel.GatewayConnectionTunnelIpsecProperties",
    jsii_struct_bases=[],
    name_mapping={
        "child_rekey_time": "childRekeyTime",
        "dpd_delay": "dpdDelay",
        "dpd_timeout": "dpdTimeout",
        "ike_lifetime": "ikeLifetime",
        "phase1_algorithms": "phase1Algorithms",
        "phase1_dh_group_numbers": "phase1DhGroupNumbers",
        "phase1_integrity_algorithms": "phase1IntegrityAlgorithms",
        "phase2_algorithms": "phase2Algorithms",
        "phase2_dh_group_numbers": "phase2DhGroupNumbers",
        "phase2_integrity_algorithms": "phase2IntegrityAlgorithms",
        "rekey_time": "rekeyTime",
    },
)
class GatewayConnectionTunnelIpsecProperties:
    def __init__(
        self,
        *,
        child_rekey_time: typing.Optional[jsii.Number] = None,
        dpd_delay: typing.Optional[jsii.Number] = None,
        dpd_timeout: typing.Optional[jsii.Number] = None,
        ike_lifetime: typing.Optional[jsii.Number] = None,
        phase1_algorithms: typing.Optional[typing.Sequence[builtins.str]] = None,
        phase1_dh_group_numbers: typing.Optional[typing.Sequence[jsii.Number]] = None,
        phase1_integrity_algorithms: typing.Optional[typing.Sequence[builtins.str]] = None,
        phase2_algorithms: typing.Optional[typing.Sequence[builtins.str]] = None,
        phase2_dh_group_numbers: typing.Optional[typing.Sequence[jsii.Number]] = None,
        phase2_integrity_algorithms: typing.Optional[typing.Sequence[builtins.str]] = None,
        rekey_time: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param child_rekey_time: IKE child SA rekey time in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#child_rekey_time GatewayConnectionTunnel#child_rekey_time}
        :param dpd_delay: Delay before sending Dead Peer Detection packets if no traffic is detected, in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#dpd_delay GatewayConnectionTunnel#dpd_delay}
        :param dpd_timeout: Timeout period for DPD reply before considering the peer to be dead, in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#dpd_timeout GatewayConnectionTunnel#dpd_timeout}
        :param ike_lifetime: Maximum IKE SA lifetime in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#ike_lifetime GatewayConnectionTunnel#ike_lifetime}
        :param phase1_algorithms: List of Phase 1: Proposal algorithms. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#phase1_algorithms GatewayConnectionTunnel#phase1_algorithms}
        :param phase1_dh_group_numbers: List of Phase 1 Diffie-Hellman group numbers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#phase1_dh_group_numbers GatewayConnectionTunnel#phase1_dh_group_numbers}
        :param phase1_integrity_algorithms: List of Phase 1 integrity algorithms. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#phase1_integrity_algorithms GatewayConnectionTunnel#phase1_integrity_algorithms}
        :param phase2_algorithms: List of Phase 2: Security Association algorithms. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#phase2_algorithms GatewayConnectionTunnel#phase2_algorithms}
        :param phase2_dh_group_numbers: List of Phase 2 Diffie-Hellman group numbers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#phase2_dh_group_numbers GatewayConnectionTunnel#phase2_dh_group_numbers}
        :param phase2_integrity_algorithms: List of Phase 2 integrity algorithms. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#phase2_integrity_algorithms GatewayConnectionTunnel#phase2_integrity_algorithms}
        :param rekey_time: IKE SA rekey time in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#rekey_time GatewayConnectionTunnel#rekey_time}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a50b18894047098027d5d6be1b8a41d8e32b22c4297ebea79c281f4c838921f4)
            check_type(argname="argument child_rekey_time", value=child_rekey_time, expected_type=type_hints["child_rekey_time"])
            check_type(argname="argument dpd_delay", value=dpd_delay, expected_type=type_hints["dpd_delay"])
            check_type(argname="argument dpd_timeout", value=dpd_timeout, expected_type=type_hints["dpd_timeout"])
            check_type(argname="argument ike_lifetime", value=ike_lifetime, expected_type=type_hints["ike_lifetime"])
            check_type(argname="argument phase1_algorithms", value=phase1_algorithms, expected_type=type_hints["phase1_algorithms"])
            check_type(argname="argument phase1_dh_group_numbers", value=phase1_dh_group_numbers, expected_type=type_hints["phase1_dh_group_numbers"])
            check_type(argname="argument phase1_integrity_algorithms", value=phase1_integrity_algorithms, expected_type=type_hints["phase1_integrity_algorithms"])
            check_type(argname="argument phase2_algorithms", value=phase2_algorithms, expected_type=type_hints["phase2_algorithms"])
            check_type(argname="argument phase2_dh_group_numbers", value=phase2_dh_group_numbers, expected_type=type_hints["phase2_dh_group_numbers"])
            check_type(argname="argument phase2_integrity_algorithms", value=phase2_integrity_algorithms, expected_type=type_hints["phase2_integrity_algorithms"])
            check_type(argname="argument rekey_time", value=rekey_time, expected_type=type_hints["rekey_time"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if child_rekey_time is not None:
            self._values["child_rekey_time"] = child_rekey_time
        if dpd_delay is not None:
            self._values["dpd_delay"] = dpd_delay
        if dpd_timeout is not None:
            self._values["dpd_timeout"] = dpd_timeout
        if ike_lifetime is not None:
            self._values["ike_lifetime"] = ike_lifetime
        if phase1_algorithms is not None:
            self._values["phase1_algorithms"] = phase1_algorithms
        if phase1_dh_group_numbers is not None:
            self._values["phase1_dh_group_numbers"] = phase1_dh_group_numbers
        if phase1_integrity_algorithms is not None:
            self._values["phase1_integrity_algorithms"] = phase1_integrity_algorithms
        if phase2_algorithms is not None:
            self._values["phase2_algorithms"] = phase2_algorithms
        if phase2_dh_group_numbers is not None:
            self._values["phase2_dh_group_numbers"] = phase2_dh_group_numbers
        if phase2_integrity_algorithms is not None:
            self._values["phase2_integrity_algorithms"] = phase2_integrity_algorithms
        if rekey_time is not None:
            self._values["rekey_time"] = rekey_time

    @builtins.property
    def child_rekey_time(self) -> typing.Optional[jsii.Number]:
        '''IKE child SA rekey time in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#child_rekey_time GatewayConnectionTunnel#child_rekey_time}
        '''
        result = self._values.get("child_rekey_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def dpd_delay(self) -> typing.Optional[jsii.Number]:
        '''Delay before sending Dead Peer Detection packets if no traffic is detected, in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#dpd_delay GatewayConnectionTunnel#dpd_delay}
        '''
        result = self._values.get("dpd_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def dpd_timeout(self) -> typing.Optional[jsii.Number]:
        '''Timeout period for DPD reply before considering the peer to be dead, in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#dpd_timeout GatewayConnectionTunnel#dpd_timeout}
        '''
        result = self._values.get("dpd_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ike_lifetime(self) -> typing.Optional[jsii.Number]:
        '''Maximum IKE SA lifetime in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#ike_lifetime GatewayConnectionTunnel#ike_lifetime}
        '''
        result = self._values.get("ike_lifetime")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def phase1_algorithms(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of Phase 1: Proposal algorithms.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#phase1_algorithms GatewayConnectionTunnel#phase1_algorithms}
        '''
        result = self._values.get("phase1_algorithms")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def phase1_dh_group_numbers(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''List of Phase 1 Diffie-Hellman group numbers.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#phase1_dh_group_numbers GatewayConnectionTunnel#phase1_dh_group_numbers}
        '''
        result = self._values.get("phase1_dh_group_numbers")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    @builtins.property
    def phase1_integrity_algorithms(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of Phase 1 integrity algorithms.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#phase1_integrity_algorithms GatewayConnectionTunnel#phase1_integrity_algorithms}
        '''
        result = self._values.get("phase1_integrity_algorithms")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def phase2_algorithms(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of Phase 2: Security Association algorithms.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#phase2_algorithms GatewayConnectionTunnel#phase2_algorithms}
        '''
        result = self._values.get("phase2_algorithms")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def phase2_dh_group_numbers(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''List of Phase 2 Diffie-Hellman group numbers.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#phase2_dh_group_numbers GatewayConnectionTunnel#phase2_dh_group_numbers}
        '''
        result = self._values.get("phase2_dh_group_numbers")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    @builtins.property
    def phase2_integrity_algorithms(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of Phase 2 integrity algorithms.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#phase2_integrity_algorithms GatewayConnectionTunnel#phase2_integrity_algorithms}
        '''
        result = self._values.get("phase2_integrity_algorithms")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def rekey_time(self) -> typing.Optional[jsii.Number]:
        '''IKE SA rekey time in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/gateway_connection_tunnel#rekey_time GatewayConnectionTunnel#rekey_time}
        '''
        result = self._values.get("rekey_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GatewayConnectionTunnelIpsecProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GatewayConnectionTunnelIpsecPropertiesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.gatewayConnectionTunnel.GatewayConnectionTunnelIpsecPropertiesOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3ce480a94c93bf5e7f9b3393fc3227f8192dbb60f5168d77e6bd72d78790a0d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetChildRekeyTime")
    def reset_child_rekey_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChildRekeyTime", []))

    @jsii.member(jsii_name="resetDpdDelay")
    def reset_dpd_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDpdDelay", []))

    @jsii.member(jsii_name="resetDpdTimeout")
    def reset_dpd_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDpdTimeout", []))

    @jsii.member(jsii_name="resetIkeLifetime")
    def reset_ike_lifetime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIkeLifetime", []))

    @jsii.member(jsii_name="resetPhase1Algorithms")
    def reset_phase1_algorithms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPhase1Algorithms", []))

    @jsii.member(jsii_name="resetPhase1DhGroupNumbers")
    def reset_phase1_dh_group_numbers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPhase1DhGroupNumbers", []))

    @jsii.member(jsii_name="resetPhase1IntegrityAlgorithms")
    def reset_phase1_integrity_algorithms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPhase1IntegrityAlgorithms", []))

    @jsii.member(jsii_name="resetPhase2Algorithms")
    def reset_phase2_algorithms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPhase2Algorithms", []))

    @jsii.member(jsii_name="resetPhase2DhGroupNumbers")
    def reset_phase2_dh_group_numbers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPhase2DhGroupNumbers", []))

    @jsii.member(jsii_name="resetPhase2IntegrityAlgorithms")
    def reset_phase2_integrity_algorithms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPhase2IntegrityAlgorithms", []))

    @jsii.member(jsii_name="resetRekeyTime")
    def reset_rekey_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRekeyTime", []))

    @builtins.property
    @jsii.member(jsii_name="childRekeyTimeInput")
    def child_rekey_time_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "childRekeyTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="dpdDelayInput")
    def dpd_delay_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "dpdDelayInput"))

    @builtins.property
    @jsii.member(jsii_name="dpdTimeoutInput")
    def dpd_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "dpdTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="ikeLifetimeInput")
    def ike_lifetime_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ikeLifetimeInput"))

    @builtins.property
    @jsii.member(jsii_name="phase1AlgorithmsInput")
    def phase1_algorithms_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "phase1AlgorithmsInput"))

    @builtins.property
    @jsii.member(jsii_name="phase1DhGroupNumbersInput")
    def phase1_dh_group_numbers_input(
        self,
    ) -> typing.Optional[typing.List[jsii.Number]]:
        return typing.cast(typing.Optional[typing.List[jsii.Number]], jsii.get(self, "phase1DhGroupNumbersInput"))

    @builtins.property
    @jsii.member(jsii_name="phase1IntegrityAlgorithmsInput")
    def phase1_integrity_algorithms_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "phase1IntegrityAlgorithmsInput"))

    @builtins.property
    @jsii.member(jsii_name="phase2AlgorithmsInput")
    def phase2_algorithms_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "phase2AlgorithmsInput"))

    @builtins.property
    @jsii.member(jsii_name="phase2DhGroupNumbersInput")
    def phase2_dh_group_numbers_input(
        self,
    ) -> typing.Optional[typing.List[jsii.Number]]:
        return typing.cast(typing.Optional[typing.List[jsii.Number]], jsii.get(self, "phase2DhGroupNumbersInput"))

    @builtins.property
    @jsii.member(jsii_name="phase2IntegrityAlgorithmsInput")
    def phase2_integrity_algorithms_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "phase2IntegrityAlgorithmsInput"))

    @builtins.property
    @jsii.member(jsii_name="rekeyTimeInput")
    def rekey_time_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "rekeyTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="childRekeyTime")
    def child_rekey_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "childRekeyTime"))

    @child_rekey_time.setter
    def child_rekey_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e694f6486c74cbeab4edc4f6423d56ac98188fab9411d41541eeb8ab5f2b2c2b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "childRekeyTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dpdDelay")
    def dpd_delay(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "dpdDelay"))

    @dpd_delay.setter
    def dpd_delay(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9809278546031a43fb807e38f15896eacfe09e2c1583ee1d39a97cf723d5620)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dpdDelay", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dpdTimeout")
    def dpd_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "dpdTimeout"))

    @dpd_timeout.setter
    def dpd_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1837f3667d2a8fe66b2d42eb54e6d6d67dec37cb6fcebaa2a823a00ee6774075)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dpdTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ikeLifetime")
    def ike_lifetime(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ikeLifetime"))

    @ike_lifetime.setter
    def ike_lifetime(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41e21702f384dacba68c3d7d2d95c69d6c893645f0354660bed5c9def6625bf0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ikeLifetime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="phase1Algorithms")
    def phase1_algorithms(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "phase1Algorithms"))

    @phase1_algorithms.setter
    def phase1_algorithms(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a43467d84bfc37a6a4e595c41f4d6c9c30894c3ac6e1a4e674997a0ee8df2afb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "phase1Algorithms", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="phase1DhGroupNumbers")
    def phase1_dh_group_numbers(self) -> typing.List[jsii.Number]:
        return typing.cast(typing.List[jsii.Number], jsii.get(self, "phase1DhGroupNumbers"))

    @phase1_dh_group_numbers.setter
    def phase1_dh_group_numbers(self, value: typing.List[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca6d6dd74a2a391d08ad0799a154941150db5c432038fe91aca9cc24e167e656)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "phase1DhGroupNumbers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="phase1IntegrityAlgorithms")
    def phase1_integrity_algorithms(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "phase1IntegrityAlgorithms"))

    @phase1_integrity_algorithms.setter
    def phase1_integrity_algorithms(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6bb396276f6888905c069f5204b8854f84ae09ae7175f40b5f63b2d43d87eb0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "phase1IntegrityAlgorithms", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="phase2Algorithms")
    def phase2_algorithms(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "phase2Algorithms"))

    @phase2_algorithms.setter
    def phase2_algorithms(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a120198d98550b7ccf0a29f6db6aa1a65f8591468a18b4fafa9a375ce7b4010)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "phase2Algorithms", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="phase2DhGroupNumbers")
    def phase2_dh_group_numbers(self) -> typing.List[jsii.Number]:
        return typing.cast(typing.List[jsii.Number], jsii.get(self, "phase2DhGroupNumbers"))

    @phase2_dh_group_numbers.setter
    def phase2_dh_group_numbers(self, value: typing.List[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30138e6759809e39e8182db3c4fcd90a02cbdaa2ace0041f7e602af46b521794)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "phase2DhGroupNumbers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="phase2IntegrityAlgorithms")
    def phase2_integrity_algorithms(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "phase2IntegrityAlgorithms"))

    @phase2_integrity_algorithms.setter
    def phase2_integrity_algorithms(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05dc13f6a5572e354b037783a155ecf1b682d7d79671c4046d8ec5277c86120f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "phase2IntegrityAlgorithms", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rekeyTime")
    def rekey_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rekeyTime"))

    @rekey_time.setter
    def rekey_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e31a7bfb67f1a32f8676774d45f8c8b631c74fee0b7d0931cdeb61318f84332)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rekeyTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[GatewayConnectionTunnelIpsecProperties]:
        return typing.cast(typing.Optional[GatewayConnectionTunnelIpsecProperties], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GatewayConnectionTunnelIpsecProperties],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9e1d36a513f06f91166fd6a6e6052ccb8fefc74d4ca1aa3c237c66c2e7f09a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "GatewayConnectionTunnel",
    "GatewayConnectionTunnelConfig",
    "GatewayConnectionTunnelIpsecAuthPsk",
    "GatewayConnectionTunnelIpsecAuthPskOutputReference",
    "GatewayConnectionTunnelIpsecProperties",
    "GatewayConnectionTunnelIpsecPropertiesOutputReference",
]

publication.publish()

def _typecheckingstub__bcba9d47af2d640b381a57614585e17d61c78e34893161a6bcb3a0e59e4893d0(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    connection_id: builtins.str,
    ipsec_auth_psk: typing.Union[GatewayConnectionTunnelIpsecAuthPsk, typing.Dict[builtins.str, typing.Any]],
    local_address_name: builtins.str,
    name: builtins.str,
    remote_address: builtins.str,
    id: typing.Optional[builtins.str] = None,
    ipsec_properties: typing.Optional[typing.Union[GatewayConnectionTunnelIpsecProperties, typing.Dict[builtins.str, typing.Any]]] = None,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95236e9d369f33914f666fa8076ddef4b5b620b25f4b18ec52b8822131b193aa(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__126516e9f2491501373dc78a2ced217cc6983515585858bddaa97a43be47c46e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f700caa4649526605c5789b4b1af9dbc420a82c8c23deedc54920d5e9b5549cd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a349ea0021d2c6d6de75a59ca14d51e1948a94c4ed9d0daa4dfed83a20b53d5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22991b014c3d2e71d2ea4eecdc4d72c95098523fea98fea667712a8f2f3f7dcb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20fc183698bb25fe3dd18b8951c12e22d0f3fcff5c932fb833788131f196f2b6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6d11a79d0e62a94d31dbeeb1b1d2a1d94139d8c65e2ddf5917626ad2d4a6f99(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    connection_id: builtins.str,
    ipsec_auth_psk: typing.Union[GatewayConnectionTunnelIpsecAuthPsk, typing.Dict[builtins.str, typing.Any]],
    local_address_name: builtins.str,
    name: builtins.str,
    remote_address: builtins.str,
    id: typing.Optional[builtins.str] = None,
    ipsec_properties: typing.Optional[typing.Union[GatewayConnectionTunnelIpsecProperties, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87c835e7d7c5605931c1ca38462874908e77d68cd5b951debc157a3d43ca979a(
    *,
    psk: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__685fc99f2c3e31478dfaba417d0029c9f025f9f6781f1b846b229190d1465d10(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c54073d7ff76d5ff3a7bb48388097398cf24b757cf5ceecdd25321fb42e85b3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e2d2460505ab3151036fc5067cfb416cf9ea5829b3ff70c70b0eba1e32b0f6f(
    value: typing.Optional[GatewayConnectionTunnelIpsecAuthPsk],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a50b18894047098027d5d6be1b8a41d8e32b22c4297ebea79c281f4c838921f4(
    *,
    child_rekey_time: typing.Optional[jsii.Number] = None,
    dpd_delay: typing.Optional[jsii.Number] = None,
    dpd_timeout: typing.Optional[jsii.Number] = None,
    ike_lifetime: typing.Optional[jsii.Number] = None,
    phase1_algorithms: typing.Optional[typing.Sequence[builtins.str]] = None,
    phase1_dh_group_numbers: typing.Optional[typing.Sequence[jsii.Number]] = None,
    phase1_integrity_algorithms: typing.Optional[typing.Sequence[builtins.str]] = None,
    phase2_algorithms: typing.Optional[typing.Sequence[builtins.str]] = None,
    phase2_dh_group_numbers: typing.Optional[typing.Sequence[jsii.Number]] = None,
    phase2_integrity_algorithms: typing.Optional[typing.Sequence[builtins.str]] = None,
    rekey_time: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3ce480a94c93bf5e7f9b3393fc3227f8192dbb60f5168d77e6bd72d78790a0d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e694f6486c74cbeab4edc4f6423d56ac98188fab9411d41541eeb8ab5f2b2c2b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9809278546031a43fb807e38f15896eacfe09e2c1583ee1d39a97cf723d5620(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1837f3667d2a8fe66b2d42eb54e6d6d67dec37cb6fcebaa2a823a00ee6774075(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41e21702f384dacba68c3d7d2d95c69d6c893645f0354660bed5c9def6625bf0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a43467d84bfc37a6a4e595c41f4d6c9c30894c3ac6e1a4e674997a0ee8df2afb(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca6d6dd74a2a391d08ad0799a154941150db5c432038fe91aca9cc24e167e656(
    value: typing.List[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6bb396276f6888905c069f5204b8854f84ae09ae7175f40b5f63b2d43d87eb0a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a120198d98550b7ccf0a29f6db6aa1a65f8591468a18b4fafa9a375ce7b4010(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30138e6759809e39e8182db3c4fcd90a02cbdaa2ace0041f7e602af46b521794(
    value: typing.List[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05dc13f6a5572e354b037783a155ecf1b682d7d79671c4046d8ec5277c86120f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e31a7bfb67f1a32f8676774d45f8c8b631c74fee0b7d0931cdeb61318f84332(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9e1d36a513f06f91166fd6a6e6052ccb8fefc74d4ca1aa3c237c66c2e7f09a2(
    value: typing.Optional[GatewayConnectionTunnelIpsecProperties],
) -> None:
    """Type checking stubs"""
    pass
