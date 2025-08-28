r'''
# `upcloud_managed_database_valkey`

Refer to the Terraform Registry for docs: [`upcloud_managed_database_valkey`](https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey).
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


class ManagedDatabaseValkey(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseValkey.ManagedDatabaseValkey",
):
    '''Represents a {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey upcloud_managed_database_valkey}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        plan: builtins.str,
        title: builtins.str,
        zone: builtins.str,
        id: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        maintenance_window_dow: typing.Optional[builtins.str] = None,
        maintenance_window_time: typing.Optional[builtins.str] = None,
        network: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedDatabaseValkeyNetwork", typing.Dict[builtins.str, typing.Any]]]]] = None,
        powered: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        properties: typing.Optional[typing.Union["ManagedDatabaseValkeyProperties", typing.Dict[builtins.str, typing.Any]]] = None,
        termination_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey upcloud_managed_database_valkey} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Name of the service. The name is used as a prefix for the logical hostname. Must be unique within an account Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#name ManagedDatabaseValkey#name}
        :param plan: Service plan to use. This determines how much resources the instance will have. You can list available plans with ``upctl database plans <type>``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#plan ManagedDatabaseValkey#plan}
        :param title: Title of a managed database instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#title ManagedDatabaseValkey#title}
        :param zone: Zone where the instance resides, e.g. ``de-fra1``. You can list available zones with ``upctl zone list``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#zone ManagedDatabaseValkey#zone}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#id ManagedDatabaseValkey#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param labels: User defined key-value pairs to classify the managed database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#labels ManagedDatabaseValkey#labels}
        :param maintenance_window_dow: Maintenance window day of week. Lower case weekday name (monday, tuesday, ...). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#maintenance_window_dow ManagedDatabaseValkey#maintenance_window_dow}
        :param maintenance_window_time: Maintenance window UTC time in hh:mm:ss format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#maintenance_window_time ManagedDatabaseValkey#maintenance_window_time}
        :param network: network block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#network ManagedDatabaseValkey#network}
        :param powered: The administrative power state of the service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#powered ManagedDatabaseValkey#powered}
        :param properties: properties block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#properties ManagedDatabaseValkey#properties}
        :param termination_protection: If set to true, prevents the managed service from being powered off, or deleted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#termination_protection ManagedDatabaseValkey#termination_protection}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9ca96a3d0255aab5bd629d642e8855d0ea99f8657e2d22de939cb10aa9e11a4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ManagedDatabaseValkeyConfig(
            name=name,
            plan=plan,
            title=title,
            zone=zone,
            id=id,
            labels=labels,
            maintenance_window_dow=maintenance_window_dow,
            maintenance_window_time=maintenance_window_time,
            network=network,
            powered=powered,
            properties=properties,
            termination_protection=termination_protection,
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
        '''Generates CDKTF code for importing a ManagedDatabaseValkey resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ManagedDatabaseValkey to import.
        :param import_from_id: The id of the existing ManagedDatabaseValkey that should be imported. Refer to the {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ManagedDatabaseValkey to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9aedfd54b5c8b1f9918c7d3df38964719bab01ca5620baa0cdacd432478b79a7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putNetwork")
    def put_network(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedDatabaseValkeyNetwork", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d39301ce9e83b0c46471cc2e091a974add7699ff0499897b02f5890d167025c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNetwork", [value]))

    @jsii.member(jsii_name="putProperties")
    def put_properties(
        self,
        *,
        automatic_utility_network_ip_filter: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        backup_hour: typing.Optional[jsii.Number] = None,
        backup_minute: typing.Optional[jsii.Number] = None,
        frequent_snapshots: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ip_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
        migration: typing.Optional[typing.Union["ManagedDatabaseValkeyPropertiesMigration", typing.Dict[builtins.str, typing.Any]]] = None,
        public_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        service_log: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        valkey_acl_channels_default: typing.Optional[builtins.str] = None,
        valkey_active_expire_effort: typing.Optional[jsii.Number] = None,
        valkey_io_threads: typing.Optional[jsii.Number] = None,
        valkey_lfu_decay_time: typing.Optional[jsii.Number] = None,
        valkey_lfu_log_factor: typing.Optional[jsii.Number] = None,
        valkey_maxmemory_policy: typing.Optional[builtins.str] = None,
        valkey_notify_keyspace_events: typing.Optional[builtins.str] = None,
        valkey_number_of_databases: typing.Optional[jsii.Number] = None,
        valkey_persistence: typing.Optional[builtins.str] = None,
        valkey_pubsub_client_output_buffer_limit: typing.Optional[jsii.Number] = None,
        valkey_ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        valkey_timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param automatic_utility_network_ip_filter: Automatic utility network IP Filter. Automatically allow connections from servers in the utility network within the same zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#automatic_utility_network_ip_filter ManagedDatabaseValkey#automatic_utility_network_ip_filter}
        :param backup_hour: The hour of day (in UTC) when backup for the service is started. New backup is only started if previous backup has already completed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#backup_hour ManagedDatabaseValkey#backup_hour}
        :param backup_minute: The minute of an hour when backup for the service is started. New backup is only started if previous backup has already completed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#backup_minute ManagedDatabaseValkey#backup_minute}
        :param frequent_snapshots: Frequent RDB snapshots. When enabled, Valkey will create frequent local RDB snapshots. When disabled, Valkey will only take RDB snapshots when a backup is created, based on the backup schedule. This setting is ignored when ``valkey_persistence`` is set to ``off``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#frequent_snapshots ManagedDatabaseValkey#frequent_snapshots}
        :param ip_filter: IP filter. Allow incoming connections from CIDR address block, e.g. '10.20.0.0/16'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#ip_filter ManagedDatabaseValkey#ip_filter}
        :param migration: migration block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#migration ManagedDatabaseValkey#migration}
        :param public_access: Public Access. Allow access to the service from the public Internet. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#public_access ManagedDatabaseValkey#public_access}
        :param service_log: Service logging. Store logs for the service so that they are available in the HTTP API and console. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#service_log ManagedDatabaseValkey#service_log}
        :param valkey_acl_channels_default: Default ACL for pub/sub channels used when a Valkey user is created. Determines default pub/sub channels' ACL for new users if ACL is not supplied. When this option is not defined, all_channels is assumed to keep backward compatibility. This option doesn't affect Valkey configuration acl-pubsub-default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_acl_channels_default ManagedDatabaseValkey#valkey_acl_channels_default}
        :param valkey_active_expire_effort: Active expire effort. Valkey reclaims expired keys both when accessed and in the background. The background process scans for expired keys to free memory. Increasing the active-expire-effort setting (default 1, max 10) uses more CPU to reclaim expired keys faster, reducing memory usage but potentially increasing latency. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_active_expire_effort ManagedDatabaseValkey#valkey_active_expire_effort}
        :param valkey_io_threads: Valkey IO thread count. Set Valkey IO thread count. Changing this will cause a restart of the Valkey service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_io_threads ManagedDatabaseValkey#valkey_io_threads}
        :param valkey_lfu_decay_time: LFU maxmemory-policy counter decay time in minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_lfu_decay_time ManagedDatabaseValkey#valkey_lfu_decay_time}
        :param valkey_lfu_log_factor: Counter logarithm factor for volatile-lfu and allkeys-lfu maxmemory-policies. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_lfu_log_factor ManagedDatabaseValkey#valkey_lfu_log_factor}
        :param valkey_maxmemory_policy: Valkey maxmemory-policy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_maxmemory_policy ManagedDatabaseValkey#valkey_maxmemory_policy}
        :param valkey_notify_keyspace_events: Set notify-keyspace-events option. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_notify_keyspace_events ManagedDatabaseValkey#valkey_notify_keyspace_events}
        :param valkey_number_of_databases: Number of Valkey databases. Set number of Valkey databases. Changing this will cause a restart of the Valkey service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_number_of_databases ManagedDatabaseValkey#valkey_number_of_databases}
        :param valkey_persistence: Valkey persistence. When persistence is 'rdb', Valkey does RDB dumps each 10 minutes if any key is changed. Also RDB dumps are done according to backup schedule for backup purposes. When persistence is 'off', no RDB dumps and backups are done, so data can be lost at any moment if service is restarted for any reason, or if service is powered off. Also service can't be forked. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_persistence ManagedDatabaseValkey#valkey_persistence}
        :param valkey_pubsub_client_output_buffer_limit: Pub/sub client output buffer hard limit in MB. Set output buffer limit for pub / sub clients in MB. The value is the hard limit, the soft limit is 1/4 of the hard limit. When setting the limit, be mindful of the available memory in the selected service plan. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_pubsub_client_output_buffer_limit ManagedDatabaseValkey#valkey_pubsub_client_output_buffer_limit}
        :param valkey_ssl: Require SSL to access Valkey. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_ssl ManagedDatabaseValkey#valkey_ssl}
        :param valkey_timeout: Valkey idle connection timeout in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_timeout ManagedDatabaseValkey#valkey_timeout}
        '''
        value = ManagedDatabaseValkeyProperties(
            automatic_utility_network_ip_filter=automatic_utility_network_ip_filter,
            backup_hour=backup_hour,
            backup_minute=backup_minute,
            frequent_snapshots=frequent_snapshots,
            ip_filter=ip_filter,
            migration=migration,
            public_access=public_access,
            service_log=service_log,
            valkey_acl_channels_default=valkey_acl_channels_default,
            valkey_active_expire_effort=valkey_active_expire_effort,
            valkey_io_threads=valkey_io_threads,
            valkey_lfu_decay_time=valkey_lfu_decay_time,
            valkey_lfu_log_factor=valkey_lfu_log_factor,
            valkey_maxmemory_policy=valkey_maxmemory_policy,
            valkey_notify_keyspace_events=valkey_notify_keyspace_events,
            valkey_number_of_databases=valkey_number_of_databases,
            valkey_persistence=valkey_persistence,
            valkey_pubsub_client_output_buffer_limit=valkey_pubsub_client_output_buffer_limit,
            valkey_ssl=valkey_ssl,
            valkey_timeout=valkey_timeout,
        )

        return typing.cast(None, jsii.invoke(self, "putProperties", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetMaintenanceWindowDow")
    def reset_maintenance_window_dow(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaintenanceWindowDow", []))

    @jsii.member(jsii_name="resetMaintenanceWindowTime")
    def reset_maintenance_window_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaintenanceWindowTime", []))

    @jsii.member(jsii_name="resetNetwork")
    def reset_network(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetwork", []))

    @jsii.member(jsii_name="resetPowered")
    def reset_powered(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPowered", []))

    @jsii.member(jsii_name="resetProperties")
    def reset_properties(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProperties", []))

    @jsii.member(jsii_name="resetTerminationProtection")
    def reset_termination_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTerminationProtection", []))

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
    @jsii.member(jsii_name="components")
    def components(self) -> "ManagedDatabaseValkeyComponentsList":
        return typing.cast("ManagedDatabaseValkeyComponentsList", jsii.get(self, "components"))

    @builtins.property
    @jsii.member(jsii_name="network")
    def network(self) -> "ManagedDatabaseValkeyNetworkList":
        return typing.cast("ManagedDatabaseValkeyNetworkList", jsii.get(self, "network"))

    @builtins.property
    @jsii.member(jsii_name="nodeStates")
    def node_states(self) -> "ManagedDatabaseValkeyNodeStatesList":
        return typing.cast("ManagedDatabaseValkeyNodeStatesList", jsii.get(self, "nodeStates"))

    @builtins.property
    @jsii.member(jsii_name="primaryDatabase")
    def primary_database(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "primaryDatabase"))

    @builtins.property
    @jsii.member(jsii_name="properties")
    def properties(self) -> "ManagedDatabaseValkeyPropertiesOutputReference":
        return typing.cast("ManagedDatabaseValkeyPropertiesOutputReference", jsii.get(self, "properties"))

    @builtins.property
    @jsii.member(jsii_name="serviceHost")
    def service_host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceHost"))

    @builtins.property
    @jsii.member(jsii_name="servicePassword")
    def service_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "servicePassword"))

    @builtins.property
    @jsii.member(jsii_name="servicePort")
    def service_port(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "servicePort"))

    @builtins.property
    @jsii.member(jsii_name="serviceUri")
    def service_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceUri"))

    @builtins.property
    @jsii.member(jsii_name="serviceUsername")
    def service_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceUsername"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="labelsInput")
    def labels_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "labelsInput"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowDowInput")
    def maintenance_window_dow_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maintenanceWindowDowInput"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowTimeInput")
    def maintenance_window_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maintenanceWindowTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="networkInput")
    def network_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedDatabaseValkeyNetwork"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedDatabaseValkeyNetwork"]]], jsii.get(self, "networkInput"))

    @builtins.property
    @jsii.member(jsii_name="planInput")
    def plan_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "planInput"))

    @builtins.property
    @jsii.member(jsii_name="poweredInput")
    def powered_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "poweredInput"))

    @builtins.property
    @jsii.member(jsii_name="propertiesInput")
    def properties_input(self) -> typing.Optional["ManagedDatabaseValkeyProperties"]:
        return typing.cast(typing.Optional["ManagedDatabaseValkeyProperties"], jsii.get(self, "propertiesInput"))

    @builtins.property
    @jsii.member(jsii_name="terminationProtectionInput")
    def termination_protection_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "terminationProtectionInput"))

    @builtins.property
    @jsii.member(jsii_name="titleInput")
    def title_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "titleInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneInput")
    def zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b41fe74abf03b1ee4f0b5f521d5e3e995ded4c72f89438f83df1a19a755cf210)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__582e5d19d5e9e322b330c3b5bede9c40c98cc138fef81206fe5627e535dff1bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "labels", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowDow")
    def maintenance_window_dow(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maintenanceWindowDow"))

    @maintenance_window_dow.setter
    def maintenance_window_dow(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__143dbf09447146d1251e1d077d8d015a4d72185c65356c2cbc926407d4a9d66d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maintenanceWindowDow", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowTime")
    def maintenance_window_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maintenanceWindowTime"))

    @maintenance_window_time.setter
    def maintenance_window_time(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94bc5c33c77b831f6591e0bd7fc829f250e2b41e491c36b6e70fba5c7fca15f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maintenanceWindowTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2558e1f521ac9d42f41277e188f9b3916e911b33d98c46eba7b35837f9d5e5aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="plan")
    def plan(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "plan"))

    @plan.setter
    def plan(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d03add559c3e5c8300d41809a9579ab79a30ac2280a9116b12f9e956f5b176e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "plan", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="powered")
    def powered(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "powered"))

    @powered.setter
    def powered(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8bad55e55d8452abe892cea5a4bec66a6ab86e9bc3d56b0a36cfe63e18325c01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "powered", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terminationProtection")
    def termination_protection(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "terminationProtection"))

    @termination_protection.setter
    def termination_protection(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e2a35e3062885d4364913bf8f82e9adbc5cf8ee7b9a4712ac632c0c18444667)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terminationProtection", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @title.setter
    def title(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__587e4697953225f3226603c43b6632073e29e531cd8559a516447b2f279761f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "title", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zone")
    def zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zone"))

    @zone.setter
    def zone(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d784cbad4812d74571ea6bd4f345ded5999d60288344c5b7666a672de8ab4f93)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zone", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseValkey.ManagedDatabaseValkeyComponents",
    jsii_struct_bases=[],
    name_mapping={},
)
class ManagedDatabaseValkeyComponents:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseValkeyComponents(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseValkeyComponentsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseValkey.ManagedDatabaseValkeyComponentsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cf4f52898b75a9b0604cb414405e6251854854d6b3965a6524b46da5002b3322)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ManagedDatabaseValkeyComponentsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4252d9db585952153c1c7b4ab9959c5e9735acd2eacc7718a173e3af9b63655)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ManagedDatabaseValkeyComponentsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d6e320ee08cff87cf383a49d240e7b08cc1cde188220b5ebbaa1aa01276cd47)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d01ad4104711108a61bfe60b65ce72760f44f64c48e6d32829e0cd80c705aae2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9717b3417f02063948e02cb67f4622cbd85be8020fbdec4526701605c0e76db8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class ManagedDatabaseValkeyComponentsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseValkey.ManagedDatabaseValkeyComponentsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__74486c446b4bb4d03113a6716ef1ae8d4f578400c1889d35913c174dcca771eb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="component")
    def component(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "component"))

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @builtins.property
    @jsii.member(jsii_name="route")
    def route(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "route"))

    @builtins.property
    @jsii.member(jsii_name="usage")
    def usage(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usage"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ManagedDatabaseValkeyComponents]:
        return typing.cast(typing.Optional[ManagedDatabaseValkeyComponents], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseValkeyComponents],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8aac1a49ad50d49df4e2f2de04bd60a6f054eeff1e57e01b8130b16417b58c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseValkey.ManagedDatabaseValkeyConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "name": "name",
        "plan": "plan",
        "title": "title",
        "zone": "zone",
        "id": "id",
        "labels": "labels",
        "maintenance_window_dow": "maintenanceWindowDow",
        "maintenance_window_time": "maintenanceWindowTime",
        "network": "network",
        "powered": "powered",
        "properties": "properties",
        "termination_protection": "terminationProtection",
    },
)
class ManagedDatabaseValkeyConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        name: builtins.str,
        plan: builtins.str,
        title: builtins.str,
        zone: builtins.str,
        id: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        maintenance_window_dow: typing.Optional[builtins.str] = None,
        maintenance_window_time: typing.Optional[builtins.str] = None,
        network: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedDatabaseValkeyNetwork", typing.Dict[builtins.str, typing.Any]]]]] = None,
        powered: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        properties: typing.Optional[typing.Union["ManagedDatabaseValkeyProperties", typing.Dict[builtins.str, typing.Any]]] = None,
        termination_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Name of the service. The name is used as a prefix for the logical hostname. Must be unique within an account Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#name ManagedDatabaseValkey#name}
        :param plan: Service plan to use. This determines how much resources the instance will have. You can list available plans with ``upctl database plans <type>``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#plan ManagedDatabaseValkey#plan}
        :param title: Title of a managed database instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#title ManagedDatabaseValkey#title}
        :param zone: Zone where the instance resides, e.g. ``de-fra1``. You can list available zones with ``upctl zone list``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#zone ManagedDatabaseValkey#zone}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#id ManagedDatabaseValkey#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param labels: User defined key-value pairs to classify the managed database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#labels ManagedDatabaseValkey#labels}
        :param maintenance_window_dow: Maintenance window day of week. Lower case weekday name (monday, tuesday, ...). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#maintenance_window_dow ManagedDatabaseValkey#maintenance_window_dow}
        :param maintenance_window_time: Maintenance window UTC time in hh:mm:ss format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#maintenance_window_time ManagedDatabaseValkey#maintenance_window_time}
        :param network: network block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#network ManagedDatabaseValkey#network}
        :param powered: The administrative power state of the service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#powered ManagedDatabaseValkey#powered}
        :param properties: properties block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#properties ManagedDatabaseValkey#properties}
        :param termination_protection: If set to true, prevents the managed service from being powered off, or deleted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#termination_protection ManagedDatabaseValkey#termination_protection}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(properties, dict):
            properties = ManagedDatabaseValkeyProperties(**properties)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__572e81ffbdca76e6a311042e02f5f60989357be28c5c9418094954727f2b5e84)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument plan", value=plan, expected_type=type_hints["plan"])
            check_type(argname="argument title", value=title, expected_type=type_hints["title"])
            check_type(argname="argument zone", value=zone, expected_type=type_hints["zone"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument labels", value=labels, expected_type=type_hints["labels"])
            check_type(argname="argument maintenance_window_dow", value=maintenance_window_dow, expected_type=type_hints["maintenance_window_dow"])
            check_type(argname="argument maintenance_window_time", value=maintenance_window_time, expected_type=type_hints["maintenance_window_time"])
            check_type(argname="argument network", value=network, expected_type=type_hints["network"])
            check_type(argname="argument powered", value=powered, expected_type=type_hints["powered"])
            check_type(argname="argument properties", value=properties, expected_type=type_hints["properties"])
            check_type(argname="argument termination_protection", value=termination_protection, expected_type=type_hints["termination_protection"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "plan": plan,
            "title": title,
            "zone": zone,
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
        if labels is not None:
            self._values["labels"] = labels
        if maintenance_window_dow is not None:
            self._values["maintenance_window_dow"] = maintenance_window_dow
        if maintenance_window_time is not None:
            self._values["maintenance_window_time"] = maintenance_window_time
        if network is not None:
            self._values["network"] = network
        if powered is not None:
            self._values["powered"] = powered
        if properties is not None:
            self._values["properties"] = properties
        if termination_protection is not None:
            self._values["termination_protection"] = termination_protection

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
    def name(self) -> builtins.str:
        '''Name of the service.

        The name is used as a prefix for the logical hostname. Must be unique within an account

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#name ManagedDatabaseValkey#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def plan(self) -> builtins.str:
        '''Service plan to use.

        This determines how much resources the instance will have. You can list available plans with ``upctl database plans <type>``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#plan ManagedDatabaseValkey#plan}
        '''
        result = self._values.get("plan")
        assert result is not None, "Required property 'plan' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''Title of a managed database instance.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#title ManagedDatabaseValkey#title}
        '''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def zone(self) -> builtins.str:
        '''Zone where the instance resides, e.g. ``de-fra1``. You can list available zones with ``upctl zone list``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#zone ManagedDatabaseValkey#zone}
        '''
        result = self._values.get("zone")
        assert result is not None, "Required property 'zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#id ManagedDatabaseValkey#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''User defined key-value pairs to classify the managed database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#labels ManagedDatabaseValkey#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def maintenance_window_dow(self) -> typing.Optional[builtins.str]:
        '''Maintenance window day of week. Lower case weekday name (monday, tuesday, ...).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#maintenance_window_dow ManagedDatabaseValkey#maintenance_window_dow}
        '''
        result = self._values.get("maintenance_window_dow")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maintenance_window_time(self) -> typing.Optional[builtins.str]:
        '''Maintenance window UTC time in hh:mm:ss format.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#maintenance_window_time ManagedDatabaseValkey#maintenance_window_time}
        '''
        result = self._values.get("maintenance_window_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedDatabaseValkeyNetwork"]]]:
        '''network block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#network ManagedDatabaseValkey#network}
        '''
        result = self._values.get("network")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedDatabaseValkeyNetwork"]]], result)

    @builtins.property
    def powered(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''The administrative power state of the service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#powered ManagedDatabaseValkey#powered}
        '''
        result = self._values.get("powered")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def properties(self) -> typing.Optional["ManagedDatabaseValkeyProperties"]:
        '''properties block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#properties ManagedDatabaseValkey#properties}
        '''
        result = self._values.get("properties")
        return typing.cast(typing.Optional["ManagedDatabaseValkeyProperties"], result)

    @builtins.property
    def termination_protection(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set to true, prevents the managed service from being powered off, or deleted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#termination_protection ManagedDatabaseValkey#termination_protection}
        '''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseValkeyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseValkey.ManagedDatabaseValkeyNetwork",
    jsii_struct_bases=[],
    name_mapping={"family": "family", "name": "name", "type": "type", "uuid": "uuid"},
)
class ManagedDatabaseValkeyNetwork:
    def __init__(
        self,
        *,
        family: builtins.str,
        name: builtins.str,
        type: builtins.str,
        uuid: builtins.str,
    ) -> None:
        '''
        :param family: Network family. Currently only ``IPv4`` is supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#family ManagedDatabaseValkey#family}
        :param name: The name of the network. Must be unique within the service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#name ManagedDatabaseValkey#name}
        :param type: The type of the network. Must be private. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#type ManagedDatabaseValkey#type}
        :param uuid: Private network UUID. Must reside in the same zone as the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#uuid ManagedDatabaseValkey#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86bc6cfbeb2b0d724aae3cd0dc476ec5f0060e413bec0604ca6101e019eba72f)
            check_type(argname="argument family", value=family, expected_type=type_hints["family"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument uuid", value=uuid, expected_type=type_hints["uuid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "family": family,
            "name": name,
            "type": type,
            "uuid": uuid,
        }

    @builtins.property
    def family(self) -> builtins.str:
        '''Network family. Currently only ``IPv4`` is supported.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#family ManagedDatabaseValkey#family}
        '''
        result = self._values.get("family")
        assert result is not None, "Required property 'family' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the network. Must be unique within the service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#name ManagedDatabaseValkey#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''The type of the network. Must be private.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#type ManagedDatabaseValkey#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def uuid(self) -> builtins.str:
        '''Private network UUID. Must reside in the same zone as the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#uuid ManagedDatabaseValkey#uuid}
        '''
        result = self._values.get("uuid")
        assert result is not None, "Required property 'uuid' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseValkeyNetwork(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseValkeyNetworkList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseValkey.ManagedDatabaseValkeyNetworkList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3f387effda8c16fde9966811ccf787b3d56271088a5b593d10bd528d49165c7f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ManagedDatabaseValkeyNetworkOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2cc2c3d970c95aa4a181f20ece6cae2da769925316379879259191e890fc425)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ManagedDatabaseValkeyNetworkOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1f288935f98f823df0793a078e8de29a92298eeac83e277d79e6f5b6e9c6819)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1ce318a3e6e190673efb3cff247a30d8c50c2a72993e57587a0a7bbac9667ca3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__481786a55a2dc14dc3f4da44e7f8873f8427ecce80d885eb17eeee0c53c32a87)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedDatabaseValkeyNetwork]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedDatabaseValkeyNetwork]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedDatabaseValkeyNetwork]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b13648ea5908387b35158d29883e52641c749981675ab65432e63968b8ef75a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ManagedDatabaseValkeyNetworkOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseValkey.ManagedDatabaseValkeyNetworkOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2824d1ded7fae4598e64b29704860b7e65e1f60cc8c2ba18af6f88b9c393faff)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="familyInput")
    def family_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "familyInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="uuidInput")
    def uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uuidInput"))

    @builtins.property
    @jsii.member(jsii_name="family")
    def family(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "family"))

    @family.setter
    def family(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fa688fb44a82433ca388090b8249ad71a4bc831cce3794d229093b4b56293f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "family", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b54ca25e12af584a57e78a38206ab3436c3e1bac4eee6604e90f51def133755)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1226f980d40c87f8397fe48cb9cc06bf941eea21e26fac7b5530ae632e3503b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12fdc41f27c6b4f2b911ddd6aba5ce7018770875b804e05212b99416e015528d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedDatabaseValkeyNetwork]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedDatabaseValkeyNetwork]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedDatabaseValkeyNetwork]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1bf6882d93a48e5aa568b7df8ec4368202184ba0e5546a39a063fbf8b69e0628)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseValkey.ManagedDatabaseValkeyNodeStates",
    jsii_struct_bases=[],
    name_mapping={},
)
class ManagedDatabaseValkeyNodeStates:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseValkeyNodeStates(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseValkeyNodeStatesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseValkey.ManagedDatabaseValkeyNodeStatesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b36a07f4f6613a569fb00669f4dff53d81c6ac0bf2755480fb4e80a1743c29ef)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ManagedDatabaseValkeyNodeStatesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7c171b3c8fbf5cf7cde17ad2a04170148cb54b6d4df2b7940c311e02710b1f9)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ManagedDatabaseValkeyNodeStatesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a84231c9993c80153c365716c8c01dab8e9bea7cb1687ec9ffe5a59e4b2a6324)
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
            type_hints = typing.get_type_hints(_typecheckingstub__33024060d747d6f3e2c9b75456197397a7aef2d57295c92716c794d24de628a0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5b4b326613b451e91b53641f7d027967e6b69bfef13702d5adde4da4e2e83459)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class ManagedDatabaseValkeyNodeStatesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseValkey.ManagedDatabaseValkeyNodeStatesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3584d0fded5a72760262405f68d64086374d1b0be18591d1e84bb4af5db5c06f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ManagedDatabaseValkeyNodeStates]:
        return typing.cast(typing.Optional[ManagedDatabaseValkeyNodeStates], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseValkeyNodeStates],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23d6fd61468e82793403951f52c6440df44471673eda077d3768f80950de87be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseValkey.ManagedDatabaseValkeyProperties",
    jsii_struct_bases=[],
    name_mapping={
        "automatic_utility_network_ip_filter": "automaticUtilityNetworkIpFilter",
        "backup_hour": "backupHour",
        "backup_minute": "backupMinute",
        "frequent_snapshots": "frequentSnapshots",
        "ip_filter": "ipFilter",
        "migration": "migration",
        "public_access": "publicAccess",
        "service_log": "serviceLog",
        "valkey_acl_channels_default": "valkeyAclChannelsDefault",
        "valkey_active_expire_effort": "valkeyActiveExpireEffort",
        "valkey_io_threads": "valkeyIoThreads",
        "valkey_lfu_decay_time": "valkeyLfuDecayTime",
        "valkey_lfu_log_factor": "valkeyLfuLogFactor",
        "valkey_maxmemory_policy": "valkeyMaxmemoryPolicy",
        "valkey_notify_keyspace_events": "valkeyNotifyKeyspaceEvents",
        "valkey_number_of_databases": "valkeyNumberOfDatabases",
        "valkey_persistence": "valkeyPersistence",
        "valkey_pubsub_client_output_buffer_limit": "valkeyPubsubClientOutputBufferLimit",
        "valkey_ssl": "valkeySsl",
        "valkey_timeout": "valkeyTimeout",
    },
)
class ManagedDatabaseValkeyProperties:
    def __init__(
        self,
        *,
        automatic_utility_network_ip_filter: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        backup_hour: typing.Optional[jsii.Number] = None,
        backup_minute: typing.Optional[jsii.Number] = None,
        frequent_snapshots: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ip_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
        migration: typing.Optional[typing.Union["ManagedDatabaseValkeyPropertiesMigration", typing.Dict[builtins.str, typing.Any]]] = None,
        public_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        service_log: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        valkey_acl_channels_default: typing.Optional[builtins.str] = None,
        valkey_active_expire_effort: typing.Optional[jsii.Number] = None,
        valkey_io_threads: typing.Optional[jsii.Number] = None,
        valkey_lfu_decay_time: typing.Optional[jsii.Number] = None,
        valkey_lfu_log_factor: typing.Optional[jsii.Number] = None,
        valkey_maxmemory_policy: typing.Optional[builtins.str] = None,
        valkey_notify_keyspace_events: typing.Optional[builtins.str] = None,
        valkey_number_of_databases: typing.Optional[jsii.Number] = None,
        valkey_persistence: typing.Optional[builtins.str] = None,
        valkey_pubsub_client_output_buffer_limit: typing.Optional[jsii.Number] = None,
        valkey_ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        valkey_timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param automatic_utility_network_ip_filter: Automatic utility network IP Filter. Automatically allow connections from servers in the utility network within the same zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#automatic_utility_network_ip_filter ManagedDatabaseValkey#automatic_utility_network_ip_filter}
        :param backup_hour: The hour of day (in UTC) when backup for the service is started. New backup is only started if previous backup has already completed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#backup_hour ManagedDatabaseValkey#backup_hour}
        :param backup_minute: The minute of an hour when backup for the service is started. New backup is only started if previous backup has already completed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#backup_minute ManagedDatabaseValkey#backup_minute}
        :param frequent_snapshots: Frequent RDB snapshots. When enabled, Valkey will create frequent local RDB snapshots. When disabled, Valkey will only take RDB snapshots when a backup is created, based on the backup schedule. This setting is ignored when ``valkey_persistence`` is set to ``off``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#frequent_snapshots ManagedDatabaseValkey#frequent_snapshots}
        :param ip_filter: IP filter. Allow incoming connections from CIDR address block, e.g. '10.20.0.0/16'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#ip_filter ManagedDatabaseValkey#ip_filter}
        :param migration: migration block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#migration ManagedDatabaseValkey#migration}
        :param public_access: Public Access. Allow access to the service from the public Internet. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#public_access ManagedDatabaseValkey#public_access}
        :param service_log: Service logging. Store logs for the service so that they are available in the HTTP API and console. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#service_log ManagedDatabaseValkey#service_log}
        :param valkey_acl_channels_default: Default ACL for pub/sub channels used when a Valkey user is created. Determines default pub/sub channels' ACL for new users if ACL is not supplied. When this option is not defined, all_channels is assumed to keep backward compatibility. This option doesn't affect Valkey configuration acl-pubsub-default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_acl_channels_default ManagedDatabaseValkey#valkey_acl_channels_default}
        :param valkey_active_expire_effort: Active expire effort. Valkey reclaims expired keys both when accessed and in the background. The background process scans for expired keys to free memory. Increasing the active-expire-effort setting (default 1, max 10) uses more CPU to reclaim expired keys faster, reducing memory usage but potentially increasing latency. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_active_expire_effort ManagedDatabaseValkey#valkey_active_expire_effort}
        :param valkey_io_threads: Valkey IO thread count. Set Valkey IO thread count. Changing this will cause a restart of the Valkey service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_io_threads ManagedDatabaseValkey#valkey_io_threads}
        :param valkey_lfu_decay_time: LFU maxmemory-policy counter decay time in minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_lfu_decay_time ManagedDatabaseValkey#valkey_lfu_decay_time}
        :param valkey_lfu_log_factor: Counter logarithm factor for volatile-lfu and allkeys-lfu maxmemory-policies. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_lfu_log_factor ManagedDatabaseValkey#valkey_lfu_log_factor}
        :param valkey_maxmemory_policy: Valkey maxmemory-policy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_maxmemory_policy ManagedDatabaseValkey#valkey_maxmemory_policy}
        :param valkey_notify_keyspace_events: Set notify-keyspace-events option. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_notify_keyspace_events ManagedDatabaseValkey#valkey_notify_keyspace_events}
        :param valkey_number_of_databases: Number of Valkey databases. Set number of Valkey databases. Changing this will cause a restart of the Valkey service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_number_of_databases ManagedDatabaseValkey#valkey_number_of_databases}
        :param valkey_persistence: Valkey persistence. When persistence is 'rdb', Valkey does RDB dumps each 10 minutes if any key is changed. Also RDB dumps are done according to backup schedule for backup purposes. When persistence is 'off', no RDB dumps and backups are done, so data can be lost at any moment if service is restarted for any reason, or if service is powered off. Also service can't be forked. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_persistence ManagedDatabaseValkey#valkey_persistence}
        :param valkey_pubsub_client_output_buffer_limit: Pub/sub client output buffer hard limit in MB. Set output buffer limit for pub / sub clients in MB. The value is the hard limit, the soft limit is 1/4 of the hard limit. When setting the limit, be mindful of the available memory in the selected service plan. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_pubsub_client_output_buffer_limit ManagedDatabaseValkey#valkey_pubsub_client_output_buffer_limit}
        :param valkey_ssl: Require SSL to access Valkey. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_ssl ManagedDatabaseValkey#valkey_ssl}
        :param valkey_timeout: Valkey idle connection timeout in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_timeout ManagedDatabaseValkey#valkey_timeout}
        '''
        if isinstance(migration, dict):
            migration = ManagedDatabaseValkeyPropertiesMigration(**migration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__130504794befd55a7bc90ab03ca53c94a25f9b733cdd13efed4a51695da4b995)
            check_type(argname="argument automatic_utility_network_ip_filter", value=automatic_utility_network_ip_filter, expected_type=type_hints["automatic_utility_network_ip_filter"])
            check_type(argname="argument backup_hour", value=backup_hour, expected_type=type_hints["backup_hour"])
            check_type(argname="argument backup_minute", value=backup_minute, expected_type=type_hints["backup_minute"])
            check_type(argname="argument frequent_snapshots", value=frequent_snapshots, expected_type=type_hints["frequent_snapshots"])
            check_type(argname="argument ip_filter", value=ip_filter, expected_type=type_hints["ip_filter"])
            check_type(argname="argument migration", value=migration, expected_type=type_hints["migration"])
            check_type(argname="argument public_access", value=public_access, expected_type=type_hints["public_access"])
            check_type(argname="argument service_log", value=service_log, expected_type=type_hints["service_log"])
            check_type(argname="argument valkey_acl_channels_default", value=valkey_acl_channels_default, expected_type=type_hints["valkey_acl_channels_default"])
            check_type(argname="argument valkey_active_expire_effort", value=valkey_active_expire_effort, expected_type=type_hints["valkey_active_expire_effort"])
            check_type(argname="argument valkey_io_threads", value=valkey_io_threads, expected_type=type_hints["valkey_io_threads"])
            check_type(argname="argument valkey_lfu_decay_time", value=valkey_lfu_decay_time, expected_type=type_hints["valkey_lfu_decay_time"])
            check_type(argname="argument valkey_lfu_log_factor", value=valkey_lfu_log_factor, expected_type=type_hints["valkey_lfu_log_factor"])
            check_type(argname="argument valkey_maxmemory_policy", value=valkey_maxmemory_policy, expected_type=type_hints["valkey_maxmemory_policy"])
            check_type(argname="argument valkey_notify_keyspace_events", value=valkey_notify_keyspace_events, expected_type=type_hints["valkey_notify_keyspace_events"])
            check_type(argname="argument valkey_number_of_databases", value=valkey_number_of_databases, expected_type=type_hints["valkey_number_of_databases"])
            check_type(argname="argument valkey_persistence", value=valkey_persistence, expected_type=type_hints["valkey_persistence"])
            check_type(argname="argument valkey_pubsub_client_output_buffer_limit", value=valkey_pubsub_client_output_buffer_limit, expected_type=type_hints["valkey_pubsub_client_output_buffer_limit"])
            check_type(argname="argument valkey_ssl", value=valkey_ssl, expected_type=type_hints["valkey_ssl"])
            check_type(argname="argument valkey_timeout", value=valkey_timeout, expected_type=type_hints["valkey_timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if automatic_utility_network_ip_filter is not None:
            self._values["automatic_utility_network_ip_filter"] = automatic_utility_network_ip_filter
        if backup_hour is not None:
            self._values["backup_hour"] = backup_hour
        if backup_minute is not None:
            self._values["backup_minute"] = backup_minute
        if frequent_snapshots is not None:
            self._values["frequent_snapshots"] = frequent_snapshots
        if ip_filter is not None:
            self._values["ip_filter"] = ip_filter
        if migration is not None:
            self._values["migration"] = migration
        if public_access is not None:
            self._values["public_access"] = public_access
        if service_log is not None:
            self._values["service_log"] = service_log
        if valkey_acl_channels_default is not None:
            self._values["valkey_acl_channels_default"] = valkey_acl_channels_default
        if valkey_active_expire_effort is not None:
            self._values["valkey_active_expire_effort"] = valkey_active_expire_effort
        if valkey_io_threads is not None:
            self._values["valkey_io_threads"] = valkey_io_threads
        if valkey_lfu_decay_time is not None:
            self._values["valkey_lfu_decay_time"] = valkey_lfu_decay_time
        if valkey_lfu_log_factor is not None:
            self._values["valkey_lfu_log_factor"] = valkey_lfu_log_factor
        if valkey_maxmemory_policy is not None:
            self._values["valkey_maxmemory_policy"] = valkey_maxmemory_policy
        if valkey_notify_keyspace_events is not None:
            self._values["valkey_notify_keyspace_events"] = valkey_notify_keyspace_events
        if valkey_number_of_databases is not None:
            self._values["valkey_number_of_databases"] = valkey_number_of_databases
        if valkey_persistence is not None:
            self._values["valkey_persistence"] = valkey_persistence
        if valkey_pubsub_client_output_buffer_limit is not None:
            self._values["valkey_pubsub_client_output_buffer_limit"] = valkey_pubsub_client_output_buffer_limit
        if valkey_ssl is not None:
            self._values["valkey_ssl"] = valkey_ssl
        if valkey_timeout is not None:
            self._values["valkey_timeout"] = valkey_timeout

    @builtins.property
    def automatic_utility_network_ip_filter(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Automatic utility network IP Filter. Automatically allow connections from servers in the utility network within the same zone.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#automatic_utility_network_ip_filter ManagedDatabaseValkey#automatic_utility_network_ip_filter}
        '''
        result = self._values.get("automatic_utility_network_ip_filter")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def backup_hour(self) -> typing.Optional[jsii.Number]:
        '''The hour of day (in UTC) when backup for the service is started.

        New backup is only started if previous backup has already completed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#backup_hour ManagedDatabaseValkey#backup_hour}
        '''
        result = self._values.get("backup_hour")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def backup_minute(self) -> typing.Optional[jsii.Number]:
        '''The minute of an hour when backup for the service is started.

        New backup is only started if previous backup has already completed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#backup_minute ManagedDatabaseValkey#backup_minute}
        '''
        result = self._values.get("backup_minute")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def frequent_snapshots(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Frequent RDB snapshots.

        When enabled, Valkey will create frequent local RDB snapshots. When disabled, Valkey will only take RDB snapshots when a backup is created, based on the backup schedule. This setting is ignored when ``valkey_persistence`` is set to ``off``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#frequent_snapshots ManagedDatabaseValkey#frequent_snapshots}
        '''
        result = self._values.get("frequent_snapshots")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ip_filter(self) -> typing.Optional[typing.List[builtins.str]]:
        '''IP filter. Allow incoming connections from CIDR address block, e.g. '10.20.0.0/16'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#ip_filter ManagedDatabaseValkey#ip_filter}
        '''
        result = self._values.get("ip_filter")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def migration(self) -> typing.Optional["ManagedDatabaseValkeyPropertiesMigration"]:
        '''migration block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#migration ManagedDatabaseValkey#migration}
        '''
        result = self._values.get("migration")
        return typing.cast(typing.Optional["ManagedDatabaseValkeyPropertiesMigration"], result)

    @builtins.property
    def public_access(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Public Access. Allow access to the service from the public Internet.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#public_access ManagedDatabaseValkey#public_access}
        '''
        result = self._values.get("public_access")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def service_log(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Service logging. Store logs for the service so that they are available in the HTTP API and console.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#service_log ManagedDatabaseValkey#service_log}
        '''
        result = self._values.get("service_log")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def valkey_acl_channels_default(self) -> typing.Optional[builtins.str]:
        '''Default ACL for pub/sub channels used when a Valkey user is created.

        Determines default pub/sub channels' ACL for new users if ACL is not supplied. When this option is not defined, all_channels is assumed to keep backward compatibility. This option doesn't affect Valkey configuration acl-pubsub-default.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_acl_channels_default ManagedDatabaseValkey#valkey_acl_channels_default}
        '''
        result = self._values.get("valkey_acl_channels_default")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def valkey_active_expire_effort(self) -> typing.Optional[jsii.Number]:
        '''Active expire effort.

        Valkey reclaims expired keys both when accessed and in the background. The background process scans for expired keys to free memory. Increasing the active-expire-effort setting (default 1, max 10) uses more CPU to reclaim expired keys faster, reducing memory usage but potentially increasing latency.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_active_expire_effort ManagedDatabaseValkey#valkey_active_expire_effort}
        '''
        result = self._values.get("valkey_active_expire_effort")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def valkey_io_threads(self) -> typing.Optional[jsii.Number]:
        '''Valkey IO thread count. Set Valkey IO thread count. Changing this will cause a restart of the Valkey service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_io_threads ManagedDatabaseValkey#valkey_io_threads}
        '''
        result = self._values.get("valkey_io_threads")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def valkey_lfu_decay_time(self) -> typing.Optional[jsii.Number]:
        '''LFU maxmemory-policy counter decay time in minutes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_lfu_decay_time ManagedDatabaseValkey#valkey_lfu_decay_time}
        '''
        result = self._values.get("valkey_lfu_decay_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def valkey_lfu_log_factor(self) -> typing.Optional[jsii.Number]:
        '''Counter logarithm factor for volatile-lfu and allkeys-lfu maxmemory-policies.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_lfu_log_factor ManagedDatabaseValkey#valkey_lfu_log_factor}
        '''
        result = self._values.get("valkey_lfu_log_factor")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def valkey_maxmemory_policy(self) -> typing.Optional[builtins.str]:
        '''Valkey maxmemory-policy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_maxmemory_policy ManagedDatabaseValkey#valkey_maxmemory_policy}
        '''
        result = self._values.get("valkey_maxmemory_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def valkey_notify_keyspace_events(self) -> typing.Optional[builtins.str]:
        '''Set notify-keyspace-events option.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_notify_keyspace_events ManagedDatabaseValkey#valkey_notify_keyspace_events}
        '''
        result = self._values.get("valkey_notify_keyspace_events")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def valkey_number_of_databases(self) -> typing.Optional[jsii.Number]:
        '''Number of Valkey databases. Set number of Valkey databases. Changing this will cause a restart of the Valkey service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_number_of_databases ManagedDatabaseValkey#valkey_number_of_databases}
        '''
        result = self._values.get("valkey_number_of_databases")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def valkey_persistence(self) -> typing.Optional[builtins.str]:
        '''Valkey persistence.

        When persistence is 'rdb', Valkey does RDB dumps each 10 minutes if any key is changed. Also RDB dumps are done according to backup schedule for backup purposes. When persistence is 'off', no RDB dumps and backups are done, so data can be lost at any moment if service is restarted for any reason, or if service is powered off. Also service can't be forked.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_persistence ManagedDatabaseValkey#valkey_persistence}
        '''
        result = self._values.get("valkey_persistence")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def valkey_pubsub_client_output_buffer_limit(self) -> typing.Optional[jsii.Number]:
        '''Pub/sub client output buffer hard limit in MB.

        Set output buffer limit for pub / sub clients in MB. The value is the hard limit, the soft limit is 1/4 of the hard limit. When setting the limit, be mindful of the available memory in the selected service plan.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_pubsub_client_output_buffer_limit ManagedDatabaseValkey#valkey_pubsub_client_output_buffer_limit}
        '''
        result = self._values.get("valkey_pubsub_client_output_buffer_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def valkey_ssl(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Require SSL to access Valkey.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_ssl ManagedDatabaseValkey#valkey_ssl}
        '''
        result = self._values.get("valkey_ssl")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def valkey_timeout(self) -> typing.Optional[jsii.Number]:
        '''Valkey idle connection timeout in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#valkey_timeout ManagedDatabaseValkey#valkey_timeout}
        '''
        result = self._values.get("valkey_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseValkeyProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseValkey.ManagedDatabaseValkeyPropertiesMigration",
    jsii_struct_bases=[],
    name_mapping={
        "dbname": "dbname",
        "host": "host",
        "ignore_dbs": "ignoreDbs",
        "ignore_roles": "ignoreRoles",
        "method": "method",
        "password": "password",
        "port": "port",
        "ssl": "ssl",
        "username": "username",
    },
)
class ManagedDatabaseValkeyPropertiesMigration:
    def __init__(
        self,
        *,
        dbname: typing.Optional[builtins.str] = None,
        host: typing.Optional[builtins.str] = None,
        ignore_dbs: typing.Optional[builtins.str] = None,
        ignore_roles: typing.Optional[builtins.str] = None,
        method: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dbname: Database name for bootstrapping the initial connection. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#dbname ManagedDatabaseValkey#dbname}
        :param host: Hostname or IP address of the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#host ManagedDatabaseValkey#host}
        :param ignore_dbs: Comma-separated list of databases, which should be ignored during migration (supported by MySQL and PostgreSQL only at the moment). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#ignore_dbs ManagedDatabaseValkey#ignore_dbs}
        :param ignore_roles: Comma-separated list of database roles, which should be ignored during migration (supported by PostgreSQL only at the moment). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#ignore_roles ManagedDatabaseValkey#ignore_roles}
        :param method: The migration method to be used (currently supported only by Redis, Dragonfly, MySQL and PostgreSQL service types). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#method ManagedDatabaseValkey#method}
        :param password: Password for authentication with the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#password ManagedDatabaseValkey#password}
        :param port: Port number of the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#port ManagedDatabaseValkey#port}
        :param ssl: The server where to migrate data from is secured with SSL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#ssl ManagedDatabaseValkey#ssl}
        :param username: User name for authentication with the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#username ManagedDatabaseValkey#username}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79d93789bda00eb59095ff4b93fc8d576f547960656fc2c2b20cdd46b3842774)
            check_type(argname="argument dbname", value=dbname, expected_type=type_hints["dbname"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument ignore_dbs", value=ignore_dbs, expected_type=type_hints["ignore_dbs"])
            check_type(argname="argument ignore_roles", value=ignore_roles, expected_type=type_hints["ignore_roles"])
            check_type(argname="argument method", value=method, expected_type=type_hints["method"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument ssl", value=ssl, expected_type=type_hints["ssl"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dbname is not None:
            self._values["dbname"] = dbname
        if host is not None:
            self._values["host"] = host
        if ignore_dbs is not None:
            self._values["ignore_dbs"] = ignore_dbs
        if ignore_roles is not None:
            self._values["ignore_roles"] = ignore_roles
        if method is not None:
            self._values["method"] = method
        if password is not None:
            self._values["password"] = password
        if port is not None:
            self._values["port"] = port
        if ssl is not None:
            self._values["ssl"] = ssl
        if username is not None:
            self._values["username"] = username

    @builtins.property
    def dbname(self) -> typing.Optional[builtins.str]:
        '''Database name for bootstrapping the initial connection.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#dbname ManagedDatabaseValkey#dbname}
        '''
        result = self._values.get("dbname")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def host(self) -> typing.Optional[builtins.str]:
        '''Hostname or IP address of the server where to migrate data from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#host ManagedDatabaseValkey#host}
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ignore_dbs(self) -> typing.Optional[builtins.str]:
        '''Comma-separated list of databases, which should be ignored during migration (supported by MySQL and PostgreSQL only at the moment).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#ignore_dbs ManagedDatabaseValkey#ignore_dbs}
        '''
        result = self._values.get("ignore_dbs")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ignore_roles(self) -> typing.Optional[builtins.str]:
        '''Comma-separated list of database roles, which should be ignored during migration (supported by PostgreSQL only at the moment).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#ignore_roles ManagedDatabaseValkey#ignore_roles}
        '''
        result = self._values.get("ignore_roles")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def method(self) -> typing.Optional[builtins.str]:
        '''The migration method to be used (currently supported only by Redis, Dragonfly, MySQL and PostgreSQL service types).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#method ManagedDatabaseValkey#method}
        '''
        result = self._values.get("method")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''Password for authentication with the server where to migrate data from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#password ManagedDatabaseValkey#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''Port number of the server where to migrate data from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#port ManagedDatabaseValkey#port}
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ssl(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''The server where to migrate data from is secured with SSL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#ssl ManagedDatabaseValkey#ssl}
        '''
        result = self._values.get("ssl")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''User name for authentication with the server where to migrate data from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#username ManagedDatabaseValkey#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseValkeyPropertiesMigration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseValkeyPropertiesMigrationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseValkey.ManagedDatabaseValkeyPropertiesMigrationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__653b9500142dcaaa00ba3451c2ff31751e33552cb8092bcd3c7cdc2da14e47cd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDbname")
    def reset_dbname(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbname", []))

    @jsii.member(jsii_name="resetHost")
    def reset_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHost", []))

    @jsii.member(jsii_name="resetIgnoreDbs")
    def reset_ignore_dbs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIgnoreDbs", []))

    @jsii.member(jsii_name="resetIgnoreRoles")
    def reset_ignore_roles(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIgnoreRoles", []))

    @jsii.member(jsii_name="resetMethod")
    def reset_method(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMethod", []))

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @jsii.member(jsii_name="resetSsl")
    def reset_ssl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSsl", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

    @builtins.property
    @jsii.member(jsii_name="dbnameInput")
    def dbname_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbnameInput"))

    @builtins.property
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property
    @jsii.member(jsii_name="ignoreDbsInput")
    def ignore_dbs_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ignoreDbsInput"))

    @builtins.property
    @jsii.member(jsii_name="ignoreRolesInput")
    def ignore_roles_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ignoreRolesInput"))

    @builtins.property
    @jsii.member(jsii_name="methodInput")
    def method_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "methodInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property
    @jsii.member(jsii_name="sslInput")
    def ssl_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "sslInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="dbname")
    def dbname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbname"))

    @dbname.setter
    def dbname(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1314b6cb90839f64d1e6b134d07633136410e75b81032064900446b8247729d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dbname", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76243e98f6cb500875bf56e8d226c15068248549c3ecd1b38c8ae49ffcdd0c65)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ignoreDbs")
    def ignore_dbs(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ignoreDbs"))

    @ignore_dbs.setter
    def ignore_dbs(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__162cd0275fe93ffc0222678a946ecd079acd01731fd60103ce60dd5b536809be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ignoreDbs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ignoreRoles")
    def ignore_roles(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ignoreRoles"))

    @ignore_roles.setter
    def ignore_roles(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6fdf035c2bfaaf78851ed75b4776ecfc0280916d034d8d88e5c518b4d31606e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ignoreRoles", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "method"))

    @method.setter
    def method(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e35e85c39397173d3e45859019af030a0c6b4ceaa3a4e544f90652fddaec8daf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "method", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__662e37d640a89c81978ab1bc6760bef1547ed14b8359ccf76d5f8c5ba2c1ca85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af55c31711e4f7afee55e9eb3357116e63b64c1178aa20a3b34caff9e7d36c63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ssl")
    def ssl(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ssl"))

    @ssl.setter
    def ssl(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f483e3934be4c35439acb518122bb176bb613a0bb411d2384a025b2fe6dbaa40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ssl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a34f9da5159916189640a32002175c4e592ba0b30620af992ca26e34a7aa9aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseValkeyPropertiesMigration]:
        return typing.cast(typing.Optional[ManagedDatabaseValkeyPropertiesMigration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseValkeyPropertiesMigration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1793c40b292b55abd22e900135f7fb7177ba88955948317e0f8e1140a8fd6bb9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ManagedDatabaseValkeyPropertiesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseValkey.ManagedDatabaseValkeyPropertiesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__55792d3e90a4aee66c1699f91bdcfb7f0f4fdd7ccf76213d91486a87ffeb6e7f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putMigration")
    def put_migration(
        self,
        *,
        dbname: typing.Optional[builtins.str] = None,
        host: typing.Optional[builtins.str] = None,
        ignore_dbs: typing.Optional[builtins.str] = None,
        ignore_roles: typing.Optional[builtins.str] = None,
        method: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dbname: Database name for bootstrapping the initial connection. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#dbname ManagedDatabaseValkey#dbname}
        :param host: Hostname or IP address of the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#host ManagedDatabaseValkey#host}
        :param ignore_dbs: Comma-separated list of databases, which should be ignored during migration (supported by MySQL and PostgreSQL only at the moment). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#ignore_dbs ManagedDatabaseValkey#ignore_dbs}
        :param ignore_roles: Comma-separated list of database roles, which should be ignored during migration (supported by PostgreSQL only at the moment). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#ignore_roles ManagedDatabaseValkey#ignore_roles}
        :param method: The migration method to be used (currently supported only by Redis, Dragonfly, MySQL and PostgreSQL service types). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#method ManagedDatabaseValkey#method}
        :param password: Password for authentication with the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#password ManagedDatabaseValkey#password}
        :param port: Port number of the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#port ManagedDatabaseValkey#port}
        :param ssl: The server where to migrate data from is secured with SSL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#ssl ManagedDatabaseValkey#ssl}
        :param username: User name for authentication with the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_valkey#username ManagedDatabaseValkey#username}
        '''
        value = ManagedDatabaseValkeyPropertiesMigration(
            dbname=dbname,
            host=host,
            ignore_dbs=ignore_dbs,
            ignore_roles=ignore_roles,
            method=method,
            password=password,
            port=port,
            ssl=ssl,
            username=username,
        )

        return typing.cast(None, jsii.invoke(self, "putMigration", [value]))

    @jsii.member(jsii_name="resetAutomaticUtilityNetworkIpFilter")
    def reset_automatic_utility_network_ip_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutomaticUtilityNetworkIpFilter", []))

    @jsii.member(jsii_name="resetBackupHour")
    def reset_backup_hour(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupHour", []))

    @jsii.member(jsii_name="resetBackupMinute")
    def reset_backup_minute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupMinute", []))

    @jsii.member(jsii_name="resetFrequentSnapshots")
    def reset_frequent_snapshots(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFrequentSnapshots", []))

    @jsii.member(jsii_name="resetIpFilter")
    def reset_ip_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpFilter", []))

    @jsii.member(jsii_name="resetMigration")
    def reset_migration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMigration", []))

    @jsii.member(jsii_name="resetPublicAccess")
    def reset_public_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicAccess", []))

    @jsii.member(jsii_name="resetServiceLog")
    def reset_service_log(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceLog", []))

    @jsii.member(jsii_name="resetValkeyAclChannelsDefault")
    def reset_valkey_acl_channels_default(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValkeyAclChannelsDefault", []))

    @jsii.member(jsii_name="resetValkeyActiveExpireEffort")
    def reset_valkey_active_expire_effort(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValkeyActiveExpireEffort", []))

    @jsii.member(jsii_name="resetValkeyIoThreads")
    def reset_valkey_io_threads(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValkeyIoThreads", []))

    @jsii.member(jsii_name="resetValkeyLfuDecayTime")
    def reset_valkey_lfu_decay_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValkeyLfuDecayTime", []))

    @jsii.member(jsii_name="resetValkeyLfuLogFactor")
    def reset_valkey_lfu_log_factor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValkeyLfuLogFactor", []))

    @jsii.member(jsii_name="resetValkeyMaxmemoryPolicy")
    def reset_valkey_maxmemory_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValkeyMaxmemoryPolicy", []))

    @jsii.member(jsii_name="resetValkeyNotifyKeyspaceEvents")
    def reset_valkey_notify_keyspace_events(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValkeyNotifyKeyspaceEvents", []))

    @jsii.member(jsii_name="resetValkeyNumberOfDatabases")
    def reset_valkey_number_of_databases(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValkeyNumberOfDatabases", []))

    @jsii.member(jsii_name="resetValkeyPersistence")
    def reset_valkey_persistence(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValkeyPersistence", []))

    @jsii.member(jsii_name="resetValkeyPubsubClientOutputBufferLimit")
    def reset_valkey_pubsub_client_output_buffer_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValkeyPubsubClientOutputBufferLimit", []))

    @jsii.member(jsii_name="resetValkeySsl")
    def reset_valkey_ssl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValkeySsl", []))

    @jsii.member(jsii_name="resetValkeyTimeout")
    def reset_valkey_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValkeyTimeout", []))

    @builtins.property
    @jsii.member(jsii_name="migration")
    def migration(self) -> ManagedDatabaseValkeyPropertiesMigrationOutputReference:
        return typing.cast(ManagedDatabaseValkeyPropertiesMigrationOutputReference, jsii.get(self, "migration"))

    @builtins.property
    @jsii.member(jsii_name="automaticUtilityNetworkIpFilterInput")
    def automatic_utility_network_ip_filter_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "automaticUtilityNetworkIpFilterInput"))

    @builtins.property
    @jsii.member(jsii_name="backupHourInput")
    def backup_hour_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "backupHourInput"))

    @builtins.property
    @jsii.member(jsii_name="backupMinuteInput")
    def backup_minute_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "backupMinuteInput"))

    @builtins.property
    @jsii.member(jsii_name="frequentSnapshotsInput")
    def frequent_snapshots_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "frequentSnapshotsInput"))

    @builtins.property
    @jsii.member(jsii_name="ipFilterInput")
    def ip_filter_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ipFilterInput"))

    @builtins.property
    @jsii.member(jsii_name="migrationInput")
    def migration_input(
        self,
    ) -> typing.Optional[ManagedDatabaseValkeyPropertiesMigration]:
        return typing.cast(typing.Optional[ManagedDatabaseValkeyPropertiesMigration], jsii.get(self, "migrationInput"))

    @builtins.property
    @jsii.member(jsii_name="publicAccessInput")
    def public_access_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "publicAccessInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceLogInput")
    def service_log_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "serviceLogInput"))

    @builtins.property
    @jsii.member(jsii_name="valkeyAclChannelsDefaultInput")
    def valkey_acl_channels_default_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valkeyAclChannelsDefaultInput"))

    @builtins.property
    @jsii.member(jsii_name="valkeyActiveExpireEffortInput")
    def valkey_active_expire_effort_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "valkeyActiveExpireEffortInput"))

    @builtins.property
    @jsii.member(jsii_name="valkeyIoThreadsInput")
    def valkey_io_threads_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "valkeyIoThreadsInput"))

    @builtins.property
    @jsii.member(jsii_name="valkeyLfuDecayTimeInput")
    def valkey_lfu_decay_time_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "valkeyLfuDecayTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="valkeyLfuLogFactorInput")
    def valkey_lfu_log_factor_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "valkeyLfuLogFactorInput"))

    @builtins.property
    @jsii.member(jsii_name="valkeyMaxmemoryPolicyInput")
    def valkey_maxmemory_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valkeyMaxmemoryPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="valkeyNotifyKeyspaceEventsInput")
    def valkey_notify_keyspace_events_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valkeyNotifyKeyspaceEventsInput"))

    @builtins.property
    @jsii.member(jsii_name="valkeyNumberOfDatabasesInput")
    def valkey_number_of_databases_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "valkeyNumberOfDatabasesInput"))

    @builtins.property
    @jsii.member(jsii_name="valkeyPersistenceInput")
    def valkey_persistence_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valkeyPersistenceInput"))

    @builtins.property
    @jsii.member(jsii_name="valkeyPubsubClientOutputBufferLimitInput")
    def valkey_pubsub_client_output_buffer_limit_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "valkeyPubsubClientOutputBufferLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="valkeySslInput")
    def valkey_ssl_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "valkeySslInput"))

    @builtins.property
    @jsii.member(jsii_name="valkeyTimeoutInput")
    def valkey_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "valkeyTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="automaticUtilityNetworkIpFilter")
    def automatic_utility_network_ip_filter(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "automaticUtilityNetworkIpFilter"))

    @automatic_utility_network_ip_filter.setter
    def automatic_utility_network_ip_filter(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c44d89cc2ed32723b08157526a381420fa119892c564fdedde7987c627d199b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "automaticUtilityNetworkIpFilter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backupHour")
    def backup_hour(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "backupHour"))

    @backup_hour.setter
    def backup_hour(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97fa6c9348419174573baa4a126b6a8e3f160ce4b9144a878e9c0157547f9cc1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backupHour", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backupMinute")
    def backup_minute(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "backupMinute"))

    @backup_minute.setter
    def backup_minute(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__811ddadc48f4551492d04783df1afbc040352a53ea4bee82d0508e3280c3c005)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backupMinute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="frequentSnapshots")
    def frequent_snapshots(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "frequentSnapshots"))

    @frequent_snapshots.setter
    def frequent_snapshots(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__646598e86ca197e938b0074e26a843906c102c1f767561d419d4b508b6dd8ebc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frequentSnapshots", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipFilter")
    def ip_filter(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ipFilter"))

    @ip_filter.setter
    def ip_filter(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef2b45dbaf8564a5828368af43f39e9e9b46f8662d13ce44cef40b45ec56f7db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipFilter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="publicAccess")
    def public_access(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "publicAccess"))

    @public_access.setter
    def public_access(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61f81631eb5f8dd781126f6a71849383ca6cb5c401a058533d0c001fdd87e963)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publicAccess", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceLog")
    def service_log(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "serviceLog"))

    @service_log.setter
    def service_log(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f875fc8095f055f0ecdfe6f2ab3f46d09111243c7ea6f03961499925bb56f00f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceLog", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="valkeyAclChannelsDefault")
    def valkey_acl_channels_default(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "valkeyAclChannelsDefault"))

    @valkey_acl_channels_default.setter
    def valkey_acl_channels_default(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fe20994370fab9130ba3ce108940f96e8805127e4d82f5b2696c1c8ed479423)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "valkeyAclChannelsDefault", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="valkeyActiveExpireEffort")
    def valkey_active_expire_effort(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "valkeyActiveExpireEffort"))

    @valkey_active_expire_effort.setter
    def valkey_active_expire_effort(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a26a8daa6315829cda61d30808c33733bd97f50727f9bf40cee814b3c2987089)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "valkeyActiveExpireEffort", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="valkeyIoThreads")
    def valkey_io_threads(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "valkeyIoThreads"))

    @valkey_io_threads.setter
    def valkey_io_threads(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36712e3e7fe0a856cf4cdb0e99d545b70df6ff8cb75d1732956a23af8faec9e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "valkeyIoThreads", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="valkeyLfuDecayTime")
    def valkey_lfu_decay_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "valkeyLfuDecayTime"))

    @valkey_lfu_decay_time.setter
    def valkey_lfu_decay_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15b6c8ce90519918204fdd1183efa1a627bb95b3268a6503b277d9da7d723c8b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "valkeyLfuDecayTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="valkeyLfuLogFactor")
    def valkey_lfu_log_factor(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "valkeyLfuLogFactor"))

    @valkey_lfu_log_factor.setter
    def valkey_lfu_log_factor(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e243578f8d78eab75cc755766a8e4f4fcb788de8b816bb45a1718db182b8ec4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "valkeyLfuLogFactor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="valkeyMaxmemoryPolicy")
    def valkey_maxmemory_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "valkeyMaxmemoryPolicy"))

    @valkey_maxmemory_policy.setter
    def valkey_maxmemory_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58d2a600744f7ded9d19d6d64758106e5dd26bf9bdefb7de08c43c6d281af215)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "valkeyMaxmemoryPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="valkeyNotifyKeyspaceEvents")
    def valkey_notify_keyspace_events(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "valkeyNotifyKeyspaceEvents"))

    @valkey_notify_keyspace_events.setter
    def valkey_notify_keyspace_events(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c11e8e05f6c742e65ebab02abf104aef2a997d1558d32e6d01bbe3f4af5ea10c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "valkeyNotifyKeyspaceEvents", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="valkeyNumberOfDatabases")
    def valkey_number_of_databases(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "valkeyNumberOfDatabases"))

    @valkey_number_of_databases.setter
    def valkey_number_of_databases(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10762b45ffd584091d6e5c546b00dc514e09029433109616a18715a1f850ad7d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "valkeyNumberOfDatabases", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="valkeyPersistence")
    def valkey_persistence(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "valkeyPersistence"))

    @valkey_persistence.setter
    def valkey_persistence(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3df38d43378b5c11dc6050c05dde117eecd487d129fac6402013aeed9ae8cd65)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "valkeyPersistence", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="valkeyPubsubClientOutputBufferLimit")
    def valkey_pubsub_client_output_buffer_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "valkeyPubsubClientOutputBufferLimit"))

    @valkey_pubsub_client_output_buffer_limit.setter
    def valkey_pubsub_client_output_buffer_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0dbcafcb27e6d3915244903e1e717c58586f72ad8034de91b6484a17f6a8b7a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "valkeyPubsubClientOutputBufferLimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="valkeySsl")
    def valkey_ssl(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "valkeySsl"))

    @valkey_ssl.setter
    def valkey_ssl(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2de1b44225297c589501a1169672e24a61f63a2250c403c2043fac2c3d51453b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "valkeySsl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="valkeyTimeout")
    def valkey_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "valkeyTimeout"))

    @valkey_timeout.setter
    def valkey_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb3af04522bbfd913260c5a68eacc426646fd40c2d829645b45ec90d5496c7d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "valkeyTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ManagedDatabaseValkeyProperties]:
        return typing.cast(typing.Optional[ManagedDatabaseValkeyProperties], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseValkeyProperties],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e856dbf1220e8ba94728c6777bc94aa3e02eb3316a2fe713db6fc687015a748)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ManagedDatabaseValkey",
    "ManagedDatabaseValkeyComponents",
    "ManagedDatabaseValkeyComponentsList",
    "ManagedDatabaseValkeyComponentsOutputReference",
    "ManagedDatabaseValkeyConfig",
    "ManagedDatabaseValkeyNetwork",
    "ManagedDatabaseValkeyNetworkList",
    "ManagedDatabaseValkeyNetworkOutputReference",
    "ManagedDatabaseValkeyNodeStates",
    "ManagedDatabaseValkeyNodeStatesList",
    "ManagedDatabaseValkeyNodeStatesOutputReference",
    "ManagedDatabaseValkeyProperties",
    "ManagedDatabaseValkeyPropertiesMigration",
    "ManagedDatabaseValkeyPropertiesMigrationOutputReference",
    "ManagedDatabaseValkeyPropertiesOutputReference",
]

publication.publish()

def _typecheckingstub__e9ca96a3d0255aab5bd629d642e8855d0ea99f8657e2d22de939cb10aa9e11a4(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    plan: builtins.str,
    title: builtins.str,
    zone: builtins.str,
    id: typing.Optional[builtins.str] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    maintenance_window_dow: typing.Optional[builtins.str] = None,
    maintenance_window_time: typing.Optional[builtins.str] = None,
    network: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedDatabaseValkeyNetwork, typing.Dict[builtins.str, typing.Any]]]]] = None,
    powered: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    properties: typing.Optional[typing.Union[ManagedDatabaseValkeyProperties, typing.Dict[builtins.str, typing.Any]]] = None,
    termination_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__9aedfd54b5c8b1f9918c7d3df38964719bab01ca5620baa0cdacd432478b79a7(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d39301ce9e83b0c46471cc2e091a974add7699ff0499897b02f5890d167025c6(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedDatabaseValkeyNetwork, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b41fe74abf03b1ee4f0b5f521d5e3e995ded4c72f89438f83df1a19a755cf210(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__582e5d19d5e9e322b330c3b5bede9c40c98cc138fef81206fe5627e535dff1bb(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__143dbf09447146d1251e1d077d8d015a4d72185c65356c2cbc926407d4a9d66d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94bc5c33c77b831f6591e0bd7fc829f250e2b41e491c36b6e70fba5c7fca15f8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2558e1f521ac9d42f41277e188f9b3916e911b33d98c46eba7b35837f9d5e5aa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d03add559c3e5c8300d41809a9579ab79a30ac2280a9116b12f9e956f5b176e7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8bad55e55d8452abe892cea5a4bec66a6ab86e9bc3d56b0a36cfe63e18325c01(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e2a35e3062885d4364913bf8f82e9adbc5cf8ee7b9a4712ac632c0c18444667(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__587e4697953225f3226603c43b6632073e29e531cd8559a516447b2f279761f1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d784cbad4812d74571ea6bd4f345ded5999d60288344c5b7666a672de8ab4f93(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf4f52898b75a9b0604cb414405e6251854854d6b3965a6524b46da5002b3322(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4252d9db585952153c1c7b4ab9959c5e9735acd2eacc7718a173e3af9b63655(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d6e320ee08cff87cf383a49d240e7b08cc1cde188220b5ebbaa1aa01276cd47(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d01ad4104711108a61bfe60b65ce72760f44f64c48e6d32829e0cd80c705aae2(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9717b3417f02063948e02cb67f4622cbd85be8020fbdec4526701605c0e76db8(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74486c446b4bb4d03113a6716ef1ae8d4f578400c1889d35913c174dcca771eb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8aac1a49ad50d49df4e2f2de04bd60a6f054eeff1e57e01b8130b16417b58c3(
    value: typing.Optional[ManagedDatabaseValkeyComponents],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__572e81ffbdca76e6a311042e02f5f60989357be28c5c9418094954727f2b5e84(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    plan: builtins.str,
    title: builtins.str,
    zone: builtins.str,
    id: typing.Optional[builtins.str] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    maintenance_window_dow: typing.Optional[builtins.str] = None,
    maintenance_window_time: typing.Optional[builtins.str] = None,
    network: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedDatabaseValkeyNetwork, typing.Dict[builtins.str, typing.Any]]]]] = None,
    powered: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    properties: typing.Optional[typing.Union[ManagedDatabaseValkeyProperties, typing.Dict[builtins.str, typing.Any]]] = None,
    termination_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86bc6cfbeb2b0d724aae3cd0dc476ec5f0060e413bec0604ca6101e019eba72f(
    *,
    family: builtins.str,
    name: builtins.str,
    type: builtins.str,
    uuid: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f387effda8c16fde9966811ccf787b3d56271088a5b593d10bd528d49165c7f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2cc2c3d970c95aa4a181f20ece6cae2da769925316379879259191e890fc425(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1f288935f98f823df0793a078e8de29a92298eeac83e277d79e6f5b6e9c6819(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ce318a3e6e190673efb3cff247a30d8c50c2a72993e57587a0a7bbac9667ca3(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__481786a55a2dc14dc3f4da44e7f8873f8427ecce80d885eb17eeee0c53c32a87(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b13648ea5908387b35158d29883e52641c749981675ab65432e63968b8ef75a5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedDatabaseValkeyNetwork]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2824d1ded7fae4598e64b29704860b7e65e1f60cc8c2ba18af6f88b9c393faff(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fa688fb44a82433ca388090b8249ad71a4bc831cce3794d229093b4b56293f6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b54ca25e12af584a57e78a38206ab3436c3e1bac4eee6604e90f51def133755(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1226f980d40c87f8397fe48cb9cc06bf941eea21e26fac7b5530ae632e3503b4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12fdc41f27c6b4f2b911ddd6aba5ce7018770875b804e05212b99416e015528d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1bf6882d93a48e5aa568b7df8ec4368202184ba0e5546a39a063fbf8b69e0628(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedDatabaseValkeyNetwork]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b36a07f4f6613a569fb00669f4dff53d81c6ac0bf2755480fb4e80a1743c29ef(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7c171b3c8fbf5cf7cde17ad2a04170148cb54b6d4df2b7940c311e02710b1f9(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a84231c9993c80153c365716c8c01dab8e9bea7cb1687ec9ffe5a59e4b2a6324(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33024060d747d6f3e2c9b75456197397a7aef2d57295c92716c794d24de628a0(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b4b326613b451e91b53641f7d027967e6b69bfef13702d5adde4da4e2e83459(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3584d0fded5a72760262405f68d64086374d1b0be18591d1e84bb4af5db5c06f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23d6fd61468e82793403951f52c6440df44471673eda077d3768f80950de87be(
    value: typing.Optional[ManagedDatabaseValkeyNodeStates],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__130504794befd55a7bc90ab03ca53c94a25f9b733cdd13efed4a51695da4b995(
    *,
    automatic_utility_network_ip_filter: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    backup_hour: typing.Optional[jsii.Number] = None,
    backup_minute: typing.Optional[jsii.Number] = None,
    frequent_snapshots: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ip_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
    migration: typing.Optional[typing.Union[ManagedDatabaseValkeyPropertiesMigration, typing.Dict[builtins.str, typing.Any]]] = None,
    public_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    service_log: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    valkey_acl_channels_default: typing.Optional[builtins.str] = None,
    valkey_active_expire_effort: typing.Optional[jsii.Number] = None,
    valkey_io_threads: typing.Optional[jsii.Number] = None,
    valkey_lfu_decay_time: typing.Optional[jsii.Number] = None,
    valkey_lfu_log_factor: typing.Optional[jsii.Number] = None,
    valkey_maxmemory_policy: typing.Optional[builtins.str] = None,
    valkey_notify_keyspace_events: typing.Optional[builtins.str] = None,
    valkey_number_of_databases: typing.Optional[jsii.Number] = None,
    valkey_persistence: typing.Optional[builtins.str] = None,
    valkey_pubsub_client_output_buffer_limit: typing.Optional[jsii.Number] = None,
    valkey_ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    valkey_timeout: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79d93789bda00eb59095ff4b93fc8d576f547960656fc2c2b20cdd46b3842774(
    *,
    dbname: typing.Optional[builtins.str] = None,
    host: typing.Optional[builtins.str] = None,
    ignore_dbs: typing.Optional[builtins.str] = None,
    ignore_roles: typing.Optional[builtins.str] = None,
    method: typing.Optional[builtins.str] = None,
    password: typing.Optional[builtins.str] = None,
    port: typing.Optional[jsii.Number] = None,
    ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    username: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__653b9500142dcaaa00ba3451c2ff31751e33552cb8092bcd3c7cdc2da14e47cd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1314b6cb90839f64d1e6b134d07633136410e75b81032064900446b8247729d5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76243e98f6cb500875bf56e8d226c15068248549c3ecd1b38c8ae49ffcdd0c65(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__162cd0275fe93ffc0222678a946ecd079acd01731fd60103ce60dd5b536809be(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6fdf035c2bfaaf78851ed75b4776ecfc0280916d034d8d88e5c518b4d31606e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e35e85c39397173d3e45859019af030a0c6b4ceaa3a4e544f90652fddaec8daf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__662e37d640a89c81978ab1bc6760bef1547ed14b8359ccf76d5f8c5ba2c1ca85(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af55c31711e4f7afee55e9eb3357116e63b64c1178aa20a3b34caff9e7d36c63(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f483e3934be4c35439acb518122bb176bb613a0bb411d2384a025b2fe6dbaa40(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a34f9da5159916189640a32002175c4e592ba0b30620af992ca26e34a7aa9aa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1793c40b292b55abd22e900135f7fb7177ba88955948317e0f8e1140a8fd6bb9(
    value: typing.Optional[ManagedDatabaseValkeyPropertiesMigration],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55792d3e90a4aee66c1699f91bdcfb7f0f4fdd7ccf76213d91486a87ffeb6e7f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c44d89cc2ed32723b08157526a381420fa119892c564fdedde7987c627d199b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97fa6c9348419174573baa4a126b6a8e3f160ce4b9144a878e9c0157547f9cc1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__811ddadc48f4551492d04783df1afbc040352a53ea4bee82d0508e3280c3c005(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__646598e86ca197e938b0074e26a843906c102c1f767561d419d4b508b6dd8ebc(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef2b45dbaf8564a5828368af43f39e9e9b46f8662d13ce44cef40b45ec56f7db(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61f81631eb5f8dd781126f6a71849383ca6cb5c401a058533d0c001fdd87e963(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f875fc8095f055f0ecdfe6f2ab3f46d09111243c7ea6f03961499925bb56f00f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fe20994370fab9130ba3ce108940f96e8805127e4d82f5b2696c1c8ed479423(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a26a8daa6315829cda61d30808c33733bd97f50727f9bf40cee814b3c2987089(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36712e3e7fe0a856cf4cdb0e99d545b70df6ff8cb75d1732956a23af8faec9e8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15b6c8ce90519918204fdd1183efa1a627bb95b3268a6503b277d9da7d723c8b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e243578f8d78eab75cc755766a8e4f4fcb788de8b816bb45a1718db182b8ec4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58d2a600744f7ded9d19d6d64758106e5dd26bf9bdefb7de08c43c6d281af215(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c11e8e05f6c742e65ebab02abf104aef2a997d1558d32e6d01bbe3f4af5ea10c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10762b45ffd584091d6e5c546b00dc514e09029433109616a18715a1f850ad7d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3df38d43378b5c11dc6050c05dde117eecd487d129fac6402013aeed9ae8cd65(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0dbcafcb27e6d3915244903e1e717c58586f72ad8034de91b6484a17f6a8b7a5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2de1b44225297c589501a1169672e24a61f63a2250c403c2043fac2c3d51453b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb3af04522bbfd913260c5a68eacc426646fd40c2d829645b45ec90d5496c7d0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e856dbf1220e8ba94728c6777bc94aa3e02eb3316a2fe713db6fc687015a748(
    value: typing.Optional[ManagedDatabaseValkeyProperties],
) -> None:
    """Type checking stubs"""
    pass
