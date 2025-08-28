r'''
# `upcloud_loadbalancer_backend`

Refer to the Terraform Registry for docs: [`upcloud_loadbalancer_backend`](https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend).
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


class LoadbalancerBackend(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.loadbalancerBackend.LoadbalancerBackend",
):
    '''Represents a {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend upcloud_loadbalancer_backend}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        loadbalancer: builtins.str,
        name: builtins.str,
        properties: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["LoadbalancerBackendProperties", typing.Dict[builtins.str, typing.Any]]]]] = None,
        resolver_name: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend upcloud_loadbalancer_backend} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param loadbalancer: UUID of the load balancer to which the backend is connected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#loadbalancer LoadbalancerBackend#loadbalancer}
        :param name: The name of the backend. Must be unique within the load balancer service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#name LoadbalancerBackend#name}
        :param properties: properties block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#properties LoadbalancerBackend#properties}
        :param resolver_name: Domain name resolver used with dynamic type members. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#resolver_name LoadbalancerBackend#resolver_name}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a57ef11b06133e84b2cf13365b88e7f2dd34adb8674508adcf3a305129d291be)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = LoadbalancerBackendConfig(
            loadbalancer=loadbalancer,
            name=name,
            properties=properties,
            resolver_name=resolver_name,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a LoadbalancerBackend resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the LoadbalancerBackend to import.
        :param import_from_id: The id of the existing LoadbalancerBackend that should be imported. Refer to the {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the LoadbalancerBackend to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a39303f6431c9b45110a25cf70f07bd7d65ab86e3d142d38f4c3a889e9439f80)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putProperties")
    def put_properties(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["LoadbalancerBackendProperties", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__425dcb0894c6def77121cea82a4b7926cb641081761e4828ac7bf13b99d8c4b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putProperties", [value]))

    @jsii.member(jsii_name="resetProperties")
    def reset_properties(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProperties", []))

    @jsii.member(jsii_name="resetResolverName")
    def reset_resolver_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResolverName", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="members")
    def members(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "members"))

    @builtins.property
    @jsii.member(jsii_name="properties")
    def properties(self) -> "LoadbalancerBackendPropertiesList":
        return typing.cast("LoadbalancerBackendPropertiesList", jsii.get(self, "properties"))

    @builtins.property
    @jsii.member(jsii_name="tlsConfigs")
    def tls_configs(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tlsConfigs"))

    @builtins.property
    @jsii.member(jsii_name="loadbalancerInput")
    def loadbalancer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "loadbalancerInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="propertiesInput")
    def properties_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["LoadbalancerBackendProperties"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["LoadbalancerBackendProperties"]]], jsii.get(self, "propertiesInput"))

    @builtins.property
    @jsii.member(jsii_name="resolverNameInput")
    def resolver_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resolverNameInput"))

    @builtins.property
    @jsii.member(jsii_name="loadbalancer")
    def loadbalancer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "loadbalancer"))

    @loadbalancer.setter
    def loadbalancer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__758a0ce0d7c7b27aef039a1ababb5170b2dcdca319a675ca5481e137f044e6e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "loadbalancer", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de7b9fba80a9bd9724064ce7ebd66895bd34dfa89b05268124ea8a52d91572a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resolverName")
    def resolver_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resolverName"))

    @resolver_name.setter
    def resolver_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d83b8ad74717dbbf2ec7a84d12d1c3f9b89191c4cd0c797584da512a2560f3b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resolverName", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.loadbalancerBackend.LoadbalancerBackendConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "loadbalancer": "loadbalancer",
        "name": "name",
        "properties": "properties",
        "resolver_name": "resolverName",
    },
)
class LoadbalancerBackendConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        loadbalancer: builtins.str,
        name: builtins.str,
        properties: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["LoadbalancerBackendProperties", typing.Dict[builtins.str, typing.Any]]]]] = None,
        resolver_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param loadbalancer: UUID of the load balancer to which the backend is connected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#loadbalancer LoadbalancerBackend#loadbalancer}
        :param name: The name of the backend. Must be unique within the load balancer service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#name LoadbalancerBackend#name}
        :param properties: properties block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#properties LoadbalancerBackend#properties}
        :param resolver_name: Domain name resolver used with dynamic type members. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#resolver_name LoadbalancerBackend#resolver_name}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6200f98d574a6cde907c9b763cf17de76dec005cc13d69bf52a284d828392061)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument loadbalancer", value=loadbalancer, expected_type=type_hints["loadbalancer"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument properties", value=properties, expected_type=type_hints["properties"])
            check_type(argname="argument resolver_name", value=resolver_name, expected_type=type_hints["resolver_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "loadbalancer": loadbalancer,
            "name": name,
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
        if properties is not None:
            self._values["properties"] = properties
        if resolver_name is not None:
            self._values["resolver_name"] = resolver_name

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
    def loadbalancer(self) -> builtins.str:
        '''UUID of the load balancer to which the backend is connected.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#loadbalancer LoadbalancerBackend#loadbalancer}
        '''
        result = self._values.get("loadbalancer")
        assert result is not None, "Required property 'loadbalancer' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the backend. Must be unique within the load balancer service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#name LoadbalancerBackend#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def properties(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["LoadbalancerBackendProperties"]]]:
        '''properties block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#properties LoadbalancerBackend#properties}
        '''
        result = self._values.get("properties")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["LoadbalancerBackendProperties"]]], result)

    @builtins.property
    def resolver_name(self) -> typing.Optional[builtins.str]:
        '''Domain name resolver used with dynamic type members.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#resolver_name LoadbalancerBackend#resolver_name}
        '''
        result = self._values.get("resolver_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerBackendConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.loadbalancerBackend.LoadbalancerBackendProperties",
    jsii_struct_bases=[],
    name_mapping={
        "health_check_expected_status": "healthCheckExpectedStatus",
        "health_check_fall": "healthCheckFall",
        "health_check_interval": "healthCheckInterval",
        "health_check_rise": "healthCheckRise",
        "health_check_tls_verify": "healthCheckTlsVerify",
        "health_check_type": "healthCheckType",
        "health_check_url": "healthCheckUrl",
        "http2_enabled": "http2Enabled",
        "outbound_proxy_protocol": "outboundProxyProtocol",
        "sticky_session_cookie_name": "stickySessionCookieName",
        "timeout_server": "timeoutServer",
        "timeout_tunnel": "timeoutTunnel",
        "tls_enabled": "tlsEnabled",
        "tls_use_system_ca": "tlsUseSystemCa",
        "tls_verify": "tlsVerify",
    },
)
class LoadbalancerBackendProperties:
    def __init__(
        self,
        *,
        health_check_expected_status: typing.Optional[jsii.Number] = None,
        health_check_fall: typing.Optional[jsii.Number] = None,
        health_check_interval: typing.Optional[jsii.Number] = None,
        health_check_rise: typing.Optional[jsii.Number] = None,
        health_check_tls_verify: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        health_check_type: typing.Optional[builtins.str] = None,
        health_check_url: typing.Optional[builtins.str] = None,
        http2_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        outbound_proxy_protocol: typing.Optional[builtins.str] = None,
        sticky_session_cookie_name: typing.Optional[builtins.str] = None,
        timeout_server: typing.Optional[jsii.Number] = None,
        timeout_tunnel: typing.Optional[jsii.Number] = None,
        tls_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tls_use_system_ca: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tls_verify: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param health_check_expected_status: Expected HTTP status code returned by the customer application to mark server as healthy. Ignored for ``tcp`` ``health_check_type``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#health_check_expected_status LoadbalancerBackend#health_check_expected_status}
        :param health_check_fall: Sets how many failed health checks are allowed until the backend member is taken off from the rotation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#health_check_fall LoadbalancerBackend#health_check_fall}
        :param health_check_interval: Interval between health checks in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#health_check_interval LoadbalancerBackend#health_check_interval}
        :param health_check_rise: Sets how many successful health checks are required to put the backend member back into rotation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#health_check_rise LoadbalancerBackend#health_check_rise}
        :param health_check_tls_verify: Enables certificate verification with the system CA certificate bundle. Works with https scheme in health_check_url, otherwise ignored. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#health_check_tls_verify LoadbalancerBackend#health_check_tls_verify}
        :param health_check_type: Health check type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#health_check_type LoadbalancerBackend#health_check_type}
        :param health_check_url: Target path for health check HTTP GET requests. Ignored for ``tcp`` ``health_check_type``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#health_check_url LoadbalancerBackend#health_check_url}
        :param http2_enabled: Allow HTTP/2 connections to backend members by utilizing ALPN extension of TLS protocol, therefore it can only be enabled when tls_enabled is set to true. Note: members should support HTTP/2 for this setting to work. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#http2_enabled LoadbalancerBackend#http2_enabled}
        :param outbound_proxy_protocol: Enable outbound proxy protocol by setting the desired version. Defaults to empty string. Empty string disables proxy protocol. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#outbound_proxy_protocol LoadbalancerBackend#outbound_proxy_protocol}
        :param sticky_session_cookie_name: Sets sticky session cookie name. Empty string disables sticky session. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#sticky_session_cookie_name LoadbalancerBackend#sticky_session_cookie_name}
        :param timeout_server: Backend server timeout in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#timeout_server LoadbalancerBackend#timeout_server}
        :param timeout_tunnel: Maximum inactivity time on the client and server side for tunnels in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#timeout_tunnel LoadbalancerBackend#timeout_tunnel}
        :param tls_enabled: Enables TLS connection from the load balancer to backend servers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#tls_enabled LoadbalancerBackend#tls_enabled}
        :param tls_use_system_ca: If enabled, then the system CA certificate bundle will be used for the certificate verification. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#tls_use_system_ca LoadbalancerBackend#tls_use_system_ca}
        :param tls_verify: Enables backend servers certificate verification. Please make sure that TLS config with the certificate bundle of type authority attached to the backend or ``tls_use_system_ca`` enabled. Note: ``tls_verify`` has preference over ``health_check_tls_verify`` when ``tls_enabled`` in true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#tls_verify LoadbalancerBackend#tls_verify}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb5988403ea7b17ea78d8a97176e2db70e4258ead0d52fc7ab7102412ecccf40)
            check_type(argname="argument health_check_expected_status", value=health_check_expected_status, expected_type=type_hints["health_check_expected_status"])
            check_type(argname="argument health_check_fall", value=health_check_fall, expected_type=type_hints["health_check_fall"])
            check_type(argname="argument health_check_interval", value=health_check_interval, expected_type=type_hints["health_check_interval"])
            check_type(argname="argument health_check_rise", value=health_check_rise, expected_type=type_hints["health_check_rise"])
            check_type(argname="argument health_check_tls_verify", value=health_check_tls_verify, expected_type=type_hints["health_check_tls_verify"])
            check_type(argname="argument health_check_type", value=health_check_type, expected_type=type_hints["health_check_type"])
            check_type(argname="argument health_check_url", value=health_check_url, expected_type=type_hints["health_check_url"])
            check_type(argname="argument http2_enabled", value=http2_enabled, expected_type=type_hints["http2_enabled"])
            check_type(argname="argument outbound_proxy_protocol", value=outbound_proxy_protocol, expected_type=type_hints["outbound_proxy_protocol"])
            check_type(argname="argument sticky_session_cookie_name", value=sticky_session_cookie_name, expected_type=type_hints["sticky_session_cookie_name"])
            check_type(argname="argument timeout_server", value=timeout_server, expected_type=type_hints["timeout_server"])
            check_type(argname="argument timeout_tunnel", value=timeout_tunnel, expected_type=type_hints["timeout_tunnel"])
            check_type(argname="argument tls_enabled", value=tls_enabled, expected_type=type_hints["tls_enabled"])
            check_type(argname="argument tls_use_system_ca", value=tls_use_system_ca, expected_type=type_hints["tls_use_system_ca"])
            check_type(argname="argument tls_verify", value=tls_verify, expected_type=type_hints["tls_verify"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if health_check_expected_status is not None:
            self._values["health_check_expected_status"] = health_check_expected_status
        if health_check_fall is not None:
            self._values["health_check_fall"] = health_check_fall
        if health_check_interval is not None:
            self._values["health_check_interval"] = health_check_interval
        if health_check_rise is not None:
            self._values["health_check_rise"] = health_check_rise
        if health_check_tls_verify is not None:
            self._values["health_check_tls_verify"] = health_check_tls_verify
        if health_check_type is not None:
            self._values["health_check_type"] = health_check_type
        if health_check_url is not None:
            self._values["health_check_url"] = health_check_url
        if http2_enabled is not None:
            self._values["http2_enabled"] = http2_enabled
        if outbound_proxy_protocol is not None:
            self._values["outbound_proxy_protocol"] = outbound_proxy_protocol
        if sticky_session_cookie_name is not None:
            self._values["sticky_session_cookie_name"] = sticky_session_cookie_name
        if timeout_server is not None:
            self._values["timeout_server"] = timeout_server
        if timeout_tunnel is not None:
            self._values["timeout_tunnel"] = timeout_tunnel
        if tls_enabled is not None:
            self._values["tls_enabled"] = tls_enabled
        if tls_use_system_ca is not None:
            self._values["tls_use_system_ca"] = tls_use_system_ca
        if tls_verify is not None:
            self._values["tls_verify"] = tls_verify

    @builtins.property
    def health_check_expected_status(self) -> typing.Optional[jsii.Number]:
        '''Expected HTTP status code returned by the customer application to mark server as healthy. Ignored for ``tcp`` ``health_check_type``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#health_check_expected_status LoadbalancerBackend#health_check_expected_status}
        '''
        result = self._values.get("health_check_expected_status")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def health_check_fall(self) -> typing.Optional[jsii.Number]:
        '''Sets how many failed health checks are allowed until the backend member is taken off from the rotation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#health_check_fall LoadbalancerBackend#health_check_fall}
        '''
        result = self._values.get("health_check_fall")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def health_check_interval(self) -> typing.Optional[jsii.Number]:
        '''Interval between health checks in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#health_check_interval LoadbalancerBackend#health_check_interval}
        '''
        result = self._values.get("health_check_interval")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def health_check_rise(self) -> typing.Optional[jsii.Number]:
        '''Sets how many successful health checks are required to put the backend member back into rotation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#health_check_rise LoadbalancerBackend#health_check_rise}
        '''
        result = self._values.get("health_check_rise")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def health_check_tls_verify(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enables certificate verification with the system CA certificate bundle. Works with https scheme in health_check_url, otherwise ignored.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#health_check_tls_verify LoadbalancerBackend#health_check_tls_verify}
        '''
        result = self._values.get("health_check_tls_verify")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def health_check_type(self) -> typing.Optional[builtins.str]:
        '''Health check type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#health_check_type LoadbalancerBackend#health_check_type}
        '''
        result = self._values.get("health_check_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def health_check_url(self) -> typing.Optional[builtins.str]:
        '''Target path for health check HTTP GET requests. Ignored for ``tcp`` ``health_check_type``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#health_check_url LoadbalancerBackend#health_check_url}
        '''
        result = self._values.get("health_check_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def http2_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allow HTTP/2 connections to backend members by utilizing ALPN extension of TLS protocol, therefore it can only be enabled when tls_enabled is set to true.

        Note: members should support HTTP/2 for this setting to work.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#http2_enabled LoadbalancerBackend#http2_enabled}
        '''
        result = self._values.get("http2_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def outbound_proxy_protocol(self) -> typing.Optional[builtins.str]:
        '''Enable outbound proxy protocol by setting the desired version. Defaults to empty string. Empty string disables proxy protocol.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#outbound_proxy_protocol LoadbalancerBackend#outbound_proxy_protocol}
        '''
        result = self._values.get("outbound_proxy_protocol")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sticky_session_cookie_name(self) -> typing.Optional[builtins.str]:
        '''Sets sticky session cookie name. Empty string disables sticky session.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#sticky_session_cookie_name LoadbalancerBackend#sticky_session_cookie_name}
        '''
        result = self._values.get("sticky_session_cookie_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeout_server(self) -> typing.Optional[jsii.Number]:
        '''Backend server timeout in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#timeout_server LoadbalancerBackend#timeout_server}
        '''
        result = self._values.get("timeout_server")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def timeout_tunnel(self) -> typing.Optional[jsii.Number]:
        '''Maximum inactivity time on the client and server side for tunnels in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#timeout_tunnel LoadbalancerBackend#timeout_tunnel}
        '''
        result = self._values.get("timeout_tunnel")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tls_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enables TLS connection from the load balancer to backend servers.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#tls_enabled LoadbalancerBackend#tls_enabled}
        '''
        result = self._values.get("tls_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tls_use_system_ca(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If enabled, then the system CA certificate bundle will be used for the certificate verification.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#tls_use_system_ca LoadbalancerBackend#tls_use_system_ca}
        '''
        result = self._values.get("tls_use_system_ca")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tls_verify(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enables backend servers certificate verification.

        Please make sure that TLS config with the certificate bundle of type authority attached to the backend or ``tls_use_system_ca`` enabled. Note: ``tls_verify`` has preference over ``health_check_tls_verify`` when ``tls_enabled`` in true.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/loadbalancer_backend#tls_verify LoadbalancerBackend#tls_verify}
        '''
        result = self._values.get("tls_verify")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerBackendProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadbalancerBackendPropertiesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.loadbalancerBackend.LoadbalancerBackendPropertiesList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6466001e8d1ef72578f27d793b879e51bb3e572eaef9521b980d493595bc42c3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "LoadbalancerBackendPropertiesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79f867fbff964aa075654e4e8af16ff600c59120999a45f0bb5d4eebbf7df082)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("LoadbalancerBackendPropertiesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9951e06afb155147ab301d7a3de3cd2fdf2af7a2dd07afb0107d1f31f5a9afe1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f8a6b5225ae6d3e8dbe934b52f44ed3cf6e1d733e66b15339254b7710ecc1bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b068ef6542bae20782fcaa4e350a92c8cd34d45062fcf493a138e97a0b38f86)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[LoadbalancerBackendProperties]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[LoadbalancerBackendProperties]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[LoadbalancerBackendProperties]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8e732b3935e5c2c284f9e0a1a9b80014417767d3cb70421fd39ff444d5c67bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class LoadbalancerBackendPropertiesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.loadbalancerBackend.LoadbalancerBackendPropertiesOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c083897711e36589f6551ae9e4bc07921aadcee7d8ec5d8bee78e03d6160dda)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetHealthCheckExpectedStatus")
    def reset_health_check_expected_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHealthCheckExpectedStatus", []))

    @jsii.member(jsii_name="resetHealthCheckFall")
    def reset_health_check_fall(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHealthCheckFall", []))

    @jsii.member(jsii_name="resetHealthCheckInterval")
    def reset_health_check_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHealthCheckInterval", []))

    @jsii.member(jsii_name="resetHealthCheckRise")
    def reset_health_check_rise(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHealthCheckRise", []))

    @jsii.member(jsii_name="resetHealthCheckTlsVerify")
    def reset_health_check_tls_verify(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHealthCheckTlsVerify", []))

    @jsii.member(jsii_name="resetHealthCheckType")
    def reset_health_check_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHealthCheckType", []))

    @jsii.member(jsii_name="resetHealthCheckUrl")
    def reset_health_check_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHealthCheckUrl", []))

    @jsii.member(jsii_name="resetHttp2Enabled")
    def reset_http2_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttp2Enabled", []))

    @jsii.member(jsii_name="resetOutboundProxyProtocol")
    def reset_outbound_proxy_protocol(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOutboundProxyProtocol", []))

    @jsii.member(jsii_name="resetStickySessionCookieName")
    def reset_sticky_session_cookie_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStickySessionCookieName", []))

    @jsii.member(jsii_name="resetTimeoutServer")
    def reset_timeout_server(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeoutServer", []))

    @jsii.member(jsii_name="resetTimeoutTunnel")
    def reset_timeout_tunnel(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeoutTunnel", []))

    @jsii.member(jsii_name="resetTlsEnabled")
    def reset_tls_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsEnabled", []))

    @jsii.member(jsii_name="resetTlsUseSystemCa")
    def reset_tls_use_system_ca(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsUseSystemCa", []))

    @jsii.member(jsii_name="resetTlsVerify")
    def reset_tls_verify(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsVerify", []))

    @builtins.property
    @jsii.member(jsii_name="healthCheckExpectedStatusInput")
    def health_check_expected_status_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "healthCheckExpectedStatusInput"))

    @builtins.property
    @jsii.member(jsii_name="healthCheckFallInput")
    def health_check_fall_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "healthCheckFallInput"))

    @builtins.property
    @jsii.member(jsii_name="healthCheckIntervalInput")
    def health_check_interval_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "healthCheckIntervalInput"))

    @builtins.property
    @jsii.member(jsii_name="healthCheckRiseInput")
    def health_check_rise_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "healthCheckRiseInput"))

    @builtins.property
    @jsii.member(jsii_name="healthCheckTlsVerifyInput")
    def health_check_tls_verify_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "healthCheckTlsVerifyInput"))

    @builtins.property
    @jsii.member(jsii_name="healthCheckTypeInput")
    def health_check_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "healthCheckTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="healthCheckUrlInput")
    def health_check_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "healthCheckUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="http2EnabledInput")
    def http2_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "http2EnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="outboundProxyProtocolInput")
    def outbound_proxy_protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "outboundProxyProtocolInput"))

    @builtins.property
    @jsii.member(jsii_name="stickySessionCookieNameInput")
    def sticky_session_cookie_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stickySessionCookieNameInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutServerInput")
    def timeout_server_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeoutServerInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutTunnelInput")
    def timeout_tunnel_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeoutTunnelInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsEnabledInput")
    def tls_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "tlsEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsUseSystemCaInput")
    def tls_use_system_ca_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "tlsUseSystemCaInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsVerifyInput")
    def tls_verify_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "tlsVerifyInput"))

    @builtins.property
    @jsii.member(jsii_name="healthCheckExpectedStatus")
    def health_check_expected_status(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "healthCheckExpectedStatus"))

    @health_check_expected_status.setter
    def health_check_expected_status(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7dc3f08a62f7f1c1d999cf41443e8d00ab201864398241c00de9cc77da1c2342)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "healthCheckExpectedStatus", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="healthCheckFall")
    def health_check_fall(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "healthCheckFall"))

    @health_check_fall.setter
    def health_check_fall(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a74c22cd3b86c3c486e323569b855be74e55b4f1661df85a24cd150f9700581)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "healthCheckFall", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="healthCheckInterval")
    def health_check_interval(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "healthCheckInterval"))

    @health_check_interval.setter
    def health_check_interval(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc4a5fcdf1d72f3f8e196e0b9fe2c716f66386010cf2bcefe94884b091dd1099)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "healthCheckInterval", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="healthCheckRise")
    def health_check_rise(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "healthCheckRise"))

    @health_check_rise.setter
    def health_check_rise(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a005b6a89678311ae87bf7a8226f1b8b8341f6f7dbe94f53264244eec7b1941)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "healthCheckRise", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="healthCheckTlsVerify")
    def health_check_tls_verify(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "healthCheckTlsVerify"))

    @health_check_tls_verify.setter
    def health_check_tls_verify(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a1f0408301a8ed0464e766b76ea9c173a85a6c5972f17c867955e8f12d24892)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "healthCheckTlsVerify", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="healthCheckType")
    def health_check_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "healthCheckType"))

    @health_check_type.setter
    def health_check_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8069e619c5eafcd61405a9b14ccbb5acc557f594802c36aa8bfd7d0fd8ff0219)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "healthCheckType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="healthCheckUrl")
    def health_check_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "healthCheckUrl"))

    @health_check_url.setter
    def health_check_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39f4a5b6a60297078707410bf16c529278fa67e401d14af087347f4acdc4f238)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "healthCheckUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="http2Enabled")
    def http2_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "http2Enabled"))

    @http2_enabled.setter
    def http2_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0ed74c710cac92ea40127eb8683ef34d63adf6cf079484e9ba4e70ae1d9c121)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "http2Enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="outboundProxyProtocol")
    def outbound_proxy_protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outboundProxyProtocol"))

    @outbound_proxy_protocol.setter
    def outbound_proxy_protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__643632d762dde3bfa52ccccc383516eae69f64de4c971e85aaa719e291c1c0fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "outboundProxyProtocol", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stickySessionCookieName")
    def sticky_session_cookie_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stickySessionCookieName"))

    @sticky_session_cookie_name.setter
    def sticky_session_cookie_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da3ab1d8ffd0ee740d498a68367ab415a83ea5bb95a96b7bca9efb4ce8d99490)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stickySessionCookieName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeoutServer")
    def timeout_server(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeoutServer"))

    @timeout_server.setter
    def timeout_server(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62977787f77a98958c7b1c163fc10ef2d04d5473932b93993b385e7a7f4725a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeoutServer", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeoutTunnel")
    def timeout_tunnel(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeoutTunnel"))

    @timeout_tunnel.setter
    def timeout_tunnel(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd7554673f8db1f54b33f3b8832599eb58807a0023a40109ca959f715cf36c9b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeoutTunnel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsEnabled")
    def tls_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "tlsEnabled"))

    @tls_enabled.setter
    def tls_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3971da5b5c90f1fd23ac2242c668f5d56a0071530ac27f4ec552f8ec4ce9ee2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsUseSystemCa")
    def tls_use_system_ca(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "tlsUseSystemCa"))

    @tls_use_system_ca.setter
    def tls_use_system_ca(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97f6e28d7e94f7b38cfe76b70291b8c0170c52b48c78b10dc8f76b4703c093e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsUseSystemCa", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsVerify")
    def tls_verify(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "tlsVerify"))

    @tls_verify.setter
    def tls_verify(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d060a9595c4cfc7ea56c1c33bf629d6166ba1a8b052484fd102442b53a67224)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsVerify", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadbalancerBackendProperties]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadbalancerBackendProperties]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadbalancerBackendProperties]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8c6fb57a71c2e0e202ceab15eb8b409d80557a71150004a0caaf083b5bb1cb5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "LoadbalancerBackend",
    "LoadbalancerBackendConfig",
    "LoadbalancerBackendProperties",
    "LoadbalancerBackendPropertiesList",
    "LoadbalancerBackendPropertiesOutputReference",
]

publication.publish()

def _typecheckingstub__a57ef11b06133e84b2cf13365b88e7f2dd34adb8674508adcf3a305129d291be(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    loadbalancer: builtins.str,
    name: builtins.str,
    properties: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[LoadbalancerBackendProperties, typing.Dict[builtins.str, typing.Any]]]]] = None,
    resolver_name: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__a39303f6431c9b45110a25cf70f07bd7d65ab86e3d142d38f4c3a889e9439f80(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__425dcb0894c6def77121cea82a4b7926cb641081761e4828ac7bf13b99d8c4b4(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[LoadbalancerBackendProperties, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__758a0ce0d7c7b27aef039a1ababb5170b2dcdca319a675ca5481e137f044e6e5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de7b9fba80a9bd9724064ce7ebd66895bd34dfa89b05268124ea8a52d91572a5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d83b8ad74717dbbf2ec7a84d12d1c3f9b89191c4cd0c797584da512a2560f3b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6200f98d574a6cde907c9b763cf17de76dec005cc13d69bf52a284d828392061(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    loadbalancer: builtins.str,
    name: builtins.str,
    properties: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[LoadbalancerBackendProperties, typing.Dict[builtins.str, typing.Any]]]]] = None,
    resolver_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb5988403ea7b17ea78d8a97176e2db70e4258ead0d52fc7ab7102412ecccf40(
    *,
    health_check_expected_status: typing.Optional[jsii.Number] = None,
    health_check_fall: typing.Optional[jsii.Number] = None,
    health_check_interval: typing.Optional[jsii.Number] = None,
    health_check_rise: typing.Optional[jsii.Number] = None,
    health_check_tls_verify: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    health_check_type: typing.Optional[builtins.str] = None,
    health_check_url: typing.Optional[builtins.str] = None,
    http2_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    outbound_proxy_protocol: typing.Optional[builtins.str] = None,
    sticky_session_cookie_name: typing.Optional[builtins.str] = None,
    timeout_server: typing.Optional[jsii.Number] = None,
    timeout_tunnel: typing.Optional[jsii.Number] = None,
    tls_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tls_use_system_ca: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tls_verify: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6466001e8d1ef72578f27d793b879e51bb3e572eaef9521b980d493595bc42c3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79f867fbff964aa075654e4e8af16ff600c59120999a45f0bb5d4eebbf7df082(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9951e06afb155147ab301d7a3de3cd2fdf2af7a2dd07afb0107d1f31f5a9afe1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f8a6b5225ae6d3e8dbe934b52f44ed3cf6e1d733e66b15339254b7710ecc1bc(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b068ef6542bae20782fcaa4e350a92c8cd34d45062fcf493a138e97a0b38f86(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8e732b3935e5c2c284f9e0a1a9b80014417767d3cb70421fd39ff444d5c67bf(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[LoadbalancerBackendProperties]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c083897711e36589f6551ae9e4bc07921aadcee7d8ec5d8bee78e03d6160dda(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7dc3f08a62f7f1c1d999cf41443e8d00ab201864398241c00de9cc77da1c2342(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a74c22cd3b86c3c486e323569b855be74e55b4f1661df85a24cd150f9700581(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc4a5fcdf1d72f3f8e196e0b9fe2c716f66386010cf2bcefe94884b091dd1099(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a005b6a89678311ae87bf7a8226f1b8b8341f6f7dbe94f53264244eec7b1941(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a1f0408301a8ed0464e766b76ea9c173a85a6c5972f17c867955e8f12d24892(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8069e619c5eafcd61405a9b14ccbb5acc557f594802c36aa8bfd7d0fd8ff0219(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39f4a5b6a60297078707410bf16c529278fa67e401d14af087347f4acdc4f238(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0ed74c710cac92ea40127eb8683ef34d63adf6cf079484e9ba4e70ae1d9c121(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__643632d762dde3bfa52ccccc383516eae69f64de4c971e85aaa719e291c1c0fa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da3ab1d8ffd0ee740d498a68367ab415a83ea5bb95a96b7bca9efb4ce8d99490(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62977787f77a98958c7b1c163fc10ef2d04d5473932b93993b385e7a7f4725a2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd7554673f8db1f54b33f3b8832599eb58807a0023a40109ca959f715cf36c9b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3971da5b5c90f1fd23ac2242c668f5d56a0071530ac27f4ec552f8ec4ce9ee2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97f6e28d7e94f7b38cfe76b70291b8c0170c52b48c78b10dc8f76b4703c093e9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d060a9595c4cfc7ea56c1c33bf629d6166ba1a8b052484fd102442b53a67224(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8c6fb57a71c2e0e202ceab15eb8b409d80557a71150004a0caaf083b5bb1cb5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadbalancerBackendProperties]],
) -> None:
    """Type checking stubs"""
    pass
