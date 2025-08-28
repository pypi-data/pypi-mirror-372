r'''
# `upcloud_managed_database_opensearch`

Refer to the Terraform Registry for docs: [`upcloud_managed_database_opensearch`](https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch).
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


class ManagedDatabaseOpensearch(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearch",
):
    '''Represents a {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch upcloud_managed_database_opensearch}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        plan: builtins.str,
        title: builtins.str,
        zone: builtins.str,
        access_control: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        extended_access_control: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        maintenance_window_dow: typing.Optional[builtins.str] = None,
        maintenance_window_time: typing.Optional[builtins.str] = None,
        network: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedDatabaseOpensearchNetwork", typing.Dict[builtins.str, typing.Any]]]]] = None,
        powered: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        properties: typing.Optional[typing.Union["ManagedDatabaseOpensearchProperties", typing.Dict[builtins.str, typing.Any]]] = None,
        termination_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch upcloud_managed_database_opensearch} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Name of the service. The name is used as a prefix for the logical hostname. Must be unique within an account Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#name ManagedDatabaseOpensearch#name}
        :param plan: Service plan to use. This determines how much resources the instance will have. You can list available plans with ``upctl database plans <type>``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#plan ManagedDatabaseOpensearch#plan}
        :param title: Title of a managed database instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#title ManagedDatabaseOpensearch#title}
        :param zone: Zone where the instance resides, e.g. ``de-fra1``. You can list available zones with ``upctl zone list``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#zone ManagedDatabaseOpensearch#zone}
        :param access_control: Enables users access control for OpenSearch service. User access control rules will only be enforced if this attribute is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#access_control ManagedDatabaseOpensearch#access_control}
        :param extended_access_control: Grant access to top-level ``_mget``, ``_msearch`` and ``_bulk`` APIs. Users are limited to perform operations on indices based on the user-specific access control rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#extended_access_control ManagedDatabaseOpensearch#extended_access_control}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#id ManagedDatabaseOpensearch#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param labels: User defined key-value pairs to classify the managed database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#labels ManagedDatabaseOpensearch#labels}
        :param maintenance_window_dow: Maintenance window day of week. Lower case weekday name (monday, tuesday, ...). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#maintenance_window_dow ManagedDatabaseOpensearch#maintenance_window_dow}
        :param maintenance_window_time: Maintenance window UTC time in hh:mm:ss format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#maintenance_window_time ManagedDatabaseOpensearch#maintenance_window_time}
        :param network: network block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#network ManagedDatabaseOpensearch#network}
        :param powered: The administrative power state of the service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#powered ManagedDatabaseOpensearch#powered}
        :param properties: properties block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#properties ManagedDatabaseOpensearch#properties}
        :param termination_protection: If set to true, prevents the managed service from being powered off, or deleted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#termination_protection ManagedDatabaseOpensearch#termination_protection}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64a04d8da6e4f1b319a40ace3990acecec34666de7dc4b9125beebfecfa929af)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ManagedDatabaseOpensearchConfig(
            name=name,
            plan=plan,
            title=title,
            zone=zone,
            access_control=access_control,
            extended_access_control=extended_access_control,
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
        '''Generates CDKTF code for importing a ManagedDatabaseOpensearch resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ManagedDatabaseOpensearch to import.
        :param import_from_id: The id of the existing ManagedDatabaseOpensearch that should be imported. Refer to the {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ManagedDatabaseOpensearch to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99473b30cd8c5d5bf751dc40a87eb264e6f724273e36350fb7751af5f0292918)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putNetwork")
    def put_network(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedDatabaseOpensearchNetwork", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__827b59afce111c617fb7e5a741d9b2a3004395e4c68a14fedcd8c61308c66442)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNetwork", [value]))

    @jsii.member(jsii_name="putProperties")
    def put_properties(
        self,
        *,
        action_auto_create_index_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        action_destructive_requires_name: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auth_failure_listeners: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesAuthFailureListeners", typing.Dict[builtins.str, typing.Any]]] = None,
        automatic_utility_network_ip_filter: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cluster_filecache_remote_data_ratio: typing.Optional[jsii.Number] = None,
        cluster_max_shards_per_node: typing.Optional[jsii.Number] = None,
        cluster_remote_store: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesClusterRemoteStore", typing.Dict[builtins.str, typing.Any]]] = None,
        cluster_routing_allocation_balance_prefer_primary: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cluster_routing_allocation_node_concurrent_recoveries: typing.Optional[jsii.Number] = None,
        cluster_search_request_slowlog: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlog", typing.Dict[builtins.str, typing.Any]]] = None,
        custom_domain: typing.Optional[builtins.str] = None,
        disk_watermarks: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesDiskWatermarks", typing.Dict[builtins.str, typing.Any]]] = None,
        elasticsearch_version: typing.Optional[builtins.str] = None,
        email_sender_name: typing.Optional[builtins.str] = None,
        email_sender_password: typing.Optional[builtins.str] = None,
        email_sender_username: typing.Optional[builtins.str] = None,
        enable_remote_backed_storage: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_searchable_snapshots: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_security_audit: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_snapshot_api: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        http_max_content_length: typing.Optional[jsii.Number] = None,
        http_max_header_size: typing.Optional[jsii.Number] = None,
        http_max_initial_line_length: typing.Optional[jsii.Number] = None,
        index_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
        index_rollup: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesIndexRollup", typing.Dict[builtins.str, typing.Any]]] = None,
        index_template: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesIndexTemplate", typing.Dict[builtins.str, typing.Any]]] = None,
        indices_fielddata_cache_size: typing.Optional[jsii.Number] = None,
        indices_memory_index_buffer_size: typing.Optional[jsii.Number] = None,
        indices_memory_max_index_buffer_size: typing.Optional[jsii.Number] = None,
        indices_memory_min_index_buffer_size: typing.Optional[jsii.Number] = None,
        indices_queries_cache_size: typing.Optional[jsii.Number] = None,
        indices_query_bool_max_clause_count: typing.Optional[jsii.Number] = None,
        indices_recovery_max_bytes_per_sec: typing.Optional[jsii.Number] = None,
        indices_recovery_max_concurrent_file_chunks: typing.Optional[jsii.Number] = None,
        ip_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
        ism_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ism_history_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ism_history_max_age: typing.Optional[jsii.Number] = None,
        ism_history_max_docs: typing.Optional[jsii.Number] = None,
        ism_history_rollover_check_period: typing.Optional[jsii.Number] = None,
        ism_history_rollover_retention_period: typing.Optional[jsii.Number] = None,
        keep_index_refresh_interval: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        knn_memory_circuit_breaker_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        knn_memory_circuit_breaker_limit: typing.Optional[jsii.Number] = None,
        node_search_cache_size: typing.Optional[builtins.str] = None,
        openid: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesOpenid", typing.Dict[builtins.str, typing.Any]]] = None,
        opensearch_dashboards: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesOpensearchDashboards", typing.Dict[builtins.str, typing.Any]]] = None,
        override_main_response_version: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        plugins_alerting_filter_by_backend_roles: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        public_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        reindex_remote_whitelist: typing.Optional[typing.Sequence[builtins.str]] = None,
        remote_store: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesRemoteStore", typing.Dict[builtins.str, typing.Any]]] = None,
        saml: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesSaml", typing.Dict[builtins.str, typing.Any]]] = None,
        script_max_compilations_rate: typing.Optional[builtins.str] = None,
        search_backpressure: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesSearchBackpressure", typing.Dict[builtins.str, typing.Any]]] = None,
        search_insights_top_queries: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueries", typing.Dict[builtins.str, typing.Any]]] = None,
        search_max_buckets: typing.Optional[jsii.Number] = None,
        segrep: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesSegrep", typing.Dict[builtins.str, typing.Any]]] = None,
        service_log: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        shard_indexing_pressure: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesShardIndexingPressure", typing.Dict[builtins.str, typing.Any]]] = None,
        thread_pool_analyze_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_analyze_size: typing.Optional[jsii.Number] = None,
        thread_pool_force_merge_size: typing.Optional[jsii.Number] = None,
        thread_pool_get_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_get_size: typing.Optional[jsii.Number] = None,
        thread_pool_search_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_search_size: typing.Optional[jsii.Number] = None,
        thread_pool_search_throttled_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_search_throttled_size: typing.Optional[jsii.Number] = None,
        thread_pool_write_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_write_size: typing.Optional[jsii.Number] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param action_auto_create_index_enabled: action.auto_create_index. Explicitly allow or block automatic creation of indices. Defaults to true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#action_auto_create_index_enabled ManagedDatabaseOpensearch#action_auto_create_index_enabled}
        :param action_destructive_requires_name: Require explicit index names when deleting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#action_destructive_requires_name ManagedDatabaseOpensearch#action_destructive_requires_name}
        :param auth_failure_listeners: auth_failure_listeners block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#auth_failure_listeners ManagedDatabaseOpensearch#auth_failure_listeners}
        :param automatic_utility_network_ip_filter: Automatic utility network IP Filter. Automatically allow connections from servers in the utility network within the same zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#automatic_utility_network_ip_filter ManagedDatabaseOpensearch#automatic_utility_network_ip_filter}
        :param cluster_filecache_remote_data_ratio: The limit of how much total remote data can be referenced. Defines a limit of how much total remote data can be referenced as a ratio of the size of the disk reserved for the file cache. This is designed to be a safeguard to prevent oversubscribing a cluster. Defaults to 0. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cluster_filecache_remote_data_ratio ManagedDatabaseOpensearch#cluster_filecache_remote_data_ratio}
        :param cluster_max_shards_per_node: Controls the number of shards allowed in the cluster per data node. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cluster_max_shards_per_node ManagedDatabaseOpensearch#cluster_max_shards_per_node}
        :param cluster_remote_store: cluster_remote_store block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cluster_remote_store ManagedDatabaseOpensearch#cluster_remote_store}
        :param cluster_routing_allocation_balance_prefer_primary: When set to true, OpenSearch attempts to evenly distribute the primary shards between the cluster nodes. Enabling this setting does not always guarantee an equal number of primary shards on each node, especially in the event of a failover. Changing this setting to false after it was set to true does not invoke redistribution of primary shards. Default is false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cluster_routing_allocation_balance_prefer_primary ManagedDatabaseOpensearch#cluster_routing_allocation_balance_prefer_primary}
        :param cluster_routing_allocation_node_concurrent_recoveries: Concurrent incoming/outgoing shard recoveries per node. How many concurrent incoming/outgoing shard recoveries (normally replicas) are allowed to happen on a node. Defaults to node cpu count * 2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cluster_routing_allocation_node_concurrent_recoveries ManagedDatabaseOpensearch#cluster_routing_allocation_node_concurrent_recoveries}
        :param cluster_search_request_slowlog: cluster_search_request_slowlog block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cluster_search_request_slowlog ManagedDatabaseOpensearch#cluster_search_request_slowlog}
        :param custom_domain: Custom domain. Serve the web frontend using a custom CNAME pointing to the Aiven DNS name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#custom_domain ManagedDatabaseOpensearch#custom_domain}
        :param disk_watermarks: disk_watermarks block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#disk_watermarks ManagedDatabaseOpensearch#disk_watermarks}
        :param elasticsearch_version: Elasticsearch major version. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#elasticsearch_version ManagedDatabaseOpensearch#elasticsearch_version}
        :param email_sender_name: Sender name placeholder to be used in Opensearch Dashboards and Opensearch keystore. This should be identical to the Sender name defined in Opensearch dashboards. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#email_sender_name ManagedDatabaseOpensearch#email_sender_name}
        :param email_sender_password: Sender password for Opensearch alerts to authenticate with SMTP server. Sender password for Opensearch alerts to authenticate with SMTP server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#email_sender_password ManagedDatabaseOpensearch#email_sender_password}
        :param email_sender_username: Sender username for Opensearch alerts. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#email_sender_username ManagedDatabaseOpensearch#email_sender_username}
        :param enable_remote_backed_storage: Enable remote-backed storage. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enable_remote_backed_storage ManagedDatabaseOpensearch#enable_remote_backed_storage}
        :param enable_searchable_snapshots: Enable searchable snapshots. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enable_searchable_snapshots ManagedDatabaseOpensearch#enable_searchable_snapshots}
        :param enable_security_audit: Enable/Disable security audit. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enable_security_audit ManagedDatabaseOpensearch#enable_security_audit}
        :param enable_snapshot_api: Enable/Disable snapshot API. Enable/Disable snapshot API for custom repositories, this requires security management to be enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enable_snapshot_api ManagedDatabaseOpensearch#enable_snapshot_api}
        :param http_max_content_length: Maximum content length for HTTP requests to the OpenSearch HTTP API, in bytes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#http_max_content_length ManagedDatabaseOpensearch#http_max_content_length}
        :param http_max_header_size: The max size of allowed headers, in bytes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#http_max_header_size ManagedDatabaseOpensearch#http_max_header_size}
        :param http_max_initial_line_length: The max length of an HTTP URL, in bytes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#http_max_initial_line_length ManagedDatabaseOpensearch#http_max_initial_line_length}
        :param index_patterns: Index patterns. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#index_patterns ManagedDatabaseOpensearch#index_patterns}
        :param index_rollup: index_rollup block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#index_rollup ManagedDatabaseOpensearch#index_rollup}
        :param index_template: index_template block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#index_template ManagedDatabaseOpensearch#index_template}
        :param indices_fielddata_cache_size: Relative amount. Maximum amount of heap memory used for field data cache. This is an expert setting; decreasing the value too much will increase overhead of loading field data; too much memory used for field data cache will decrease amount of heap available for other operations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#indices_fielddata_cache_size ManagedDatabaseOpensearch#indices_fielddata_cache_size}
        :param indices_memory_index_buffer_size: Percentage value. Default is 10%. Total amount of heap used for indexing buffer, before writing segments to disk. This is an expert setting. Too low value will slow down indexing; too high value will increase indexing performance but causes performance issues for query performance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#indices_memory_index_buffer_size ManagedDatabaseOpensearch#indices_memory_index_buffer_size}
        :param indices_memory_max_index_buffer_size: Absolute value. Default is unbound. Doesn't work without indices.memory.index_buffer_size. Maximum amount of heap used for query cache, an absolute indices.memory.index_buffer_size maximum hard limit. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#indices_memory_max_index_buffer_size ManagedDatabaseOpensearch#indices_memory_max_index_buffer_size}
        :param indices_memory_min_index_buffer_size: Absolute value. Default is 48mb. Doesn't work without indices.memory.index_buffer_size. Minimum amount of heap used for query cache, an absolute indices.memory.index_buffer_size minimal hard limit. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#indices_memory_min_index_buffer_size ManagedDatabaseOpensearch#indices_memory_min_index_buffer_size}
        :param indices_queries_cache_size: Percentage value. Default is 10%. Maximum amount of heap used for query cache. This is an expert setting. Too low value will decrease query performance and increase performance for other operations; too high value will cause issues with other OpenSearch functionality. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#indices_queries_cache_size ManagedDatabaseOpensearch#indices_queries_cache_size}
        :param indices_query_bool_max_clause_count: Maximum number of clauses Lucene BooleanQuery can have. The default value (1024) is relatively high, and increasing it may cause performance issues. Investigate other approaches first before increasing this value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#indices_query_bool_max_clause_count ManagedDatabaseOpensearch#indices_query_bool_max_clause_count}
        :param indices_recovery_max_bytes_per_sec: Limits total inbound and outbound recovery traffic for each node. Applies to both peer recoveries as well as snapshot recoveries (i.e., restores from a snapshot). Defaults to 40mb. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#indices_recovery_max_bytes_per_sec ManagedDatabaseOpensearch#indices_recovery_max_bytes_per_sec}
        :param indices_recovery_max_concurrent_file_chunks: Number of file chunks sent in parallel for each recovery. Defaults to 2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#indices_recovery_max_concurrent_file_chunks ManagedDatabaseOpensearch#indices_recovery_max_concurrent_file_chunks}
        :param ip_filter: IP filter. Allow incoming connections from CIDR address block, e.g. '10.20.0.0/16'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#ip_filter ManagedDatabaseOpensearch#ip_filter}
        :param ism_enabled: Specifies whether ISM is enabled or not. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#ism_enabled ManagedDatabaseOpensearch#ism_enabled}
        :param ism_history_enabled: Specifies whether audit history is enabled or not. The logs from ISM are automatically indexed to a logs document. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#ism_history_enabled ManagedDatabaseOpensearch#ism_history_enabled}
        :param ism_history_max_age: The maximum age before rolling over the audit history index in hours. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#ism_history_max_age ManagedDatabaseOpensearch#ism_history_max_age}
        :param ism_history_max_docs: The maximum number of documents before rolling over the audit history index. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#ism_history_max_docs ManagedDatabaseOpensearch#ism_history_max_docs}
        :param ism_history_rollover_check_period: The time between rollover checks for the audit history index in hours. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#ism_history_rollover_check_period ManagedDatabaseOpensearch#ism_history_rollover_check_period}
        :param ism_history_rollover_retention_period: How long audit history indices are kept in days. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#ism_history_rollover_retention_period ManagedDatabaseOpensearch#ism_history_rollover_retention_period}
        :param keep_index_refresh_interval: Don't reset index.refresh_interval to the default value. Aiven automation resets index.refresh_interval to default value for every index to be sure that indices are always visible to search. If it doesn't fit your case, you can disable this by setting up this flag to true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#keep_index_refresh_interval ManagedDatabaseOpensearch#keep_index_refresh_interval}
        :param knn_memory_circuit_breaker_enabled: Enable or disable KNN memory circuit breaker. Defaults to true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#knn_memory_circuit_breaker_enabled ManagedDatabaseOpensearch#knn_memory_circuit_breaker_enabled}
        :param knn_memory_circuit_breaker_limit: Maximum amount of memory that can be used for KNN index. Defaults to 50% of the JVM heap size. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#knn_memory_circuit_breaker_limit ManagedDatabaseOpensearch#knn_memory_circuit_breaker_limit}
        :param node_search_cache_size: The limit of how much total remote data can be referenced. Defines a limit of how much total remote data can be referenced as a ratio of the size of the disk reserved for the file cache. This is designed to be a safeguard to prevent oversubscribing a cluster. Defaults to 5gb. Requires restarting all OpenSearch nodes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#node_search_cache_size ManagedDatabaseOpensearch#node_search_cache_size}
        :param openid: openid block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#openid ManagedDatabaseOpensearch#openid}
        :param opensearch_dashboards: opensearch_dashboards block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#opensearch_dashboards ManagedDatabaseOpensearch#opensearch_dashboards}
        :param override_main_response_version: Compatibility mode sets OpenSearch to report its version as 7.10 so clients continue to work. Default is false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#override_main_response_version ManagedDatabaseOpensearch#override_main_response_version}
        :param plugins_alerting_filter_by_backend_roles: Enable or disable filtering of alerting by backend roles. Requires Security plugin. Defaults to false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#plugins_alerting_filter_by_backend_roles ManagedDatabaseOpensearch#plugins_alerting_filter_by_backend_roles}
        :param public_access: Public Access. Allow access to the service from the public Internet. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#public_access ManagedDatabaseOpensearch#public_access}
        :param reindex_remote_whitelist: Whitelisted addresses for reindexing. Changing this value will cause all OpenSearch instances to restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#reindex_remote_whitelist ManagedDatabaseOpensearch#reindex_remote_whitelist}
        :param remote_store: remote_store block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#remote_store ManagedDatabaseOpensearch#remote_store}
        :param saml: saml block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#saml ManagedDatabaseOpensearch#saml}
        :param script_max_compilations_rate: Script max compilation rate - circuit breaker to prevent/minimize OOMs. Script compilation circuit breaker limits the number of inline script compilations within a period of time. Default is use-context. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#script_max_compilations_rate ManagedDatabaseOpensearch#script_max_compilations_rate}
        :param search_backpressure: search_backpressure block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#search_backpressure ManagedDatabaseOpensearch#search_backpressure}
        :param search_insights_top_queries: search_insights_top_queries block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#search_insights_top_queries ManagedDatabaseOpensearch#search_insights_top_queries}
        :param search_max_buckets: Maximum number of aggregation buckets allowed in a single response. OpenSearch default value is used when this is not defined. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#search_max_buckets ManagedDatabaseOpensearch#search_max_buckets}
        :param segrep: segrep block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#segrep ManagedDatabaseOpensearch#segrep}
        :param service_log: Service logging. Store logs for the service so that they are available in the HTTP API and console. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#service_log ManagedDatabaseOpensearch#service_log}
        :param shard_indexing_pressure: shard_indexing_pressure block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#shard_indexing_pressure ManagedDatabaseOpensearch#shard_indexing_pressure}
        :param thread_pool_analyze_queue_size: analyze thread pool queue size. Size for the thread pool queue. See documentation for exact details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_analyze_queue_size ManagedDatabaseOpensearch#thread_pool_analyze_queue_size}
        :param thread_pool_analyze_size: analyze thread pool size. Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_analyze_size ManagedDatabaseOpensearch#thread_pool_analyze_size}
        :param thread_pool_force_merge_size: force_merge thread pool size. Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_force_merge_size ManagedDatabaseOpensearch#thread_pool_force_merge_size}
        :param thread_pool_get_queue_size: get thread pool queue size. Size for the thread pool queue. See documentation for exact details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_get_queue_size ManagedDatabaseOpensearch#thread_pool_get_queue_size}
        :param thread_pool_get_size: get thread pool size. Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_get_size ManagedDatabaseOpensearch#thread_pool_get_size}
        :param thread_pool_search_queue_size: search thread pool queue size. Size for the thread pool queue. See documentation for exact details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_search_queue_size ManagedDatabaseOpensearch#thread_pool_search_queue_size}
        :param thread_pool_search_size: search thread pool size. Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_search_size ManagedDatabaseOpensearch#thread_pool_search_size}
        :param thread_pool_search_throttled_queue_size: search_throttled thread pool queue size. Size for the thread pool queue. See documentation for exact details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_search_throttled_queue_size ManagedDatabaseOpensearch#thread_pool_search_throttled_queue_size}
        :param thread_pool_search_throttled_size: search_throttled thread pool size. Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_search_throttled_size ManagedDatabaseOpensearch#thread_pool_search_throttled_size}
        :param thread_pool_write_queue_size: write thread pool queue size. Size for the thread pool queue. See documentation for exact details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_write_queue_size ManagedDatabaseOpensearch#thread_pool_write_queue_size}
        :param thread_pool_write_size: write thread pool size. Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_write_size ManagedDatabaseOpensearch#thread_pool_write_size}
        :param version: OpenSearch major version. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#version ManagedDatabaseOpensearch#version}
        '''
        value = ManagedDatabaseOpensearchProperties(
            action_auto_create_index_enabled=action_auto_create_index_enabled,
            action_destructive_requires_name=action_destructive_requires_name,
            auth_failure_listeners=auth_failure_listeners,
            automatic_utility_network_ip_filter=automatic_utility_network_ip_filter,
            cluster_filecache_remote_data_ratio=cluster_filecache_remote_data_ratio,
            cluster_max_shards_per_node=cluster_max_shards_per_node,
            cluster_remote_store=cluster_remote_store,
            cluster_routing_allocation_balance_prefer_primary=cluster_routing_allocation_balance_prefer_primary,
            cluster_routing_allocation_node_concurrent_recoveries=cluster_routing_allocation_node_concurrent_recoveries,
            cluster_search_request_slowlog=cluster_search_request_slowlog,
            custom_domain=custom_domain,
            disk_watermarks=disk_watermarks,
            elasticsearch_version=elasticsearch_version,
            email_sender_name=email_sender_name,
            email_sender_password=email_sender_password,
            email_sender_username=email_sender_username,
            enable_remote_backed_storage=enable_remote_backed_storage,
            enable_searchable_snapshots=enable_searchable_snapshots,
            enable_security_audit=enable_security_audit,
            enable_snapshot_api=enable_snapshot_api,
            http_max_content_length=http_max_content_length,
            http_max_header_size=http_max_header_size,
            http_max_initial_line_length=http_max_initial_line_length,
            index_patterns=index_patterns,
            index_rollup=index_rollup,
            index_template=index_template,
            indices_fielddata_cache_size=indices_fielddata_cache_size,
            indices_memory_index_buffer_size=indices_memory_index_buffer_size,
            indices_memory_max_index_buffer_size=indices_memory_max_index_buffer_size,
            indices_memory_min_index_buffer_size=indices_memory_min_index_buffer_size,
            indices_queries_cache_size=indices_queries_cache_size,
            indices_query_bool_max_clause_count=indices_query_bool_max_clause_count,
            indices_recovery_max_bytes_per_sec=indices_recovery_max_bytes_per_sec,
            indices_recovery_max_concurrent_file_chunks=indices_recovery_max_concurrent_file_chunks,
            ip_filter=ip_filter,
            ism_enabled=ism_enabled,
            ism_history_enabled=ism_history_enabled,
            ism_history_max_age=ism_history_max_age,
            ism_history_max_docs=ism_history_max_docs,
            ism_history_rollover_check_period=ism_history_rollover_check_period,
            ism_history_rollover_retention_period=ism_history_rollover_retention_period,
            keep_index_refresh_interval=keep_index_refresh_interval,
            knn_memory_circuit_breaker_enabled=knn_memory_circuit_breaker_enabled,
            knn_memory_circuit_breaker_limit=knn_memory_circuit_breaker_limit,
            node_search_cache_size=node_search_cache_size,
            openid=openid,
            opensearch_dashboards=opensearch_dashboards,
            override_main_response_version=override_main_response_version,
            plugins_alerting_filter_by_backend_roles=plugins_alerting_filter_by_backend_roles,
            public_access=public_access,
            reindex_remote_whitelist=reindex_remote_whitelist,
            remote_store=remote_store,
            saml=saml,
            script_max_compilations_rate=script_max_compilations_rate,
            search_backpressure=search_backpressure,
            search_insights_top_queries=search_insights_top_queries,
            search_max_buckets=search_max_buckets,
            segrep=segrep,
            service_log=service_log,
            shard_indexing_pressure=shard_indexing_pressure,
            thread_pool_analyze_queue_size=thread_pool_analyze_queue_size,
            thread_pool_analyze_size=thread_pool_analyze_size,
            thread_pool_force_merge_size=thread_pool_force_merge_size,
            thread_pool_get_queue_size=thread_pool_get_queue_size,
            thread_pool_get_size=thread_pool_get_size,
            thread_pool_search_queue_size=thread_pool_search_queue_size,
            thread_pool_search_size=thread_pool_search_size,
            thread_pool_search_throttled_queue_size=thread_pool_search_throttled_queue_size,
            thread_pool_search_throttled_size=thread_pool_search_throttled_size,
            thread_pool_write_queue_size=thread_pool_write_queue_size,
            thread_pool_write_size=thread_pool_write_size,
            version=version,
        )

        return typing.cast(None, jsii.invoke(self, "putProperties", [value]))

    @jsii.member(jsii_name="resetAccessControl")
    def reset_access_control(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessControl", []))

    @jsii.member(jsii_name="resetExtendedAccessControl")
    def reset_extended_access_control(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExtendedAccessControl", []))

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
    def components(self) -> "ManagedDatabaseOpensearchComponentsList":
        return typing.cast("ManagedDatabaseOpensearchComponentsList", jsii.get(self, "components"))

    @builtins.property
    @jsii.member(jsii_name="network")
    def network(self) -> "ManagedDatabaseOpensearchNetworkList":
        return typing.cast("ManagedDatabaseOpensearchNetworkList", jsii.get(self, "network"))

    @builtins.property
    @jsii.member(jsii_name="nodeStates")
    def node_states(self) -> "ManagedDatabaseOpensearchNodeStatesList":
        return typing.cast("ManagedDatabaseOpensearchNodeStatesList", jsii.get(self, "nodeStates"))

    @builtins.property
    @jsii.member(jsii_name="primaryDatabase")
    def primary_database(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "primaryDatabase"))

    @builtins.property
    @jsii.member(jsii_name="properties")
    def properties(self) -> "ManagedDatabaseOpensearchPropertiesOutputReference":
        return typing.cast("ManagedDatabaseOpensearchPropertiesOutputReference", jsii.get(self, "properties"))

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
    @jsii.member(jsii_name="accessControlInput")
    def access_control_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "accessControlInput"))

    @builtins.property
    @jsii.member(jsii_name="extendedAccessControlInput")
    def extended_access_control_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "extendedAccessControlInput"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedDatabaseOpensearchNetwork"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedDatabaseOpensearchNetwork"]]], jsii.get(self, "networkInput"))

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
    def properties_input(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchProperties"]:
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchProperties"], jsii.get(self, "propertiesInput"))

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
    @jsii.member(jsii_name="accessControl")
    def access_control(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "accessControl"))

    @access_control.setter
    def access_control(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc380db9b723b44538f0654f873b7e6938e7f77a5500c11f59172853bb812451)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessControl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="extendedAccessControl")
    def extended_access_control(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "extendedAccessControl"))

    @extended_access_control.setter
    def extended_access_control(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a861bcb5d8f073071a3fc6c246b46bb262c59eb6ed230613542b683d9ed7c266)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "extendedAccessControl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03c43ec7ae33e6b60985ef2de80521f4f4ad3629a44711cd102de73bdede18b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab7b7c324ffaf25c97aa2385c0cd8bc6a0d40f0cd84fade78ab276bb76bd2286)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "labels", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowDow")
    def maintenance_window_dow(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maintenanceWindowDow"))

    @maintenance_window_dow.setter
    def maintenance_window_dow(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__778bfd3bad1122cec5c9a8b1233c9c30f21e60cdc07d7a6dcd73160f3e8f3e9c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maintenanceWindowDow", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowTime")
    def maintenance_window_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maintenanceWindowTime"))

    @maintenance_window_time.setter
    def maintenance_window_time(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__530a55728ead99da54d717ec010026a48f653d62a58301fef9f9b7df2338770b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maintenanceWindowTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__483f921db7c5dfd553cc7ae4edbed08bbf6e087ac61e5e73e3d36d5d28906fd7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="plan")
    def plan(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "plan"))

    @plan.setter
    def plan(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aaae0df4ce6f9b86602301afc165377558c6979c9d648f5b3b8a28f1427c34e3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__45778f8cc87e5d7b6f2d7c690dc5f0615c03f6d3acfd1258fa752f26e3f8740b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__80445b2497f5053a7db532b13cb213b977109e6177a17548b462ef2c9231be75)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terminationProtection", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @title.setter
    def title(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__579f921500d29592dd476a83479c64100aa52fd4cc27afa5eae53e2740c76556)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "title", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zone")
    def zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zone"))

    @zone.setter
    def zone(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71dbfb4b6bef08098f6a9392298bab540d9d5a48287b7ff1514dbdef9db71b1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zone", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchComponents",
    jsii_struct_bases=[],
    name_mapping={},
)
class ManagedDatabaseOpensearchComponents:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchComponents(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchComponentsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchComponentsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__05e0104604c6d119c33be2ffc1295050857aba0fbf9013e5d6022408797e700e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ManagedDatabaseOpensearchComponentsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3df9409d3f44676e26c2ca792935f6fef5261571686ce099b21079ee9cbf626c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ManagedDatabaseOpensearchComponentsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1797fa76f17542a4461981c77c1febde7b7dc7ffbd53ddc05cf07be29a5ae4c8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6c439c2c67d2cf65e96be6f9aae6aed6b527fa71224a5e82d9bfb478b705b43d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__90f578c3b7e470de9a79795d445280c0213bf84b88b837792ae7c769b5a24be2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class ManagedDatabaseOpensearchComponentsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchComponentsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a85bd4824a9de6b259bc7ccba33f22669db6f14724268fea2997edfec3db5c36)
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
    def internal_value(self) -> typing.Optional[ManagedDatabaseOpensearchComponents]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchComponents], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchComponents],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3927b44417f2561e30157a8e7bbae613a717e7583e7952dae4442c4727ed67b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchConfig",
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
        "access_control": "accessControl",
        "extended_access_control": "extendedAccessControl",
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
class ManagedDatabaseOpensearchConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        access_control: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        extended_access_control: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        maintenance_window_dow: typing.Optional[builtins.str] = None,
        maintenance_window_time: typing.Optional[builtins.str] = None,
        network: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedDatabaseOpensearchNetwork", typing.Dict[builtins.str, typing.Any]]]]] = None,
        powered: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        properties: typing.Optional[typing.Union["ManagedDatabaseOpensearchProperties", typing.Dict[builtins.str, typing.Any]]] = None,
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
        :param name: Name of the service. The name is used as a prefix for the logical hostname. Must be unique within an account Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#name ManagedDatabaseOpensearch#name}
        :param plan: Service plan to use. This determines how much resources the instance will have. You can list available plans with ``upctl database plans <type>``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#plan ManagedDatabaseOpensearch#plan}
        :param title: Title of a managed database instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#title ManagedDatabaseOpensearch#title}
        :param zone: Zone where the instance resides, e.g. ``de-fra1``. You can list available zones with ``upctl zone list``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#zone ManagedDatabaseOpensearch#zone}
        :param access_control: Enables users access control for OpenSearch service. User access control rules will only be enforced if this attribute is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#access_control ManagedDatabaseOpensearch#access_control}
        :param extended_access_control: Grant access to top-level ``_mget``, ``_msearch`` and ``_bulk`` APIs. Users are limited to perform operations on indices based on the user-specific access control rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#extended_access_control ManagedDatabaseOpensearch#extended_access_control}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#id ManagedDatabaseOpensearch#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param labels: User defined key-value pairs to classify the managed database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#labels ManagedDatabaseOpensearch#labels}
        :param maintenance_window_dow: Maintenance window day of week. Lower case weekday name (monday, tuesday, ...). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#maintenance_window_dow ManagedDatabaseOpensearch#maintenance_window_dow}
        :param maintenance_window_time: Maintenance window UTC time in hh:mm:ss format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#maintenance_window_time ManagedDatabaseOpensearch#maintenance_window_time}
        :param network: network block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#network ManagedDatabaseOpensearch#network}
        :param powered: The administrative power state of the service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#powered ManagedDatabaseOpensearch#powered}
        :param properties: properties block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#properties ManagedDatabaseOpensearch#properties}
        :param termination_protection: If set to true, prevents the managed service from being powered off, or deleted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#termination_protection ManagedDatabaseOpensearch#termination_protection}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(properties, dict):
            properties = ManagedDatabaseOpensearchProperties(**properties)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5005f5a996eb4e5ca1f0d2c27e74393a05028526f22e88c6ac2dc4e0b094b28)
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
            check_type(argname="argument access_control", value=access_control, expected_type=type_hints["access_control"])
            check_type(argname="argument extended_access_control", value=extended_access_control, expected_type=type_hints["extended_access_control"])
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
        if access_control is not None:
            self._values["access_control"] = access_control
        if extended_access_control is not None:
            self._values["extended_access_control"] = extended_access_control
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#name ManagedDatabaseOpensearch#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def plan(self) -> builtins.str:
        '''Service plan to use.

        This determines how much resources the instance will have. You can list available plans with ``upctl database plans <type>``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#plan ManagedDatabaseOpensearch#plan}
        '''
        result = self._values.get("plan")
        assert result is not None, "Required property 'plan' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''Title of a managed database instance.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#title ManagedDatabaseOpensearch#title}
        '''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def zone(self) -> builtins.str:
        '''Zone where the instance resides, e.g. ``de-fra1``. You can list available zones with ``upctl zone list``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#zone ManagedDatabaseOpensearch#zone}
        '''
        result = self._values.get("zone")
        assert result is not None, "Required property 'zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_control(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enables users access control for OpenSearch service.

        User access control rules will only be enforced if this attribute is enabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#access_control ManagedDatabaseOpensearch#access_control}
        '''
        result = self._values.get("access_control")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def extended_access_control(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Grant access to top-level ``_mget``, ``_msearch`` and ``_bulk`` APIs.

        Users are limited to perform operations on indices based on the user-specific access control rules.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#extended_access_control ManagedDatabaseOpensearch#extended_access_control}
        '''
        result = self._values.get("extended_access_control")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#id ManagedDatabaseOpensearch#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''User defined key-value pairs to classify the managed database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#labels ManagedDatabaseOpensearch#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def maintenance_window_dow(self) -> typing.Optional[builtins.str]:
        '''Maintenance window day of week. Lower case weekday name (monday, tuesday, ...).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#maintenance_window_dow ManagedDatabaseOpensearch#maintenance_window_dow}
        '''
        result = self._values.get("maintenance_window_dow")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maintenance_window_time(self) -> typing.Optional[builtins.str]:
        '''Maintenance window UTC time in hh:mm:ss format.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#maintenance_window_time ManagedDatabaseOpensearch#maintenance_window_time}
        '''
        result = self._values.get("maintenance_window_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedDatabaseOpensearchNetwork"]]]:
        '''network block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#network ManagedDatabaseOpensearch#network}
        '''
        result = self._values.get("network")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedDatabaseOpensearchNetwork"]]], result)

    @builtins.property
    def powered(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''The administrative power state of the service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#powered ManagedDatabaseOpensearch#powered}
        '''
        result = self._values.get("powered")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def properties(self) -> typing.Optional["ManagedDatabaseOpensearchProperties"]:
        '''properties block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#properties ManagedDatabaseOpensearch#properties}
        '''
        result = self._values.get("properties")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchProperties"], result)

    @builtins.property
    def termination_protection(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set to true, prevents the managed service from being powered off, or deleted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#termination_protection ManagedDatabaseOpensearch#termination_protection}
        '''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchNetwork",
    jsii_struct_bases=[],
    name_mapping={"family": "family", "name": "name", "type": "type", "uuid": "uuid"},
)
class ManagedDatabaseOpensearchNetwork:
    def __init__(
        self,
        *,
        family: builtins.str,
        name: builtins.str,
        type: builtins.str,
        uuid: builtins.str,
    ) -> None:
        '''
        :param family: Network family. Currently only ``IPv4`` is supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#family ManagedDatabaseOpensearch#family}
        :param name: The name of the network. Must be unique within the service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#name ManagedDatabaseOpensearch#name}
        :param type: The type of the network. Must be private. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#type ManagedDatabaseOpensearch#type}
        :param uuid: Private network UUID. Must reside in the same zone as the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#uuid ManagedDatabaseOpensearch#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fca8408590124dd06a9281b50a661dcbdbb53334fd0cbfb3b4fed6c54dc2fd83)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#family ManagedDatabaseOpensearch#family}
        '''
        result = self._values.get("family")
        assert result is not None, "Required property 'family' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the network. Must be unique within the service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#name ManagedDatabaseOpensearch#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''The type of the network. Must be private.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#type ManagedDatabaseOpensearch#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def uuid(self) -> builtins.str:
        '''Private network UUID. Must reside in the same zone as the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#uuid ManagedDatabaseOpensearch#uuid}
        '''
        result = self._values.get("uuid")
        assert result is not None, "Required property 'uuid' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchNetwork(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchNetworkList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchNetworkList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e329b18badd7d49b48b57bfe67898d0a24d2355460b3e92344a172ad07ecd4f0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ManagedDatabaseOpensearchNetworkOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32720d726b88051a33b0a45fd56ea4118a2f932301f8c2b2a1d84423707660d7)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ManagedDatabaseOpensearchNetworkOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48f41e22d45dd70224aad1ec2381618b7683e3b9cbc00c500cdc37da46e33fbf)
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
            type_hints = typing.get_type_hints(_typecheckingstub__517c0a72cf55cce1ae9b6342f33106b189fcd6dc12b3fb06aece1db1c9deae0b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2429cd8dff761f1e319900b52e924676682282f94ad7505ba9fe22ee0013cf20)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedDatabaseOpensearchNetwork]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedDatabaseOpensearchNetwork]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedDatabaseOpensearchNetwork]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7988b51be371d4764a089b96fd2c9e8d7deb564eb6a899f5837744f8aa64b302)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ManagedDatabaseOpensearchNetworkOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchNetworkOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__14f5527b348fe4ce85b3f81d752ce7962795f510497f946d3c9fa3d824f60542)
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
            type_hints = typing.get_type_hints(_typecheckingstub__caf0f3fab78ca354752f87686c4ceb87c0908570faaf71c9732bf3b9af492e9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "family", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f552807981014b5ed36ce91c9049ddd1640edc60f00b525be36ade219e1114fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38e73f2b43516cb1cd2e49b889369e26357e42dba138c5c96b56d7155745209e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ae4a80d42aa53b63a4e5515fe09be52313dfd3d7869eb5dfcb8797bdfedaa35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedDatabaseOpensearchNetwork]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedDatabaseOpensearchNetwork]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedDatabaseOpensearchNetwork]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e17b8944baa901c2ed823dd7faa74dbd4e7cdddd833b000fe7f421fb4ee6b6a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchNodeStates",
    jsii_struct_bases=[],
    name_mapping={},
)
class ManagedDatabaseOpensearchNodeStates:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchNodeStates(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchNodeStatesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchNodeStatesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6dabf973c57f1eeb683ec41bdb082376b0d3560469ba973ef9241b6d0f7caa7f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ManagedDatabaseOpensearchNodeStatesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b36091a7798a7e3cf1e20b74cd929271ac53667c3eb0dffd8c1e02230d698148)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ManagedDatabaseOpensearchNodeStatesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d821842074c66d72233fdba46b159048348bfd6348d4a84352047819b9397ed0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__721b09f1dbc677bfbbdf1acb348a60d81f02d69bddbfc5ea3dc0507161c8745e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__732002e48eb319c6455b5f536a3f908279777ddbb6aca495c13f3c337f205389)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class ManagedDatabaseOpensearchNodeStatesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchNodeStatesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__230770a22010afacb40ca84242cbcaf8dc73a365b4513ab7b9b99d283bd1184c)
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
    def internal_value(self) -> typing.Optional[ManagedDatabaseOpensearchNodeStates]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchNodeStates], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchNodeStates],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0f38cb62584f08fe2a0d73b2d546e0165c39f2136e81c6846a602f1affb622c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchProperties",
    jsii_struct_bases=[],
    name_mapping={
        "action_auto_create_index_enabled": "actionAutoCreateIndexEnabled",
        "action_destructive_requires_name": "actionDestructiveRequiresName",
        "auth_failure_listeners": "authFailureListeners",
        "automatic_utility_network_ip_filter": "automaticUtilityNetworkIpFilter",
        "cluster_filecache_remote_data_ratio": "clusterFilecacheRemoteDataRatio",
        "cluster_max_shards_per_node": "clusterMaxShardsPerNode",
        "cluster_remote_store": "clusterRemoteStore",
        "cluster_routing_allocation_balance_prefer_primary": "clusterRoutingAllocationBalancePreferPrimary",
        "cluster_routing_allocation_node_concurrent_recoveries": "clusterRoutingAllocationNodeConcurrentRecoveries",
        "cluster_search_request_slowlog": "clusterSearchRequestSlowlog",
        "custom_domain": "customDomain",
        "disk_watermarks": "diskWatermarks",
        "elasticsearch_version": "elasticsearchVersion",
        "email_sender_name": "emailSenderName",
        "email_sender_password": "emailSenderPassword",
        "email_sender_username": "emailSenderUsername",
        "enable_remote_backed_storage": "enableRemoteBackedStorage",
        "enable_searchable_snapshots": "enableSearchableSnapshots",
        "enable_security_audit": "enableSecurityAudit",
        "enable_snapshot_api": "enableSnapshotApi",
        "http_max_content_length": "httpMaxContentLength",
        "http_max_header_size": "httpMaxHeaderSize",
        "http_max_initial_line_length": "httpMaxInitialLineLength",
        "index_patterns": "indexPatterns",
        "index_rollup": "indexRollup",
        "index_template": "indexTemplate",
        "indices_fielddata_cache_size": "indicesFielddataCacheSize",
        "indices_memory_index_buffer_size": "indicesMemoryIndexBufferSize",
        "indices_memory_max_index_buffer_size": "indicesMemoryMaxIndexBufferSize",
        "indices_memory_min_index_buffer_size": "indicesMemoryMinIndexBufferSize",
        "indices_queries_cache_size": "indicesQueriesCacheSize",
        "indices_query_bool_max_clause_count": "indicesQueryBoolMaxClauseCount",
        "indices_recovery_max_bytes_per_sec": "indicesRecoveryMaxBytesPerSec",
        "indices_recovery_max_concurrent_file_chunks": "indicesRecoveryMaxConcurrentFileChunks",
        "ip_filter": "ipFilter",
        "ism_enabled": "ismEnabled",
        "ism_history_enabled": "ismHistoryEnabled",
        "ism_history_max_age": "ismHistoryMaxAge",
        "ism_history_max_docs": "ismHistoryMaxDocs",
        "ism_history_rollover_check_period": "ismHistoryRolloverCheckPeriod",
        "ism_history_rollover_retention_period": "ismHistoryRolloverRetentionPeriod",
        "keep_index_refresh_interval": "keepIndexRefreshInterval",
        "knn_memory_circuit_breaker_enabled": "knnMemoryCircuitBreakerEnabled",
        "knn_memory_circuit_breaker_limit": "knnMemoryCircuitBreakerLimit",
        "node_search_cache_size": "nodeSearchCacheSize",
        "openid": "openid",
        "opensearch_dashboards": "opensearchDashboards",
        "override_main_response_version": "overrideMainResponseVersion",
        "plugins_alerting_filter_by_backend_roles": "pluginsAlertingFilterByBackendRoles",
        "public_access": "publicAccess",
        "reindex_remote_whitelist": "reindexRemoteWhitelist",
        "remote_store": "remoteStore",
        "saml": "saml",
        "script_max_compilations_rate": "scriptMaxCompilationsRate",
        "search_backpressure": "searchBackpressure",
        "search_insights_top_queries": "searchInsightsTopQueries",
        "search_max_buckets": "searchMaxBuckets",
        "segrep": "segrep",
        "service_log": "serviceLog",
        "shard_indexing_pressure": "shardIndexingPressure",
        "thread_pool_analyze_queue_size": "threadPoolAnalyzeQueueSize",
        "thread_pool_analyze_size": "threadPoolAnalyzeSize",
        "thread_pool_force_merge_size": "threadPoolForceMergeSize",
        "thread_pool_get_queue_size": "threadPoolGetQueueSize",
        "thread_pool_get_size": "threadPoolGetSize",
        "thread_pool_search_queue_size": "threadPoolSearchQueueSize",
        "thread_pool_search_size": "threadPoolSearchSize",
        "thread_pool_search_throttled_queue_size": "threadPoolSearchThrottledQueueSize",
        "thread_pool_search_throttled_size": "threadPoolSearchThrottledSize",
        "thread_pool_write_queue_size": "threadPoolWriteQueueSize",
        "thread_pool_write_size": "threadPoolWriteSize",
        "version": "version",
    },
)
class ManagedDatabaseOpensearchProperties:
    def __init__(
        self,
        *,
        action_auto_create_index_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        action_destructive_requires_name: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auth_failure_listeners: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesAuthFailureListeners", typing.Dict[builtins.str, typing.Any]]] = None,
        automatic_utility_network_ip_filter: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cluster_filecache_remote_data_ratio: typing.Optional[jsii.Number] = None,
        cluster_max_shards_per_node: typing.Optional[jsii.Number] = None,
        cluster_remote_store: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesClusterRemoteStore", typing.Dict[builtins.str, typing.Any]]] = None,
        cluster_routing_allocation_balance_prefer_primary: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cluster_routing_allocation_node_concurrent_recoveries: typing.Optional[jsii.Number] = None,
        cluster_search_request_slowlog: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlog", typing.Dict[builtins.str, typing.Any]]] = None,
        custom_domain: typing.Optional[builtins.str] = None,
        disk_watermarks: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesDiskWatermarks", typing.Dict[builtins.str, typing.Any]]] = None,
        elasticsearch_version: typing.Optional[builtins.str] = None,
        email_sender_name: typing.Optional[builtins.str] = None,
        email_sender_password: typing.Optional[builtins.str] = None,
        email_sender_username: typing.Optional[builtins.str] = None,
        enable_remote_backed_storage: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_searchable_snapshots: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_security_audit: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_snapshot_api: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        http_max_content_length: typing.Optional[jsii.Number] = None,
        http_max_header_size: typing.Optional[jsii.Number] = None,
        http_max_initial_line_length: typing.Optional[jsii.Number] = None,
        index_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
        index_rollup: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesIndexRollup", typing.Dict[builtins.str, typing.Any]]] = None,
        index_template: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesIndexTemplate", typing.Dict[builtins.str, typing.Any]]] = None,
        indices_fielddata_cache_size: typing.Optional[jsii.Number] = None,
        indices_memory_index_buffer_size: typing.Optional[jsii.Number] = None,
        indices_memory_max_index_buffer_size: typing.Optional[jsii.Number] = None,
        indices_memory_min_index_buffer_size: typing.Optional[jsii.Number] = None,
        indices_queries_cache_size: typing.Optional[jsii.Number] = None,
        indices_query_bool_max_clause_count: typing.Optional[jsii.Number] = None,
        indices_recovery_max_bytes_per_sec: typing.Optional[jsii.Number] = None,
        indices_recovery_max_concurrent_file_chunks: typing.Optional[jsii.Number] = None,
        ip_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
        ism_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ism_history_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ism_history_max_age: typing.Optional[jsii.Number] = None,
        ism_history_max_docs: typing.Optional[jsii.Number] = None,
        ism_history_rollover_check_period: typing.Optional[jsii.Number] = None,
        ism_history_rollover_retention_period: typing.Optional[jsii.Number] = None,
        keep_index_refresh_interval: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        knn_memory_circuit_breaker_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        knn_memory_circuit_breaker_limit: typing.Optional[jsii.Number] = None,
        node_search_cache_size: typing.Optional[builtins.str] = None,
        openid: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesOpenid", typing.Dict[builtins.str, typing.Any]]] = None,
        opensearch_dashboards: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesOpensearchDashboards", typing.Dict[builtins.str, typing.Any]]] = None,
        override_main_response_version: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        plugins_alerting_filter_by_backend_roles: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        public_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        reindex_remote_whitelist: typing.Optional[typing.Sequence[builtins.str]] = None,
        remote_store: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesRemoteStore", typing.Dict[builtins.str, typing.Any]]] = None,
        saml: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesSaml", typing.Dict[builtins.str, typing.Any]]] = None,
        script_max_compilations_rate: typing.Optional[builtins.str] = None,
        search_backpressure: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesSearchBackpressure", typing.Dict[builtins.str, typing.Any]]] = None,
        search_insights_top_queries: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueries", typing.Dict[builtins.str, typing.Any]]] = None,
        search_max_buckets: typing.Optional[jsii.Number] = None,
        segrep: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesSegrep", typing.Dict[builtins.str, typing.Any]]] = None,
        service_log: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        shard_indexing_pressure: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesShardIndexingPressure", typing.Dict[builtins.str, typing.Any]]] = None,
        thread_pool_analyze_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_analyze_size: typing.Optional[jsii.Number] = None,
        thread_pool_force_merge_size: typing.Optional[jsii.Number] = None,
        thread_pool_get_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_get_size: typing.Optional[jsii.Number] = None,
        thread_pool_search_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_search_size: typing.Optional[jsii.Number] = None,
        thread_pool_search_throttled_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_search_throttled_size: typing.Optional[jsii.Number] = None,
        thread_pool_write_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_write_size: typing.Optional[jsii.Number] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param action_auto_create_index_enabled: action.auto_create_index. Explicitly allow or block automatic creation of indices. Defaults to true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#action_auto_create_index_enabled ManagedDatabaseOpensearch#action_auto_create_index_enabled}
        :param action_destructive_requires_name: Require explicit index names when deleting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#action_destructive_requires_name ManagedDatabaseOpensearch#action_destructive_requires_name}
        :param auth_failure_listeners: auth_failure_listeners block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#auth_failure_listeners ManagedDatabaseOpensearch#auth_failure_listeners}
        :param automatic_utility_network_ip_filter: Automatic utility network IP Filter. Automatically allow connections from servers in the utility network within the same zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#automatic_utility_network_ip_filter ManagedDatabaseOpensearch#automatic_utility_network_ip_filter}
        :param cluster_filecache_remote_data_ratio: The limit of how much total remote data can be referenced. Defines a limit of how much total remote data can be referenced as a ratio of the size of the disk reserved for the file cache. This is designed to be a safeguard to prevent oversubscribing a cluster. Defaults to 0. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cluster_filecache_remote_data_ratio ManagedDatabaseOpensearch#cluster_filecache_remote_data_ratio}
        :param cluster_max_shards_per_node: Controls the number of shards allowed in the cluster per data node. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cluster_max_shards_per_node ManagedDatabaseOpensearch#cluster_max_shards_per_node}
        :param cluster_remote_store: cluster_remote_store block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cluster_remote_store ManagedDatabaseOpensearch#cluster_remote_store}
        :param cluster_routing_allocation_balance_prefer_primary: When set to true, OpenSearch attempts to evenly distribute the primary shards between the cluster nodes. Enabling this setting does not always guarantee an equal number of primary shards on each node, especially in the event of a failover. Changing this setting to false after it was set to true does not invoke redistribution of primary shards. Default is false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cluster_routing_allocation_balance_prefer_primary ManagedDatabaseOpensearch#cluster_routing_allocation_balance_prefer_primary}
        :param cluster_routing_allocation_node_concurrent_recoveries: Concurrent incoming/outgoing shard recoveries per node. How many concurrent incoming/outgoing shard recoveries (normally replicas) are allowed to happen on a node. Defaults to node cpu count * 2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cluster_routing_allocation_node_concurrent_recoveries ManagedDatabaseOpensearch#cluster_routing_allocation_node_concurrent_recoveries}
        :param cluster_search_request_slowlog: cluster_search_request_slowlog block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cluster_search_request_slowlog ManagedDatabaseOpensearch#cluster_search_request_slowlog}
        :param custom_domain: Custom domain. Serve the web frontend using a custom CNAME pointing to the Aiven DNS name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#custom_domain ManagedDatabaseOpensearch#custom_domain}
        :param disk_watermarks: disk_watermarks block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#disk_watermarks ManagedDatabaseOpensearch#disk_watermarks}
        :param elasticsearch_version: Elasticsearch major version. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#elasticsearch_version ManagedDatabaseOpensearch#elasticsearch_version}
        :param email_sender_name: Sender name placeholder to be used in Opensearch Dashboards and Opensearch keystore. This should be identical to the Sender name defined in Opensearch dashboards. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#email_sender_name ManagedDatabaseOpensearch#email_sender_name}
        :param email_sender_password: Sender password for Opensearch alerts to authenticate with SMTP server. Sender password for Opensearch alerts to authenticate with SMTP server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#email_sender_password ManagedDatabaseOpensearch#email_sender_password}
        :param email_sender_username: Sender username for Opensearch alerts. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#email_sender_username ManagedDatabaseOpensearch#email_sender_username}
        :param enable_remote_backed_storage: Enable remote-backed storage. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enable_remote_backed_storage ManagedDatabaseOpensearch#enable_remote_backed_storage}
        :param enable_searchable_snapshots: Enable searchable snapshots. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enable_searchable_snapshots ManagedDatabaseOpensearch#enable_searchable_snapshots}
        :param enable_security_audit: Enable/Disable security audit. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enable_security_audit ManagedDatabaseOpensearch#enable_security_audit}
        :param enable_snapshot_api: Enable/Disable snapshot API. Enable/Disable snapshot API for custom repositories, this requires security management to be enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enable_snapshot_api ManagedDatabaseOpensearch#enable_snapshot_api}
        :param http_max_content_length: Maximum content length for HTTP requests to the OpenSearch HTTP API, in bytes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#http_max_content_length ManagedDatabaseOpensearch#http_max_content_length}
        :param http_max_header_size: The max size of allowed headers, in bytes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#http_max_header_size ManagedDatabaseOpensearch#http_max_header_size}
        :param http_max_initial_line_length: The max length of an HTTP URL, in bytes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#http_max_initial_line_length ManagedDatabaseOpensearch#http_max_initial_line_length}
        :param index_patterns: Index patterns. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#index_patterns ManagedDatabaseOpensearch#index_patterns}
        :param index_rollup: index_rollup block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#index_rollup ManagedDatabaseOpensearch#index_rollup}
        :param index_template: index_template block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#index_template ManagedDatabaseOpensearch#index_template}
        :param indices_fielddata_cache_size: Relative amount. Maximum amount of heap memory used for field data cache. This is an expert setting; decreasing the value too much will increase overhead of loading field data; too much memory used for field data cache will decrease amount of heap available for other operations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#indices_fielddata_cache_size ManagedDatabaseOpensearch#indices_fielddata_cache_size}
        :param indices_memory_index_buffer_size: Percentage value. Default is 10%. Total amount of heap used for indexing buffer, before writing segments to disk. This is an expert setting. Too low value will slow down indexing; too high value will increase indexing performance but causes performance issues for query performance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#indices_memory_index_buffer_size ManagedDatabaseOpensearch#indices_memory_index_buffer_size}
        :param indices_memory_max_index_buffer_size: Absolute value. Default is unbound. Doesn't work without indices.memory.index_buffer_size. Maximum amount of heap used for query cache, an absolute indices.memory.index_buffer_size maximum hard limit. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#indices_memory_max_index_buffer_size ManagedDatabaseOpensearch#indices_memory_max_index_buffer_size}
        :param indices_memory_min_index_buffer_size: Absolute value. Default is 48mb. Doesn't work without indices.memory.index_buffer_size. Minimum amount of heap used for query cache, an absolute indices.memory.index_buffer_size minimal hard limit. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#indices_memory_min_index_buffer_size ManagedDatabaseOpensearch#indices_memory_min_index_buffer_size}
        :param indices_queries_cache_size: Percentage value. Default is 10%. Maximum amount of heap used for query cache. This is an expert setting. Too low value will decrease query performance and increase performance for other operations; too high value will cause issues with other OpenSearch functionality. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#indices_queries_cache_size ManagedDatabaseOpensearch#indices_queries_cache_size}
        :param indices_query_bool_max_clause_count: Maximum number of clauses Lucene BooleanQuery can have. The default value (1024) is relatively high, and increasing it may cause performance issues. Investigate other approaches first before increasing this value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#indices_query_bool_max_clause_count ManagedDatabaseOpensearch#indices_query_bool_max_clause_count}
        :param indices_recovery_max_bytes_per_sec: Limits total inbound and outbound recovery traffic for each node. Applies to both peer recoveries as well as snapshot recoveries (i.e., restores from a snapshot). Defaults to 40mb. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#indices_recovery_max_bytes_per_sec ManagedDatabaseOpensearch#indices_recovery_max_bytes_per_sec}
        :param indices_recovery_max_concurrent_file_chunks: Number of file chunks sent in parallel for each recovery. Defaults to 2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#indices_recovery_max_concurrent_file_chunks ManagedDatabaseOpensearch#indices_recovery_max_concurrent_file_chunks}
        :param ip_filter: IP filter. Allow incoming connections from CIDR address block, e.g. '10.20.0.0/16'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#ip_filter ManagedDatabaseOpensearch#ip_filter}
        :param ism_enabled: Specifies whether ISM is enabled or not. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#ism_enabled ManagedDatabaseOpensearch#ism_enabled}
        :param ism_history_enabled: Specifies whether audit history is enabled or not. The logs from ISM are automatically indexed to a logs document. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#ism_history_enabled ManagedDatabaseOpensearch#ism_history_enabled}
        :param ism_history_max_age: The maximum age before rolling over the audit history index in hours. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#ism_history_max_age ManagedDatabaseOpensearch#ism_history_max_age}
        :param ism_history_max_docs: The maximum number of documents before rolling over the audit history index. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#ism_history_max_docs ManagedDatabaseOpensearch#ism_history_max_docs}
        :param ism_history_rollover_check_period: The time between rollover checks for the audit history index in hours. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#ism_history_rollover_check_period ManagedDatabaseOpensearch#ism_history_rollover_check_period}
        :param ism_history_rollover_retention_period: How long audit history indices are kept in days. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#ism_history_rollover_retention_period ManagedDatabaseOpensearch#ism_history_rollover_retention_period}
        :param keep_index_refresh_interval: Don't reset index.refresh_interval to the default value. Aiven automation resets index.refresh_interval to default value for every index to be sure that indices are always visible to search. If it doesn't fit your case, you can disable this by setting up this flag to true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#keep_index_refresh_interval ManagedDatabaseOpensearch#keep_index_refresh_interval}
        :param knn_memory_circuit_breaker_enabled: Enable or disable KNN memory circuit breaker. Defaults to true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#knn_memory_circuit_breaker_enabled ManagedDatabaseOpensearch#knn_memory_circuit_breaker_enabled}
        :param knn_memory_circuit_breaker_limit: Maximum amount of memory that can be used for KNN index. Defaults to 50% of the JVM heap size. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#knn_memory_circuit_breaker_limit ManagedDatabaseOpensearch#knn_memory_circuit_breaker_limit}
        :param node_search_cache_size: The limit of how much total remote data can be referenced. Defines a limit of how much total remote data can be referenced as a ratio of the size of the disk reserved for the file cache. This is designed to be a safeguard to prevent oversubscribing a cluster. Defaults to 5gb. Requires restarting all OpenSearch nodes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#node_search_cache_size ManagedDatabaseOpensearch#node_search_cache_size}
        :param openid: openid block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#openid ManagedDatabaseOpensearch#openid}
        :param opensearch_dashboards: opensearch_dashboards block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#opensearch_dashboards ManagedDatabaseOpensearch#opensearch_dashboards}
        :param override_main_response_version: Compatibility mode sets OpenSearch to report its version as 7.10 so clients continue to work. Default is false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#override_main_response_version ManagedDatabaseOpensearch#override_main_response_version}
        :param plugins_alerting_filter_by_backend_roles: Enable or disable filtering of alerting by backend roles. Requires Security plugin. Defaults to false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#plugins_alerting_filter_by_backend_roles ManagedDatabaseOpensearch#plugins_alerting_filter_by_backend_roles}
        :param public_access: Public Access. Allow access to the service from the public Internet. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#public_access ManagedDatabaseOpensearch#public_access}
        :param reindex_remote_whitelist: Whitelisted addresses for reindexing. Changing this value will cause all OpenSearch instances to restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#reindex_remote_whitelist ManagedDatabaseOpensearch#reindex_remote_whitelist}
        :param remote_store: remote_store block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#remote_store ManagedDatabaseOpensearch#remote_store}
        :param saml: saml block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#saml ManagedDatabaseOpensearch#saml}
        :param script_max_compilations_rate: Script max compilation rate - circuit breaker to prevent/minimize OOMs. Script compilation circuit breaker limits the number of inline script compilations within a period of time. Default is use-context. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#script_max_compilations_rate ManagedDatabaseOpensearch#script_max_compilations_rate}
        :param search_backpressure: search_backpressure block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#search_backpressure ManagedDatabaseOpensearch#search_backpressure}
        :param search_insights_top_queries: search_insights_top_queries block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#search_insights_top_queries ManagedDatabaseOpensearch#search_insights_top_queries}
        :param search_max_buckets: Maximum number of aggregation buckets allowed in a single response. OpenSearch default value is used when this is not defined. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#search_max_buckets ManagedDatabaseOpensearch#search_max_buckets}
        :param segrep: segrep block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#segrep ManagedDatabaseOpensearch#segrep}
        :param service_log: Service logging. Store logs for the service so that they are available in the HTTP API and console. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#service_log ManagedDatabaseOpensearch#service_log}
        :param shard_indexing_pressure: shard_indexing_pressure block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#shard_indexing_pressure ManagedDatabaseOpensearch#shard_indexing_pressure}
        :param thread_pool_analyze_queue_size: analyze thread pool queue size. Size for the thread pool queue. See documentation for exact details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_analyze_queue_size ManagedDatabaseOpensearch#thread_pool_analyze_queue_size}
        :param thread_pool_analyze_size: analyze thread pool size. Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_analyze_size ManagedDatabaseOpensearch#thread_pool_analyze_size}
        :param thread_pool_force_merge_size: force_merge thread pool size. Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_force_merge_size ManagedDatabaseOpensearch#thread_pool_force_merge_size}
        :param thread_pool_get_queue_size: get thread pool queue size. Size for the thread pool queue. See documentation for exact details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_get_queue_size ManagedDatabaseOpensearch#thread_pool_get_queue_size}
        :param thread_pool_get_size: get thread pool size. Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_get_size ManagedDatabaseOpensearch#thread_pool_get_size}
        :param thread_pool_search_queue_size: search thread pool queue size. Size for the thread pool queue. See documentation for exact details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_search_queue_size ManagedDatabaseOpensearch#thread_pool_search_queue_size}
        :param thread_pool_search_size: search thread pool size. Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_search_size ManagedDatabaseOpensearch#thread_pool_search_size}
        :param thread_pool_search_throttled_queue_size: search_throttled thread pool queue size. Size for the thread pool queue. See documentation for exact details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_search_throttled_queue_size ManagedDatabaseOpensearch#thread_pool_search_throttled_queue_size}
        :param thread_pool_search_throttled_size: search_throttled thread pool size. Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_search_throttled_size ManagedDatabaseOpensearch#thread_pool_search_throttled_size}
        :param thread_pool_write_queue_size: write thread pool queue size. Size for the thread pool queue. See documentation for exact details. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_write_queue_size ManagedDatabaseOpensearch#thread_pool_write_queue_size}
        :param thread_pool_write_size: write thread pool size. Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_write_size ManagedDatabaseOpensearch#thread_pool_write_size}
        :param version: OpenSearch major version. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#version ManagedDatabaseOpensearch#version}
        '''
        if isinstance(auth_failure_listeners, dict):
            auth_failure_listeners = ManagedDatabaseOpensearchPropertiesAuthFailureListeners(**auth_failure_listeners)
        if isinstance(cluster_remote_store, dict):
            cluster_remote_store = ManagedDatabaseOpensearchPropertiesClusterRemoteStore(**cluster_remote_store)
        if isinstance(cluster_search_request_slowlog, dict):
            cluster_search_request_slowlog = ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlog(**cluster_search_request_slowlog)
        if isinstance(disk_watermarks, dict):
            disk_watermarks = ManagedDatabaseOpensearchPropertiesDiskWatermarks(**disk_watermarks)
        if isinstance(index_rollup, dict):
            index_rollup = ManagedDatabaseOpensearchPropertiesIndexRollup(**index_rollup)
        if isinstance(index_template, dict):
            index_template = ManagedDatabaseOpensearchPropertiesIndexTemplate(**index_template)
        if isinstance(openid, dict):
            openid = ManagedDatabaseOpensearchPropertiesOpenid(**openid)
        if isinstance(opensearch_dashboards, dict):
            opensearch_dashboards = ManagedDatabaseOpensearchPropertiesOpensearchDashboards(**opensearch_dashboards)
        if isinstance(remote_store, dict):
            remote_store = ManagedDatabaseOpensearchPropertiesRemoteStore(**remote_store)
        if isinstance(saml, dict):
            saml = ManagedDatabaseOpensearchPropertiesSaml(**saml)
        if isinstance(search_backpressure, dict):
            search_backpressure = ManagedDatabaseOpensearchPropertiesSearchBackpressure(**search_backpressure)
        if isinstance(search_insights_top_queries, dict):
            search_insights_top_queries = ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueries(**search_insights_top_queries)
        if isinstance(segrep, dict):
            segrep = ManagedDatabaseOpensearchPropertiesSegrep(**segrep)
        if isinstance(shard_indexing_pressure, dict):
            shard_indexing_pressure = ManagedDatabaseOpensearchPropertiesShardIndexingPressure(**shard_indexing_pressure)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de14c8022684ac9416f06b1fd8069683ff6f1b4d90f2879d52bb0843d4b3353d)
            check_type(argname="argument action_auto_create_index_enabled", value=action_auto_create_index_enabled, expected_type=type_hints["action_auto_create_index_enabled"])
            check_type(argname="argument action_destructive_requires_name", value=action_destructive_requires_name, expected_type=type_hints["action_destructive_requires_name"])
            check_type(argname="argument auth_failure_listeners", value=auth_failure_listeners, expected_type=type_hints["auth_failure_listeners"])
            check_type(argname="argument automatic_utility_network_ip_filter", value=automatic_utility_network_ip_filter, expected_type=type_hints["automatic_utility_network_ip_filter"])
            check_type(argname="argument cluster_filecache_remote_data_ratio", value=cluster_filecache_remote_data_ratio, expected_type=type_hints["cluster_filecache_remote_data_ratio"])
            check_type(argname="argument cluster_max_shards_per_node", value=cluster_max_shards_per_node, expected_type=type_hints["cluster_max_shards_per_node"])
            check_type(argname="argument cluster_remote_store", value=cluster_remote_store, expected_type=type_hints["cluster_remote_store"])
            check_type(argname="argument cluster_routing_allocation_balance_prefer_primary", value=cluster_routing_allocation_balance_prefer_primary, expected_type=type_hints["cluster_routing_allocation_balance_prefer_primary"])
            check_type(argname="argument cluster_routing_allocation_node_concurrent_recoveries", value=cluster_routing_allocation_node_concurrent_recoveries, expected_type=type_hints["cluster_routing_allocation_node_concurrent_recoveries"])
            check_type(argname="argument cluster_search_request_slowlog", value=cluster_search_request_slowlog, expected_type=type_hints["cluster_search_request_slowlog"])
            check_type(argname="argument custom_domain", value=custom_domain, expected_type=type_hints["custom_domain"])
            check_type(argname="argument disk_watermarks", value=disk_watermarks, expected_type=type_hints["disk_watermarks"])
            check_type(argname="argument elasticsearch_version", value=elasticsearch_version, expected_type=type_hints["elasticsearch_version"])
            check_type(argname="argument email_sender_name", value=email_sender_name, expected_type=type_hints["email_sender_name"])
            check_type(argname="argument email_sender_password", value=email_sender_password, expected_type=type_hints["email_sender_password"])
            check_type(argname="argument email_sender_username", value=email_sender_username, expected_type=type_hints["email_sender_username"])
            check_type(argname="argument enable_remote_backed_storage", value=enable_remote_backed_storage, expected_type=type_hints["enable_remote_backed_storage"])
            check_type(argname="argument enable_searchable_snapshots", value=enable_searchable_snapshots, expected_type=type_hints["enable_searchable_snapshots"])
            check_type(argname="argument enable_security_audit", value=enable_security_audit, expected_type=type_hints["enable_security_audit"])
            check_type(argname="argument enable_snapshot_api", value=enable_snapshot_api, expected_type=type_hints["enable_snapshot_api"])
            check_type(argname="argument http_max_content_length", value=http_max_content_length, expected_type=type_hints["http_max_content_length"])
            check_type(argname="argument http_max_header_size", value=http_max_header_size, expected_type=type_hints["http_max_header_size"])
            check_type(argname="argument http_max_initial_line_length", value=http_max_initial_line_length, expected_type=type_hints["http_max_initial_line_length"])
            check_type(argname="argument index_patterns", value=index_patterns, expected_type=type_hints["index_patterns"])
            check_type(argname="argument index_rollup", value=index_rollup, expected_type=type_hints["index_rollup"])
            check_type(argname="argument index_template", value=index_template, expected_type=type_hints["index_template"])
            check_type(argname="argument indices_fielddata_cache_size", value=indices_fielddata_cache_size, expected_type=type_hints["indices_fielddata_cache_size"])
            check_type(argname="argument indices_memory_index_buffer_size", value=indices_memory_index_buffer_size, expected_type=type_hints["indices_memory_index_buffer_size"])
            check_type(argname="argument indices_memory_max_index_buffer_size", value=indices_memory_max_index_buffer_size, expected_type=type_hints["indices_memory_max_index_buffer_size"])
            check_type(argname="argument indices_memory_min_index_buffer_size", value=indices_memory_min_index_buffer_size, expected_type=type_hints["indices_memory_min_index_buffer_size"])
            check_type(argname="argument indices_queries_cache_size", value=indices_queries_cache_size, expected_type=type_hints["indices_queries_cache_size"])
            check_type(argname="argument indices_query_bool_max_clause_count", value=indices_query_bool_max_clause_count, expected_type=type_hints["indices_query_bool_max_clause_count"])
            check_type(argname="argument indices_recovery_max_bytes_per_sec", value=indices_recovery_max_bytes_per_sec, expected_type=type_hints["indices_recovery_max_bytes_per_sec"])
            check_type(argname="argument indices_recovery_max_concurrent_file_chunks", value=indices_recovery_max_concurrent_file_chunks, expected_type=type_hints["indices_recovery_max_concurrent_file_chunks"])
            check_type(argname="argument ip_filter", value=ip_filter, expected_type=type_hints["ip_filter"])
            check_type(argname="argument ism_enabled", value=ism_enabled, expected_type=type_hints["ism_enabled"])
            check_type(argname="argument ism_history_enabled", value=ism_history_enabled, expected_type=type_hints["ism_history_enabled"])
            check_type(argname="argument ism_history_max_age", value=ism_history_max_age, expected_type=type_hints["ism_history_max_age"])
            check_type(argname="argument ism_history_max_docs", value=ism_history_max_docs, expected_type=type_hints["ism_history_max_docs"])
            check_type(argname="argument ism_history_rollover_check_period", value=ism_history_rollover_check_period, expected_type=type_hints["ism_history_rollover_check_period"])
            check_type(argname="argument ism_history_rollover_retention_period", value=ism_history_rollover_retention_period, expected_type=type_hints["ism_history_rollover_retention_period"])
            check_type(argname="argument keep_index_refresh_interval", value=keep_index_refresh_interval, expected_type=type_hints["keep_index_refresh_interval"])
            check_type(argname="argument knn_memory_circuit_breaker_enabled", value=knn_memory_circuit_breaker_enabled, expected_type=type_hints["knn_memory_circuit_breaker_enabled"])
            check_type(argname="argument knn_memory_circuit_breaker_limit", value=knn_memory_circuit_breaker_limit, expected_type=type_hints["knn_memory_circuit_breaker_limit"])
            check_type(argname="argument node_search_cache_size", value=node_search_cache_size, expected_type=type_hints["node_search_cache_size"])
            check_type(argname="argument openid", value=openid, expected_type=type_hints["openid"])
            check_type(argname="argument opensearch_dashboards", value=opensearch_dashboards, expected_type=type_hints["opensearch_dashboards"])
            check_type(argname="argument override_main_response_version", value=override_main_response_version, expected_type=type_hints["override_main_response_version"])
            check_type(argname="argument plugins_alerting_filter_by_backend_roles", value=plugins_alerting_filter_by_backend_roles, expected_type=type_hints["plugins_alerting_filter_by_backend_roles"])
            check_type(argname="argument public_access", value=public_access, expected_type=type_hints["public_access"])
            check_type(argname="argument reindex_remote_whitelist", value=reindex_remote_whitelist, expected_type=type_hints["reindex_remote_whitelist"])
            check_type(argname="argument remote_store", value=remote_store, expected_type=type_hints["remote_store"])
            check_type(argname="argument saml", value=saml, expected_type=type_hints["saml"])
            check_type(argname="argument script_max_compilations_rate", value=script_max_compilations_rate, expected_type=type_hints["script_max_compilations_rate"])
            check_type(argname="argument search_backpressure", value=search_backpressure, expected_type=type_hints["search_backpressure"])
            check_type(argname="argument search_insights_top_queries", value=search_insights_top_queries, expected_type=type_hints["search_insights_top_queries"])
            check_type(argname="argument search_max_buckets", value=search_max_buckets, expected_type=type_hints["search_max_buckets"])
            check_type(argname="argument segrep", value=segrep, expected_type=type_hints["segrep"])
            check_type(argname="argument service_log", value=service_log, expected_type=type_hints["service_log"])
            check_type(argname="argument shard_indexing_pressure", value=shard_indexing_pressure, expected_type=type_hints["shard_indexing_pressure"])
            check_type(argname="argument thread_pool_analyze_queue_size", value=thread_pool_analyze_queue_size, expected_type=type_hints["thread_pool_analyze_queue_size"])
            check_type(argname="argument thread_pool_analyze_size", value=thread_pool_analyze_size, expected_type=type_hints["thread_pool_analyze_size"])
            check_type(argname="argument thread_pool_force_merge_size", value=thread_pool_force_merge_size, expected_type=type_hints["thread_pool_force_merge_size"])
            check_type(argname="argument thread_pool_get_queue_size", value=thread_pool_get_queue_size, expected_type=type_hints["thread_pool_get_queue_size"])
            check_type(argname="argument thread_pool_get_size", value=thread_pool_get_size, expected_type=type_hints["thread_pool_get_size"])
            check_type(argname="argument thread_pool_search_queue_size", value=thread_pool_search_queue_size, expected_type=type_hints["thread_pool_search_queue_size"])
            check_type(argname="argument thread_pool_search_size", value=thread_pool_search_size, expected_type=type_hints["thread_pool_search_size"])
            check_type(argname="argument thread_pool_search_throttled_queue_size", value=thread_pool_search_throttled_queue_size, expected_type=type_hints["thread_pool_search_throttled_queue_size"])
            check_type(argname="argument thread_pool_search_throttled_size", value=thread_pool_search_throttled_size, expected_type=type_hints["thread_pool_search_throttled_size"])
            check_type(argname="argument thread_pool_write_queue_size", value=thread_pool_write_queue_size, expected_type=type_hints["thread_pool_write_queue_size"])
            check_type(argname="argument thread_pool_write_size", value=thread_pool_write_size, expected_type=type_hints["thread_pool_write_size"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if action_auto_create_index_enabled is not None:
            self._values["action_auto_create_index_enabled"] = action_auto_create_index_enabled
        if action_destructive_requires_name is not None:
            self._values["action_destructive_requires_name"] = action_destructive_requires_name
        if auth_failure_listeners is not None:
            self._values["auth_failure_listeners"] = auth_failure_listeners
        if automatic_utility_network_ip_filter is not None:
            self._values["automatic_utility_network_ip_filter"] = automatic_utility_network_ip_filter
        if cluster_filecache_remote_data_ratio is not None:
            self._values["cluster_filecache_remote_data_ratio"] = cluster_filecache_remote_data_ratio
        if cluster_max_shards_per_node is not None:
            self._values["cluster_max_shards_per_node"] = cluster_max_shards_per_node
        if cluster_remote_store is not None:
            self._values["cluster_remote_store"] = cluster_remote_store
        if cluster_routing_allocation_balance_prefer_primary is not None:
            self._values["cluster_routing_allocation_balance_prefer_primary"] = cluster_routing_allocation_balance_prefer_primary
        if cluster_routing_allocation_node_concurrent_recoveries is not None:
            self._values["cluster_routing_allocation_node_concurrent_recoveries"] = cluster_routing_allocation_node_concurrent_recoveries
        if cluster_search_request_slowlog is not None:
            self._values["cluster_search_request_slowlog"] = cluster_search_request_slowlog
        if custom_domain is not None:
            self._values["custom_domain"] = custom_domain
        if disk_watermarks is not None:
            self._values["disk_watermarks"] = disk_watermarks
        if elasticsearch_version is not None:
            self._values["elasticsearch_version"] = elasticsearch_version
        if email_sender_name is not None:
            self._values["email_sender_name"] = email_sender_name
        if email_sender_password is not None:
            self._values["email_sender_password"] = email_sender_password
        if email_sender_username is not None:
            self._values["email_sender_username"] = email_sender_username
        if enable_remote_backed_storage is not None:
            self._values["enable_remote_backed_storage"] = enable_remote_backed_storage
        if enable_searchable_snapshots is not None:
            self._values["enable_searchable_snapshots"] = enable_searchable_snapshots
        if enable_security_audit is not None:
            self._values["enable_security_audit"] = enable_security_audit
        if enable_snapshot_api is not None:
            self._values["enable_snapshot_api"] = enable_snapshot_api
        if http_max_content_length is not None:
            self._values["http_max_content_length"] = http_max_content_length
        if http_max_header_size is not None:
            self._values["http_max_header_size"] = http_max_header_size
        if http_max_initial_line_length is not None:
            self._values["http_max_initial_line_length"] = http_max_initial_line_length
        if index_patterns is not None:
            self._values["index_patterns"] = index_patterns
        if index_rollup is not None:
            self._values["index_rollup"] = index_rollup
        if index_template is not None:
            self._values["index_template"] = index_template
        if indices_fielddata_cache_size is not None:
            self._values["indices_fielddata_cache_size"] = indices_fielddata_cache_size
        if indices_memory_index_buffer_size is not None:
            self._values["indices_memory_index_buffer_size"] = indices_memory_index_buffer_size
        if indices_memory_max_index_buffer_size is not None:
            self._values["indices_memory_max_index_buffer_size"] = indices_memory_max_index_buffer_size
        if indices_memory_min_index_buffer_size is not None:
            self._values["indices_memory_min_index_buffer_size"] = indices_memory_min_index_buffer_size
        if indices_queries_cache_size is not None:
            self._values["indices_queries_cache_size"] = indices_queries_cache_size
        if indices_query_bool_max_clause_count is not None:
            self._values["indices_query_bool_max_clause_count"] = indices_query_bool_max_clause_count
        if indices_recovery_max_bytes_per_sec is not None:
            self._values["indices_recovery_max_bytes_per_sec"] = indices_recovery_max_bytes_per_sec
        if indices_recovery_max_concurrent_file_chunks is not None:
            self._values["indices_recovery_max_concurrent_file_chunks"] = indices_recovery_max_concurrent_file_chunks
        if ip_filter is not None:
            self._values["ip_filter"] = ip_filter
        if ism_enabled is not None:
            self._values["ism_enabled"] = ism_enabled
        if ism_history_enabled is not None:
            self._values["ism_history_enabled"] = ism_history_enabled
        if ism_history_max_age is not None:
            self._values["ism_history_max_age"] = ism_history_max_age
        if ism_history_max_docs is not None:
            self._values["ism_history_max_docs"] = ism_history_max_docs
        if ism_history_rollover_check_period is not None:
            self._values["ism_history_rollover_check_period"] = ism_history_rollover_check_period
        if ism_history_rollover_retention_period is not None:
            self._values["ism_history_rollover_retention_period"] = ism_history_rollover_retention_period
        if keep_index_refresh_interval is not None:
            self._values["keep_index_refresh_interval"] = keep_index_refresh_interval
        if knn_memory_circuit_breaker_enabled is not None:
            self._values["knn_memory_circuit_breaker_enabled"] = knn_memory_circuit_breaker_enabled
        if knn_memory_circuit_breaker_limit is not None:
            self._values["knn_memory_circuit_breaker_limit"] = knn_memory_circuit_breaker_limit
        if node_search_cache_size is not None:
            self._values["node_search_cache_size"] = node_search_cache_size
        if openid is not None:
            self._values["openid"] = openid
        if opensearch_dashboards is not None:
            self._values["opensearch_dashboards"] = opensearch_dashboards
        if override_main_response_version is not None:
            self._values["override_main_response_version"] = override_main_response_version
        if plugins_alerting_filter_by_backend_roles is not None:
            self._values["plugins_alerting_filter_by_backend_roles"] = plugins_alerting_filter_by_backend_roles
        if public_access is not None:
            self._values["public_access"] = public_access
        if reindex_remote_whitelist is not None:
            self._values["reindex_remote_whitelist"] = reindex_remote_whitelist
        if remote_store is not None:
            self._values["remote_store"] = remote_store
        if saml is not None:
            self._values["saml"] = saml
        if script_max_compilations_rate is not None:
            self._values["script_max_compilations_rate"] = script_max_compilations_rate
        if search_backpressure is not None:
            self._values["search_backpressure"] = search_backpressure
        if search_insights_top_queries is not None:
            self._values["search_insights_top_queries"] = search_insights_top_queries
        if search_max_buckets is not None:
            self._values["search_max_buckets"] = search_max_buckets
        if segrep is not None:
            self._values["segrep"] = segrep
        if service_log is not None:
            self._values["service_log"] = service_log
        if shard_indexing_pressure is not None:
            self._values["shard_indexing_pressure"] = shard_indexing_pressure
        if thread_pool_analyze_queue_size is not None:
            self._values["thread_pool_analyze_queue_size"] = thread_pool_analyze_queue_size
        if thread_pool_analyze_size is not None:
            self._values["thread_pool_analyze_size"] = thread_pool_analyze_size
        if thread_pool_force_merge_size is not None:
            self._values["thread_pool_force_merge_size"] = thread_pool_force_merge_size
        if thread_pool_get_queue_size is not None:
            self._values["thread_pool_get_queue_size"] = thread_pool_get_queue_size
        if thread_pool_get_size is not None:
            self._values["thread_pool_get_size"] = thread_pool_get_size
        if thread_pool_search_queue_size is not None:
            self._values["thread_pool_search_queue_size"] = thread_pool_search_queue_size
        if thread_pool_search_size is not None:
            self._values["thread_pool_search_size"] = thread_pool_search_size
        if thread_pool_search_throttled_queue_size is not None:
            self._values["thread_pool_search_throttled_queue_size"] = thread_pool_search_throttled_queue_size
        if thread_pool_search_throttled_size is not None:
            self._values["thread_pool_search_throttled_size"] = thread_pool_search_throttled_size
        if thread_pool_write_queue_size is not None:
            self._values["thread_pool_write_queue_size"] = thread_pool_write_queue_size
        if thread_pool_write_size is not None:
            self._values["thread_pool_write_size"] = thread_pool_write_size
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def action_auto_create_index_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''action.auto_create_index. Explicitly allow or block automatic creation of indices. Defaults to true.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#action_auto_create_index_enabled ManagedDatabaseOpensearch#action_auto_create_index_enabled}
        '''
        result = self._values.get("action_auto_create_index_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def action_destructive_requires_name(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Require explicit index names when deleting.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#action_destructive_requires_name ManagedDatabaseOpensearch#action_destructive_requires_name}
        '''
        result = self._values.get("action_destructive_requires_name")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def auth_failure_listeners(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesAuthFailureListeners"]:
        '''auth_failure_listeners block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#auth_failure_listeners ManagedDatabaseOpensearch#auth_failure_listeners}
        '''
        result = self._values.get("auth_failure_listeners")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesAuthFailureListeners"], result)

    @builtins.property
    def automatic_utility_network_ip_filter(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Automatic utility network IP Filter. Automatically allow connections from servers in the utility network within the same zone.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#automatic_utility_network_ip_filter ManagedDatabaseOpensearch#automatic_utility_network_ip_filter}
        '''
        result = self._values.get("automatic_utility_network_ip_filter")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def cluster_filecache_remote_data_ratio(self) -> typing.Optional[jsii.Number]:
        '''The limit of how much total remote data can be referenced.

        Defines a limit of how much total remote data can be referenced as a ratio of the size of the disk reserved for the file cache. This is designed to be a safeguard to prevent oversubscribing a cluster. Defaults to 0.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cluster_filecache_remote_data_ratio ManagedDatabaseOpensearch#cluster_filecache_remote_data_ratio}
        '''
        result = self._values.get("cluster_filecache_remote_data_ratio")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cluster_max_shards_per_node(self) -> typing.Optional[jsii.Number]:
        '''Controls the number of shards allowed in the cluster per data node.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cluster_max_shards_per_node ManagedDatabaseOpensearch#cluster_max_shards_per_node}
        '''
        result = self._values.get("cluster_max_shards_per_node")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cluster_remote_store(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesClusterRemoteStore"]:
        '''cluster_remote_store block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cluster_remote_store ManagedDatabaseOpensearch#cluster_remote_store}
        '''
        result = self._values.get("cluster_remote_store")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesClusterRemoteStore"], result)

    @builtins.property
    def cluster_routing_allocation_balance_prefer_primary(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''When set to true, OpenSearch attempts to evenly distribute the primary shards between the cluster nodes.

        Enabling this setting does not always guarantee an equal number of primary shards on each node, especially in the event of a failover. Changing this setting to false after it was set to true does not invoke redistribution of primary shards. Default is false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cluster_routing_allocation_balance_prefer_primary ManagedDatabaseOpensearch#cluster_routing_allocation_balance_prefer_primary}
        '''
        result = self._values.get("cluster_routing_allocation_balance_prefer_primary")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def cluster_routing_allocation_node_concurrent_recoveries(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''Concurrent incoming/outgoing shard recoveries per node.

        How many concurrent incoming/outgoing shard recoveries (normally replicas) are allowed to happen on a node. Defaults to node cpu count * 2.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cluster_routing_allocation_node_concurrent_recoveries ManagedDatabaseOpensearch#cluster_routing_allocation_node_concurrent_recoveries}
        '''
        result = self._values.get("cluster_routing_allocation_node_concurrent_recoveries")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cluster_search_request_slowlog(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlog"]:
        '''cluster_search_request_slowlog block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cluster_search_request_slowlog ManagedDatabaseOpensearch#cluster_search_request_slowlog}
        '''
        result = self._values.get("cluster_search_request_slowlog")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlog"], result)

    @builtins.property
    def custom_domain(self) -> typing.Optional[builtins.str]:
        '''Custom domain. Serve the web frontend using a custom CNAME pointing to the Aiven DNS name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#custom_domain ManagedDatabaseOpensearch#custom_domain}
        '''
        result = self._values.get("custom_domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disk_watermarks(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesDiskWatermarks"]:
        '''disk_watermarks block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#disk_watermarks ManagedDatabaseOpensearch#disk_watermarks}
        '''
        result = self._values.get("disk_watermarks")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesDiskWatermarks"], result)

    @builtins.property
    def elasticsearch_version(self) -> typing.Optional[builtins.str]:
        '''Elasticsearch major version.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#elasticsearch_version ManagedDatabaseOpensearch#elasticsearch_version}
        '''
        result = self._values.get("elasticsearch_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_sender_name(self) -> typing.Optional[builtins.str]:
        '''Sender name placeholder to be used in Opensearch Dashboards and Opensearch keystore.

        This should be identical to the Sender name defined in Opensearch dashboards.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#email_sender_name ManagedDatabaseOpensearch#email_sender_name}
        '''
        result = self._values.get("email_sender_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_sender_password(self) -> typing.Optional[builtins.str]:
        '''Sender password for Opensearch alerts to authenticate with SMTP server.

        Sender password for Opensearch alerts to authenticate with SMTP server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#email_sender_password ManagedDatabaseOpensearch#email_sender_password}
        '''
        result = self._values.get("email_sender_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_sender_username(self) -> typing.Optional[builtins.str]:
        '''Sender username for Opensearch alerts.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#email_sender_username ManagedDatabaseOpensearch#email_sender_username}
        '''
        result = self._values.get("email_sender_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_remote_backed_storage(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable remote-backed storage.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enable_remote_backed_storage ManagedDatabaseOpensearch#enable_remote_backed_storage}
        '''
        result = self._values.get("enable_remote_backed_storage")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enable_searchable_snapshots(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable searchable snapshots.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enable_searchable_snapshots ManagedDatabaseOpensearch#enable_searchable_snapshots}
        '''
        result = self._values.get("enable_searchable_snapshots")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enable_security_audit(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable/Disable security audit.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enable_security_audit ManagedDatabaseOpensearch#enable_security_audit}
        '''
        result = self._values.get("enable_security_audit")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enable_snapshot_api(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable/Disable snapshot API. Enable/Disable snapshot API for custom repositories, this requires security management to be enabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enable_snapshot_api ManagedDatabaseOpensearch#enable_snapshot_api}
        '''
        result = self._values.get("enable_snapshot_api")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def http_max_content_length(self) -> typing.Optional[jsii.Number]:
        '''Maximum content length for HTTP requests to the OpenSearch HTTP API, in bytes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#http_max_content_length ManagedDatabaseOpensearch#http_max_content_length}
        '''
        result = self._values.get("http_max_content_length")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def http_max_header_size(self) -> typing.Optional[jsii.Number]:
        '''The max size of allowed headers, in bytes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#http_max_header_size ManagedDatabaseOpensearch#http_max_header_size}
        '''
        result = self._values.get("http_max_header_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def http_max_initial_line_length(self) -> typing.Optional[jsii.Number]:
        '''The max length of an HTTP URL, in bytes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#http_max_initial_line_length ManagedDatabaseOpensearch#http_max_initial_line_length}
        '''
        result = self._values.get("http_max_initial_line_length")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def index_patterns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Index patterns.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#index_patterns ManagedDatabaseOpensearch#index_patterns}
        '''
        result = self._values.get("index_patterns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def index_rollup(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesIndexRollup"]:
        '''index_rollup block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#index_rollup ManagedDatabaseOpensearch#index_rollup}
        '''
        result = self._values.get("index_rollup")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesIndexRollup"], result)

    @builtins.property
    def index_template(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesIndexTemplate"]:
        '''index_template block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#index_template ManagedDatabaseOpensearch#index_template}
        '''
        result = self._values.get("index_template")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesIndexTemplate"], result)

    @builtins.property
    def indices_fielddata_cache_size(self) -> typing.Optional[jsii.Number]:
        '''Relative amount.

        Maximum amount of heap memory used for field data cache. This is an expert setting; decreasing the value too much will increase overhead of loading field data; too much memory used for field data cache will decrease amount of heap available for other operations.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#indices_fielddata_cache_size ManagedDatabaseOpensearch#indices_fielddata_cache_size}
        '''
        result = self._values.get("indices_fielddata_cache_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def indices_memory_index_buffer_size(self) -> typing.Optional[jsii.Number]:
        '''Percentage value.

        Default is 10%. Total amount of heap used for indexing buffer, before writing segments to disk. This is an expert setting. Too low value will slow down indexing; too high value will increase indexing performance but causes performance issues for query performance.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#indices_memory_index_buffer_size ManagedDatabaseOpensearch#indices_memory_index_buffer_size}
        '''
        result = self._values.get("indices_memory_index_buffer_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def indices_memory_max_index_buffer_size(self) -> typing.Optional[jsii.Number]:
        '''Absolute value.

        Default is unbound. Doesn't work without indices.memory.index_buffer_size. Maximum amount of heap used for query cache, an absolute indices.memory.index_buffer_size maximum hard limit.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#indices_memory_max_index_buffer_size ManagedDatabaseOpensearch#indices_memory_max_index_buffer_size}
        '''
        result = self._values.get("indices_memory_max_index_buffer_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def indices_memory_min_index_buffer_size(self) -> typing.Optional[jsii.Number]:
        '''Absolute value.

        Default is 48mb. Doesn't work without indices.memory.index_buffer_size. Minimum amount of heap used for query cache, an absolute indices.memory.index_buffer_size minimal hard limit.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#indices_memory_min_index_buffer_size ManagedDatabaseOpensearch#indices_memory_min_index_buffer_size}
        '''
        result = self._values.get("indices_memory_min_index_buffer_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def indices_queries_cache_size(self) -> typing.Optional[jsii.Number]:
        '''Percentage value.

        Default is 10%. Maximum amount of heap used for query cache. This is an expert setting. Too low value will decrease query performance and increase performance for other operations; too high value will cause issues with other OpenSearch functionality.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#indices_queries_cache_size ManagedDatabaseOpensearch#indices_queries_cache_size}
        '''
        result = self._values.get("indices_queries_cache_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def indices_query_bool_max_clause_count(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of clauses Lucene BooleanQuery can have.

        The default value (1024) is relatively high, and increasing it may cause performance issues. Investigate other approaches first before increasing this value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#indices_query_bool_max_clause_count ManagedDatabaseOpensearch#indices_query_bool_max_clause_count}
        '''
        result = self._values.get("indices_query_bool_max_clause_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def indices_recovery_max_bytes_per_sec(self) -> typing.Optional[jsii.Number]:
        '''Limits total inbound and outbound recovery traffic for each node.

        Applies to both peer recoveries as well as snapshot recoveries (i.e., restores from a snapshot). Defaults to 40mb.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#indices_recovery_max_bytes_per_sec ManagedDatabaseOpensearch#indices_recovery_max_bytes_per_sec}
        '''
        result = self._values.get("indices_recovery_max_bytes_per_sec")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def indices_recovery_max_concurrent_file_chunks(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''Number of file chunks sent in parallel for each recovery. Defaults to 2.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#indices_recovery_max_concurrent_file_chunks ManagedDatabaseOpensearch#indices_recovery_max_concurrent_file_chunks}
        '''
        result = self._values.get("indices_recovery_max_concurrent_file_chunks")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ip_filter(self) -> typing.Optional[typing.List[builtins.str]]:
        '''IP filter. Allow incoming connections from CIDR address block, e.g. '10.20.0.0/16'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#ip_filter ManagedDatabaseOpensearch#ip_filter}
        '''
        result = self._values.get("ip_filter")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ism_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies whether ISM is enabled or not.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#ism_enabled ManagedDatabaseOpensearch#ism_enabled}
        '''
        result = self._values.get("ism_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ism_history_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies whether audit history is enabled or not. The logs from ISM are automatically indexed to a logs document.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#ism_history_enabled ManagedDatabaseOpensearch#ism_history_enabled}
        '''
        result = self._values.get("ism_history_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ism_history_max_age(self) -> typing.Optional[jsii.Number]:
        '''The maximum age before rolling over the audit history index in hours.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#ism_history_max_age ManagedDatabaseOpensearch#ism_history_max_age}
        '''
        result = self._values.get("ism_history_max_age")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ism_history_max_docs(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of documents before rolling over the audit history index.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#ism_history_max_docs ManagedDatabaseOpensearch#ism_history_max_docs}
        '''
        result = self._values.get("ism_history_max_docs")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ism_history_rollover_check_period(self) -> typing.Optional[jsii.Number]:
        '''The time between rollover checks for the audit history index in hours.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#ism_history_rollover_check_period ManagedDatabaseOpensearch#ism_history_rollover_check_period}
        '''
        result = self._values.get("ism_history_rollover_check_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ism_history_rollover_retention_period(self) -> typing.Optional[jsii.Number]:
        '''How long audit history indices are kept in days.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#ism_history_rollover_retention_period ManagedDatabaseOpensearch#ism_history_rollover_retention_period}
        '''
        result = self._values.get("ism_history_rollover_retention_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def keep_index_refresh_interval(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Don't reset index.refresh_interval to the default value. Aiven automation resets index.refresh_interval to default value for every index to be sure that indices are always visible to search. If it doesn't fit your case, you can disable this by setting up this flag to true.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#keep_index_refresh_interval ManagedDatabaseOpensearch#keep_index_refresh_interval}
        '''
        result = self._values.get("keep_index_refresh_interval")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def knn_memory_circuit_breaker_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable or disable KNN memory circuit breaker. Defaults to true.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#knn_memory_circuit_breaker_enabled ManagedDatabaseOpensearch#knn_memory_circuit_breaker_enabled}
        '''
        result = self._values.get("knn_memory_circuit_breaker_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def knn_memory_circuit_breaker_limit(self) -> typing.Optional[jsii.Number]:
        '''Maximum amount of memory that can be used for KNN index. Defaults to 50% of the JVM heap size.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#knn_memory_circuit_breaker_limit ManagedDatabaseOpensearch#knn_memory_circuit_breaker_limit}
        '''
        result = self._values.get("knn_memory_circuit_breaker_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def node_search_cache_size(self) -> typing.Optional[builtins.str]:
        '''The limit of how much total remote data can be referenced.

        Defines a limit of how much total remote data can be referenced as a ratio of the size of the disk reserved for the file cache. This is designed to be a safeguard to prevent oversubscribing a cluster. Defaults to 5gb. Requires restarting all OpenSearch nodes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#node_search_cache_size ManagedDatabaseOpensearch#node_search_cache_size}
        '''
        result = self._values.get("node_search_cache_size")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def openid(self) -> typing.Optional["ManagedDatabaseOpensearchPropertiesOpenid"]:
        '''openid block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#openid ManagedDatabaseOpensearch#openid}
        '''
        result = self._values.get("openid")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesOpenid"], result)

    @builtins.property
    def opensearch_dashboards(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesOpensearchDashboards"]:
        '''opensearch_dashboards block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#opensearch_dashboards ManagedDatabaseOpensearch#opensearch_dashboards}
        '''
        result = self._values.get("opensearch_dashboards")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesOpensearchDashboards"], result)

    @builtins.property
    def override_main_response_version(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Compatibility mode sets OpenSearch to report its version as 7.10 so clients continue to work. Default is false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#override_main_response_version ManagedDatabaseOpensearch#override_main_response_version}
        '''
        result = self._values.get("override_main_response_version")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def plugins_alerting_filter_by_backend_roles(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable or disable filtering of alerting by backend roles. Requires Security plugin. Defaults to false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#plugins_alerting_filter_by_backend_roles ManagedDatabaseOpensearch#plugins_alerting_filter_by_backend_roles}
        '''
        result = self._values.get("plugins_alerting_filter_by_backend_roles")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def public_access(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Public Access. Allow access to the service from the public Internet.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#public_access ManagedDatabaseOpensearch#public_access}
        '''
        result = self._values.get("public_access")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def reindex_remote_whitelist(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Whitelisted addresses for reindexing. Changing this value will cause all OpenSearch instances to restart.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#reindex_remote_whitelist ManagedDatabaseOpensearch#reindex_remote_whitelist}
        '''
        result = self._values.get("reindex_remote_whitelist")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def remote_store(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesRemoteStore"]:
        '''remote_store block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#remote_store ManagedDatabaseOpensearch#remote_store}
        '''
        result = self._values.get("remote_store")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesRemoteStore"], result)

    @builtins.property
    def saml(self) -> typing.Optional["ManagedDatabaseOpensearchPropertiesSaml"]:
        '''saml block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#saml ManagedDatabaseOpensearch#saml}
        '''
        result = self._values.get("saml")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesSaml"], result)

    @builtins.property
    def script_max_compilations_rate(self) -> typing.Optional[builtins.str]:
        '''Script max compilation rate - circuit breaker to prevent/minimize OOMs.

        Script compilation circuit breaker limits the number of inline script compilations within a period of time. Default is use-context.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#script_max_compilations_rate ManagedDatabaseOpensearch#script_max_compilations_rate}
        '''
        result = self._values.get("script_max_compilations_rate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def search_backpressure(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesSearchBackpressure"]:
        '''search_backpressure block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#search_backpressure ManagedDatabaseOpensearch#search_backpressure}
        '''
        result = self._values.get("search_backpressure")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesSearchBackpressure"], result)

    @builtins.property
    def search_insights_top_queries(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueries"]:
        '''search_insights_top_queries block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#search_insights_top_queries ManagedDatabaseOpensearch#search_insights_top_queries}
        '''
        result = self._values.get("search_insights_top_queries")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueries"], result)

    @builtins.property
    def search_max_buckets(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of aggregation buckets allowed in a single response.

        OpenSearch default value is used when this is not defined.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#search_max_buckets ManagedDatabaseOpensearch#search_max_buckets}
        '''
        result = self._values.get("search_max_buckets")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def segrep(self) -> typing.Optional["ManagedDatabaseOpensearchPropertiesSegrep"]:
        '''segrep block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#segrep ManagedDatabaseOpensearch#segrep}
        '''
        result = self._values.get("segrep")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesSegrep"], result)

    @builtins.property
    def service_log(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Service logging. Store logs for the service so that they are available in the HTTP API and console.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#service_log ManagedDatabaseOpensearch#service_log}
        '''
        result = self._values.get("service_log")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def shard_indexing_pressure(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesShardIndexingPressure"]:
        '''shard_indexing_pressure block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#shard_indexing_pressure ManagedDatabaseOpensearch#shard_indexing_pressure}
        '''
        result = self._values.get("shard_indexing_pressure")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesShardIndexingPressure"], result)

    @builtins.property
    def thread_pool_analyze_queue_size(self) -> typing.Optional[jsii.Number]:
        '''analyze thread pool queue size. Size for the thread pool queue. See documentation for exact details.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_analyze_queue_size ManagedDatabaseOpensearch#thread_pool_analyze_queue_size}
        '''
        result = self._values.get("thread_pool_analyze_queue_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_analyze_size(self) -> typing.Optional[jsii.Number]:
        '''analyze thread pool size.

        Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_analyze_size ManagedDatabaseOpensearch#thread_pool_analyze_size}
        '''
        result = self._values.get("thread_pool_analyze_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_force_merge_size(self) -> typing.Optional[jsii.Number]:
        '''force_merge thread pool size.

        Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_force_merge_size ManagedDatabaseOpensearch#thread_pool_force_merge_size}
        '''
        result = self._values.get("thread_pool_force_merge_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_get_queue_size(self) -> typing.Optional[jsii.Number]:
        '''get thread pool queue size. Size for the thread pool queue. See documentation for exact details.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_get_queue_size ManagedDatabaseOpensearch#thread_pool_get_queue_size}
        '''
        result = self._values.get("thread_pool_get_queue_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_get_size(self) -> typing.Optional[jsii.Number]:
        '''get thread pool size.

        Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_get_size ManagedDatabaseOpensearch#thread_pool_get_size}
        '''
        result = self._values.get("thread_pool_get_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_search_queue_size(self) -> typing.Optional[jsii.Number]:
        '''search thread pool queue size. Size for the thread pool queue. See documentation for exact details.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_search_queue_size ManagedDatabaseOpensearch#thread_pool_search_queue_size}
        '''
        result = self._values.get("thread_pool_search_queue_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_search_size(self) -> typing.Optional[jsii.Number]:
        '''search thread pool size.

        Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_search_size ManagedDatabaseOpensearch#thread_pool_search_size}
        '''
        result = self._values.get("thread_pool_search_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_search_throttled_queue_size(self) -> typing.Optional[jsii.Number]:
        '''search_throttled thread pool queue size. Size for the thread pool queue. See documentation for exact details.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_search_throttled_queue_size ManagedDatabaseOpensearch#thread_pool_search_throttled_queue_size}
        '''
        result = self._values.get("thread_pool_search_throttled_queue_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_search_throttled_size(self) -> typing.Optional[jsii.Number]:
        '''search_throttled thread pool size.

        Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_search_throttled_size ManagedDatabaseOpensearch#thread_pool_search_throttled_size}
        '''
        result = self._values.get("thread_pool_search_throttled_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_write_queue_size(self) -> typing.Optional[jsii.Number]:
        '''write thread pool queue size. Size for the thread pool queue. See documentation for exact details.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_write_queue_size ManagedDatabaseOpensearch#thread_pool_write_queue_size}
        '''
        result = self._values.get("thread_pool_write_queue_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_write_size(self) -> typing.Optional[jsii.Number]:
        '''write thread pool size.

        Size for the thread pool. See documentation for exact details. Do note this may have maximum value depending on CPU count - value is automatically lowered if set to higher than maximum value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#thread_pool_write_size ManagedDatabaseOpensearch#thread_pool_write_size}
        '''
        result = self._values.get("thread_pool_write_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''OpenSearch major version.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#version ManagedDatabaseOpensearch#version}
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesAuthFailureListeners",
    jsii_struct_bases=[],
    name_mapping={
        "internal_authentication_backend_limiting": "internalAuthenticationBackendLimiting",
    },
)
class ManagedDatabaseOpensearchPropertiesAuthFailureListeners:
    def __init__(
        self,
        *,
        internal_authentication_backend_limiting: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param internal_authentication_backend_limiting: internal_authentication_backend_limiting block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#internal_authentication_backend_limiting ManagedDatabaseOpensearch#internal_authentication_backend_limiting}
        '''
        if isinstance(internal_authentication_backend_limiting, dict):
            internal_authentication_backend_limiting = ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting(**internal_authentication_backend_limiting)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da6df7d26b0238df040ca0d1aeaa659a956825f3139e84791c48d896c03493a3)
            check_type(argname="argument internal_authentication_backend_limiting", value=internal_authentication_backend_limiting, expected_type=type_hints["internal_authentication_backend_limiting"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if internal_authentication_backend_limiting is not None:
            self._values["internal_authentication_backend_limiting"] = internal_authentication_backend_limiting

    @builtins.property
    def internal_authentication_backend_limiting(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting"]:
        '''internal_authentication_backend_limiting block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#internal_authentication_backend_limiting ManagedDatabaseOpensearch#internal_authentication_backend_limiting}
        '''
        result = self._values.get("internal_authentication_backend_limiting")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesAuthFailureListeners(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting",
    jsii_struct_bases=[],
    name_mapping={
        "allowed_tries": "allowedTries",
        "authentication_backend": "authenticationBackend",
        "block_expiry_seconds": "blockExpirySeconds",
        "max_blocked_clients": "maxBlockedClients",
        "max_tracked_clients": "maxTrackedClients",
        "time_window_seconds": "timeWindowSeconds",
        "type": "type",
    },
)
class ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting:
    def __init__(
        self,
        *,
        allowed_tries: typing.Optional[jsii.Number] = None,
        authentication_backend: typing.Optional[builtins.str] = None,
        block_expiry_seconds: typing.Optional[jsii.Number] = None,
        max_blocked_clients: typing.Optional[jsii.Number] = None,
        max_tracked_clients: typing.Optional[jsii.Number] = None,
        time_window_seconds: typing.Optional[jsii.Number] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param allowed_tries: The number of login attempts allowed before login is blocked. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#allowed_tries ManagedDatabaseOpensearch#allowed_tries}
        :param authentication_backend: The internal backend. Enter ``internal``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#authentication_backend ManagedDatabaseOpensearch#authentication_backend}
        :param block_expiry_seconds: The duration of time that login remains blocked after a failed login. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#block_expiry_seconds ManagedDatabaseOpensearch#block_expiry_seconds}
        :param max_blocked_clients: The maximum number of blocked IP addresses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#max_blocked_clients ManagedDatabaseOpensearch#max_blocked_clients}
        :param max_tracked_clients: The maximum number of tracked IP addresses that have failed login. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#max_tracked_clients ManagedDatabaseOpensearch#max_tracked_clients}
        :param time_window_seconds: The window of time in which the value for ``allowed_tries`` is enforced. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#time_window_seconds ManagedDatabaseOpensearch#time_window_seconds}
        :param type: The type of rate limiting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#type ManagedDatabaseOpensearch#type}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9435799fa69802c70cf9a1ec8b896a69d09f232c4c49f47ff2d40e3e18c2343b)
            check_type(argname="argument allowed_tries", value=allowed_tries, expected_type=type_hints["allowed_tries"])
            check_type(argname="argument authentication_backend", value=authentication_backend, expected_type=type_hints["authentication_backend"])
            check_type(argname="argument block_expiry_seconds", value=block_expiry_seconds, expected_type=type_hints["block_expiry_seconds"])
            check_type(argname="argument max_blocked_clients", value=max_blocked_clients, expected_type=type_hints["max_blocked_clients"])
            check_type(argname="argument max_tracked_clients", value=max_tracked_clients, expected_type=type_hints["max_tracked_clients"])
            check_type(argname="argument time_window_seconds", value=time_window_seconds, expected_type=type_hints["time_window_seconds"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if allowed_tries is not None:
            self._values["allowed_tries"] = allowed_tries
        if authentication_backend is not None:
            self._values["authentication_backend"] = authentication_backend
        if block_expiry_seconds is not None:
            self._values["block_expiry_seconds"] = block_expiry_seconds
        if max_blocked_clients is not None:
            self._values["max_blocked_clients"] = max_blocked_clients
        if max_tracked_clients is not None:
            self._values["max_tracked_clients"] = max_tracked_clients
        if time_window_seconds is not None:
            self._values["time_window_seconds"] = time_window_seconds
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def allowed_tries(self) -> typing.Optional[jsii.Number]:
        '''The number of login attempts allowed before login is blocked.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#allowed_tries ManagedDatabaseOpensearch#allowed_tries}
        '''
        result = self._values.get("allowed_tries")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def authentication_backend(self) -> typing.Optional[builtins.str]:
        '''The internal backend. Enter ``internal``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#authentication_backend ManagedDatabaseOpensearch#authentication_backend}
        '''
        result = self._values.get("authentication_backend")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def block_expiry_seconds(self) -> typing.Optional[jsii.Number]:
        '''The duration of time that login remains blocked after a failed login.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#block_expiry_seconds ManagedDatabaseOpensearch#block_expiry_seconds}
        '''
        result = self._values.get("block_expiry_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_blocked_clients(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of blocked IP addresses.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#max_blocked_clients ManagedDatabaseOpensearch#max_blocked_clients}
        '''
        result = self._values.get("max_blocked_clients")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_tracked_clients(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of tracked IP addresses that have failed login.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#max_tracked_clients ManagedDatabaseOpensearch#max_tracked_clients}
        '''
        result = self._values.get("max_tracked_clients")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def time_window_seconds(self) -> typing.Optional[jsii.Number]:
        '''The window of time in which the value for ``allowed_tries`` is enforced.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#time_window_seconds ManagedDatabaseOpensearch#time_window_seconds}
        '''
        result = self._values.get("time_window_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''The type of rate limiting.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#type ManagedDatabaseOpensearch#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimitingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimitingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__99749960614da71029c64a8b792ced764cdf27a0962414854d04210bb1ae2acd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAllowedTries")
    def reset_allowed_tries(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedTries", []))

    @jsii.member(jsii_name="resetAuthenticationBackend")
    def reset_authentication_backend(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthenticationBackend", []))

    @jsii.member(jsii_name="resetBlockExpirySeconds")
    def reset_block_expiry_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlockExpirySeconds", []))

    @jsii.member(jsii_name="resetMaxBlockedClients")
    def reset_max_blocked_clients(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxBlockedClients", []))

    @jsii.member(jsii_name="resetMaxTrackedClients")
    def reset_max_tracked_clients(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxTrackedClients", []))

    @jsii.member(jsii_name="resetTimeWindowSeconds")
    def reset_time_window_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeWindowSeconds", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @builtins.property
    @jsii.member(jsii_name="allowedTriesInput")
    def allowed_tries_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "allowedTriesInput"))

    @builtins.property
    @jsii.member(jsii_name="authenticationBackendInput")
    def authentication_backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authenticationBackendInput"))

    @builtins.property
    @jsii.member(jsii_name="blockExpirySecondsInput")
    def block_expiry_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "blockExpirySecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxBlockedClientsInput")
    def max_blocked_clients_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxBlockedClientsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxTrackedClientsInput")
    def max_tracked_clients_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxTrackedClientsInput"))

    @builtins.property
    @jsii.member(jsii_name="timeWindowSecondsInput")
    def time_window_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeWindowSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedTries")
    def allowed_tries(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "allowedTries"))

    @allowed_tries.setter
    def allowed_tries(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3cd07b462b44760122178a37243eab5bce0c8902d031193949d1c2e9b173cef8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedTries", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authenticationBackend")
    def authentication_backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authenticationBackend"))

    @authentication_backend.setter
    def authentication_backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c97e2414097315d7ba383e33a5dc0b3357f770c50a34a76b2c31435635e7ede3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authenticationBackend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="blockExpirySeconds")
    def block_expiry_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "blockExpirySeconds"))

    @block_expiry_seconds.setter
    def block_expiry_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8966671b06b0cb755048c486e085213fe8c8f8eb3434ef864493050eac73e366)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "blockExpirySeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxBlockedClients")
    def max_blocked_clients(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxBlockedClients"))

    @max_blocked_clients.setter
    def max_blocked_clients(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0448c88bdb2b3db18c1c620763fad421cf34b0e345fd1cfeb0590539f6fbf08)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxBlockedClients", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxTrackedClients")
    def max_tracked_clients(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxTrackedClients"))

    @max_tracked_clients.setter
    def max_tracked_clients(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0911499e4bd4d24c4fe2f3f9f3cd2c527bcfc391686536082567743a93ddb080)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxTrackedClients", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeWindowSeconds")
    def time_window_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeWindowSeconds"))

    @time_window_seconds.setter
    def time_window_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe8bc44df1f627c05d7f87446be558febc5900c4b151855121869224bf95cf0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeWindowSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__524634a3518077cc05d7163bab39b1e5c92bf78a97db61a74f322b581322cf1b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__827575e00c1eaecf35d33d817e94688109afe1fa2f142d1614bdc103f0e670cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ManagedDatabaseOpensearchPropertiesAuthFailureListenersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesAuthFailureListenersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2bb457d048cf3243bf7b1785b9d3430cd66839097d28517e5978e7c0ff727704)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putInternalAuthenticationBackendLimiting")
    def put_internal_authentication_backend_limiting(
        self,
        *,
        allowed_tries: typing.Optional[jsii.Number] = None,
        authentication_backend: typing.Optional[builtins.str] = None,
        block_expiry_seconds: typing.Optional[jsii.Number] = None,
        max_blocked_clients: typing.Optional[jsii.Number] = None,
        max_tracked_clients: typing.Optional[jsii.Number] = None,
        time_window_seconds: typing.Optional[jsii.Number] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param allowed_tries: The number of login attempts allowed before login is blocked. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#allowed_tries ManagedDatabaseOpensearch#allowed_tries}
        :param authentication_backend: The internal backend. Enter ``internal``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#authentication_backend ManagedDatabaseOpensearch#authentication_backend}
        :param block_expiry_seconds: The duration of time that login remains blocked after a failed login. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#block_expiry_seconds ManagedDatabaseOpensearch#block_expiry_seconds}
        :param max_blocked_clients: The maximum number of blocked IP addresses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#max_blocked_clients ManagedDatabaseOpensearch#max_blocked_clients}
        :param max_tracked_clients: The maximum number of tracked IP addresses that have failed login. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#max_tracked_clients ManagedDatabaseOpensearch#max_tracked_clients}
        :param time_window_seconds: The window of time in which the value for ``allowed_tries`` is enforced. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#time_window_seconds ManagedDatabaseOpensearch#time_window_seconds}
        :param type: The type of rate limiting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#type ManagedDatabaseOpensearch#type}
        '''
        value = ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting(
            allowed_tries=allowed_tries,
            authentication_backend=authentication_backend,
            block_expiry_seconds=block_expiry_seconds,
            max_blocked_clients=max_blocked_clients,
            max_tracked_clients=max_tracked_clients,
            time_window_seconds=time_window_seconds,
            type=type,
        )

        return typing.cast(None, jsii.invoke(self, "putInternalAuthenticationBackendLimiting", [value]))

    @jsii.member(jsii_name="resetInternalAuthenticationBackendLimiting")
    def reset_internal_authentication_backend_limiting(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInternalAuthenticationBackendLimiting", []))

    @builtins.property
    @jsii.member(jsii_name="internalAuthenticationBackendLimiting")
    def internal_authentication_backend_limiting(
        self,
    ) -> ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimitingOutputReference:
        return typing.cast(ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimitingOutputReference, jsii.get(self, "internalAuthenticationBackendLimiting"))

    @builtins.property
    @jsii.member(jsii_name="internalAuthenticationBackendLimitingInput")
    def internal_authentication_backend_limiting_input(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting], jsii.get(self, "internalAuthenticationBackendLimitingInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListeners]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListeners], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListeners],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9841d9da7d378cfedc4cae10fb3cd1f05a03ee8993362ac50891755214ff708)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesClusterRemoteStore",
    jsii_struct_bases=[],
    name_mapping={
        "state_global_metadata_upload_timeout": "stateGlobalMetadataUploadTimeout",
        "state_metadata_manifest_upload_timeout": "stateMetadataManifestUploadTimeout",
        "translog_buffer_interval": "translogBufferInterval",
        "translog_max_readers": "translogMaxReaders",
    },
)
class ManagedDatabaseOpensearchPropertiesClusterRemoteStore:
    def __init__(
        self,
        *,
        state_global_metadata_upload_timeout: typing.Optional[builtins.str] = None,
        state_metadata_manifest_upload_timeout: typing.Optional[builtins.str] = None,
        translog_buffer_interval: typing.Optional[builtins.str] = None,
        translog_max_readers: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param state_global_metadata_upload_timeout: The amount of time to wait for the cluster state upload to complete. The amount of time to wait for the cluster state upload to complete. Defaults to 20s. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#state_global_metadata_upload_timeout ManagedDatabaseOpensearch#state_global_metadata_upload_timeout}
        :param state_metadata_manifest_upload_timeout: The amount of time to wait for the manifest file upload to complete. The amount of time to wait for the manifest file upload to complete. The manifest file contains the details of each of the files uploaded for a single cluster state, both index metadata files and global metadata files. Defaults to 20s. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#state_metadata_manifest_upload_timeout ManagedDatabaseOpensearch#state_metadata_manifest_upload_timeout}
        :param translog_buffer_interval: The default value of the translog buffer interval. The default value of the translog buffer interval used when performing periodic translog updates. This setting is only effective when the index setting ``index.remote_store.translog.buffer_interval`` is not present. Defaults to 650ms. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#translog_buffer_interval ManagedDatabaseOpensearch#translog_buffer_interval}
        :param translog_max_readers: The maximum number of open translog files for remote-backed indexes. Sets the maximum number of open translog files for remote-backed indexes. This limits the total number of translog files per shard. After reaching this limit, the remote store flushes the translog files. Default is 1000. The minimum required is 100. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#translog_max_readers ManagedDatabaseOpensearch#translog_max_readers}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8bf09b01c282df36e41b853e405726d98c811dab3e94915dc82e4bce9ce583ce)
            check_type(argname="argument state_global_metadata_upload_timeout", value=state_global_metadata_upload_timeout, expected_type=type_hints["state_global_metadata_upload_timeout"])
            check_type(argname="argument state_metadata_manifest_upload_timeout", value=state_metadata_manifest_upload_timeout, expected_type=type_hints["state_metadata_manifest_upload_timeout"])
            check_type(argname="argument translog_buffer_interval", value=translog_buffer_interval, expected_type=type_hints["translog_buffer_interval"])
            check_type(argname="argument translog_max_readers", value=translog_max_readers, expected_type=type_hints["translog_max_readers"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if state_global_metadata_upload_timeout is not None:
            self._values["state_global_metadata_upload_timeout"] = state_global_metadata_upload_timeout
        if state_metadata_manifest_upload_timeout is not None:
            self._values["state_metadata_manifest_upload_timeout"] = state_metadata_manifest_upload_timeout
        if translog_buffer_interval is not None:
            self._values["translog_buffer_interval"] = translog_buffer_interval
        if translog_max_readers is not None:
            self._values["translog_max_readers"] = translog_max_readers

    @builtins.property
    def state_global_metadata_upload_timeout(self) -> typing.Optional[builtins.str]:
        '''The amount of time to wait for the cluster state upload to complete.

        The amount of time to wait for the cluster state upload to complete. Defaults to 20s.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#state_global_metadata_upload_timeout ManagedDatabaseOpensearch#state_global_metadata_upload_timeout}
        '''
        result = self._values.get("state_global_metadata_upload_timeout")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state_metadata_manifest_upload_timeout(self) -> typing.Optional[builtins.str]:
        '''The amount of time to wait for the manifest file upload to complete.

        The amount of time to wait for the manifest file upload to complete. The manifest file contains the details of each of the files uploaded for a single cluster state, both index metadata files and global metadata files. Defaults to 20s.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#state_metadata_manifest_upload_timeout ManagedDatabaseOpensearch#state_metadata_manifest_upload_timeout}
        '''
        result = self._values.get("state_metadata_manifest_upload_timeout")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def translog_buffer_interval(self) -> typing.Optional[builtins.str]:
        '''The default value of the translog buffer interval.

        The default value of the translog buffer interval used when performing periodic translog updates. This setting is only effective when the index setting ``index.remote_store.translog.buffer_interval`` is not present. Defaults to 650ms.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#translog_buffer_interval ManagedDatabaseOpensearch#translog_buffer_interval}
        '''
        result = self._values.get("translog_buffer_interval")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def translog_max_readers(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of open translog files for remote-backed indexes.

        Sets the maximum number of open translog files for remote-backed indexes. This limits the total number of translog files per shard. After reaching this limit, the remote store flushes the translog files. Default is 1000. The minimum required is 100.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#translog_max_readers ManagedDatabaseOpensearch#translog_max_readers}
        '''
        result = self._values.get("translog_max_readers")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesClusterRemoteStore(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchPropertiesClusterRemoteStoreOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesClusterRemoteStoreOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3a2ce59de3d35325edbf31f06bd6314fd8a1f6f2b0cbf0cc4c852657ac53b74f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetStateGlobalMetadataUploadTimeout")
    def reset_state_global_metadata_upload_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStateGlobalMetadataUploadTimeout", []))

    @jsii.member(jsii_name="resetStateMetadataManifestUploadTimeout")
    def reset_state_metadata_manifest_upload_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStateMetadataManifestUploadTimeout", []))

    @jsii.member(jsii_name="resetTranslogBufferInterval")
    def reset_translog_buffer_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTranslogBufferInterval", []))

    @jsii.member(jsii_name="resetTranslogMaxReaders")
    def reset_translog_max_readers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTranslogMaxReaders", []))

    @builtins.property
    @jsii.member(jsii_name="stateGlobalMetadataUploadTimeoutInput")
    def state_global_metadata_upload_timeout_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateGlobalMetadataUploadTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="stateMetadataManifestUploadTimeoutInput")
    def state_metadata_manifest_upload_timeout_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateMetadataManifestUploadTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="translogBufferIntervalInput")
    def translog_buffer_interval_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "translogBufferIntervalInput"))

    @builtins.property
    @jsii.member(jsii_name="translogMaxReadersInput")
    def translog_max_readers_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "translogMaxReadersInput"))

    @builtins.property
    @jsii.member(jsii_name="stateGlobalMetadataUploadTimeout")
    def state_global_metadata_upload_timeout(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stateGlobalMetadataUploadTimeout"))

    @state_global_metadata_upload_timeout.setter
    def state_global_metadata_upload_timeout(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__262389b84e11bdd882c1d940b5bbde682b70a413568e5d144d27966190c7ae18)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stateGlobalMetadataUploadTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stateMetadataManifestUploadTimeout")
    def state_metadata_manifest_upload_timeout(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stateMetadataManifestUploadTimeout"))

    @state_metadata_manifest_upload_timeout.setter
    def state_metadata_manifest_upload_timeout(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9de1fc53a6ea5f030acd5311533fa5594e2e560df3ba985952c9d7b266004c51)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stateMetadataManifestUploadTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="translogBufferInterval")
    def translog_buffer_interval(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "translogBufferInterval"))

    @translog_buffer_interval.setter
    def translog_buffer_interval(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18485bd7370577759f74717505aa14e2600467bbcf2e3ee12cf56de0c96f0030)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "translogBufferInterval", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="translogMaxReaders")
    def translog_max_readers(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "translogMaxReaders"))

    @translog_max_readers.setter
    def translog_max_readers(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d288fe3c75526f1f2dc35253affa3e160d3e45a773c50dc363eaeb2f542fe229)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "translogMaxReaders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesClusterRemoteStore]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesClusterRemoteStore], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesClusterRemoteStore],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b9e5024bfb1eae2b8040b8cf5457ca2dd70962144d91f9aa51c22d2ef702b27)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlog",
    jsii_struct_bases=[],
    name_mapping={"level": "level", "threshold": "threshold"},
)
class ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlog:
    def __init__(
        self,
        *,
        level: typing.Optional[builtins.str] = None,
        threshold: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlogThreshold", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param level: Log level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#level ManagedDatabaseOpensearch#level}
        :param threshold: threshold block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#threshold ManagedDatabaseOpensearch#threshold}
        '''
        if isinstance(threshold, dict):
            threshold = ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlogThreshold(**threshold)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1eadea9efdeac59a42a8f43fdb4be6968800ad553251e2efe3e8597efb2c7fb)
            check_type(argname="argument level", value=level, expected_type=type_hints["level"])
            check_type(argname="argument threshold", value=threshold, expected_type=type_hints["threshold"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if level is not None:
            self._values["level"] = level
        if threshold is not None:
            self._values["threshold"] = threshold

    @builtins.property
    def level(self) -> typing.Optional[builtins.str]:
        '''Log level.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#level ManagedDatabaseOpensearch#level}
        '''
        result = self._values.get("level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def threshold(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlogThreshold"]:
        '''threshold block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#threshold ManagedDatabaseOpensearch#threshold}
        '''
        result = self._values.get("threshold")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlogThreshold"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlog(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlogOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlogOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6a2e383dfbb2de0011633030253319bf1abf3c6c5c6831459f3b97e703ca19ba)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putThreshold")
    def put_threshold(
        self,
        *,
        debug: typing.Optional[builtins.str] = None,
        info: typing.Optional[builtins.str] = None,
        trace: typing.Optional[builtins.str] = None,
        warn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param debug: Debug threshold for total request took time. The value should be in the form count and unit, where unit one of (s,m,h,d,nanos,ms,micros) or -1. Default is -1. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#debug ManagedDatabaseOpensearch#debug}
        :param info: Info threshold for total request took time. The value should be in the form count and unit, where unit one of (s,m,h,d,nanos,ms,micros) or -1. Default is -1. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#info ManagedDatabaseOpensearch#info}
        :param trace: Trace threshold for total request took time. The value should be in the form count and unit, where unit one of (s,m,h,d,nanos,ms,micros) or -1. Default is -1. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#trace ManagedDatabaseOpensearch#trace}
        :param warn: Warning threshold for total request took time. The value should be in the form count and unit, where unit one of (s,m,h,d,nanos,ms,micros) or -1. Default is -1. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#warn ManagedDatabaseOpensearch#warn}
        '''
        value = ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlogThreshold(
            debug=debug, info=info, trace=trace, warn=warn
        )

        return typing.cast(None, jsii.invoke(self, "putThreshold", [value]))

    @jsii.member(jsii_name="resetLevel")
    def reset_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLevel", []))

    @jsii.member(jsii_name="resetThreshold")
    def reset_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreshold", []))

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(
        self,
    ) -> "ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlogThresholdOutputReference":
        return typing.cast("ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlogThresholdOutputReference", jsii.get(self, "threshold"))

    @builtins.property
    @jsii.member(jsii_name="levelInput")
    def level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "levelInput"))

    @builtins.property
    @jsii.member(jsii_name="thresholdInput")
    def threshold_input(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlogThreshold"]:
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlogThreshold"], jsii.get(self, "thresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="level")
    def level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "level"))

    @level.setter
    def level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b14d13f5622ae593489f694e875d89afd8bcfedc7dc9ef82306ea211d1a05da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "level", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlog]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlog], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlog],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43bd50dc17e271b755c3fca4452f83c3e2e79379fd91a6d11d12dfa6eb1bdb63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlogThreshold",
    jsii_struct_bases=[],
    name_mapping={"debug": "debug", "info": "info", "trace": "trace", "warn": "warn"},
)
class ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlogThreshold:
    def __init__(
        self,
        *,
        debug: typing.Optional[builtins.str] = None,
        info: typing.Optional[builtins.str] = None,
        trace: typing.Optional[builtins.str] = None,
        warn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param debug: Debug threshold for total request took time. The value should be in the form count and unit, where unit one of (s,m,h,d,nanos,ms,micros) or -1. Default is -1. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#debug ManagedDatabaseOpensearch#debug}
        :param info: Info threshold for total request took time. The value should be in the form count and unit, where unit one of (s,m,h,d,nanos,ms,micros) or -1. Default is -1. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#info ManagedDatabaseOpensearch#info}
        :param trace: Trace threshold for total request took time. The value should be in the form count and unit, where unit one of (s,m,h,d,nanos,ms,micros) or -1. Default is -1. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#trace ManagedDatabaseOpensearch#trace}
        :param warn: Warning threshold for total request took time. The value should be in the form count and unit, where unit one of (s,m,h,d,nanos,ms,micros) or -1. Default is -1. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#warn ManagedDatabaseOpensearch#warn}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7693880d283c41692690ec00b0f211583f9092af9a4f9be8cc2503b2af685fc)
            check_type(argname="argument debug", value=debug, expected_type=type_hints["debug"])
            check_type(argname="argument info", value=info, expected_type=type_hints["info"])
            check_type(argname="argument trace", value=trace, expected_type=type_hints["trace"])
            check_type(argname="argument warn", value=warn, expected_type=type_hints["warn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if debug is not None:
            self._values["debug"] = debug
        if info is not None:
            self._values["info"] = info
        if trace is not None:
            self._values["trace"] = trace
        if warn is not None:
            self._values["warn"] = warn

    @builtins.property
    def debug(self) -> typing.Optional[builtins.str]:
        '''Debug threshold for total request took time.

        The value should be in the form count and unit, where unit one of (s,m,h,d,nanos,ms,micros) or -1. Default is -1.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#debug ManagedDatabaseOpensearch#debug}
        '''
        result = self._values.get("debug")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def info(self) -> typing.Optional[builtins.str]:
        '''Info threshold for total request took time.

        The value should be in the form count and unit, where unit one of (s,m,h,d,nanos,ms,micros) or -1. Default is -1.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#info ManagedDatabaseOpensearch#info}
        '''
        result = self._values.get("info")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def trace(self) -> typing.Optional[builtins.str]:
        '''Trace threshold for total request took time.

        The value should be in the form count and unit, where unit one of (s,m,h,d,nanos,ms,micros) or -1. Default is -1.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#trace ManagedDatabaseOpensearch#trace}
        '''
        result = self._values.get("trace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def warn(self) -> typing.Optional[builtins.str]:
        '''Warning threshold for total request took time.

        The value should be in the form count and unit, where unit one of (s,m,h,d,nanos,ms,micros) or -1. Default is -1.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#warn ManagedDatabaseOpensearch#warn}
        '''
        result = self._values.get("warn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlogThreshold(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlogThresholdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlogThresholdOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__746e796ffd67ae3881ed3680bae51d65b7298cd5e3841cebd66ee49f5e60ee64)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDebug")
    def reset_debug(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDebug", []))

    @jsii.member(jsii_name="resetInfo")
    def reset_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInfo", []))

    @jsii.member(jsii_name="resetTrace")
    def reset_trace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTrace", []))

    @jsii.member(jsii_name="resetWarn")
    def reset_warn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWarn", []))

    @builtins.property
    @jsii.member(jsii_name="debugInput")
    def debug_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "debugInput"))

    @builtins.property
    @jsii.member(jsii_name="infoInput")
    def info_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "infoInput"))

    @builtins.property
    @jsii.member(jsii_name="traceInput")
    def trace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "traceInput"))

    @builtins.property
    @jsii.member(jsii_name="warnInput")
    def warn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "warnInput"))

    @builtins.property
    @jsii.member(jsii_name="debug")
    def debug(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "debug"))

    @debug.setter
    def debug(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1edac68c2f51e1d8421f2df83f6d764637d8e5d50db4d416276e81b7dc64a10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "debug", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="info")
    def info(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "info"))

    @info.setter
    def info(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9acd66c824a35920ef5f66e89cc105ab20a49ab57b57a82783cdbd9aa1c4615b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "info", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="trace")
    def trace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "trace"))

    @trace.setter
    def trace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53cfc2baf6e36ac98957aef65f5ebbfe6e59103dd0926217a9ea40b32e62e6c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "trace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="warn")
    def warn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "warn"))

    @warn.setter
    def warn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0345010facfd876213e3ee645c559fc9fdfc44774d7b355274e07db2d57555dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "warn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlogThreshold]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlogThreshold], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlogThreshold],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed00f49e466ba4afcc8014fb654ab34c631b78a933333f34cf113da3bc94d13d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesDiskWatermarks",
    jsii_struct_bases=[],
    name_mapping={"flood_stage": "floodStage", "high": "high", "low": "low"},
)
class ManagedDatabaseOpensearchPropertiesDiskWatermarks:
    def __init__(
        self,
        *,
        flood_stage: typing.Optional[jsii.Number] = None,
        high: typing.Optional[jsii.Number] = None,
        low: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param flood_stage: Flood stage watermark (percentage). The flood stage watermark for disk usage. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#flood_stage ManagedDatabaseOpensearch#flood_stage}
        :param high: High watermark (percentage). The high watermark for disk usage. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#high ManagedDatabaseOpensearch#high}
        :param low: Low watermark (percentage). The low watermark for disk usage. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#low ManagedDatabaseOpensearch#low}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9a670c205c08f4ac01cd4501f4103c0e0bc30f14aa62b77bfae1c27c816ef3d)
            check_type(argname="argument flood_stage", value=flood_stage, expected_type=type_hints["flood_stage"])
            check_type(argname="argument high", value=high, expected_type=type_hints["high"])
            check_type(argname="argument low", value=low, expected_type=type_hints["low"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if flood_stage is not None:
            self._values["flood_stage"] = flood_stage
        if high is not None:
            self._values["high"] = high
        if low is not None:
            self._values["low"] = low

    @builtins.property
    def flood_stage(self) -> typing.Optional[jsii.Number]:
        '''Flood stage watermark (percentage). The flood stage watermark for disk usage.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#flood_stage ManagedDatabaseOpensearch#flood_stage}
        '''
        result = self._values.get("flood_stage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def high(self) -> typing.Optional[jsii.Number]:
        '''High watermark (percentage). The high watermark for disk usage.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#high ManagedDatabaseOpensearch#high}
        '''
        result = self._values.get("high")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def low(self) -> typing.Optional[jsii.Number]:
        '''Low watermark (percentage). The low watermark for disk usage.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#low ManagedDatabaseOpensearch#low}
        '''
        result = self._values.get("low")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesDiskWatermarks(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchPropertiesDiskWatermarksOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesDiskWatermarksOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bf1c6f6948b6ebbff397a49dbd1226357f6783b4078a6ce19039517b616fa315)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetFloodStage")
    def reset_flood_stage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFloodStage", []))

    @jsii.member(jsii_name="resetHigh")
    def reset_high(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHigh", []))

    @jsii.member(jsii_name="resetLow")
    def reset_low(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLow", []))

    @builtins.property
    @jsii.member(jsii_name="floodStageInput")
    def flood_stage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "floodStageInput"))

    @builtins.property
    @jsii.member(jsii_name="highInput")
    def high_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "highInput"))

    @builtins.property
    @jsii.member(jsii_name="lowInput")
    def low_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "lowInput"))

    @builtins.property
    @jsii.member(jsii_name="floodStage")
    def flood_stage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "floodStage"))

    @flood_stage.setter
    def flood_stage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3cf4f285faa268c65a163130a1737433054040990833b9b664b94080736f2c27)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "floodStage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="high")
    def high(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "high"))

    @high.setter
    def high(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__093f7f3025441dad65428b9930e853d6ce7a37fd588398fdf2544d4aebf31edf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "high", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="low")
    def low(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "low"))

    @low.setter
    def low(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9bb2cbe5f289bc789e377337f83f4aa1924821be012296e0578b1d55ed2c495)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "low", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesDiskWatermarks]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesDiskWatermarks], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesDiskWatermarks],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a603893dd48ece901e23fab7bee75233f5a3a69ca14256f14b8be2885cdd82b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesIndexRollup",
    jsii_struct_bases=[],
    name_mapping={
        "rollup_dashboards_enabled": "rollupDashboardsEnabled",
        "rollup_enabled": "rollupEnabled",
        "rollup_search_backoff_count": "rollupSearchBackoffCount",
        "rollup_search_backoff_millis": "rollupSearchBackoffMillis",
        "rollup_search_search_all_jobs": "rollupSearchSearchAllJobs",
    },
)
class ManagedDatabaseOpensearchPropertiesIndexRollup:
    def __init__(
        self,
        *,
        rollup_dashboards_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        rollup_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        rollup_search_backoff_count: typing.Optional[jsii.Number] = None,
        rollup_search_backoff_millis: typing.Optional[jsii.Number] = None,
        rollup_search_search_all_jobs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param rollup_dashboards_enabled: plugins.rollup.dashboards.enabled. Whether rollups are enabled in OpenSearch Dashboards. Defaults to true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#rollup_dashboards_enabled ManagedDatabaseOpensearch#rollup_dashboards_enabled}
        :param rollup_enabled: plugins.rollup.enabled. Whether the rollup plugin is enabled. Defaults to true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#rollup_enabled ManagedDatabaseOpensearch#rollup_enabled}
        :param rollup_search_backoff_count: plugins.rollup.search.backoff_count. How many retries the plugin should attempt for failed rollup jobs. Defaults to 5. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#rollup_search_backoff_count ManagedDatabaseOpensearch#rollup_search_backoff_count}
        :param rollup_search_backoff_millis: plugins.rollup.search.backoff_millis. The backoff time between retries for failed rollup jobs. Defaults to 1000ms. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#rollup_search_backoff_millis ManagedDatabaseOpensearch#rollup_search_backoff_millis}
        :param rollup_search_search_all_jobs: plugins.rollup.search.all_jobs. Whether OpenSearch should return all jobs that match all specified search terms. If disabled, OpenSearch returns just one, as opposed to all, of the jobs that matches the search terms. Defaults to false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#rollup_search_search_all_jobs ManagedDatabaseOpensearch#rollup_search_search_all_jobs}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73e080e9f13ad7c30ec45334431a3eaa752568545186fa7cf689bd26e836d2d3)
            check_type(argname="argument rollup_dashboards_enabled", value=rollup_dashboards_enabled, expected_type=type_hints["rollup_dashboards_enabled"])
            check_type(argname="argument rollup_enabled", value=rollup_enabled, expected_type=type_hints["rollup_enabled"])
            check_type(argname="argument rollup_search_backoff_count", value=rollup_search_backoff_count, expected_type=type_hints["rollup_search_backoff_count"])
            check_type(argname="argument rollup_search_backoff_millis", value=rollup_search_backoff_millis, expected_type=type_hints["rollup_search_backoff_millis"])
            check_type(argname="argument rollup_search_search_all_jobs", value=rollup_search_search_all_jobs, expected_type=type_hints["rollup_search_search_all_jobs"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if rollup_dashboards_enabled is not None:
            self._values["rollup_dashboards_enabled"] = rollup_dashboards_enabled
        if rollup_enabled is not None:
            self._values["rollup_enabled"] = rollup_enabled
        if rollup_search_backoff_count is not None:
            self._values["rollup_search_backoff_count"] = rollup_search_backoff_count
        if rollup_search_backoff_millis is not None:
            self._values["rollup_search_backoff_millis"] = rollup_search_backoff_millis
        if rollup_search_search_all_jobs is not None:
            self._values["rollup_search_search_all_jobs"] = rollup_search_search_all_jobs

    @builtins.property
    def rollup_dashboards_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''plugins.rollup.dashboards.enabled. Whether rollups are enabled in OpenSearch Dashboards. Defaults to true.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#rollup_dashboards_enabled ManagedDatabaseOpensearch#rollup_dashboards_enabled}
        '''
        result = self._values.get("rollup_dashboards_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def rollup_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''plugins.rollup.enabled. Whether the rollup plugin is enabled. Defaults to true.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#rollup_enabled ManagedDatabaseOpensearch#rollup_enabled}
        '''
        result = self._values.get("rollup_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def rollup_search_backoff_count(self) -> typing.Optional[jsii.Number]:
        '''plugins.rollup.search.backoff_count. How many retries the plugin should attempt for failed rollup jobs. Defaults to 5.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#rollup_search_backoff_count ManagedDatabaseOpensearch#rollup_search_backoff_count}
        '''
        result = self._values.get("rollup_search_backoff_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def rollup_search_backoff_millis(self) -> typing.Optional[jsii.Number]:
        '''plugins.rollup.search.backoff_millis. The backoff time between retries for failed rollup jobs. Defaults to 1000ms.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#rollup_search_backoff_millis ManagedDatabaseOpensearch#rollup_search_backoff_millis}
        '''
        result = self._values.get("rollup_search_backoff_millis")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def rollup_search_search_all_jobs(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''plugins.rollup.search.all_jobs. Whether OpenSearch should return all jobs that match all specified search terms. If disabled, OpenSearch returns just one, as opposed to all, of the jobs that matches the search terms. Defaults to false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#rollup_search_search_all_jobs ManagedDatabaseOpensearch#rollup_search_search_all_jobs}
        '''
        result = self._values.get("rollup_search_search_all_jobs")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesIndexRollup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchPropertiesIndexRollupOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesIndexRollupOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e365e9aac6cc1a319fc9231d277e888c9d08fb84bc33dfd4676e14ac5a3e2792)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetRollupDashboardsEnabled")
    def reset_rollup_dashboards_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRollupDashboardsEnabled", []))

    @jsii.member(jsii_name="resetRollupEnabled")
    def reset_rollup_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRollupEnabled", []))

    @jsii.member(jsii_name="resetRollupSearchBackoffCount")
    def reset_rollup_search_backoff_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRollupSearchBackoffCount", []))

    @jsii.member(jsii_name="resetRollupSearchBackoffMillis")
    def reset_rollup_search_backoff_millis(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRollupSearchBackoffMillis", []))

    @jsii.member(jsii_name="resetRollupSearchSearchAllJobs")
    def reset_rollup_search_search_all_jobs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRollupSearchSearchAllJobs", []))

    @builtins.property
    @jsii.member(jsii_name="rollupDashboardsEnabledInput")
    def rollup_dashboards_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "rollupDashboardsEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="rollupEnabledInput")
    def rollup_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "rollupEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="rollupSearchBackoffCountInput")
    def rollup_search_backoff_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "rollupSearchBackoffCountInput"))

    @builtins.property
    @jsii.member(jsii_name="rollupSearchBackoffMillisInput")
    def rollup_search_backoff_millis_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "rollupSearchBackoffMillisInput"))

    @builtins.property
    @jsii.member(jsii_name="rollupSearchSearchAllJobsInput")
    def rollup_search_search_all_jobs_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "rollupSearchSearchAllJobsInput"))

    @builtins.property
    @jsii.member(jsii_name="rollupDashboardsEnabled")
    def rollup_dashboards_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "rollupDashboardsEnabled"))

    @rollup_dashboards_enabled.setter
    def rollup_dashboards_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cdddffb92f343672b638d95d72399987b6afbcb570d66841e49c76e5dbbd9ad9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rollupDashboardsEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rollupEnabled")
    def rollup_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "rollupEnabled"))

    @rollup_enabled.setter
    def rollup_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22ca82987ac8fb9e6089aae6b6e1e31399abcae717d6de93a8018d2f63a9e025)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rollupEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rollupSearchBackoffCount")
    def rollup_search_backoff_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rollupSearchBackoffCount"))

    @rollup_search_backoff_count.setter
    def rollup_search_backoff_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ccb0eadf36f64f36891241b43dce8e4139bc5c1d4c265dac2f7b2066c3f264da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rollupSearchBackoffCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rollupSearchBackoffMillis")
    def rollup_search_backoff_millis(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rollupSearchBackoffMillis"))

    @rollup_search_backoff_millis.setter
    def rollup_search_backoff_millis(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__589fe605a3a57f384029ffd93b26dc6dc0fb7f39c30e6e374de2e8c29a524bff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rollupSearchBackoffMillis", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rollupSearchSearchAllJobs")
    def rollup_search_search_all_jobs(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "rollupSearchSearchAllJobs"))

    @rollup_search_search_all_jobs.setter
    def rollup_search_search_all_jobs(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5e692cd596ade320b01ba6435902b99a0f95fd1902b94cdfed205b2d9945fcf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rollupSearchSearchAllJobs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesIndexRollup]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesIndexRollup], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesIndexRollup],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3de6c360d6b8c8fdc0066e73b3c6b34d637866ecd30541d52ec07debcd855387)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesIndexTemplate",
    jsii_struct_bases=[],
    name_mapping={
        "mapping_nested_objects_limit": "mappingNestedObjectsLimit",
        "number_of_replicas": "numberOfReplicas",
        "number_of_shards": "numberOfShards",
    },
)
class ManagedDatabaseOpensearchPropertiesIndexTemplate:
    def __init__(
        self,
        *,
        mapping_nested_objects_limit: typing.Optional[jsii.Number] = None,
        number_of_replicas: typing.Optional[jsii.Number] = None,
        number_of_shards: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param mapping_nested_objects_limit: index.mapping.nested_objects.limit. The maximum number of nested JSON objects that a single document can contain across all nested types. This limit helps to prevent out of memory errors when a document contains too many nested objects. Default is 10000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#mapping_nested_objects_limit ManagedDatabaseOpensearch#mapping_nested_objects_limit}
        :param number_of_replicas: The number of replicas each primary shard has. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#number_of_replicas ManagedDatabaseOpensearch#number_of_replicas}
        :param number_of_shards: The number of primary shards that an index should have. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#number_of_shards ManagedDatabaseOpensearch#number_of_shards}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__091ebe000c02a1dbf5147d4d6e2e100eaaea7c918311494e9ada1f78674a89e3)
            check_type(argname="argument mapping_nested_objects_limit", value=mapping_nested_objects_limit, expected_type=type_hints["mapping_nested_objects_limit"])
            check_type(argname="argument number_of_replicas", value=number_of_replicas, expected_type=type_hints["number_of_replicas"])
            check_type(argname="argument number_of_shards", value=number_of_shards, expected_type=type_hints["number_of_shards"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if mapping_nested_objects_limit is not None:
            self._values["mapping_nested_objects_limit"] = mapping_nested_objects_limit
        if number_of_replicas is not None:
            self._values["number_of_replicas"] = number_of_replicas
        if number_of_shards is not None:
            self._values["number_of_shards"] = number_of_shards

    @builtins.property
    def mapping_nested_objects_limit(self) -> typing.Optional[jsii.Number]:
        '''index.mapping.nested_objects.limit. The maximum number of nested JSON objects that a single document can contain across all nested types. This limit helps to prevent out of memory errors when a document contains too many nested objects. Default is 10000.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#mapping_nested_objects_limit ManagedDatabaseOpensearch#mapping_nested_objects_limit}
        '''
        result = self._values.get("mapping_nested_objects_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def number_of_replicas(self) -> typing.Optional[jsii.Number]:
        '''The number of replicas each primary shard has.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#number_of_replicas ManagedDatabaseOpensearch#number_of_replicas}
        '''
        result = self._values.get("number_of_replicas")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def number_of_shards(self) -> typing.Optional[jsii.Number]:
        '''The number of primary shards that an index should have.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#number_of_shards ManagedDatabaseOpensearch#number_of_shards}
        '''
        result = self._values.get("number_of_shards")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesIndexTemplate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchPropertiesIndexTemplateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesIndexTemplateOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__80db9e8d6bfffacb73cb1f100468062628a53d92d9dbb8e053b4f82011e7088d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMappingNestedObjectsLimit")
    def reset_mapping_nested_objects_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMappingNestedObjectsLimit", []))

    @jsii.member(jsii_name="resetNumberOfReplicas")
    def reset_number_of_replicas(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumberOfReplicas", []))

    @jsii.member(jsii_name="resetNumberOfShards")
    def reset_number_of_shards(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumberOfShards", []))

    @builtins.property
    @jsii.member(jsii_name="mappingNestedObjectsLimitInput")
    def mapping_nested_objects_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "mappingNestedObjectsLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="numberOfReplicasInput")
    def number_of_replicas_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numberOfReplicasInput"))

    @builtins.property
    @jsii.member(jsii_name="numberOfShardsInput")
    def number_of_shards_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numberOfShardsInput"))

    @builtins.property
    @jsii.member(jsii_name="mappingNestedObjectsLimit")
    def mapping_nested_objects_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "mappingNestedObjectsLimit"))

    @mapping_nested_objects_limit.setter
    def mapping_nested_objects_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9714605aa57197fc59ce6c9f2e363fa7bb5622ebb54ee19ef15e7857c251df97)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mappingNestedObjectsLimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numberOfReplicas")
    def number_of_replicas(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numberOfReplicas"))

    @number_of_replicas.setter
    def number_of_replicas(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99332dc6f1965838c8118775aebd1f65b3d65be63b32bd7b866815bfbe8a3d51)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numberOfReplicas", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numberOfShards")
    def number_of_shards(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numberOfShards"))

    @number_of_shards.setter
    def number_of_shards(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c96ce7acc291c5aaec545dcee6fda8acc85e631432e5aa54434163de41edffe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numberOfShards", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesIndexTemplate]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesIndexTemplate], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesIndexTemplate],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b16dccbd691a6d637fb1fe54be64ca4acfec30c4e49cc9add81d99b41d2f5ea2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesOpenid",
    jsii_struct_bases=[],
    name_mapping={
        "client_id": "clientId",
        "client_secret": "clientSecret",
        "connect_url": "connectUrl",
        "enabled": "enabled",
        "header": "header",
        "jwt_header": "jwtHeader",
        "jwt_url_parameter": "jwtUrlParameter",
        "refresh_rate_limit_count": "refreshRateLimitCount",
        "refresh_rate_limit_time_window_ms": "refreshRateLimitTimeWindowMs",
        "roles_key": "rolesKey",
        "scope": "scope",
        "subject_key": "subjectKey",
    },
)
class ManagedDatabaseOpensearchPropertiesOpenid:
    def __init__(
        self,
        *,
        client_id: typing.Optional[builtins.str] = None,
        client_secret: typing.Optional[builtins.str] = None,
        connect_url: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        header: typing.Optional[builtins.str] = None,
        jwt_header: typing.Optional[builtins.str] = None,
        jwt_url_parameter: typing.Optional[builtins.str] = None,
        refresh_rate_limit_count: typing.Optional[jsii.Number] = None,
        refresh_rate_limit_time_window_ms: typing.Optional[jsii.Number] = None,
        roles_key: typing.Optional[builtins.str] = None,
        scope: typing.Optional[builtins.str] = None,
        subject_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param client_id: The ID of the OpenID Connect client. The ID of the OpenID Connect client configured in your IdP. Required. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#client_id ManagedDatabaseOpensearch#client_id}
        :param client_secret: The client secret of the OpenID Connect. The client secret of the OpenID Connect client configured in your IdP. Required. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#client_secret ManagedDatabaseOpensearch#client_secret}
        :param connect_url: OpenID Connect metadata/configuration URL. The URL of your IdP where the Security plugin can find the OpenID Connect metadata/configuration settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#connect_url ManagedDatabaseOpensearch#connect_url}
        :param enabled: Enable or disable OpenSearch OpenID Connect authentication. Enables or disables OpenID Connect authentication for OpenSearch. When enabled, users can authenticate using OpenID Connect with an Identity Provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        :param header: HTTP header name of the JWT token. HTTP header name of the JWT token. Optional. Default is Authorization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#header ManagedDatabaseOpensearch#header}
        :param jwt_header: The HTTP header that stores the token. The HTTP header that stores the token. Typically the Authorization header with the Bearer schema: Authorization: Bearer . Optional. Default is Authorization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#jwt_header ManagedDatabaseOpensearch#jwt_header}
        :param jwt_url_parameter: URL JWT token. If the token is not transmitted in the HTTP header, but as an URL parameter, define the name of the parameter here. Optional. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#jwt_url_parameter ManagedDatabaseOpensearch#jwt_url_parameter}
        :param refresh_rate_limit_count: The maximum number of unknown key IDs in the time frame. The maximum number of unknown key IDs in the time frame. Default is 10. Optional. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#refresh_rate_limit_count ManagedDatabaseOpensearch#refresh_rate_limit_count}
        :param refresh_rate_limit_time_window_ms: The time frame to use when checking the maximum number of unknown key IDs, in milliseconds. The time frame to use when checking the maximum number of unknown key IDs, in milliseconds. Optional.Default is 10000 (10 seconds). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#refresh_rate_limit_time_window_ms ManagedDatabaseOpensearch#refresh_rate_limit_time_window_ms}
        :param roles_key: The key in the JSON payload that stores the user’s roles. The key in the JSON payload that stores the user’s roles. The value of this key must be a comma-separated list of roles. Required only if you want to use roles in the JWT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#roles_key ManagedDatabaseOpensearch#roles_key}
        :param scope: The scope of the identity token issued by the IdP. The scope of the identity token issued by the IdP. Optional. Default is openid profile email address phone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#scope ManagedDatabaseOpensearch#scope}
        :param subject_key: The key in the JSON payload that stores the user’s name. The key in the JSON payload that stores the user’s name. If not defined, the subject registered claim is used. Most IdP providers use the preferred_username claim. Optional. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#subject_key ManagedDatabaseOpensearch#subject_key}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73c0a3837cca5d07ee0176744b302d89e862a8b39ec6f0e2781b94b27f82af92)
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument client_secret", value=client_secret, expected_type=type_hints["client_secret"])
            check_type(argname="argument connect_url", value=connect_url, expected_type=type_hints["connect_url"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument header", value=header, expected_type=type_hints["header"])
            check_type(argname="argument jwt_header", value=jwt_header, expected_type=type_hints["jwt_header"])
            check_type(argname="argument jwt_url_parameter", value=jwt_url_parameter, expected_type=type_hints["jwt_url_parameter"])
            check_type(argname="argument refresh_rate_limit_count", value=refresh_rate_limit_count, expected_type=type_hints["refresh_rate_limit_count"])
            check_type(argname="argument refresh_rate_limit_time_window_ms", value=refresh_rate_limit_time_window_ms, expected_type=type_hints["refresh_rate_limit_time_window_ms"])
            check_type(argname="argument roles_key", value=roles_key, expected_type=type_hints["roles_key"])
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument subject_key", value=subject_key, expected_type=type_hints["subject_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if client_id is not None:
            self._values["client_id"] = client_id
        if client_secret is not None:
            self._values["client_secret"] = client_secret
        if connect_url is not None:
            self._values["connect_url"] = connect_url
        if enabled is not None:
            self._values["enabled"] = enabled
        if header is not None:
            self._values["header"] = header
        if jwt_header is not None:
            self._values["jwt_header"] = jwt_header
        if jwt_url_parameter is not None:
            self._values["jwt_url_parameter"] = jwt_url_parameter
        if refresh_rate_limit_count is not None:
            self._values["refresh_rate_limit_count"] = refresh_rate_limit_count
        if refresh_rate_limit_time_window_ms is not None:
            self._values["refresh_rate_limit_time_window_ms"] = refresh_rate_limit_time_window_ms
        if roles_key is not None:
            self._values["roles_key"] = roles_key
        if scope is not None:
            self._values["scope"] = scope
        if subject_key is not None:
            self._values["subject_key"] = subject_key

    @builtins.property
    def client_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the OpenID Connect client. The ID of the OpenID Connect client configured in your IdP. Required.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#client_id ManagedDatabaseOpensearch#client_id}
        '''
        result = self._values.get("client_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_secret(self) -> typing.Optional[builtins.str]:
        '''The client secret of the OpenID Connect.

        The client secret of the OpenID Connect client configured in your IdP. Required.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#client_secret ManagedDatabaseOpensearch#client_secret}
        '''
        result = self._values.get("client_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connect_url(self) -> typing.Optional[builtins.str]:
        '''OpenID Connect metadata/configuration URL.

        The URL of your IdP where the Security plugin can find the OpenID Connect metadata/configuration settings.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#connect_url ManagedDatabaseOpensearch#connect_url}
        '''
        result = self._values.get("connect_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable or disable OpenSearch OpenID Connect authentication.

        Enables or disables OpenID Connect authentication for OpenSearch. When enabled, users can authenticate using OpenID Connect with an Identity Provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def header(self) -> typing.Optional[builtins.str]:
        '''HTTP header name of the JWT token. HTTP header name of the JWT token. Optional. Default is Authorization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#header ManagedDatabaseOpensearch#header}
        '''
        result = self._values.get("header")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jwt_header(self) -> typing.Optional[builtins.str]:
        '''The HTTP header that stores the token.

        The HTTP header that stores the token. Typically the Authorization header with the Bearer schema: Authorization: Bearer . Optional. Default is Authorization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#jwt_header ManagedDatabaseOpensearch#jwt_header}
        '''
        result = self._values.get("jwt_header")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jwt_url_parameter(self) -> typing.Optional[builtins.str]:
        '''URL JWT token.

        If the token is not transmitted in the HTTP header, but as an URL parameter, define the name of the parameter here. Optional.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#jwt_url_parameter ManagedDatabaseOpensearch#jwt_url_parameter}
        '''
        result = self._values.get("jwt_url_parameter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def refresh_rate_limit_count(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of unknown key IDs in the time frame.

        The maximum number of unknown key IDs in the time frame. Default is 10. Optional.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#refresh_rate_limit_count ManagedDatabaseOpensearch#refresh_rate_limit_count}
        '''
        result = self._values.get("refresh_rate_limit_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def refresh_rate_limit_time_window_ms(self) -> typing.Optional[jsii.Number]:
        '''The time frame to use when checking the maximum number of unknown key IDs, in milliseconds.

        The time frame to use when checking the maximum number of unknown key IDs, in milliseconds. Optional.Default is 10000 (10 seconds).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#refresh_rate_limit_time_window_ms ManagedDatabaseOpensearch#refresh_rate_limit_time_window_ms}
        '''
        result = self._values.get("refresh_rate_limit_time_window_ms")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def roles_key(self) -> typing.Optional[builtins.str]:
        '''The key in the JSON payload that stores the user’s roles.

        The key in the JSON payload that stores the user’s roles. The value of this key must be a comma-separated list of roles. Required only if you want to use roles in the JWT.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#roles_key ManagedDatabaseOpensearch#roles_key}
        '''
        result = self._values.get("roles_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scope(self) -> typing.Optional[builtins.str]:
        '''The scope of the identity token issued by the IdP.

        The scope of the identity token issued by the IdP. Optional. Default is openid profile email address phone.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#scope ManagedDatabaseOpensearch#scope}
        '''
        result = self._values.get("scope")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subject_key(self) -> typing.Optional[builtins.str]:
        '''The key in the JSON payload that stores the user’s name.

        The key in the JSON payload that stores the user’s name. If not defined, the subject registered claim is used. Most IdP providers use the preferred_username claim. Optional.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#subject_key ManagedDatabaseOpensearch#subject_key}
        '''
        result = self._values.get("subject_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesOpenid(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchPropertiesOpenidOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesOpenidOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f2d1f05510b29d1e71f1ca51d5c296f3e66e489b68f141c0cb11fdf1089181a8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetClientId")
    def reset_client_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientId", []))

    @jsii.member(jsii_name="resetClientSecret")
    def reset_client_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientSecret", []))

    @jsii.member(jsii_name="resetConnectUrl")
    def reset_connect_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectUrl", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetHeader")
    def reset_header(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeader", []))

    @jsii.member(jsii_name="resetJwtHeader")
    def reset_jwt_header(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJwtHeader", []))

    @jsii.member(jsii_name="resetJwtUrlParameter")
    def reset_jwt_url_parameter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJwtUrlParameter", []))

    @jsii.member(jsii_name="resetRefreshRateLimitCount")
    def reset_refresh_rate_limit_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRefreshRateLimitCount", []))

    @jsii.member(jsii_name="resetRefreshRateLimitTimeWindowMs")
    def reset_refresh_rate_limit_time_window_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRefreshRateLimitTimeWindowMs", []))

    @jsii.member(jsii_name="resetRolesKey")
    def reset_roles_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRolesKey", []))

    @jsii.member(jsii_name="resetScope")
    def reset_scope(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScope", []))

    @jsii.member(jsii_name="resetSubjectKey")
    def reset_subject_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubjectKey", []))

    @builtins.property
    @jsii.member(jsii_name="clientIdInput")
    def client_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientIdInput"))

    @builtins.property
    @jsii.member(jsii_name="clientSecretInput")
    def client_secret_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientSecretInput"))

    @builtins.property
    @jsii.member(jsii_name="connectUrlInput")
    def connect_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="headerInput")
    def header_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "headerInput"))

    @builtins.property
    @jsii.member(jsii_name="jwtHeaderInput")
    def jwt_header_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jwtHeaderInput"))

    @builtins.property
    @jsii.member(jsii_name="jwtUrlParameterInput")
    def jwt_url_parameter_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jwtUrlParameterInput"))

    @builtins.property
    @jsii.member(jsii_name="refreshRateLimitCountInput")
    def refresh_rate_limit_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "refreshRateLimitCountInput"))

    @builtins.property
    @jsii.member(jsii_name="refreshRateLimitTimeWindowMsInput")
    def refresh_rate_limit_time_window_ms_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "refreshRateLimitTimeWindowMsInput"))

    @builtins.property
    @jsii.member(jsii_name="rolesKeyInput")
    def roles_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rolesKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="scopeInput")
    def scope_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scopeInput"))

    @builtins.property
    @jsii.member(jsii_name="subjectKeyInput")
    def subject_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subjectKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientId"))

    @client_id.setter
    def client_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa7261a89918dbfb9f50fa9dfae42227fb7412ceab80b7a8b982e2db47c07f02)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientSecret")
    def client_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientSecret"))

    @client_secret.setter
    def client_secret(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__699da58a3d40107a39d2119729ecbb14aaeff7207705a003c1357d842dc1ea48)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientSecret", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="connectUrl")
    def connect_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectUrl"))

    @connect_url.setter
    def connect_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e90a34de40e81274f86eb828ee2b88ed8bbf5ef9e0814fc5f8f5486266be9f71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00987cb520a1f1a0ea820dcfda52b67895e8d1b1f813300c1440cda0e27f1139)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="header")
    def header(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "header"))

    @header.setter
    def header(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f9bf04854b7ff6094b1426fa9ec13b04739a31f9863bbbcb53eec2116cdbafc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "header", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jwtHeader")
    def jwt_header(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jwtHeader"))

    @jwt_header.setter
    def jwt_header(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3decaf18072bd601d7198339380575ee2070f319206ca5742d1ca686393ca774)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jwtHeader", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jwtUrlParameter")
    def jwt_url_parameter(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jwtUrlParameter"))

    @jwt_url_parameter.setter
    def jwt_url_parameter(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a9e04be6387363a6fb27928afe6e422ba0787832599b73c3798bded4bbbeaa7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jwtUrlParameter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="refreshRateLimitCount")
    def refresh_rate_limit_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "refreshRateLimitCount"))

    @refresh_rate_limit_count.setter
    def refresh_rate_limit_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f125200f527ffbb5e3cbc957fcf1254d0f49b7bc28cc54daf6b9114de79a999e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "refreshRateLimitCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="refreshRateLimitTimeWindowMs")
    def refresh_rate_limit_time_window_ms(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "refreshRateLimitTimeWindowMs"))

    @refresh_rate_limit_time_window_ms.setter
    def refresh_rate_limit_time_window_ms(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58b2b1fdb72bb20c47f3f3da6e88eb14a71ad8399fe12a1f255177f46d28dfec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "refreshRateLimitTimeWindowMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rolesKey")
    def roles_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rolesKey"))

    @roles_key.setter
    def roles_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e308c3ca6ee25c5414c9c3b5b5add06951a6a78c7783c033bd7d39f387c28a89)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rolesKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scope")
    def scope(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scope"))

    @scope.setter
    def scope(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5cedd7c2ad307531bb92f92c1dc2b02714e9a953ac794098ab5e972da769fb7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scope", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subjectKey")
    def subject_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subjectKey"))

    @subject_key.setter
    def subject_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2e8077939eb6e386d424c3909093dc0fd2f5595c3f150af06f218539a68a082)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subjectKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesOpenid]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesOpenid], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesOpenid],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a06c0f82afb429010a7bf11d739c6e615490b1602601145c983041209f49f06)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesOpensearchDashboards",
    jsii_struct_bases=[],
    name_mapping={
        "enabled": "enabled",
        "max_old_space_size": "maxOldSpaceSize",
        "multiple_data_source_enabled": "multipleDataSourceEnabled",
        "opensearch_request_timeout": "opensearchRequestTimeout",
    },
)
class ManagedDatabaseOpensearchPropertiesOpensearchDashboards:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_old_space_size: typing.Optional[jsii.Number] = None,
        multiple_data_source_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        opensearch_request_timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param enabled: Enable or disable OpenSearch Dashboards. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        :param max_old_space_size: Limits the maximum amount of memory (in MiB) the OpenSearch Dashboards process can use. This sets the max_old_space_size option of the nodejs running the OpenSearch Dashboards. Note: the memory reserved by OpenSearch Dashboards is not available for OpenSearch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#max_old_space_size ManagedDatabaseOpensearch#max_old_space_size}
        :param multiple_data_source_enabled: Enable or disable multiple data sources in OpenSearch Dashboards. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#multiple_data_source_enabled ManagedDatabaseOpensearch#multiple_data_source_enabled}
        :param opensearch_request_timeout: Timeout in milliseconds for requests made by OpenSearch Dashboards towards OpenSearch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#opensearch_request_timeout ManagedDatabaseOpensearch#opensearch_request_timeout}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c02ebecf926c4894c4481fd34c44a4f69278e1e4c9c78e3ec30f9d08a36971c3)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument max_old_space_size", value=max_old_space_size, expected_type=type_hints["max_old_space_size"])
            check_type(argname="argument multiple_data_source_enabled", value=multiple_data_source_enabled, expected_type=type_hints["multiple_data_source_enabled"])
            check_type(argname="argument opensearch_request_timeout", value=opensearch_request_timeout, expected_type=type_hints["opensearch_request_timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if max_old_space_size is not None:
            self._values["max_old_space_size"] = max_old_space_size
        if multiple_data_source_enabled is not None:
            self._values["multiple_data_source_enabled"] = multiple_data_source_enabled
        if opensearch_request_timeout is not None:
            self._values["opensearch_request_timeout"] = opensearch_request_timeout

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable or disable OpenSearch Dashboards.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def max_old_space_size(self) -> typing.Optional[jsii.Number]:
        '''Limits the maximum amount of memory (in MiB) the OpenSearch Dashboards process can use.

        This sets the max_old_space_size option of the nodejs running the OpenSearch Dashboards. Note: the memory reserved by OpenSearch Dashboards is not available for OpenSearch.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#max_old_space_size ManagedDatabaseOpensearch#max_old_space_size}
        '''
        result = self._values.get("max_old_space_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def multiple_data_source_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable or disable multiple data sources in OpenSearch Dashboards.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#multiple_data_source_enabled ManagedDatabaseOpensearch#multiple_data_source_enabled}
        '''
        result = self._values.get("multiple_data_source_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def opensearch_request_timeout(self) -> typing.Optional[jsii.Number]:
        '''Timeout in milliseconds for requests made by OpenSearch Dashboards towards OpenSearch.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#opensearch_request_timeout ManagedDatabaseOpensearch#opensearch_request_timeout}
        '''
        result = self._values.get("opensearch_request_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesOpensearchDashboards(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchPropertiesOpensearchDashboardsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesOpensearchDashboardsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__46269da753bb4825eb2d2eb52d1679232eb04b442c74f7cafddf4cf14945aec0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetMaxOldSpaceSize")
    def reset_max_old_space_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxOldSpaceSize", []))

    @jsii.member(jsii_name="resetMultipleDataSourceEnabled")
    def reset_multiple_data_source_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMultipleDataSourceEnabled", []))

    @jsii.member(jsii_name="resetOpensearchRequestTimeout")
    def reset_opensearch_request_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpensearchRequestTimeout", []))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="maxOldSpaceSizeInput")
    def max_old_space_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxOldSpaceSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="multipleDataSourceEnabledInput")
    def multiple_data_source_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "multipleDataSourceEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="opensearchRequestTimeoutInput")
    def opensearch_request_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "opensearchRequestTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1019ad4a6f0e57b8f798e7a399405937723d4cbd1b0109900787a017b35b7f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxOldSpaceSize")
    def max_old_space_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxOldSpaceSize"))

    @max_old_space_size.setter
    def max_old_space_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15484f5f1d02602bd803336a02543fef580fed4327eeca3c32e0e19880cb41a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxOldSpaceSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="multipleDataSourceEnabled")
    def multiple_data_source_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "multipleDataSourceEnabled"))

    @multiple_data_source_enabled.setter
    def multiple_data_source_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d40ab4d7811997e535f4f7ddf3e45b333ebefa915dcae062cef05fc5d07b8711)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "multipleDataSourceEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="opensearchRequestTimeout")
    def opensearch_request_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "opensearchRequestTimeout"))

    @opensearch_request_timeout.setter
    def opensearch_request_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39f2bb44168338b5f62f27d6c68aa85795f001b64ec8ee27ccfd05945977e24a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "opensearchRequestTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesOpensearchDashboards]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesOpensearchDashboards], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesOpensearchDashboards],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__642b1eeba71d0c8859ae09897efcd46c46a7f3266c413676870e000d26269bab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ManagedDatabaseOpensearchPropertiesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__751155185e1458cf144b0b3f995bffe965d316250c0fff7682404038d0582237)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAuthFailureListeners")
    def put_auth_failure_listeners(
        self,
        *,
        internal_authentication_backend_limiting: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param internal_authentication_backend_limiting: internal_authentication_backend_limiting block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#internal_authentication_backend_limiting ManagedDatabaseOpensearch#internal_authentication_backend_limiting}
        '''
        value = ManagedDatabaseOpensearchPropertiesAuthFailureListeners(
            internal_authentication_backend_limiting=internal_authentication_backend_limiting,
        )

        return typing.cast(None, jsii.invoke(self, "putAuthFailureListeners", [value]))

    @jsii.member(jsii_name="putClusterRemoteStore")
    def put_cluster_remote_store(
        self,
        *,
        state_global_metadata_upload_timeout: typing.Optional[builtins.str] = None,
        state_metadata_manifest_upload_timeout: typing.Optional[builtins.str] = None,
        translog_buffer_interval: typing.Optional[builtins.str] = None,
        translog_max_readers: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param state_global_metadata_upload_timeout: The amount of time to wait for the cluster state upload to complete. The amount of time to wait for the cluster state upload to complete. Defaults to 20s. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#state_global_metadata_upload_timeout ManagedDatabaseOpensearch#state_global_metadata_upload_timeout}
        :param state_metadata_manifest_upload_timeout: The amount of time to wait for the manifest file upload to complete. The amount of time to wait for the manifest file upload to complete. The manifest file contains the details of each of the files uploaded for a single cluster state, both index metadata files and global metadata files. Defaults to 20s. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#state_metadata_manifest_upload_timeout ManagedDatabaseOpensearch#state_metadata_manifest_upload_timeout}
        :param translog_buffer_interval: The default value of the translog buffer interval. The default value of the translog buffer interval used when performing periodic translog updates. This setting is only effective when the index setting ``index.remote_store.translog.buffer_interval`` is not present. Defaults to 650ms. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#translog_buffer_interval ManagedDatabaseOpensearch#translog_buffer_interval}
        :param translog_max_readers: The maximum number of open translog files for remote-backed indexes. Sets the maximum number of open translog files for remote-backed indexes. This limits the total number of translog files per shard. After reaching this limit, the remote store flushes the translog files. Default is 1000. The minimum required is 100. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#translog_max_readers ManagedDatabaseOpensearch#translog_max_readers}
        '''
        value = ManagedDatabaseOpensearchPropertiesClusterRemoteStore(
            state_global_metadata_upload_timeout=state_global_metadata_upload_timeout,
            state_metadata_manifest_upload_timeout=state_metadata_manifest_upload_timeout,
            translog_buffer_interval=translog_buffer_interval,
            translog_max_readers=translog_max_readers,
        )

        return typing.cast(None, jsii.invoke(self, "putClusterRemoteStore", [value]))

    @jsii.member(jsii_name="putClusterSearchRequestSlowlog")
    def put_cluster_search_request_slowlog(
        self,
        *,
        level: typing.Optional[builtins.str] = None,
        threshold: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlogThreshold, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param level: Log level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#level ManagedDatabaseOpensearch#level}
        :param threshold: threshold block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#threshold ManagedDatabaseOpensearch#threshold}
        '''
        value = ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlog(
            level=level, threshold=threshold
        )

        return typing.cast(None, jsii.invoke(self, "putClusterSearchRequestSlowlog", [value]))

    @jsii.member(jsii_name="putDiskWatermarks")
    def put_disk_watermarks(
        self,
        *,
        flood_stage: typing.Optional[jsii.Number] = None,
        high: typing.Optional[jsii.Number] = None,
        low: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param flood_stage: Flood stage watermark (percentage). The flood stage watermark for disk usage. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#flood_stage ManagedDatabaseOpensearch#flood_stage}
        :param high: High watermark (percentage). The high watermark for disk usage. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#high ManagedDatabaseOpensearch#high}
        :param low: Low watermark (percentage). The low watermark for disk usage. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#low ManagedDatabaseOpensearch#low}
        '''
        value = ManagedDatabaseOpensearchPropertiesDiskWatermarks(
            flood_stage=flood_stage, high=high, low=low
        )

        return typing.cast(None, jsii.invoke(self, "putDiskWatermarks", [value]))

    @jsii.member(jsii_name="putIndexRollup")
    def put_index_rollup(
        self,
        *,
        rollup_dashboards_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        rollup_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        rollup_search_backoff_count: typing.Optional[jsii.Number] = None,
        rollup_search_backoff_millis: typing.Optional[jsii.Number] = None,
        rollup_search_search_all_jobs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param rollup_dashboards_enabled: plugins.rollup.dashboards.enabled. Whether rollups are enabled in OpenSearch Dashboards. Defaults to true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#rollup_dashboards_enabled ManagedDatabaseOpensearch#rollup_dashboards_enabled}
        :param rollup_enabled: plugins.rollup.enabled. Whether the rollup plugin is enabled. Defaults to true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#rollup_enabled ManagedDatabaseOpensearch#rollup_enabled}
        :param rollup_search_backoff_count: plugins.rollup.search.backoff_count. How many retries the plugin should attempt for failed rollup jobs. Defaults to 5. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#rollup_search_backoff_count ManagedDatabaseOpensearch#rollup_search_backoff_count}
        :param rollup_search_backoff_millis: plugins.rollup.search.backoff_millis. The backoff time between retries for failed rollup jobs. Defaults to 1000ms. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#rollup_search_backoff_millis ManagedDatabaseOpensearch#rollup_search_backoff_millis}
        :param rollup_search_search_all_jobs: plugins.rollup.search.all_jobs. Whether OpenSearch should return all jobs that match all specified search terms. If disabled, OpenSearch returns just one, as opposed to all, of the jobs that matches the search terms. Defaults to false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#rollup_search_search_all_jobs ManagedDatabaseOpensearch#rollup_search_search_all_jobs}
        '''
        value = ManagedDatabaseOpensearchPropertiesIndexRollup(
            rollup_dashboards_enabled=rollup_dashboards_enabled,
            rollup_enabled=rollup_enabled,
            rollup_search_backoff_count=rollup_search_backoff_count,
            rollup_search_backoff_millis=rollup_search_backoff_millis,
            rollup_search_search_all_jobs=rollup_search_search_all_jobs,
        )

        return typing.cast(None, jsii.invoke(self, "putIndexRollup", [value]))

    @jsii.member(jsii_name="putIndexTemplate")
    def put_index_template(
        self,
        *,
        mapping_nested_objects_limit: typing.Optional[jsii.Number] = None,
        number_of_replicas: typing.Optional[jsii.Number] = None,
        number_of_shards: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param mapping_nested_objects_limit: index.mapping.nested_objects.limit. The maximum number of nested JSON objects that a single document can contain across all nested types. This limit helps to prevent out of memory errors when a document contains too many nested objects. Default is 10000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#mapping_nested_objects_limit ManagedDatabaseOpensearch#mapping_nested_objects_limit}
        :param number_of_replicas: The number of replicas each primary shard has. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#number_of_replicas ManagedDatabaseOpensearch#number_of_replicas}
        :param number_of_shards: The number of primary shards that an index should have. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#number_of_shards ManagedDatabaseOpensearch#number_of_shards}
        '''
        value = ManagedDatabaseOpensearchPropertiesIndexTemplate(
            mapping_nested_objects_limit=mapping_nested_objects_limit,
            number_of_replicas=number_of_replicas,
            number_of_shards=number_of_shards,
        )

        return typing.cast(None, jsii.invoke(self, "putIndexTemplate", [value]))

    @jsii.member(jsii_name="putOpenid")
    def put_openid(
        self,
        *,
        client_id: typing.Optional[builtins.str] = None,
        client_secret: typing.Optional[builtins.str] = None,
        connect_url: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        header: typing.Optional[builtins.str] = None,
        jwt_header: typing.Optional[builtins.str] = None,
        jwt_url_parameter: typing.Optional[builtins.str] = None,
        refresh_rate_limit_count: typing.Optional[jsii.Number] = None,
        refresh_rate_limit_time_window_ms: typing.Optional[jsii.Number] = None,
        roles_key: typing.Optional[builtins.str] = None,
        scope: typing.Optional[builtins.str] = None,
        subject_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param client_id: The ID of the OpenID Connect client. The ID of the OpenID Connect client configured in your IdP. Required. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#client_id ManagedDatabaseOpensearch#client_id}
        :param client_secret: The client secret of the OpenID Connect. The client secret of the OpenID Connect client configured in your IdP. Required. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#client_secret ManagedDatabaseOpensearch#client_secret}
        :param connect_url: OpenID Connect metadata/configuration URL. The URL of your IdP where the Security plugin can find the OpenID Connect metadata/configuration settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#connect_url ManagedDatabaseOpensearch#connect_url}
        :param enabled: Enable or disable OpenSearch OpenID Connect authentication. Enables or disables OpenID Connect authentication for OpenSearch. When enabled, users can authenticate using OpenID Connect with an Identity Provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        :param header: HTTP header name of the JWT token. HTTP header name of the JWT token. Optional. Default is Authorization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#header ManagedDatabaseOpensearch#header}
        :param jwt_header: The HTTP header that stores the token. The HTTP header that stores the token. Typically the Authorization header with the Bearer schema: Authorization: Bearer . Optional. Default is Authorization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#jwt_header ManagedDatabaseOpensearch#jwt_header}
        :param jwt_url_parameter: URL JWT token. If the token is not transmitted in the HTTP header, but as an URL parameter, define the name of the parameter here. Optional. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#jwt_url_parameter ManagedDatabaseOpensearch#jwt_url_parameter}
        :param refresh_rate_limit_count: The maximum number of unknown key IDs in the time frame. The maximum number of unknown key IDs in the time frame. Default is 10. Optional. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#refresh_rate_limit_count ManagedDatabaseOpensearch#refresh_rate_limit_count}
        :param refresh_rate_limit_time_window_ms: The time frame to use when checking the maximum number of unknown key IDs, in milliseconds. The time frame to use when checking the maximum number of unknown key IDs, in milliseconds. Optional.Default is 10000 (10 seconds). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#refresh_rate_limit_time_window_ms ManagedDatabaseOpensearch#refresh_rate_limit_time_window_ms}
        :param roles_key: The key in the JSON payload that stores the user’s roles. The key in the JSON payload that stores the user’s roles. The value of this key must be a comma-separated list of roles. Required only if you want to use roles in the JWT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#roles_key ManagedDatabaseOpensearch#roles_key}
        :param scope: The scope of the identity token issued by the IdP. The scope of the identity token issued by the IdP. Optional. Default is openid profile email address phone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#scope ManagedDatabaseOpensearch#scope}
        :param subject_key: The key in the JSON payload that stores the user’s name. The key in the JSON payload that stores the user’s name. If not defined, the subject registered claim is used. Most IdP providers use the preferred_username claim. Optional. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#subject_key ManagedDatabaseOpensearch#subject_key}
        '''
        value = ManagedDatabaseOpensearchPropertiesOpenid(
            client_id=client_id,
            client_secret=client_secret,
            connect_url=connect_url,
            enabled=enabled,
            header=header,
            jwt_header=jwt_header,
            jwt_url_parameter=jwt_url_parameter,
            refresh_rate_limit_count=refresh_rate_limit_count,
            refresh_rate_limit_time_window_ms=refresh_rate_limit_time_window_ms,
            roles_key=roles_key,
            scope=scope,
            subject_key=subject_key,
        )

        return typing.cast(None, jsii.invoke(self, "putOpenid", [value]))

    @jsii.member(jsii_name="putOpensearchDashboards")
    def put_opensearch_dashboards(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_old_space_size: typing.Optional[jsii.Number] = None,
        multiple_data_source_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        opensearch_request_timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param enabled: Enable or disable OpenSearch Dashboards. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        :param max_old_space_size: Limits the maximum amount of memory (in MiB) the OpenSearch Dashboards process can use. This sets the max_old_space_size option of the nodejs running the OpenSearch Dashboards. Note: the memory reserved by OpenSearch Dashboards is not available for OpenSearch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#max_old_space_size ManagedDatabaseOpensearch#max_old_space_size}
        :param multiple_data_source_enabled: Enable or disable multiple data sources in OpenSearch Dashboards. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#multiple_data_source_enabled ManagedDatabaseOpensearch#multiple_data_source_enabled}
        :param opensearch_request_timeout: Timeout in milliseconds for requests made by OpenSearch Dashboards towards OpenSearch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#opensearch_request_timeout ManagedDatabaseOpensearch#opensearch_request_timeout}
        '''
        value = ManagedDatabaseOpensearchPropertiesOpensearchDashboards(
            enabled=enabled,
            max_old_space_size=max_old_space_size,
            multiple_data_source_enabled=multiple_data_source_enabled,
            opensearch_request_timeout=opensearch_request_timeout,
        )

        return typing.cast(None, jsii.invoke(self, "putOpensearchDashboards", [value]))

    @jsii.member(jsii_name="putRemoteStore")
    def put_remote_store(
        self,
        *,
        segment_pressure_bytes_lag_variance_factor: typing.Optional[jsii.Number] = None,
        segment_pressure_consecutive_failures_limit: typing.Optional[jsii.Number] = None,
        segment_pressure_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        segment_pressure_time_lag_variance_factor: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param segment_pressure_bytes_lag_variance_factor: The variance factor that is used to calculate the dynamic bytes lag threshold. The variance factor that is used together with the moving average to calculate the dynamic bytes lag threshold for activating remote segment backpressure. Defaults to 10. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#segment_pressure_bytes_lag_variance_factor ManagedDatabaseOpensearch#segment_pressure_bytes_lag_variance_factor}
        :param segment_pressure_consecutive_failures_limit: The minimum consecutive failure count for activating remote segment backpressure. The minimum consecutive failure count for activating remote segment backpressure. Defaults to 5. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#segment_pressure_consecutive_failures_limit ManagedDatabaseOpensearch#segment_pressure_consecutive_failures_limit}
        :param segment_pressure_enabled: Enables remote segment backpressure. Enables remote segment backpressure. Default is ``true``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#segment_pressure_enabled ManagedDatabaseOpensearch#segment_pressure_enabled}
        :param segment_pressure_time_lag_variance_factor: The variance factor that is used to calculate the dynamic bytes lag threshold. The variance factor that is used together with the moving average to calculate the dynamic time lag threshold for activating remote segment backpressure. Defaults to 10. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#segment_pressure_time_lag_variance_factor ManagedDatabaseOpensearch#segment_pressure_time_lag_variance_factor}
        '''
        value = ManagedDatabaseOpensearchPropertiesRemoteStore(
            segment_pressure_bytes_lag_variance_factor=segment_pressure_bytes_lag_variance_factor,
            segment_pressure_consecutive_failures_limit=segment_pressure_consecutive_failures_limit,
            segment_pressure_enabled=segment_pressure_enabled,
            segment_pressure_time_lag_variance_factor=segment_pressure_time_lag_variance_factor,
        )

        return typing.cast(None, jsii.invoke(self, "putRemoteStore", [value]))

    @jsii.member(jsii_name="putSaml")
    def put_saml(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        idp_entity_id: typing.Optional[builtins.str] = None,
        idp_metadata_url: typing.Optional[builtins.str] = None,
        idp_pemtrustedcas_content: typing.Optional[builtins.str] = None,
        roles_key: typing.Optional[builtins.str] = None,
        sp_entity_id: typing.Optional[builtins.str] = None,
        subject_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Enable or disable OpenSearch SAML authentication. Enables or disables SAML-based authentication for OpenSearch. When enabled, users can authenticate using SAML with an Identity Provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        :param idp_entity_id: Identity Provider Entity ID. The unique identifier for the Identity Provider (IdP) entity that is used for SAML authentication. This value is typically provided by the IdP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#idp_entity_id ManagedDatabaseOpensearch#idp_entity_id}
        :param idp_metadata_url: Identity Provider (IdP) SAML metadata URL. The URL of the SAML metadata for the Identity Provider (IdP). This is used to configure SAML-based authentication with the IdP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#idp_metadata_url ManagedDatabaseOpensearch#idp_metadata_url}
        :param idp_pemtrustedcas_content: PEM-encoded root CA Content for SAML IdP server verification. This parameter specifies the PEM-encoded root certificate authority (CA) content for the SAML identity provider (IdP) server verification. The root CA content is used to verify the SSL/TLS certificate presented by the server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#idp_pemtrustedcas_content ManagedDatabaseOpensearch#idp_pemtrustedcas_content}
        :param roles_key: SAML response role attribute. Optional. Specifies the attribute in the SAML response where role information is stored, if available. Role attributes are not required for SAML authentication, but can be included in SAML assertions by most Identity Providers (IdPs) to determine user access levels or permissions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#roles_key ManagedDatabaseOpensearch#roles_key}
        :param sp_entity_id: Service Provider Entity ID. The unique identifier for the Service Provider (SP) entity that is used for SAML authentication. This value is typically provided by the SP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#sp_entity_id ManagedDatabaseOpensearch#sp_entity_id}
        :param subject_key: SAML response subject attribute. Optional. Specifies the attribute in the SAML response where the subject identifier is stored. If not configured, the NameID attribute is used by default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#subject_key ManagedDatabaseOpensearch#subject_key}
        '''
        value = ManagedDatabaseOpensearchPropertiesSaml(
            enabled=enabled,
            idp_entity_id=idp_entity_id,
            idp_metadata_url=idp_metadata_url,
            idp_pemtrustedcas_content=idp_pemtrustedcas_content,
            roles_key=roles_key,
            sp_entity_id=sp_entity_id,
            subject_key=subject_key,
        )

        return typing.cast(None, jsii.invoke(self, "putSaml", [value]))

    @jsii.member(jsii_name="putSearchBackpressure")
    def put_search_backpressure(
        self,
        *,
        mode: typing.Optional[builtins.str] = None,
        node_duress: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesSearchBackpressureNodeDuress", typing.Dict[builtins.str, typing.Any]]] = None,
        search_shard_task: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchShardTask", typing.Dict[builtins.str, typing.Any]]] = None,
        search_task: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchTask", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param mode: The search backpressure mode. The search backpressure mode. Valid values are monitor_only, enforced, or disabled. Default is monitor_only. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#mode ManagedDatabaseOpensearch#mode}
        :param node_duress: node_duress block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#node_duress ManagedDatabaseOpensearch#node_duress}
        :param search_shard_task: search_shard_task block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#search_shard_task ManagedDatabaseOpensearch#search_shard_task}
        :param search_task: search_task block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#search_task ManagedDatabaseOpensearch#search_task}
        '''
        value = ManagedDatabaseOpensearchPropertiesSearchBackpressure(
            mode=mode,
            node_duress=node_duress,
            search_shard_task=search_shard_task,
            search_task=search_task,
        )

        return typing.cast(None, jsii.invoke(self, "putSearchBackpressure", [value]))

    @jsii.member(jsii_name="putSearchInsightsTopQueries")
    def put_search_insights_top_queries(
        self,
        *,
        cpu: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesCpu", typing.Dict[builtins.str, typing.Any]]] = None,
        latency: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesLatency", typing.Dict[builtins.str, typing.Any]]] = None,
        memory: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesMemory", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param cpu: cpu block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cpu ManagedDatabaseOpensearch#cpu}
        :param latency: latency block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#latency ManagedDatabaseOpensearch#latency}
        :param memory: memory block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#memory ManagedDatabaseOpensearch#memory}
        '''
        value = ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueries(
            cpu=cpu, latency=latency, memory=memory
        )

        return typing.cast(None, jsii.invoke(self, "putSearchInsightsTopQueries", [value]))

    @jsii.member(jsii_name="putSegrep")
    def put_segrep(
        self,
        *,
        pressure_checkpoint_limit: typing.Optional[jsii.Number] = None,
        pressure_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        pressure_replica_stale_limit: typing.Optional[jsii.Number] = None,
        pressure_time_limit: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param pressure_checkpoint_limit: The maximum number of indexing checkpoints that a replica shard can fall behind when copying from primary. Once ``segrep.pressure.checkpoint.limit`` is breached along with ``segrep.pressure.time.limit``, the segment replication backpressure mechanism is initiated. Default is 4 checkpoints. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#pressure_checkpoint_limit ManagedDatabaseOpensearch#pressure_checkpoint_limit}
        :param pressure_enabled: Enables the segment replication backpressure mechanism. Default is false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#pressure_enabled ManagedDatabaseOpensearch#pressure_enabled}
        :param pressure_replica_stale_limit: The maximum number of stale replica shards that can exist in a replication group. Once ``segrep.pressure.replica.stale.limit`` is breached, the segment replication backpressure mechanism is initiated. Default is .5, which is 50% of a replication group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#pressure_replica_stale_limit ManagedDatabaseOpensearch#pressure_replica_stale_limit}
        :param pressure_time_limit: The maximum amount of time that a replica shard can take to copy from the primary shard. Once segrep.pressure.time.limit is breached along with segrep.pressure.checkpoint.limit, the segment replication backpressure mechanism is initiated. Default is 5 minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#pressure_time_limit ManagedDatabaseOpensearch#pressure_time_limit}
        '''
        value = ManagedDatabaseOpensearchPropertiesSegrep(
            pressure_checkpoint_limit=pressure_checkpoint_limit,
            pressure_enabled=pressure_enabled,
            pressure_replica_stale_limit=pressure_replica_stale_limit,
            pressure_time_limit=pressure_time_limit,
        )

        return typing.cast(None, jsii.invoke(self, "putSegrep", [value]))

    @jsii.member(jsii_name="putShardIndexingPressure")
    def put_shard_indexing_pressure(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enforced: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        operating_factor: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesShardIndexingPressureOperatingFactor", typing.Dict[builtins.str, typing.Any]]] = None,
        primary_parameter: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameter", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param enabled: Enable or disable shard indexing backpressure. Enable or disable shard indexing backpressure. Default is false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        :param enforced: Run shard indexing backpressure in shadow mode or enforced mode. Run shard indexing backpressure in shadow mode or enforced mode. In shadow mode (value set as false), shard indexing backpressure tracks all granular-level metrics, but it doesn’t actually reject any indexing requests. In enforced mode (value set as true), shard indexing backpressure rejects any requests to the cluster that might cause a dip in its performance. Default is false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enforced ManagedDatabaseOpensearch#enforced}
        :param operating_factor: operating_factor block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#operating_factor ManagedDatabaseOpensearch#operating_factor}
        :param primary_parameter: primary_parameter block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#primary_parameter ManagedDatabaseOpensearch#primary_parameter}
        '''
        value = ManagedDatabaseOpensearchPropertiesShardIndexingPressure(
            enabled=enabled,
            enforced=enforced,
            operating_factor=operating_factor,
            primary_parameter=primary_parameter,
        )

        return typing.cast(None, jsii.invoke(self, "putShardIndexingPressure", [value]))

    @jsii.member(jsii_name="resetActionAutoCreateIndexEnabled")
    def reset_action_auto_create_index_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActionAutoCreateIndexEnabled", []))

    @jsii.member(jsii_name="resetActionDestructiveRequiresName")
    def reset_action_destructive_requires_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActionDestructiveRequiresName", []))

    @jsii.member(jsii_name="resetAuthFailureListeners")
    def reset_auth_failure_listeners(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthFailureListeners", []))

    @jsii.member(jsii_name="resetAutomaticUtilityNetworkIpFilter")
    def reset_automatic_utility_network_ip_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutomaticUtilityNetworkIpFilter", []))

    @jsii.member(jsii_name="resetClusterFilecacheRemoteDataRatio")
    def reset_cluster_filecache_remote_data_ratio(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterFilecacheRemoteDataRatio", []))

    @jsii.member(jsii_name="resetClusterMaxShardsPerNode")
    def reset_cluster_max_shards_per_node(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterMaxShardsPerNode", []))

    @jsii.member(jsii_name="resetClusterRemoteStore")
    def reset_cluster_remote_store(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterRemoteStore", []))

    @jsii.member(jsii_name="resetClusterRoutingAllocationBalancePreferPrimary")
    def reset_cluster_routing_allocation_balance_prefer_primary(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterRoutingAllocationBalancePreferPrimary", []))

    @jsii.member(jsii_name="resetClusterRoutingAllocationNodeConcurrentRecoveries")
    def reset_cluster_routing_allocation_node_concurrent_recoveries(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterRoutingAllocationNodeConcurrentRecoveries", []))

    @jsii.member(jsii_name="resetClusterSearchRequestSlowlog")
    def reset_cluster_search_request_slowlog(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterSearchRequestSlowlog", []))

    @jsii.member(jsii_name="resetCustomDomain")
    def reset_custom_domain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomDomain", []))

    @jsii.member(jsii_name="resetDiskWatermarks")
    def reset_disk_watermarks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskWatermarks", []))

    @jsii.member(jsii_name="resetElasticsearchVersion")
    def reset_elasticsearch_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetElasticsearchVersion", []))

    @jsii.member(jsii_name="resetEmailSenderName")
    def reset_email_sender_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailSenderName", []))

    @jsii.member(jsii_name="resetEmailSenderPassword")
    def reset_email_sender_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailSenderPassword", []))

    @jsii.member(jsii_name="resetEmailSenderUsername")
    def reset_email_sender_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailSenderUsername", []))

    @jsii.member(jsii_name="resetEnableRemoteBackedStorage")
    def reset_enable_remote_backed_storage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableRemoteBackedStorage", []))

    @jsii.member(jsii_name="resetEnableSearchableSnapshots")
    def reset_enable_searchable_snapshots(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableSearchableSnapshots", []))

    @jsii.member(jsii_name="resetEnableSecurityAudit")
    def reset_enable_security_audit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableSecurityAudit", []))

    @jsii.member(jsii_name="resetEnableSnapshotApi")
    def reset_enable_snapshot_api(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableSnapshotApi", []))

    @jsii.member(jsii_name="resetHttpMaxContentLength")
    def reset_http_max_content_length(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpMaxContentLength", []))

    @jsii.member(jsii_name="resetHttpMaxHeaderSize")
    def reset_http_max_header_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpMaxHeaderSize", []))

    @jsii.member(jsii_name="resetHttpMaxInitialLineLength")
    def reset_http_max_initial_line_length(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpMaxInitialLineLength", []))

    @jsii.member(jsii_name="resetIndexPatterns")
    def reset_index_patterns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndexPatterns", []))

    @jsii.member(jsii_name="resetIndexRollup")
    def reset_index_rollup(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndexRollup", []))

    @jsii.member(jsii_name="resetIndexTemplate")
    def reset_index_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndexTemplate", []))

    @jsii.member(jsii_name="resetIndicesFielddataCacheSize")
    def reset_indices_fielddata_cache_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndicesFielddataCacheSize", []))

    @jsii.member(jsii_name="resetIndicesMemoryIndexBufferSize")
    def reset_indices_memory_index_buffer_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndicesMemoryIndexBufferSize", []))

    @jsii.member(jsii_name="resetIndicesMemoryMaxIndexBufferSize")
    def reset_indices_memory_max_index_buffer_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndicesMemoryMaxIndexBufferSize", []))

    @jsii.member(jsii_name="resetIndicesMemoryMinIndexBufferSize")
    def reset_indices_memory_min_index_buffer_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndicesMemoryMinIndexBufferSize", []))

    @jsii.member(jsii_name="resetIndicesQueriesCacheSize")
    def reset_indices_queries_cache_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndicesQueriesCacheSize", []))

    @jsii.member(jsii_name="resetIndicesQueryBoolMaxClauseCount")
    def reset_indices_query_bool_max_clause_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndicesQueryBoolMaxClauseCount", []))

    @jsii.member(jsii_name="resetIndicesRecoveryMaxBytesPerSec")
    def reset_indices_recovery_max_bytes_per_sec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndicesRecoveryMaxBytesPerSec", []))

    @jsii.member(jsii_name="resetIndicesRecoveryMaxConcurrentFileChunks")
    def reset_indices_recovery_max_concurrent_file_chunks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndicesRecoveryMaxConcurrentFileChunks", []))

    @jsii.member(jsii_name="resetIpFilter")
    def reset_ip_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpFilter", []))

    @jsii.member(jsii_name="resetIsmEnabled")
    def reset_ism_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsmEnabled", []))

    @jsii.member(jsii_name="resetIsmHistoryEnabled")
    def reset_ism_history_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsmHistoryEnabled", []))

    @jsii.member(jsii_name="resetIsmHistoryMaxAge")
    def reset_ism_history_max_age(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsmHistoryMaxAge", []))

    @jsii.member(jsii_name="resetIsmHistoryMaxDocs")
    def reset_ism_history_max_docs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsmHistoryMaxDocs", []))

    @jsii.member(jsii_name="resetIsmHistoryRolloverCheckPeriod")
    def reset_ism_history_rollover_check_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsmHistoryRolloverCheckPeriod", []))

    @jsii.member(jsii_name="resetIsmHistoryRolloverRetentionPeriod")
    def reset_ism_history_rollover_retention_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsmHistoryRolloverRetentionPeriod", []))

    @jsii.member(jsii_name="resetKeepIndexRefreshInterval")
    def reset_keep_index_refresh_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeepIndexRefreshInterval", []))

    @jsii.member(jsii_name="resetKnnMemoryCircuitBreakerEnabled")
    def reset_knn_memory_circuit_breaker_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKnnMemoryCircuitBreakerEnabled", []))

    @jsii.member(jsii_name="resetKnnMemoryCircuitBreakerLimit")
    def reset_knn_memory_circuit_breaker_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKnnMemoryCircuitBreakerLimit", []))

    @jsii.member(jsii_name="resetNodeSearchCacheSize")
    def reset_node_search_cache_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodeSearchCacheSize", []))

    @jsii.member(jsii_name="resetOpenid")
    def reset_openid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpenid", []))

    @jsii.member(jsii_name="resetOpensearchDashboards")
    def reset_opensearch_dashboards(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpensearchDashboards", []))

    @jsii.member(jsii_name="resetOverrideMainResponseVersion")
    def reset_override_main_response_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOverrideMainResponseVersion", []))

    @jsii.member(jsii_name="resetPluginsAlertingFilterByBackendRoles")
    def reset_plugins_alerting_filter_by_backend_roles(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPluginsAlertingFilterByBackendRoles", []))

    @jsii.member(jsii_name="resetPublicAccess")
    def reset_public_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicAccess", []))

    @jsii.member(jsii_name="resetReindexRemoteWhitelist")
    def reset_reindex_remote_whitelist(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReindexRemoteWhitelist", []))

    @jsii.member(jsii_name="resetRemoteStore")
    def reset_remote_store(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRemoteStore", []))

    @jsii.member(jsii_name="resetSaml")
    def reset_saml(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSaml", []))

    @jsii.member(jsii_name="resetScriptMaxCompilationsRate")
    def reset_script_max_compilations_rate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScriptMaxCompilationsRate", []))

    @jsii.member(jsii_name="resetSearchBackpressure")
    def reset_search_backpressure(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSearchBackpressure", []))

    @jsii.member(jsii_name="resetSearchInsightsTopQueries")
    def reset_search_insights_top_queries(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSearchInsightsTopQueries", []))

    @jsii.member(jsii_name="resetSearchMaxBuckets")
    def reset_search_max_buckets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSearchMaxBuckets", []))

    @jsii.member(jsii_name="resetSegrep")
    def reset_segrep(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSegrep", []))

    @jsii.member(jsii_name="resetServiceLog")
    def reset_service_log(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceLog", []))

    @jsii.member(jsii_name="resetShardIndexingPressure")
    def reset_shard_indexing_pressure(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShardIndexingPressure", []))

    @jsii.member(jsii_name="resetThreadPoolAnalyzeQueueSize")
    def reset_thread_pool_analyze_queue_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolAnalyzeQueueSize", []))

    @jsii.member(jsii_name="resetThreadPoolAnalyzeSize")
    def reset_thread_pool_analyze_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolAnalyzeSize", []))

    @jsii.member(jsii_name="resetThreadPoolForceMergeSize")
    def reset_thread_pool_force_merge_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolForceMergeSize", []))

    @jsii.member(jsii_name="resetThreadPoolGetQueueSize")
    def reset_thread_pool_get_queue_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolGetQueueSize", []))

    @jsii.member(jsii_name="resetThreadPoolGetSize")
    def reset_thread_pool_get_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolGetSize", []))

    @jsii.member(jsii_name="resetThreadPoolSearchQueueSize")
    def reset_thread_pool_search_queue_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolSearchQueueSize", []))

    @jsii.member(jsii_name="resetThreadPoolSearchSize")
    def reset_thread_pool_search_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolSearchSize", []))

    @jsii.member(jsii_name="resetThreadPoolSearchThrottledQueueSize")
    def reset_thread_pool_search_throttled_queue_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolSearchThrottledQueueSize", []))

    @jsii.member(jsii_name="resetThreadPoolSearchThrottledSize")
    def reset_thread_pool_search_throttled_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolSearchThrottledSize", []))

    @jsii.member(jsii_name="resetThreadPoolWriteQueueSize")
    def reset_thread_pool_write_queue_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolWriteQueueSize", []))

    @jsii.member(jsii_name="resetThreadPoolWriteSize")
    def reset_thread_pool_write_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolWriteSize", []))

    @jsii.member(jsii_name="resetVersion")
    def reset_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersion", []))

    @builtins.property
    @jsii.member(jsii_name="authFailureListeners")
    def auth_failure_listeners(
        self,
    ) -> ManagedDatabaseOpensearchPropertiesAuthFailureListenersOutputReference:
        return typing.cast(ManagedDatabaseOpensearchPropertiesAuthFailureListenersOutputReference, jsii.get(self, "authFailureListeners"))

    @builtins.property
    @jsii.member(jsii_name="clusterRemoteStore")
    def cluster_remote_store(
        self,
    ) -> ManagedDatabaseOpensearchPropertiesClusterRemoteStoreOutputReference:
        return typing.cast(ManagedDatabaseOpensearchPropertiesClusterRemoteStoreOutputReference, jsii.get(self, "clusterRemoteStore"))

    @builtins.property
    @jsii.member(jsii_name="clusterSearchRequestSlowlog")
    def cluster_search_request_slowlog(
        self,
    ) -> ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlogOutputReference:
        return typing.cast(ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlogOutputReference, jsii.get(self, "clusterSearchRequestSlowlog"))

    @builtins.property
    @jsii.member(jsii_name="diskWatermarks")
    def disk_watermarks(
        self,
    ) -> ManagedDatabaseOpensearchPropertiesDiskWatermarksOutputReference:
        return typing.cast(ManagedDatabaseOpensearchPropertiesDiskWatermarksOutputReference, jsii.get(self, "diskWatermarks"))

    @builtins.property
    @jsii.member(jsii_name="indexRollup")
    def index_rollup(
        self,
    ) -> ManagedDatabaseOpensearchPropertiesIndexRollupOutputReference:
        return typing.cast(ManagedDatabaseOpensearchPropertiesIndexRollupOutputReference, jsii.get(self, "indexRollup"))

    @builtins.property
    @jsii.member(jsii_name="indexTemplate")
    def index_template(
        self,
    ) -> ManagedDatabaseOpensearchPropertiesIndexTemplateOutputReference:
        return typing.cast(ManagedDatabaseOpensearchPropertiesIndexTemplateOutputReference, jsii.get(self, "indexTemplate"))

    @builtins.property
    @jsii.member(jsii_name="openid")
    def openid(self) -> ManagedDatabaseOpensearchPropertiesOpenidOutputReference:
        return typing.cast(ManagedDatabaseOpensearchPropertiesOpenidOutputReference, jsii.get(self, "openid"))

    @builtins.property
    @jsii.member(jsii_name="opensearchDashboards")
    def opensearch_dashboards(
        self,
    ) -> ManagedDatabaseOpensearchPropertiesOpensearchDashboardsOutputReference:
        return typing.cast(ManagedDatabaseOpensearchPropertiesOpensearchDashboardsOutputReference, jsii.get(self, "opensearchDashboards"))

    @builtins.property
    @jsii.member(jsii_name="remoteStore")
    def remote_store(
        self,
    ) -> "ManagedDatabaseOpensearchPropertiesRemoteStoreOutputReference":
        return typing.cast("ManagedDatabaseOpensearchPropertiesRemoteStoreOutputReference", jsii.get(self, "remoteStore"))

    @builtins.property
    @jsii.member(jsii_name="saml")
    def saml(self) -> "ManagedDatabaseOpensearchPropertiesSamlOutputReference":
        return typing.cast("ManagedDatabaseOpensearchPropertiesSamlOutputReference", jsii.get(self, "saml"))

    @builtins.property
    @jsii.member(jsii_name="searchBackpressure")
    def search_backpressure(
        self,
    ) -> "ManagedDatabaseOpensearchPropertiesSearchBackpressureOutputReference":
        return typing.cast("ManagedDatabaseOpensearchPropertiesSearchBackpressureOutputReference", jsii.get(self, "searchBackpressure"))

    @builtins.property
    @jsii.member(jsii_name="searchInsightsTopQueries")
    def search_insights_top_queries(
        self,
    ) -> "ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesOutputReference":
        return typing.cast("ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesOutputReference", jsii.get(self, "searchInsightsTopQueries"))

    @builtins.property
    @jsii.member(jsii_name="segrep")
    def segrep(self) -> "ManagedDatabaseOpensearchPropertiesSegrepOutputReference":
        return typing.cast("ManagedDatabaseOpensearchPropertiesSegrepOutputReference", jsii.get(self, "segrep"))

    @builtins.property
    @jsii.member(jsii_name="shardIndexingPressure")
    def shard_indexing_pressure(
        self,
    ) -> "ManagedDatabaseOpensearchPropertiesShardIndexingPressureOutputReference":
        return typing.cast("ManagedDatabaseOpensearchPropertiesShardIndexingPressureOutputReference", jsii.get(self, "shardIndexingPressure"))

    @builtins.property
    @jsii.member(jsii_name="actionAutoCreateIndexEnabledInput")
    def action_auto_create_index_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "actionAutoCreateIndexEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="actionDestructiveRequiresNameInput")
    def action_destructive_requires_name_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "actionDestructiveRequiresNameInput"))

    @builtins.property
    @jsii.member(jsii_name="authFailureListenersInput")
    def auth_failure_listeners_input(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListeners]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListeners], jsii.get(self, "authFailureListenersInput"))

    @builtins.property
    @jsii.member(jsii_name="automaticUtilityNetworkIpFilterInput")
    def automatic_utility_network_ip_filter_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "automaticUtilityNetworkIpFilterInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterFilecacheRemoteDataRatioInput")
    def cluster_filecache_remote_data_ratio_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "clusterFilecacheRemoteDataRatioInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterMaxShardsPerNodeInput")
    def cluster_max_shards_per_node_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "clusterMaxShardsPerNodeInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterRemoteStoreInput")
    def cluster_remote_store_input(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesClusterRemoteStore]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesClusterRemoteStore], jsii.get(self, "clusterRemoteStoreInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterRoutingAllocationBalancePreferPrimaryInput")
    def cluster_routing_allocation_balance_prefer_primary_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "clusterRoutingAllocationBalancePreferPrimaryInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterRoutingAllocationNodeConcurrentRecoveriesInput")
    def cluster_routing_allocation_node_concurrent_recoveries_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "clusterRoutingAllocationNodeConcurrentRecoveriesInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterSearchRequestSlowlogInput")
    def cluster_search_request_slowlog_input(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlog]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlog], jsii.get(self, "clusterSearchRequestSlowlogInput"))

    @builtins.property
    @jsii.member(jsii_name="customDomainInput")
    def custom_domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customDomainInput"))

    @builtins.property
    @jsii.member(jsii_name="diskWatermarksInput")
    def disk_watermarks_input(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesDiskWatermarks]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesDiskWatermarks], jsii.get(self, "diskWatermarksInput"))

    @builtins.property
    @jsii.member(jsii_name="elasticsearchVersionInput")
    def elasticsearch_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "elasticsearchVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="emailSenderNameInput")
    def email_sender_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailSenderNameInput"))

    @builtins.property
    @jsii.member(jsii_name="emailSenderPasswordInput")
    def email_sender_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailSenderPasswordInput"))

    @builtins.property
    @jsii.member(jsii_name="emailSenderUsernameInput")
    def email_sender_username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailSenderUsernameInput"))

    @builtins.property
    @jsii.member(jsii_name="enableRemoteBackedStorageInput")
    def enable_remote_backed_storage_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableRemoteBackedStorageInput"))

    @builtins.property
    @jsii.member(jsii_name="enableSearchableSnapshotsInput")
    def enable_searchable_snapshots_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableSearchableSnapshotsInput"))

    @builtins.property
    @jsii.member(jsii_name="enableSecurityAuditInput")
    def enable_security_audit_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableSecurityAuditInput"))

    @builtins.property
    @jsii.member(jsii_name="enableSnapshotApiInput")
    def enable_snapshot_api_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableSnapshotApiInput"))

    @builtins.property
    @jsii.member(jsii_name="httpMaxContentLengthInput")
    def http_max_content_length_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "httpMaxContentLengthInput"))

    @builtins.property
    @jsii.member(jsii_name="httpMaxHeaderSizeInput")
    def http_max_header_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "httpMaxHeaderSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="httpMaxInitialLineLengthInput")
    def http_max_initial_line_length_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "httpMaxInitialLineLengthInput"))

    @builtins.property
    @jsii.member(jsii_name="indexPatternsInput")
    def index_patterns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "indexPatternsInput"))

    @builtins.property
    @jsii.member(jsii_name="indexRollupInput")
    def index_rollup_input(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesIndexRollup]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesIndexRollup], jsii.get(self, "indexRollupInput"))

    @builtins.property
    @jsii.member(jsii_name="indexTemplateInput")
    def index_template_input(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesIndexTemplate]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesIndexTemplate], jsii.get(self, "indexTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="indicesFielddataCacheSizeInput")
    def indices_fielddata_cache_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "indicesFielddataCacheSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="indicesMemoryIndexBufferSizeInput")
    def indices_memory_index_buffer_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "indicesMemoryIndexBufferSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="indicesMemoryMaxIndexBufferSizeInput")
    def indices_memory_max_index_buffer_size_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "indicesMemoryMaxIndexBufferSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="indicesMemoryMinIndexBufferSizeInput")
    def indices_memory_min_index_buffer_size_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "indicesMemoryMinIndexBufferSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="indicesQueriesCacheSizeInput")
    def indices_queries_cache_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "indicesQueriesCacheSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="indicesQueryBoolMaxClauseCountInput")
    def indices_query_bool_max_clause_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "indicesQueryBoolMaxClauseCountInput"))

    @builtins.property
    @jsii.member(jsii_name="indicesRecoveryMaxBytesPerSecInput")
    def indices_recovery_max_bytes_per_sec_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "indicesRecoveryMaxBytesPerSecInput"))

    @builtins.property
    @jsii.member(jsii_name="indicesRecoveryMaxConcurrentFileChunksInput")
    def indices_recovery_max_concurrent_file_chunks_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "indicesRecoveryMaxConcurrentFileChunksInput"))

    @builtins.property
    @jsii.member(jsii_name="ipFilterInput")
    def ip_filter_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ipFilterInput"))

    @builtins.property
    @jsii.member(jsii_name="ismEnabledInput")
    def ism_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "ismEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="ismHistoryEnabledInput")
    def ism_history_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "ismHistoryEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="ismHistoryMaxAgeInput")
    def ism_history_max_age_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ismHistoryMaxAgeInput"))

    @builtins.property
    @jsii.member(jsii_name="ismHistoryMaxDocsInput")
    def ism_history_max_docs_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ismHistoryMaxDocsInput"))

    @builtins.property
    @jsii.member(jsii_name="ismHistoryRolloverCheckPeriodInput")
    def ism_history_rollover_check_period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ismHistoryRolloverCheckPeriodInput"))

    @builtins.property
    @jsii.member(jsii_name="ismHistoryRolloverRetentionPeriodInput")
    def ism_history_rollover_retention_period_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ismHistoryRolloverRetentionPeriodInput"))

    @builtins.property
    @jsii.member(jsii_name="keepIndexRefreshIntervalInput")
    def keep_index_refresh_interval_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "keepIndexRefreshIntervalInput"))

    @builtins.property
    @jsii.member(jsii_name="knnMemoryCircuitBreakerEnabledInput")
    def knn_memory_circuit_breaker_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "knnMemoryCircuitBreakerEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="knnMemoryCircuitBreakerLimitInput")
    def knn_memory_circuit_breaker_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "knnMemoryCircuitBreakerLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="nodeSearchCacheSizeInput")
    def node_search_cache_size_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nodeSearchCacheSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="openidInput")
    def openid_input(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesOpenid]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesOpenid], jsii.get(self, "openidInput"))

    @builtins.property
    @jsii.member(jsii_name="opensearchDashboardsInput")
    def opensearch_dashboards_input(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesOpensearchDashboards]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesOpensearchDashboards], jsii.get(self, "opensearchDashboardsInput"))

    @builtins.property
    @jsii.member(jsii_name="overrideMainResponseVersionInput")
    def override_main_response_version_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "overrideMainResponseVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="pluginsAlertingFilterByBackendRolesInput")
    def plugins_alerting_filter_by_backend_roles_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "pluginsAlertingFilterByBackendRolesInput"))

    @builtins.property
    @jsii.member(jsii_name="publicAccessInput")
    def public_access_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "publicAccessInput"))

    @builtins.property
    @jsii.member(jsii_name="reindexRemoteWhitelistInput")
    def reindex_remote_whitelist_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "reindexRemoteWhitelistInput"))

    @builtins.property
    @jsii.member(jsii_name="remoteStoreInput")
    def remote_store_input(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesRemoteStore"]:
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesRemoteStore"], jsii.get(self, "remoteStoreInput"))

    @builtins.property
    @jsii.member(jsii_name="samlInput")
    def saml_input(self) -> typing.Optional["ManagedDatabaseOpensearchPropertiesSaml"]:
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesSaml"], jsii.get(self, "samlInput"))

    @builtins.property
    @jsii.member(jsii_name="scriptMaxCompilationsRateInput")
    def script_max_compilations_rate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scriptMaxCompilationsRateInput"))

    @builtins.property
    @jsii.member(jsii_name="searchBackpressureInput")
    def search_backpressure_input(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesSearchBackpressure"]:
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesSearchBackpressure"], jsii.get(self, "searchBackpressureInput"))

    @builtins.property
    @jsii.member(jsii_name="searchInsightsTopQueriesInput")
    def search_insights_top_queries_input(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueries"]:
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueries"], jsii.get(self, "searchInsightsTopQueriesInput"))

    @builtins.property
    @jsii.member(jsii_name="searchMaxBucketsInput")
    def search_max_buckets_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "searchMaxBucketsInput"))

    @builtins.property
    @jsii.member(jsii_name="segrepInput")
    def segrep_input(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesSegrep"]:
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesSegrep"], jsii.get(self, "segrepInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceLogInput")
    def service_log_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "serviceLogInput"))

    @builtins.property
    @jsii.member(jsii_name="shardIndexingPressureInput")
    def shard_indexing_pressure_input(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesShardIndexingPressure"]:
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesShardIndexingPressure"], jsii.get(self, "shardIndexingPressureInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolAnalyzeQueueSizeInput")
    def thread_pool_analyze_queue_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolAnalyzeQueueSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolAnalyzeSizeInput")
    def thread_pool_analyze_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolAnalyzeSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolForceMergeSizeInput")
    def thread_pool_force_merge_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolForceMergeSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolGetQueueSizeInput")
    def thread_pool_get_queue_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolGetQueueSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolGetSizeInput")
    def thread_pool_get_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolGetSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolSearchQueueSizeInput")
    def thread_pool_search_queue_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolSearchQueueSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolSearchSizeInput")
    def thread_pool_search_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolSearchSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolSearchThrottledQueueSizeInput")
    def thread_pool_search_throttled_queue_size_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolSearchThrottledQueueSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolSearchThrottledSizeInput")
    def thread_pool_search_throttled_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolSearchThrottledSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolWriteQueueSizeInput")
    def thread_pool_write_queue_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolWriteQueueSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolWriteSizeInput")
    def thread_pool_write_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolWriteSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property
    @jsii.member(jsii_name="actionAutoCreateIndexEnabled")
    def action_auto_create_index_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "actionAutoCreateIndexEnabled"))

    @action_auto_create_index_enabled.setter
    def action_auto_create_index_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f95b49868c2e1ec7544168878febf8b6696a57483b6f51fa99aa0925cb16697)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "actionAutoCreateIndexEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="actionDestructiveRequiresName")
    def action_destructive_requires_name(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "actionDestructiveRequiresName"))

    @action_destructive_requires_name.setter
    def action_destructive_requires_name(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e457da88de09c5532affd0a501416c99106d06518e52d2a5677fde17f0757fd7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "actionDestructiveRequiresName", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__be63faa87856b340f7df4fdaa463d51315ab3cec9d31b97f5c4d5f518b414508)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "automaticUtilityNetworkIpFilter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterFilecacheRemoteDataRatio")
    def cluster_filecache_remote_data_ratio(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "clusterFilecacheRemoteDataRatio"))

    @cluster_filecache_remote_data_ratio.setter
    def cluster_filecache_remote_data_ratio(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56ad8b6cd68415d53aed2467ec71f02ea55b6b3fbe4d64b15a5285311a1dc3b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterFilecacheRemoteDataRatio", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterMaxShardsPerNode")
    def cluster_max_shards_per_node(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "clusterMaxShardsPerNode"))

    @cluster_max_shards_per_node.setter
    def cluster_max_shards_per_node(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3368d21a864593369d41fa3b6553ceda22676badcd2892eab312b0d160b62f1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterMaxShardsPerNode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterRoutingAllocationBalancePreferPrimary")
    def cluster_routing_allocation_balance_prefer_primary(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "clusterRoutingAllocationBalancePreferPrimary"))

    @cluster_routing_allocation_balance_prefer_primary.setter
    def cluster_routing_allocation_balance_prefer_primary(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4acaa825e4505022989c6428a6d611632f85344bcb6863b74490ff70481c3df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterRoutingAllocationBalancePreferPrimary", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterRoutingAllocationNodeConcurrentRecoveries")
    def cluster_routing_allocation_node_concurrent_recoveries(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "clusterRoutingAllocationNodeConcurrentRecoveries"))

    @cluster_routing_allocation_node_concurrent_recoveries.setter
    def cluster_routing_allocation_node_concurrent_recoveries(
        self,
        value: jsii.Number,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0448eb5420a97c55d350dfab1c0a0d3e8726d744e441f4fde0d412dd04f31497)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterRoutingAllocationNodeConcurrentRecoveries", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="customDomain")
    def custom_domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customDomain"))

    @custom_domain.setter
    def custom_domain(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07a65588eb7a4625bdb8375e03839f7d7ccf09b91bb824e3b31afc1c39388598)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customDomain", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="elasticsearchVersion")
    def elasticsearch_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "elasticsearchVersion"))

    @elasticsearch_version.setter
    def elasticsearch_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__def39ace52f9f4b94afbcd8016abe63135f081d70125685ec54dd3ef178d1de3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "elasticsearchVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="emailSenderName")
    def email_sender_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailSenderName"))

    @email_sender_name.setter
    def email_sender_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d549945259dc5d5d9b2134e2a3264e213b749e4f33396341c391bf22353af47)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailSenderName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="emailSenderPassword")
    def email_sender_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailSenderPassword"))

    @email_sender_password.setter
    def email_sender_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b181764d7b414fdac2022d32d63421fe71b45025faa283d816517a60e472c6c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailSenderPassword", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="emailSenderUsername")
    def email_sender_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailSenderUsername"))

    @email_sender_username.setter
    def email_sender_username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__342025668ce074acad3db548bb92de3b1aaf5e8a569bcdf9f928e24b1dce9c38)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailSenderUsername", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableRemoteBackedStorage")
    def enable_remote_backed_storage(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableRemoteBackedStorage"))

    @enable_remote_backed_storage.setter
    def enable_remote_backed_storage(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6bca62f115362f57dd2893e4d92a97631fc0dae4d4b38a8347471bd6a8c2259)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableRemoteBackedStorage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableSearchableSnapshots")
    def enable_searchable_snapshots(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableSearchableSnapshots"))

    @enable_searchable_snapshots.setter
    def enable_searchable_snapshots(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3477e1ea1b7e2193121b11b3416a7dbff4f64a222dc6cc3963488697ec8352d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableSearchableSnapshots", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableSecurityAudit")
    def enable_security_audit(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableSecurityAudit"))

    @enable_security_audit.setter
    def enable_security_audit(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff78f5e79729d11ea6229a93440341c6dfb144628a5a51a9a4f0c10d9983ef87)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableSecurityAudit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableSnapshotApi")
    def enable_snapshot_api(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableSnapshotApi"))

    @enable_snapshot_api.setter
    def enable_snapshot_api(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e45ead370d8febc26e146a75b660cd2627775fd50527d1c042f0d05328e66c1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableSnapshotApi", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="httpMaxContentLength")
    def http_max_content_length(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "httpMaxContentLength"))

    @http_max_content_length.setter
    def http_max_content_length(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09252df690d98b7364842578b7664698629fd55a3c709cedfc832883b986e93c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpMaxContentLength", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="httpMaxHeaderSize")
    def http_max_header_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "httpMaxHeaderSize"))

    @http_max_header_size.setter
    def http_max_header_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f23654b3c993300d915c75caa2b551bed505e332e601ae1d318b6f7c22eec1d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpMaxHeaderSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="httpMaxInitialLineLength")
    def http_max_initial_line_length(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "httpMaxInitialLineLength"))

    @http_max_initial_line_length.setter
    def http_max_initial_line_length(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71c76b5482471bb5f448beac6f8f0c45b923c1fc3debd34a481229204fb99ca1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpMaxInitialLineLength", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="indexPatterns")
    def index_patterns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "indexPatterns"))

    @index_patterns.setter
    def index_patterns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58c6add2afd8176cf65752af011b26017ea4026647b88807e7848153aa808c88)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indexPatterns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="indicesFielddataCacheSize")
    def indices_fielddata_cache_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "indicesFielddataCacheSize"))

    @indices_fielddata_cache_size.setter
    def indices_fielddata_cache_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa13f532a0cc1807de56948d104831eea41a922b8cccfa4dbededb8056bc2101)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indicesFielddataCacheSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="indicesMemoryIndexBufferSize")
    def indices_memory_index_buffer_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "indicesMemoryIndexBufferSize"))

    @indices_memory_index_buffer_size.setter
    def indices_memory_index_buffer_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a8c26865a2a9328ae331cb883300375516826479d56c03bbe3b173701034e54)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indicesMemoryIndexBufferSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="indicesMemoryMaxIndexBufferSize")
    def indices_memory_max_index_buffer_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "indicesMemoryMaxIndexBufferSize"))

    @indices_memory_max_index_buffer_size.setter
    def indices_memory_max_index_buffer_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__066a7c0b66ed33e66af285d45119ca128f33fc0bcbfe01b3a35bcf4a21b2f488)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indicesMemoryMaxIndexBufferSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="indicesMemoryMinIndexBufferSize")
    def indices_memory_min_index_buffer_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "indicesMemoryMinIndexBufferSize"))

    @indices_memory_min_index_buffer_size.setter
    def indices_memory_min_index_buffer_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a2af7f1a139f5456a3f2eeca4e3867ef26c85c7ba01267c4acf3fcbe89eb9ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indicesMemoryMinIndexBufferSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="indicesQueriesCacheSize")
    def indices_queries_cache_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "indicesQueriesCacheSize"))

    @indices_queries_cache_size.setter
    def indices_queries_cache_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db0348b951ec966edf534f9e879d0bee16e2d53cf2ff85b213c5dc31755a5aa4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indicesQueriesCacheSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="indicesQueryBoolMaxClauseCount")
    def indices_query_bool_max_clause_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "indicesQueryBoolMaxClauseCount"))

    @indices_query_bool_max_clause_count.setter
    def indices_query_bool_max_clause_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__363b9a51b2ae015e89e6f9beea8cd6589eb3254d3e9a8ed918d7f8a059b00488)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indicesQueryBoolMaxClauseCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="indicesRecoveryMaxBytesPerSec")
    def indices_recovery_max_bytes_per_sec(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "indicesRecoveryMaxBytesPerSec"))

    @indices_recovery_max_bytes_per_sec.setter
    def indices_recovery_max_bytes_per_sec(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d857a7fba85a3ccba0ca1972bd70c474b4d2fea3a6f3b935d6bf1920e087333b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indicesRecoveryMaxBytesPerSec", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="indicesRecoveryMaxConcurrentFileChunks")
    def indices_recovery_max_concurrent_file_chunks(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "indicesRecoveryMaxConcurrentFileChunks"))

    @indices_recovery_max_concurrent_file_chunks.setter
    def indices_recovery_max_concurrent_file_chunks(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__511b44be808d39b3f5d61cf6c8b691b91fc91afda941c083d2ba0fee3107aece)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indicesRecoveryMaxConcurrentFileChunks", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipFilter")
    def ip_filter(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ipFilter"))

    @ip_filter.setter
    def ip_filter(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5817885ce9a4dfdaf892000c0e8757e89b0d1233e8785edbee32917946b1f379)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipFilter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ismEnabled")
    def ism_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ismEnabled"))

    @ism_enabled.setter
    def ism_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dde81e5014559bf79849f8363ddaef4d0fe9186cec22e692bf4b937ed30bf89)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ismEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ismHistoryEnabled")
    def ism_history_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ismHistoryEnabled"))

    @ism_history_enabled.setter
    def ism_history_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d409d4c93acb6dbddf3ea05ef640c8c083700c01312ae34de3c952a00933254)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ismHistoryEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ismHistoryMaxAge")
    def ism_history_max_age(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ismHistoryMaxAge"))

    @ism_history_max_age.setter
    def ism_history_max_age(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd4ad47529fc509173d3341762a0c1b8ce4e8d381578c9db0e9588fb5bd11e69)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ismHistoryMaxAge", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ismHistoryMaxDocs")
    def ism_history_max_docs(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ismHistoryMaxDocs"))

    @ism_history_max_docs.setter
    def ism_history_max_docs(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7988c725f00df71948d13e3c7a67c37939bfbdf59be068727cb0f1b6fe5c0b49)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ismHistoryMaxDocs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ismHistoryRolloverCheckPeriod")
    def ism_history_rollover_check_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ismHistoryRolloverCheckPeriod"))

    @ism_history_rollover_check_period.setter
    def ism_history_rollover_check_period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6579b40abc92fc56536665342c25021b16220f2bd87f5e74283f08704cfe6abb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ismHistoryRolloverCheckPeriod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ismHistoryRolloverRetentionPeriod")
    def ism_history_rollover_retention_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ismHistoryRolloverRetentionPeriod"))

    @ism_history_rollover_retention_period.setter
    def ism_history_rollover_retention_period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb9144f9ff10e0665d17f1dab9d796961a1f30385738d5fac5012ac1e12d73c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ismHistoryRolloverRetentionPeriod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keepIndexRefreshInterval")
    def keep_index_refresh_interval(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "keepIndexRefreshInterval"))

    @keep_index_refresh_interval.setter
    def keep_index_refresh_interval(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__475c7d9ea1f132358fd8876b5bce857503b42c419cf0edd268668a9396576272)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keepIndexRefreshInterval", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="knnMemoryCircuitBreakerEnabled")
    def knn_memory_circuit_breaker_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "knnMemoryCircuitBreakerEnabled"))

    @knn_memory_circuit_breaker_enabled.setter
    def knn_memory_circuit_breaker_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79543fe9d0bb8f49f03afaba4905ee1fc1c6bb8081b72a0ce935e05db800d019)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "knnMemoryCircuitBreakerEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="knnMemoryCircuitBreakerLimit")
    def knn_memory_circuit_breaker_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "knnMemoryCircuitBreakerLimit"))

    @knn_memory_circuit_breaker_limit.setter
    def knn_memory_circuit_breaker_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d77bb2fd42dcdec4347d48a5fd38597e5fd7a8bd356c3b4be6c11e5d48f49eca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "knnMemoryCircuitBreakerLimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nodeSearchCacheSize")
    def node_search_cache_size(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeSearchCacheSize"))

    @node_search_cache_size.setter
    def node_search_cache_size(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e9d2f14dde38e4490263e09c4c724a7695c50bcf345ee919284647e4ec77730)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nodeSearchCacheSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="overrideMainResponseVersion")
    def override_main_response_version(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "overrideMainResponseVersion"))

    @override_main_response_version.setter
    def override_main_response_version(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec6c829c8246593bfea087d544de86602dcf1c3f827bb531e45fb456fd06b41a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "overrideMainResponseVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pluginsAlertingFilterByBackendRoles")
    def plugins_alerting_filter_by_backend_roles(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "pluginsAlertingFilterByBackendRoles"))

    @plugins_alerting_filter_by_backend_roles.setter
    def plugins_alerting_filter_by_backend_roles(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc45a3b1177a7e18688e7dbcc3ca2d16552505944545509d4b5a66e029a2afd3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pluginsAlertingFilterByBackendRoles", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__1877b1cae754d3c61d03eab40de84ea8994bc6a8f432702bdad2e544cca0bb93)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publicAccess", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="reindexRemoteWhitelist")
    def reindex_remote_whitelist(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "reindexRemoteWhitelist"))

    @reindex_remote_whitelist.setter
    def reindex_remote_whitelist(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00d138e917ad74a2a8c043cd17d158357905bed6e23949c38b382514204bd13f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reindexRemoteWhitelist", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scriptMaxCompilationsRate")
    def script_max_compilations_rate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scriptMaxCompilationsRate"))

    @script_max_compilations_rate.setter
    def script_max_compilations_rate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de1660d38a30c3e2336ab4a8e93e4240c706d088fe2d0a466fcf8ddb12386f10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scriptMaxCompilationsRate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="searchMaxBuckets")
    def search_max_buckets(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "searchMaxBuckets"))

    @search_max_buckets.setter
    def search_max_buckets(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a031050a9e6f8a40b6fff2021afeb15b5ad471d2a0772dbf01945324746e1c4e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "searchMaxBuckets", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__e8c3fe099944b1f56a32bc799baf5e867e2cdf4f7b392cab873ea63870b05066)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceLog", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threadPoolAnalyzeQueueSize")
    def thread_pool_analyze_queue_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolAnalyzeQueueSize"))

    @thread_pool_analyze_queue_size.setter
    def thread_pool_analyze_queue_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33a0fbdcfa0733a258cb09a7fec41cb87f369bb39dbe3d656186fee89fbfc0bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolAnalyzeQueueSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threadPoolAnalyzeSize")
    def thread_pool_analyze_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolAnalyzeSize"))

    @thread_pool_analyze_size.setter
    def thread_pool_analyze_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__284920e01c9389024b53f7d33cd743be906b889c598a63b378523ba83bee9165)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolAnalyzeSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threadPoolForceMergeSize")
    def thread_pool_force_merge_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolForceMergeSize"))

    @thread_pool_force_merge_size.setter
    def thread_pool_force_merge_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c49306bfe5e374f98a93dbde13277a081ed1c78280db967a45ae6d9aa463d68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolForceMergeSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threadPoolGetQueueSize")
    def thread_pool_get_queue_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolGetQueueSize"))

    @thread_pool_get_queue_size.setter
    def thread_pool_get_queue_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dda12e0a9350f10cc58dfb4503e36cef9ef54b196da052bb6919eefe1b4ddcd2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolGetQueueSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threadPoolGetSize")
    def thread_pool_get_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolGetSize"))

    @thread_pool_get_size.setter
    def thread_pool_get_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56ae2dc20f615630e63a616e89cc1fe881038dcec11ccd7feda4fbca3d504561)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolGetSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threadPoolSearchQueueSize")
    def thread_pool_search_queue_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolSearchQueueSize"))

    @thread_pool_search_queue_size.setter
    def thread_pool_search_queue_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2c716fb378769c59082cbd6ef2a98ab923895cd0d2907af1ddaa2e22ac6933d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolSearchQueueSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threadPoolSearchSize")
    def thread_pool_search_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolSearchSize"))

    @thread_pool_search_size.setter
    def thread_pool_search_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2acbdf19ba9102e2e1937592da16eb85b1c62ad65e6149f8c3d0a3bace050cad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolSearchSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threadPoolSearchThrottledQueueSize")
    def thread_pool_search_throttled_queue_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolSearchThrottledQueueSize"))

    @thread_pool_search_throttled_queue_size.setter
    def thread_pool_search_throttled_queue_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf6c4b8bedfe2dab74ff62e0b49929a7e29387a92737dd6be0d7da5dc2e30672)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolSearchThrottledQueueSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threadPoolSearchThrottledSize")
    def thread_pool_search_throttled_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolSearchThrottledSize"))

    @thread_pool_search_throttled_size.setter
    def thread_pool_search_throttled_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5be01f06da11cbc0ff664fcfcdfa1885cecb35a2be2f64f3db7a6c82afe350d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolSearchThrottledSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threadPoolWriteQueueSize")
    def thread_pool_write_queue_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolWriteQueueSize"))

    @thread_pool_write_queue_size.setter
    def thread_pool_write_queue_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__363d81378d4e1cd4dd5f6d81316deffe21c2b78c49e33a7350d70233def65523)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolWriteQueueSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threadPoolWriteSize")
    def thread_pool_write_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolWriteSize"))

    @thread_pool_write_size.setter
    def thread_pool_write_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b53d519b13b838c462a6929cbcbecaa084a53ce80392b3cfe23e41033ed0af8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolWriteSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fdf3ac54e30cad1108c45853dba19226fdd8c66b79009b24e04a2bfd594cff5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ManagedDatabaseOpensearchProperties]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchProperties], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchProperties],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8adbbea4f99ad4d0b9aca6ba9727235da1a05ed87b8c7206bf576514664c1eba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesRemoteStore",
    jsii_struct_bases=[],
    name_mapping={
        "segment_pressure_bytes_lag_variance_factor": "segmentPressureBytesLagVarianceFactor",
        "segment_pressure_consecutive_failures_limit": "segmentPressureConsecutiveFailuresLimit",
        "segment_pressure_enabled": "segmentPressureEnabled",
        "segment_pressure_time_lag_variance_factor": "segmentPressureTimeLagVarianceFactor",
    },
)
class ManagedDatabaseOpensearchPropertiesRemoteStore:
    def __init__(
        self,
        *,
        segment_pressure_bytes_lag_variance_factor: typing.Optional[jsii.Number] = None,
        segment_pressure_consecutive_failures_limit: typing.Optional[jsii.Number] = None,
        segment_pressure_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        segment_pressure_time_lag_variance_factor: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param segment_pressure_bytes_lag_variance_factor: The variance factor that is used to calculate the dynamic bytes lag threshold. The variance factor that is used together with the moving average to calculate the dynamic bytes lag threshold for activating remote segment backpressure. Defaults to 10. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#segment_pressure_bytes_lag_variance_factor ManagedDatabaseOpensearch#segment_pressure_bytes_lag_variance_factor}
        :param segment_pressure_consecutive_failures_limit: The minimum consecutive failure count for activating remote segment backpressure. The minimum consecutive failure count for activating remote segment backpressure. Defaults to 5. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#segment_pressure_consecutive_failures_limit ManagedDatabaseOpensearch#segment_pressure_consecutive_failures_limit}
        :param segment_pressure_enabled: Enables remote segment backpressure. Enables remote segment backpressure. Default is ``true``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#segment_pressure_enabled ManagedDatabaseOpensearch#segment_pressure_enabled}
        :param segment_pressure_time_lag_variance_factor: The variance factor that is used to calculate the dynamic bytes lag threshold. The variance factor that is used together with the moving average to calculate the dynamic time lag threshold for activating remote segment backpressure. Defaults to 10. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#segment_pressure_time_lag_variance_factor ManagedDatabaseOpensearch#segment_pressure_time_lag_variance_factor}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e1013d27f16812c588f69f95f6c4ed8a1edf66c5571a35c767b4a4ce0496a56)
            check_type(argname="argument segment_pressure_bytes_lag_variance_factor", value=segment_pressure_bytes_lag_variance_factor, expected_type=type_hints["segment_pressure_bytes_lag_variance_factor"])
            check_type(argname="argument segment_pressure_consecutive_failures_limit", value=segment_pressure_consecutive_failures_limit, expected_type=type_hints["segment_pressure_consecutive_failures_limit"])
            check_type(argname="argument segment_pressure_enabled", value=segment_pressure_enabled, expected_type=type_hints["segment_pressure_enabled"])
            check_type(argname="argument segment_pressure_time_lag_variance_factor", value=segment_pressure_time_lag_variance_factor, expected_type=type_hints["segment_pressure_time_lag_variance_factor"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if segment_pressure_bytes_lag_variance_factor is not None:
            self._values["segment_pressure_bytes_lag_variance_factor"] = segment_pressure_bytes_lag_variance_factor
        if segment_pressure_consecutive_failures_limit is not None:
            self._values["segment_pressure_consecutive_failures_limit"] = segment_pressure_consecutive_failures_limit
        if segment_pressure_enabled is not None:
            self._values["segment_pressure_enabled"] = segment_pressure_enabled
        if segment_pressure_time_lag_variance_factor is not None:
            self._values["segment_pressure_time_lag_variance_factor"] = segment_pressure_time_lag_variance_factor

    @builtins.property
    def segment_pressure_bytes_lag_variance_factor(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''The variance factor that is used to calculate the dynamic bytes lag threshold.

        The variance factor that is used together with the moving average to calculate the dynamic bytes lag threshold for activating remote segment backpressure. Defaults to 10.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#segment_pressure_bytes_lag_variance_factor ManagedDatabaseOpensearch#segment_pressure_bytes_lag_variance_factor}
        '''
        result = self._values.get("segment_pressure_bytes_lag_variance_factor")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def segment_pressure_consecutive_failures_limit(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''The minimum consecutive failure count for activating remote segment backpressure.

        The minimum consecutive failure count for activating remote segment backpressure. Defaults to 5.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#segment_pressure_consecutive_failures_limit ManagedDatabaseOpensearch#segment_pressure_consecutive_failures_limit}
        '''
        result = self._values.get("segment_pressure_consecutive_failures_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def segment_pressure_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enables remote segment backpressure. Enables remote segment backpressure. Default is ``true``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#segment_pressure_enabled ManagedDatabaseOpensearch#segment_pressure_enabled}
        '''
        result = self._values.get("segment_pressure_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def segment_pressure_time_lag_variance_factor(self) -> typing.Optional[jsii.Number]:
        '''The variance factor that is used to calculate the dynamic bytes lag threshold.

        The variance factor that is used together with the moving average to calculate the dynamic time lag threshold for activating remote segment backpressure. Defaults to 10.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#segment_pressure_time_lag_variance_factor ManagedDatabaseOpensearch#segment_pressure_time_lag_variance_factor}
        '''
        result = self._values.get("segment_pressure_time_lag_variance_factor")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesRemoteStore(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchPropertiesRemoteStoreOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesRemoteStoreOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e5e4c43397a7ba947a68ea82400d769dd2f03b78aa2f4aebcd0c9b0770ec936e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetSegmentPressureBytesLagVarianceFactor")
    def reset_segment_pressure_bytes_lag_variance_factor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSegmentPressureBytesLagVarianceFactor", []))

    @jsii.member(jsii_name="resetSegmentPressureConsecutiveFailuresLimit")
    def reset_segment_pressure_consecutive_failures_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSegmentPressureConsecutiveFailuresLimit", []))

    @jsii.member(jsii_name="resetSegmentPressureEnabled")
    def reset_segment_pressure_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSegmentPressureEnabled", []))

    @jsii.member(jsii_name="resetSegmentPressureTimeLagVarianceFactor")
    def reset_segment_pressure_time_lag_variance_factor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSegmentPressureTimeLagVarianceFactor", []))

    @builtins.property
    @jsii.member(jsii_name="segmentPressureBytesLagVarianceFactorInput")
    def segment_pressure_bytes_lag_variance_factor_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "segmentPressureBytesLagVarianceFactorInput"))

    @builtins.property
    @jsii.member(jsii_name="segmentPressureConsecutiveFailuresLimitInput")
    def segment_pressure_consecutive_failures_limit_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "segmentPressureConsecutiveFailuresLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="segmentPressureEnabledInput")
    def segment_pressure_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "segmentPressureEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="segmentPressureTimeLagVarianceFactorInput")
    def segment_pressure_time_lag_variance_factor_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "segmentPressureTimeLagVarianceFactorInput"))

    @builtins.property
    @jsii.member(jsii_name="segmentPressureBytesLagVarianceFactor")
    def segment_pressure_bytes_lag_variance_factor(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "segmentPressureBytesLagVarianceFactor"))

    @segment_pressure_bytes_lag_variance_factor.setter
    def segment_pressure_bytes_lag_variance_factor(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b1f15abf13cd92cd37d890df5391a8106a6e7ea2c3cd00aa1a800aa83904469)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "segmentPressureBytesLagVarianceFactor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="segmentPressureConsecutiveFailuresLimit")
    def segment_pressure_consecutive_failures_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "segmentPressureConsecutiveFailuresLimit"))

    @segment_pressure_consecutive_failures_limit.setter
    def segment_pressure_consecutive_failures_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66c5b2fb7de039d911e9c5c44abf4cd980eca04ea40aa66368af670c3b71e0b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "segmentPressureConsecutiveFailuresLimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="segmentPressureEnabled")
    def segment_pressure_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "segmentPressureEnabled"))

    @segment_pressure_enabled.setter
    def segment_pressure_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__976704fb886f0bbd658b1b4324e53cbd1e9210e4e5b9064276185b095cdba0ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "segmentPressureEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="segmentPressureTimeLagVarianceFactor")
    def segment_pressure_time_lag_variance_factor(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "segmentPressureTimeLagVarianceFactor"))

    @segment_pressure_time_lag_variance_factor.setter
    def segment_pressure_time_lag_variance_factor(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__befba414fd08d46bbe36653b548f4b9000e538c2805b736018c35277bd013b7d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "segmentPressureTimeLagVarianceFactor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesRemoteStore]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesRemoteStore], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesRemoteStore],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dff13f45f0788b5975d5ad4140cec670a70fef0e37928cbfdeaacd1d7d25c75e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesSaml",
    jsii_struct_bases=[],
    name_mapping={
        "enabled": "enabled",
        "idp_entity_id": "idpEntityId",
        "idp_metadata_url": "idpMetadataUrl",
        "idp_pemtrustedcas_content": "idpPemtrustedcasContent",
        "roles_key": "rolesKey",
        "sp_entity_id": "spEntityId",
        "subject_key": "subjectKey",
    },
)
class ManagedDatabaseOpensearchPropertiesSaml:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        idp_entity_id: typing.Optional[builtins.str] = None,
        idp_metadata_url: typing.Optional[builtins.str] = None,
        idp_pemtrustedcas_content: typing.Optional[builtins.str] = None,
        roles_key: typing.Optional[builtins.str] = None,
        sp_entity_id: typing.Optional[builtins.str] = None,
        subject_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Enable or disable OpenSearch SAML authentication. Enables or disables SAML-based authentication for OpenSearch. When enabled, users can authenticate using SAML with an Identity Provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        :param idp_entity_id: Identity Provider Entity ID. The unique identifier for the Identity Provider (IdP) entity that is used for SAML authentication. This value is typically provided by the IdP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#idp_entity_id ManagedDatabaseOpensearch#idp_entity_id}
        :param idp_metadata_url: Identity Provider (IdP) SAML metadata URL. The URL of the SAML metadata for the Identity Provider (IdP). This is used to configure SAML-based authentication with the IdP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#idp_metadata_url ManagedDatabaseOpensearch#idp_metadata_url}
        :param idp_pemtrustedcas_content: PEM-encoded root CA Content for SAML IdP server verification. This parameter specifies the PEM-encoded root certificate authority (CA) content for the SAML identity provider (IdP) server verification. The root CA content is used to verify the SSL/TLS certificate presented by the server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#idp_pemtrustedcas_content ManagedDatabaseOpensearch#idp_pemtrustedcas_content}
        :param roles_key: SAML response role attribute. Optional. Specifies the attribute in the SAML response where role information is stored, if available. Role attributes are not required for SAML authentication, but can be included in SAML assertions by most Identity Providers (IdPs) to determine user access levels or permissions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#roles_key ManagedDatabaseOpensearch#roles_key}
        :param sp_entity_id: Service Provider Entity ID. The unique identifier for the Service Provider (SP) entity that is used for SAML authentication. This value is typically provided by the SP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#sp_entity_id ManagedDatabaseOpensearch#sp_entity_id}
        :param subject_key: SAML response subject attribute. Optional. Specifies the attribute in the SAML response where the subject identifier is stored. If not configured, the NameID attribute is used by default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#subject_key ManagedDatabaseOpensearch#subject_key}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b14f1e134e8d0c84c0341fd18666aca6f997046615ab52f5363393b4ab7937e)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument idp_entity_id", value=idp_entity_id, expected_type=type_hints["idp_entity_id"])
            check_type(argname="argument idp_metadata_url", value=idp_metadata_url, expected_type=type_hints["idp_metadata_url"])
            check_type(argname="argument idp_pemtrustedcas_content", value=idp_pemtrustedcas_content, expected_type=type_hints["idp_pemtrustedcas_content"])
            check_type(argname="argument roles_key", value=roles_key, expected_type=type_hints["roles_key"])
            check_type(argname="argument sp_entity_id", value=sp_entity_id, expected_type=type_hints["sp_entity_id"])
            check_type(argname="argument subject_key", value=subject_key, expected_type=type_hints["subject_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if idp_entity_id is not None:
            self._values["idp_entity_id"] = idp_entity_id
        if idp_metadata_url is not None:
            self._values["idp_metadata_url"] = idp_metadata_url
        if idp_pemtrustedcas_content is not None:
            self._values["idp_pemtrustedcas_content"] = idp_pemtrustedcas_content
        if roles_key is not None:
            self._values["roles_key"] = roles_key
        if sp_entity_id is not None:
            self._values["sp_entity_id"] = sp_entity_id
        if subject_key is not None:
            self._values["subject_key"] = subject_key

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable or disable OpenSearch SAML authentication.

        Enables or disables SAML-based authentication for OpenSearch. When enabled, users can authenticate using SAML with an Identity Provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def idp_entity_id(self) -> typing.Optional[builtins.str]:
        '''Identity Provider Entity ID.

        The unique identifier for the Identity Provider (IdP) entity that is used for SAML authentication. This value is typically provided by the IdP.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#idp_entity_id ManagedDatabaseOpensearch#idp_entity_id}
        '''
        result = self._values.get("idp_entity_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def idp_metadata_url(self) -> typing.Optional[builtins.str]:
        '''Identity Provider (IdP) SAML metadata URL.

        The URL of the SAML metadata for the Identity Provider (IdP). This is used to configure SAML-based authentication with the IdP.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#idp_metadata_url ManagedDatabaseOpensearch#idp_metadata_url}
        '''
        result = self._values.get("idp_metadata_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def idp_pemtrustedcas_content(self) -> typing.Optional[builtins.str]:
        '''PEM-encoded root CA Content for SAML IdP server verification.

        This parameter specifies the PEM-encoded root certificate authority (CA) content for the SAML identity provider (IdP) server verification. The root CA content is used to verify the SSL/TLS certificate presented by the server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#idp_pemtrustedcas_content ManagedDatabaseOpensearch#idp_pemtrustedcas_content}
        '''
        result = self._values.get("idp_pemtrustedcas_content")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def roles_key(self) -> typing.Optional[builtins.str]:
        '''SAML response role attribute.

        Optional. Specifies the attribute in the SAML response where role information is stored, if available. Role attributes are not required for SAML authentication, but can be included in SAML assertions by most Identity Providers (IdPs) to determine user access levels or permissions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#roles_key ManagedDatabaseOpensearch#roles_key}
        '''
        result = self._values.get("roles_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sp_entity_id(self) -> typing.Optional[builtins.str]:
        '''Service Provider Entity ID.

        The unique identifier for the Service Provider (SP) entity that is used for SAML authentication. This value is typically provided by the SP.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#sp_entity_id ManagedDatabaseOpensearch#sp_entity_id}
        '''
        result = self._values.get("sp_entity_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subject_key(self) -> typing.Optional[builtins.str]:
        '''SAML response subject attribute.

        Optional. Specifies the attribute in the SAML response where the subject identifier is stored. If not configured, the NameID attribute is used by default.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#subject_key ManagedDatabaseOpensearch#subject_key}
        '''
        result = self._values.get("subject_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesSaml(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchPropertiesSamlOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesSamlOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9006f804233866e0bcbcabfee80e240d58ca3aa0b270b35fca9e093fc1e32e9c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetIdpEntityId")
    def reset_idp_entity_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdpEntityId", []))

    @jsii.member(jsii_name="resetIdpMetadataUrl")
    def reset_idp_metadata_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdpMetadataUrl", []))

    @jsii.member(jsii_name="resetIdpPemtrustedcasContent")
    def reset_idp_pemtrustedcas_content(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdpPemtrustedcasContent", []))

    @jsii.member(jsii_name="resetRolesKey")
    def reset_roles_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRolesKey", []))

    @jsii.member(jsii_name="resetSpEntityId")
    def reset_sp_entity_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpEntityId", []))

    @jsii.member(jsii_name="resetSubjectKey")
    def reset_subject_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubjectKey", []))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="idpEntityIdInput")
    def idp_entity_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idpEntityIdInput"))

    @builtins.property
    @jsii.member(jsii_name="idpMetadataUrlInput")
    def idp_metadata_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idpMetadataUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="idpPemtrustedcasContentInput")
    def idp_pemtrustedcas_content_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idpPemtrustedcasContentInput"))

    @builtins.property
    @jsii.member(jsii_name="rolesKeyInput")
    def roles_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rolesKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="spEntityIdInput")
    def sp_entity_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "spEntityIdInput"))

    @builtins.property
    @jsii.member(jsii_name="subjectKeyInput")
    def subject_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subjectKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d469be80b1364917873721e8af88e7062483a039aaed7718db029f5ca170884)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="idpEntityId")
    def idp_entity_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "idpEntityId"))

    @idp_entity_id.setter
    def idp_entity_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__814ab6ecf48749b6d62f26b6567d61ef65ea0bfbbe19f1358d51810029ef998a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "idpEntityId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="idpMetadataUrl")
    def idp_metadata_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "idpMetadataUrl"))

    @idp_metadata_url.setter
    def idp_metadata_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__608b37237be872718973058fb30455a02be360f5053c70e96510693c9b9244d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "idpMetadataUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="idpPemtrustedcasContent")
    def idp_pemtrustedcas_content(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "idpPemtrustedcasContent"))

    @idp_pemtrustedcas_content.setter
    def idp_pemtrustedcas_content(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1814aa90ebfc251af6c91642e42ce08a47300fa1a8e3cacf378c1886d789c06)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "idpPemtrustedcasContent", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rolesKey")
    def roles_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rolesKey"))

    @roles_key.setter
    def roles_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e94553764dddbdb00b434cdebba04db1366d57e07aaf8f5c89ff45bf9529acbc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rolesKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="spEntityId")
    def sp_entity_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "spEntityId"))

    @sp_entity_id.setter
    def sp_entity_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecf9acff0d36a02176d62a477d13b9d21e0065d4067d1da39833b3dc9b1054ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spEntityId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subjectKey")
    def subject_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subjectKey"))

    @subject_key.setter
    def subject_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c2749a1852f09b8e903fc5f21f9fc37f4be29b4b73b365e767ca5ec1eed0097)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subjectKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesSaml]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesSaml], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesSaml],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3eef83ead552c9f4ef0503c6cd5db370ccfefde7338e3dca2b88ba0fdcc15ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesSearchBackpressure",
    jsii_struct_bases=[],
    name_mapping={
        "mode": "mode",
        "node_duress": "nodeDuress",
        "search_shard_task": "searchShardTask",
        "search_task": "searchTask",
    },
)
class ManagedDatabaseOpensearchPropertiesSearchBackpressure:
    def __init__(
        self,
        *,
        mode: typing.Optional[builtins.str] = None,
        node_duress: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesSearchBackpressureNodeDuress", typing.Dict[builtins.str, typing.Any]]] = None,
        search_shard_task: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchShardTask", typing.Dict[builtins.str, typing.Any]]] = None,
        search_task: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchTask", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param mode: The search backpressure mode. The search backpressure mode. Valid values are monitor_only, enforced, or disabled. Default is monitor_only. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#mode ManagedDatabaseOpensearch#mode}
        :param node_duress: node_duress block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#node_duress ManagedDatabaseOpensearch#node_duress}
        :param search_shard_task: search_shard_task block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#search_shard_task ManagedDatabaseOpensearch#search_shard_task}
        :param search_task: search_task block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#search_task ManagedDatabaseOpensearch#search_task}
        '''
        if isinstance(node_duress, dict):
            node_duress = ManagedDatabaseOpensearchPropertiesSearchBackpressureNodeDuress(**node_duress)
        if isinstance(search_shard_task, dict):
            search_shard_task = ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchShardTask(**search_shard_task)
        if isinstance(search_task, dict):
            search_task = ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchTask(**search_task)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__805f97b9e5a6105534a09bda5ae4938f7f200c78f7107c05aa43e852e3889554)
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
            check_type(argname="argument node_duress", value=node_duress, expected_type=type_hints["node_duress"])
            check_type(argname="argument search_shard_task", value=search_shard_task, expected_type=type_hints["search_shard_task"])
            check_type(argname="argument search_task", value=search_task, expected_type=type_hints["search_task"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if mode is not None:
            self._values["mode"] = mode
        if node_duress is not None:
            self._values["node_duress"] = node_duress
        if search_shard_task is not None:
            self._values["search_shard_task"] = search_shard_task
        if search_task is not None:
            self._values["search_task"] = search_task

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''The search backpressure mode. The search backpressure mode. Valid values are monitor_only, enforced, or disabled. Default is monitor_only.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#mode ManagedDatabaseOpensearch#mode}
        '''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_duress(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesSearchBackpressureNodeDuress"]:
        '''node_duress block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#node_duress ManagedDatabaseOpensearch#node_duress}
        '''
        result = self._values.get("node_duress")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesSearchBackpressureNodeDuress"], result)

    @builtins.property
    def search_shard_task(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchShardTask"]:
        '''search_shard_task block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#search_shard_task ManagedDatabaseOpensearch#search_shard_task}
        '''
        result = self._values.get("search_shard_task")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchShardTask"], result)

    @builtins.property
    def search_task(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchTask"]:
        '''search_task block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#search_task ManagedDatabaseOpensearch#search_task}
        '''
        result = self._values.get("search_task")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchTask"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesSearchBackpressure(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesSearchBackpressureNodeDuress",
    jsii_struct_bases=[],
    name_mapping={
        "cpu_threshold": "cpuThreshold",
        "heap_threshold": "heapThreshold",
        "num_successive_breaches": "numSuccessiveBreaches",
    },
)
class ManagedDatabaseOpensearchPropertiesSearchBackpressureNodeDuress:
    def __init__(
        self,
        *,
        cpu_threshold: typing.Optional[jsii.Number] = None,
        heap_threshold: typing.Optional[jsii.Number] = None,
        num_successive_breaches: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cpu_threshold: The CPU usage threshold (as a percentage) required for a node to be considered to be under duress. The CPU usage threshold (as a percentage) required for a node to be considered to be under duress. Default is 0.9. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cpu_threshold ManagedDatabaseOpensearch#cpu_threshold}
        :param heap_threshold: The heap usage threshold (as a percentage) required for a node to be considered to be under duress. The heap usage threshold (as a percentage) required for a node to be considered to be under duress. Default is 0.7. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#heap_threshold ManagedDatabaseOpensearch#heap_threshold}
        :param num_successive_breaches: The number of successive limit breaches after which the node is considered to be under duress. The number of successive limit breaches after which the node is considered to be under duress. Default is 3. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#num_successive_breaches ManagedDatabaseOpensearch#num_successive_breaches}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d39b711eab4461a4c1b96d616ef21c90bba1b606f922482a8bfe12b3daa624f)
            check_type(argname="argument cpu_threshold", value=cpu_threshold, expected_type=type_hints["cpu_threshold"])
            check_type(argname="argument heap_threshold", value=heap_threshold, expected_type=type_hints["heap_threshold"])
            check_type(argname="argument num_successive_breaches", value=num_successive_breaches, expected_type=type_hints["num_successive_breaches"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cpu_threshold is not None:
            self._values["cpu_threshold"] = cpu_threshold
        if heap_threshold is not None:
            self._values["heap_threshold"] = heap_threshold
        if num_successive_breaches is not None:
            self._values["num_successive_breaches"] = num_successive_breaches

    @builtins.property
    def cpu_threshold(self) -> typing.Optional[jsii.Number]:
        '''The CPU usage threshold (as a percentage) required for a node to be considered to be under duress.

        The CPU usage threshold (as a percentage) required for a node to be considered to be under duress. Default is 0.9.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cpu_threshold ManagedDatabaseOpensearch#cpu_threshold}
        '''
        result = self._values.get("cpu_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def heap_threshold(self) -> typing.Optional[jsii.Number]:
        '''The heap usage threshold (as a percentage) required for a node to be considered to be under duress.

        The heap usage threshold (as a percentage) required for a node to be considered to be under duress. Default is 0.7.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#heap_threshold ManagedDatabaseOpensearch#heap_threshold}
        '''
        result = self._values.get("heap_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def num_successive_breaches(self) -> typing.Optional[jsii.Number]:
        '''The number of successive limit breaches after which the node is considered to be under duress.

        The number of successive limit breaches after which the node is considered to be under duress. Default is 3.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#num_successive_breaches ManagedDatabaseOpensearch#num_successive_breaches}
        '''
        result = self._values.get("num_successive_breaches")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesSearchBackpressureNodeDuress(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchPropertiesSearchBackpressureNodeDuressOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesSearchBackpressureNodeDuressOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__59378e31f4cd6201c364bda38b88b6f38570309207761b21d5081dcd0f615b45)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCpuThreshold")
    def reset_cpu_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuThreshold", []))

    @jsii.member(jsii_name="resetHeapThreshold")
    def reset_heap_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeapThreshold", []))

    @jsii.member(jsii_name="resetNumSuccessiveBreaches")
    def reset_num_successive_breaches(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumSuccessiveBreaches", []))

    @builtins.property
    @jsii.member(jsii_name="cpuThresholdInput")
    def cpu_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cpuThresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="heapThresholdInput")
    def heap_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "heapThresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="numSuccessiveBreachesInput")
    def num_successive_breaches_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numSuccessiveBreachesInput"))

    @builtins.property
    @jsii.member(jsii_name="cpuThreshold")
    def cpu_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cpuThreshold"))

    @cpu_threshold.setter
    def cpu_threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f2da3c5a443b5809eec45d188e064b67733e4bf33b42120835068a003d3d85d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuThreshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="heapThreshold")
    def heap_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "heapThreshold"))

    @heap_threshold.setter
    def heap_threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6154536222d2a3ce408361d85a35cfef51b1b35a0846573a851b79b4f792c0e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "heapThreshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numSuccessiveBreaches")
    def num_successive_breaches(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numSuccessiveBreaches"))

    @num_successive_breaches.setter
    def num_successive_breaches(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c8c912fb67610b192ee3462abb62f58c7e902befe1f3bed88fe18276e982303)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numSuccessiveBreaches", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesSearchBackpressureNodeDuress]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesSearchBackpressureNodeDuress], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesSearchBackpressureNodeDuress],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f92228b2e318521cde3a3494dc8e2af648769323ff3412958f2d717ea853d01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ManagedDatabaseOpensearchPropertiesSearchBackpressureOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesSearchBackpressureOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4ee58dca98bdd2a102e2b6572f78fe85eeaa363b2520afc85444288b079a3b7f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putNodeDuress")
    def put_node_duress(
        self,
        *,
        cpu_threshold: typing.Optional[jsii.Number] = None,
        heap_threshold: typing.Optional[jsii.Number] = None,
        num_successive_breaches: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cpu_threshold: The CPU usage threshold (as a percentage) required for a node to be considered to be under duress. The CPU usage threshold (as a percentage) required for a node to be considered to be under duress. Default is 0.9. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cpu_threshold ManagedDatabaseOpensearch#cpu_threshold}
        :param heap_threshold: The heap usage threshold (as a percentage) required for a node to be considered to be under duress. The heap usage threshold (as a percentage) required for a node to be considered to be under duress. Default is 0.7. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#heap_threshold ManagedDatabaseOpensearch#heap_threshold}
        :param num_successive_breaches: The number of successive limit breaches after which the node is considered to be under duress. The number of successive limit breaches after which the node is considered to be under duress. Default is 3. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#num_successive_breaches ManagedDatabaseOpensearch#num_successive_breaches}
        '''
        value = ManagedDatabaseOpensearchPropertiesSearchBackpressureNodeDuress(
            cpu_threshold=cpu_threshold,
            heap_threshold=heap_threshold,
            num_successive_breaches=num_successive_breaches,
        )

        return typing.cast(None, jsii.invoke(self, "putNodeDuress", [value]))

    @jsii.member(jsii_name="putSearchShardTask")
    def put_search_shard_task(
        self,
        *,
        cancellation_burst: typing.Optional[jsii.Number] = None,
        cancellation_rate: typing.Optional[jsii.Number] = None,
        cancellation_ratio: typing.Optional[jsii.Number] = None,
        cpu_time_millis_threshold: typing.Optional[jsii.Number] = None,
        elapsed_time_millis_threshold: typing.Optional[jsii.Number] = None,
        heap_moving_average_window_size: typing.Optional[jsii.Number] = None,
        heap_percent_threshold: typing.Optional[jsii.Number] = None,
        heap_variance: typing.Optional[jsii.Number] = None,
        total_heap_percent_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cancellation_burst: The maximum number of search tasks to cancel in a single iteration of the observer thread. The maximum number of search tasks to cancel in a single iteration of the observer thread. Default is 10.0. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cancellation_burst ManagedDatabaseOpensearch#cancellation_burst}
        :param cancellation_rate: The maximum number of tasks to cancel per millisecond of elapsed time. The maximum number of tasks to cancel per millisecond of elapsed time. Default is 0.003. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cancellation_rate ManagedDatabaseOpensearch#cancellation_rate}
        :param cancellation_ratio: The maximum number of tasks to cancel. The maximum number of tasks to cancel, as a percentage of successful task completions. Default is 0.1. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cancellation_ratio ManagedDatabaseOpensearch#cancellation_ratio}
        :param cpu_time_millis_threshold: The CPU usage threshold (in milliseconds) required for a single search shard task before it is considered for cancellation. The CPU usage threshold (in milliseconds) required for a single search shard task before it is considered for cancellation. Default is 15000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cpu_time_millis_threshold ManagedDatabaseOpensearch#cpu_time_millis_threshold}
        :param elapsed_time_millis_threshold: The elapsed time threshold (in milliseconds) required for a single search shard task before it is considered for cancellation. The elapsed time threshold (in milliseconds) required for a single search shard task before it is considered for cancellation. Default is 30000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#elapsed_time_millis_threshold ManagedDatabaseOpensearch#elapsed_time_millis_threshold}
        :param heap_moving_average_window_size: The number of previously completed search shard tasks to consider when calculating the rolling average of heap usage. The number of previously completed search shard tasks to consider when calculating the rolling average of heap usage. Default is 100. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#heap_moving_average_window_size ManagedDatabaseOpensearch#heap_moving_average_window_size}
        :param heap_percent_threshold: The heap usage threshold (as a percentage) required for a single search shard task before it is considered for cancellation. The heap usage threshold (as a percentage) required for a single search shard task before it is considered for cancellation. Default is 0.5. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#heap_percent_threshold ManagedDatabaseOpensearch#heap_percent_threshold}
        :param heap_variance: The minimum variance required for a single search shard task’s heap usage compared to the rolling average of previously completed tasks before it is considered for cancellation. The minimum variance required for a single search shard task’s heap usage compared to the rolling average of previously completed tasks before it is considered for cancellation. Default is 2.0. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#heap_variance ManagedDatabaseOpensearch#heap_variance}
        :param total_heap_percent_threshold: The heap usage threshold (as a percentage) required for the sum of heap usages of all search shard tasks before cancellation is applied. The heap usage threshold (as a percentage) required for the sum of heap usages of all search shard tasks before cancellation is applied. Default is 0.5. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#total_heap_percent_threshold ManagedDatabaseOpensearch#total_heap_percent_threshold}
        '''
        value = ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchShardTask(
            cancellation_burst=cancellation_burst,
            cancellation_rate=cancellation_rate,
            cancellation_ratio=cancellation_ratio,
            cpu_time_millis_threshold=cpu_time_millis_threshold,
            elapsed_time_millis_threshold=elapsed_time_millis_threshold,
            heap_moving_average_window_size=heap_moving_average_window_size,
            heap_percent_threshold=heap_percent_threshold,
            heap_variance=heap_variance,
            total_heap_percent_threshold=total_heap_percent_threshold,
        )

        return typing.cast(None, jsii.invoke(self, "putSearchShardTask", [value]))

    @jsii.member(jsii_name="putSearchTask")
    def put_search_task(
        self,
        *,
        cancellation_burst: typing.Optional[jsii.Number] = None,
        cancellation_rate: typing.Optional[jsii.Number] = None,
        cancellation_ratio: typing.Optional[jsii.Number] = None,
        cpu_time_millis_threshold: typing.Optional[jsii.Number] = None,
        elapsed_time_millis_threshold: typing.Optional[jsii.Number] = None,
        heap_moving_average_window_size: typing.Optional[jsii.Number] = None,
        heap_percent_threshold: typing.Optional[jsii.Number] = None,
        heap_variance: typing.Optional[jsii.Number] = None,
        total_heap_percent_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cancellation_burst: The maximum number of search tasks to cancel in a single iteration of the observer thread. The maximum number of search tasks to cancel in a single iteration of the observer thread. Default is 5.0. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cancellation_burst ManagedDatabaseOpensearch#cancellation_burst}
        :param cancellation_rate: The maximum number of search tasks to cancel per millisecond of elapsed time. The maximum number of search tasks to cancel per millisecond of elapsed time. Default is 0.003. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cancellation_rate ManagedDatabaseOpensearch#cancellation_rate}
        :param cancellation_ratio: The maximum number of search tasks to cancel, as a percentage of successful search task completions. The maximum number of search tasks to cancel, as a percentage of successful search task completions. Default is 0.1. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cancellation_ratio ManagedDatabaseOpensearch#cancellation_ratio}
        :param cpu_time_millis_threshold: The CPU usage threshold (in milliseconds) required for an individual parent task before it is considered for cancellation. The CPU usage threshold (in milliseconds) required for an individual parent task before it is considered for cancellation. Default is 30000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cpu_time_millis_threshold ManagedDatabaseOpensearch#cpu_time_millis_threshold}
        :param elapsed_time_millis_threshold: The elapsed time threshold (in milliseconds) required for an individual parent task before it is considered for cancellation. The elapsed time threshold (in milliseconds) required for an individual parent task before it is considered for cancellation. Default is 45000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#elapsed_time_millis_threshold ManagedDatabaseOpensearch#elapsed_time_millis_threshold}
        :param heap_moving_average_window_size: The window size used to calculate the rolling average of the heap usage for the completed parent tasks. The window size used to calculate the rolling average of the heap usage for the completed parent tasks. Default is 10. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#heap_moving_average_window_size ManagedDatabaseOpensearch#heap_moving_average_window_size}
        :param heap_percent_threshold: The heap usage threshold (as a percentage) required for an individual parent task before it is considered for cancellation. The heap usage threshold (as a percentage) required for an individual parent task before it is considered for cancellation. Default is 0.2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#heap_percent_threshold ManagedDatabaseOpensearch#heap_percent_threshold}
        :param heap_variance: The heap usage variance required for an individual parent task before it is considered for cancellation. The heap usage variance required for an individual parent task before it is considered for cancellation. A task is considered for cancellation when taskHeapUsage is greater than or equal to heapUsageMovingAverage * variance. Default is 2.0. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#heap_variance ManagedDatabaseOpensearch#heap_variance}
        :param total_heap_percent_threshold: The heap usage threshold (as a percentage) required for the sum of heap usages of all search tasks before cancellation is applied. The heap usage threshold (as a percentage) required for the sum of heap usages of all search tasks before cancellation is applied. Default is 0.5. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#total_heap_percent_threshold ManagedDatabaseOpensearch#total_heap_percent_threshold}
        '''
        value = ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchTask(
            cancellation_burst=cancellation_burst,
            cancellation_rate=cancellation_rate,
            cancellation_ratio=cancellation_ratio,
            cpu_time_millis_threshold=cpu_time_millis_threshold,
            elapsed_time_millis_threshold=elapsed_time_millis_threshold,
            heap_moving_average_window_size=heap_moving_average_window_size,
            heap_percent_threshold=heap_percent_threshold,
            heap_variance=heap_variance,
            total_heap_percent_threshold=total_heap_percent_threshold,
        )

        return typing.cast(None, jsii.invoke(self, "putSearchTask", [value]))

    @jsii.member(jsii_name="resetMode")
    def reset_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMode", []))

    @jsii.member(jsii_name="resetNodeDuress")
    def reset_node_duress(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodeDuress", []))

    @jsii.member(jsii_name="resetSearchShardTask")
    def reset_search_shard_task(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSearchShardTask", []))

    @jsii.member(jsii_name="resetSearchTask")
    def reset_search_task(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSearchTask", []))

    @builtins.property
    @jsii.member(jsii_name="nodeDuress")
    def node_duress(
        self,
    ) -> ManagedDatabaseOpensearchPropertiesSearchBackpressureNodeDuressOutputReference:
        return typing.cast(ManagedDatabaseOpensearchPropertiesSearchBackpressureNodeDuressOutputReference, jsii.get(self, "nodeDuress"))

    @builtins.property
    @jsii.member(jsii_name="searchShardTask")
    def search_shard_task(
        self,
    ) -> "ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchShardTaskOutputReference":
        return typing.cast("ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchShardTaskOutputReference", jsii.get(self, "searchShardTask"))

    @builtins.property
    @jsii.member(jsii_name="searchTask")
    def search_task(
        self,
    ) -> "ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchTaskOutputReference":
        return typing.cast("ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchTaskOutputReference", jsii.get(self, "searchTask"))

    @builtins.property
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modeInput"))

    @builtins.property
    @jsii.member(jsii_name="nodeDuressInput")
    def node_duress_input(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesSearchBackpressureNodeDuress]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesSearchBackpressureNodeDuress], jsii.get(self, "nodeDuressInput"))

    @builtins.property
    @jsii.member(jsii_name="searchShardTaskInput")
    def search_shard_task_input(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchShardTask"]:
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchShardTask"], jsii.get(self, "searchShardTaskInput"))

    @builtins.property
    @jsii.member(jsii_name="searchTaskInput")
    def search_task_input(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchTask"]:
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchTask"], jsii.get(self, "searchTaskInput"))

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59438a0bf07b464ca34125d05eb0622f3179f66fd3e2abb87e7897f12bf80d24)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesSearchBackpressure]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesSearchBackpressure], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesSearchBackpressure],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d199f7493f2c000b226300b70baaf081c1006c6f92609eded529318d5bb81856)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchShardTask",
    jsii_struct_bases=[],
    name_mapping={
        "cancellation_burst": "cancellationBurst",
        "cancellation_rate": "cancellationRate",
        "cancellation_ratio": "cancellationRatio",
        "cpu_time_millis_threshold": "cpuTimeMillisThreshold",
        "elapsed_time_millis_threshold": "elapsedTimeMillisThreshold",
        "heap_moving_average_window_size": "heapMovingAverageWindowSize",
        "heap_percent_threshold": "heapPercentThreshold",
        "heap_variance": "heapVariance",
        "total_heap_percent_threshold": "totalHeapPercentThreshold",
    },
)
class ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchShardTask:
    def __init__(
        self,
        *,
        cancellation_burst: typing.Optional[jsii.Number] = None,
        cancellation_rate: typing.Optional[jsii.Number] = None,
        cancellation_ratio: typing.Optional[jsii.Number] = None,
        cpu_time_millis_threshold: typing.Optional[jsii.Number] = None,
        elapsed_time_millis_threshold: typing.Optional[jsii.Number] = None,
        heap_moving_average_window_size: typing.Optional[jsii.Number] = None,
        heap_percent_threshold: typing.Optional[jsii.Number] = None,
        heap_variance: typing.Optional[jsii.Number] = None,
        total_heap_percent_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cancellation_burst: The maximum number of search tasks to cancel in a single iteration of the observer thread. The maximum number of search tasks to cancel in a single iteration of the observer thread. Default is 10.0. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cancellation_burst ManagedDatabaseOpensearch#cancellation_burst}
        :param cancellation_rate: The maximum number of tasks to cancel per millisecond of elapsed time. The maximum number of tasks to cancel per millisecond of elapsed time. Default is 0.003. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cancellation_rate ManagedDatabaseOpensearch#cancellation_rate}
        :param cancellation_ratio: The maximum number of tasks to cancel. The maximum number of tasks to cancel, as a percentage of successful task completions. Default is 0.1. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cancellation_ratio ManagedDatabaseOpensearch#cancellation_ratio}
        :param cpu_time_millis_threshold: The CPU usage threshold (in milliseconds) required for a single search shard task before it is considered for cancellation. The CPU usage threshold (in milliseconds) required for a single search shard task before it is considered for cancellation. Default is 15000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cpu_time_millis_threshold ManagedDatabaseOpensearch#cpu_time_millis_threshold}
        :param elapsed_time_millis_threshold: The elapsed time threshold (in milliseconds) required for a single search shard task before it is considered for cancellation. The elapsed time threshold (in milliseconds) required for a single search shard task before it is considered for cancellation. Default is 30000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#elapsed_time_millis_threshold ManagedDatabaseOpensearch#elapsed_time_millis_threshold}
        :param heap_moving_average_window_size: The number of previously completed search shard tasks to consider when calculating the rolling average of heap usage. The number of previously completed search shard tasks to consider when calculating the rolling average of heap usage. Default is 100. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#heap_moving_average_window_size ManagedDatabaseOpensearch#heap_moving_average_window_size}
        :param heap_percent_threshold: The heap usage threshold (as a percentage) required for a single search shard task before it is considered for cancellation. The heap usage threshold (as a percentage) required for a single search shard task before it is considered for cancellation. Default is 0.5. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#heap_percent_threshold ManagedDatabaseOpensearch#heap_percent_threshold}
        :param heap_variance: The minimum variance required for a single search shard task’s heap usage compared to the rolling average of previously completed tasks before it is considered for cancellation. The minimum variance required for a single search shard task’s heap usage compared to the rolling average of previously completed tasks before it is considered for cancellation. Default is 2.0. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#heap_variance ManagedDatabaseOpensearch#heap_variance}
        :param total_heap_percent_threshold: The heap usage threshold (as a percentage) required for the sum of heap usages of all search shard tasks before cancellation is applied. The heap usage threshold (as a percentage) required for the sum of heap usages of all search shard tasks before cancellation is applied. Default is 0.5. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#total_heap_percent_threshold ManagedDatabaseOpensearch#total_heap_percent_threshold}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b00773335f5cd697d7f58058999e1087b88965f82632c43cd0fda0432f5c39f)
            check_type(argname="argument cancellation_burst", value=cancellation_burst, expected_type=type_hints["cancellation_burst"])
            check_type(argname="argument cancellation_rate", value=cancellation_rate, expected_type=type_hints["cancellation_rate"])
            check_type(argname="argument cancellation_ratio", value=cancellation_ratio, expected_type=type_hints["cancellation_ratio"])
            check_type(argname="argument cpu_time_millis_threshold", value=cpu_time_millis_threshold, expected_type=type_hints["cpu_time_millis_threshold"])
            check_type(argname="argument elapsed_time_millis_threshold", value=elapsed_time_millis_threshold, expected_type=type_hints["elapsed_time_millis_threshold"])
            check_type(argname="argument heap_moving_average_window_size", value=heap_moving_average_window_size, expected_type=type_hints["heap_moving_average_window_size"])
            check_type(argname="argument heap_percent_threshold", value=heap_percent_threshold, expected_type=type_hints["heap_percent_threshold"])
            check_type(argname="argument heap_variance", value=heap_variance, expected_type=type_hints["heap_variance"])
            check_type(argname="argument total_heap_percent_threshold", value=total_heap_percent_threshold, expected_type=type_hints["total_heap_percent_threshold"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cancellation_burst is not None:
            self._values["cancellation_burst"] = cancellation_burst
        if cancellation_rate is not None:
            self._values["cancellation_rate"] = cancellation_rate
        if cancellation_ratio is not None:
            self._values["cancellation_ratio"] = cancellation_ratio
        if cpu_time_millis_threshold is not None:
            self._values["cpu_time_millis_threshold"] = cpu_time_millis_threshold
        if elapsed_time_millis_threshold is not None:
            self._values["elapsed_time_millis_threshold"] = elapsed_time_millis_threshold
        if heap_moving_average_window_size is not None:
            self._values["heap_moving_average_window_size"] = heap_moving_average_window_size
        if heap_percent_threshold is not None:
            self._values["heap_percent_threshold"] = heap_percent_threshold
        if heap_variance is not None:
            self._values["heap_variance"] = heap_variance
        if total_heap_percent_threshold is not None:
            self._values["total_heap_percent_threshold"] = total_heap_percent_threshold

    @builtins.property
    def cancellation_burst(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of search tasks to cancel in a single iteration of the observer thread.

        The maximum number of search tasks to cancel in a single iteration of the observer thread. Default is 10.0.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cancellation_burst ManagedDatabaseOpensearch#cancellation_burst}
        '''
        result = self._values.get("cancellation_burst")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cancellation_rate(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of tasks to cancel per millisecond of elapsed time.

        The maximum number of tasks to cancel per millisecond of elapsed time. Default is 0.003.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cancellation_rate ManagedDatabaseOpensearch#cancellation_rate}
        '''
        result = self._values.get("cancellation_rate")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cancellation_ratio(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of tasks to cancel.

        The maximum number of tasks to cancel, as a percentage of successful task completions. Default is 0.1.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cancellation_ratio ManagedDatabaseOpensearch#cancellation_ratio}
        '''
        result = self._values.get("cancellation_ratio")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cpu_time_millis_threshold(self) -> typing.Optional[jsii.Number]:
        '''The CPU usage threshold (in milliseconds) required for a single search shard task before it is considered for cancellation.

        The CPU usage threshold (in milliseconds) required for a single search shard task before it is considered for cancellation. Default is 15000.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cpu_time_millis_threshold ManagedDatabaseOpensearch#cpu_time_millis_threshold}
        '''
        result = self._values.get("cpu_time_millis_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def elapsed_time_millis_threshold(self) -> typing.Optional[jsii.Number]:
        '''The elapsed time threshold (in milliseconds) required for a single search shard task before it is considered for cancellation.

        The elapsed time threshold (in milliseconds) required for a single search shard task before it is considered for cancellation. Default is 30000.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#elapsed_time_millis_threshold ManagedDatabaseOpensearch#elapsed_time_millis_threshold}
        '''
        result = self._values.get("elapsed_time_millis_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def heap_moving_average_window_size(self) -> typing.Optional[jsii.Number]:
        '''The number of previously completed search shard tasks to consider when calculating the rolling average of heap usage.

        The number of previously completed search shard tasks to consider when calculating the rolling average of heap usage. Default is 100.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#heap_moving_average_window_size ManagedDatabaseOpensearch#heap_moving_average_window_size}
        '''
        result = self._values.get("heap_moving_average_window_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def heap_percent_threshold(self) -> typing.Optional[jsii.Number]:
        '''The heap usage threshold (as a percentage) required for a single search shard task before it is considered for cancellation.

        The heap usage threshold (as a percentage) required for a single search shard task before it is considered for cancellation. Default is 0.5.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#heap_percent_threshold ManagedDatabaseOpensearch#heap_percent_threshold}
        '''
        result = self._values.get("heap_percent_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def heap_variance(self) -> typing.Optional[jsii.Number]:
        '''The minimum variance required for a single search shard task’s heap usage compared to the rolling average of previously completed tasks before it is considered for cancellation.

        The minimum variance required for a single search shard task’s heap usage compared to the rolling average of previously completed tasks before it is considered for cancellation. Default is 2.0.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#heap_variance ManagedDatabaseOpensearch#heap_variance}
        '''
        result = self._values.get("heap_variance")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def total_heap_percent_threshold(self) -> typing.Optional[jsii.Number]:
        '''The heap usage threshold (as a percentage) required for the sum of heap usages of all search shard tasks before cancellation is applied.

        The heap usage threshold (as a percentage) required for the sum of heap usages of all search shard tasks before cancellation is applied. Default is 0.5.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#total_heap_percent_threshold ManagedDatabaseOpensearch#total_heap_percent_threshold}
        '''
        result = self._values.get("total_heap_percent_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchShardTask(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchShardTaskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchShardTaskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2f804c6e61b9f50dbdd61773a74c3e8afc03e032f98aee1aa97ebf6ffccfb7bc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCancellationBurst")
    def reset_cancellation_burst(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCancellationBurst", []))

    @jsii.member(jsii_name="resetCancellationRate")
    def reset_cancellation_rate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCancellationRate", []))

    @jsii.member(jsii_name="resetCancellationRatio")
    def reset_cancellation_ratio(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCancellationRatio", []))

    @jsii.member(jsii_name="resetCpuTimeMillisThreshold")
    def reset_cpu_time_millis_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuTimeMillisThreshold", []))

    @jsii.member(jsii_name="resetElapsedTimeMillisThreshold")
    def reset_elapsed_time_millis_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetElapsedTimeMillisThreshold", []))

    @jsii.member(jsii_name="resetHeapMovingAverageWindowSize")
    def reset_heap_moving_average_window_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeapMovingAverageWindowSize", []))

    @jsii.member(jsii_name="resetHeapPercentThreshold")
    def reset_heap_percent_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeapPercentThreshold", []))

    @jsii.member(jsii_name="resetHeapVariance")
    def reset_heap_variance(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeapVariance", []))

    @jsii.member(jsii_name="resetTotalHeapPercentThreshold")
    def reset_total_heap_percent_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTotalHeapPercentThreshold", []))

    @builtins.property
    @jsii.member(jsii_name="cancellationBurstInput")
    def cancellation_burst_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cancellationBurstInput"))

    @builtins.property
    @jsii.member(jsii_name="cancellationRateInput")
    def cancellation_rate_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cancellationRateInput"))

    @builtins.property
    @jsii.member(jsii_name="cancellationRatioInput")
    def cancellation_ratio_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cancellationRatioInput"))

    @builtins.property
    @jsii.member(jsii_name="cpuTimeMillisThresholdInput")
    def cpu_time_millis_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cpuTimeMillisThresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="elapsedTimeMillisThresholdInput")
    def elapsed_time_millis_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "elapsedTimeMillisThresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="heapMovingAverageWindowSizeInput")
    def heap_moving_average_window_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "heapMovingAverageWindowSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="heapPercentThresholdInput")
    def heap_percent_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "heapPercentThresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="heapVarianceInput")
    def heap_variance_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "heapVarianceInput"))

    @builtins.property
    @jsii.member(jsii_name="totalHeapPercentThresholdInput")
    def total_heap_percent_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "totalHeapPercentThresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="cancellationBurst")
    def cancellation_burst(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cancellationBurst"))

    @cancellation_burst.setter
    def cancellation_burst(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f108b14c1e006b3bcc6d425fe8211a20712d24a3819dfe5282d7691a85aa33e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cancellationBurst", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cancellationRate")
    def cancellation_rate(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cancellationRate"))

    @cancellation_rate.setter
    def cancellation_rate(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06b5a829eb31d417a55412068d78f6b0d8cc9ddec00eff4e7cd3977dd7cb220f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cancellationRate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cancellationRatio")
    def cancellation_ratio(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cancellationRatio"))

    @cancellation_ratio.setter
    def cancellation_ratio(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__958b2bb0a9c540cf94b080ec29e1e5fbd9c1eccc6b0f76721eb7556ebd5f304a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cancellationRatio", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cpuTimeMillisThreshold")
    def cpu_time_millis_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cpuTimeMillisThreshold"))

    @cpu_time_millis_threshold.setter
    def cpu_time_millis_threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__418e25f5c93bcdcdad5dfb9588fa1ef68f91e1805449a4ebe0863cd9e236dd10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuTimeMillisThreshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="elapsedTimeMillisThreshold")
    def elapsed_time_millis_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "elapsedTimeMillisThreshold"))

    @elapsed_time_millis_threshold.setter
    def elapsed_time_millis_threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc232fd43df166748d3e1067024548b6294d59ffb154cd820ea942add2307684)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "elapsedTimeMillisThreshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="heapMovingAverageWindowSize")
    def heap_moving_average_window_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "heapMovingAverageWindowSize"))

    @heap_moving_average_window_size.setter
    def heap_moving_average_window_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__148f2fa12f2ab2b039fefea9a071860481923f97e2ecdd3e6d6c963f30aa2e1b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "heapMovingAverageWindowSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="heapPercentThreshold")
    def heap_percent_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "heapPercentThreshold"))

    @heap_percent_threshold.setter
    def heap_percent_threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6609ecf296fecc3af6bda9c2302dcc426b51abaa327fc9faa6812b9a075d3e9b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "heapPercentThreshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="heapVariance")
    def heap_variance(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "heapVariance"))

    @heap_variance.setter
    def heap_variance(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__058ac4dba8c69f12eac4a1c56b99c448e10926597b85c9de8a85050346f284af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "heapVariance", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="totalHeapPercentThreshold")
    def total_heap_percent_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "totalHeapPercentThreshold"))

    @total_heap_percent_threshold.setter
    def total_heap_percent_threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9beee3db3d9a9a0e1f2a338f8d566dad145af24446f43479404ef603069ba180)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "totalHeapPercentThreshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchShardTask]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchShardTask], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchShardTask],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0580e72b91eb41bcd047005aceb043de5835de8fa3c97079618b8126f372372)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchTask",
    jsii_struct_bases=[],
    name_mapping={
        "cancellation_burst": "cancellationBurst",
        "cancellation_rate": "cancellationRate",
        "cancellation_ratio": "cancellationRatio",
        "cpu_time_millis_threshold": "cpuTimeMillisThreshold",
        "elapsed_time_millis_threshold": "elapsedTimeMillisThreshold",
        "heap_moving_average_window_size": "heapMovingAverageWindowSize",
        "heap_percent_threshold": "heapPercentThreshold",
        "heap_variance": "heapVariance",
        "total_heap_percent_threshold": "totalHeapPercentThreshold",
    },
)
class ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchTask:
    def __init__(
        self,
        *,
        cancellation_burst: typing.Optional[jsii.Number] = None,
        cancellation_rate: typing.Optional[jsii.Number] = None,
        cancellation_ratio: typing.Optional[jsii.Number] = None,
        cpu_time_millis_threshold: typing.Optional[jsii.Number] = None,
        elapsed_time_millis_threshold: typing.Optional[jsii.Number] = None,
        heap_moving_average_window_size: typing.Optional[jsii.Number] = None,
        heap_percent_threshold: typing.Optional[jsii.Number] = None,
        heap_variance: typing.Optional[jsii.Number] = None,
        total_heap_percent_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cancellation_burst: The maximum number of search tasks to cancel in a single iteration of the observer thread. The maximum number of search tasks to cancel in a single iteration of the observer thread. Default is 5.0. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cancellation_burst ManagedDatabaseOpensearch#cancellation_burst}
        :param cancellation_rate: The maximum number of search tasks to cancel per millisecond of elapsed time. The maximum number of search tasks to cancel per millisecond of elapsed time. Default is 0.003. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cancellation_rate ManagedDatabaseOpensearch#cancellation_rate}
        :param cancellation_ratio: The maximum number of search tasks to cancel, as a percentage of successful search task completions. The maximum number of search tasks to cancel, as a percentage of successful search task completions. Default is 0.1. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cancellation_ratio ManagedDatabaseOpensearch#cancellation_ratio}
        :param cpu_time_millis_threshold: The CPU usage threshold (in milliseconds) required for an individual parent task before it is considered for cancellation. The CPU usage threshold (in milliseconds) required for an individual parent task before it is considered for cancellation. Default is 30000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cpu_time_millis_threshold ManagedDatabaseOpensearch#cpu_time_millis_threshold}
        :param elapsed_time_millis_threshold: The elapsed time threshold (in milliseconds) required for an individual parent task before it is considered for cancellation. The elapsed time threshold (in milliseconds) required for an individual parent task before it is considered for cancellation. Default is 45000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#elapsed_time_millis_threshold ManagedDatabaseOpensearch#elapsed_time_millis_threshold}
        :param heap_moving_average_window_size: The window size used to calculate the rolling average of the heap usage for the completed parent tasks. The window size used to calculate the rolling average of the heap usage for the completed parent tasks. Default is 10. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#heap_moving_average_window_size ManagedDatabaseOpensearch#heap_moving_average_window_size}
        :param heap_percent_threshold: The heap usage threshold (as a percentage) required for an individual parent task before it is considered for cancellation. The heap usage threshold (as a percentage) required for an individual parent task before it is considered for cancellation. Default is 0.2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#heap_percent_threshold ManagedDatabaseOpensearch#heap_percent_threshold}
        :param heap_variance: The heap usage variance required for an individual parent task before it is considered for cancellation. The heap usage variance required for an individual parent task before it is considered for cancellation. A task is considered for cancellation when taskHeapUsage is greater than or equal to heapUsageMovingAverage * variance. Default is 2.0. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#heap_variance ManagedDatabaseOpensearch#heap_variance}
        :param total_heap_percent_threshold: The heap usage threshold (as a percentage) required for the sum of heap usages of all search tasks before cancellation is applied. The heap usage threshold (as a percentage) required for the sum of heap usages of all search tasks before cancellation is applied. Default is 0.5. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#total_heap_percent_threshold ManagedDatabaseOpensearch#total_heap_percent_threshold}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c70c1faa9e9872e82b30ac5de548218cf7b3888e93ee8b9564bce272a55c420)
            check_type(argname="argument cancellation_burst", value=cancellation_burst, expected_type=type_hints["cancellation_burst"])
            check_type(argname="argument cancellation_rate", value=cancellation_rate, expected_type=type_hints["cancellation_rate"])
            check_type(argname="argument cancellation_ratio", value=cancellation_ratio, expected_type=type_hints["cancellation_ratio"])
            check_type(argname="argument cpu_time_millis_threshold", value=cpu_time_millis_threshold, expected_type=type_hints["cpu_time_millis_threshold"])
            check_type(argname="argument elapsed_time_millis_threshold", value=elapsed_time_millis_threshold, expected_type=type_hints["elapsed_time_millis_threshold"])
            check_type(argname="argument heap_moving_average_window_size", value=heap_moving_average_window_size, expected_type=type_hints["heap_moving_average_window_size"])
            check_type(argname="argument heap_percent_threshold", value=heap_percent_threshold, expected_type=type_hints["heap_percent_threshold"])
            check_type(argname="argument heap_variance", value=heap_variance, expected_type=type_hints["heap_variance"])
            check_type(argname="argument total_heap_percent_threshold", value=total_heap_percent_threshold, expected_type=type_hints["total_heap_percent_threshold"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cancellation_burst is not None:
            self._values["cancellation_burst"] = cancellation_burst
        if cancellation_rate is not None:
            self._values["cancellation_rate"] = cancellation_rate
        if cancellation_ratio is not None:
            self._values["cancellation_ratio"] = cancellation_ratio
        if cpu_time_millis_threshold is not None:
            self._values["cpu_time_millis_threshold"] = cpu_time_millis_threshold
        if elapsed_time_millis_threshold is not None:
            self._values["elapsed_time_millis_threshold"] = elapsed_time_millis_threshold
        if heap_moving_average_window_size is not None:
            self._values["heap_moving_average_window_size"] = heap_moving_average_window_size
        if heap_percent_threshold is not None:
            self._values["heap_percent_threshold"] = heap_percent_threshold
        if heap_variance is not None:
            self._values["heap_variance"] = heap_variance
        if total_heap_percent_threshold is not None:
            self._values["total_heap_percent_threshold"] = total_heap_percent_threshold

    @builtins.property
    def cancellation_burst(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of search tasks to cancel in a single iteration of the observer thread.

        The maximum number of search tasks to cancel in a single iteration of the observer thread. Default is 5.0.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cancellation_burst ManagedDatabaseOpensearch#cancellation_burst}
        '''
        result = self._values.get("cancellation_burst")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cancellation_rate(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of search tasks to cancel per millisecond of elapsed time.

        The maximum number of search tasks to cancel per millisecond of elapsed time. Default is 0.003.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cancellation_rate ManagedDatabaseOpensearch#cancellation_rate}
        '''
        result = self._values.get("cancellation_rate")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cancellation_ratio(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of search tasks to cancel, as a percentage of successful search task completions.

        The maximum number of search tasks to cancel, as a percentage of successful search task completions. Default is 0.1.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cancellation_ratio ManagedDatabaseOpensearch#cancellation_ratio}
        '''
        result = self._values.get("cancellation_ratio")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cpu_time_millis_threshold(self) -> typing.Optional[jsii.Number]:
        '''The CPU usage threshold (in milliseconds) required for an individual parent task before it is considered for cancellation.

        The CPU usage threshold (in milliseconds) required for an individual parent task before it is considered for cancellation. Default is 30000.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cpu_time_millis_threshold ManagedDatabaseOpensearch#cpu_time_millis_threshold}
        '''
        result = self._values.get("cpu_time_millis_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def elapsed_time_millis_threshold(self) -> typing.Optional[jsii.Number]:
        '''The elapsed time threshold (in milliseconds) required for an individual parent task before it is considered for cancellation.

        The elapsed time threshold (in milliseconds) required for an individual parent task before it is considered for cancellation. Default is 45000.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#elapsed_time_millis_threshold ManagedDatabaseOpensearch#elapsed_time_millis_threshold}
        '''
        result = self._values.get("elapsed_time_millis_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def heap_moving_average_window_size(self) -> typing.Optional[jsii.Number]:
        '''The window size used to calculate the rolling average of the heap usage for the completed parent tasks.

        The window size used to calculate the rolling average of the heap usage for the completed parent tasks. Default is 10.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#heap_moving_average_window_size ManagedDatabaseOpensearch#heap_moving_average_window_size}
        '''
        result = self._values.get("heap_moving_average_window_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def heap_percent_threshold(self) -> typing.Optional[jsii.Number]:
        '''The heap usage threshold (as a percentage) required for an individual parent task before it is considered for cancellation.

        The heap usage threshold (as a percentage) required for an individual parent task before it is considered for cancellation. Default is 0.2.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#heap_percent_threshold ManagedDatabaseOpensearch#heap_percent_threshold}
        '''
        result = self._values.get("heap_percent_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def heap_variance(self) -> typing.Optional[jsii.Number]:
        '''The heap usage variance required for an individual parent task before it is considered for cancellation.

        The heap usage variance required for an individual parent task before it is considered for cancellation. A task is considered for cancellation when taskHeapUsage is greater than or equal to heapUsageMovingAverage * variance. Default is 2.0.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#heap_variance ManagedDatabaseOpensearch#heap_variance}
        '''
        result = self._values.get("heap_variance")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def total_heap_percent_threshold(self) -> typing.Optional[jsii.Number]:
        '''The heap usage threshold (as a percentage) required for the sum of heap usages of all search tasks before cancellation is applied.

        The heap usage threshold (as a percentage) required for the sum of heap usages of all search tasks before cancellation is applied. Default is 0.5.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#total_heap_percent_threshold ManagedDatabaseOpensearch#total_heap_percent_threshold}
        '''
        result = self._values.get("total_heap_percent_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchTask(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchTaskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchTaskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__eb68300a3716965aa0739e17464200040f8410e9f8cbfb0de5bd51b840f7841a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCancellationBurst")
    def reset_cancellation_burst(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCancellationBurst", []))

    @jsii.member(jsii_name="resetCancellationRate")
    def reset_cancellation_rate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCancellationRate", []))

    @jsii.member(jsii_name="resetCancellationRatio")
    def reset_cancellation_ratio(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCancellationRatio", []))

    @jsii.member(jsii_name="resetCpuTimeMillisThreshold")
    def reset_cpu_time_millis_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuTimeMillisThreshold", []))

    @jsii.member(jsii_name="resetElapsedTimeMillisThreshold")
    def reset_elapsed_time_millis_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetElapsedTimeMillisThreshold", []))

    @jsii.member(jsii_name="resetHeapMovingAverageWindowSize")
    def reset_heap_moving_average_window_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeapMovingAverageWindowSize", []))

    @jsii.member(jsii_name="resetHeapPercentThreshold")
    def reset_heap_percent_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeapPercentThreshold", []))

    @jsii.member(jsii_name="resetHeapVariance")
    def reset_heap_variance(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeapVariance", []))

    @jsii.member(jsii_name="resetTotalHeapPercentThreshold")
    def reset_total_heap_percent_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTotalHeapPercentThreshold", []))

    @builtins.property
    @jsii.member(jsii_name="cancellationBurstInput")
    def cancellation_burst_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cancellationBurstInput"))

    @builtins.property
    @jsii.member(jsii_name="cancellationRateInput")
    def cancellation_rate_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cancellationRateInput"))

    @builtins.property
    @jsii.member(jsii_name="cancellationRatioInput")
    def cancellation_ratio_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cancellationRatioInput"))

    @builtins.property
    @jsii.member(jsii_name="cpuTimeMillisThresholdInput")
    def cpu_time_millis_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cpuTimeMillisThresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="elapsedTimeMillisThresholdInput")
    def elapsed_time_millis_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "elapsedTimeMillisThresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="heapMovingAverageWindowSizeInput")
    def heap_moving_average_window_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "heapMovingAverageWindowSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="heapPercentThresholdInput")
    def heap_percent_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "heapPercentThresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="heapVarianceInput")
    def heap_variance_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "heapVarianceInput"))

    @builtins.property
    @jsii.member(jsii_name="totalHeapPercentThresholdInput")
    def total_heap_percent_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "totalHeapPercentThresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="cancellationBurst")
    def cancellation_burst(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cancellationBurst"))

    @cancellation_burst.setter
    def cancellation_burst(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f011251c4054e5a2f9f0d8ca1da2019dc1c416fa17bfbf254af7cc16f8650327)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cancellationBurst", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cancellationRate")
    def cancellation_rate(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cancellationRate"))

    @cancellation_rate.setter
    def cancellation_rate(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9d9b604e956a1438c3dcbdb13a64b082101ec26baab2814dbd6485ee27dc328)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cancellationRate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cancellationRatio")
    def cancellation_ratio(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cancellationRatio"))

    @cancellation_ratio.setter
    def cancellation_ratio(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__731378f09e674acfd4cb1106c09d76c14e022ecba7d606d41302ee614bc09bae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cancellationRatio", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cpuTimeMillisThreshold")
    def cpu_time_millis_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cpuTimeMillisThreshold"))

    @cpu_time_millis_threshold.setter
    def cpu_time_millis_threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__548de9238ad329c51e89e200692774c420ff4f058fbd2be43eb3b92e19d8e3f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuTimeMillisThreshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="elapsedTimeMillisThreshold")
    def elapsed_time_millis_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "elapsedTimeMillisThreshold"))

    @elapsed_time_millis_threshold.setter
    def elapsed_time_millis_threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0c404670c846add12b8db9028df0dd2c1c4ced077ca983140b69dc55f6a3c6e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "elapsedTimeMillisThreshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="heapMovingAverageWindowSize")
    def heap_moving_average_window_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "heapMovingAverageWindowSize"))

    @heap_moving_average_window_size.setter
    def heap_moving_average_window_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b01af9bbe1d7c211255b8dc962c9aa13e183cd9ac3ebb05f9be2017ccc2f030)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "heapMovingAverageWindowSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="heapPercentThreshold")
    def heap_percent_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "heapPercentThreshold"))

    @heap_percent_threshold.setter
    def heap_percent_threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e31b26ab229e38083cbd838766c8927e810d896ca91a578fd20be7064d4ea0b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "heapPercentThreshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="heapVariance")
    def heap_variance(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "heapVariance"))

    @heap_variance.setter
    def heap_variance(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ce6dec80d334a78f1ea07ca3dec7cc150ff1506b65ac8c3e4362e84d12fd7f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "heapVariance", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="totalHeapPercentThreshold")
    def total_heap_percent_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "totalHeapPercentThreshold"))

    @total_heap_percent_threshold.setter
    def total_heap_percent_threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b772c62b59d8d9b7c922635138cfdb94021055caa57f4c06a201173b2a90f72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "totalHeapPercentThreshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchTask]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchTask], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchTask],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eed630a0a87e30594d254415564dc323657cbe20478aa9957e0510fb9688286d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueries",
    jsii_struct_bases=[],
    name_mapping={"cpu": "cpu", "latency": "latency", "memory": "memory"},
)
class ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueries:
    def __init__(
        self,
        *,
        cpu: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesCpu", typing.Dict[builtins.str, typing.Any]]] = None,
        latency: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesLatency", typing.Dict[builtins.str, typing.Any]]] = None,
        memory: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesMemory", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param cpu: cpu block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cpu ManagedDatabaseOpensearch#cpu}
        :param latency: latency block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#latency ManagedDatabaseOpensearch#latency}
        :param memory: memory block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#memory ManagedDatabaseOpensearch#memory}
        '''
        if isinstance(cpu, dict):
            cpu = ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesCpu(**cpu)
        if isinstance(latency, dict):
            latency = ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesLatency(**latency)
        if isinstance(memory, dict):
            memory = ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesMemory(**memory)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d48540eb48253b4690ae28a201bd0c2656eeb882644f670058d040de533de63)
            check_type(argname="argument cpu", value=cpu, expected_type=type_hints["cpu"])
            check_type(argname="argument latency", value=latency, expected_type=type_hints["latency"])
            check_type(argname="argument memory", value=memory, expected_type=type_hints["memory"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cpu is not None:
            self._values["cpu"] = cpu
        if latency is not None:
            self._values["latency"] = latency
        if memory is not None:
            self._values["memory"] = memory

    @builtins.property
    def cpu(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesCpu"]:
        '''cpu block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#cpu ManagedDatabaseOpensearch#cpu}
        '''
        result = self._values.get("cpu")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesCpu"], result)

    @builtins.property
    def latency(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesLatency"]:
        '''latency block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#latency ManagedDatabaseOpensearch#latency}
        '''
        result = self._values.get("latency")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesLatency"], result)

    @builtins.property
    def memory(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesMemory"]:
        '''memory block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#memory ManagedDatabaseOpensearch#memory}
        '''
        result = self._values.get("memory")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesMemory"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueries(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesCpu",
    jsii_struct_bases=[],
    name_mapping={
        "enabled": "enabled",
        "top_n_size": "topNSize",
        "window_size": "windowSize",
    },
)
class ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesCpu:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        top_n_size: typing.Optional[jsii.Number] = None,
        window_size: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Enable or disable top N query monitoring by the metric. Enable or disable top N query monitoring by the metric. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        :param top_n_size: Specify the value of N for the top N queries by the metric. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#top_n_size ManagedDatabaseOpensearch#top_n_size}
        :param window_size: The window size of the top N queries by the metric. Configure the window size of the top N queries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#window_size ManagedDatabaseOpensearch#window_size}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d766d1d3c272cdb4b9cf1f83e27dff76cdbba937c7c5a6167ca8bf17039385f)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument top_n_size", value=top_n_size, expected_type=type_hints["top_n_size"])
            check_type(argname="argument window_size", value=window_size, expected_type=type_hints["window_size"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if top_n_size is not None:
            self._values["top_n_size"] = top_n_size
        if window_size is not None:
            self._values["window_size"] = window_size

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable or disable top N query monitoring by the metric.

        Enable or disable top N query monitoring by the metric.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def top_n_size(self) -> typing.Optional[jsii.Number]:
        '''Specify the value of N for the top N queries by the metric.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#top_n_size ManagedDatabaseOpensearch#top_n_size}
        '''
        result = self._values.get("top_n_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def window_size(self) -> typing.Optional[builtins.str]:
        '''The window size of the top N queries by the metric.

        Configure the window size of the top N queries.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#window_size ManagedDatabaseOpensearch#window_size}
        '''
        result = self._values.get("window_size")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesCpu(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesCpuOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesCpuOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1d5962e931b874e9f7ab5e5f7438de4de506b33512e4bf1db8ed3f578a4397b4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetTopNSize")
    def reset_top_n_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTopNSize", []))

    @jsii.member(jsii_name="resetWindowSize")
    def reset_window_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWindowSize", []))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="topNSizeInput")
    def top_n_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "topNSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="windowSizeInput")
    def window_size_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "windowSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c566b4e58830f7450ab54cdc5ad8b232fcdc22a85ded360eb32927e19391415b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="topNSize")
    def top_n_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "topNSize"))

    @top_n_size.setter
    def top_n_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9656f062bc576f9b07a0395445a8bd121599de63e79f3b1ea39a05fbfec94892)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "topNSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="windowSize")
    def window_size(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "windowSize"))

    @window_size.setter
    def window_size(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78a35a1f301fcd9b30c7ae5fbd4bbc9ec8046797e0a9cf9713c7f8eb74d7ec5d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "windowSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesCpu]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesCpu], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesCpu],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5196bba0013f06e7ffc62eae3cdf60b50a09516ef07225892521ad448f132e01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesLatency",
    jsii_struct_bases=[],
    name_mapping={
        "enabled": "enabled",
        "top_n_size": "topNSize",
        "window_size": "windowSize",
    },
)
class ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesLatency:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        top_n_size: typing.Optional[jsii.Number] = None,
        window_size: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Enable or disable top N query monitoring by the metric. Enable or disable top N query monitoring by the metric. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        :param top_n_size: Specify the value of N for the top N queries by the metric. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#top_n_size ManagedDatabaseOpensearch#top_n_size}
        :param window_size: The window size of the top N queries by the metric. Configure the window size of the top N queries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#window_size ManagedDatabaseOpensearch#window_size}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af605383a3698bbbbd930e4ff42d3558bc2b49d2a45ef275ee19f303369ab414)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument top_n_size", value=top_n_size, expected_type=type_hints["top_n_size"])
            check_type(argname="argument window_size", value=window_size, expected_type=type_hints["window_size"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if top_n_size is not None:
            self._values["top_n_size"] = top_n_size
        if window_size is not None:
            self._values["window_size"] = window_size

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable or disable top N query monitoring by the metric.

        Enable or disable top N query monitoring by the metric.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def top_n_size(self) -> typing.Optional[jsii.Number]:
        '''Specify the value of N for the top N queries by the metric.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#top_n_size ManagedDatabaseOpensearch#top_n_size}
        '''
        result = self._values.get("top_n_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def window_size(self) -> typing.Optional[builtins.str]:
        '''The window size of the top N queries by the metric.

        Configure the window size of the top N queries.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#window_size ManagedDatabaseOpensearch#window_size}
        '''
        result = self._values.get("window_size")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesLatency(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesLatencyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesLatencyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1db8915b762bb83cee8f09c8c2587676181353e6416f6ce83a301cce5d37031c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetTopNSize")
    def reset_top_n_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTopNSize", []))

    @jsii.member(jsii_name="resetWindowSize")
    def reset_window_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWindowSize", []))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="topNSizeInput")
    def top_n_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "topNSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="windowSizeInput")
    def window_size_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "windowSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4f31ccf61d6ad91d9d6537c8eb3050a37589c776869b257ca260fd425aaa6d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="topNSize")
    def top_n_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "topNSize"))

    @top_n_size.setter
    def top_n_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cc3a7e1ac13e5967087288faa477a91f073fde072c273be6e3bb9642b6510f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "topNSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="windowSize")
    def window_size(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "windowSize"))

    @window_size.setter
    def window_size(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__daf65203437b117b5aad96a21b85738efe93a3c6397a41005287daf2689c6f68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "windowSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesLatency]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesLatency], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesLatency],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfeebd32e0797c42f022cd01695f87fea69c78b53dd94074570331a5eed74645)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesMemory",
    jsii_struct_bases=[],
    name_mapping={
        "enabled": "enabled",
        "top_n_size": "topNSize",
        "window_size": "windowSize",
    },
)
class ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesMemory:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        top_n_size: typing.Optional[jsii.Number] = None,
        window_size: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Enable or disable top N query monitoring by the metric. Enable or disable top N query monitoring by the metric. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        :param top_n_size: Specify the value of N for the top N queries by the metric. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#top_n_size ManagedDatabaseOpensearch#top_n_size}
        :param window_size: The window size of the top N queries by the metric. Configure the window size of the top N queries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#window_size ManagedDatabaseOpensearch#window_size}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8f1e26fb94e46db6ae20ea187b2ad98f67fdc7bd6181ac39e4a17900b83dedd)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument top_n_size", value=top_n_size, expected_type=type_hints["top_n_size"])
            check_type(argname="argument window_size", value=window_size, expected_type=type_hints["window_size"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if top_n_size is not None:
            self._values["top_n_size"] = top_n_size
        if window_size is not None:
            self._values["window_size"] = window_size

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable or disable top N query monitoring by the metric.

        Enable or disable top N query monitoring by the metric.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def top_n_size(self) -> typing.Optional[jsii.Number]:
        '''Specify the value of N for the top N queries by the metric.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#top_n_size ManagedDatabaseOpensearch#top_n_size}
        '''
        result = self._values.get("top_n_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def window_size(self) -> typing.Optional[builtins.str]:
        '''The window size of the top N queries by the metric.

        Configure the window size of the top N queries.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#window_size ManagedDatabaseOpensearch#window_size}
        '''
        result = self._values.get("window_size")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesMemory(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesMemoryOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesMemoryOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0c7996c4148c3487cd4a0b6c34800f557119ff6e610e44e5e52c5b4cccb5f11e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetTopNSize")
    def reset_top_n_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTopNSize", []))

    @jsii.member(jsii_name="resetWindowSize")
    def reset_window_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWindowSize", []))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="topNSizeInput")
    def top_n_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "topNSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="windowSizeInput")
    def window_size_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "windowSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1dc368d8d4da1d3a1403f015eece87acc2dbb75f1b9043c989c57a4cf7f4cd20)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="topNSize")
    def top_n_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "topNSize"))

    @top_n_size.setter
    def top_n_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d59f46ab37e6e48e49ef775fafef4727d6a45005dba13d505e62c57a3be2af8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "topNSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="windowSize")
    def window_size(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "windowSize"))

    @window_size.setter
    def window_size(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__555cfc577bffd5e159cabab8507aa4c904ac32d7e3475475e368117642de8709)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "windowSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesMemory]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesMemory], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesMemory],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__851229a5e5379f4ff018059170242ff6ff7b18521656568fca27f0a09ebbf7ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a438c41538b402d8b9bb0e310691458cf458e06f1e054fbd7d66c6a6891f6345)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putCpu")
    def put_cpu(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        top_n_size: typing.Optional[jsii.Number] = None,
        window_size: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Enable or disable top N query monitoring by the metric. Enable or disable top N query monitoring by the metric. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        :param top_n_size: Specify the value of N for the top N queries by the metric. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#top_n_size ManagedDatabaseOpensearch#top_n_size}
        :param window_size: The window size of the top N queries by the metric. Configure the window size of the top N queries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#window_size ManagedDatabaseOpensearch#window_size}
        '''
        value = ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesCpu(
            enabled=enabled, top_n_size=top_n_size, window_size=window_size
        )

        return typing.cast(None, jsii.invoke(self, "putCpu", [value]))

    @jsii.member(jsii_name="putLatency")
    def put_latency(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        top_n_size: typing.Optional[jsii.Number] = None,
        window_size: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Enable or disable top N query monitoring by the metric. Enable or disable top N query monitoring by the metric. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        :param top_n_size: Specify the value of N for the top N queries by the metric. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#top_n_size ManagedDatabaseOpensearch#top_n_size}
        :param window_size: The window size of the top N queries by the metric. Configure the window size of the top N queries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#window_size ManagedDatabaseOpensearch#window_size}
        '''
        value = ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesLatency(
            enabled=enabled, top_n_size=top_n_size, window_size=window_size
        )

        return typing.cast(None, jsii.invoke(self, "putLatency", [value]))

    @jsii.member(jsii_name="putMemory")
    def put_memory(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        top_n_size: typing.Optional[jsii.Number] = None,
        window_size: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Enable or disable top N query monitoring by the metric. Enable or disable top N query monitoring by the metric. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        :param top_n_size: Specify the value of N for the top N queries by the metric. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#top_n_size ManagedDatabaseOpensearch#top_n_size}
        :param window_size: The window size of the top N queries by the metric. Configure the window size of the top N queries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#window_size ManagedDatabaseOpensearch#window_size}
        '''
        value = ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesMemory(
            enabled=enabled, top_n_size=top_n_size, window_size=window_size
        )

        return typing.cast(None, jsii.invoke(self, "putMemory", [value]))

    @jsii.member(jsii_name="resetCpu")
    def reset_cpu(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpu", []))

    @jsii.member(jsii_name="resetLatency")
    def reset_latency(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLatency", []))

    @jsii.member(jsii_name="resetMemory")
    def reset_memory(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemory", []))

    @builtins.property
    @jsii.member(jsii_name="cpu")
    def cpu(
        self,
    ) -> ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesCpuOutputReference:
        return typing.cast(ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesCpuOutputReference, jsii.get(self, "cpu"))

    @builtins.property
    @jsii.member(jsii_name="latency")
    def latency(
        self,
    ) -> ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesLatencyOutputReference:
        return typing.cast(ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesLatencyOutputReference, jsii.get(self, "latency"))

    @builtins.property
    @jsii.member(jsii_name="memory")
    def memory(
        self,
    ) -> ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesMemoryOutputReference:
        return typing.cast(ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesMemoryOutputReference, jsii.get(self, "memory"))

    @builtins.property
    @jsii.member(jsii_name="cpuInput")
    def cpu_input(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesCpu]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesCpu], jsii.get(self, "cpuInput"))

    @builtins.property
    @jsii.member(jsii_name="latencyInput")
    def latency_input(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesLatency]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesLatency], jsii.get(self, "latencyInput"))

    @builtins.property
    @jsii.member(jsii_name="memoryInput")
    def memory_input(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesMemory]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesMemory], jsii.get(self, "memoryInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueries]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueries], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueries],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9317c4bd4bf51d262cb77b52440acd892fcfc9deb0b110bf7c69ce4a7caaa6ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesSegrep",
    jsii_struct_bases=[],
    name_mapping={
        "pressure_checkpoint_limit": "pressureCheckpointLimit",
        "pressure_enabled": "pressureEnabled",
        "pressure_replica_stale_limit": "pressureReplicaStaleLimit",
        "pressure_time_limit": "pressureTimeLimit",
    },
)
class ManagedDatabaseOpensearchPropertiesSegrep:
    def __init__(
        self,
        *,
        pressure_checkpoint_limit: typing.Optional[jsii.Number] = None,
        pressure_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        pressure_replica_stale_limit: typing.Optional[jsii.Number] = None,
        pressure_time_limit: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param pressure_checkpoint_limit: The maximum number of indexing checkpoints that a replica shard can fall behind when copying from primary. Once ``segrep.pressure.checkpoint.limit`` is breached along with ``segrep.pressure.time.limit``, the segment replication backpressure mechanism is initiated. Default is 4 checkpoints. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#pressure_checkpoint_limit ManagedDatabaseOpensearch#pressure_checkpoint_limit}
        :param pressure_enabled: Enables the segment replication backpressure mechanism. Default is false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#pressure_enabled ManagedDatabaseOpensearch#pressure_enabled}
        :param pressure_replica_stale_limit: The maximum number of stale replica shards that can exist in a replication group. Once ``segrep.pressure.replica.stale.limit`` is breached, the segment replication backpressure mechanism is initiated. Default is .5, which is 50% of a replication group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#pressure_replica_stale_limit ManagedDatabaseOpensearch#pressure_replica_stale_limit}
        :param pressure_time_limit: The maximum amount of time that a replica shard can take to copy from the primary shard. Once segrep.pressure.time.limit is breached along with segrep.pressure.checkpoint.limit, the segment replication backpressure mechanism is initiated. Default is 5 minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#pressure_time_limit ManagedDatabaseOpensearch#pressure_time_limit}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9a29cf3d5cc5ae1d0c9f47a3e6bd31c5ad02450141253c8c11375bd90c2137f)
            check_type(argname="argument pressure_checkpoint_limit", value=pressure_checkpoint_limit, expected_type=type_hints["pressure_checkpoint_limit"])
            check_type(argname="argument pressure_enabled", value=pressure_enabled, expected_type=type_hints["pressure_enabled"])
            check_type(argname="argument pressure_replica_stale_limit", value=pressure_replica_stale_limit, expected_type=type_hints["pressure_replica_stale_limit"])
            check_type(argname="argument pressure_time_limit", value=pressure_time_limit, expected_type=type_hints["pressure_time_limit"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if pressure_checkpoint_limit is not None:
            self._values["pressure_checkpoint_limit"] = pressure_checkpoint_limit
        if pressure_enabled is not None:
            self._values["pressure_enabled"] = pressure_enabled
        if pressure_replica_stale_limit is not None:
            self._values["pressure_replica_stale_limit"] = pressure_replica_stale_limit
        if pressure_time_limit is not None:
            self._values["pressure_time_limit"] = pressure_time_limit

    @builtins.property
    def pressure_checkpoint_limit(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of indexing checkpoints that a replica shard can fall behind when copying from primary.

        Once ``segrep.pressure.checkpoint.limit`` is breached along with ``segrep.pressure.time.limit``, the segment replication backpressure mechanism is initiated. Default is 4 checkpoints.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#pressure_checkpoint_limit ManagedDatabaseOpensearch#pressure_checkpoint_limit}
        '''
        result = self._values.get("pressure_checkpoint_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def pressure_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enables the segment replication backpressure mechanism. Default is false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#pressure_enabled ManagedDatabaseOpensearch#pressure_enabled}
        '''
        result = self._values.get("pressure_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def pressure_replica_stale_limit(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of stale replica shards that can exist in a replication group.

        Once ``segrep.pressure.replica.stale.limit`` is breached, the segment replication backpressure mechanism is initiated. Default is .5, which is 50% of a replication group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#pressure_replica_stale_limit ManagedDatabaseOpensearch#pressure_replica_stale_limit}
        '''
        result = self._values.get("pressure_replica_stale_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def pressure_time_limit(self) -> typing.Optional[builtins.str]:
        '''The maximum amount of time that a replica shard can take to copy from the primary shard.

        Once segrep.pressure.time.limit is breached along with segrep.pressure.checkpoint.limit, the segment replication backpressure mechanism is initiated. Default is 5 minutes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#pressure_time_limit ManagedDatabaseOpensearch#pressure_time_limit}
        '''
        result = self._values.get("pressure_time_limit")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesSegrep(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchPropertiesSegrepOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesSegrepOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a9da31e1fc75c1a98cd7eaba9e7de567232e771faa66cd7e2cd34338934c30f9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetPressureCheckpointLimit")
    def reset_pressure_checkpoint_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPressureCheckpointLimit", []))

    @jsii.member(jsii_name="resetPressureEnabled")
    def reset_pressure_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPressureEnabled", []))

    @jsii.member(jsii_name="resetPressureReplicaStaleLimit")
    def reset_pressure_replica_stale_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPressureReplicaStaleLimit", []))

    @jsii.member(jsii_name="resetPressureTimeLimit")
    def reset_pressure_time_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPressureTimeLimit", []))

    @builtins.property
    @jsii.member(jsii_name="pressureCheckpointLimitInput")
    def pressure_checkpoint_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "pressureCheckpointLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="pressureEnabledInput")
    def pressure_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "pressureEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="pressureReplicaStaleLimitInput")
    def pressure_replica_stale_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "pressureReplicaStaleLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="pressureTimeLimitInput")
    def pressure_time_limit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pressureTimeLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="pressureCheckpointLimit")
    def pressure_checkpoint_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "pressureCheckpointLimit"))

    @pressure_checkpoint_limit.setter
    def pressure_checkpoint_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4723698c764c50efc62be0e8f65280c6509ef8ee02f4afb753ac826498205ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pressureCheckpointLimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pressureEnabled")
    def pressure_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "pressureEnabled"))

    @pressure_enabled.setter
    def pressure_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef3029aa6191c0ba9a6e087ee2f190ce88aa8d1b8cbe7d1c3c383c4bb181e1ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pressureEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pressureReplicaStaleLimit")
    def pressure_replica_stale_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "pressureReplicaStaleLimit"))

    @pressure_replica_stale_limit.setter
    def pressure_replica_stale_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c298308bacd7294b38a8ac1012c412f9b25be54bb42e178bb20e8764121e10a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pressureReplicaStaleLimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pressureTimeLimit")
    def pressure_time_limit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pressureTimeLimit"))

    @pressure_time_limit.setter
    def pressure_time_limit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6528f27f2b94a77fccca0a03dc16a26dfbfae9bd5994e696cccb18723681a701)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pressureTimeLimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesSegrep]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesSegrep], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesSegrep],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__954d28124997316766dd128bf9febd598356be3ffb2b0b392d63f1b92ed12457)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesShardIndexingPressure",
    jsii_struct_bases=[],
    name_mapping={
        "enabled": "enabled",
        "enforced": "enforced",
        "operating_factor": "operatingFactor",
        "primary_parameter": "primaryParameter",
    },
)
class ManagedDatabaseOpensearchPropertiesShardIndexingPressure:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enforced: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        operating_factor: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesShardIndexingPressureOperatingFactor", typing.Dict[builtins.str, typing.Any]]] = None,
        primary_parameter: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameter", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param enabled: Enable or disable shard indexing backpressure. Enable or disable shard indexing backpressure. Default is false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        :param enforced: Run shard indexing backpressure in shadow mode or enforced mode. Run shard indexing backpressure in shadow mode or enforced mode. In shadow mode (value set as false), shard indexing backpressure tracks all granular-level metrics, but it doesn’t actually reject any indexing requests. In enforced mode (value set as true), shard indexing backpressure rejects any requests to the cluster that might cause a dip in its performance. Default is false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enforced ManagedDatabaseOpensearch#enforced}
        :param operating_factor: operating_factor block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#operating_factor ManagedDatabaseOpensearch#operating_factor}
        :param primary_parameter: primary_parameter block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#primary_parameter ManagedDatabaseOpensearch#primary_parameter}
        '''
        if isinstance(operating_factor, dict):
            operating_factor = ManagedDatabaseOpensearchPropertiesShardIndexingPressureOperatingFactor(**operating_factor)
        if isinstance(primary_parameter, dict):
            primary_parameter = ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameter(**primary_parameter)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eea2862c5f0d31396bcb60288f73bd2a482b2c0d5fecb40f6e155d69cdb9084d)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument enforced", value=enforced, expected_type=type_hints["enforced"])
            check_type(argname="argument operating_factor", value=operating_factor, expected_type=type_hints["operating_factor"])
            check_type(argname="argument primary_parameter", value=primary_parameter, expected_type=type_hints["primary_parameter"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if enforced is not None:
            self._values["enforced"] = enforced
        if operating_factor is not None:
            self._values["operating_factor"] = operating_factor
        if primary_parameter is not None:
            self._values["primary_parameter"] = primary_parameter

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable or disable shard indexing backpressure. Enable or disable shard indexing backpressure. Default is false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enabled ManagedDatabaseOpensearch#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enforced(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Run shard indexing backpressure in shadow mode or enforced mode.

        Run shard indexing backpressure in shadow mode or enforced mode.
        In shadow mode (value set as false), shard indexing backpressure tracks all granular-level metrics,
        but it doesn’t actually reject any indexing requests.
        In enforced mode (value set as true),
        shard indexing backpressure rejects any requests to the cluster that might cause a dip in its performance.
        Default is false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#enforced ManagedDatabaseOpensearch#enforced}
        '''
        result = self._values.get("enforced")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def operating_factor(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesShardIndexingPressureOperatingFactor"]:
        '''operating_factor block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#operating_factor ManagedDatabaseOpensearch#operating_factor}
        '''
        result = self._values.get("operating_factor")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesShardIndexingPressureOperatingFactor"], result)

    @builtins.property
    def primary_parameter(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameter"]:
        '''primary_parameter block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#primary_parameter ManagedDatabaseOpensearch#primary_parameter}
        '''
        result = self._values.get("primary_parameter")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameter"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesShardIndexingPressure(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesShardIndexingPressureOperatingFactor",
    jsii_struct_bases=[],
    name_mapping={"lower": "lower", "optimal": "optimal", "upper": "upper"},
)
class ManagedDatabaseOpensearchPropertiesShardIndexingPressureOperatingFactor:
    def __init__(
        self,
        *,
        lower: typing.Optional[jsii.Number] = None,
        optimal: typing.Optional[jsii.Number] = None,
        upper: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param lower: Lower occupancy limit of the allocated quota of memory for the shard. Specify the lower occupancy limit of the allocated quota of memory for the shard. If the total memory usage of a shard is below this limit, shard indexing backpressure decreases the current allocated memory for that shard. Default is 0.75. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#lower ManagedDatabaseOpensearch#lower}
        :param optimal: Optimal occupancy of the allocated quota of memory for the shard. Specify the optimal occupancy of the allocated quota of memory for the shard. If the total memory usage of a shard is at this level, shard indexing backpressure doesn’t change the current allocated memory for that shard. Default is 0.85. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#optimal ManagedDatabaseOpensearch#optimal}
        :param upper: Upper occupancy limit of the allocated quota of memory for the shard. Specify the upper occupancy limit of the allocated quota of memory for the shard. If the total memory usage of a shard is above this limit, shard indexing backpressure increases the current allocated memory for that shard. Default is 0.95. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#upper ManagedDatabaseOpensearch#upper}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c2a585c78e0ebd7884489c51c18d79c728f4e6cf96723e8f1445b9a17a8bcb8)
            check_type(argname="argument lower", value=lower, expected_type=type_hints["lower"])
            check_type(argname="argument optimal", value=optimal, expected_type=type_hints["optimal"])
            check_type(argname="argument upper", value=upper, expected_type=type_hints["upper"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if lower is not None:
            self._values["lower"] = lower
        if optimal is not None:
            self._values["optimal"] = optimal
        if upper is not None:
            self._values["upper"] = upper

    @builtins.property
    def lower(self) -> typing.Optional[jsii.Number]:
        '''Lower occupancy limit of the allocated quota of memory for the shard.

        Specify the lower occupancy limit of the allocated quota of memory for the shard.
        If the total memory usage of a shard is below this limit,
        shard indexing backpressure decreases the current allocated memory for that shard.
        Default is 0.75.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#lower ManagedDatabaseOpensearch#lower}
        '''
        result = self._values.get("lower")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def optimal(self) -> typing.Optional[jsii.Number]:
        '''Optimal occupancy of the allocated quota of memory for the shard.

        Specify the optimal occupancy of the allocated quota of memory for the shard.
        If the total memory usage of a shard is at this level,
        shard indexing backpressure doesn’t change the current allocated memory for that shard.
        Default is 0.85.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#optimal ManagedDatabaseOpensearch#optimal}
        '''
        result = self._values.get("optimal")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def upper(self) -> typing.Optional[jsii.Number]:
        '''Upper occupancy limit of the allocated quota of memory for the shard.

        Specify the upper occupancy limit of the allocated quota of memory for the shard.
        If the total memory usage of a shard is above this limit,
        shard indexing backpressure increases the current allocated memory for that shard.
        Default is 0.95.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#upper ManagedDatabaseOpensearch#upper}
        '''
        result = self._values.get("upper")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesShardIndexingPressureOperatingFactor(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchPropertiesShardIndexingPressureOperatingFactorOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesShardIndexingPressureOperatingFactorOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e246cb950dc762e7a7e14c8d5ce7fe16db345693d083cf9d47fe835eaa32364b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetLower")
    def reset_lower(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLower", []))

    @jsii.member(jsii_name="resetOptimal")
    def reset_optimal(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOptimal", []))

    @jsii.member(jsii_name="resetUpper")
    def reset_upper(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpper", []))

    @builtins.property
    @jsii.member(jsii_name="lowerInput")
    def lower_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "lowerInput"))

    @builtins.property
    @jsii.member(jsii_name="optimalInput")
    def optimal_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "optimalInput"))

    @builtins.property
    @jsii.member(jsii_name="upperInput")
    def upper_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "upperInput"))

    @builtins.property
    @jsii.member(jsii_name="lower")
    def lower(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lower"))

    @lower.setter
    def lower(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20d701974306f722b43b37c7685ac55b61db2d530f42015c1aa2dd560f2d515c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lower", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="optimal")
    def optimal(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "optimal"))

    @optimal.setter
    def optimal(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4c6252daae2131b97906db1abcd58b4e77574142b36ad81d5d5647835fcb0a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "optimal", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="upper")
    def upper(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "upper"))

    @upper.setter
    def upper(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd5c63c967ebf10a5cf575aaba8815e67ce2878b8f6b192bfd644b5df1dbe454)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "upper", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesShardIndexingPressureOperatingFactor]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesShardIndexingPressureOperatingFactor], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesShardIndexingPressureOperatingFactor],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbe0ff08c3ff852e4ea101582100860b534c74a9f0f49ab9360c5323fbb9bf24)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ManagedDatabaseOpensearchPropertiesShardIndexingPressureOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesShardIndexingPressureOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b33a13b7ed9dcb82bdedc7aa4c42760418159bb6c42b9a3c415a66737cd64f7c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putOperatingFactor")
    def put_operating_factor(
        self,
        *,
        lower: typing.Optional[jsii.Number] = None,
        optimal: typing.Optional[jsii.Number] = None,
        upper: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param lower: Lower occupancy limit of the allocated quota of memory for the shard. Specify the lower occupancy limit of the allocated quota of memory for the shard. If the total memory usage of a shard is below this limit, shard indexing backpressure decreases the current allocated memory for that shard. Default is 0.75. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#lower ManagedDatabaseOpensearch#lower}
        :param optimal: Optimal occupancy of the allocated quota of memory for the shard. Specify the optimal occupancy of the allocated quota of memory for the shard. If the total memory usage of a shard is at this level, shard indexing backpressure doesn’t change the current allocated memory for that shard. Default is 0.85. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#optimal ManagedDatabaseOpensearch#optimal}
        :param upper: Upper occupancy limit of the allocated quota of memory for the shard. Specify the upper occupancy limit of the allocated quota of memory for the shard. If the total memory usage of a shard is above this limit, shard indexing backpressure increases the current allocated memory for that shard. Default is 0.95. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#upper ManagedDatabaseOpensearch#upper}
        '''
        value = ManagedDatabaseOpensearchPropertiesShardIndexingPressureOperatingFactor(
            lower=lower, optimal=optimal, upper=upper
        )

        return typing.cast(None, jsii.invoke(self, "putOperatingFactor", [value]))

    @jsii.member(jsii_name="putPrimaryParameter")
    def put_primary_parameter(
        self,
        *,
        node_attribute: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterNode", typing.Dict[builtins.str, typing.Any]]] = None,
        shard: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterShard", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param node_attribute: node block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#node ManagedDatabaseOpensearch#node}
        :param shard: shard block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#shard ManagedDatabaseOpensearch#shard}
        '''
        value = ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameter(
            node_attribute=node_attribute, shard=shard
        )

        return typing.cast(None, jsii.invoke(self, "putPrimaryParameter", [value]))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetEnforced")
    def reset_enforced(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnforced", []))

    @jsii.member(jsii_name="resetOperatingFactor")
    def reset_operating_factor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperatingFactor", []))

    @jsii.member(jsii_name="resetPrimaryParameter")
    def reset_primary_parameter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrimaryParameter", []))

    @builtins.property
    @jsii.member(jsii_name="operatingFactor")
    def operating_factor(
        self,
    ) -> ManagedDatabaseOpensearchPropertiesShardIndexingPressureOperatingFactorOutputReference:
        return typing.cast(ManagedDatabaseOpensearchPropertiesShardIndexingPressureOperatingFactorOutputReference, jsii.get(self, "operatingFactor"))

    @builtins.property
    @jsii.member(jsii_name="primaryParameter")
    def primary_parameter(
        self,
    ) -> "ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterOutputReference":
        return typing.cast("ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterOutputReference", jsii.get(self, "primaryParameter"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="enforcedInput")
    def enforced_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enforcedInput"))

    @builtins.property
    @jsii.member(jsii_name="operatingFactorInput")
    def operating_factor_input(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesShardIndexingPressureOperatingFactor]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesShardIndexingPressureOperatingFactor], jsii.get(self, "operatingFactorInput"))

    @builtins.property
    @jsii.member(jsii_name="primaryParameterInput")
    def primary_parameter_input(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameter"]:
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameter"], jsii.get(self, "primaryParameterInput"))

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f36cbe8ea87c863f8547b379d77f5d561bba6062d81d16d9eb55910568823c50)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enforced")
    def enforced(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enforced"))

    @enforced.setter
    def enforced(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08e82d879f8f210b3d91f31b0c17b5c27a58c2209ef2a4dc3d34fe2fc9b03742)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enforced", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesShardIndexingPressure]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesShardIndexingPressure], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesShardIndexingPressure],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85cdbf1751ba4796b5cd0b9e8b24f0e9c7f3a8fed73f201b276457d8c8779016)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameter",
    jsii_struct_bases=[],
    name_mapping={"node_attribute": "nodeAttribute", "shard": "shard"},
)
class ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameter:
    def __init__(
        self,
        *,
        node_attribute: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterNode", typing.Dict[builtins.str, typing.Any]]] = None,
        shard: typing.Optional[typing.Union["ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterShard", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param node_attribute: node block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#node ManagedDatabaseOpensearch#node}
        :param shard: shard block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#shard ManagedDatabaseOpensearch#shard}
        '''
        if isinstance(node_attribute, dict):
            node_attribute = ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterNode(**node_attribute)
        if isinstance(shard, dict):
            shard = ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterShard(**shard)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6cbaac709f053962d06f3c94d810fad956ee10e361e216e769dfcca117244cdb)
            check_type(argname="argument node_attribute", value=node_attribute, expected_type=type_hints["node_attribute"])
            check_type(argname="argument shard", value=shard, expected_type=type_hints["shard"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if node_attribute is not None:
            self._values["node_attribute"] = node_attribute
        if shard is not None:
            self._values["shard"] = shard

    @builtins.property
    def node_attribute(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterNode"]:
        '''node block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#node ManagedDatabaseOpensearch#node}
        '''
        result = self._values.get("node_attribute")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterNode"], result)

    @builtins.property
    def shard(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterShard"]:
        '''shard block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#shard ManagedDatabaseOpensearch#shard}
        '''
        result = self._values.get("shard")
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterShard"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterNode",
    jsii_struct_bases=[],
    name_mapping={"soft_limit": "softLimit"},
)
class ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterNode:
    def __init__(self, *, soft_limit: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param soft_limit: Node soft limit. Define the percentage of the node-level memory threshold that acts as a soft indicator for strain on a node. Default is 0.7. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#soft_limit ManagedDatabaseOpensearch#soft_limit}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95918dc70f50ad9e3281b3f7d9734e2c0361a87e02f2466a872b57e27e96e88b)
            check_type(argname="argument soft_limit", value=soft_limit, expected_type=type_hints["soft_limit"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if soft_limit is not None:
            self._values["soft_limit"] = soft_limit

    @builtins.property
    def soft_limit(self) -> typing.Optional[jsii.Number]:
        '''Node soft limit.

        Define the percentage of the node-level memory
        threshold that acts as a soft indicator for strain on a node.
        Default is 0.7.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#soft_limit ManagedDatabaseOpensearch#soft_limit}
        '''
        result = self._values.get("soft_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterNode(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterNodeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterNodeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__69f5fbeaf1b377102840e627dfa704a1c44a8f231a489c99bf1d8837728fd750)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetSoftLimit")
    def reset_soft_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSoftLimit", []))

    @builtins.property
    @jsii.member(jsii_name="softLimitInput")
    def soft_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "softLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="softLimit")
    def soft_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "softLimit"))

    @soft_limit.setter
    def soft_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa3ef487ff0ab79d3448b30fd602224e5920930d3ece53c6ce1f3aebfdf21a15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "softLimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterNode]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterNode], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterNode],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f25656eae56e547cb057a25d07612a6eb1c6cb415004c8ef7c7096fe3204714e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cc81668fe15038bf2abc0120b1e6f589b383a39206888122ca850044329a3bfd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putNodeAttribute")
    def put_node_attribute(
        self,
        *,
        soft_limit: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param soft_limit: Node soft limit. Define the percentage of the node-level memory threshold that acts as a soft indicator for strain on a node. Default is 0.7. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#soft_limit ManagedDatabaseOpensearch#soft_limit}
        '''
        value = ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterNode(
            soft_limit=soft_limit
        )

        return typing.cast(None, jsii.invoke(self, "putNodeAttribute", [value]))

    @jsii.member(jsii_name="putShard")
    def put_shard(self, *, min_limit: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param min_limit: Shard min limit. Specify the minimum assigned quota for a new shard in any role (coordinator, primary, or replica). Shard indexing backpressure increases or decreases this allocated quota based on the inflow of traffic for the shard. Default is 0.001. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#min_limit ManagedDatabaseOpensearch#min_limit}
        '''
        value = ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterShard(
            min_limit=min_limit
        )

        return typing.cast(None, jsii.invoke(self, "putShard", [value]))

    @jsii.member(jsii_name="resetNodeAttribute")
    def reset_node_attribute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodeAttribute", []))

    @jsii.member(jsii_name="resetShard")
    def reset_shard(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShard", []))

    @builtins.property
    @jsii.member(jsii_name="nodeAttribute")
    def node_attribute(
        self,
    ) -> ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterNodeOutputReference:
        return typing.cast(ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterNodeOutputReference, jsii.get(self, "nodeAttribute"))

    @builtins.property
    @jsii.member(jsii_name="shard")
    def shard(
        self,
    ) -> "ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterShardOutputReference":
        return typing.cast("ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterShardOutputReference", jsii.get(self, "shard"))

    @builtins.property
    @jsii.member(jsii_name="nodeAttributeInput")
    def node_attribute_input(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterNode]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterNode], jsii.get(self, "nodeAttributeInput"))

    @builtins.property
    @jsii.member(jsii_name="shardInput")
    def shard_input(
        self,
    ) -> typing.Optional["ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterShard"]:
        return typing.cast(typing.Optional["ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterShard"], jsii.get(self, "shardInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameter]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameter], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameter],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1d29b5fe513f2e85cf52aefefd94d542a7745f1f9634dda5e4b1be2eb5be6fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterShard",
    jsii_struct_bases=[],
    name_mapping={"min_limit": "minLimit"},
)
class ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterShard:
    def __init__(self, *, min_limit: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param min_limit: Shard min limit. Specify the minimum assigned quota for a new shard in any role (coordinator, primary, or replica). Shard indexing backpressure increases or decreases this allocated quota based on the inflow of traffic for the shard. Default is 0.001. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#min_limit ManagedDatabaseOpensearch#min_limit}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61809a554eeb88b3f45b401f1246c1075998ae05ab7a23a06d1335c6882a0f6a)
            check_type(argname="argument min_limit", value=min_limit, expected_type=type_hints["min_limit"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if min_limit is not None:
            self._values["min_limit"] = min_limit

    @builtins.property
    def min_limit(self) -> typing.Optional[jsii.Number]:
        '''Shard min limit.

        Specify the minimum assigned quota for a new shard in any role (coordinator, primary, or replica).
        Shard indexing backpressure increases or decreases this allocated quota based on the inflow of traffic for the shard.
        Default is 0.001.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_opensearch#min_limit ManagedDatabaseOpensearch#min_limit}
        '''
        result = self._values.get("min_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterShard(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterShardOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseOpensearch.ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterShardOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__07e6ae39477c9d0947cf6293f38cd0b584ee798fa7082d008b4cabe59aae88bd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMinLimit")
    def reset_min_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinLimit", []))

    @builtins.property
    @jsii.member(jsii_name="minLimitInput")
    def min_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="minLimit")
    def min_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minLimit"))

    @min_limit.setter
    def min_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6601512049cc59a57e3848cbb2316944a99c57b5eae8fa4a63e3f045a1d504c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minLimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterShard]:
        return typing.cast(typing.Optional[ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterShard], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterShard],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9030c498df8b6dfb71c3a7129b3d4b73327e5c02bcb26b75b2616ed4b5587884)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ManagedDatabaseOpensearch",
    "ManagedDatabaseOpensearchComponents",
    "ManagedDatabaseOpensearchComponentsList",
    "ManagedDatabaseOpensearchComponentsOutputReference",
    "ManagedDatabaseOpensearchConfig",
    "ManagedDatabaseOpensearchNetwork",
    "ManagedDatabaseOpensearchNetworkList",
    "ManagedDatabaseOpensearchNetworkOutputReference",
    "ManagedDatabaseOpensearchNodeStates",
    "ManagedDatabaseOpensearchNodeStatesList",
    "ManagedDatabaseOpensearchNodeStatesOutputReference",
    "ManagedDatabaseOpensearchProperties",
    "ManagedDatabaseOpensearchPropertiesAuthFailureListeners",
    "ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting",
    "ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimitingOutputReference",
    "ManagedDatabaseOpensearchPropertiesAuthFailureListenersOutputReference",
    "ManagedDatabaseOpensearchPropertiesClusterRemoteStore",
    "ManagedDatabaseOpensearchPropertiesClusterRemoteStoreOutputReference",
    "ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlog",
    "ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlogOutputReference",
    "ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlogThreshold",
    "ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlogThresholdOutputReference",
    "ManagedDatabaseOpensearchPropertiesDiskWatermarks",
    "ManagedDatabaseOpensearchPropertiesDiskWatermarksOutputReference",
    "ManagedDatabaseOpensearchPropertiesIndexRollup",
    "ManagedDatabaseOpensearchPropertiesIndexRollupOutputReference",
    "ManagedDatabaseOpensearchPropertiesIndexTemplate",
    "ManagedDatabaseOpensearchPropertiesIndexTemplateOutputReference",
    "ManagedDatabaseOpensearchPropertiesOpenid",
    "ManagedDatabaseOpensearchPropertiesOpenidOutputReference",
    "ManagedDatabaseOpensearchPropertiesOpensearchDashboards",
    "ManagedDatabaseOpensearchPropertiesOpensearchDashboardsOutputReference",
    "ManagedDatabaseOpensearchPropertiesOutputReference",
    "ManagedDatabaseOpensearchPropertiesRemoteStore",
    "ManagedDatabaseOpensearchPropertiesRemoteStoreOutputReference",
    "ManagedDatabaseOpensearchPropertiesSaml",
    "ManagedDatabaseOpensearchPropertiesSamlOutputReference",
    "ManagedDatabaseOpensearchPropertiesSearchBackpressure",
    "ManagedDatabaseOpensearchPropertiesSearchBackpressureNodeDuress",
    "ManagedDatabaseOpensearchPropertiesSearchBackpressureNodeDuressOutputReference",
    "ManagedDatabaseOpensearchPropertiesSearchBackpressureOutputReference",
    "ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchShardTask",
    "ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchShardTaskOutputReference",
    "ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchTask",
    "ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchTaskOutputReference",
    "ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueries",
    "ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesCpu",
    "ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesCpuOutputReference",
    "ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesLatency",
    "ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesLatencyOutputReference",
    "ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesMemory",
    "ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesMemoryOutputReference",
    "ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesOutputReference",
    "ManagedDatabaseOpensearchPropertiesSegrep",
    "ManagedDatabaseOpensearchPropertiesSegrepOutputReference",
    "ManagedDatabaseOpensearchPropertiesShardIndexingPressure",
    "ManagedDatabaseOpensearchPropertiesShardIndexingPressureOperatingFactor",
    "ManagedDatabaseOpensearchPropertiesShardIndexingPressureOperatingFactorOutputReference",
    "ManagedDatabaseOpensearchPropertiesShardIndexingPressureOutputReference",
    "ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameter",
    "ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterNode",
    "ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterNodeOutputReference",
    "ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterOutputReference",
    "ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterShard",
    "ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterShardOutputReference",
]

publication.publish()

def _typecheckingstub__64a04d8da6e4f1b319a40ace3990acecec34666de7dc4b9125beebfecfa929af(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    plan: builtins.str,
    title: builtins.str,
    zone: builtins.str,
    access_control: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    extended_access_control: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    maintenance_window_dow: typing.Optional[builtins.str] = None,
    maintenance_window_time: typing.Optional[builtins.str] = None,
    network: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedDatabaseOpensearchNetwork, typing.Dict[builtins.str, typing.Any]]]]] = None,
    powered: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    properties: typing.Optional[typing.Union[ManagedDatabaseOpensearchProperties, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__99473b30cd8c5d5bf751dc40a87eb264e6f724273e36350fb7751af5f0292918(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__827b59afce111c617fb7e5a741d9b2a3004395e4c68a14fedcd8c61308c66442(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedDatabaseOpensearchNetwork, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc380db9b723b44538f0654f873b7e6938e7f77a5500c11f59172853bb812451(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a861bcb5d8f073071a3fc6c246b46bb262c59eb6ed230613542b683d9ed7c266(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03c43ec7ae33e6b60985ef2de80521f4f4ad3629a44711cd102de73bdede18b7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab7b7c324ffaf25c97aa2385c0cd8bc6a0d40f0cd84fade78ab276bb76bd2286(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__778bfd3bad1122cec5c9a8b1233c9c30f21e60cdc07d7a6dcd73160f3e8f3e9c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__530a55728ead99da54d717ec010026a48f653d62a58301fef9f9b7df2338770b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__483f921db7c5dfd553cc7ae4edbed08bbf6e087ac61e5e73e3d36d5d28906fd7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aaae0df4ce6f9b86602301afc165377558c6979c9d648f5b3b8a28f1427c34e3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45778f8cc87e5d7b6f2d7c690dc5f0615c03f6d3acfd1258fa752f26e3f8740b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80445b2497f5053a7db532b13cb213b977109e6177a17548b462ef2c9231be75(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__579f921500d29592dd476a83479c64100aa52fd4cc27afa5eae53e2740c76556(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71dbfb4b6bef08098f6a9392298bab540d9d5a48287b7ff1514dbdef9db71b1c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05e0104604c6d119c33be2ffc1295050857aba0fbf9013e5d6022408797e700e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3df9409d3f44676e26c2ca792935f6fef5261571686ce099b21079ee9cbf626c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1797fa76f17542a4461981c77c1febde7b7dc7ffbd53ddc05cf07be29a5ae4c8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c439c2c67d2cf65e96be6f9aae6aed6b527fa71224a5e82d9bfb478b705b43d(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90f578c3b7e470de9a79795d445280c0213bf84b88b837792ae7c769b5a24be2(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a85bd4824a9de6b259bc7ccba33f22669db6f14724268fea2997edfec3db5c36(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3927b44417f2561e30157a8e7bbae613a717e7583e7952dae4442c4727ed67b2(
    value: typing.Optional[ManagedDatabaseOpensearchComponents],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5005f5a996eb4e5ca1f0d2c27e74393a05028526f22e88c6ac2dc4e0b094b28(
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
    access_control: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    extended_access_control: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    maintenance_window_dow: typing.Optional[builtins.str] = None,
    maintenance_window_time: typing.Optional[builtins.str] = None,
    network: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedDatabaseOpensearchNetwork, typing.Dict[builtins.str, typing.Any]]]]] = None,
    powered: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    properties: typing.Optional[typing.Union[ManagedDatabaseOpensearchProperties, typing.Dict[builtins.str, typing.Any]]] = None,
    termination_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fca8408590124dd06a9281b50a661dcbdbb53334fd0cbfb3b4fed6c54dc2fd83(
    *,
    family: builtins.str,
    name: builtins.str,
    type: builtins.str,
    uuid: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e329b18badd7d49b48b57bfe67898d0a24d2355460b3e92344a172ad07ecd4f0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32720d726b88051a33b0a45fd56ea4118a2f932301f8c2b2a1d84423707660d7(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48f41e22d45dd70224aad1ec2381618b7683e3b9cbc00c500cdc37da46e33fbf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__517c0a72cf55cce1ae9b6342f33106b189fcd6dc12b3fb06aece1db1c9deae0b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2429cd8dff761f1e319900b52e924676682282f94ad7505ba9fe22ee0013cf20(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7988b51be371d4764a089b96fd2c9e8d7deb564eb6a899f5837744f8aa64b302(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedDatabaseOpensearchNetwork]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14f5527b348fe4ce85b3f81d752ce7962795f510497f946d3c9fa3d824f60542(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__caf0f3fab78ca354752f87686c4ceb87c0908570faaf71c9732bf3b9af492e9f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f552807981014b5ed36ce91c9049ddd1640edc60f00b525be36ade219e1114fc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38e73f2b43516cb1cd2e49b889369e26357e42dba138c5c96b56d7155745209e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ae4a80d42aa53b63a4e5515fe09be52313dfd3d7869eb5dfcb8797bdfedaa35(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e17b8944baa901c2ed823dd7faa74dbd4e7cdddd833b000fe7f421fb4ee6b6a9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedDatabaseOpensearchNetwork]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6dabf973c57f1eeb683ec41bdb082376b0d3560469ba973ef9241b6d0f7caa7f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b36091a7798a7e3cf1e20b74cd929271ac53667c3eb0dffd8c1e02230d698148(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d821842074c66d72233fdba46b159048348bfd6348d4a84352047819b9397ed0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__721b09f1dbc677bfbbdf1acb348a60d81f02d69bddbfc5ea3dc0507161c8745e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__732002e48eb319c6455b5f536a3f908279777ddbb6aca495c13f3c337f205389(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__230770a22010afacb40ca84242cbcaf8dc73a365b4513ab7b9b99d283bd1184c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0f38cb62584f08fe2a0d73b2d546e0165c39f2136e81c6846a602f1affb622c(
    value: typing.Optional[ManagedDatabaseOpensearchNodeStates],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de14c8022684ac9416f06b1fd8069683ff6f1b4d90f2879d52bb0843d4b3353d(
    *,
    action_auto_create_index_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    action_destructive_requires_name: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    auth_failure_listeners: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesAuthFailureListeners, typing.Dict[builtins.str, typing.Any]]] = None,
    automatic_utility_network_ip_filter: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cluster_filecache_remote_data_ratio: typing.Optional[jsii.Number] = None,
    cluster_max_shards_per_node: typing.Optional[jsii.Number] = None,
    cluster_remote_store: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesClusterRemoteStore, typing.Dict[builtins.str, typing.Any]]] = None,
    cluster_routing_allocation_balance_prefer_primary: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cluster_routing_allocation_node_concurrent_recoveries: typing.Optional[jsii.Number] = None,
    cluster_search_request_slowlog: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlog, typing.Dict[builtins.str, typing.Any]]] = None,
    custom_domain: typing.Optional[builtins.str] = None,
    disk_watermarks: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesDiskWatermarks, typing.Dict[builtins.str, typing.Any]]] = None,
    elasticsearch_version: typing.Optional[builtins.str] = None,
    email_sender_name: typing.Optional[builtins.str] = None,
    email_sender_password: typing.Optional[builtins.str] = None,
    email_sender_username: typing.Optional[builtins.str] = None,
    enable_remote_backed_storage: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_searchable_snapshots: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_security_audit: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_snapshot_api: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    http_max_content_length: typing.Optional[jsii.Number] = None,
    http_max_header_size: typing.Optional[jsii.Number] = None,
    http_max_initial_line_length: typing.Optional[jsii.Number] = None,
    index_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
    index_rollup: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesIndexRollup, typing.Dict[builtins.str, typing.Any]]] = None,
    index_template: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesIndexTemplate, typing.Dict[builtins.str, typing.Any]]] = None,
    indices_fielddata_cache_size: typing.Optional[jsii.Number] = None,
    indices_memory_index_buffer_size: typing.Optional[jsii.Number] = None,
    indices_memory_max_index_buffer_size: typing.Optional[jsii.Number] = None,
    indices_memory_min_index_buffer_size: typing.Optional[jsii.Number] = None,
    indices_queries_cache_size: typing.Optional[jsii.Number] = None,
    indices_query_bool_max_clause_count: typing.Optional[jsii.Number] = None,
    indices_recovery_max_bytes_per_sec: typing.Optional[jsii.Number] = None,
    indices_recovery_max_concurrent_file_chunks: typing.Optional[jsii.Number] = None,
    ip_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
    ism_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ism_history_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ism_history_max_age: typing.Optional[jsii.Number] = None,
    ism_history_max_docs: typing.Optional[jsii.Number] = None,
    ism_history_rollover_check_period: typing.Optional[jsii.Number] = None,
    ism_history_rollover_retention_period: typing.Optional[jsii.Number] = None,
    keep_index_refresh_interval: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    knn_memory_circuit_breaker_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    knn_memory_circuit_breaker_limit: typing.Optional[jsii.Number] = None,
    node_search_cache_size: typing.Optional[builtins.str] = None,
    openid: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesOpenid, typing.Dict[builtins.str, typing.Any]]] = None,
    opensearch_dashboards: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesOpensearchDashboards, typing.Dict[builtins.str, typing.Any]]] = None,
    override_main_response_version: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    plugins_alerting_filter_by_backend_roles: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    public_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    reindex_remote_whitelist: typing.Optional[typing.Sequence[builtins.str]] = None,
    remote_store: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesRemoteStore, typing.Dict[builtins.str, typing.Any]]] = None,
    saml: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesSaml, typing.Dict[builtins.str, typing.Any]]] = None,
    script_max_compilations_rate: typing.Optional[builtins.str] = None,
    search_backpressure: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesSearchBackpressure, typing.Dict[builtins.str, typing.Any]]] = None,
    search_insights_top_queries: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueries, typing.Dict[builtins.str, typing.Any]]] = None,
    search_max_buckets: typing.Optional[jsii.Number] = None,
    segrep: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesSegrep, typing.Dict[builtins.str, typing.Any]]] = None,
    service_log: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    shard_indexing_pressure: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesShardIndexingPressure, typing.Dict[builtins.str, typing.Any]]] = None,
    thread_pool_analyze_queue_size: typing.Optional[jsii.Number] = None,
    thread_pool_analyze_size: typing.Optional[jsii.Number] = None,
    thread_pool_force_merge_size: typing.Optional[jsii.Number] = None,
    thread_pool_get_queue_size: typing.Optional[jsii.Number] = None,
    thread_pool_get_size: typing.Optional[jsii.Number] = None,
    thread_pool_search_queue_size: typing.Optional[jsii.Number] = None,
    thread_pool_search_size: typing.Optional[jsii.Number] = None,
    thread_pool_search_throttled_queue_size: typing.Optional[jsii.Number] = None,
    thread_pool_search_throttled_size: typing.Optional[jsii.Number] = None,
    thread_pool_write_queue_size: typing.Optional[jsii.Number] = None,
    thread_pool_write_size: typing.Optional[jsii.Number] = None,
    version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da6df7d26b0238df040ca0d1aeaa659a956825f3139e84791c48d896c03493a3(
    *,
    internal_authentication_backend_limiting: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9435799fa69802c70cf9a1ec8b896a69d09f232c4c49f47ff2d40e3e18c2343b(
    *,
    allowed_tries: typing.Optional[jsii.Number] = None,
    authentication_backend: typing.Optional[builtins.str] = None,
    block_expiry_seconds: typing.Optional[jsii.Number] = None,
    max_blocked_clients: typing.Optional[jsii.Number] = None,
    max_tracked_clients: typing.Optional[jsii.Number] = None,
    time_window_seconds: typing.Optional[jsii.Number] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99749960614da71029c64a8b792ced764cdf27a0962414854d04210bb1ae2acd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cd07b462b44760122178a37243eab5bce0c8902d031193949d1c2e9b173cef8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c97e2414097315d7ba383e33a5dc0b3357f770c50a34a76b2c31435635e7ede3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8966671b06b0cb755048c486e085213fe8c8f8eb3434ef864493050eac73e366(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0448c88bdb2b3db18c1c620763fad421cf34b0e345fd1cfeb0590539f6fbf08(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0911499e4bd4d24c4fe2f3f9f3cd2c527bcfc391686536082567743a93ddb080(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe8bc44df1f627c05d7f87446be558febc5900c4b151855121869224bf95cf0a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__524634a3518077cc05d7163bab39b1e5c92bf78a97db61a74f322b581322cf1b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__827575e00c1eaecf35d33d817e94688109afe1fa2f142d1614bdc103f0e670cf(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListenersInternalAuthenticationBackendLimiting],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bb457d048cf3243bf7b1785b9d3430cd66839097d28517e5978e7c0ff727704(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9841d9da7d378cfedc4cae10fb3cd1f05a03ee8993362ac50891755214ff708(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesAuthFailureListeners],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8bf09b01c282df36e41b853e405726d98c811dab3e94915dc82e4bce9ce583ce(
    *,
    state_global_metadata_upload_timeout: typing.Optional[builtins.str] = None,
    state_metadata_manifest_upload_timeout: typing.Optional[builtins.str] = None,
    translog_buffer_interval: typing.Optional[builtins.str] = None,
    translog_max_readers: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a2ce59de3d35325edbf31f06bd6314fd8a1f6f2b0cbf0cc4c852657ac53b74f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__262389b84e11bdd882c1d940b5bbde682b70a413568e5d144d27966190c7ae18(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9de1fc53a6ea5f030acd5311533fa5594e2e560df3ba985952c9d7b266004c51(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18485bd7370577759f74717505aa14e2600467bbcf2e3ee12cf56de0c96f0030(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d288fe3c75526f1f2dc35253affa3e160d3e45a773c50dc363eaeb2f542fe229(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b9e5024bfb1eae2b8040b8cf5457ca2dd70962144d91f9aa51c22d2ef702b27(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesClusterRemoteStore],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1eadea9efdeac59a42a8f43fdb4be6968800ad553251e2efe3e8597efb2c7fb(
    *,
    level: typing.Optional[builtins.str] = None,
    threshold: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlogThreshold, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a2e383dfbb2de0011633030253319bf1abf3c6c5c6831459f3b97e703ca19ba(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b14d13f5622ae593489f694e875d89afd8bcfedc7dc9ef82306ea211d1a05da(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43bd50dc17e271b755c3fca4452f83c3e2e79379fd91a6d11d12dfa6eb1bdb63(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlog],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7693880d283c41692690ec00b0f211583f9092af9a4f9be8cc2503b2af685fc(
    *,
    debug: typing.Optional[builtins.str] = None,
    info: typing.Optional[builtins.str] = None,
    trace: typing.Optional[builtins.str] = None,
    warn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__746e796ffd67ae3881ed3680bae51d65b7298cd5e3841cebd66ee49f5e60ee64(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1edac68c2f51e1d8421f2df83f6d764637d8e5d50db4d416276e81b7dc64a10(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9acd66c824a35920ef5f66e89cc105ab20a49ab57b57a82783cdbd9aa1c4615b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53cfc2baf6e36ac98957aef65f5ebbfe6e59103dd0926217a9ea40b32e62e6c1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0345010facfd876213e3ee645c559fc9fdfc44774d7b355274e07db2d57555dd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed00f49e466ba4afcc8014fb654ab34c631b78a933333f34cf113da3bc94d13d(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesClusterSearchRequestSlowlogThreshold],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9a670c205c08f4ac01cd4501f4103c0e0bc30f14aa62b77bfae1c27c816ef3d(
    *,
    flood_stage: typing.Optional[jsii.Number] = None,
    high: typing.Optional[jsii.Number] = None,
    low: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf1c6f6948b6ebbff397a49dbd1226357f6783b4078a6ce19039517b616fa315(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cf4f285faa268c65a163130a1737433054040990833b9b664b94080736f2c27(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__093f7f3025441dad65428b9930e853d6ce7a37fd588398fdf2544d4aebf31edf(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9bb2cbe5f289bc789e377337f83f4aa1924821be012296e0578b1d55ed2c495(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a603893dd48ece901e23fab7bee75233f5a3a69ca14256f14b8be2885cdd82b(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesDiskWatermarks],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73e080e9f13ad7c30ec45334431a3eaa752568545186fa7cf689bd26e836d2d3(
    *,
    rollup_dashboards_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    rollup_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    rollup_search_backoff_count: typing.Optional[jsii.Number] = None,
    rollup_search_backoff_millis: typing.Optional[jsii.Number] = None,
    rollup_search_search_all_jobs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e365e9aac6cc1a319fc9231d277e888c9d08fb84bc33dfd4676e14ac5a3e2792(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdddffb92f343672b638d95d72399987b6afbcb570d66841e49c76e5dbbd9ad9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22ca82987ac8fb9e6089aae6b6e1e31399abcae717d6de93a8018d2f63a9e025(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccb0eadf36f64f36891241b43dce8e4139bc5c1d4c265dac2f7b2066c3f264da(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__589fe605a3a57f384029ffd93b26dc6dc0fb7f39c30e6e374de2e8c29a524bff(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5e692cd596ade320b01ba6435902b99a0f95fd1902b94cdfed205b2d9945fcf(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3de6c360d6b8c8fdc0066e73b3c6b34d637866ecd30541d52ec07debcd855387(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesIndexRollup],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__091ebe000c02a1dbf5147d4d6e2e100eaaea7c918311494e9ada1f78674a89e3(
    *,
    mapping_nested_objects_limit: typing.Optional[jsii.Number] = None,
    number_of_replicas: typing.Optional[jsii.Number] = None,
    number_of_shards: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80db9e8d6bfffacb73cb1f100468062628a53d92d9dbb8e053b4f82011e7088d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9714605aa57197fc59ce6c9f2e363fa7bb5622ebb54ee19ef15e7857c251df97(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99332dc6f1965838c8118775aebd1f65b3d65be63b32bd7b866815bfbe8a3d51(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c96ce7acc291c5aaec545dcee6fda8acc85e631432e5aa54434163de41edffe(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b16dccbd691a6d637fb1fe54be64ca4acfec30c4e49cc9add81d99b41d2f5ea2(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesIndexTemplate],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73c0a3837cca5d07ee0176744b302d89e862a8b39ec6f0e2781b94b27f82af92(
    *,
    client_id: typing.Optional[builtins.str] = None,
    client_secret: typing.Optional[builtins.str] = None,
    connect_url: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    header: typing.Optional[builtins.str] = None,
    jwt_header: typing.Optional[builtins.str] = None,
    jwt_url_parameter: typing.Optional[builtins.str] = None,
    refresh_rate_limit_count: typing.Optional[jsii.Number] = None,
    refresh_rate_limit_time_window_ms: typing.Optional[jsii.Number] = None,
    roles_key: typing.Optional[builtins.str] = None,
    scope: typing.Optional[builtins.str] = None,
    subject_key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2d1f05510b29d1e71f1ca51d5c296f3e66e489b68f141c0cb11fdf1089181a8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa7261a89918dbfb9f50fa9dfae42227fb7412ceab80b7a8b982e2db47c07f02(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__699da58a3d40107a39d2119729ecbb14aaeff7207705a003c1357d842dc1ea48(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e90a34de40e81274f86eb828ee2b88ed8bbf5ef9e0814fc5f8f5486266be9f71(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00987cb520a1f1a0ea820dcfda52b67895e8d1b1f813300c1440cda0e27f1139(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f9bf04854b7ff6094b1426fa9ec13b04739a31f9863bbbcb53eec2116cdbafc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3decaf18072bd601d7198339380575ee2070f319206ca5742d1ca686393ca774(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a9e04be6387363a6fb27928afe6e422ba0787832599b73c3798bded4bbbeaa7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f125200f527ffbb5e3cbc957fcf1254d0f49b7bc28cc54daf6b9114de79a999e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58b2b1fdb72bb20c47f3f3da6e88eb14a71ad8399fe12a1f255177f46d28dfec(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e308c3ca6ee25c5414c9c3b5b5add06951a6a78c7783c033bd7d39f387c28a89(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5cedd7c2ad307531bb92f92c1dc2b02714e9a953ac794098ab5e972da769fb7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2e8077939eb6e386d424c3909093dc0fd2f5595c3f150af06f218539a68a082(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a06c0f82afb429010a7bf11d739c6e615490b1602601145c983041209f49f06(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesOpenid],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c02ebecf926c4894c4481fd34c44a4f69278e1e4c9c78e3ec30f9d08a36971c3(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    max_old_space_size: typing.Optional[jsii.Number] = None,
    multiple_data_source_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    opensearch_request_timeout: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46269da753bb4825eb2d2eb52d1679232eb04b442c74f7cafddf4cf14945aec0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1019ad4a6f0e57b8f798e7a399405937723d4cbd1b0109900787a017b35b7f7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15484f5f1d02602bd803336a02543fef580fed4327eeca3c32e0e19880cb41a0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d40ab4d7811997e535f4f7ddf3e45b333ebefa915dcae062cef05fc5d07b8711(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39f2bb44168338b5f62f27d6c68aa85795f001b64ec8ee27ccfd05945977e24a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__642b1eeba71d0c8859ae09897efcd46c46a7f3266c413676870e000d26269bab(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesOpensearchDashboards],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__751155185e1458cf144b0b3f995bffe965d316250c0fff7682404038d0582237(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f95b49868c2e1ec7544168878febf8b6696a57483b6f51fa99aa0925cb16697(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e457da88de09c5532affd0a501416c99106d06518e52d2a5677fde17f0757fd7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be63faa87856b340f7df4fdaa463d51315ab3cec9d31b97f5c4d5f518b414508(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56ad8b6cd68415d53aed2467ec71f02ea55b6b3fbe4d64b15a5285311a1dc3b9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3368d21a864593369d41fa3b6553ceda22676badcd2892eab312b0d160b62f1a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4acaa825e4505022989c6428a6d611632f85344bcb6863b74490ff70481c3df(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0448eb5420a97c55d350dfab1c0a0d3e8726d744e441f4fde0d412dd04f31497(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07a65588eb7a4625bdb8375e03839f7d7ccf09b91bb824e3b31afc1c39388598(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__def39ace52f9f4b94afbcd8016abe63135f081d70125685ec54dd3ef178d1de3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d549945259dc5d5d9b2134e2a3264e213b749e4f33396341c391bf22353af47(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b181764d7b414fdac2022d32d63421fe71b45025faa283d816517a60e472c6c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__342025668ce074acad3db548bb92de3b1aaf5e8a569bcdf9f928e24b1dce9c38(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6bca62f115362f57dd2893e4d92a97631fc0dae4d4b38a8347471bd6a8c2259(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3477e1ea1b7e2193121b11b3416a7dbff4f64a222dc6cc3963488697ec8352d6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff78f5e79729d11ea6229a93440341c6dfb144628a5a51a9a4f0c10d9983ef87(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e45ead370d8febc26e146a75b660cd2627775fd50527d1c042f0d05328e66c1e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09252df690d98b7364842578b7664698629fd55a3c709cedfc832883b986e93c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f23654b3c993300d915c75caa2b551bed505e332e601ae1d318b6f7c22eec1d4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71c76b5482471bb5f448beac6f8f0c45b923c1fc3debd34a481229204fb99ca1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58c6add2afd8176cf65752af011b26017ea4026647b88807e7848153aa808c88(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa13f532a0cc1807de56948d104831eea41a922b8cccfa4dbededb8056bc2101(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a8c26865a2a9328ae331cb883300375516826479d56c03bbe3b173701034e54(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__066a7c0b66ed33e66af285d45119ca128f33fc0bcbfe01b3a35bcf4a21b2f488(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a2af7f1a139f5456a3f2eeca4e3867ef26c85c7ba01267c4acf3fcbe89eb9ea(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db0348b951ec966edf534f9e879d0bee16e2d53cf2ff85b213c5dc31755a5aa4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__363b9a51b2ae015e89e6f9beea8cd6589eb3254d3e9a8ed918d7f8a059b00488(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d857a7fba85a3ccba0ca1972bd70c474b4d2fea3a6f3b935d6bf1920e087333b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__511b44be808d39b3f5d61cf6c8b691b91fc91afda941c083d2ba0fee3107aece(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5817885ce9a4dfdaf892000c0e8757e89b0d1233e8785edbee32917946b1f379(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dde81e5014559bf79849f8363ddaef4d0fe9186cec22e692bf4b937ed30bf89(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d409d4c93acb6dbddf3ea05ef640c8c083700c01312ae34de3c952a00933254(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd4ad47529fc509173d3341762a0c1b8ce4e8d381578c9db0e9588fb5bd11e69(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7988c725f00df71948d13e3c7a67c37939bfbdf59be068727cb0f1b6fe5c0b49(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6579b40abc92fc56536665342c25021b16220f2bd87f5e74283f08704cfe6abb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb9144f9ff10e0665d17f1dab9d796961a1f30385738d5fac5012ac1e12d73c4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__475c7d9ea1f132358fd8876b5bce857503b42c419cf0edd268668a9396576272(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79543fe9d0bb8f49f03afaba4905ee1fc1c6bb8081b72a0ce935e05db800d019(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d77bb2fd42dcdec4347d48a5fd38597e5fd7a8bd356c3b4be6c11e5d48f49eca(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e9d2f14dde38e4490263e09c4c724a7695c50bcf345ee919284647e4ec77730(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec6c829c8246593bfea087d544de86602dcf1c3f827bb531e45fb456fd06b41a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc45a3b1177a7e18688e7dbcc3ca2d16552505944545509d4b5a66e029a2afd3(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1877b1cae754d3c61d03eab40de84ea8994bc6a8f432702bdad2e544cca0bb93(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00d138e917ad74a2a8c043cd17d158357905bed6e23949c38b382514204bd13f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de1660d38a30c3e2336ab4a8e93e4240c706d088fe2d0a466fcf8ddb12386f10(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a031050a9e6f8a40b6fff2021afeb15b5ad471d2a0772dbf01945324746e1c4e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8c3fe099944b1f56a32bc799baf5e867e2cdf4f7b392cab873ea63870b05066(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33a0fbdcfa0733a258cb09a7fec41cb87f369bb39dbe3d656186fee89fbfc0bf(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__284920e01c9389024b53f7d33cd743be906b889c598a63b378523ba83bee9165(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c49306bfe5e374f98a93dbde13277a081ed1c78280db967a45ae6d9aa463d68(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dda12e0a9350f10cc58dfb4503e36cef9ef54b196da052bb6919eefe1b4ddcd2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56ae2dc20f615630e63a616e89cc1fe881038dcec11ccd7feda4fbca3d504561(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2c716fb378769c59082cbd6ef2a98ab923895cd0d2907af1ddaa2e22ac6933d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2acbdf19ba9102e2e1937592da16eb85b1c62ad65e6149f8c3d0a3bace050cad(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf6c4b8bedfe2dab74ff62e0b49929a7e29387a92737dd6be0d7da5dc2e30672(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5be01f06da11cbc0ff664fcfcdfa1885cecb35a2be2f64f3db7a6c82afe350d6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__363d81378d4e1cd4dd5f6d81316deffe21c2b78c49e33a7350d70233def65523(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b53d519b13b838c462a6929cbcbecaa084a53ce80392b3cfe23e41033ed0af8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fdf3ac54e30cad1108c45853dba19226fdd8c66b79009b24e04a2bfd594cff5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8adbbea4f99ad4d0b9aca6ba9727235da1a05ed87b8c7206bf576514664c1eba(
    value: typing.Optional[ManagedDatabaseOpensearchProperties],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e1013d27f16812c588f69f95f6c4ed8a1edf66c5571a35c767b4a4ce0496a56(
    *,
    segment_pressure_bytes_lag_variance_factor: typing.Optional[jsii.Number] = None,
    segment_pressure_consecutive_failures_limit: typing.Optional[jsii.Number] = None,
    segment_pressure_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    segment_pressure_time_lag_variance_factor: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5e4c43397a7ba947a68ea82400d769dd2f03b78aa2f4aebcd0c9b0770ec936e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b1f15abf13cd92cd37d890df5391a8106a6e7ea2c3cd00aa1a800aa83904469(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66c5b2fb7de039d911e9c5c44abf4cd980eca04ea40aa66368af670c3b71e0b9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__976704fb886f0bbd658b1b4324e53cbd1e9210e4e5b9064276185b095cdba0ce(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__befba414fd08d46bbe36653b548f4b9000e538c2805b736018c35277bd013b7d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dff13f45f0788b5975d5ad4140cec670a70fef0e37928cbfdeaacd1d7d25c75e(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesRemoteStore],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b14f1e134e8d0c84c0341fd18666aca6f997046615ab52f5363393b4ab7937e(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    idp_entity_id: typing.Optional[builtins.str] = None,
    idp_metadata_url: typing.Optional[builtins.str] = None,
    idp_pemtrustedcas_content: typing.Optional[builtins.str] = None,
    roles_key: typing.Optional[builtins.str] = None,
    sp_entity_id: typing.Optional[builtins.str] = None,
    subject_key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9006f804233866e0bcbcabfee80e240d58ca3aa0b270b35fca9e093fc1e32e9c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d469be80b1364917873721e8af88e7062483a039aaed7718db029f5ca170884(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__814ab6ecf48749b6d62f26b6567d61ef65ea0bfbbe19f1358d51810029ef998a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__608b37237be872718973058fb30455a02be360f5053c70e96510693c9b9244d8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1814aa90ebfc251af6c91642e42ce08a47300fa1a8e3cacf378c1886d789c06(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e94553764dddbdb00b434cdebba04db1366d57e07aaf8f5c89ff45bf9529acbc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecf9acff0d36a02176d62a477d13b9d21e0065d4067d1da39833b3dc9b1054ae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c2749a1852f09b8e903fc5f21f9fc37f4be29b4b73b365e767ca5ec1eed0097(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3eef83ead552c9f4ef0503c6cd5db370ccfefde7338e3dca2b88ba0fdcc15ed(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesSaml],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__805f97b9e5a6105534a09bda5ae4938f7f200c78f7107c05aa43e852e3889554(
    *,
    mode: typing.Optional[builtins.str] = None,
    node_duress: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesSearchBackpressureNodeDuress, typing.Dict[builtins.str, typing.Any]]] = None,
    search_shard_task: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchShardTask, typing.Dict[builtins.str, typing.Any]]] = None,
    search_task: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchTask, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d39b711eab4461a4c1b96d616ef21c90bba1b606f922482a8bfe12b3daa624f(
    *,
    cpu_threshold: typing.Optional[jsii.Number] = None,
    heap_threshold: typing.Optional[jsii.Number] = None,
    num_successive_breaches: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59378e31f4cd6201c364bda38b88b6f38570309207761b21d5081dcd0f615b45(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f2da3c5a443b5809eec45d188e064b67733e4bf33b42120835068a003d3d85d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6154536222d2a3ce408361d85a35cfef51b1b35a0846573a851b79b4f792c0e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c8c912fb67610b192ee3462abb62f58c7e902befe1f3bed88fe18276e982303(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f92228b2e318521cde3a3494dc8e2af648769323ff3412958f2d717ea853d01(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesSearchBackpressureNodeDuress],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ee58dca98bdd2a102e2b6572f78fe85eeaa363b2520afc85444288b079a3b7f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59438a0bf07b464ca34125d05eb0622f3179f66fd3e2abb87e7897f12bf80d24(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d199f7493f2c000b226300b70baaf081c1006c6f92609eded529318d5bb81856(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesSearchBackpressure],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b00773335f5cd697d7f58058999e1087b88965f82632c43cd0fda0432f5c39f(
    *,
    cancellation_burst: typing.Optional[jsii.Number] = None,
    cancellation_rate: typing.Optional[jsii.Number] = None,
    cancellation_ratio: typing.Optional[jsii.Number] = None,
    cpu_time_millis_threshold: typing.Optional[jsii.Number] = None,
    elapsed_time_millis_threshold: typing.Optional[jsii.Number] = None,
    heap_moving_average_window_size: typing.Optional[jsii.Number] = None,
    heap_percent_threshold: typing.Optional[jsii.Number] = None,
    heap_variance: typing.Optional[jsii.Number] = None,
    total_heap_percent_threshold: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f804c6e61b9f50dbdd61773a74c3e8afc03e032f98aee1aa97ebf6ffccfb7bc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f108b14c1e006b3bcc6d425fe8211a20712d24a3819dfe5282d7691a85aa33e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06b5a829eb31d417a55412068d78f6b0d8cc9ddec00eff4e7cd3977dd7cb220f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__958b2bb0a9c540cf94b080ec29e1e5fbd9c1eccc6b0f76721eb7556ebd5f304a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__418e25f5c93bcdcdad5dfb9588fa1ef68f91e1805449a4ebe0863cd9e236dd10(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc232fd43df166748d3e1067024548b6294d59ffb154cd820ea942add2307684(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__148f2fa12f2ab2b039fefea9a071860481923f97e2ecdd3e6d6c963f30aa2e1b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6609ecf296fecc3af6bda9c2302dcc426b51abaa327fc9faa6812b9a075d3e9b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__058ac4dba8c69f12eac4a1c56b99c448e10926597b85c9de8a85050346f284af(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9beee3db3d9a9a0e1f2a338f8d566dad145af24446f43479404ef603069ba180(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0580e72b91eb41bcd047005aceb043de5835de8fa3c97079618b8126f372372(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchShardTask],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c70c1faa9e9872e82b30ac5de548218cf7b3888e93ee8b9564bce272a55c420(
    *,
    cancellation_burst: typing.Optional[jsii.Number] = None,
    cancellation_rate: typing.Optional[jsii.Number] = None,
    cancellation_ratio: typing.Optional[jsii.Number] = None,
    cpu_time_millis_threshold: typing.Optional[jsii.Number] = None,
    elapsed_time_millis_threshold: typing.Optional[jsii.Number] = None,
    heap_moving_average_window_size: typing.Optional[jsii.Number] = None,
    heap_percent_threshold: typing.Optional[jsii.Number] = None,
    heap_variance: typing.Optional[jsii.Number] = None,
    total_heap_percent_threshold: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb68300a3716965aa0739e17464200040f8410e9f8cbfb0de5bd51b840f7841a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f011251c4054e5a2f9f0d8ca1da2019dc1c416fa17bfbf254af7cc16f8650327(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9d9b604e956a1438c3dcbdb13a64b082101ec26baab2814dbd6485ee27dc328(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__731378f09e674acfd4cb1106c09d76c14e022ecba7d606d41302ee614bc09bae(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__548de9238ad329c51e89e200692774c420ff4f058fbd2be43eb3b92e19d8e3f6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0c404670c846add12b8db9028df0dd2c1c4ced077ca983140b69dc55f6a3c6e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b01af9bbe1d7c211255b8dc962c9aa13e183cd9ac3ebb05f9be2017ccc2f030(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e31b26ab229e38083cbd838766c8927e810d896ca91a578fd20be7064d4ea0b6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ce6dec80d334a78f1ea07ca3dec7cc150ff1506b65ac8c3e4362e84d12fd7f4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b772c62b59d8d9b7c922635138cfdb94021055caa57f4c06a201173b2a90f72(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eed630a0a87e30594d254415564dc323657cbe20478aa9957e0510fb9688286d(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesSearchBackpressureSearchTask],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d48540eb48253b4690ae28a201bd0c2656eeb882644f670058d040de533de63(
    *,
    cpu: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesCpu, typing.Dict[builtins.str, typing.Any]]] = None,
    latency: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesLatency, typing.Dict[builtins.str, typing.Any]]] = None,
    memory: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesMemory, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d766d1d3c272cdb4b9cf1f83e27dff76cdbba937c7c5a6167ca8bf17039385f(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    top_n_size: typing.Optional[jsii.Number] = None,
    window_size: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d5962e931b874e9f7ab5e5f7438de4de506b33512e4bf1db8ed3f578a4397b4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c566b4e58830f7450ab54cdc5ad8b232fcdc22a85ded360eb32927e19391415b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9656f062bc576f9b07a0395445a8bd121599de63e79f3b1ea39a05fbfec94892(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78a35a1f301fcd9b30c7ae5fbd4bbc9ec8046797e0a9cf9713c7f8eb74d7ec5d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5196bba0013f06e7ffc62eae3cdf60b50a09516ef07225892521ad448f132e01(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesCpu],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af605383a3698bbbbd930e4ff42d3558bc2b49d2a45ef275ee19f303369ab414(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    top_n_size: typing.Optional[jsii.Number] = None,
    window_size: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1db8915b762bb83cee8f09c8c2587676181353e6416f6ce83a301cce5d37031c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4f31ccf61d6ad91d9d6537c8eb3050a37589c776869b257ca260fd425aaa6d3(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cc3a7e1ac13e5967087288faa477a91f073fde072c273be6e3bb9642b6510f7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__daf65203437b117b5aad96a21b85738efe93a3c6397a41005287daf2689c6f68(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfeebd32e0797c42f022cd01695f87fea69c78b53dd94074570331a5eed74645(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesLatency],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8f1e26fb94e46db6ae20ea187b2ad98f67fdc7bd6181ac39e4a17900b83dedd(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    top_n_size: typing.Optional[jsii.Number] = None,
    window_size: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c7996c4148c3487cd4a0b6c34800f557119ff6e610e44e5e52c5b4cccb5f11e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1dc368d8d4da1d3a1403f015eece87acc2dbb75f1b9043c989c57a4cf7f4cd20(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d59f46ab37e6e48e49ef775fafef4727d6a45005dba13d505e62c57a3be2af8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__555cfc577bffd5e159cabab8507aa4c904ac32d7e3475475e368117642de8709(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__851229a5e5379f4ff018059170242ff6ff7b18521656568fca27f0a09ebbf7ba(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueriesMemory],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a438c41538b402d8b9bb0e310691458cf458e06f1e054fbd7d66c6a6891f6345(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9317c4bd4bf51d262cb77b52440acd892fcfc9deb0b110bf7c69ce4a7caaa6ac(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesSearchInsightsTopQueries],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9a29cf3d5cc5ae1d0c9f47a3e6bd31c5ad02450141253c8c11375bd90c2137f(
    *,
    pressure_checkpoint_limit: typing.Optional[jsii.Number] = None,
    pressure_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    pressure_replica_stale_limit: typing.Optional[jsii.Number] = None,
    pressure_time_limit: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9da31e1fc75c1a98cd7eaba9e7de567232e771faa66cd7e2cd34338934c30f9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4723698c764c50efc62be0e8f65280c6509ef8ee02f4afb753ac826498205ab(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef3029aa6191c0ba9a6e087ee2f190ce88aa8d1b8cbe7d1c3c383c4bb181e1ba(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c298308bacd7294b38a8ac1012c412f9b25be54bb42e178bb20e8764121e10a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6528f27f2b94a77fccca0a03dc16a26dfbfae9bd5994e696cccb18723681a701(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__954d28124997316766dd128bf9febd598356be3ffb2b0b392d63f1b92ed12457(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesSegrep],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eea2862c5f0d31396bcb60288f73bd2a482b2c0d5fecb40f6e155d69cdb9084d(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enforced: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    operating_factor: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesShardIndexingPressureOperatingFactor, typing.Dict[builtins.str, typing.Any]]] = None,
    primary_parameter: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameter, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c2a585c78e0ebd7884489c51c18d79c728f4e6cf96723e8f1445b9a17a8bcb8(
    *,
    lower: typing.Optional[jsii.Number] = None,
    optimal: typing.Optional[jsii.Number] = None,
    upper: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e246cb950dc762e7a7e14c8d5ce7fe16db345693d083cf9d47fe835eaa32364b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20d701974306f722b43b37c7685ac55b61db2d530f42015c1aa2dd560f2d515c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4c6252daae2131b97906db1abcd58b4e77574142b36ad81d5d5647835fcb0a9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd5c63c967ebf10a5cf575aaba8815e67ce2878b8f6b192bfd644b5df1dbe454(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbe0ff08c3ff852e4ea101582100860b534c74a9f0f49ab9360c5323fbb9bf24(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesShardIndexingPressureOperatingFactor],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b33a13b7ed9dcb82bdedc7aa4c42760418159bb6c42b9a3c415a66737cd64f7c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f36cbe8ea87c863f8547b379d77f5d561bba6062d81d16d9eb55910568823c50(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08e82d879f8f210b3d91f31b0c17b5c27a58c2209ef2a4dc3d34fe2fc9b03742(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85cdbf1751ba4796b5cd0b9e8b24f0e9c7f3a8fed73f201b276457d8c8779016(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesShardIndexingPressure],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cbaac709f053962d06f3c94d810fad956ee10e361e216e769dfcca117244cdb(
    *,
    node_attribute: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterNode, typing.Dict[builtins.str, typing.Any]]] = None,
    shard: typing.Optional[typing.Union[ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterShard, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95918dc70f50ad9e3281b3f7d9734e2c0361a87e02f2466a872b57e27e96e88b(
    *,
    soft_limit: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69f5fbeaf1b377102840e627dfa704a1c44a8f231a489c99bf1d8837728fd750(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa3ef487ff0ab79d3448b30fd602224e5920930d3ece53c6ce1f3aebfdf21a15(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f25656eae56e547cb057a25d07612a6eb1c6cb415004c8ef7c7096fe3204714e(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterNode],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc81668fe15038bf2abc0120b1e6f589b383a39206888122ca850044329a3bfd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1d29b5fe513f2e85cf52aefefd94d542a7745f1f9634dda5e4b1be2eb5be6fa(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameter],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61809a554eeb88b3f45b401f1246c1075998ae05ab7a23a06d1335c6882a0f6a(
    *,
    min_limit: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07e6ae39477c9d0947cf6293f38cd0b584ee798fa7082d008b4cabe59aae88bd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6601512049cc59a57e3848cbb2316944a99c57b5eae8fa4a63e3f045a1d504c0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9030c498df8b6dfb71c3a7129b3d4b73327e5c02bcb26b75b2616ed4b5587884(
    value: typing.Optional[ManagedDatabaseOpensearchPropertiesShardIndexingPressurePrimaryParameterShard],
) -> None:
    """Type checking stubs"""
    pass
