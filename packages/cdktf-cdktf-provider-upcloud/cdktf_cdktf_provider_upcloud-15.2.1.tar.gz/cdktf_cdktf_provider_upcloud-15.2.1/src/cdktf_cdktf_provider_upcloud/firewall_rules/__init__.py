r'''
# `upcloud_firewall_rules`

Refer to the Terraform Registry for docs: [`upcloud_firewall_rules`](https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules).
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


class FirewallRules(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.firewallRules.FirewallRules",
):
    '''Represents a {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules upcloud_firewall_rules}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        server_id: builtins.str,
        firewall_rule: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["FirewallRulesFirewallRule", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules upcloud_firewall_rules} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param server_id: The UUID of the server to be protected with the firewall rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#server_id FirewallRules#server_id}
        :param firewall_rule: firewall_rule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#firewall_rule FirewallRules#firewall_rule}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3dd7e6461a1cb9b9f531749add09b10411da35a685dbccc19e6eae9f39484aba)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = FirewallRulesConfig(
            server_id=server_id,
            firewall_rule=firewall_rule,
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
        '''Generates CDKTF code for importing a FirewallRules resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the FirewallRules to import.
        :param import_from_id: The id of the existing FirewallRules that should be imported. Refer to the {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the FirewallRules to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3291f4d6d253a7020d12aa2a547bf6bf9304edc0dc3b1ac8a09e0f89e9294c92)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putFirewallRule")
    def put_firewall_rule(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["FirewallRulesFirewallRule", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2bed86233110e50c69609c787a79a37508bd2b39f8c7dd910fe89f65bd5f40d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putFirewallRule", [value]))

    @jsii.member(jsii_name="resetFirewallRule")
    def reset_firewall_rule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFirewallRule", []))

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
    @jsii.member(jsii_name="firewallRule")
    def firewall_rule(self) -> "FirewallRulesFirewallRuleList":
        return typing.cast("FirewallRulesFirewallRuleList", jsii.get(self, "firewallRule"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="firewallRuleInput")
    def firewall_rule_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["FirewallRulesFirewallRule"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["FirewallRulesFirewallRule"]]], jsii.get(self, "firewallRuleInput"))

    @builtins.property
    @jsii.member(jsii_name="serverIdInput")
    def server_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverIdInput"))

    @builtins.property
    @jsii.member(jsii_name="serverId")
    def server_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverId"))

    @server_id.setter
    def server_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58d36060cbaa53ac44e8eee4a67ae3fb2b894aa4b92b5809a705a5d3073ea15f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.firewallRules.FirewallRulesConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "server_id": "serverId",
        "firewall_rule": "firewallRule",
    },
)
class FirewallRulesConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        server_id: builtins.str,
        firewall_rule: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["FirewallRulesFirewallRule", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param server_id: The UUID of the server to be protected with the firewall rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#server_id FirewallRules#server_id}
        :param firewall_rule: firewall_rule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#firewall_rule FirewallRules#firewall_rule}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ead3fa66c8a64e9f8e657b68d25827ef2a936835b7d7dd2169abd3f3a1e7295)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument server_id", value=server_id, expected_type=type_hints["server_id"])
            check_type(argname="argument firewall_rule", value=firewall_rule, expected_type=type_hints["firewall_rule"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "server_id": server_id,
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
        if firewall_rule is not None:
            self._values["firewall_rule"] = firewall_rule

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
    def server_id(self) -> builtins.str:
        '''The UUID of the server to be protected with the firewall rules.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#server_id FirewallRules#server_id}
        '''
        result = self._values.get("server_id")
        assert result is not None, "Required property 'server_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def firewall_rule(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["FirewallRulesFirewallRule"]]]:
        '''firewall_rule block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#firewall_rule FirewallRules#firewall_rule}
        '''
        result = self._values.get("firewall_rule")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["FirewallRulesFirewallRule"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FirewallRulesConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.firewallRules.FirewallRulesFirewallRule",
    jsii_struct_bases=[],
    name_mapping={
        "action": "action",
        "direction": "direction",
        "comment": "comment",
        "destination_address_end": "destinationAddressEnd",
        "destination_address_start": "destinationAddressStart",
        "destination_port_end": "destinationPortEnd",
        "destination_port_start": "destinationPortStart",
        "family": "family",
        "icmp_type": "icmpType",
        "protocol": "protocol",
        "source_address_end": "sourceAddressEnd",
        "source_address_start": "sourceAddressStart",
        "source_port_end": "sourcePortEnd",
        "source_port_start": "sourcePortStart",
    },
)
class FirewallRulesFirewallRule:
    def __init__(
        self,
        *,
        action: builtins.str,
        direction: builtins.str,
        comment: typing.Optional[builtins.str] = None,
        destination_address_end: typing.Optional[builtins.str] = None,
        destination_address_start: typing.Optional[builtins.str] = None,
        destination_port_end: typing.Optional[builtins.str] = None,
        destination_port_start: typing.Optional[builtins.str] = None,
        family: typing.Optional[builtins.str] = None,
        icmp_type: typing.Optional[builtins.str] = None,
        protocol: typing.Optional[builtins.str] = None,
        source_address_end: typing.Optional[builtins.str] = None,
        source_address_start: typing.Optional[builtins.str] = None,
        source_port_end: typing.Optional[builtins.str] = None,
        source_port_start: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param action: Action to take if the rule conditions are met. Valid values ``accept | drop``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#action FirewallRules#action}
        :param direction: The direction of network traffic this rule will be applied to. Valid values are ``in`` and ``out``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#direction FirewallRules#direction}
        :param comment: A comment for the rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#comment FirewallRules#comment}
        :param destination_address_end: The destination address range ends from this address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#destination_address_end FirewallRules#destination_address_end}
        :param destination_address_start: The destination address range starts from this address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#destination_address_start FirewallRules#destination_address_start}
        :param destination_port_end: The destination port range ends from this port number. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#destination_port_end FirewallRules#destination_port_end}
        :param destination_port_start: The destination port range starts from this port number. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#destination_port_start FirewallRules#destination_port_start}
        :param family: The address family of new firewall rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#family FirewallRules#family}
        :param icmp_type: The ICMP type of the rule. Only valid if protocol is ICMP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#icmp_type FirewallRules#icmp_type}
        :param protocol: The protocol of the rule. Possible values are `` (empty), ``tcp``, ``udp``, ``icmp``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#protocol FirewallRules#protocol}
        :param source_address_end: The source address range ends from this address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#source_address_end FirewallRules#source_address_end}
        :param source_address_start: The source address range starts from this address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#source_address_start FirewallRules#source_address_start}
        :param source_port_end: The source port range ends from this port number. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#source_port_end FirewallRules#source_port_end}
        :param source_port_start: The source port range starts from this port number. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#source_port_start FirewallRules#source_port_start}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b77e978fb66d25b46f06da19493b15c4f42527dec58b7335729cf86141901af)
            check_type(argname="argument action", value=action, expected_type=type_hints["action"])
            check_type(argname="argument direction", value=direction, expected_type=type_hints["direction"])
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument destination_address_end", value=destination_address_end, expected_type=type_hints["destination_address_end"])
            check_type(argname="argument destination_address_start", value=destination_address_start, expected_type=type_hints["destination_address_start"])
            check_type(argname="argument destination_port_end", value=destination_port_end, expected_type=type_hints["destination_port_end"])
            check_type(argname="argument destination_port_start", value=destination_port_start, expected_type=type_hints["destination_port_start"])
            check_type(argname="argument family", value=family, expected_type=type_hints["family"])
            check_type(argname="argument icmp_type", value=icmp_type, expected_type=type_hints["icmp_type"])
            check_type(argname="argument protocol", value=protocol, expected_type=type_hints["protocol"])
            check_type(argname="argument source_address_end", value=source_address_end, expected_type=type_hints["source_address_end"])
            check_type(argname="argument source_address_start", value=source_address_start, expected_type=type_hints["source_address_start"])
            check_type(argname="argument source_port_end", value=source_port_end, expected_type=type_hints["source_port_end"])
            check_type(argname="argument source_port_start", value=source_port_start, expected_type=type_hints["source_port_start"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "action": action,
            "direction": direction,
        }
        if comment is not None:
            self._values["comment"] = comment
        if destination_address_end is not None:
            self._values["destination_address_end"] = destination_address_end
        if destination_address_start is not None:
            self._values["destination_address_start"] = destination_address_start
        if destination_port_end is not None:
            self._values["destination_port_end"] = destination_port_end
        if destination_port_start is not None:
            self._values["destination_port_start"] = destination_port_start
        if family is not None:
            self._values["family"] = family
        if icmp_type is not None:
            self._values["icmp_type"] = icmp_type
        if protocol is not None:
            self._values["protocol"] = protocol
        if source_address_end is not None:
            self._values["source_address_end"] = source_address_end
        if source_address_start is not None:
            self._values["source_address_start"] = source_address_start
        if source_port_end is not None:
            self._values["source_port_end"] = source_port_end
        if source_port_start is not None:
            self._values["source_port_start"] = source_port_start

    @builtins.property
    def action(self) -> builtins.str:
        '''Action to take if the rule conditions are met. Valid values ``accept | drop``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#action FirewallRules#action}
        '''
        result = self._values.get("action")
        assert result is not None, "Required property 'action' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def direction(self) -> builtins.str:
        '''The direction of network traffic this rule will be applied to. Valid values are ``in`` and ``out``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#direction FirewallRules#direction}
        '''
        result = self._values.get("direction")
        assert result is not None, "Required property 'direction' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''A comment for the rule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#comment FirewallRules#comment}
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def destination_address_end(self) -> typing.Optional[builtins.str]:
        '''The destination address range ends from this address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#destination_address_end FirewallRules#destination_address_end}
        '''
        result = self._values.get("destination_address_end")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def destination_address_start(self) -> typing.Optional[builtins.str]:
        '''The destination address range starts from this address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#destination_address_start FirewallRules#destination_address_start}
        '''
        result = self._values.get("destination_address_start")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def destination_port_end(self) -> typing.Optional[builtins.str]:
        '''The destination port range ends from this port number.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#destination_port_end FirewallRules#destination_port_end}
        '''
        result = self._values.get("destination_port_end")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def destination_port_start(self) -> typing.Optional[builtins.str]:
        '''The destination port range starts from this port number.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#destination_port_start FirewallRules#destination_port_start}
        '''
        result = self._values.get("destination_port_start")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def family(self) -> typing.Optional[builtins.str]:
        '''The address family of new firewall rule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#family FirewallRules#family}
        '''
        result = self._values.get("family")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def icmp_type(self) -> typing.Optional[builtins.str]:
        '''The ICMP type of the rule. Only valid if protocol is ICMP.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#icmp_type FirewallRules#icmp_type}
        '''
        result = self._values.get("icmp_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def protocol(self) -> typing.Optional[builtins.str]:
        '''The protocol of the rule. Possible values are `` (empty), ``tcp``, ``udp``, ``icmp``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#protocol FirewallRules#protocol}
        '''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_address_end(self) -> typing.Optional[builtins.str]:
        '''The source address range ends from this address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#source_address_end FirewallRules#source_address_end}
        '''
        result = self._values.get("source_address_end")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_address_start(self) -> typing.Optional[builtins.str]:
        '''The source address range starts from this address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#source_address_start FirewallRules#source_address_start}
        '''
        result = self._values.get("source_address_start")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_port_end(self) -> typing.Optional[builtins.str]:
        '''The source port range ends from this port number.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#source_port_end FirewallRules#source_port_end}
        '''
        result = self._values.get("source_port_end")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_port_start(self) -> typing.Optional[builtins.str]:
        '''The source port range starts from this port number.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/firewall_rules#source_port_start FirewallRules#source_port_start}
        '''
        result = self._values.get("source_port_start")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FirewallRulesFirewallRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FirewallRulesFirewallRuleList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.firewallRules.FirewallRulesFirewallRuleList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__be9a3286793c7b780c1f2211a4b8454dc7ce78580680fec420e340a7243622a1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "FirewallRulesFirewallRuleOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__279903c33d49c86617e4f2180e58a1a6e251e7f5da5e24a185815a10ca8c71ef)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("FirewallRulesFirewallRuleOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8c0667b5246b36656b65a0197f71b1be7dd4913264b18a8f964bb03d46e0f31)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2f485ce2be519a06464be51456be1a6082db33afb0dc146c5295a7ce6327267a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b5ed2e7c1ca8241abef1bcdfd639eda4a1c8b13b12614419551aba8da56714d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FirewallRulesFirewallRule]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FirewallRulesFirewallRule]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FirewallRulesFirewallRule]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86aa44126bbd5ae12ad54058822b7caba978de31968f8df12c8a012a7642896c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class FirewallRulesFirewallRuleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.firewallRules.FirewallRulesFirewallRuleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f63ab3f124af332601c8d24ac1dbed88ef0997982f15c6c057a556087d9b15c0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetDestinationAddressEnd")
    def reset_destination_address_end(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestinationAddressEnd", []))

    @jsii.member(jsii_name="resetDestinationAddressStart")
    def reset_destination_address_start(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestinationAddressStart", []))

    @jsii.member(jsii_name="resetDestinationPortEnd")
    def reset_destination_port_end(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestinationPortEnd", []))

    @jsii.member(jsii_name="resetDestinationPortStart")
    def reset_destination_port_start(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestinationPortStart", []))

    @jsii.member(jsii_name="resetFamily")
    def reset_family(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFamily", []))

    @jsii.member(jsii_name="resetIcmpType")
    def reset_icmp_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIcmpType", []))

    @jsii.member(jsii_name="resetProtocol")
    def reset_protocol(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProtocol", []))

    @jsii.member(jsii_name="resetSourceAddressEnd")
    def reset_source_address_end(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceAddressEnd", []))

    @jsii.member(jsii_name="resetSourceAddressStart")
    def reset_source_address_start(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceAddressStart", []))

    @jsii.member(jsii_name="resetSourcePortEnd")
    def reset_source_port_end(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourcePortEnd", []))

    @jsii.member(jsii_name="resetSourcePortStart")
    def reset_source_port_start(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourcePortStart", []))

    @builtins.property
    @jsii.member(jsii_name="actionInput")
    def action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionInput"))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="destinationAddressEndInput")
    def destination_address_end_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationAddressEndInput"))

    @builtins.property
    @jsii.member(jsii_name="destinationAddressStartInput")
    def destination_address_start_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationAddressStartInput"))

    @builtins.property
    @jsii.member(jsii_name="destinationPortEndInput")
    def destination_port_end_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationPortEndInput"))

    @builtins.property
    @jsii.member(jsii_name="destinationPortStartInput")
    def destination_port_start_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationPortStartInput"))

    @builtins.property
    @jsii.member(jsii_name="directionInput")
    def direction_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "directionInput"))

    @builtins.property
    @jsii.member(jsii_name="familyInput")
    def family_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "familyInput"))

    @builtins.property
    @jsii.member(jsii_name="icmpTypeInput")
    def icmp_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "icmpTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="protocolInput")
    def protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "protocolInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceAddressEndInput")
    def source_address_end_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceAddressEndInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceAddressStartInput")
    def source_address_start_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceAddressStartInput"))

    @builtins.property
    @jsii.member(jsii_name="sourcePortEndInput")
    def source_port_end_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourcePortEndInput"))

    @builtins.property
    @jsii.member(jsii_name="sourcePortStartInput")
    def source_port_start_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourcePortStartInput"))

    @builtins.property
    @jsii.member(jsii_name="action")
    def action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "action"))

    @action.setter
    def action(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf5d77e9b808a5b2988f3a6654c3e9139819ac431e2f95c9e5cff41dde9c5f94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "action", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b91f92cb088fa23c430b161883c5372b64c80e7695a5dc0d56709ff8b250595)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="destinationAddressEnd")
    def destination_address_end(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationAddressEnd"))

    @destination_address_end.setter
    def destination_address_end(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f7eb292b90d80a698dd8379cf4a1b7720cbb26f3218dd2c5628a524de2c37d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destinationAddressEnd", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="destinationAddressStart")
    def destination_address_start(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationAddressStart"))

    @destination_address_start.setter
    def destination_address_start(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20587ec84eb611c98035fea7ea314b6143d56185b4a64fbc8230a2c4a0fbafa2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destinationAddressStart", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="destinationPortEnd")
    def destination_port_end(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationPortEnd"))

    @destination_port_end.setter
    def destination_port_end(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dabf172600ce549d515b972b8ea8e7805bd96e407de84a02cf2fceff3f8c3a83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destinationPortEnd", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="destinationPortStart")
    def destination_port_start(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationPortStart"))

    @destination_port_start.setter
    def destination_port_start(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d88e34c4e91fb7cdbc15f89e46e2e94fff59570bf5406589c1a3e23f26b49b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destinationPortStart", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="direction")
    def direction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "direction"))

    @direction.setter
    def direction(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__532bebe01b1fe3ad35f6fecfcb8b05d23ff4766c67436324b523c33c46172fd1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "direction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="family")
    def family(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "family"))

    @family.setter
    def family(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc82326e5f373043d64665f6c6a8a3cf83c2b0bedc6592edef0116bf89ced524)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "family", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="icmpType")
    def icmp_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "icmpType"))

    @icmp_type.setter
    def icmp_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c98da5a7a41b0a2eb46eaa7d3a966c5f1f56dfa2c275c6ba075aeffa7383fc3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "icmpType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="protocol")
    def protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "protocol"))

    @protocol.setter
    def protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90dd48388c4582e71016f824db682a0e6badaaa68192d2f75fd11df31454bcec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "protocol", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceAddressEnd")
    def source_address_end(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceAddressEnd"))

    @source_address_end.setter
    def source_address_end(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64e12a12a20cdee9fd9c4ab584665fd7d2c5e0ef17a986482ca1ffc3ccd2e8d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceAddressEnd", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceAddressStart")
    def source_address_start(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceAddressStart"))

    @source_address_start.setter
    def source_address_start(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65e8b63f6139968901f5dd1be0e577d5020648bf37a8cfc699f60b84ec4f1925)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceAddressStart", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourcePortEnd")
    def source_port_end(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourcePortEnd"))

    @source_port_end.setter
    def source_port_end(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49eacef077b5828707589d620d969195fb255d20caf3d33a2091f58f3d299733)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourcePortEnd", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourcePortStart")
    def source_port_start(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourcePortStart"))

    @source_port_start.setter
    def source_port_start(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4e448528c042dda5a3679431eace4acbc8a79820637256ca64a7cb946c21d9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourcePortStart", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[FirewallRulesFirewallRule, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[FirewallRulesFirewallRule, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[FirewallRulesFirewallRule, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__caf76bc209bb05575c5fe33f2a065f78e22a3cad53fce656b4371ab3233464d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "FirewallRules",
    "FirewallRulesConfig",
    "FirewallRulesFirewallRule",
    "FirewallRulesFirewallRuleList",
    "FirewallRulesFirewallRuleOutputReference",
]

publication.publish()

def _typecheckingstub__3dd7e6461a1cb9b9f531749add09b10411da35a685dbccc19e6eae9f39484aba(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    server_id: builtins.str,
    firewall_rule: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[FirewallRulesFirewallRule, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__3291f4d6d253a7020d12aa2a547bf6bf9304edc0dc3b1ac8a09e0f89e9294c92(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2bed86233110e50c69609c787a79a37508bd2b39f8c7dd910fe89f65bd5f40d(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[FirewallRulesFirewallRule, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58d36060cbaa53ac44e8eee4a67ae3fb2b894aa4b92b5809a705a5d3073ea15f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ead3fa66c8a64e9f8e657b68d25827ef2a936835b7d7dd2169abd3f3a1e7295(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    server_id: builtins.str,
    firewall_rule: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[FirewallRulesFirewallRule, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b77e978fb66d25b46f06da19493b15c4f42527dec58b7335729cf86141901af(
    *,
    action: builtins.str,
    direction: builtins.str,
    comment: typing.Optional[builtins.str] = None,
    destination_address_end: typing.Optional[builtins.str] = None,
    destination_address_start: typing.Optional[builtins.str] = None,
    destination_port_end: typing.Optional[builtins.str] = None,
    destination_port_start: typing.Optional[builtins.str] = None,
    family: typing.Optional[builtins.str] = None,
    icmp_type: typing.Optional[builtins.str] = None,
    protocol: typing.Optional[builtins.str] = None,
    source_address_end: typing.Optional[builtins.str] = None,
    source_address_start: typing.Optional[builtins.str] = None,
    source_port_end: typing.Optional[builtins.str] = None,
    source_port_start: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be9a3286793c7b780c1f2211a4b8454dc7ce78580680fec420e340a7243622a1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__279903c33d49c86617e4f2180e58a1a6e251e7f5da5e24a185815a10ca8c71ef(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8c0667b5246b36656b65a0197f71b1be7dd4913264b18a8f964bb03d46e0f31(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f485ce2be519a06464be51456be1a6082db33afb0dc146c5295a7ce6327267a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5ed2e7c1ca8241abef1bcdfd639eda4a1c8b13b12614419551aba8da56714d1(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86aa44126bbd5ae12ad54058822b7caba978de31968f8df12c8a012a7642896c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FirewallRulesFirewallRule]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f63ab3f124af332601c8d24ac1dbed88ef0997982f15c6c057a556087d9b15c0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf5d77e9b808a5b2988f3a6654c3e9139819ac431e2f95c9e5cff41dde9c5f94(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b91f92cb088fa23c430b161883c5372b64c80e7695a5dc0d56709ff8b250595(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f7eb292b90d80a698dd8379cf4a1b7720cbb26f3218dd2c5628a524de2c37d0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20587ec84eb611c98035fea7ea314b6143d56185b4a64fbc8230a2c4a0fbafa2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dabf172600ce549d515b972b8ea8e7805bd96e407de84a02cf2fceff3f8c3a83(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d88e34c4e91fb7cdbc15f89e46e2e94fff59570bf5406589c1a3e23f26b49b6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__532bebe01b1fe3ad35f6fecfcb8b05d23ff4766c67436324b523c33c46172fd1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc82326e5f373043d64665f6c6a8a3cf83c2b0bedc6592edef0116bf89ced524(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c98da5a7a41b0a2eb46eaa7d3a966c5f1f56dfa2c275c6ba075aeffa7383fc3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90dd48388c4582e71016f824db682a0e6badaaa68192d2f75fd11df31454bcec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64e12a12a20cdee9fd9c4ab584665fd7d2c5e0ef17a986482ca1ffc3ccd2e8d5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65e8b63f6139968901f5dd1be0e577d5020648bf37a8cfc699f60b84ec4f1925(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49eacef077b5828707589d620d969195fb255d20caf3d33a2091f58f3d299733(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4e448528c042dda5a3679431eace4acbc8a79820637256ca64a7cb946c21d9f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__caf76bc209bb05575c5fe33f2a065f78e22a3cad53fce656b4371ab3233464d7(
    value: typing.Optional[typing.Union[FirewallRulesFirewallRule, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass
