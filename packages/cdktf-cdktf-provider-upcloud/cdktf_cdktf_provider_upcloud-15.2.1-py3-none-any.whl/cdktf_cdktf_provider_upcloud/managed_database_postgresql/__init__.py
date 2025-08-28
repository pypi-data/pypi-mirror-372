r'''
# `upcloud_managed_database_postgresql`

Refer to the Terraform Registry for docs: [`upcloud_managed_database_postgresql`](https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql).
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


class ManagedDatabasePostgresql(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabasePostgresql.ManagedDatabasePostgresql",
):
    '''Represents a {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql upcloud_managed_database_postgresql}.'''

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
        network: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedDatabasePostgresqlNetwork", typing.Dict[builtins.str, typing.Any]]]]] = None,
        powered: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        properties: typing.Optional[typing.Union["ManagedDatabasePostgresqlProperties", typing.Dict[builtins.str, typing.Any]]] = None,
        termination_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql upcloud_managed_database_postgresql} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Name of the service. The name is used as a prefix for the logical hostname. Must be unique within an account Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#name ManagedDatabasePostgresql#name}
        :param plan: Service plan to use. This determines how much resources the instance will have. You can list available plans with ``upctl database plans <type>``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#plan ManagedDatabasePostgresql#plan}
        :param title: Title of a managed database instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#title ManagedDatabasePostgresql#title}
        :param zone: Zone where the instance resides, e.g. ``de-fra1``. You can list available zones with ``upctl zone list``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#zone ManagedDatabasePostgresql#zone}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#id ManagedDatabasePostgresql#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param labels: User defined key-value pairs to classify the managed database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#labels ManagedDatabasePostgresql#labels}
        :param maintenance_window_dow: Maintenance window day of week. Lower case weekday name (monday, tuesday, ...). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#maintenance_window_dow ManagedDatabasePostgresql#maintenance_window_dow}
        :param maintenance_window_time: Maintenance window UTC time in hh:mm:ss format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#maintenance_window_time ManagedDatabasePostgresql#maintenance_window_time}
        :param network: network block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#network ManagedDatabasePostgresql#network}
        :param powered: The administrative power state of the service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#powered ManagedDatabasePostgresql#powered}
        :param properties: properties block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#properties ManagedDatabasePostgresql#properties}
        :param termination_protection: If set to true, prevents the managed service from being powered off, or deleted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#termination_protection ManagedDatabasePostgresql#termination_protection}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fa809510c8f69da52891462ee8f64a2638b82c8a731ae399fb00992f714b475)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ManagedDatabasePostgresqlConfig(
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
        '''Generates CDKTF code for importing a ManagedDatabasePostgresql resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ManagedDatabasePostgresql to import.
        :param import_from_id: The id of the existing ManagedDatabasePostgresql that should be imported. Refer to the {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ManagedDatabasePostgresql to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__571201bbf7edad587623dcace5caa1c79f3a3df20b06c10b6b082be7ace14fb8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putNetwork")
    def put_network(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedDatabasePostgresqlNetwork", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbbb3dfe7015b488e0b1c155e305ab2c73855a004722f839bee402b92a211b69)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNetwork", [value]))

    @jsii.member(jsii_name="putProperties")
    def put_properties(
        self,
        *,
        admin_password: typing.Optional[builtins.str] = None,
        admin_username: typing.Optional[builtins.str] = None,
        automatic_utility_network_ip_filter: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        autovacuum_analyze_scale_factor: typing.Optional[jsii.Number] = None,
        autovacuum_analyze_threshold: typing.Optional[jsii.Number] = None,
        autovacuum_freeze_max_age: typing.Optional[jsii.Number] = None,
        autovacuum_max_workers: typing.Optional[jsii.Number] = None,
        autovacuum_naptime: typing.Optional[jsii.Number] = None,
        autovacuum_vacuum_cost_delay: typing.Optional[jsii.Number] = None,
        autovacuum_vacuum_cost_limit: typing.Optional[jsii.Number] = None,
        autovacuum_vacuum_scale_factor: typing.Optional[jsii.Number] = None,
        autovacuum_vacuum_threshold: typing.Optional[jsii.Number] = None,
        backup_hour: typing.Optional[jsii.Number] = None,
        backup_minute: typing.Optional[jsii.Number] = None,
        bgwriter_delay: typing.Optional[jsii.Number] = None,
        bgwriter_flush_after: typing.Optional[jsii.Number] = None,
        bgwriter_lru_maxpages: typing.Optional[jsii.Number] = None,
        bgwriter_lru_multiplier: typing.Optional[jsii.Number] = None,
        deadlock_timeout: typing.Optional[jsii.Number] = None,
        default_toast_compression: typing.Optional[builtins.str] = None,
        idle_in_transaction_session_timeout: typing.Optional[jsii.Number] = None,
        ip_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
        jit: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        log_autovacuum_min_duration: typing.Optional[jsii.Number] = None,
        log_error_verbosity: typing.Optional[builtins.str] = None,
        log_line_prefix: typing.Optional[builtins.str] = None,
        log_min_duration_statement: typing.Optional[jsii.Number] = None,
        log_temp_files: typing.Optional[jsii.Number] = None,
        max_connections: typing.Optional[jsii.Number] = None,
        max_files_per_process: typing.Optional[jsii.Number] = None,
        max_locks_per_transaction: typing.Optional[jsii.Number] = None,
        max_logical_replication_workers: typing.Optional[jsii.Number] = None,
        max_parallel_workers: typing.Optional[jsii.Number] = None,
        max_parallel_workers_per_gather: typing.Optional[jsii.Number] = None,
        max_pred_locks_per_transaction: typing.Optional[jsii.Number] = None,
        max_prepared_transactions: typing.Optional[jsii.Number] = None,
        max_replication_slots: typing.Optional[jsii.Number] = None,
        max_slot_wal_keep_size: typing.Optional[jsii.Number] = None,
        max_stack_depth: typing.Optional[jsii.Number] = None,
        max_standby_archive_delay: typing.Optional[jsii.Number] = None,
        max_standby_streaming_delay: typing.Optional[jsii.Number] = None,
        max_sync_workers_per_subscription: typing.Optional[jsii.Number] = None,
        max_wal_senders: typing.Optional[jsii.Number] = None,
        max_worker_processes: typing.Optional[jsii.Number] = None,
        migration: typing.Optional[typing.Union["ManagedDatabasePostgresqlPropertiesMigration", typing.Dict[builtins.str, typing.Any]]] = None,
        password_encryption: typing.Optional[builtins.str] = None,
        pgaudit: typing.Optional[typing.Union["ManagedDatabasePostgresqlPropertiesPgaudit", typing.Dict[builtins.str, typing.Any]]] = None,
        pgbouncer: typing.Optional[typing.Union["ManagedDatabasePostgresqlPropertiesPgbouncer", typing.Dict[builtins.str, typing.Any]]] = None,
        pglookout: typing.Optional[typing.Union["ManagedDatabasePostgresqlPropertiesPglookout", typing.Dict[builtins.str, typing.Any]]] = None,
        pg_partman_bgw_interval: typing.Optional[jsii.Number] = None,
        pg_partman_bgw_role: typing.Optional[builtins.str] = None,
        pg_stat_monitor_enable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        pg_stat_monitor_pgsm_enable_query_plan: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        pg_stat_monitor_pgsm_max_buckets: typing.Optional[jsii.Number] = None,
        pg_stat_statements_track: typing.Optional[builtins.str] = None,
        public_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        service_log: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        shared_buffers_percentage: typing.Optional[jsii.Number] = None,
        synchronous_replication: typing.Optional[builtins.str] = None,
        temp_file_limit: typing.Optional[jsii.Number] = None,
        timescaledb: typing.Optional[typing.Union["ManagedDatabasePostgresqlPropertiesTimescaledb", typing.Dict[builtins.str, typing.Any]]] = None,
        timezone: typing.Optional[builtins.str] = None,
        track_activity_query_size: typing.Optional[jsii.Number] = None,
        track_commit_timestamp: typing.Optional[builtins.str] = None,
        track_functions: typing.Optional[builtins.str] = None,
        track_io_timing: typing.Optional[builtins.str] = None,
        variant: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
        wal_sender_timeout: typing.Optional[jsii.Number] = None,
        wal_writer_delay: typing.Optional[jsii.Number] = None,
        work_mem: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param admin_password: Custom password for admin user. Defaults to random string. This must be set only when a new service is being created. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#admin_password ManagedDatabasePostgresql#admin_password}
        :param admin_username: Custom username for admin user. This must be set only when a new service is being created. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#admin_username ManagedDatabasePostgresql#admin_username}
        :param automatic_utility_network_ip_filter: Automatic utility network IP Filter. Automatically allow connections from servers in the utility network within the same zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#automatic_utility_network_ip_filter ManagedDatabasePostgresql#automatic_utility_network_ip_filter}
        :param autovacuum_analyze_scale_factor: Specifies a fraction of the table size to add to autovacuum_analyze_threshold when deciding whether to trigger an ANALYZE (e.g. ``0.2`` for 20% of the table size). The default is ``0.2``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autovacuum_analyze_scale_factor ManagedDatabasePostgresql#autovacuum_analyze_scale_factor}
        :param autovacuum_analyze_threshold: Specifies the minimum number of inserted, updated or deleted tuples needed to trigger an ANALYZE in any one table. The default is ``50``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autovacuum_analyze_threshold ManagedDatabasePostgresql#autovacuum_analyze_threshold}
        :param autovacuum_freeze_max_age: Specifies the maximum age (in transactions) that a table's pg_class.relfrozenxid field can attain before a VACUUM operation is forced to prevent transaction ID wraparound within the table. The system launches autovacuum processes to prevent wraparound even when autovacuum is otherwise disabled. Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autovacuum_freeze_max_age ManagedDatabasePostgresql#autovacuum_freeze_max_age}
        :param autovacuum_max_workers: Specifies the maximum number of autovacuum processes (other than the autovacuum launcher) that may be running at any one time. The default is ``3``. Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autovacuum_max_workers ManagedDatabasePostgresql#autovacuum_max_workers}
        :param autovacuum_naptime: Specifies the minimum delay between autovacuum runs on any given database. The delay is measured in seconds. The default is ``60``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autovacuum_naptime ManagedDatabasePostgresql#autovacuum_naptime}
        :param autovacuum_vacuum_cost_delay: Specifies the cost delay value that will be used in automatic VACUUM operations. If ``-1`` is specified, the regular vacuum_cost_delay value will be used. The default is ``2`` (upstream default). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autovacuum_vacuum_cost_delay ManagedDatabasePostgresql#autovacuum_vacuum_cost_delay}
        :param autovacuum_vacuum_cost_limit: Specifies the cost limit value that will be used in automatic VACUUM operations. If ``-1`` is specified, the regular vacuum_cost_limit value will be used. The default is ``-1`` (upstream default). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autovacuum_vacuum_cost_limit ManagedDatabasePostgresql#autovacuum_vacuum_cost_limit}
        :param autovacuum_vacuum_scale_factor: Specifies a fraction of the table size to add to autovacuum_vacuum_threshold when deciding whether to trigger a VACUUM (e.g. ``0.2`` for 20% of the table size). The default is ``0.2``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autovacuum_vacuum_scale_factor ManagedDatabasePostgresql#autovacuum_vacuum_scale_factor}
        :param autovacuum_vacuum_threshold: Specifies the minimum number of updated or deleted tuples needed to trigger a VACUUM in any one table. The default is ``50``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autovacuum_vacuum_threshold ManagedDatabasePostgresql#autovacuum_vacuum_threshold}
        :param backup_hour: The hour of day (in UTC) when backup for the service is started. New backup is only started if previous backup has already completed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#backup_hour ManagedDatabasePostgresql#backup_hour}
        :param backup_minute: The minute of an hour when backup for the service is started. New backup is only started if previous backup has already completed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#backup_minute ManagedDatabasePostgresql#backup_minute}
        :param bgwriter_delay: Specifies the delay between activity rounds for the background writer in milliseconds. The default is ``200``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#bgwriter_delay ManagedDatabasePostgresql#bgwriter_delay}
        :param bgwriter_flush_after: Whenever more than bgwriter_flush_after bytes have been written by the background writer, attempt to force the OS to issue these writes to the underlying storage. Specified in kilobytes. Setting of 0 disables forced writeback. The default is ``512``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#bgwriter_flush_after ManagedDatabasePostgresql#bgwriter_flush_after}
        :param bgwriter_lru_maxpages: In each round, no more than this many buffers will be written by the background writer. Setting this to zero disables background writing. The default is ``100``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#bgwriter_lru_maxpages ManagedDatabasePostgresql#bgwriter_lru_maxpages}
        :param bgwriter_lru_multiplier: The average recent need for new buffers is multiplied by bgwriter_lru_multiplier to arrive at an estimate of the number that will be needed during the next round, (up to bgwriter_lru_maxpages). 1.0 represents a “just in time” policy of writing exactly the number of buffers predicted to be needed. Larger values provide some cushion against spikes in demand, while smaller values intentionally leave writes to be done by server processes. The default is ``2.0``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#bgwriter_lru_multiplier ManagedDatabasePostgresql#bgwriter_lru_multiplier}
        :param deadlock_timeout: This is the amount of time, in milliseconds, to wait on a lock before checking to see if there is a deadlock condition. The default is ``1000`` (upstream default). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#deadlock_timeout ManagedDatabasePostgresql#deadlock_timeout}
        :param default_toast_compression: Specifies the default TOAST compression method for values of compressible columns. The default is ``lz4``. Only available for PostgreSQL 14+. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#default_toast_compression ManagedDatabasePostgresql#default_toast_compression}
        :param idle_in_transaction_session_timeout: Time out sessions with open transactions after this number of milliseconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#idle_in_transaction_session_timeout ManagedDatabasePostgresql#idle_in_transaction_session_timeout}
        :param ip_filter: IP filter. Allow incoming connections from CIDR address block, e.g. '10.20.0.0/16'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#ip_filter ManagedDatabasePostgresql#ip_filter}
        :param jit: Controls system-wide use of Just-in-Time Compilation (JIT). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#jit ManagedDatabasePostgresql#jit}
        :param log_autovacuum_min_duration: Causes each action executed by autovacuum to be logged if it ran for at least the specified number of milliseconds. Setting this to zero logs all autovacuum actions. Minus-one disables logging autovacuum actions. The default is ``1000``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_autovacuum_min_duration ManagedDatabasePostgresql#log_autovacuum_min_duration}
        :param log_error_verbosity: Controls the amount of detail written in the server log for each message that is logged. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_error_verbosity ManagedDatabasePostgresql#log_error_verbosity}
        :param log_line_prefix: Choose from one of the available log formats. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_line_prefix ManagedDatabasePostgresql#log_line_prefix}
        :param log_min_duration_statement: Log statements that take more than this number of milliseconds to run, -1 disables. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_min_duration_statement ManagedDatabasePostgresql#log_min_duration_statement}
        :param log_temp_files: Log statements for each temporary file created larger than this number of kilobytes, -1 disables. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_temp_files ManagedDatabasePostgresql#log_temp_files}
        :param max_connections: PostgreSQL maximum number of concurrent connections to the database server. Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_connections ManagedDatabasePostgresql#max_connections}
        :param max_files_per_process: PostgreSQL maximum number of files that can be open per process. The default is ``1000`` (upstream default). Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_files_per_process ManagedDatabasePostgresql#max_files_per_process}
        :param max_locks_per_transaction: PostgreSQL maximum locks per transaction. Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_locks_per_transaction ManagedDatabasePostgresql#max_locks_per_transaction}
        :param max_logical_replication_workers: PostgreSQL maximum logical replication workers (taken from the pool of max_parallel_workers). The default is ``4`` (upstream default). Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_logical_replication_workers ManagedDatabasePostgresql#max_logical_replication_workers}
        :param max_parallel_workers: Sets the maximum number of workers that the system can support for parallel queries. The default is ``8`` (upstream default). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_parallel_workers ManagedDatabasePostgresql#max_parallel_workers}
        :param max_parallel_workers_per_gather: Sets the maximum number of workers that can be started by a single Gather or Gather Merge node. The default is ``2`` (upstream default). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_parallel_workers_per_gather ManagedDatabasePostgresql#max_parallel_workers_per_gather}
        :param max_pred_locks_per_transaction: PostgreSQL maximum predicate locks per transaction. The default is ``64`` (upstream default). Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_pred_locks_per_transaction ManagedDatabasePostgresql#max_pred_locks_per_transaction}
        :param max_prepared_transactions: PostgreSQL maximum prepared transactions. The default is ``0``. Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_prepared_transactions ManagedDatabasePostgresql#max_prepared_transactions}
        :param max_replication_slots: PostgreSQL maximum replication slots. The default is ``20``. Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_replication_slots ManagedDatabasePostgresql#max_replication_slots}
        :param max_slot_wal_keep_size: PostgreSQL maximum WAL size (MB) reserved for replication slots. If ``-1`` is specified, replication slots may retain an unlimited amount of WAL files. The default is ``-1`` (upstream default). wal_keep_size minimum WAL size setting takes precedence over this. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_slot_wal_keep_size ManagedDatabasePostgresql#max_slot_wal_keep_size}
        :param max_stack_depth: Maximum depth of the stack in bytes. The default is ``2097152`` (upstream default). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_stack_depth ManagedDatabasePostgresql#max_stack_depth}
        :param max_standby_archive_delay: Max standby archive delay in milliseconds. The default is ``30000`` (upstream default). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_standby_archive_delay ManagedDatabasePostgresql#max_standby_archive_delay}
        :param max_standby_streaming_delay: Max standby streaming delay in milliseconds. The default is ``30000`` (upstream default). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_standby_streaming_delay ManagedDatabasePostgresql#max_standby_streaming_delay}
        :param max_sync_workers_per_subscription: Maximum number of synchronization workers per subscription. The default is ``2``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_sync_workers_per_subscription ManagedDatabasePostgresql#max_sync_workers_per_subscription}
        :param max_wal_senders: PostgreSQL maximum WAL senders. The default is ``20``. Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_wal_senders ManagedDatabasePostgresql#max_wal_senders}
        :param max_worker_processes: Sets the maximum number of background processes that the system can support. The default is ``8``. Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_worker_processes ManagedDatabasePostgresql#max_worker_processes}
        :param migration: migration block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#migration ManagedDatabasePostgresql#migration}
        :param password_encryption: Chooses the algorithm for encrypting passwords. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#password_encryption ManagedDatabasePostgresql#password_encryption}
        :param pgaudit: pgaudit block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#pgaudit ManagedDatabasePostgresql#pgaudit}
        :param pgbouncer: pgbouncer block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#pgbouncer ManagedDatabasePostgresql#pgbouncer}
        :param pglookout: pglookout block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#pglookout ManagedDatabasePostgresql#pglookout}
        :param pg_partman_bgw_interval: Sets the time interval in seconds to run pg_partman's scheduled tasks. The default is ``3600``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#pg_partman_bgw_interval ManagedDatabasePostgresql#pg_partman_bgw_interval}
        :param pg_partman_bgw_role: Controls which role to use for pg_partman's scheduled background tasks. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#pg_partman_bgw_role ManagedDatabasePostgresql#pg_partman_bgw_role}
        :param pg_stat_monitor_enable: Enable pg_stat_monitor extension if available for the current cluster. Enable the pg_stat_monitor extension. Changing this parameter causes a service restart. When this extension is enabled, pg_stat_statements results for utility commands are unreliable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#pg_stat_monitor_enable ManagedDatabasePostgresql#pg_stat_monitor_enable}
        :param pg_stat_monitor_pgsm_enable_query_plan: Enables or disables query plan monitoring. Changing this parameter causes a service restart. Only available for PostgreSQL 13+. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#pg_stat_monitor_pgsm_enable_query_plan ManagedDatabasePostgresql#pg_stat_monitor_pgsm_enable_query_plan}
        :param pg_stat_monitor_pgsm_max_buckets: Sets the maximum number of buckets. Changing this parameter causes a service restart. Only available for PostgreSQL 13+. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#pg_stat_monitor_pgsm_max_buckets ManagedDatabasePostgresql#pg_stat_monitor_pgsm_max_buckets}
        :param pg_stat_statements_track: Controls which statements are counted. Specify top to track top-level statements (those issued directly by clients), all to also track nested statements (such as statements invoked within functions), or none to disable statement statistics collection. The default is ``top``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#pg_stat_statements_track ManagedDatabasePostgresql#pg_stat_statements_track}
        :param public_access: Public Access. Allow access to the service from the public Internet. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#public_access ManagedDatabasePostgresql#public_access}
        :param service_log: Service logging. Store logs for the service so that they are available in the HTTP API and console. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#service_log ManagedDatabasePostgresql#service_log}
        :param shared_buffers_percentage: Percentage of total RAM that the database server uses for shared memory buffers. Valid range is 20-60 (float), which corresponds to 20% - 60%. This setting adjusts the shared_buffers configuration value. Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#shared_buffers_percentage ManagedDatabasePostgresql#shared_buffers_percentage}
        :param synchronous_replication: Synchronous replication type. Note that the service plan also needs to support synchronous replication. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#synchronous_replication ManagedDatabasePostgresql#synchronous_replication}
        :param temp_file_limit: PostgreSQL temporary file limit in KiB, -1 for unlimited. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#temp_file_limit ManagedDatabasePostgresql#temp_file_limit}
        :param timescaledb: timescaledb block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#timescaledb ManagedDatabasePostgresql#timescaledb}
        :param timezone: PostgreSQL service timezone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#timezone ManagedDatabasePostgresql#timezone}
        :param track_activity_query_size: Specifies the number of bytes reserved to track the currently executing command for each active session. Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#track_activity_query_size ManagedDatabasePostgresql#track_activity_query_size}
        :param track_commit_timestamp: Record commit time of transactions. Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#track_commit_timestamp ManagedDatabasePostgresql#track_commit_timestamp}
        :param track_functions: Enables tracking of function call counts and time used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#track_functions ManagedDatabasePostgresql#track_functions}
        :param track_io_timing: Enables timing of database I/O calls. The default is ``off``. When on, it will repeatedly query the operating system for the current time, which may cause significant overhead on some platforms. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#track_io_timing ManagedDatabasePostgresql#track_io_timing}
        :param variant: Variant of the PostgreSQL service, may affect the features that are exposed by default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#variant ManagedDatabasePostgresql#variant}
        :param version: PostgreSQL major version. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#version ManagedDatabasePostgresql#version}
        :param wal_sender_timeout: Terminate replication connections that are inactive for longer than this amount of time, in milliseconds. Setting this value to zero disables the timeout. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#wal_sender_timeout ManagedDatabasePostgresql#wal_sender_timeout}
        :param wal_writer_delay: WAL flush interval in milliseconds. The default is ``200``. Setting this parameter to a lower value may negatively impact performance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#wal_writer_delay ManagedDatabasePostgresql#wal_writer_delay}
        :param work_mem: Sets the maximum amount of memory to be used by a query operation (such as a sort or hash table) before writing to temporary disk files, in MB. The default is 1MB + 0.075% of total RAM (up to 32MB). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#work_mem ManagedDatabasePostgresql#work_mem}
        '''
        value = ManagedDatabasePostgresqlProperties(
            admin_password=admin_password,
            admin_username=admin_username,
            automatic_utility_network_ip_filter=automatic_utility_network_ip_filter,
            autovacuum_analyze_scale_factor=autovacuum_analyze_scale_factor,
            autovacuum_analyze_threshold=autovacuum_analyze_threshold,
            autovacuum_freeze_max_age=autovacuum_freeze_max_age,
            autovacuum_max_workers=autovacuum_max_workers,
            autovacuum_naptime=autovacuum_naptime,
            autovacuum_vacuum_cost_delay=autovacuum_vacuum_cost_delay,
            autovacuum_vacuum_cost_limit=autovacuum_vacuum_cost_limit,
            autovacuum_vacuum_scale_factor=autovacuum_vacuum_scale_factor,
            autovacuum_vacuum_threshold=autovacuum_vacuum_threshold,
            backup_hour=backup_hour,
            backup_minute=backup_minute,
            bgwriter_delay=bgwriter_delay,
            bgwriter_flush_after=bgwriter_flush_after,
            bgwriter_lru_maxpages=bgwriter_lru_maxpages,
            bgwriter_lru_multiplier=bgwriter_lru_multiplier,
            deadlock_timeout=deadlock_timeout,
            default_toast_compression=default_toast_compression,
            idle_in_transaction_session_timeout=idle_in_transaction_session_timeout,
            ip_filter=ip_filter,
            jit=jit,
            log_autovacuum_min_duration=log_autovacuum_min_duration,
            log_error_verbosity=log_error_verbosity,
            log_line_prefix=log_line_prefix,
            log_min_duration_statement=log_min_duration_statement,
            log_temp_files=log_temp_files,
            max_connections=max_connections,
            max_files_per_process=max_files_per_process,
            max_locks_per_transaction=max_locks_per_transaction,
            max_logical_replication_workers=max_logical_replication_workers,
            max_parallel_workers=max_parallel_workers,
            max_parallel_workers_per_gather=max_parallel_workers_per_gather,
            max_pred_locks_per_transaction=max_pred_locks_per_transaction,
            max_prepared_transactions=max_prepared_transactions,
            max_replication_slots=max_replication_slots,
            max_slot_wal_keep_size=max_slot_wal_keep_size,
            max_stack_depth=max_stack_depth,
            max_standby_archive_delay=max_standby_archive_delay,
            max_standby_streaming_delay=max_standby_streaming_delay,
            max_sync_workers_per_subscription=max_sync_workers_per_subscription,
            max_wal_senders=max_wal_senders,
            max_worker_processes=max_worker_processes,
            migration=migration,
            password_encryption=password_encryption,
            pgaudit=pgaudit,
            pgbouncer=pgbouncer,
            pglookout=pglookout,
            pg_partman_bgw_interval=pg_partman_bgw_interval,
            pg_partman_bgw_role=pg_partman_bgw_role,
            pg_stat_monitor_enable=pg_stat_monitor_enable,
            pg_stat_monitor_pgsm_enable_query_plan=pg_stat_monitor_pgsm_enable_query_plan,
            pg_stat_monitor_pgsm_max_buckets=pg_stat_monitor_pgsm_max_buckets,
            pg_stat_statements_track=pg_stat_statements_track,
            public_access=public_access,
            service_log=service_log,
            shared_buffers_percentage=shared_buffers_percentage,
            synchronous_replication=synchronous_replication,
            temp_file_limit=temp_file_limit,
            timescaledb=timescaledb,
            timezone=timezone,
            track_activity_query_size=track_activity_query_size,
            track_commit_timestamp=track_commit_timestamp,
            track_functions=track_functions,
            track_io_timing=track_io_timing,
            variant=variant,
            version=version,
            wal_sender_timeout=wal_sender_timeout,
            wal_writer_delay=wal_writer_delay,
            work_mem=work_mem,
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
    def components(self) -> "ManagedDatabasePostgresqlComponentsList":
        return typing.cast("ManagedDatabasePostgresqlComponentsList", jsii.get(self, "components"))

    @builtins.property
    @jsii.member(jsii_name="network")
    def network(self) -> "ManagedDatabasePostgresqlNetworkList":
        return typing.cast("ManagedDatabasePostgresqlNetworkList", jsii.get(self, "network"))

    @builtins.property
    @jsii.member(jsii_name="nodeStates")
    def node_states(self) -> "ManagedDatabasePostgresqlNodeStatesList":
        return typing.cast("ManagedDatabasePostgresqlNodeStatesList", jsii.get(self, "nodeStates"))

    @builtins.property
    @jsii.member(jsii_name="primaryDatabase")
    def primary_database(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "primaryDatabase"))

    @builtins.property
    @jsii.member(jsii_name="properties")
    def properties(self) -> "ManagedDatabasePostgresqlPropertiesOutputReference":
        return typing.cast("ManagedDatabasePostgresqlPropertiesOutputReference", jsii.get(self, "properties"))

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
    @jsii.member(jsii_name="sslmode")
    def sslmode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sslmode"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedDatabasePostgresqlNetwork"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedDatabasePostgresqlNetwork"]]], jsii.get(self, "networkInput"))

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
    ) -> typing.Optional["ManagedDatabasePostgresqlProperties"]:
        return typing.cast(typing.Optional["ManagedDatabasePostgresqlProperties"], jsii.get(self, "propertiesInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__f9a630d3a04b1e85d141f152306b1446a41a3f48ba0d2183d43b5587ed01b4e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d237b647d468f025eced5d1f869c5704b40f8d693184cae12ed221d60d195bca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "labels", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowDow")
    def maintenance_window_dow(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maintenanceWindowDow"))

    @maintenance_window_dow.setter
    def maintenance_window_dow(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2c0f77034fed7e75ffc25cc3f6dbd523c87396fc50302ef44e7a62fb55bccd3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maintenanceWindowDow", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowTime")
    def maintenance_window_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maintenanceWindowTime"))

    @maintenance_window_time.setter
    def maintenance_window_time(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3b522c1e2fa5f9ebcbd420abad1f5687e71bf47b1f53b8aba4d8eae624c15f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maintenanceWindowTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b616f5a643e9362103bfe51d176cebeb11c5a7c116871765dc94705dfef5db23)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="plan")
    def plan(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "plan"))

    @plan.setter
    def plan(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62ca746fcdc84d286b895013db6a84b26e62e0d3f9368d2e25f84a74a7264b94)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ea14ac222a06ab006f9282ded2425426342e694303ff49e133423cad91b073d2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a040b3151c2d2f9c017cfde26b6d5f6d6408e630f17d6eab06dd6c1142465b2b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terminationProtection", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @title.setter
    def title(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a6d4eea83ac11ab3241ebe5783562662925bb3b73987673a1f5bd2da77529d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "title", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zone")
    def zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zone"))

    @zone.setter
    def zone(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8e769b3f7bdff6efb6eeabc49ebfb039d0a13ba0401e55deb7401478cc6ed17)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zone", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabasePostgresql.ManagedDatabasePostgresqlComponents",
    jsii_struct_bases=[],
    name_mapping={},
)
class ManagedDatabasePostgresqlComponents:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabasePostgresqlComponents(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabasePostgresqlComponentsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabasePostgresql.ManagedDatabasePostgresqlComponentsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7b6a3962c8507785c3645c0b9c137496603c528b307ef84fbc81f8718c4023cd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ManagedDatabasePostgresqlComponentsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c2bbea3f665bf989974836bb45ee48957afef39c46c57d80210f6b103ce05c8)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ManagedDatabasePostgresqlComponentsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47d3f8173c3c000fe3926caf6e494fc6cddb15ac79d3c90a3aa20089abc9431f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4ee6156235319d8ff5191af25d8e1cd5758406c4efcc4fa304274758654ff952)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a9ceac319a9c2fe1f1572d1ef10795a5bd5a1de81fb1d7f4cb2ddeafe2a500c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class ManagedDatabasePostgresqlComponentsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabasePostgresql.ManagedDatabasePostgresqlComponentsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__83ec3ca2d809487f6fddb91dcdaf317ca8f3bb5d75792bb13ec00c6e612a3d4d)
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
    def internal_value(self) -> typing.Optional[ManagedDatabasePostgresqlComponents]:
        return typing.cast(typing.Optional[ManagedDatabasePostgresqlComponents], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabasePostgresqlComponents],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2a3104ae2962fdb60f3b3307320726a7821e29d9fe32777924514d905a12282)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabasePostgresql.ManagedDatabasePostgresqlConfig",
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
class ManagedDatabasePostgresqlConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        network: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedDatabasePostgresqlNetwork", typing.Dict[builtins.str, typing.Any]]]]] = None,
        powered: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        properties: typing.Optional[typing.Union["ManagedDatabasePostgresqlProperties", typing.Dict[builtins.str, typing.Any]]] = None,
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
        :param name: Name of the service. The name is used as a prefix for the logical hostname. Must be unique within an account Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#name ManagedDatabasePostgresql#name}
        :param plan: Service plan to use. This determines how much resources the instance will have. You can list available plans with ``upctl database plans <type>``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#plan ManagedDatabasePostgresql#plan}
        :param title: Title of a managed database instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#title ManagedDatabasePostgresql#title}
        :param zone: Zone where the instance resides, e.g. ``de-fra1``. You can list available zones with ``upctl zone list``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#zone ManagedDatabasePostgresql#zone}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#id ManagedDatabasePostgresql#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param labels: User defined key-value pairs to classify the managed database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#labels ManagedDatabasePostgresql#labels}
        :param maintenance_window_dow: Maintenance window day of week. Lower case weekday name (monday, tuesday, ...). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#maintenance_window_dow ManagedDatabasePostgresql#maintenance_window_dow}
        :param maintenance_window_time: Maintenance window UTC time in hh:mm:ss format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#maintenance_window_time ManagedDatabasePostgresql#maintenance_window_time}
        :param network: network block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#network ManagedDatabasePostgresql#network}
        :param powered: The administrative power state of the service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#powered ManagedDatabasePostgresql#powered}
        :param properties: properties block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#properties ManagedDatabasePostgresql#properties}
        :param termination_protection: If set to true, prevents the managed service from being powered off, or deleted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#termination_protection ManagedDatabasePostgresql#termination_protection}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(properties, dict):
            properties = ManagedDatabasePostgresqlProperties(**properties)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45f42ebdf030afdba0d57f507b07d90736dd58b3b6241153662af2f459e6929b)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#name ManagedDatabasePostgresql#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def plan(self) -> builtins.str:
        '''Service plan to use.

        This determines how much resources the instance will have. You can list available plans with ``upctl database plans <type>``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#plan ManagedDatabasePostgresql#plan}
        '''
        result = self._values.get("plan")
        assert result is not None, "Required property 'plan' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''Title of a managed database instance.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#title ManagedDatabasePostgresql#title}
        '''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def zone(self) -> builtins.str:
        '''Zone where the instance resides, e.g. ``de-fra1``. You can list available zones with ``upctl zone list``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#zone ManagedDatabasePostgresql#zone}
        '''
        result = self._values.get("zone")
        assert result is not None, "Required property 'zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#id ManagedDatabasePostgresql#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''User defined key-value pairs to classify the managed database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#labels ManagedDatabasePostgresql#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def maintenance_window_dow(self) -> typing.Optional[builtins.str]:
        '''Maintenance window day of week. Lower case weekday name (monday, tuesday, ...).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#maintenance_window_dow ManagedDatabasePostgresql#maintenance_window_dow}
        '''
        result = self._values.get("maintenance_window_dow")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maintenance_window_time(self) -> typing.Optional[builtins.str]:
        '''Maintenance window UTC time in hh:mm:ss format.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#maintenance_window_time ManagedDatabasePostgresql#maintenance_window_time}
        '''
        result = self._values.get("maintenance_window_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedDatabasePostgresqlNetwork"]]]:
        '''network block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#network ManagedDatabasePostgresql#network}
        '''
        result = self._values.get("network")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedDatabasePostgresqlNetwork"]]], result)

    @builtins.property
    def powered(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''The administrative power state of the service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#powered ManagedDatabasePostgresql#powered}
        '''
        result = self._values.get("powered")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def properties(self) -> typing.Optional["ManagedDatabasePostgresqlProperties"]:
        '''properties block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#properties ManagedDatabasePostgresql#properties}
        '''
        result = self._values.get("properties")
        return typing.cast(typing.Optional["ManagedDatabasePostgresqlProperties"], result)

    @builtins.property
    def termination_protection(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set to true, prevents the managed service from being powered off, or deleted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#termination_protection ManagedDatabasePostgresql#termination_protection}
        '''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabasePostgresqlConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabasePostgresql.ManagedDatabasePostgresqlNetwork",
    jsii_struct_bases=[],
    name_mapping={"family": "family", "name": "name", "type": "type", "uuid": "uuid"},
)
class ManagedDatabasePostgresqlNetwork:
    def __init__(
        self,
        *,
        family: builtins.str,
        name: builtins.str,
        type: builtins.str,
        uuid: builtins.str,
    ) -> None:
        '''
        :param family: Network family. Currently only ``IPv4`` is supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#family ManagedDatabasePostgresql#family}
        :param name: The name of the network. Must be unique within the service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#name ManagedDatabasePostgresql#name}
        :param type: The type of the network. Must be private. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#type ManagedDatabasePostgresql#type}
        :param uuid: Private network UUID. Must reside in the same zone as the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#uuid ManagedDatabasePostgresql#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5737b331959851ea941ce795bfc130d63e5ac24633787479fac442c8d6e54407)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#family ManagedDatabasePostgresql#family}
        '''
        result = self._values.get("family")
        assert result is not None, "Required property 'family' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the network. Must be unique within the service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#name ManagedDatabasePostgresql#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''The type of the network. Must be private.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#type ManagedDatabasePostgresql#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def uuid(self) -> builtins.str:
        '''Private network UUID. Must reside in the same zone as the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#uuid ManagedDatabasePostgresql#uuid}
        '''
        result = self._values.get("uuid")
        assert result is not None, "Required property 'uuid' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabasePostgresqlNetwork(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabasePostgresqlNetworkList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabasePostgresql.ManagedDatabasePostgresqlNetworkList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b3b947cc2484ffb23bbafd58aa46b1a5c58cfbe888b01cf39fdab8d0ceaaf695)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ManagedDatabasePostgresqlNetworkOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a360dd571f33825fe94a1c525824de2b6b6956a728a48d2b2bdd61f6557e9e3d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ManagedDatabasePostgresqlNetworkOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__409ed79705ae4380a337e7bdf603a4ccf6d324f3ebe87024e49a3261703efc8c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e527f157396ba616a48da774b0d360a6f4aaff257be3460fdf3195f85dc119d2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b995063066d133b223f91e57e786991501f7f6ef4db004beb2d18daeb8a65aa8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedDatabasePostgresqlNetwork]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedDatabasePostgresqlNetwork]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedDatabasePostgresqlNetwork]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80edead81e58717b2e65e007e33b02196e634c72111cd07c76b3f587de0f4f34)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ManagedDatabasePostgresqlNetworkOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabasePostgresql.ManagedDatabasePostgresqlNetworkOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0ba9c3d39eb1c44f562260266c493ed246f4ef7c0f77ccc1999be2f1591fea8a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d91f571ddaa3e094e149844de7c144597f83eb5aaca79f72a86cec6e58c672c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "family", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__460f49c71e7ba9909b6c7e6724334fbc1b82ea4c0d018a7f0c42230222c6e7d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33e124f5de2e3777f97e94b613d5f82b6b1ef5ddab810c1648eb135ec8fd4ca7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4085f8142c211fdc139fc6a946b712a7cf489b0e7bffdba7a3d0d330a30bd883)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedDatabasePostgresqlNetwork]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedDatabasePostgresqlNetwork]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedDatabasePostgresqlNetwork]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1cccfea5a3b234cba4824b362afd23a009b35c8cfaa17da2f59f7e84412b8c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabasePostgresql.ManagedDatabasePostgresqlNodeStates",
    jsii_struct_bases=[],
    name_mapping={},
)
class ManagedDatabasePostgresqlNodeStates:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabasePostgresqlNodeStates(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabasePostgresqlNodeStatesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabasePostgresql.ManagedDatabasePostgresqlNodeStatesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__970899e82ef0d640d5cb8230a8fae3d8913f2ea73e5763ea4b69f28dce477894)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ManagedDatabasePostgresqlNodeStatesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3a6e4ddfd5e53444bf09e87427773d81f67b11732af145283f685298b5153e0)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ManagedDatabasePostgresqlNodeStatesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1048670c405a391dca4b3526ff9ca8191643277f5ddca90dbe29dae88ed7dde3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ab82061724a9896284d4068dffb73938dba936286a5eda3a45718e311572acf2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0609ce7acd96a0e4a4ca9993aa7cda81130c9d4270192d88dd48b92d3771833f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class ManagedDatabasePostgresqlNodeStatesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabasePostgresql.ManagedDatabasePostgresqlNodeStatesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6a36fa4f1406f761c1d3d6a9cffbeed270912d248d4042be2221a9780f008111)
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
    def internal_value(self) -> typing.Optional[ManagedDatabasePostgresqlNodeStates]:
        return typing.cast(typing.Optional[ManagedDatabasePostgresqlNodeStates], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabasePostgresqlNodeStates],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3da753e354ef908f815fa40182abc184639e86107112304380f0cdc2ba2755d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabasePostgresql.ManagedDatabasePostgresqlProperties",
    jsii_struct_bases=[],
    name_mapping={
        "admin_password": "adminPassword",
        "admin_username": "adminUsername",
        "automatic_utility_network_ip_filter": "automaticUtilityNetworkIpFilter",
        "autovacuum_analyze_scale_factor": "autovacuumAnalyzeScaleFactor",
        "autovacuum_analyze_threshold": "autovacuumAnalyzeThreshold",
        "autovacuum_freeze_max_age": "autovacuumFreezeMaxAge",
        "autovacuum_max_workers": "autovacuumMaxWorkers",
        "autovacuum_naptime": "autovacuumNaptime",
        "autovacuum_vacuum_cost_delay": "autovacuumVacuumCostDelay",
        "autovacuum_vacuum_cost_limit": "autovacuumVacuumCostLimit",
        "autovacuum_vacuum_scale_factor": "autovacuumVacuumScaleFactor",
        "autovacuum_vacuum_threshold": "autovacuumVacuumThreshold",
        "backup_hour": "backupHour",
        "backup_minute": "backupMinute",
        "bgwriter_delay": "bgwriterDelay",
        "bgwriter_flush_after": "bgwriterFlushAfter",
        "bgwriter_lru_maxpages": "bgwriterLruMaxpages",
        "bgwriter_lru_multiplier": "bgwriterLruMultiplier",
        "deadlock_timeout": "deadlockTimeout",
        "default_toast_compression": "defaultToastCompression",
        "idle_in_transaction_session_timeout": "idleInTransactionSessionTimeout",
        "ip_filter": "ipFilter",
        "jit": "jit",
        "log_autovacuum_min_duration": "logAutovacuumMinDuration",
        "log_error_verbosity": "logErrorVerbosity",
        "log_line_prefix": "logLinePrefix",
        "log_min_duration_statement": "logMinDurationStatement",
        "log_temp_files": "logTempFiles",
        "max_connections": "maxConnections",
        "max_files_per_process": "maxFilesPerProcess",
        "max_locks_per_transaction": "maxLocksPerTransaction",
        "max_logical_replication_workers": "maxLogicalReplicationWorkers",
        "max_parallel_workers": "maxParallelWorkers",
        "max_parallel_workers_per_gather": "maxParallelWorkersPerGather",
        "max_pred_locks_per_transaction": "maxPredLocksPerTransaction",
        "max_prepared_transactions": "maxPreparedTransactions",
        "max_replication_slots": "maxReplicationSlots",
        "max_slot_wal_keep_size": "maxSlotWalKeepSize",
        "max_stack_depth": "maxStackDepth",
        "max_standby_archive_delay": "maxStandbyArchiveDelay",
        "max_standby_streaming_delay": "maxStandbyStreamingDelay",
        "max_sync_workers_per_subscription": "maxSyncWorkersPerSubscription",
        "max_wal_senders": "maxWalSenders",
        "max_worker_processes": "maxWorkerProcesses",
        "migration": "migration",
        "password_encryption": "passwordEncryption",
        "pgaudit": "pgaudit",
        "pgbouncer": "pgbouncer",
        "pglookout": "pglookout",
        "pg_partman_bgw_interval": "pgPartmanBgwInterval",
        "pg_partman_bgw_role": "pgPartmanBgwRole",
        "pg_stat_monitor_enable": "pgStatMonitorEnable",
        "pg_stat_monitor_pgsm_enable_query_plan": "pgStatMonitorPgsmEnableQueryPlan",
        "pg_stat_monitor_pgsm_max_buckets": "pgStatMonitorPgsmMaxBuckets",
        "pg_stat_statements_track": "pgStatStatementsTrack",
        "public_access": "publicAccess",
        "service_log": "serviceLog",
        "shared_buffers_percentage": "sharedBuffersPercentage",
        "synchronous_replication": "synchronousReplication",
        "temp_file_limit": "tempFileLimit",
        "timescaledb": "timescaledb",
        "timezone": "timezone",
        "track_activity_query_size": "trackActivityQuerySize",
        "track_commit_timestamp": "trackCommitTimestamp",
        "track_functions": "trackFunctions",
        "track_io_timing": "trackIoTiming",
        "variant": "variant",
        "version": "version",
        "wal_sender_timeout": "walSenderTimeout",
        "wal_writer_delay": "walWriterDelay",
        "work_mem": "workMem",
    },
)
class ManagedDatabasePostgresqlProperties:
    def __init__(
        self,
        *,
        admin_password: typing.Optional[builtins.str] = None,
        admin_username: typing.Optional[builtins.str] = None,
        automatic_utility_network_ip_filter: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        autovacuum_analyze_scale_factor: typing.Optional[jsii.Number] = None,
        autovacuum_analyze_threshold: typing.Optional[jsii.Number] = None,
        autovacuum_freeze_max_age: typing.Optional[jsii.Number] = None,
        autovacuum_max_workers: typing.Optional[jsii.Number] = None,
        autovacuum_naptime: typing.Optional[jsii.Number] = None,
        autovacuum_vacuum_cost_delay: typing.Optional[jsii.Number] = None,
        autovacuum_vacuum_cost_limit: typing.Optional[jsii.Number] = None,
        autovacuum_vacuum_scale_factor: typing.Optional[jsii.Number] = None,
        autovacuum_vacuum_threshold: typing.Optional[jsii.Number] = None,
        backup_hour: typing.Optional[jsii.Number] = None,
        backup_minute: typing.Optional[jsii.Number] = None,
        bgwriter_delay: typing.Optional[jsii.Number] = None,
        bgwriter_flush_after: typing.Optional[jsii.Number] = None,
        bgwriter_lru_maxpages: typing.Optional[jsii.Number] = None,
        bgwriter_lru_multiplier: typing.Optional[jsii.Number] = None,
        deadlock_timeout: typing.Optional[jsii.Number] = None,
        default_toast_compression: typing.Optional[builtins.str] = None,
        idle_in_transaction_session_timeout: typing.Optional[jsii.Number] = None,
        ip_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
        jit: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        log_autovacuum_min_duration: typing.Optional[jsii.Number] = None,
        log_error_verbosity: typing.Optional[builtins.str] = None,
        log_line_prefix: typing.Optional[builtins.str] = None,
        log_min_duration_statement: typing.Optional[jsii.Number] = None,
        log_temp_files: typing.Optional[jsii.Number] = None,
        max_connections: typing.Optional[jsii.Number] = None,
        max_files_per_process: typing.Optional[jsii.Number] = None,
        max_locks_per_transaction: typing.Optional[jsii.Number] = None,
        max_logical_replication_workers: typing.Optional[jsii.Number] = None,
        max_parallel_workers: typing.Optional[jsii.Number] = None,
        max_parallel_workers_per_gather: typing.Optional[jsii.Number] = None,
        max_pred_locks_per_transaction: typing.Optional[jsii.Number] = None,
        max_prepared_transactions: typing.Optional[jsii.Number] = None,
        max_replication_slots: typing.Optional[jsii.Number] = None,
        max_slot_wal_keep_size: typing.Optional[jsii.Number] = None,
        max_stack_depth: typing.Optional[jsii.Number] = None,
        max_standby_archive_delay: typing.Optional[jsii.Number] = None,
        max_standby_streaming_delay: typing.Optional[jsii.Number] = None,
        max_sync_workers_per_subscription: typing.Optional[jsii.Number] = None,
        max_wal_senders: typing.Optional[jsii.Number] = None,
        max_worker_processes: typing.Optional[jsii.Number] = None,
        migration: typing.Optional[typing.Union["ManagedDatabasePostgresqlPropertiesMigration", typing.Dict[builtins.str, typing.Any]]] = None,
        password_encryption: typing.Optional[builtins.str] = None,
        pgaudit: typing.Optional[typing.Union["ManagedDatabasePostgresqlPropertiesPgaudit", typing.Dict[builtins.str, typing.Any]]] = None,
        pgbouncer: typing.Optional[typing.Union["ManagedDatabasePostgresqlPropertiesPgbouncer", typing.Dict[builtins.str, typing.Any]]] = None,
        pglookout: typing.Optional[typing.Union["ManagedDatabasePostgresqlPropertiesPglookout", typing.Dict[builtins.str, typing.Any]]] = None,
        pg_partman_bgw_interval: typing.Optional[jsii.Number] = None,
        pg_partman_bgw_role: typing.Optional[builtins.str] = None,
        pg_stat_monitor_enable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        pg_stat_monitor_pgsm_enable_query_plan: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        pg_stat_monitor_pgsm_max_buckets: typing.Optional[jsii.Number] = None,
        pg_stat_statements_track: typing.Optional[builtins.str] = None,
        public_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        service_log: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        shared_buffers_percentage: typing.Optional[jsii.Number] = None,
        synchronous_replication: typing.Optional[builtins.str] = None,
        temp_file_limit: typing.Optional[jsii.Number] = None,
        timescaledb: typing.Optional[typing.Union["ManagedDatabasePostgresqlPropertiesTimescaledb", typing.Dict[builtins.str, typing.Any]]] = None,
        timezone: typing.Optional[builtins.str] = None,
        track_activity_query_size: typing.Optional[jsii.Number] = None,
        track_commit_timestamp: typing.Optional[builtins.str] = None,
        track_functions: typing.Optional[builtins.str] = None,
        track_io_timing: typing.Optional[builtins.str] = None,
        variant: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
        wal_sender_timeout: typing.Optional[jsii.Number] = None,
        wal_writer_delay: typing.Optional[jsii.Number] = None,
        work_mem: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param admin_password: Custom password for admin user. Defaults to random string. This must be set only when a new service is being created. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#admin_password ManagedDatabasePostgresql#admin_password}
        :param admin_username: Custom username for admin user. This must be set only when a new service is being created. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#admin_username ManagedDatabasePostgresql#admin_username}
        :param automatic_utility_network_ip_filter: Automatic utility network IP Filter. Automatically allow connections from servers in the utility network within the same zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#automatic_utility_network_ip_filter ManagedDatabasePostgresql#automatic_utility_network_ip_filter}
        :param autovacuum_analyze_scale_factor: Specifies a fraction of the table size to add to autovacuum_analyze_threshold when deciding whether to trigger an ANALYZE (e.g. ``0.2`` for 20% of the table size). The default is ``0.2``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autovacuum_analyze_scale_factor ManagedDatabasePostgresql#autovacuum_analyze_scale_factor}
        :param autovacuum_analyze_threshold: Specifies the minimum number of inserted, updated or deleted tuples needed to trigger an ANALYZE in any one table. The default is ``50``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autovacuum_analyze_threshold ManagedDatabasePostgresql#autovacuum_analyze_threshold}
        :param autovacuum_freeze_max_age: Specifies the maximum age (in transactions) that a table's pg_class.relfrozenxid field can attain before a VACUUM operation is forced to prevent transaction ID wraparound within the table. The system launches autovacuum processes to prevent wraparound even when autovacuum is otherwise disabled. Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autovacuum_freeze_max_age ManagedDatabasePostgresql#autovacuum_freeze_max_age}
        :param autovacuum_max_workers: Specifies the maximum number of autovacuum processes (other than the autovacuum launcher) that may be running at any one time. The default is ``3``. Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autovacuum_max_workers ManagedDatabasePostgresql#autovacuum_max_workers}
        :param autovacuum_naptime: Specifies the minimum delay between autovacuum runs on any given database. The delay is measured in seconds. The default is ``60``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autovacuum_naptime ManagedDatabasePostgresql#autovacuum_naptime}
        :param autovacuum_vacuum_cost_delay: Specifies the cost delay value that will be used in automatic VACUUM operations. If ``-1`` is specified, the regular vacuum_cost_delay value will be used. The default is ``2`` (upstream default). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autovacuum_vacuum_cost_delay ManagedDatabasePostgresql#autovacuum_vacuum_cost_delay}
        :param autovacuum_vacuum_cost_limit: Specifies the cost limit value that will be used in automatic VACUUM operations. If ``-1`` is specified, the regular vacuum_cost_limit value will be used. The default is ``-1`` (upstream default). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autovacuum_vacuum_cost_limit ManagedDatabasePostgresql#autovacuum_vacuum_cost_limit}
        :param autovacuum_vacuum_scale_factor: Specifies a fraction of the table size to add to autovacuum_vacuum_threshold when deciding whether to trigger a VACUUM (e.g. ``0.2`` for 20% of the table size). The default is ``0.2``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autovacuum_vacuum_scale_factor ManagedDatabasePostgresql#autovacuum_vacuum_scale_factor}
        :param autovacuum_vacuum_threshold: Specifies the minimum number of updated or deleted tuples needed to trigger a VACUUM in any one table. The default is ``50``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autovacuum_vacuum_threshold ManagedDatabasePostgresql#autovacuum_vacuum_threshold}
        :param backup_hour: The hour of day (in UTC) when backup for the service is started. New backup is only started if previous backup has already completed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#backup_hour ManagedDatabasePostgresql#backup_hour}
        :param backup_minute: The minute of an hour when backup for the service is started. New backup is only started if previous backup has already completed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#backup_minute ManagedDatabasePostgresql#backup_minute}
        :param bgwriter_delay: Specifies the delay between activity rounds for the background writer in milliseconds. The default is ``200``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#bgwriter_delay ManagedDatabasePostgresql#bgwriter_delay}
        :param bgwriter_flush_after: Whenever more than bgwriter_flush_after bytes have been written by the background writer, attempt to force the OS to issue these writes to the underlying storage. Specified in kilobytes. Setting of 0 disables forced writeback. The default is ``512``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#bgwriter_flush_after ManagedDatabasePostgresql#bgwriter_flush_after}
        :param bgwriter_lru_maxpages: In each round, no more than this many buffers will be written by the background writer. Setting this to zero disables background writing. The default is ``100``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#bgwriter_lru_maxpages ManagedDatabasePostgresql#bgwriter_lru_maxpages}
        :param bgwriter_lru_multiplier: The average recent need for new buffers is multiplied by bgwriter_lru_multiplier to arrive at an estimate of the number that will be needed during the next round, (up to bgwriter_lru_maxpages). 1.0 represents a “just in time” policy of writing exactly the number of buffers predicted to be needed. Larger values provide some cushion against spikes in demand, while smaller values intentionally leave writes to be done by server processes. The default is ``2.0``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#bgwriter_lru_multiplier ManagedDatabasePostgresql#bgwriter_lru_multiplier}
        :param deadlock_timeout: This is the amount of time, in milliseconds, to wait on a lock before checking to see if there is a deadlock condition. The default is ``1000`` (upstream default). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#deadlock_timeout ManagedDatabasePostgresql#deadlock_timeout}
        :param default_toast_compression: Specifies the default TOAST compression method for values of compressible columns. The default is ``lz4``. Only available for PostgreSQL 14+. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#default_toast_compression ManagedDatabasePostgresql#default_toast_compression}
        :param idle_in_transaction_session_timeout: Time out sessions with open transactions after this number of milliseconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#idle_in_transaction_session_timeout ManagedDatabasePostgresql#idle_in_transaction_session_timeout}
        :param ip_filter: IP filter. Allow incoming connections from CIDR address block, e.g. '10.20.0.0/16'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#ip_filter ManagedDatabasePostgresql#ip_filter}
        :param jit: Controls system-wide use of Just-in-Time Compilation (JIT). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#jit ManagedDatabasePostgresql#jit}
        :param log_autovacuum_min_duration: Causes each action executed by autovacuum to be logged if it ran for at least the specified number of milliseconds. Setting this to zero logs all autovacuum actions. Minus-one disables logging autovacuum actions. The default is ``1000``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_autovacuum_min_duration ManagedDatabasePostgresql#log_autovacuum_min_duration}
        :param log_error_verbosity: Controls the amount of detail written in the server log for each message that is logged. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_error_verbosity ManagedDatabasePostgresql#log_error_verbosity}
        :param log_line_prefix: Choose from one of the available log formats. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_line_prefix ManagedDatabasePostgresql#log_line_prefix}
        :param log_min_duration_statement: Log statements that take more than this number of milliseconds to run, -1 disables. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_min_duration_statement ManagedDatabasePostgresql#log_min_duration_statement}
        :param log_temp_files: Log statements for each temporary file created larger than this number of kilobytes, -1 disables. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_temp_files ManagedDatabasePostgresql#log_temp_files}
        :param max_connections: PostgreSQL maximum number of concurrent connections to the database server. Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_connections ManagedDatabasePostgresql#max_connections}
        :param max_files_per_process: PostgreSQL maximum number of files that can be open per process. The default is ``1000`` (upstream default). Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_files_per_process ManagedDatabasePostgresql#max_files_per_process}
        :param max_locks_per_transaction: PostgreSQL maximum locks per transaction. Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_locks_per_transaction ManagedDatabasePostgresql#max_locks_per_transaction}
        :param max_logical_replication_workers: PostgreSQL maximum logical replication workers (taken from the pool of max_parallel_workers). The default is ``4`` (upstream default). Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_logical_replication_workers ManagedDatabasePostgresql#max_logical_replication_workers}
        :param max_parallel_workers: Sets the maximum number of workers that the system can support for parallel queries. The default is ``8`` (upstream default). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_parallel_workers ManagedDatabasePostgresql#max_parallel_workers}
        :param max_parallel_workers_per_gather: Sets the maximum number of workers that can be started by a single Gather or Gather Merge node. The default is ``2`` (upstream default). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_parallel_workers_per_gather ManagedDatabasePostgresql#max_parallel_workers_per_gather}
        :param max_pred_locks_per_transaction: PostgreSQL maximum predicate locks per transaction. The default is ``64`` (upstream default). Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_pred_locks_per_transaction ManagedDatabasePostgresql#max_pred_locks_per_transaction}
        :param max_prepared_transactions: PostgreSQL maximum prepared transactions. The default is ``0``. Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_prepared_transactions ManagedDatabasePostgresql#max_prepared_transactions}
        :param max_replication_slots: PostgreSQL maximum replication slots. The default is ``20``. Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_replication_slots ManagedDatabasePostgresql#max_replication_slots}
        :param max_slot_wal_keep_size: PostgreSQL maximum WAL size (MB) reserved for replication slots. If ``-1`` is specified, replication slots may retain an unlimited amount of WAL files. The default is ``-1`` (upstream default). wal_keep_size minimum WAL size setting takes precedence over this. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_slot_wal_keep_size ManagedDatabasePostgresql#max_slot_wal_keep_size}
        :param max_stack_depth: Maximum depth of the stack in bytes. The default is ``2097152`` (upstream default). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_stack_depth ManagedDatabasePostgresql#max_stack_depth}
        :param max_standby_archive_delay: Max standby archive delay in milliseconds. The default is ``30000`` (upstream default). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_standby_archive_delay ManagedDatabasePostgresql#max_standby_archive_delay}
        :param max_standby_streaming_delay: Max standby streaming delay in milliseconds. The default is ``30000`` (upstream default). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_standby_streaming_delay ManagedDatabasePostgresql#max_standby_streaming_delay}
        :param max_sync_workers_per_subscription: Maximum number of synchronization workers per subscription. The default is ``2``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_sync_workers_per_subscription ManagedDatabasePostgresql#max_sync_workers_per_subscription}
        :param max_wal_senders: PostgreSQL maximum WAL senders. The default is ``20``. Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_wal_senders ManagedDatabasePostgresql#max_wal_senders}
        :param max_worker_processes: Sets the maximum number of background processes that the system can support. The default is ``8``. Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_worker_processes ManagedDatabasePostgresql#max_worker_processes}
        :param migration: migration block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#migration ManagedDatabasePostgresql#migration}
        :param password_encryption: Chooses the algorithm for encrypting passwords. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#password_encryption ManagedDatabasePostgresql#password_encryption}
        :param pgaudit: pgaudit block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#pgaudit ManagedDatabasePostgresql#pgaudit}
        :param pgbouncer: pgbouncer block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#pgbouncer ManagedDatabasePostgresql#pgbouncer}
        :param pglookout: pglookout block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#pglookout ManagedDatabasePostgresql#pglookout}
        :param pg_partman_bgw_interval: Sets the time interval in seconds to run pg_partman's scheduled tasks. The default is ``3600``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#pg_partman_bgw_interval ManagedDatabasePostgresql#pg_partman_bgw_interval}
        :param pg_partman_bgw_role: Controls which role to use for pg_partman's scheduled background tasks. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#pg_partman_bgw_role ManagedDatabasePostgresql#pg_partman_bgw_role}
        :param pg_stat_monitor_enable: Enable pg_stat_monitor extension if available for the current cluster. Enable the pg_stat_monitor extension. Changing this parameter causes a service restart. When this extension is enabled, pg_stat_statements results for utility commands are unreliable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#pg_stat_monitor_enable ManagedDatabasePostgresql#pg_stat_monitor_enable}
        :param pg_stat_monitor_pgsm_enable_query_plan: Enables or disables query plan monitoring. Changing this parameter causes a service restart. Only available for PostgreSQL 13+. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#pg_stat_monitor_pgsm_enable_query_plan ManagedDatabasePostgresql#pg_stat_monitor_pgsm_enable_query_plan}
        :param pg_stat_monitor_pgsm_max_buckets: Sets the maximum number of buckets. Changing this parameter causes a service restart. Only available for PostgreSQL 13+. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#pg_stat_monitor_pgsm_max_buckets ManagedDatabasePostgresql#pg_stat_monitor_pgsm_max_buckets}
        :param pg_stat_statements_track: Controls which statements are counted. Specify top to track top-level statements (those issued directly by clients), all to also track nested statements (such as statements invoked within functions), or none to disable statement statistics collection. The default is ``top``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#pg_stat_statements_track ManagedDatabasePostgresql#pg_stat_statements_track}
        :param public_access: Public Access. Allow access to the service from the public Internet. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#public_access ManagedDatabasePostgresql#public_access}
        :param service_log: Service logging. Store logs for the service so that they are available in the HTTP API and console. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#service_log ManagedDatabasePostgresql#service_log}
        :param shared_buffers_percentage: Percentage of total RAM that the database server uses for shared memory buffers. Valid range is 20-60 (float), which corresponds to 20% - 60%. This setting adjusts the shared_buffers configuration value. Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#shared_buffers_percentage ManagedDatabasePostgresql#shared_buffers_percentage}
        :param synchronous_replication: Synchronous replication type. Note that the service plan also needs to support synchronous replication. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#synchronous_replication ManagedDatabasePostgresql#synchronous_replication}
        :param temp_file_limit: PostgreSQL temporary file limit in KiB, -1 for unlimited. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#temp_file_limit ManagedDatabasePostgresql#temp_file_limit}
        :param timescaledb: timescaledb block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#timescaledb ManagedDatabasePostgresql#timescaledb}
        :param timezone: PostgreSQL service timezone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#timezone ManagedDatabasePostgresql#timezone}
        :param track_activity_query_size: Specifies the number of bytes reserved to track the currently executing command for each active session. Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#track_activity_query_size ManagedDatabasePostgresql#track_activity_query_size}
        :param track_commit_timestamp: Record commit time of transactions. Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#track_commit_timestamp ManagedDatabasePostgresql#track_commit_timestamp}
        :param track_functions: Enables tracking of function call counts and time used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#track_functions ManagedDatabasePostgresql#track_functions}
        :param track_io_timing: Enables timing of database I/O calls. The default is ``off``. When on, it will repeatedly query the operating system for the current time, which may cause significant overhead on some platforms. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#track_io_timing ManagedDatabasePostgresql#track_io_timing}
        :param variant: Variant of the PostgreSQL service, may affect the features that are exposed by default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#variant ManagedDatabasePostgresql#variant}
        :param version: PostgreSQL major version. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#version ManagedDatabasePostgresql#version}
        :param wal_sender_timeout: Terminate replication connections that are inactive for longer than this amount of time, in milliseconds. Setting this value to zero disables the timeout. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#wal_sender_timeout ManagedDatabasePostgresql#wal_sender_timeout}
        :param wal_writer_delay: WAL flush interval in milliseconds. The default is ``200``. Setting this parameter to a lower value may negatively impact performance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#wal_writer_delay ManagedDatabasePostgresql#wal_writer_delay}
        :param work_mem: Sets the maximum amount of memory to be used by a query operation (such as a sort or hash table) before writing to temporary disk files, in MB. The default is 1MB + 0.075% of total RAM (up to 32MB). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#work_mem ManagedDatabasePostgresql#work_mem}
        '''
        if isinstance(migration, dict):
            migration = ManagedDatabasePostgresqlPropertiesMigration(**migration)
        if isinstance(pgaudit, dict):
            pgaudit = ManagedDatabasePostgresqlPropertiesPgaudit(**pgaudit)
        if isinstance(pgbouncer, dict):
            pgbouncer = ManagedDatabasePostgresqlPropertiesPgbouncer(**pgbouncer)
        if isinstance(pglookout, dict):
            pglookout = ManagedDatabasePostgresqlPropertiesPglookout(**pglookout)
        if isinstance(timescaledb, dict):
            timescaledb = ManagedDatabasePostgresqlPropertiesTimescaledb(**timescaledb)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6910d3220979fbcd86275a19c629678468755096ca15771873a4cee0a9a244d)
            check_type(argname="argument admin_password", value=admin_password, expected_type=type_hints["admin_password"])
            check_type(argname="argument admin_username", value=admin_username, expected_type=type_hints["admin_username"])
            check_type(argname="argument automatic_utility_network_ip_filter", value=automatic_utility_network_ip_filter, expected_type=type_hints["automatic_utility_network_ip_filter"])
            check_type(argname="argument autovacuum_analyze_scale_factor", value=autovacuum_analyze_scale_factor, expected_type=type_hints["autovacuum_analyze_scale_factor"])
            check_type(argname="argument autovacuum_analyze_threshold", value=autovacuum_analyze_threshold, expected_type=type_hints["autovacuum_analyze_threshold"])
            check_type(argname="argument autovacuum_freeze_max_age", value=autovacuum_freeze_max_age, expected_type=type_hints["autovacuum_freeze_max_age"])
            check_type(argname="argument autovacuum_max_workers", value=autovacuum_max_workers, expected_type=type_hints["autovacuum_max_workers"])
            check_type(argname="argument autovacuum_naptime", value=autovacuum_naptime, expected_type=type_hints["autovacuum_naptime"])
            check_type(argname="argument autovacuum_vacuum_cost_delay", value=autovacuum_vacuum_cost_delay, expected_type=type_hints["autovacuum_vacuum_cost_delay"])
            check_type(argname="argument autovacuum_vacuum_cost_limit", value=autovacuum_vacuum_cost_limit, expected_type=type_hints["autovacuum_vacuum_cost_limit"])
            check_type(argname="argument autovacuum_vacuum_scale_factor", value=autovacuum_vacuum_scale_factor, expected_type=type_hints["autovacuum_vacuum_scale_factor"])
            check_type(argname="argument autovacuum_vacuum_threshold", value=autovacuum_vacuum_threshold, expected_type=type_hints["autovacuum_vacuum_threshold"])
            check_type(argname="argument backup_hour", value=backup_hour, expected_type=type_hints["backup_hour"])
            check_type(argname="argument backup_minute", value=backup_minute, expected_type=type_hints["backup_minute"])
            check_type(argname="argument bgwriter_delay", value=bgwriter_delay, expected_type=type_hints["bgwriter_delay"])
            check_type(argname="argument bgwriter_flush_after", value=bgwriter_flush_after, expected_type=type_hints["bgwriter_flush_after"])
            check_type(argname="argument bgwriter_lru_maxpages", value=bgwriter_lru_maxpages, expected_type=type_hints["bgwriter_lru_maxpages"])
            check_type(argname="argument bgwriter_lru_multiplier", value=bgwriter_lru_multiplier, expected_type=type_hints["bgwriter_lru_multiplier"])
            check_type(argname="argument deadlock_timeout", value=deadlock_timeout, expected_type=type_hints["deadlock_timeout"])
            check_type(argname="argument default_toast_compression", value=default_toast_compression, expected_type=type_hints["default_toast_compression"])
            check_type(argname="argument idle_in_transaction_session_timeout", value=idle_in_transaction_session_timeout, expected_type=type_hints["idle_in_transaction_session_timeout"])
            check_type(argname="argument ip_filter", value=ip_filter, expected_type=type_hints["ip_filter"])
            check_type(argname="argument jit", value=jit, expected_type=type_hints["jit"])
            check_type(argname="argument log_autovacuum_min_duration", value=log_autovacuum_min_duration, expected_type=type_hints["log_autovacuum_min_duration"])
            check_type(argname="argument log_error_verbosity", value=log_error_verbosity, expected_type=type_hints["log_error_verbosity"])
            check_type(argname="argument log_line_prefix", value=log_line_prefix, expected_type=type_hints["log_line_prefix"])
            check_type(argname="argument log_min_duration_statement", value=log_min_duration_statement, expected_type=type_hints["log_min_duration_statement"])
            check_type(argname="argument log_temp_files", value=log_temp_files, expected_type=type_hints["log_temp_files"])
            check_type(argname="argument max_connections", value=max_connections, expected_type=type_hints["max_connections"])
            check_type(argname="argument max_files_per_process", value=max_files_per_process, expected_type=type_hints["max_files_per_process"])
            check_type(argname="argument max_locks_per_transaction", value=max_locks_per_transaction, expected_type=type_hints["max_locks_per_transaction"])
            check_type(argname="argument max_logical_replication_workers", value=max_logical_replication_workers, expected_type=type_hints["max_logical_replication_workers"])
            check_type(argname="argument max_parallel_workers", value=max_parallel_workers, expected_type=type_hints["max_parallel_workers"])
            check_type(argname="argument max_parallel_workers_per_gather", value=max_parallel_workers_per_gather, expected_type=type_hints["max_parallel_workers_per_gather"])
            check_type(argname="argument max_pred_locks_per_transaction", value=max_pred_locks_per_transaction, expected_type=type_hints["max_pred_locks_per_transaction"])
            check_type(argname="argument max_prepared_transactions", value=max_prepared_transactions, expected_type=type_hints["max_prepared_transactions"])
            check_type(argname="argument max_replication_slots", value=max_replication_slots, expected_type=type_hints["max_replication_slots"])
            check_type(argname="argument max_slot_wal_keep_size", value=max_slot_wal_keep_size, expected_type=type_hints["max_slot_wal_keep_size"])
            check_type(argname="argument max_stack_depth", value=max_stack_depth, expected_type=type_hints["max_stack_depth"])
            check_type(argname="argument max_standby_archive_delay", value=max_standby_archive_delay, expected_type=type_hints["max_standby_archive_delay"])
            check_type(argname="argument max_standby_streaming_delay", value=max_standby_streaming_delay, expected_type=type_hints["max_standby_streaming_delay"])
            check_type(argname="argument max_sync_workers_per_subscription", value=max_sync_workers_per_subscription, expected_type=type_hints["max_sync_workers_per_subscription"])
            check_type(argname="argument max_wal_senders", value=max_wal_senders, expected_type=type_hints["max_wal_senders"])
            check_type(argname="argument max_worker_processes", value=max_worker_processes, expected_type=type_hints["max_worker_processes"])
            check_type(argname="argument migration", value=migration, expected_type=type_hints["migration"])
            check_type(argname="argument password_encryption", value=password_encryption, expected_type=type_hints["password_encryption"])
            check_type(argname="argument pgaudit", value=pgaudit, expected_type=type_hints["pgaudit"])
            check_type(argname="argument pgbouncer", value=pgbouncer, expected_type=type_hints["pgbouncer"])
            check_type(argname="argument pglookout", value=pglookout, expected_type=type_hints["pglookout"])
            check_type(argname="argument pg_partman_bgw_interval", value=pg_partman_bgw_interval, expected_type=type_hints["pg_partman_bgw_interval"])
            check_type(argname="argument pg_partman_bgw_role", value=pg_partman_bgw_role, expected_type=type_hints["pg_partman_bgw_role"])
            check_type(argname="argument pg_stat_monitor_enable", value=pg_stat_monitor_enable, expected_type=type_hints["pg_stat_monitor_enable"])
            check_type(argname="argument pg_stat_monitor_pgsm_enable_query_plan", value=pg_stat_monitor_pgsm_enable_query_plan, expected_type=type_hints["pg_stat_monitor_pgsm_enable_query_plan"])
            check_type(argname="argument pg_stat_monitor_pgsm_max_buckets", value=pg_stat_monitor_pgsm_max_buckets, expected_type=type_hints["pg_stat_monitor_pgsm_max_buckets"])
            check_type(argname="argument pg_stat_statements_track", value=pg_stat_statements_track, expected_type=type_hints["pg_stat_statements_track"])
            check_type(argname="argument public_access", value=public_access, expected_type=type_hints["public_access"])
            check_type(argname="argument service_log", value=service_log, expected_type=type_hints["service_log"])
            check_type(argname="argument shared_buffers_percentage", value=shared_buffers_percentage, expected_type=type_hints["shared_buffers_percentage"])
            check_type(argname="argument synchronous_replication", value=synchronous_replication, expected_type=type_hints["synchronous_replication"])
            check_type(argname="argument temp_file_limit", value=temp_file_limit, expected_type=type_hints["temp_file_limit"])
            check_type(argname="argument timescaledb", value=timescaledb, expected_type=type_hints["timescaledb"])
            check_type(argname="argument timezone", value=timezone, expected_type=type_hints["timezone"])
            check_type(argname="argument track_activity_query_size", value=track_activity_query_size, expected_type=type_hints["track_activity_query_size"])
            check_type(argname="argument track_commit_timestamp", value=track_commit_timestamp, expected_type=type_hints["track_commit_timestamp"])
            check_type(argname="argument track_functions", value=track_functions, expected_type=type_hints["track_functions"])
            check_type(argname="argument track_io_timing", value=track_io_timing, expected_type=type_hints["track_io_timing"])
            check_type(argname="argument variant", value=variant, expected_type=type_hints["variant"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            check_type(argname="argument wal_sender_timeout", value=wal_sender_timeout, expected_type=type_hints["wal_sender_timeout"])
            check_type(argname="argument wal_writer_delay", value=wal_writer_delay, expected_type=type_hints["wal_writer_delay"])
            check_type(argname="argument work_mem", value=work_mem, expected_type=type_hints["work_mem"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if admin_password is not None:
            self._values["admin_password"] = admin_password
        if admin_username is not None:
            self._values["admin_username"] = admin_username
        if automatic_utility_network_ip_filter is not None:
            self._values["automatic_utility_network_ip_filter"] = automatic_utility_network_ip_filter
        if autovacuum_analyze_scale_factor is not None:
            self._values["autovacuum_analyze_scale_factor"] = autovacuum_analyze_scale_factor
        if autovacuum_analyze_threshold is not None:
            self._values["autovacuum_analyze_threshold"] = autovacuum_analyze_threshold
        if autovacuum_freeze_max_age is not None:
            self._values["autovacuum_freeze_max_age"] = autovacuum_freeze_max_age
        if autovacuum_max_workers is not None:
            self._values["autovacuum_max_workers"] = autovacuum_max_workers
        if autovacuum_naptime is not None:
            self._values["autovacuum_naptime"] = autovacuum_naptime
        if autovacuum_vacuum_cost_delay is not None:
            self._values["autovacuum_vacuum_cost_delay"] = autovacuum_vacuum_cost_delay
        if autovacuum_vacuum_cost_limit is not None:
            self._values["autovacuum_vacuum_cost_limit"] = autovacuum_vacuum_cost_limit
        if autovacuum_vacuum_scale_factor is not None:
            self._values["autovacuum_vacuum_scale_factor"] = autovacuum_vacuum_scale_factor
        if autovacuum_vacuum_threshold is not None:
            self._values["autovacuum_vacuum_threshold"] = autovacuum_vacuum_threshold
        if backup_hour is not None:
            self._values["backup_hour"] = backup_hour
        if backup_minute is not None:
            self._values["backup_minute"] = backup_minute
        if bgwriter_delay is not None:
            self._values["bgwriter_delay"] = bgwriter_delay
        if bgwriter_flush_after is not None:
            self._values["bgwriter_flush_after"] = bgwriter_flush_after
        if bgwriter_lru_maxpages is not None:
            self._values["bgwriter_lru_maxpages"] = bgwriter_lru_maxpages
        if bgwriter_lru_multiplier is not None:
            self._values["bgwriter_lru_multiplier"] = bgwriter_lru_multiplier
        if deadlock_timeout is not None:
            self._values["deadlock_timeout"] = deadlock_timeout
        if default_toast_compression is not None:
            self._values["default_toast_compression"] = default_toast_compression
        if idle_in_transaction_session_timeout is not None:
            self._values["idle_in_transaction_session_timeout"] = idle_in_transaction_session_timeout
        if ip_filter is not None:
            self._values["ip_filter"] = ip_filter
        if jit is not None:
            self._values["jit"] = jit
        if log_autovacuum_min_duration is not None:
            self._values["log_autovacuum_min_duration"] = log_autovacuum_min_duration
        if log_error_verbosity is not None:
            self._values["log_error_verbosity"] = log_error_verbosity
        if log_line_prefix is not None:
            self._values["log_line_prefix"] = log_line_prefix
        if log_min_duration_statement is not None:
            self._values["log_min_duration_statement"] = log_min_duration_statement
        if log_temp_files is not None:
            self._values["log_temp_files"] = log_temp_files
        if max_connections is not None:
            self._values["max_connections"] = max_connections
        if max_files_per_process is not None:
            self._values["max_files_per_process"] = max_files_per_process
        if max_locks_per_transaction is not None:
            self._values["max_locks_per_transaction"] = max_locks_per_transaction
        if max_logical_replication_workers is not None:
            self._values["max_logical_replication_workers"] = max_logical_replication_workers
        if max_parallel_workers is not None:
            self._values["max_parallel_workers"] = max_parallel_workers
        if max_parallel_workers_per_gather is not None:
            self._values["max_parallel_workers_per_gather"] = max_parallel_workers_per_gather
        if max_pred_locks_per_transaction is not None:
            self._values["max_pred_locks_per_transaction"] = max_pred_locks_per_transaction
        if max_prepared_transactions is not None:
            self._values["max_prepared_transactions"] = max_prepared_transactions
        if max_replication_slots is not None:
            self._values["max_replication_slots"] = max_replication_slots
        if max_slot_wal_keep_size is not None:
            self._values["max_slot_wal_keep_size"] = max_slot_wal_keep_size
        if max_stack_depth is not None:
            self._values["max_stack_depth"] = max_stack_depth
        if max_standby_archive_delay is not None:
            self._values["max_standby_archive_delay"] = max_standby_archive_delay
        if max_standby_streaming_delay is not None:
            self._values["max_standby_streaming_delay"] = max_standby_streaming_delay
        if max_sync_workers_per_subscription is not None:
            self._values["max_sync_workers_per_subscription"] = max_sync_workers_per_subscription
        if max_wal_senders is not None:
            self._values["max_wal_senders"] = max_wal_senders
        if max_worker_processes is not None:
            self._values["max_worker_processes"] = max_worker_processes
        if migration is not None:
            self._values["migration"] = migration
        if password_encryption is not None:
            self._values["password_encryption"] = password_encryption
        if pgaudit is not None:
            self._values["pgaudit"] = pgaudit
        if pgbouncer is not None:
            self._values["pgbouncer"] = pgbouncer
        if pglookout is not None:
            self._values["pglookout"] = pglookout
        if pg_partman_bgw_interval is not None:
            self._values["pg_partman_bgw_interval"] = pg_partman_bgw_interval
        if pg_partman_bgw_role is not None:
            self._values["pg_partman_bgw_role"] = pg_partman_bgw_role
        if pg_stat_monitor_enable is not None:
            self._values["pg_stat_monitor_enable"] = pg_stat_monitor_enable
        if pg_stat_monitor_pgsm_enable_query_plan is not None:
            self._values["pg_stat_monitor_pgsm_enable_query_plan"] = pg_stat_monitor_pgsm_enable_query_plan
        if pg_stat_monitor_pgsm_max_buckets is not None:
            self._values["pg_stat_monitor_pgsm_max_buckets"] = pg_stat_monitor_pgsm_max_buckets
        if pg_stat_statements_track is not None:
            self._values["pg_stat_statements_track"] = pg_stat_statements_track
        if public_access is not None:
            self._values["public_access"] = public_access
        if service_log is not None:
            self._values["service_log"] = service_log
        if shared_buffers_percentage is not None:
            self._values["shared_buffers_percentage"] = shared_buffers_percentage
        if synchronous_replication is not None:
            self._values["synchronous_replication"] = synchronous_replication
        if temp_file_limit is not None:
            self._values["temp_file_limit"] = temp_file_limit
        if timescaledb is not None:
            self._values["timescaledb"] = timescaledb
        if timezone is not None:
            self._values["timezone"] = timezone
        if track_activity_query_size is not None:
            self._values["track_activity_query_size"] = track_activity_query_size
        if track_commit_timestamp is not None:
            self._values["track_commit_timestamp"] = track_commit_timestamp
        if track_functions is not None:
            self._values["track_functions"] = track_functions
        if track_io_timing is not None:
            self._values["track_io_timing"] = track_io_timing
        if variant is not None:
            self._values["variant"] = variant
        if version is not None:
            self._values["version"] = version
        if wal_sender_timeout is not None:
            self._values["wal_sender_timeout"] = wal_sender_timeout
        if wal_writer_delay is not None:
            self._values["wal_writer_delay"] = wal_writer_delay
        if work_mem is not None:
            self._values["work_mem"] = work_mem

    @builtins.property
    def admin_password(self) -> typing.Optional[builtins.str]:
        '''Custom password for admin user.

        Defaults to random string. This must be set only when a new service is being created.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#admin_password ManagedDatabasePostgresql#admin_password}
        '''
        result = self._values.get("admin_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def admin_username(self) -> typing.Optional[builtins.str]:
        '''Custom username for admin user. This must be set only when a new service is being created.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#admin_username ManagedDatabasePostgresql#admin_username}
        '''
        result = self._values.get("admin_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def automatic_utility_network_ip_filter(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Automatic utility network IP Filter. Automatically allow connections from servers in the utility network within the same zone.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#automatic_utility_network_ip_filter ManagedDatabasePostgresql#automatic_utility_network_ip_filter}
        '''
        result = self._values.get("automatic_utility_network_ip_filter")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def autovacuum_analyze_scale_factor(self) -> typing.Optional[jsii.Number]:
        '''Specifies a fraction of the table size to add to autovacuum_analyze_threshold when deciding whether to trigger an ANALYZE (e.g. ``0.2`` for 20% of the table size). The default is ``0.2``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autovacuum_analyze_scale_factor ManagedDatabasePostgresql#autovacuum_analyze_scale_factor}
        '''
        result = self._values.get("autovacuum_analyze_scale_factor")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autovacuum_analyze_threshold(self) -> typing.Optional[jsii.Number]:
        '''Specifies the minimum number of inserted, updated or deleted tuples needed to trigger an ANALYZE in any one table.

        The default is ``50``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autovacuum_analyze_threshold ManagedDatabasePostgresql#autovacuum_analyze_threshold}
        '''
        result = self._values.get("autovacuum_analyze_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autovacuum_freeze_max_age(self) -> typing.Optional[jsii.Number]:
        '''Specifies the maximum age (in transactions) that a table's pg_class.relfrozenxid field can attain before a VACUUM operation is forced to prevent transaction ID wraparound within the table. The system launches autovacuum processes to prevent wraparound even when autovacuum is otherwise disabled. Changing this parameter causes a service restart.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autovacuum_freeze_max_age ManagedDatabasePostgresql#autovacuum_freeze_max_age}
        '''
        result = self._values.get("autovacuum_freeze_max_age")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autovacuum_max_workers(self) -> typing.Optional[jsii.Number]:
        '''Specifies the maximum number of autovacuum processes (other than the autovacuum launcher) that may be running at any one time.

        The default is ``3``. Changing this parameter causes a service restart.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autovacuum_max_workers ManagedDatabasePostgresql#autovacuum_max_workers}
        '''
        result = self._values.get("autovacuum_max_workers")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autovacuum_naptime(self) -> typing.Optional[jsii.Number]:
        '''Specifies the minimum delay between autovacuum runs on any given database.

        The delay is measured in seconds. The default is ``60``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autovacuum_naptime ManagedDatabasePostgresql#autovacuum_naptime}
        '''
        result = self._values.get("autovacuum_naptime")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autovacuum_vacuum_cost_delay(self) -> typing.Optional[jsii.Number]:
        '''Specifies the cost delay value that will be used in automatic VACUUM operations.

        If ``-1`` is specified, the regular vacuum_cost_delay value will be used. The default is ``2`` (upstream default).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autovacuum_vacuum_cost_delay ManagedDatabasePostgresql#autovacuum_vacuum_cost_delay}
        '''
        result = self._values.get("autovacuum_vacuum_cost_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autovacuum_vacuum_cost_limit(self) -> typing.Optional[jsii.Number]:
        '''Specifies the cost limit value that will be used in automatic VACUUM operations.

        If ``-1`` is specified, the regular vacuum_cost_limit value will be used. The default is ``-1`` (upstream default).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autovacuum_vacuum_cost_limit ManagedDatabasePostgresql#autovacuum_vacuum_cost_limit}
        '''
        result = self._values.get("autovacuum_vacuum_cost_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autovacuum_vacuum_scale_factor(self) -> typing.Optional[jsii.Number]:
        '''Specifies a fraction of the table size to add to autovacuum_vacuum_threshold when deciding whether to trigger a VACUUM (e.g. ``0.2`` for 20% of the table size). The default is ``0.2``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autovacuum_vacuum_scale_factor ManagedDatabasePostgresql#autovacuum_vacuum_scale_factor}
        '''
        result = self._values.get("autovacuum_vacuum_scale_factor")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autovacuum_vacuum_threshold(self) -> typing.Optional[jsii.Number]:
        '''Specifies the minimum number of updated or deleted tuples needed to trigger a VACUUM in any one table.

        The default is ``50``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autovacuum_vacuum_threshold ManagedDatabasePostgresql#autovacuum_vacuum_threshold}
        '''
        result = self._values.get("autovacuum_vacuum_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def backup_hour(self) -> typing.Optional[jsii.Number]:
        '''The hour of day (in UTC) when backup for the service is started.

        New backup is only started if previous backup has already completed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#backup_hour ManagedDatabasePostgresql#backup_hour}
        '''
        result = self._values.get("backup_hour")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def backup_minute(self) -> typing.Optional[jsii.Number]:
        '''The minute of an hour when backup for the service is started.

        New backup is only started if previous backup has already completed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#backup_minute ManagedDatabasePostgresql#backup_minute}
        '''
        result = self._values.get("backup_minute")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def bgwriter_delay(self) -> typing.Optional[jsii.Number]:
        '''Specifies the delay between activity rounds for the background writer in milliseconds. The default is ``200``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#bgwriter_delay ManagedDatabasePostgresql#bgwriter_delay}
        '''
        result = self._values.get("bgwriter_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def bgwriter_flush_after(self) -> typing.Optional[jsii.Number]:
        '''Whenever more than bgwriter_flush_after bytes have been written by the background writer, attempt to force the OS to issue these writes to the underlying storage.

        Specified in kilobytes. Setting of 0 disables forced writeback. The default is ``512``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#bgwriter_flush_after ManagedDatabasePostgresql#bgwriter_flush_after}
        '''
        result = self._values.get("bgwriter_flush_after")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def bgwriter_lru_maxpages(self) -> typing.Optional[jsii.Number]:
        '''In each round, no more than this many buffers will be written by the background writer.

        Setting this to zero disables background writing. The default is ``100``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#bgwriter_lru_maxpages ManagedDatabasePostgresql#bgwriter_lru_maxpages}
        '''
        result = self._values.get("bgwriter_lru_maxpages")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def bgwriter_lru_multiplier(self) -> typing.Optional[jsii.Number]:
        '''The average recent need for new buffers is multiplied by bgwriter_lru_multiplier to arrive at an estimate of the number that will be needed during the next round, (up to bgwriter_lru_maxpages).

        1.0 represents a “just in time” policy of writing exactly the number of buffers predicted to be needed. Larger values provide some cushion against spikes in demand, while smaller values intentionally leave writes to be done by server processes. The default is ``2.0``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#bgwriter_lru_multiplier ManagedDatabasePostgresql#bgwriter_lru_multiplier}
        '''
        result = self._values.get("bgwriter_lru_multiplier")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def deadlock_timeout(self) -> typing.Optional[jsii.Number]:
        '''This is the amount of time, in milliseconds, to wait on a lock before checking to see if there is a deadlock condition.

        The default is ``1000`` (upstream default).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#deadlock_timeout ManagedDatabasePostgresql#deadlock_timeout}
        '''
        result = self._values.get("deadlock_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def default_toast_compression(self) -> typing.Optional[builtins.str]:
        '''Specifies the default TOAST compression method for values of compressible columns.

        The default is ``lz4``. Only available for PostgreSQL 14+.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#default_toast_compression ManagedDatabasePostgresql#default_toast_compression}
        '''
        result = self._values.get("default_toast_compression")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def idle_in_transaction_session_timeout(self) -> typing.Optional[jsii.Number]:
        '''Time out sessions with open transactions after this number of milliseconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#idle_in_transaction_session_timeout ManagedDatabasePostgresql#idle_in_transaction_session_timeout}
        '''
        result = self._values.get("idle_in_transaction_session_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ip_filter(self) -> typing.Optional[typing.List[builtins.str]]:
        '''IP filter. Allow incoming connections from CIDR address block, e.g. '10.20.0.0/16'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#ip_filter ManagedDatabasePostgresql#ip_filter}
        '''
        result = self._values.get("ip_filter")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def jit(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Controls system-wide use of Just-in-Time Compilation (JIT).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#jit ManagedDatabasePostgresql#jit}
        '''
        result = self._values.get("jit")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def log_autovacuum_min_duration(self) -> typing.Optional[jsii.Number]:
        '''Causes each action executed by autovacuum to be logged if it ran for at least the specified number of milliseconds.

        Setting this to zero logs all autovacuum actions. Minus-one disables logging autovacuum actions. The default is ``1000``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_autovacuum_min_duration ManagedDatabasePostgresql#log_autovacuum_min_duration}
        '''
        result = self._values.get("log_autovacuum_min_duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def log_error_verbosity(self) -> typing.Optional[builtins.str]:
        '''Controls the amount of detail written in the server log for each message that is logged.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_error_verbosity ManagedDatabasePostgresql#log_error_verbosity}
        '''
        result = self._values.get("log_error_verbosity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_line_prefix(self) -> typing.Optional[builtins.str]:
        '''Choose from one of the available log formats.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_line_prefix ManagedDatabasePostgresql#log_line_prefix}
        '''
        result = self._values.get("log_line_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_min_duration_statement(self) -> typing.Optional[jsii.Number]:
        '''Log statements that take more than this number of milliseconds to run, -1 disables.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_min_duration_statement ManagedDatabasePostgresql#log_min_duration_statement}
        '''
        result = self._values.get("log_min_duration_statement")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def log_temp_files(self) -> typing.Optional[jsii.Number]:
        '''Log statements for each temporary file created larger than this number of kilobytes, -1 disables.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_temp_files ManagedDatabasePostgresql#log_temp_files}
        '''
        result = self._values.get("log_temp_files")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_connections(self) -> typing.Optional[jsii.Number]:
        '''PostgreSQL maximum number of concurrent connections to the database server. Changing this parameter causes a service restart.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_connections ManagedDatabasePostgresql#max_connections}
        '''
        result = self._values.get("max_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_files_per_process(self) -> typing.Optional[jsii.Number]:
        '''PostgreSQL maximum number of files that can be open per process.

        The default is ``1000`` (upstream default). Changing this parameter causes a service restart.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_files_per_process ManagedDatabasePostgresql#max_files_per_process}
        '''
        result = self._values.get("max_files_per_process")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_locks_per_transaction(self) -> typing.Optional[jsii.Number]:
        '''PostgreSQL maximum locks per transaction. Changing this parameter causes a service restart.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_locks_per_transaction ManagedDatabasePostgresql#max_locks_per_transaction}
        '''
        result = self._values.get("max_locks_per_transaction")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_logical_replication_workers(self) -> typing.Optional[jsii.Number]:
        '''PostgreSQL maximum logical replication workers (taken from the pool of max_parallel_workers).

        The default is ``4`` (upstream default). Changing this parameter causes a service restart.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_logical_replication_workers ManagedDatabasePostgresql#max_logical_replication_workers}
        '''
        result = self._values.get("max_logical_replication_workers")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_parallel_workers(self) -> typing.Optional[jsii.Number]:
        '''Sets the maximum number of workers that the system can support for parallel queries.

        The default is ``8`` (upstream default).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_parallel_workers ManagedDatabasePostgresql#max_parallel_workers}
        '''
        result = self._values.get("max_parallel_workers")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_parallel_workers_per_gather(self) -> typing.Optional[jsii.Number]:
        '''Sets the maximum number of workers that can be started by a single Gather or Gather Merge node.

        The default is ``2`` (upstream default).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_parallel_workers_per_gather ManagedDatabasePostgresql#max_parallel_workers_per_gather}
        '''
        result = self._values.get("max_parallel_workers_per_gather")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_pred_locks_per_transaction(self) -> typing.Optional[jsii.Number]:
        '''PostgreSQL maximum predicate locks per transaction. The default is ``64`` (upstream default). Changing this parameter causes a service restart.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_pred_locks_per_transaction ManagedDatabasePostgresql#max_pred_locks_per_transaction}
        '''
        result = self._values.get("max_pred_locks_per_transaction")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_prepared_transactions(self) -> typing.Optional[jsii.Number]:
        '''PostgreSQL maximum prepared transactions. The default is ``0``. Changing this parameter causes a service restart.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_prepared_transactions ManagedDatabasePostgresql#max_prepared_transactions}
        '''
        result = self._values.get("max_prepared_transactions")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_replication_slots(self) -> typing.Optional[jsii.Number]:
        '''PostgreSQL maximum replication slots. The default is ``20``. Changing this parameter causes a service restart.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_replication_slots ManagedDatabasePostgresql#max_replication_slots}
        '''
        result = self._values.get("max_replication_slots")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_slot_wal_keep_size(self) -> typing.Optional[jsii.Number]:
        '''PostgreSQL maximum WAL size (MB) reserved for replication slots.

        If ``-1`` is specified, replication slots may retain an unlimited amount of WAL files. The default is ``-1`` (upstream default). wal_keep_size minimum WAL size setting takes precedence over this.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_slot_wal_keep_size ManagedDatabasePostgresql#max_slot_wal_keep_size}
        '''
        result = self._values.get("max_slot_wal_keep_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_stack_depth(self) -> typing.Optional[jsii.Number]:
        '''Maximum depth of the stack in bytes. The default is ``2097152`` (upstream default).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_stack_depth ManagedDatabasePostgresql#max_stack_depth}
        '''
        result = self._values.get("max_stack_depth")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_standby_archive_delay(self) -> typing.Optional[jsii.Number]:
        '''Max standby archive delay in milliseconds. The default is ``30000`` (upstream default).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_standby_archive_delay ManagedDatabasePostgresql#max_standby_archive_delay}
        '''
        result = self._values.get("max_standby_archive_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_standby_streaming_delay(self) -> typing.Optional[jsii.Number]:
        '''Max standby streaming delay in milliseconds. The default is ``30000`` (upstream default).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_standby_streaming_delay ManagedDatabasePostgresql#max_standby_streaming_delay}
        '''
        result = self._values.get("max_standby_streaming_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_sync_workers_per_subscription(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of synchronization workers per subscription. The default is ``2``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_sync_workers_per_subscription ManagedDatabasePostgresql#max_sync_workers_per_subscription}
        '''
        result = self._values.get("max_sync_workers_per_subscription")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_wal_senders(self) -> typing.Optional[jsii.Number]:
        '''PostgreSQL maximum WAL senders. The default is ``20``. Changing this parameter causes a service restart.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_wal_senders ManagedDatabasePostgresql#max_wal_senders}
        '''
        result = self._values.get("max_wal_senders")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_worker_processes(self) -> typing.Optional[jsii.Number]:
        '''Sets the maximum number of background processes that the system can support.

        The default is ``8``. Changing this parameter causes a service restart.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_worker_processes ManagedDatabasePostgresql#max_worker_processes}
        '''
        result = self._values.get("max_worker_processes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def migration(
        self,
    ) -> typing.Optional["ManagedDatabasePostgresqlPropertiesMigration"]:
        '''migration block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#migration ManagedDatabasePostgresql#migration}
        '''
        result = self._values.get("migration")
        return typing.cast(typing.Optional["ManagedDatabasePostgresqlPropertiesMigration"], result)

    @builtins.property
    def password_encryption(self) -> typing.Optional[builtins.str]:
        '''Chooses the algorithm for encrypting passwords.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#password_encryption ManagedDatabasePostgresql#password_encryption}
        '''
        result = self._values.get("password_encryption")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pgaudit(self) -> typing.Optional["ManagedDatabasePostgresqlPropertiesPgaudit"]:
        '''pgaudit block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#pgaudit ManagedDatabasePostgresql#pgaudit}
        '''
        result = self._values.get("pgaudit")
        return typing.cast(typing.Optional["ManagedDatabasePostgresqlPropertiesPgaudit"], result)

    @builtins.property
    def pgbouncer(
        self,
    ) -> typing.Optional["ManagedDatabasePostgresqlPropertiesPgbouncer"]:
        '''pgbouncer block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#pgbouncer ManagedDatabasePostgresql#pgbouncer}
        '''
        result = self._values.get("pgbouncer")
        return typing.cast(typing.Optional["ManagedDatabasePostgresqlPropertiesPgbouncer"], result)

    @builtins.property
    def pglookout(
        self,
    ) -> typing.Optional["ManagedDatabasePostgresqlPropertiesPglookout"]:
        '''pglookout block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#pglookout ManagedDatabasePostgresql#pglookout}
        '''
        result = self._values.get("pglookout")
        return typing.cast(typing.Optional["ManagedDatabasePostgresqlPropertiesPglookout"], result)

    @builtins.property
    def pg_partman_bgw_interval(self) -> typing.Optional[jsii.Number]:
        '''Sets the time interval in seconds to run pg_partman's scheduled tasks. The default is ``3600``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#pg_partman_bgw_interval ManagedDatabasePostgresql#pg_partman_bgw_interval}
        '''
        result = self._values.get("pg_partman_bgw_interval")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def pg_partman_bgw_role(self) -> typing.Optional[builtins.str]:
        '''Controls which role to use for pg_partman's scheduled background tasks.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#pg_partman_bgw_role ManagedDatabasePostgresql#pg_partman_bgw_role}
        '''
        result = self._values.get("pg_partman_bgw_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pg_stat_monitor_enable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable pg_stat_monitor extension if available for the current cluster.

        Enable the pg_stat_monitor extension. Changing this parameter causes a service restart. When this extension is enabled, pg_stat_statements results for utility commands are unreliable.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#pg_stat_monitor_enable ManagedDatabasePostgresql#pg_stat_monitor_enable}
        '''
        result = self._values.get("pg_stat_monitor_enable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def pg_stat_monitor_pgsm_enable_query_plan(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enables or disables query plan monitoring. Changing this parameter causes a service restart. Only available for PostgreSQL 13+.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#pg_stat_monitor_pgsm_enable_query_plan ManagedDatabasePostgresql#pg_stat_monitor_pgsm_enable_query_plan}
        '''
        result = self._values.get("pg_stat_monitor_pgsm_enable_query_plan")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def pg_stat_monitor_pgsm_max_buckets(self) -> typing.Optional[jsii.Number]:
        '''Sets the maximum number of buckets. Changing this parameter causes a service restart. Only available for PostgreSQL 13+.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#pg_stat_monitor_pgsm_max_buckets ManagedDatabasePostgresql#pg_stat_monitor_pgsm_max_buckets}
        '''
        result = self._values.get("pg_stat_monitor_pgsm_max_buckets")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def pg_stat_statements_track(self) -> typing.Optional[builtins.str]:
        '''Controls which statements are counted.

        Specify top to track top-level statements (those issued directly by clients), all to also track nested statements (such as statements invoked within functions), or none to disable statement statistics collection. The default is ``top``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#pg_stat_statements_track ManagedDatabasePostgresql#pg_stat_statements_track}
        '''
        result = self._values.get("pg_stat_statements_track")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def public_access(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Public Access. Allow access to the service from the public Internet.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#public_access ManagedDatabasePostgresql#public_access}
        '''
        result = self._values.get("public_access")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def service_log(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Service logging. Store logs for the service so that they are available in the HTTP API and console.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#service_log ManagedDatabasePostgresql#service_log}
        '''
        result = self._values.get("service_log")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def shared_buffers_percentage(self) -> typing.Optional[jsii.Number]:
        '''Percentage of total RAM that the database server uses for shared memory buffers.

        Valid range is 20-60 (float), which corresponds to 20% - 60%. This setting adjusts the shared_buffers configuration value. Changing this parameter causes a service restart.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#shared_buffers_percentage ManagedDatabasePostgresql#shared_buffers_percentage}
        '''
        result = self._values.get("shared_buffers_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def synchronous_replication(self) -> typing.Optional[builtins.str]:
        '''Synchronous replication type. Note that the service plan also needs to support synchronous replication.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#synchronous_replication ManagedDatabasePostgresql#synchronous_replication}
        '''
        result = self._values.get("synchronous_replication")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def temp_file_limit(self) -> typing.Optional[jsii.Number]:
        '''PostgreSQL temporary file limit in KiB, -1 for unlimited.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#temp_file_limit ManagedDatabasePostgresql#temp_file_limit}
        '''
        result = self._values.get("temp_file_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def timescaledb(
        self,
    ) -> typing.Optional["ManagedDatabasePostgresqlPropertiesTimescaledb"]:
        '''timescaledb block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#timescaledb ManagedDatabasePostgresql#timescaledb}
        '''
        result = self._values.get("timescaledb")
        return typing.cast(typing.Optional["ManagedDatabasePostgresqlPropertiesTimescaledb"], result)

    @builtins.property
    def timezone(self) -> typing.Optional[builtins.str]:
        '''PostgreSQL service timezone.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#timezone ManagedDatabasePostgresql#timezone}
        '''
        result = self._values.get("timezone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def track_activity_query_size(self) -> typing.Optional[jsii.Number]:
        '''Specifies the number of bytes reserved to track the currently executing command for each active session.

        Changing this parameter causes a service restart.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#track_activity_query_size ManagedDatabasePostgresql#track_activity_query_size}
        '''
        result = self._values.get("track_activity_query_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def track_commit_timestamp(self) -> typing.Optional[builtins.str]:
        '''Record commit time of transactions. Changing this parameter causes a service restart.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#track_commit_timestamp ManagedDatabasePostgresql#track_commit_timestamp}
        '''
        result = self._values.get("track_commit_timestamp")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def track_functions(self) -> typing.Optional[builtins.str]:
        '''Enables tracking of function call counts and time used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#track_functions ManagedDatabasePostgresql#track_functions}
        '''
        result = self._values.get("track_functions")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def track_io_timing(self) -> typing.Optional[builtins.str]:
        '''Enables timing of database I/O calls.

        The default is ``off``. When on, it will repeatedly query the operating system for the current time, which may cause significant overhead on some platforms.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#track_io_timing ManagedDatabasePostgresql#track_io_timing}
        '''
        result = self._values.get("track_io_timing")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def variant(self) -> typing.Optional[builtins.str]:
        '''Variant of the PostgreSQL service, may affect the features that are exposed by default.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#variant ManagedDatabasePostgresql#variant}
        '''
        result = self._values.get("variant")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''PostgreSQL major version.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#version ManagedDatabasePostgresql#version}
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def wal_sender_timeout(self) -> typing.Optional[jsii.Number]:
        '''Terminate replication connections that are inactive for longer than this amount of time, in milliseconds.

        Setting this value to zero disables the timeout.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#wal_sender_timeout ManagedDatabasePostgresql#wal_sender_timeout}
        '''
        result = self._values.get("wal_sender_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def wal_writer_delay(self) -> typing.Optional[jsii.Number]:
        '''WAL flush interval in milliseconds.

        The default is ``200``. Setting this parameter to a lower value may negatively impact performance.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#wal_writer_delay ManagedDatabasePostgresql#wal_writer_delay}
        '''
        result = self._values.get("wal_writer_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def work_mem(self) -> typing.Optional[jsii.Number]:
        '''Sets the maximum amount of memory to be used by a query operation (such as a sort or hash table) before writing to temporary disk files, in MB.

        The default is 1MB + 0.075% of total RAM (up to 32MB).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#work_mem ManagedDatabasePostgresql#work_mem}
        '''
        result = self._values.get("work_mem")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabasePostgresqlProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabasePostgresql.ManagedDatabasePostgresqlPropertiesMigration",
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
class ManagedDatabasePostgresqlPropertiesMigration:
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
        :param dbname: Database name for bootstrapping the initial connection. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#dbname ManagedDatabasePostgresql#dbname}
        :param host: Hostname or IP address of the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#host ManagedDatabasePostgresql#host}
        :param ignore_dbs: Comma-separated list of databases, which should be ignored during migration (supported by MySQL and PostgreSQL only at the moment). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#ignore_dbs ManagedDatabasePostgresql#ignore_dbs}
        :param ignore_roles: Comma-separated list of database roles, which should be ignored during migration (supported by PostgreSQL only at the moment). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#ignore_roles ManagedDatabasePostgresql#ignore_roles}
        :param method: The migration method to be used (currently supported only by Redis, Dragonfly, MySQL and PostgreSQL service types). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#method ManagedDatabasePostgresql#method}
        :param password: Password for authentication with the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#password ManagedDatabasePostgresql#password}
        :param port: Port number of the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#port ManagedDatabasePostgresql#port}
        :param ssl: The server where to migrate data from is secured with SSL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#ssl ManagedDatabasePostgresql#ssl}
        :param username: User name for authentication with the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#username ManagedDatabasePostgresql#username}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a22b07e9381a03b0e883019f9869d2e86afe1337164b3f40f42a65332f93686)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#dbname ManagedDatabasePostgresql#dbname}
        '''
        result = self._values.get("dbname")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def host(self) -> typing.Optional[builtins.str]:
        '''Hostname or IP address of the server where to migrate data from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#host ManagedDatabasePostgresql#host}
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ignore_dbs(self) -> typing.Optional[builtins.str]:
        '''Comma-separated list of databases, which should be ignored during migration (supported by MySQL and PostgreSQL only at the moment).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#ignore_dbs ManagedDatabasePostgresql#ignore_dbs}
        '''
        result = self._values.get("ignore_dbs")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ignore_roles(self) -> typing.Optional[builtins.str]:
        '''Comma-separated list of database roles, which should be ignored during migration (supported by PostgreSQL only at the moment).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#ignore_roles ManagedDatabasePostgresql#ignore_roles}
        '''
        result = self._values.get("ignore_roles")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def method(self) -> typing.Optional[builtins.str]:
        '''The migration method to be used (currently supported only by Redis, Dragonfly, MySQL and PostgreSQL service types).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#method ManagedDatabasePostgresql#method}
        '''
        result = self._values.get("method")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''Password for authentication with the server where to migrate data from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#password ManagedDatabasePostgresql#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''Port number of the server where to migrate data from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#port ManagedDatabasePostgresql#port}
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ssl(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''The server where to migrate data from is secured with SSL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#ssl ManagedDatabasePostgresql#ssl}
        '''
        result = self._values.get("ssl")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''User name for authentication with the server where to migrate data from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#username ManagedDatabasePostgresql#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabasePostgresqlPropertiesMigration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabasePostgresqlPropertiesMigrationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabasePostgresql.ManagedDatabasePostgresqlPropertiesMigrationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4c1cd6b016b3ecb62182c2c4b44e046bb68d9a8b41715e737aba7a40ab4e1637)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b35ea3bbc7714f1786f8de42e581bd9d0755d59208f76b03479dc828d8245f43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dbname", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3d28cbb40378d958cbd4f1486106b3f33d4fcb347c34e4cfe965dcbc84f6072)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ignoreDbs")
    def ignore_dbs(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ignoreDbs"))

    @ignore_dbs.setter
    def ignore_dbs(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ed77193308666d5a3848635d267e0d341fc69179190e0832fb81a48f162713c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ignoreDbs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ignoreRoles")
    def ignore_roles(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ignoreRoles"))

    @ignore_roles.setter
    def ignore_roles(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a20cfd19af931dbf2350ffb4fb7828dc7d2993e5d8584a2ea8328dd07dc40bbd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ignoreRoles", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "method"))

    @method.setter
    def method(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1fb4c8b4612f86674f4e64dd17d4ed079eecd07d785ab3841dc409b159a5e95c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "method", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0fdfd5c0b89db2edd92450c9ac53a11e1f3dd5d6210595996291472c6e80be5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b9b1430714b0435905f992cb1eaf06eb4fb5ef51814d7828c304129e683d5d1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__02d3b89fb0ac87ce8d17953f5475d399eab9cc555961de1f9ce099be18c0c578)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ssl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__167fb42ea04e1b821e95e7693f524cc2b079cb09f33c63d1dbc80af39e37da15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabasePostgresqlPropertiesMigration]:
        return typing.cast(typing.Optional[ManagedDatabasePostgresqlPropertiesMigration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabasePostgresqlPropertiesMigration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f46213f544334fa98fbf9d56573c816a8c7df86df770ee7114ad7be53e0e700)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ManagedDatabasePostgresqlPropertiesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabasePostgresql.ManagedDatabasePostgresqlPropertiesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fd90a4ce70c5f20045cf9addde31aea1f70a84fb416d20f3285b17ca585a10e9)
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
        :param dbname: Database name for bootstrapping the initial connection. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#dbname ManagedDatabasePostgresql#dbname}
        :param host: Hostname or IP address of the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#host ManagedDatabasePostgresql#host}
        :param ignore_dbs: Comma-separated list of databases, which should be ignored during migration (supported by MySQL and PostgreSQL only at the moment). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#ignore_dbs ManagedDatabasePostgresql#ignore_dbs}
        :param ignore_roles: Comma-separated list of database roles, which should be ignored during migration (supported by PostgreSQL only at the moment). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#ignore_roles ManagedDatabasePostgresql#ignore_roles}
        :param method: The migration method to be used (currently supported only by Redis, Dragonfly, MySQL and PostgreSQL service types). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#method ManagedDatabasePostgresql#method}
        :param password: Password for authentication with the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#password ManagedDatabasePostgresql#password}
        :param port: Port number of the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#port ManagedDatabasePostgresql#port}
        :param ssl: The server where to migrate data from is secured with SSL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#ssl ManagedDatabasePostgresql#ssl}
        :param username: User name for authentication with the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#username ManagedDatabasePostgresql#username}
        '''
        value = ManagedDatabasePostgresqlPropertiesMigration(
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

    @jsii.member(jsii_name="putPgaudit")
    def put_pgaudit(
        self,
        *,
        feature_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        log: typing.Optional[typing.Sequence[builtins.str]] = None,
        log_catalog: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        log_client: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        log_level: typing.Optional[builtins.str] = None,
        log_max_string_length: typing.Optional[jsii.Number] = None,
        log_nested_statements: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        log_parameter: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        log_parameter_max_size: typing.Optional[jsii.Number] = None,
        log_relation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        log_rows: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        log_statement: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        log_statement_once: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        role: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param feature_enabled: Enable pgaudit extension. Enable pgaudit extension. When enabled, pgaudit extension will be automatically installed.Otherwise, extension will be uninstalled but auditing configurations will be preserved. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#feature_enabled ManagedDatabasePostgresql#feature_enabled}
        :param log: Specifies which classes of statements will be logged by session audit logging. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log ManagedDatabasePostgresql#log}
        :param log_catalog: Specifies that session logging should be enabled in the casewhere all relations in a statement are in pg_catalog. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_catalog ManagedDatabasePostgresql#log_catalog}
        :param log_client: Specifies whether log messages will be visible to a client process such as psql. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_client ManagedDatabasePostgresql#log_client}
        :param log_level: Specifies the log level that will be used for log entries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_level ManagedDatabasePostgresql#log_level}
        :param log_max_string_length: Crop parameters representation and whole statements if they exceed this threshold. A (default) value of -1 disable the truncation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_max_string_length ManagedDatabasePostgresql#log_max_string_length}
        :param log_nested_statements: This GUC allows to turn off logging nested statements, that is, statements that are executed as part of another ExecutorRun. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_nested_statements ManagedDatabasePostgresql#log_nested_statements}
        :param log_parameter: Specifies that audit logging should include the parameters that were passed with the statement. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_parameter ManagedDatabasePostgresql#log_parameter}
        :param log_parameter_max_size: Specifies that parameter values longer than this setting (in bytes) should not be logged, but replaced with . Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_parameter_max_size ManagedDatabasePostgresql#log_parameter_max_size}
        :param log_relation: Specifies whether session audit logging should create a separate log entry for each relation (TABLE, VIEW, etc.) referenced in a SELECT or DML statement. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_relation ManagedDatabasePostgresql#log_relation}
        :param log_rows: Specifies that audit logging should include the rows retrieved or affected by a statement. When enabled the rows field will be included after the parameter field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_rows ManagedDatabasePostgresql#log_rows}
        :param log_statement: Specifies whether logging will include the statement text and parameters (if enabled). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_statement ManagedDatabasePostgresql#log_statement}
        :param log_statement_once: Specifies whether logging will include the statement text and parameters with the first log entry for a statement/substatement combination or with every entry. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_statement_once ManagedDatabasePostgresql#log_statement_once}
        :param role: Specifies the master role to use for object audit logging. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#role ManagedDatabasePostgresql#role}
        '''
        value = ManagedDatabasePostgresqlPropertiesPgaudit(
            feature_enabled=feature_enabled,
            log=log,
            log_catalog=log_catalog,
            log_client=log_client,
            log_level=log_level,
            log_max_string_length=log_max_string_length,
            log_nested_statements=log_nested_statements,
            log_parameter=log_parameter,
            log_parameter_max_size=log_parameter_max_size,
            log_relation=log_relation,
            log_rows=log_rows,
            log_statement=log_statement,
            log_statement_once=log_statement_once,
            role=role,
        )

        return typing.cast(None, jsii.invoke(self, "putPgaudit", [value]))

    @jsii.member(jsii_name="putPgbouncer")
    def put_pgbouncer(
        self,
        *,
        autodb_idle_timeout: typing.Optional[jsii.Number] = None,
        autodb_max_db_connections: typing.Optional[jsii.Number] = None,
        autodb_pool_mode: typing.Optional[builtins.str] = None,
        autodb_pool_size: typing.Optional[jsii.Number] = None,
        ignore_startup_parameters: typing.Optional[typing.Sequence[builtins.str]] = None,
        max_prepared_statements: typing.Optional[jsii.Number] = None,
        min_pool_size: typing.Optional[jsii.Number] = None,
        server_idle_timeout: typing.Optional[jsii.Number] = None,
        server_lifetime: typing.Optional[jsii.Number] = None,
        server_reset_query_always: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param autodb_idle_timeout: If the automatically created database pools have been unused this many seconds, they are freed. If 0 then timeout is disabled. [seconds]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autodb_idle_timeout ManagedDatabasePostgresql#autodb_idle_timeout}
        :param autodb_max_db_connections: Do not allow more than this many server connections per database (regardless of user). Setting it to 0 means unlimited. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autodb_max_db_connections ManagedDatabasePostgresql#autodb_max_db_connections}
        :param autodb_pool_mode: PGBouncer pool mode. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autodb_pool_mode ManagedDatabasePostgresql#autodb_pool_mode}
        :param autodb_pool_size: If non-zero then create automatically a pool of that size per user when a pool doesn't exist. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autodb_pool_size ManagedDatabasePostgresql#autodb_pool_size}
        :param ignore_startup_parameters: List of parameters to ignore when given in startup packet. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#ignore_startup_parameters ManagedDatabasePostgresql#ignore_startup_parameters}
        :param max_prepared_statements: PgBouncer tracks protocol-level named prepared statements related commands sent by the client in transaction and statement pooling modes when max_prepared_statements is set to a non-zero value. Setting it to 0 disables prepared statements. max_prepared_statements defaults to 100, and its maximum is 3000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_prepared_statements ManagedDatabasePostgresql#max_prepared_statements}
        :param min_pool_size: Add more server connections to pool if below this number. Improves behavior when usual load comes suddenly back after period of total inactivity. The value is effectively capped at the pool size. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#min_pool_size ManagedDatabasePostgresql#min_pool_size}
        :param server_idle_timeout: If a server connection has been idle more than this many seconds it will be dropped. If 0 then timeout is disabled. [seconds]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#server_idle_timeout ManagedDatabasePostgresql#server_idle_timeout}
        :param server_lifetime: The pooler will close an unused server connection that has been connected longer than this. [seconds]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#server_lifetime ManagedDatabasePostgresql#server_lifetime}
        :param server_reset_query_always: Run server_reset_query (DISCARD ALL) in all pooling modes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#server_reset_query_always ManagedDatabasePostgresql#server_reset_query_always}
        '''
        value = ManagedDatabasePostgresqlPropertiesPgbouncer(
            autodb_idle_timeout=autodb_idle_timeout,
            autodb_max_db_connections=autodb_max_db_connections,
            autodb_pool_mode=autodb_pool_mode,
            autodb_pool_size=autodb_pool_size,
            ignore_startup_parameters=ignore_startup_parameters,
            max_prepared_statements=max_prepared_statements,
            min_pool_size=min_pool_size,
            server_idle_timeout=server_idle_timeout,
            server_lifetime=server_lifetime,
            server_reset_query_always=server_reset_query_always,
        )

        return typing.cast(None, jsii.invoke(self, "putPgbouncer", [value]))

    @jsii.member(jsii_name="putPglookout")
    def put_pglookout(
        self,
        *,
        max_failover_replication_time_lag: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_failover_replication_time_lag: Number of seconds of master unavailability before triggering database failover to standby. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_failover_replication_time_lag ManagedDatabasePostgresql#max_failover_replication_time_lag}
        '''
        value = ManagedDatabasePostgresqlPropertiesPglookout(
            max_failover_replication_time_lag=max_failover_replication_time_lag
        )

        return typing.cast(None, jsii.invoke(self, "putPglookout", [value]))

    @jsii.member(jsii_name="putTimescaledb")
    def put_timescaledb(
        self,
        *,
        max_background_workers: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_background_workers: The number of background workers for timescaledb operations. You should configure this setting to the sum of your number of databases and the total number of concurrent background workers you want running at any given point in time. Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_background_workers ManagedDatabasePostgresql#max_background_workers}
        '''
        value = ManagedDatabasePostgresqlPropertiesTimescaledb(
            max_background_workers=max_background_workers
        )

        return typing.cast(None, jsii.invoke(self, "putTimescaledb", [value]))

    @jsii.member(jsii_name="resetAdminPassword")
    def reset_admin_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdminPassword", []))

    @jsii.member(jsii_name="resetAdminUsername")
    def reset_admin_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdminUsername", []))

    @jsii.member(jsii_name="resetAutomaticUtilityNetworkIpFilter")
    def reset_automatic_utility_network_ip_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutomaticUtilityNetworkIpFilter", []))

    @jsii.member(jsii_name="resetAutovacuumAnalyzeScaleFactor")
    def reset_autovacuum_analyze_scale_factor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutovacuumAnalyzeScaleFactor", []))

    @jsii.member(jsii_name="resetAutovacuumAnalyzeThreshold")
    def reset_autovacuum_analyze_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutovacuumAnalyzeThreshold", []))

    @jsii.member(jsii_name="resetAutovacuumFreezeMaxAge")
    def reset_autovacuum_freeze_max_age(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutovacuumFreezeMaxAge", []))

    @jsii.member(jsii_name="resetAutovacuumMaxWorkers")
    def reset_autovacuum_max_workers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutovacuumMaxWorkers", []))

    @jsii.member(jsii_name="resetAutovacuumNaptime")
    def reset_autovacuum_naptime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutovacuumNaptime", []))

    @jsii.member(jsii_name="resetAutovacuumVacuumCostDelay")
    def reset_autovacuum_vacuum_cost_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutovacuumVacuumCostDelay", []))

    @jsii.member(jsii_name="resetAutovacuumVacuumCostLimit")
    def reset_autovacuum_vacuum_cost_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutovacuumVacuumCostLimit", []))

    @jsii.member(jsii_name="resetAutovacuumVacuumScaleFactor")
    def reset_autovacuum_vacuum_scale_factor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutovacuumVacuumScaleFactor", []))

    @jsii.member(jsii_name="resetAutovacuumVacuumThreshold")
    def reset_autovacuum_vacuum_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutovacuumVacuumThreshold", []))

    @jsii.member(jsii_name="resetBackupHour")
    def reset_backup_hour(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupHour", []))

    @jsii.member(jsii_name="resetBackupMinute")
    def reset_backup_minute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupMinute", []))

    @jsii.member(jsii_name="resetBgwriterDelay")
    def reset_bgwriter_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBgwriterDelay", []))

    @jsii.member(jsii_name="resetBgwriterFlushAfter")
    def reset_bgwriter_flush_after(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBgwriterFlushAfter", []))

    @jsii.member(jsii_name="resetBgwriterLruMaxpages")
    def reset_bgwriter_lru_maxpages(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBgwriterLruMaxpages", []))

    @jsii.member(jsii_name="resetBgwriterLruMultiplier")
    def reset_bgwriter_lru_multiplier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBgwriterLruMultiplier", []))

    @jsii.member(jsii_name="resetDeadlockTimeout")
    def reset_deadlock_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeadlockTimeout", []))

    @jsii.member(jsii_name="resetDefaultToastCompression")
    def reset_default_toast_compression(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultToastCompression", []))

    @jsii.member(jsii_name="resetIdleInTransactionSessionTimeout")
    def reset_idle_in_transaction_session_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdleInTransactionSessionTimeout", []))

    @jsii.member(jsii_name="resetIpFilter")
    def reset_ip_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpFilter", []))

    @jsii.member(jsii_name="resetJit")
    def reset_jit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJit", []))

    @jsii.member(jsii_name="resetLogAutovacuumMinDuration")
    def reset_log_autovacuum_min_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogAutovacuumMinDuration", []))

    @jsii.member(jsii_name="resetLogErrorVerbosity")
    def reset_log_error_verbosity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogErrorVerbosity", []))

    @jsii.member(jsii_name="resetLogLinePrefix")
    def reset_log_line_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogLinePrefix", []))

    @jsii.member(jsii_name="resetLogMinDurationStatement")
    def reset_log_min_duration_statement(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogMinDurationStatement", []))

    @jsii.member(jsii_name="resetLogTempFiles")
    def reset_log_temp_files(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogTempFiles", []))

    @jsii.member(jsii_name="resetMaxConnections")
    def reset_max_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxConnections", []))

    @jsii.member(jsii_name="resetMaxFilesPerProcess")
    def reset_max_files_per_process(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxFilesPerProcess", []))

    @jsii.member(jsii_name="resetMaxLocksPerTransaction")
    def reset_max_locks_per_transaction(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxLocksPerTransaction", []))

    @jsii.member(jsii_name="resetMaxLogicalReplicationWorkers")
    def reset_max_logical_replication_workers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxLogicalReplicationWorkers", []))

    @jsii.member(jsii_name="resetMaxParallelWorkers")
    def reset_max_parallel_workers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxParallelWorkers", []))

    @jsii.member(jsii_name="resetMaxParallelWorkersPerGather")
    def reset_max_parallel_workers_per_gather(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxParallelWorkersPerGather", []))

    @jsii.member(jsii_name="resetMaxPredLocksPerTransaction")
    def reset_max_pred_locks_per_transaction(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxPredLocksPerTransaction", []))

    @jsii.member(jsii_name="resetMaxPreparedTransactions")
    def reset_max_prepared_transactions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxPreparedTransactions", []))

    @jsii.member(jsii_name="resetMaxReplicationSlots")
    def reset_max_replication_slots(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxReplicationSlots", []))

    @jsii.member(jsii_name="resetMaxSlotWalKeepSize")
    def reset_max_slot_wal_keep_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxSlotWalKeepSize", []))

    @jsii.member(jsii_name="resetMaxStackDepth")
    def reset_max_stack_depth(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxStackDepth", []))

    @jsii.member(jsii_name="resetMaxStandbyArchiveDelay")
    def reset_max_standby_archive_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxStandbyArchiveDelay", []))

    @jsii.member(jsii_name="resetMaxStandbyStreamingDelay")
    def reset_max_standby_streaming_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxStandbyStreamingDelay", []))

    @jsii.member(jsii_name="resetMaxSyncWorkersPerSubscription")
    def reset_max_sync_workers_per_subscription(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxSyncWorkersPerSubscription", []))

    @jsii.member(jsii_name="resetMaxWalSenders")
    def reset_max_wal_senders(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxWalSenders", []))

    @jsii.member(jsii_name="resetMaxWorkerProcesses")
    def reset_max_worker_processes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxWorkerProcesses", []))

    @jsii.member(jsii_name="resetMigration")
    def reset_migration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMigration", []))

    @jsii.member(jsii_name="resetPasswordEncryption")
    def reset_password_encryption(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordEncryption", []))

    @jsii.member(jsii_name="resetPgaudit")
    def reset_pgaudit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPgaudit", []))

    @jsii.member(jsii_name="resetPgbouncer")
    def reset_pgbouncer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPgbouncer", []))

    @jsii.member(jsii_name="resetPglookout")
    def reset_pglookout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPglookout", []))

    @jsii.member(jsii_name="resetPgPartmanBgwInterval")
    def reset_pg_partman_bgw_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPgPartmanBgwInterval", []))

    @jsii.member(jsii_name="resetPgPartmanBgwRole")
    def reset_pg_partman_bgw_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPgPartmanBgwRole", []))

    @jsii.member(jsii_name="resetPgStatMonitorEnable")
    def reset_pg_stat_monitor_enable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPgStatMonitorEnable", []))

    @jsii.member(jsii_name="resetPgStatMonitorPgsmEnableQueryPlan")
    def reset_pg_stat_monitor_pgsm_enable_query_plan(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPgStatMonitorPgsmEnableQueryPlan", []))

    @jsii.member(jsii_name="resetPgStatMonitorPgsmMaxBuckets")
    def reset_pg_stat_monitor_pgsm_max_buckets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPgStatMonitorPgsmMaxBuckets", []))

    @jsii.member(jsii_name="resetPgStatStatementsTrack")
    def reset_pg_stat_statements_track(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPgStatStatementsTrack", []))

    @jsii.member(jsii_name="resetPublicAccess")
    def reset_public_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicAccess", []))

    @jsii.member(jsii_name="resetServiceLog")
    def reset_service_log(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceLog", []))

    @jsii.member(jsii_name="resetSharedBuffersPercentage")
    def reset_shared_buffers_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSharedBuffersPercentage", []))

    @jsii.member(jsii_name="resetSynchronousReplication")
    def reset_synchronous_replication(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSynchronousReplication", []))

    @jsii.member(jsii_name="resetTempFileLimit")
    def reset_temp_file_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTempFileLimit", []))

    @jsii.member(jsii_name="resetTimescaledb")
    def reset_timescaledb(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimescaledb", []))

    @jsii.member(jsii_name="resetTimezone")
    def reset_timezone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimezone", []))

    @jsii.member(jsii_name="resetTrackActivityQuerySize")
    def reset_track_activity_query_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTrackActivityQuerySize", []))

    @jsii.member(jsii_name="resetTrackCommitTimestamp")
    def reset_track_commit_timestamp(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTrackCommitTimestamp", []))

    @jsii.member(jsii_name="resetTrackFunctions")
    def reset_track_functions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTrackFunctions", []))

    @jsii.member(jsii_name="resetTrackIoTiming")
    def reset_track_io_timing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTrackIoTiming", []))

    @jsii.member(jsii_name="resetVariant")
    def reset_variant(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVariant", []))

    @jsii.member(jsii_name="resetVersion")
    def reset_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersion", []))

    @jsii.member(jsii_name="resetWalSenderTimeout")
    def reset_wal_sender_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWalSenderTimeout", []))

    @jsii.member(jsii_name="resetWalWriterDelay")
    def reset_wal_writer_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWalWriterDelay", []))

    @jsii.member(jsii_name="resetWorkMem")
    def reset_work_mem(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkMem", []))

    @builtins.property
    @jsii.member(jsii_name="migration")
    def migration(self) -> ManagedDatabasePostgresqlPropertiesMigrationOutputReference:
        return typing.cast(ManagedDatabasePostgresqlPropertiesMigrationOutputReference, jsii.get(self, "migration"))

    @builtins.property
    @jsii.member(jsii_name="pgaudit")
    def pgaudit(self) -> "ManagedDatabasePostgresqlPropertiesPgauditOutputReference":
        return typing.cast("ManagedDatabasePostgresqlPropertiesPgauditOutputReference", jsii.get(self, "pgaudit"))

    @builtins.property
    @jsii.member(jsii_name="pgbouncer")
    def pgbouncer(
        self,
    ) -> "ManagedDatabasePostgresqlPropertiesPgbouncerOutputReference":
        return typing.cast("ManagedDatabasePostgresqlPropertiesPgbouncerOutputReference", jsii.get(self, "pgbouncer"))

    @builtins.property
    @jsii.member(jsii_name="pglookout")
    def pglookout(
        self,
    ) -> "ManagedDatabasePostgresqlPropertiesPglookoutOutputReference":
        return typing.cast("ManagedDatabasePostgresqlPropertiesPglookoutOutputReference", jsii.get(self, "pglookout"))

    @builtins.property
    @jsii.member(jsii_name="timescaledb")
    def timescaledb(
        self,
    ) -> "ManagedDatabasePostgresqlPropertiesTimescaledbOutputReference":
        return typing.cast("ManagedDatabasePostgresqlPropertiesTimescaledbOutputReference", jsii.get(self, "timescaledb"))

    @builtins.property
    @jsii.member(jsii_name="adminPasswordInput")
    def admin_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "adminPasswordInput"))

    @builtins.property
    @jsii.member(jsii_name="adminUsernameInput")
    def admin_username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "adminUsernameInput"))

    @builtins.property
    @jsii.member(jsii_name="automaticUtilityNetworkIpFilterInput")
    def automatic_utility_network_ip_filter_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "automaticUtilityNetworkIpFilterInput"))

    @builtins.property
    @jsii.member(jsii_name="autovacuumAnalyzeScaleFactorInput")
    def autovacuum_analyze_scale_factor_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autovacuumAnalyzeScaleFactorInput"))

    @builtins.property
    @jsii.member(jsii_name="autovacuumAnalyzeThresholdInput")
    def autovacuum_analyze_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autovacuumAnalyzeThresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="autovacuumFreezeMaxAgeInput")
    def autovacuum_freeze_max_age_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autovacuumFreezeMaxAgeInput"))

    @builtins.property
    @jsii.member(jsii_name="autovacuumMaxWorkersInput")
    def autovacuum_max_workers_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autovacuumMaxWorkersInput"))

    @builtins.property
    @jsii.member(jsii_name="autovacuumNaptimeInput")
    def autovacuum_naptime_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autovacuumNaptimeInput"))

    @builtins.property
    @jsii.member(jsii_name="autovacuumVacuumCostDelayInput")
    def autovacuum_vacuum_cost_delay_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autovacuumVacuumCostDelayInput"))

    @builtins.property
    @jsii.member(jsii_name="autovacuumVacuumCostLimitInput")
    def autovacuum_vacuum_cost_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autovacuumVacuumCostLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="autovacuumVacuumScaleFactorInput")
    def autovacuum_vacuum_scale_factor_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autovacuumVacuumScaleFactorInput"))

    @builtins.property
    @jsii.member(jsii_name="autovacuumVacuumThresholdInput")
    def autovacuum_vacuum_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autovacuumVacuumThresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="backupHourInput")
    def backup_hour_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "backupHourInput"))

    @builtins.property
    @jsii.member(jsii_name="backupMinuteInput")
    def backup_minute_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "backupMinuteInput"))

    @builtins.property
    @jsii.member(jsii_name="bgwriterDelayInput")
    def bgwriter_delay_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bgwriterDelayInput"))

    @builtins.property
    @jsii.member(jsii_name="bgwriterFlushAfterInput")
    def bgwriter_flush_after_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bgwriterFlushAfterInput"))

    @builtins.property
    @jsii.member(jsii_name="bgwriterLruMaxpagesInput")
    def bgwriter_lru_maxpages_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bgwriterLruMaxpagesInput"))

    @builtins.property
    @jsii.member(jsii_name="bgwriterLruMultiplierInput")
    def bgwriter_lru_multiplier_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bgwriterLruMultiplierInput"))

    @builtins.property
    @jsii.member(jsii_name="deadlockTimeoutInput")
    def deadlock_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "deadlockTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultToastCompressionInput")
    def default_toast_compression_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultToastCompressionInput"))

    @builtins.property
    @jsii.member(jsii_name="idleInTransactionSessionTimeoutInput")
    def idle_in_transaction_session_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "idleInTransactionSessionTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="ipFilterInput")
    def ip_filter_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ipFilterInput"))

    @builtins.property
    @jsii.member(jsii_name="jitInput")
    def jit_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "jitInput"))

    @builtins.property
    @jsii.member(jsii_name="logAutovacuumMinDurationInput")
    def log_autovacuum_min_duration_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "logAutovacuumMinDurationInput"))

    @builtins.property
    @jsii.member(jsii_name="logErrorVerbosityInput")
    def log_error_verbosity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logErrorVerbosityInput"))

    @builtins.property
    @jsii.member(jsii_name="logLinePrefixInput")
    def log_line_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logLinePrefixInput"))

    @builtins.property
    @jsii.member(jsii_name="logMinDurationStatementInput")
    def log_min_duration_statement_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "logMinDurationStatementInput"))

    @builtins.property
    @jsii.member(jsii_name="logTempFilesInput")
    def log_temp_files_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "logTempFilesInput"))

    @builtins.property
    @jsii.member(jsii_name="maxConnectionsInput")
    def max_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxFilesPerProcessInput")
    def max_files_per_process_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxFilesPerProcessInput"))

    @builtins.property
    @jsii.member(jsii_name="maxLocksPerTransactionInput")
    def max_locks_per_transaction_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxLocksPerTransactionInput"))

    @builtins.property
    @jsii.member(jsii_name="maxLogicalReplicationWorkersInput")
    def max_logical_replication_workers_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxLogicalReplicationWorkersInput"))

    @builtins.property
    @jsii.member(jsii_name="maxParallelWorkersInput")
    def max_parallel_workers_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxParallelWorkersInput"))

    @builtins.property
    @jsii.member(jsii_name="maxParallelWorkersPerGatherInput")
    def max_parallel_workers_per_gather_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxParallelWorkersPerGatherInput"))

    @builtins.property
    @jsii.member(jsii_name="maxPredLocksPerTransactionInput")
    def max_pred_locks_per_transaction_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxPredLocksPerTransactionInput"))

    @builtins.property
    @jsii.member(jsii_name="maxPreparedTransactionsInput")
    def max_prepared_transactions_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxPreparedTransactionsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxReplicationSlotsInput")
    def max_replication_slots_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxReplicationSlotsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxSlotWalKeepSizeInput")
    def max_slot_wal_keep_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxSlotWalKeepSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="maxStackDepthInput")
    def max_stack_depth_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxStackDepthInput"))

    @builtins.property
    @jsii.member(jsii_name="maxStandbyArchiveDelayInput")
    def max_standby_archive_delay_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxStandbyArchiveDelayInput"))

    @builtins.property
    @jsii.member(jsii_name="maxStandbyStreamingDelayInput")
    def max_standby_streaming_delay_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxStandbyStreamingDelayInput"))

    @builtins.property
    @jsii.member(jsii_name="maxSyncWorkersPerSubscriptionInput")
    def max_sync_workers_per_subscription_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxSyncWorkersPerSubscriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="maxWalSendersInput")
    def max_wal_senders_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxWalSendersInput"))

    @builtins.property
    @jsii.member(jsii_name="maxWorkerProcessesInput")
    def max_worker_processes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxWorkerProcessesInput"))

    @builtins.property
    @jsii.member(jsii_name="migrationInput")
    def migration_input(
        self,
    ) -> typing.Optional[ManagedDatabasePostgresqlPropertiesMigration]:
        return typing.cast(typing.Optional[ManagedDatabasePostgresqlPropertiesMigration], jsii.get(self, "migrationInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordEncryptionInput")
    def password_encryption_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordEncryptionInput"))

    @builtins.property
    @jsii.member(jsii_name="pgauditInput")
    def pgaudit_input(
        self,
    ) -> typing.Optional["ManagedDatabasePostgresqlPropertiesPgaudit"]:
        return typing.cast(typing.Optional["ManagedDatabasePostgresqlPropertiesPgaudit"], jsii.get(self, "pgauditInput"))

    @builtins.property
    @jsii.member(jsii_name="pgbouncerInput")
    def pgbouncer_input(
        self,
    ) -> typing.Optional["ManagedDatabasePostgresqlPropertiesPgbouncer"]:
        return typing.cast(typing.Optional["ManagedDatabasePostgresqlPropertiesPgbouncer"], jsii.get(self, "pgbouncerInput"))

    @builtins.property
    @jsii.member(jsii_name="pglookoutInput")
    def pglookout_input(
        self,
    ) -> typing.Optional["ManagedDatabasePostgresqlPropertiesPglookout"]:
        return typing.cast(typing.Optional["ManagedDatabasePostgresqlPropertiesPglookout"], jsii.get(self, "pglookoutInput"))

    @builtins.property
    @jsii.member(jsii_name="pgPartmanBgwIntervalInput")
    def pg_partman_bgw_interval_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "pgPartmanBgwIntervalInput"))

    @builtins.property
    @jsii.member(jsii_name="pgPartmanBgwRoleInput")
    def pg_partman_bgw_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pgPartmanBgwRoleInput"))

    @builtins.property
    @jsii.member(jsii_name="pgStatMonitorEnableInput")
    def pg_stat_monitor_enable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "pgStatMonitorEnableInput"))

    @builtins.property
    @jsii.member(jsii_name="pgStatMonitorPgsmEnableQueryPlanInput")
    def pg_stat_monitor_pgsm_enable_query_plan_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "pgStatMonitorPgsmEnableQueryPlanInput"))

    @builtins.property
    @jsii.member(jsii_name="pgStatMonitorPgsmMaxBucketsInput")
    def pg_stat_monitor_pgsm_max_buckets_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "pgStatMonitorPgsmMaxBucketsInput"))

    @builtins.property
    @jsii.member(jsii_name="pgStatStatementsTrackInput")
    def pg_stat_statements_track_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pgStatStatementsTrackInput"))

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
    @jsii.member(jsii_name="sharedBuffersPercentageInput")
    def shared_buffers_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sharedBuffersPercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="synchronousReplicationInput")
    def synchronous_replication_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "synchronousReplicationInput"))

    @builtins.property
    @jsii.member(jsii_name="tempFileLimitInput")
    def temp_file_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "tempFileLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="timescaledbInput")
    def timescaledb_input(
        self,
    ) -> typing.Optional["ManagedDatabasePostgresqlPropertiesTimescaledb"]:
        return typing.cast(typing.Optional["ManagedDatabasePostgresqlPropertiesTimescaledb"], jsii.get(self, "timescaledbInput"))

    @builtins.property
    @jsii.member(jsii_name="timezoneInput")
    def timezone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timezoneInput"))

    @builtins.property
    @jsii.member(jsii_name="trackActivityQuerySizeInput")
    def track_activity_query_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "trackActivityQuerySizeInput"))

    @builtins.property
    @jsii.member(jsii_name="trackCommitTimestampInput")
    def track_commit_timestamp_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "trackCommitTimestampInput"))

    @builtins.property
    @jsii.member(jsii_name="trackFunctionsInput")
    def track_functions_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "trackFunctionsInput"))

    @builtins.property
    @jsii.member(jsii_name="trackIoTimingInput")
    def track_io_timing_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "trackIoTimingInput"))

    @builtins.property
    @jsii.member(jsii_name="variantInput")
    def variant_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "variantInput"))

    @builtins.property
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property
    @jsii.member(jsii_name="walSenderTimeoutInput")
    def wal_sender_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "walSenderTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="walWriterDelayInput")
    def wal_writer_delay_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "walWriterDelayInput"))

    @builtins.property
    @jsii.member(jsii_name="workMemInput")
    def work_mem_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "workMemInput"))

    @builtins.property
    @jsii.member(jsii_name="adminPassword")
    def admin_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adminPassword"))

    @admin_password.setter
    def admin_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dac988dc10ea16fb9d73a6bdeae092b92a2168b105b9582d692594c7083e324f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "adminPassword", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="adminUsername")
    def admin_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adminUsername"))

    @admin_username.setter
    def admin_username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0123a505cee8cef160f18f3716f895f89d5be5281c74f431861401dc632a8d56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "adminUsername", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__18323f68552123f0f23878838b830072c84a1d23d6ae5860aff23f18333b42ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "automaticUtilityNetworkIpFilter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autovacuumAnalyzeScaleFactor")
    def autovacuum_analyze_scale_factor(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autovacuumAnalyzeScaleFactor"))

    @autovacuum_analyze_scale_factor.setter
    def autovacuum_analyze_scale_factor(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a618a6d81df2b2decb7cfe9c114ac7a4b0bcb36d417cf676112d031e859d679f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autovacuumAnalyzeScaleFactor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autovacuumAnalyzeThreshold")
    def autovacuum_analyze_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autovacuumAnalyzeThreshold"))

    @autovacuum_analyze_threshold.setter
    def autovacuum_analyze_threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c07cfc51fe1598362f03697b2b0bb8e9179fb54050e6fcfc8540c42b2e95348)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autovacuumAnalyzeThreshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autovacuumFreezeMaxAge")
    def autovacuum_freeze_max_age(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autovacuumFreezeMaxAge"))

    @autovacuum_freeze_max_age.setter
    def autovacuum_freeze_max_age(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75489be2d1e658ac650ac29df5035521bb5a8082d17cfa3e793eaba19548d1b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autovacuumFreezeMaxAge", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autovacuumMaxWorkers")
    def autovacuum_max_workers(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autovacuumMaxWorkers"))

    @autovacuum_max_workers.setter
    def autovacuum_max_workers(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0635a8f3ceace0d0a4f6d5a43812c5632ab3de0c78310a9695579ff9c47d75a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autovacuumMaxWorkers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autovacuumNaptime")
    def autovacuum_naptime(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autovacuumNaptime"))

    @autovacuum_naptime.setter
    def autovacuum_naptime(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2db694007dd91d65c9b3b5ec8006f1756a4b6a931580bc7bdd21cb1086ab10b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autovacuumNaptime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autovacuumVacuumCostDelay")
    def autovacuum_vacuum_cost_delay(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autovacuumVacuumCostDelay"))

    @autovacuum_vacuum_cost_delay.setter
    def autovacuum_vacuum_cost_delay(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04a29a145fc98ceabd22d030c911868b284a234fdceaf518a58943364e7d3c8d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autovacuumVacuumCostDelay", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autovacuumVacuumCostLimit")
    def autovacuum_vacuum_cost_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autovacuumVacuumCostLimit"))

    @autovacuum_vacuum_cost_limit.setter
    def autovacuum_vacuum_cost_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7de5d23bbc4de2fa1bbe22a369eb8e374a5524f0bdfab27ed9c06916248712b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autovacuumVacuumCostLimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autovacuumVacuumScaleFactor")
    def autovacuum_vacuum_scale_factor(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autovacuumVacuumScaleFactor"))

    @autovacuum_vacuum_scale_factor.setter
    def autovacuum_vacuum_scale_factor(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__855b94ed8fdfeda7d578415566ffbb9c45fbcd24448de195e00f5cc8857772a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autovacuumVacuumScaleFactor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autovacuumVacuumThreshold")
    def autovacuum_vacuum_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autovacuumVacuumThreshold"))

    @autovacuum_vacuum_threshold.setter
    def autovacuum_vacuum_threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8958a970bed1aabf8c821857f37ccd8cb9d367466198e4093e10cd22e96c40ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autovacuumVacuumThreshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backupHour")
    def backup_hour(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "backupHour"))

    @backup_hour.setter
    def backup_hour(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ad16c11d7070fcace393ac131f62b8b0e0102b11780c91c4ea8d6d4336999a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backupHour", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backupMinute")
    def backup_minute(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "backupMinute"))

    @backup_minute.setter
    def backup_minute(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3cc1bdd7b35aa05f812e23d395f242921db855b5ddd67d2dad923b0720a01586)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backupMinute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bgwriterDelay")
    def bgwriter_delay(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bgwriterDelay"))

    @bgwriter_delay.setter
    def bgwriter_delay(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4abda546f558372c3256e28f606948c39da36ec568a2210a313c740e85116faf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bgwriterDelay", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bgwriterFlushAfter")
    def bgwriter_flush_after(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bgwriterFlushAfter"))

    @bgwriter_flush_after.setter
    def bgwriter_flush_after(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__054e3bbb6bdffd7b026b893f24da5331dbf751d8d826c30bb55830fcce2bb046)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bgwriterFlushAfter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bgwriterLruMaxpages")
    def bgwriter_lru_maxpages(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bgwriterLruMaxpages"))

    @bgwriter_lru_maxpages.setter
    def bgwriter_lru_maxpages(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__256293bdd5d65032ca8ebf18ab8ead4e10a5b6e12bef228e145c36908d09d7d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bgwriterLruMaxpages", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bgwriterLruMultiplier")
    def bgwriter_lru_multiplier(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bgwriterLruMultiplier"))

    @bgwriter_lru_multiplier.setter
    def bgwriter_lru_multiplier(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c01e6d51d8ebc918ea01fb3b38fda7c82e1ffb4870954be8caa2bace0da6f4b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bgwriterLruMultiplier", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deadlockTimeout")
    def deadlock_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "deadlockTimeout"))

    @deadlock_timeout.setter
    def deadlock_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de06356f491efdf8ee9e6856971bbe3b723030300d3c58ed31e766b1757eafe9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deadlockTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultToastCompression")
    def default_toast_compression(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultToastCompression"))

    @default_toast_compression.setter
    def default_toast_compression(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73ebbe5188bca46451fe5d8822638d348d6eb864f47e78c4299a3402c7998da2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultToastCompression", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="idleInTransactionSessionTimeout")
    def idle_in_transaction_session_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "idleInTransactionSessionTimeout"))

    @idle_in_transaction_session_timeout.setter
    def idle_in_transaction_session_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6dba37e80f1d633dc0ff7740e34d3436a607e8533fd984b35db99f9e51aca01c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "idleInTransactionSessionTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipFilter")
    def ip_filter(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ipFilter"))

    @ip_filter.setter
    def ip_filter(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__697351eead8e5b99283b4f51a672c2c230c8a65b858c6d540100961543d869e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipFilter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jit")
    def jit(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "jit"))

    @jit.setter
    def jit(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41882650008f06177862191d7760a830e068e667281ec52a1e1549a31852c796)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logAutovacuumMinDuration")
    def log_autovacuum_min_duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "logAutovacuumMinDuration"))

    @log_autovacuum_min_duration.setter
    def log_autovacuum_min_duration(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e82677a9e7af4b821512bc43ce8271842e49c2228e0a3847da8a3734cde323b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logAutovacuumMinDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logErrorVerbosity")
    def log_error_verbosity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logErrorVerbosity"))

    @log_error_verbosity.setter
    def log_error_verbosity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8880c1644800b0855d35ec4d3c944aecdfb9ad4087b81e8feea0006a6bf3a82)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logErrorVerbosity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logLinePrefix")
    def log_line_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logLinePrefix"))

    @log_line_prefix.setter
    def log_line_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__467136c784cb8d1bfbb9509da43f5ce9829d28b93ab2fa476f0cfafb238d1b7d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logLinePrefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logMinDurationStatement")
    def log_min_duration_statement(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "logMinDurationStatement"))

    @log_min_duration_statement.setter
    def log_min_duration_statement(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0cecd85bcbe97926ecd7cca39a7e4dda8834f2effc7babce590dbcc9a6602c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logMinDurationStatement", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logTempFiles")
    def log_temp_files(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "logTempFiles"))

    @log_temp_files.setter
    def log_temp_files(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de9268535c04a79b1d0411a6b438165d5304e769b7cdd4242e9d9c82424bf5d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logTempFiles", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxConnections")
    def max_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxConnections"))

    @max_connections.setter
    def max_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c34bafe7ac41fade6c3dd59c8fa03a2afbbc6f85746b5097e7f753f4547ea367)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxFilesPerProcess")
    def max_files_per_process(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxFilesPerProcess"))

    @max_files_per_process.setter
    def max_files_per_process(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cdd98a86086d80cb220e3ecc3418eae2ccdcc18f32fac6371f2ec091ee3ce789)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxFilesPerProcess", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxLocksPerTransaction")
    def max_locks_per_transaction(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxLocksPerTransaction"))

    @max_locks_per_transaction.setter
    def max_locks_per_transaction(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f27ad9b336fa914b7f4988f5d7ceac0d1e092d4c2b6e57b36677e6a228f429a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxLocksPerTransaction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxLogicalReplicationWorkers")
    def max_logical_replication_workers(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxLogicalReplicationWorkers"))

    @max_logical_replication_workers.setter
    def max_logical_replication_workers(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c279b6eac7f28b6d7389be2a71083aea90c51c198613f8a0c6520b9a6ab6d73)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxLogicalReplicationWorkers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxParallelWorkers")
    def max_parallel_workers(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxParallelWorkers"))

    @max_parallel_workers.setter
    def max_parallel_workers(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c91ce9226feb4c2977dcb3017dbf66a49c371d8cdf19486236017558a0661a4a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxParallelWorkers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxParallelWorkersPerGather")
    def max_parallel_workers_per_gather(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxParallelWorkersPerGather"))

    @max_parallel_workers_per_gather.setter
    def max_parallel_workers_per_gather(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2bc487be24a34828a0eefb536e39c65556cebeb32288b19b1ae34785b056a055)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxParallelWorkersPerGather", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxPredLocksPerTransaction")
    def max_pred_locks_per_transaction(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxPredLocksPerTransaction"))

    @max_pred_locks_per_transaction.setter
    def max_pred_locks_per_transaction(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d66eec8374e9b3dfa88317c48088aa40fc980255ae534f0d0d88f19e6d33681)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxPredLocksPerTransaction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxPreparedTransactions")
    def max_prepared_transactions(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxPreparedTransactions"))

    @max_prepared_transactions.setter
    def max_prepared_transactions(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de4edb189d4acf6c6bf2387f5a6c015e074a86b1230cf99fd46099dc0a6c4e68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxPreparedTransactions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxReplicationSlots")
    def max_replication_slots(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxReplicationSlots"))

    @max_replication_slots.setter
    def max_replication_slots(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6454aeeb2e612fdcdfce7dcb2b1c2792da09410760d4b4473eba6ce4edc6310)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxReplicationSlots", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxSlotWalKeepSize")
    def max_slot_wal_keep_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxSlotWalKeepSize"))

    @max_slot_wal_keep_size.setter
    def max_slot_wal_keep_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f019073bd42fc4fb9dd0e0b54f133e32c67aa3b2361c9fd2938cb96cd9e43db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxSlotWalKeepSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxStackDepth")
    def max_stack_depth(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxStackDepth"))

    @max_stack_depth.setter
    def max_stack_depth(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b405ac3b80bbd9ef2d693b6d4295c369a3356bb9beee08b413d5f87c324d5b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxStackDepth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxStandbyArchiveDelay")
    def max_standby_archive_delay(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxStandbyArchiveDelay"))

    @max_standby_archive_delay.setter
    def max_standby_archive_delay(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__155ade29e0811bc668c05c926468f7bf5296983f586f8ae29bde0aeba831fc5c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxStandbyArchiveDelay", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxStandbyStreamingDelay")
    def max_standby_streaming_delay(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxStandbyStreamingDelay"))

    @max_standby_streaming_delay.setter
    def max_standby_streaming_delay(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1c986690e191392b25c5b73b4f4f8ddfcf47cff91b1892b7b4bcf0e5b32aae7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxStandbyStreamingDelay", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxSyncWorkersPerSubscription")
    def max_sync_workers_per_subscription(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxSyncWorkersPerSubscription"))

    @max_sync_workers_per_subscription.setter
    def max_sync_workers_per_subscription(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b7bad3f8fc9f998368f6d88dea78ac56390331ecb34b4988bb2073240532691)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxSyncWorkersPerSubscription", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxWalSenders")
    def max_wal_senders(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxWalSenders"))

    @max_wal_senders.setter
    def max_wal_senders(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bfbc4d3406b62bcf9e7516d2e9e3d6ea7c21a9e5d9c18b45d299aeb17ba91ec2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxWalSenders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxWorkerProcesses")
    def max_worker_processes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxWorkerProcesses"))

    @max_worker_processes.setter
    def max_worker_processes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e948928e818da004176e363a2f0f2908db9b0ca2dc562efd6a932fd7ade5f0c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxWorkerProcesses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passwordEncryption")
    def password_encryption(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordEncryption"))

    @password_encryption.setter
    def password_encryption(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6097c67500ebbf2161ac4c0f362f0cdd35e8a2bbd76d01dd9ada7d7d9ec618fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordEncryption", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pgPartmanBgwInterval")
    def pg_partman_bgw_interval(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "pgPartmanBgwInterval"))

    @pg_partman_bgw_interval.setter
    def pg_partman_bgw_interval(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e7c39d3398b89ecbde622d25d90b6c1a7c033dbecc8bd3b4ba1f10c9b8144f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pgPartmanBgwInterval", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pgPartmanBgwRole")
    def pg_partman_bgw_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pgPartmanBgwRole"))

    @pg_partman_bgw_role.setter
    def pg_partman_bgw_role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__626c47c64eb8f096c0e31d3afb2c0748c087c018ae25b94d949dee44878bce38)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pgPartmanBgwRole", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pgStatMonitorEnable")
    def pg_stat_monitor_enable(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "pgStatMonitorEnable"))

    @pg_stat_monitor_enable.setter
    def pg_stat_monitor_enable(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0bffe3527ba3889a568bce7c605725e472374da1d243afd472b8096468cf50e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pgStatMonitorEnable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pgStatMonitorPgsmEnableQueryPlan")
    def pg_stat_monitor_pgsm_enable_query_plan(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "pgStatMonitorPgsmEnableQueryPlan"))

    @pg_stat_monitor_pgsm_enable_query_plan.setter
    def pg_stat_monitor_pgsm_enable_query_plan(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5523ea201642e452f29002110d74b8b38efc4324dc5b669c7ee3c267c7b1cb07)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pgStatMonitorPgsmEnableQueryPlan", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pgStatMonitorPgsmMaxBuckets")
    def pg_stat_monitor_pgsm_max_buckets(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "pgStatMonitorPgsmMaxBuckets"))

    @pg_stat_monitor_pgsm_max_buckets.setter
    def pg_stat_monitor_pgsm_max_buckets(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb684ed91e21c6f7f74e81bdef8bf2d46eaa3480e927af8848a0adf8b2990be9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pgStatMonitorPgsmMaxBuckets", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pgStatStatementsTrack")
    def pg_stat_statements_track(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pgStatStatementsTrack"))

    @pg_stat_statements_track.setter
    def pg_stat_statements_track(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e670dd8e54887ee6075b3d7a487edc7d4c6b541ff5c00564faca1ba4fb7262c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pgStatStatementsTrack", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__af63b1953469fa77f074a386cbdb4d14d32a7832bc188f6f31b113b817ded912)
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
            type_hints = typing.get_type_hints(_typecheckingstub__82264e7ac32c533f8abc9673cd204798ae0fc1152b2a7fa39c0b72e00b689f27)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceLog", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sharedBuffersPercentage")
    def shared_buffers_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sharedBuffersPercentage"))

    @shared_buffers_percentage.setter
    def shared_buffers_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65f9cce4b47ad1802da63c41840db80ff48caa13fe45cc2320e8fc370bca7618)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sharedBuffersPercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="synchronousReplication")
    def synchronous_replication(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "synchronousReplication"))

    @synchronous_replication.setter
    def synchronous_replication(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__252938d2dbbcf472c760d211c8c1c9f4a70fb4fbe81a107143f04e7501063cb8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "synchronousReplication", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tempFileLimit")
    def temp_file_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tempFileLimit"))

    @temp_file_limit.setter
    def temp_file_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__864f11b50159d92edb254f40b28c601f4f2f8fbfa2a544ef89226e710ab8f55b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tempFileLimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timezone")
    def timezone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timezone"))

    @timezone.setter
    def timezone(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd8274d99148593585db96cd1e114dcd40f8f7ed508669b1614ee8207f47d06d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timezone", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="trackActivityQuerySize")
    def track_activity_query_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "trackActivityQuerySize"))

    @track_activity_query_size.setter
    def track_activity_query_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3de24251f7f91e60882212985b4e65c3b8d77594634528744daf6802444ac070)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "trackActivityQuerySize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="trackCommitTimestamp")
    def track_commit_timestamp(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "trackCommitTimestamp"))

    @track_commit_timestamp.setter
    def track_commit_timestamp(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00c081c35a8f2680b79c4f6761085903f7ee3216bb92d9a3d36225cb3154fd52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "trackCommitTimestamp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="trackFunctions")
    def track_functions(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "trackFunctions"))

    @track_functions.setter
    def track_functions(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c44285a408be26c3929f8e516cee6048ec7efe0d3edf360cc492ef4dd6820bea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "trackFunctions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="trackIoTiming")
    def track_io_timing(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "trackIoTiming"))

    @track_io_timing.setter
    def track_io_timing(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a7c5008dfef3f45f791265f72267cff9cedc455080c735a9ba8e3bbe4e0456e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "trackIoTiming", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="variant")
    def variant(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "variant"))

    @variant.setter
    def variant(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd80543a93be6e541c5b8705506b844f3cf06d8b8eee1b339788dfca1d295fb9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "variant", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc64b26a05a3063a578b7f0bc6817c087f93f1eeaf4212422d39a4617ee30948)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="walSenderTimeout")
    def wal_sender_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "walSenderTimeout"))

    @wal_sender_timeout.setter
    def wal_sender_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e64f775ba944c88c15b262537a35bb9c5ab2af09ce61b822a8fd619261008fef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "walSenderTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="walWriterDelay")
    def wal_writer_delay(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "walWriterDelay"))

    @wal_writer_delay.setter
    def wal_writer_delay(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d438f9a80427b9879f1e5fa484c2d14d14ad544bf655dc9b83603891fc2e17d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "walWriterDelay", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workMem")
    def work_mem(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "workMem"))

    @work_mem.setter
    def work_mem(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f798d46e03ca466204e4eaf2c9e6caffb185597aeb92e958612f1f127c564ea0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workMem", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ManagedDatabasePostgresqlProperties]:
        return typing.cast(typing.Optional[ManagedDatabasePostgresqlProperties], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabasePostgresqlProperties],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__520a338727eb7d856b3b656bc7f18cdedc438461e851ce535758677490196542)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabasePostgresql.ManagedDatabasePostgresqlPropertiesPgaudit",
    jsii_struct_bases=[],
    name_mapping={
        "feature_enabled": "featureEnabled",
        "log": "log",
        "log_catalog": "logCatalog",
        "log_client": "logClient",
        "log_level": "logLevel",
        "log_max_string_length": "logMaxStringLength",
        "log_nested_statements": "logNestedStatements",
        "log_parameter": "logParameter",
        "log_parameter_max_size": "logParameterMaxSize",
        "log_relation": "logRelation",
        "log_rows": "logRows",
        "log_statement": "logStatement",
        "log_statement_once": "logStatementOnce",
        "role": "role",
    },
)
class ManagedDatabasePostgresqlPropertiesPgaudit:
    def __init__(
        self,
        *,
        feature_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        log: typing.Optional[typing.Sequence[builtins.str]] = None,
        log_catalog: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        log_client: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        log_level: typing.Optional[builtins.str] = None,
        log_max_string_length: typing.Optional[jsii.Number] = None,
        log_nested_statements: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        log_parameter: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        log_parameter_max_size: typing.Optional[jsii.Number] = None,
        log_relation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        log_rows: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        log_statement: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        log_statement_once: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        role: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param feature_enabled: Enable pgaudit extension. Enable pgaudit extension. When enabled, pgaudit extension will be automatically installed.Otherwise, extension will be uninstalled but auditing configurations will be preserved. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#feature_enabled ManagedDatabasePostgresql#feature_enabled}
        :param log: Specifies which classes of statements will be logged by session audit logging. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log ManagedDatabasePostgresql#log}
        :param log_catalog: Specifies that session logging should be enabled in the casewhere all relations in a statement are in pg_catalog. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_catalog ManagedDatabasePostgresql#log_catalog}
        :param log_client: Specifies whether log messages will be visible to a client process such as psql. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_client ManagedDatabasePostgresql#log_client}
        :param log_level: Specifies the log level that will be used for log entries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_level ManagedDatabasePostgresql#log_level}
        :param log_max_string_length: Crop parameters representation and whole statements if they exceed this threshold. A (default) value of -1 disable the truncation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_max_string_length ManagedDatabasePostgresql#log_max_string_length}
        :param log_nested_statements: This GUC allows to turn off logging nested statements, that is, statements that are executed as part of another ExecutorRun. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_nested_statements ManagedDatabasePostgresql#log_nested_statements}
        :param log_parameter: Specifies that audit logging should include the parameters that were passed with the statement. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_parameter ManagedDatabasePostgresql#log_parameter}
        :param log_parameter_max_size: Specifies that parameter values longer than this setting (in bytes) should not be logged, but replaced with . Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_parameter_max_size ManagedDatabasePostgresql#log_parameter_max_size}
        :param log_relation: Specifies whether session audit logging should create a separate log entry for each relation (TABLE, VIEW, etc.) referenced in a SELECT or DML statement. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_relation ManagedDatabasePostgresql#log_relation}
        :param log_rows: Specifies that audit logging should include the rows retrieved or affected by a statement. When enabled the rows field will be included after the parameter field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_rows ManagedDatabasePostgresql#log_rows}
        :param log_statement: Specifies whether logging will include the statement text and parameters (if enabled). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_statement ManagedDatabasePostgresql#log_statement}
        :param log_statement_once: Specifies whether logging will include the statement text and parameters with the first log entry for a statement/substatement combination or with every entry. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_statement_once ManagedDatabasePostgresql#log_statement_once}
        :param role: Specifies the master role to use for object audit logging. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#role ManagedDatabasePostgresql#role}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ceddef9157916dec3e9a0146d7eedd65e39272ad64a94090ac97ce9eb4e638a6)
            check_type(argname="argument feature_enabled", value=feature_enabled, expected_type=type_hints["feature_enabled"])
            check_type(argname="argument log", value=log, expected_type=type_hints["log"])
            check_type(argname="argument log_catalog", value=log_catalog, expected_type=type_hints["log_catalog"])
            check_type(argname="argument log_client", value=log_client, expected_type=type_hints["log_client"])
            check_type(argname="argument log_level", value=log_level, expected_type=type_hints["log_level"])
            check_type(argname="argument log_max_string_length", value=log_max_string_length, expected_type=type_hints["log_max_string_length"])
            check_type(argname="argument log_nested_statements", value=log_nested_statements, expected_type=type_hints["log_nested_statements"])
            check_type(argname="argument log_parameter", value=log_parameter, expected_type=type_hints["log_parameter"])
            check_type(argname="argument log_parameter_max_size", value=log_parameter_max_size, expected_type=type_hints["log_parameter_max_size"])
            check_type(argname="argument log_relation", value=log_relation, expected_type=type_hints["log_relation"])
            check_type(argname="argument log_rows", value=log_rows, expected_type=type_hints["log_rows"])
            check_type(argname="argument log_statement", value=log_statement, expected_type=type_hints["log_statement"])
            check_type(argname="argument log_statement_once", value=log_statement_once, expected_type=type_hints["log_statement_once"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if feature_enabled is not None:
            self._values["feature_enabled"] = feature_enabled
        if log is not None:
            self._values["log"] = log
        if log_catalog is not None:
            self._values["log_catalog"] = log_catalog
        if log_client is not None:
            self._values["log_client"] = log_client
        if log_level is not None:
            self._values["log_level"] = log_level
        if log_max_string_length is not None:
            self._values["log_max_string_length"] = log_max_string_length
        if log_nested_statements is not None:
            self._values["log_nested_statements"] = log_nested_statements
        if log_parameter is not None:
            self._values["log_parameter"] = log_parameter
        if log_parameter_max_size is not None:
            self._values["log_parameter_max_size"] = log_parameter_max_size
        if log_relation is not None:
            self._values["log_relation"] = log_relation
        if log_rows is not None:
            self._values["log_rows"] = log_rows
        if log_statement is not None:
            self._values["log_statement"] = log_statement
        if log_statement_once is not None:
            self._values["log_statement_once"] = log_statement_once
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def feature_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable pgaudit extension.

        Enable pgaudit extension. When enabled, pgaudit extension will be automatically installed.Otherwise, extension will be uninstalled but auditing configurations will be preserved.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#feature_enabled ManagedDatabasePostgresql#feature_enabled}
        '''
        result = self._values.get("feature_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def log(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies which classes of statements will be logged by session audit logging.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log ManagedDatabasePostgresql#log}
        '''
        result = self._values.get("log")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def log_catalog(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies that session logging should be enabled in the casewhere all relations in a statement are in pg_catalog.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_catalog ManagedDatabasePostgresql#log_catalog}
        '''
        result = self._values.get("log_catalog")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def log_client(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies whether log messages will be visible to a client process such as psql.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_client ManagedDatabasePostgresql#log_client}
        '''
        result = self._values.get("log_client")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def log_level(self) -> typing.Optional[builtins.str]:
        '''Specifies the log level that will be used for log entries.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_level ManagedDatabasePostgresql#log_level}
        '''
        result = self._values.get("log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_max_string_length(self) -> typing.Optional[jsii.Number]:
        '''Crop parameters representation and whole statements if they exceed this threshold. A (default) value of -1 disable the truncation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_max_string_length ManagedDatabasePostgresql#log_max_string_length}
        '''
        result = self._values.get("log_max_string_length")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def log_nested_statements(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''This GUC allows to turn off logging nested statements, that is, statements that are executed as part of another ExecutorRun.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_nested_statements ManagedDatabasePostgresql#log_nested_statements}
        '''
        result = self._values.get("log_nested_statements")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def log_parameter(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies that audit logging should include the parameters that were passed with the statement.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_parameter ManagedDatabasePostgresql#log_parameter}
        '''
        result = self._values.get("log_parameter")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def log_parameter_max_size(self) -> typing.Optional[jsii.Number]:
        '''Specifies that parameter values longer than this setting (in bytes) should not be logged, but replaced with .

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_parameter_max_size ManagedDatabasePostgresql#log_parameter_max_size}
        '''
        result = self._values.get("log_parameter_max_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def log_relation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies whether session audit logging should create a separate log entry for each relation (TABLE, VIEW, etc.) referenced in a SELECT or DML statement.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_relation ManagedDatabasePostgresql#log_relation}
        '''
        result = self._values.get("log_relation")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def log_rows(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies that audit logging should include the rows retrieved or affected by a statement.

        When enabled the rows field will be included after the parameter field.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_rows ManagedDatabasePostgresql#log_rows}
        '''
        result = self._values.get("log_rows")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def log_statement(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies whether logging will include the statement text and parameters (if enabled).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_statement ManagedDatabasePostgresql#log_statement}
        '''
        result = self._values.get("log_statement")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def log_statement_once(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies whether logging will include the statement text and parameters with the first log entry for a statement/substatement combination or with every entry.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#log_statement_once ManagedDatabasePostgresql#log_statement_once}
        '''
        result = self._values.get("log_statement_once")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def role(self) -> typing.Optional[builtins.str]:
        '''Specifies the master role to use for object audit logging.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#role ManagedDatabasePostgresql#role}
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabasePostgresqlPropertiesPgaudit(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabasePostgresqlPropertiesPgauditOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabasePostgresql.ManagedDatabasePostgresqlPropertiesPgauditOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__464ca482964593b0d9e773fbd6dc07d727fc64f0af5ecb299985f5926fe9926f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetFeatureEnabled")
    def reset_feature_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFeatureEnabled", []))

    @jsii.member(jsii_name="resetLog")
    def reset_log(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLog", []))

    @jsii.member(jsii_name="resetLogCatalog")
    def reset_log_catalog(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogCatalog", []))

    @jsii.member(jsii_name="resetLogClient")
    def reset_log_client(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogClient", []))

    @jsii.member(jsii_name="resetLogLevel")
    def reset_log_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogLevel", []))

    @jsii.member(jsii_name="resetLogMaxStringLength")
    def reset_log_max_string_length(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogMaxStringLength", []))

    @jsii.member(jsii_name="resetLogNestedStatements")
    def reset_log_nested_statements(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogNestedStatements", []))

    @jsii.member(jsii_name="resetLogParameter")
    def reset_log_parameter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogParameter", []))

    @jsii.member(jsii_name="resetLogParameterMaxSize")
    def reset_log_parameter_max_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogParameterMaxSize", []))

    @jsii.member(jsii_name="resetLogRelation")
    def reset_log_relation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogRelation", []))

    @jsii.member(jsii_name="resetLogRows")
    def reset_log_rows(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogRows", []))

    @jsii.member(jsii_name="resetLogStatement")
    def reset_log_statement(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogStatement", []))

    @jsii.member(jsii_name="resetLogStatementOnce")
    def reset_log_statement_once(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogStatementOnce", []))

    @jsii.member(jsii_name="resetRole")
    def reset_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRole", []))

    @builtins.property
    @jsii.member(jsii_name="featureEnabledInput")
    def feature_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "featureEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="logCatalogInput")
    def log_catalog_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "logCatalogInput"))

    @builtins.property
    @jsii.member(jsii_name="logClientInput")
    def log_client_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "logClientInput"))

    @builtins.property
    @jsii.member(jsii_name="logInput")
    def log_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "logInput"))

    @builtins.property
    @jsii.member(jsii_name="logLevelInput")
    def log_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logLevelInput"))

    @builtins.property
    @jsii.member(jsii_name="logMaxStringLengthInput")
    def log_max_string_length_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "logMaxStringLengthInput"))

    @builtins.property
    @jsii.member(jsii_name="logNestedStatementsInput")
    def log_nested_statements_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "logNestedStatementsInput"))

    @builtins.property
    @jsii.member(jsii_name="logParameterInput")
    def log_parameter_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "logParameterInput"))

    @builtins.property
    @jsii.member(jsii_name="logParameterMaxSizeInput")
    def log_parameter_max_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "logParameterMaxSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="logRelationInput")
    def log_relation_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "logRelationInput"))

    @builtins.property
    @jsii.member(jsii_name="logRowsInput")
    def log_rows_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "logRowsInput"))

    @builtins.property
    @jsii.member(jsii_name="logStatementInput")
    def log_statement_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "logStatementInput"))

    @builtins.property
    @jsii.member(jsii_name="logStatementOnceInput")
    def log_statement_once_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "logStatementOnceInput"))

    @builtins.property
    @jsii.member(jsii_name="roleInput")
    def role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleInput"))

    @builtins.property
    @jsii.member(jsii_name="featureEnabled")
    def feature_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "featureEnabled"))

    @feature_enabled.setter
    def feature_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbc9b433486d9bb7d1609f8a5132fe20e78e3c0f5c752c920af98c9e7de822e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "featureEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="log")
    def log(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "log"))

    @log.setter
    def log(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d42260ac22d8d15c9b3103737e859b27c183e431b97bb47c1a2cb32f3ed5232)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "log", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logCatalog")
    def log_catalog(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "logCatalog"))

    @log_catalog.setter
    def log_catalog(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2e01677919856bac39b08212f3a95dd303d385856121a095ea097d8627f226c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logCatalog", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logClient")
    def log_client(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "logClient"))

    @log_client.setter
    def log_client(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e85f22f31e95a82529a0182521fe54e51b95cc55171651188c909327a7cda591)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logClient", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logLevel")
    def log_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logLevel"))

    @log_level.setter
    def log_level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6b17d3021c92b2d92d85de2aa175a78950f3edb6630682261da5f055c1bd5fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logLevel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logMaxStringLength")
    def log_max_string_length(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "logMaxStringLength"))

    @log_max_string_length.setter
    def log_max_string_length(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5289994fd6001603188306c40f7d768c770c8b24ac29b201562957f408410db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logMaxStringLength", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logNestedStatements")
    def log_nested_statements(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "logNestedStatements"))

    @log_nested_statements.setter
    def log_nested_statements(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79ba090e99b2ef9d8ed41d6e44ce66470ddcefe1c32d027e0463228cc96d6685)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logNestedStatements", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logParameter")
    def log_parameter(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "logParameter"))

    @log_parameter.setter
    def log_parameter(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce37f1d5b091e3bef4d0ceef4d0bd3d6e8c9d020ab9434f480ee27f96db29e67)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logParameter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logParameterMaxSize")
    def log_parameter_max_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "logParameterMaxSize"))

    @log_parameter_max_size.setter
    def log_parameter_max_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c637be970804d44fa68b279ab066787132117df8c2cf404436ab10521d07f616)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logParameterMaxSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logRelation")
    def log_relation(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "logRelation"))

    @log_relation.setter
    def log_relation(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc52cfab3594e81eeda4e6dbe187d1c4a2e5e035649775d384a4fa2160772234)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logRelation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logRows")
    def log_rows(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "logRows"))

    @log_rows.setter
    def log_rows(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5633b1a7e74d6a2c0b066feebb76ab2f159c97dc1f56b47afd171dcd2483c435)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logRows", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logStatement")
    def log_statement(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "logStatement"))

    @log_statement.setter
    def log_statement(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7524618da50a3107d8f6d8db59750b885f5eee1808ede6defa9d3b53991a34c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logStatement", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logStatementOnce")
    def log_statement_once(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "logStatementOnce"))

    @log_statement_once.setter
    def log_statement_once(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06eb0435d6455a516aceb5fbf3ecdf75f11263abc7e24b00ccbb15d60e94be95)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logStatementOnce", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @role.setter
    def role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f6a3198b0c922afc3600eaa8ef6e6ba0ab8816525f10d28f67fd6c2be9e00e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "role", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabasePostgresqlPropertiesPgaudit]:
        return typing.cast(typing.Optional[ManagedDatabasePostgresqlPropertiesPgaudit], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabasePostgresqlPropertiesPgaudit],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8481bc4e1262a1119a3da0eb3f4597c912a4ac32d1819f992cc4c470b3e8272)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabasePostgresql.ManagedDatabasePostgresqlPropertiesPgbouncer",
    jsii_struct_bases=[],
    name_mapping={
        "autodb_idle_timeout": "autodbIdleTimeout",
        "autodb_max_db_connections": "autodbMaxDbConnections",
        "autodb_pool_mode": "autodbPoolMode",
        "autodb_pool_size": "autodbPoolSize",
        "ignore_startup_parameters": "ignoreStartupParameters",
        "max_prepared_statements": "maxPreparedStatements",
        "min_pool_size": "minPoolSize",
        "server_idle_timeout": "serverIdleTimeout",
        "server_lifetime": "serverLifetime",
        "server_reset_query_always": "serverResetQueryAlways",
    },
)
class ManagedDatabasePostgresqlPropertiesPgbouncer:
    def __init__(
        self,
        *,
        autodb_idle_timeout: typing.Optional[jsii.Number] = None,
        autodb_max_db_connections: typing.Optional[jsii.Number] = None,
        autodb_pool_mode: typing.Optional[builtins.str] = None,
        autodb_pool_size: typing.Optional[jsii.Number] = None,
        ignore_startup_parameters: typing.Optional[typing.Sequence[builtins.str]] = None,
        max_prepared_statements: typing.Optional[jsii.Number] = None,
        min_pool_size: typing.Optional[jsii.Number] = None,
        server_idle_timeout: typing.Optional[jsii.Number] = None,
        server_lifetime: typing.Optional[jsii.Number] = None,
        server_reset_query_always: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param autodb_idle_timeout: If the automatically created database pools have been unused this many seconds, they are freed. If 0 then timeout is disabled. [seconds]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autodb_idle_timeout ManagedDatabasePostgresql#autodb_idle_timeout}
        :param autodb_max_db_connections: Do not allow more than this many server connections per database (regardless of user). Setting it to 0 means unlimited. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autodb_max_db_connections ManagedDatabasePostgresql#autodb_max_db_connections}
        :param autodb_pool_mode: PGBouncer pool mode. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autodb_pool_mode ManagedDatabasePostgresql#autodb_pool_mode}
        :param autodb_pool_size: If non-zero then create automatically a pool of that size per user when a pool doesn't exist. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autodb_pool_size ManagedDatabasePostgresql#autodb_pool_size}
        :param ignore_startup_parameters: List of parameters to ignore when given in startup packet. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#ignore_startup_parameters ManagedDatabasePostgresql#ignore_startup_parameters}
        :param max_prepared_statements: PgBouncer tracks protocol-level named prepared statements related commands sent by the client in transaction and statement pooling modes when max_prepared_statements is set to a non-zero value. Setting it to 0 disables prepared statements. max_prepared_statements defaults to 100, and its maximum is 3000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_prepared_statements ManagedDatabasePostgresql#max_prepared_statements}
        :param min_pool_size: Add more server connections to pool if below this number. Improves behavior when usual load comes suddenly back after period of total inactivity. The value is effectively capped at the pool size. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#min_pool_size ManagedDatabasePostgresql#min_pool_size}
        :param server_idle_timeout: If a server connection has been idle more than this many seconds it will be dropped. If 0 then timeout is disabled. [seconds]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#server_idle_timeout ManagedDatabasePostgresql#server_idle_timeout}
        :param server_lifetime: The pooler will close an unused server connection that has been connected longer than this. [seconds]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#server_lifetime ManagedDatabasePostgresql#server_lifetime}
        :param server_reset_query_always: Run server_reset_query (DISCARD ALL) in all pooling modes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#server_reset_query_always ManagedDatabasePostgresql#server_reset_query_always}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2862abffc43a442ad2bff1c444cf98fb770986970925fafb7cc295e2cc45a9b9)
            check_type(argname="argument autodb_idle_timeout", value=autodb_idle_timeout, expected_type=type_hints["autodb_idle_timeout"])
            check_type(argname="argument autodb_max_db_connections", value=autodb_max_db_connections, expected_type=type_hints["autodb_max_db_connections"])
            check_type(argname="argument autodb_pool_mode", value=autodb_pool_mode, expected_type=type_hints["autodb_pool_mode"])
            check_type(argname="argument autodb_pool_size", value=autodb_pool_size, expected_type=type_hints["autodb_pool_size"])
            check_type(argname="argument ignore_startup_parameters", value=ignore_startup_parameters, expected_type=type_hints["ignore_startup_parameters"])
            check_type(argname="argument max_prepared_statements", value=max_prepared_statements, expected_type=type_hints["max_prepared_statements"])
            check_type(argname="argument min_pool_size", value=min_pool_size, expected_type=type_hints["min_pool_size"])
            check_type(argname="argument server_idle_timeout", value=server_idle_timeout, expected_type=type_hints["server_idle_timeout"])
            check_type(argname="argument server_lifetime", value=server_lifetime, expected_type=type_hints["server_lifetime"])
            check_type(argname="argument server_reset_query_always", value=server_reset_query_always, expected_type=type_hints["server_reset_query_always"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if autodb_idle_timeout is not None:
            self._values["autodb_idle_timeout"] = autodb_idle_timeout
        if autodb_max_db_connections is not None:
            self._values["autodb_max_db_connections"] = autodb_max_db_connections
        if autodb_pool_mode is not None:
            self._values["autodb_pool_mode"] = autodb_pool_mode
        if autodb_pool_size is not None:
            self._values["autodb_pool_size"] = autodb_pool_size
        if ignore_startup_parameters is not None:
            self._values["ignore_startup_parameters"] = ignore_startup_parameters
        if max_prepared_statements is not None:
            self._values["max_prepared_statements"] = max_prepared_statements
        if min_pool_size is not None:
            self._values["min_pool_size"] = min_pool_size
        if server_idle_timeout is not None:
            self._values["server_idle_timeout"] = server_idle_timeout
        if server_lifetime is not None:
            self._values["server_lifetime"] = server_lifetime
        if server_reset_query_always is not None:
            self._values["server_reset_query_always"] = server_reset_query_always

    @builtins.property
    def autodb_idle_timeout(self) -> typing.Optional[jsii.Number]:
        '''If the automatically created database pools have been unused this many seconds, they are freed.

        If 0 then timeout is disabled. [seconds].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autodb_idle_timeout ManagedDatabasePostgresql#autodb_idle_timeout}
        '''
        result = self._values.get("autodb_idle_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autodb_max_db_connections(self) -> typing.Optional[jsii.Number]:
        '''Do not allow more than this many server connections per database (regardless of user).

        Setting it to 0 means unlimited.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autodb_max_db_connections ManagedDatabasePostgresql#autodb_max_db_connections}
        '''
        result = self._values.get("autodb_max_db_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autodb_pool_mode(self) -> typing.Optional[builtins.str]:
        '''PGBouncer pool mode.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autodb_pool_mode ManagedDatabasePostgresql#autodb_pool_mode}
        '''
        result = self._values.get("autodb_pool_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def autodb_pool_size(self) -> typing.Optional[jsii.Number]:
        '''If non-zero then create automatically a pool of that size per user when a pool doesn't exist.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#autodb_pool_size ManagedDatabasePostgresql#autodb_pool_size}
        '''
        result = self._values.get("autodb_pool_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ignore_startup_parameters(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of parameters to ignore when given in startup packet.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#ignore_startup_parameters ManagedDatabasePostgresql#ignore_startup_parameters}
        '''
        result = self._values.get("ignore_startup_parameters")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def max_prepared_statements(self) -> typing.Optional[jsii.Number]:
        '''PgBouncer tracks protocol-level named prepared statements related commands sent by the client in transaction and statement pooling modes when max_prepared_statements is set to a non-zero value.

        Setting it to 0 disables prepared statements. max_prepared_statements defaults to 100, and its maximum is 3000.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_prepared_statements ManagedDatabasePostgresql#max_prepared_statements}
        '''
        result = self._values.get("max_prepared_statements")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_pool_size(self) -> typing.Optional[jsii.Number]:
        '''Add more server connections to pool if below this number.

        Improves behavior when usual load comes suddenly back after period of total inactivity. The value is effectively capped at the pool size.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#min_pool_size ManagedDatabasePostgresql#min_pool_size}
        '''
        result = self._values.get("min_pool_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def server_idle_timeout(self) -> typing.Optional[jsii.Number]:
        '''If a server connection has been idle more than this many seconds it will be dropped.

        If 0 then timeout is disabled. [seconds].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#server_idle_timeout ManagedDatabasePostgresql#server_idle_timeout}
        '''
        result = self._values.get("server_idle_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def server_lifetime(self) -> typing.Optional[jsii.Number]:
        '''The pooler will close an unused server connection that has been connected longer than this. [seconds].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#server_lifetime ManagedDatabasePostgresql#server_lifetime}
        '''
        result = self._values.get("server_lifetime")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def server_reset_query_always(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Run server_reset_query (DISCARD ALL) in all pooling modes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#server_reset_query_always ManagedDatabasePostgresql#server_reset_query_always}
        '''
        result = self._values.get("server_reset_query_always")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabasePostgresqlPropertiesPgbouncer(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabasePostgresqlPropertiesPgbouncerOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabasePostgresql.ManagedDatabasePostgresqlPropertiesPgbouncerOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__61222568dada92bfef5c5725c39b1b57b38d5ceff4bb0beb3340697754fe92a8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAutodbIdleTimeout")
    def reset_autodb_idle_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutodbIdleTimeout", []))

    @jsii.member(jsii_name="resetAutodbMaxDbConnections")
    def reset_autodb_max_db_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutodbMaxDbConnections", []))

    @jsii.member(jsii_name="resetAutodbPoolMode")
    def reset_autodb_pool_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutodbPoolMode", []))

    @jsii.member(jsii_name="resetAutodbPoolSize")
    def reset_autodb_pool_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutodbPoolSize", []))

    @jsii.member(jsii_name="resetIgnoreStartupParameters")
    def reset_ignore_startup_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIgnoreStartupParameters", []))

    @jsii.member(jsii_name="resetMaxPreparedStatements")
    def reset_max_prepared_statements(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxPreparedStatements", []))

    @jsii.member(jsii_name="resetMinPoolSize")
    def reset_min_pool_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinPoolSize", []))

    @jsii.member(jsii_name="resetServerIdleTimeout")
    def reset_server_idle_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerIdleTimeout", []))

    @jsii.member(jsii_name="resetServerLifetime")
    def reset_server_lifetime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerLifetime", []))

    @jsii.member(jsii_name="resetServerResetQueryAlways")
    def reset_server_reset_query_always(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerResetQueryAlways", []))

    @builtins.property
    @jsii.member(jsii_name="autodbIdleTimeoutInput")
    def autodb_idle_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autodbIdleTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="autodbMaxDbConnectionsInput")
    def autodb_max_db_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autodbMaxDbConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="autodbPoolModeInput")
    def autodb_pool_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "autodbPoolModeInput"))

    @builtins.property
    @jsii.member(jsii_name="autodbPoolSizeInput")
    def autodb_pool_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autodbPoolSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="ignoreStartupParametersInput")
    def ignore_startup_parameters_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ignoreStartupParametersInput"))

    @builtins.property
    @jsii.member(jsii_name="maxPreparedStatementsInput")
    def max_prepared_statements_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxPreparedStatementsInput"))

    @builtins.property
    @jsii.member(jsii_name="minPoolSizeInput")
    def min_pool_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minPoolSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="serverIdleTimeoutInput")
    def server_idle_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "serverIdleTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="serverLifetimeInput")
    def server_lifetime_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "serverLifetimeInput"))

    @builtins.property
    @jsii.member(jsii_name="serverResetQueryAlwaysInput")
    def server_reset_query_always_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "serverResetQueryAlwaysInput"))

    @builtins.property
    @jsii.member(jsii_name="autodbIdleTimeout")
    def autodb_idle_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autodbIdleTimeout"))

    @autodb_idle_timeout.setter
    def autodb_idle_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce972406e06643c117f973486aab7e9b90c2de0a19167dcc4a91d1f67c3be224)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autodbIdleTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autodbMaxDbConnections")
    def autodb_max_db_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autodbMaxDbConnections"))

    @autodb_max_db_connections.setter
    def autodb_max_db_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f174d35ae6becea43c4005cf8d171a3f5b38e1e9ed961fd472ff71ace836a643)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autodbMaxDbConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autodbPoolMode")
    def autodb_pool_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "autodbPoolMode"))

    @autodb_pool_mode.setter
    def autodb_pool_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c89625ebfc5b1171d9adb631a22f77b877b00db92269684183b9d62d5ca000e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autodbPoolMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autodbPoolSize")
    def autodb_pool_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autodbPoolSize"))

    @autodb_pool_size.setter
    def autodb_pool_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6455db15790093dfe2a1d5908d16ee62da352ab2be9b7ed392cf201f8252bb8f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autodbPoolSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ignoreStartupParameters")
    def ignore_startup_parameters(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ignoreStartupParameters"))

    @ignore_startup_parameters.setter
    def ignore_startup_parameters(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffa7e3d14d9a55b881ea76e07dd347874b2459e06c8d89905ba71ff8ffcd9791)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ignoreStartupParameters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxPreparedStatements")
    def max_prepared_statements(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxPreparedStatements"))

    @max_prepared_statements.setter
    def max_prepared_statements(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1714d88a07031186abba7bd75b3044a59c7bbe49477e83d5c20153eabd372c07)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxPreparedStatements", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minPoolSize")
    def min_pool_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minPoolSize"))

    @min_pool_size.setter
    def min_pool_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0433626c85344b9838a6b512cde678d20b02d3792eaa058b4de2be4bc8009851)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minPoolSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serverIdleTimeout")
    def server_idle_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "serverIdleTimeout"))

    @server_idle_timeout.setter
    def server_idle_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f80b710e775e8ab14f4e4ab50e163f888e70bd3108cf6935ce365619a87b38b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverIdleTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serverLifetime")
    def server_lifetime(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "serverLifetime"))

    @server_lifetime.setter
    def server_lifetime(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc7d78e16970caa5cec1af6076b323b5bc850f89776553fc6522730bc5750ea1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverLifetime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serverResetQueryAlways")
    def server_reset_query_always(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "serverResetQueryAlways"))

    @server_reset_query_always.setter
    def server_reset_query_always(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ca0d1d22fc45834d7b10e43700bebb5a67d5f752e0dced7a3b20f0282010fdf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverResetQueryAlways", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabasePostgresqlPropertiesPgbouncer]:
        return typing.cast(typing.Optional[ManagedDatabasePostgresqlPropertiesPgbouncer], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabasePostgresqlPropertiesPgbouncer],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9528ede7d75ae7969c77b9e4cec0539ada3f5505040b873b6594f6a2948a4823)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabasePostgresql.ManagedDatabasePostgresqlPropertiesPglookout",
    jsii_struct_bases=[],
    name_mapping={
        "max_failover_replication_time_lag": "maxFailoverReplicationTimeLag",
    },
)
class ManagedDatabasePostgresqlPropertiesPglookout:
    def __init__(
        self,
        *,
        max_failover_replication_time_lag: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_failover_replication_time_lag: Number of seconds of master unavailability before triggering database failover to standby. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_failover_replication_time_lag ManagedDatabasePostgresql#max_failover_replication_time_lag}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd81ae3f527ba52eaf4f2d07e7187afc3b2328ed800858a2364717bdfe0081a9)
            check_type(argname="argument max_failover_replication_time_lag", value=max_failover_replication_time_lag, expected_type=type_hints["max_failover_replication_time_lag"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if max_failover_replication_time_lag is not None:
            self._values["max_failover_replication_time_lag"] = max_failover_replication_time_lag

    @builtins.property
    def max_failover_replication_time_lag(self) -> typing.Optional[jsii.Number]:
        '''Number of seconds of master unavailability before triggering database failover to standby.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_failover_replication_time_lag ManagedDatabasePostgresql#max_failover_replication_time_lag}
        '''
        result = self._values.get("max_failover_replication_time_lag")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabasePostgresqlPropertiesPglookout(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabasePostgresqlPropertiesPglookoutOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabasePostgresql.ManagedDatabasePostgresqlPropertiesPglookoutOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3dc34eb16c0feb84003a8eeefbb09dab17f0a74e8b22043406c416ec43987274)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMaxFailoverReplicationTimeLag")
    def reset_max_failover_replication_time_lag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxFailoverReplicationTimeLag", []))

    @builtins.property
    @jsii.member(jsii_name="maxFailoverReplicationTimeLagInput")
    def max_failover_replication_time_lag_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxFailoverReplicationTimeLagInput"))

    @builtins.property
    @jsii.member(jsii_name="maxFailoverReplicationTimeLag")
    def max_failover_replication_time_lag(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxFailoverReplicationTimeLag"))

    @max_failover_replication_time_lag.setter
    def max_failover_replication_time_lag(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8283df738aae5d11534883b9b78ed5fef3c788a0f2073f06c598ca8dad4a6288)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxFailoverReplicationTimeLag", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabasePostgresqlPropertiesPglookout]:
        return typing.cast(typing.Optional[ManagedDatabasePostgresqlPropertiesPglookout], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabasePostgresqlPropertiesPglookout],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a46bcae58aa1cd348a1a9371df5872df78258680d3dc6748e237e8bcb3597e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabasePostgresql.ManagedDatabasePostgresqlPropertiesTimescaledb",
    jsii_struct_bases=[],
    name_mapping={"max_background_workers": "maxBackgroundWorkers"},
)
class ManagedDatabasePostgresqlPropertiesTimescaledb:
    def __init__(
        self,
        *,
        max_background_workers: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_background_workers: The number of background workers for timescaledb operations. You should configure this setting to the sum of your number of databases and the total number of concurrent background workers you want running at any given point in time. Changing this parameter causes a service restart. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_background_workers ManagedDatabasePostgresql#max_background_workers}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71c8b11f8b53026baff50866f6d74787011a28fc791f639a52c7c58b6f897621)
            check_type(argname="argument max_background_workers", value=max_background_workers, expected_type=type_hints["max_background_workers"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if max_background_workers is not None:
            self._values["max_background_workers"] = max_background_workers

    @builtins.property
    def max_background_workers(self) -> typing.Optional[jsii.Number]:
        '''The number of background workers for timescaledb operations.

        You should configure this setting to the sum of your number of databases and the total number of concurrent background workers you want running at any given point in time. Changing this parameter causes a service restart.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_postgresql#max_background_workers ManagedDatabasePostgresql#max_background_workers}
        '''
        result = self._values.get("max_background_workers")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabasePostgresqlPropertiesTimescaledb(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabasePostgresqlPropertiesTimescaledbOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabasePostgresql.ManagedDatabasePostgresqlPropertiesTimescaledbOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9bbbda2af1005991302dae40f469de426075f1f91ac642daaf1883c5b91bdead)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMaxBackgroundWorkers")
    def reset_max_background_workers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxBackgroundWorkers", []))

    @builtins.property
    @jsii.member(jsii_name="maxBackgroundWorkersInput")
    def max_background_workers_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxBackgroundWorkersInput"))

    @builtins.property
    @jsii.member(jsii_name="maxBackgroundWorkers")
    def max_background_workers(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxBackgroundWorkers"))

    @max_background_workers.setter
    def max_background_workers(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23e67c9ed6769dafb2f62a8094ada00c7c96a2d32feb06b59a6403494e68d195)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxBackgroundWorkers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabasePostgresqlPropertiesTimescaledb]:
        return typing.cast(typing.Optional[ManagedDatabasePostgresqlPropertiesTimescaledb], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabasePostgresqlPropertiesTimescaledb],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf5f49a55ef153abaf9698cc84fa23749e5a65e92b79b9473d21eb8bf61b46e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ManagedDatabasePostgresql",
    "ManagedDatabasePostgresqlComponents",
    "ManagedDatabasePostgresqlComponentsList",
    "ManagedDatabasePostgresqlComponentsOutputReference",
    "ManagedDatabasePostgresqlConfig",
    "ManagedDatabasePostgresqlNetwork",
    "ManagedDatabasePostgresqlNetworkList",
    "ManagedDatabasePostgresqlNetworkOutputReference",
    "ManagedDatabasePostgresqlNodeStates",
    "ManagedDatabasePostgresqlNodeStatesList",
    "ManagedDatabasePostgresqlNodeStatesOutputReference",
    "ManagedDatabasePostgresqlProperties",
    "ManagedDatabasePostgresqlPropertiesMigration",
    "ManagedDatabasePostgresqlPropertiesMigrationOutputReference",
    "ManagedDatabasePostgresqlPropertiesOutputReference",
    "ManagedDatabasePostgresqlPropertiesPgaudit",
    "ManagedDatabasePostgresqlPropertiesPgauditOutputReference",
    "ManagedDatabasePostgresqlPropertiesPgbouncer",
    "ManagedDatabasePostgresqlPropertiesPgbouncerOutputReference",
    "ManagedDatabasePostgresqlPropertiesPglookout",
    "ManagedDatabasePostgresqlPropertiesPglookoutOutputReference",
    "ManagedDatabasePostgresqlPropertiesTimescaledb",
    "ManagedDatabasePostgresqlPropertiesTimescaledbOutputReference",
]

publication.publish()

def _typecheckingstub__5fa809510c8f69da52891462ee8f64a2638b82c8a731ae399fb00992f714b475(
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
    network: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedDatabasePostgresqlNetwork, typing.Dict[builtins.str, typing.Any]]]]] = None,
    powered: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    properties: typing.Optional[typing.Union[ManagedDatabasePostgresqlProperties, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__571201bbf7edad587623dcace5caa1c79f3a3df20b06c10b6b082be7ace14fb8(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbbb3dfe7015b488e0b1c155e305ab2c73855a004722f839bee402b92a211b69(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedDatabasePostgresqlNetwork, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9a630d3a04b1e85d141f152306b1446a41a3f48ba0d2183d43b5587ed01b4e2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d237b647d468f025eced5d1f869c5704b40f8d693184cae12ed221d60d195bca(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2c0f77034fed7e75ffc25cc3f6dbd523c87396fc50302ef44e7a62fb55bccd3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3b522c1e2fa5f9ebcbd420abad1f5687e71bf47b1f53b8aba4d8eae624c15f8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b616f5a643e9362103bfe51d176cebeb11c5a7c116871765dc94705dfef5db23(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62ca746fcdc84d286b895013db6a84b26e62e0d3f9368d2e25f84a74a7264b94(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea14ac222a06ab006f9282ded2425426342e694303ff49e133423cad91b073d2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a040b3151c2d2f9c017cfde26b6d5f6d6408e630f17d6eab06dd6c1142465b2b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a6d4eea83ac11ab3241ebe5783562662925bb3b73987673a1f5bd2da77529d0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8e769b3f7bdff6efb6eeabc49ebfb039d0a13ba0401e55deb7401478cc6ed17(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b6a3962c8507785c3645c0b9c137496603c528b307ef84fbc81f8718c4023cd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c2bbea3f665bf989974836bb45ee48957afef39c46c57d80210f6b103ce05c8(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47d3f8173c3c000fe3926caf6e494fc6cddb15ac79d3c90a3aa20089abc9431f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ee6156235319d8ff5191af25d8e1cd5758406c4efcc4fa304274758654ff952(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9ceac319a9c2fe1f1572d1ef10795a5bd5a1de81fb1d7f4cb2ddeafe2a500c0(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83ec3ca2d809487f6fddb91dcdaf317ca8f3bb5d75792bb13ec00c6e612a3d4d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2a3104ae2962fdb60f3b3307320726a7821e29d9fe32777924514d905a12282(
    value: typing.Optional[ManagedDatabasePostgresqlComponents],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45f42ebdf030afdba0d57f507b07d90736dd58b3b6241153662af2f459e6929b(
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
    network: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedDatabasePostgresqlNetwork, typing.Dict[builtins.str, typing.Any]]]]] = None,
    powered: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    properties: typing.Optional[typing.Union[ManagedDatabasePostgresqlProperties, typing.Dict[builtins.str, typing.Any]]] = None,
    termination_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5737b331959851ea941ce795bfc130d63e5ac24633787479fac442c8d6e54407(
    *,
    family: builtins.str,
    name: builtins.str,
    type: builtins.str,
    uuid: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3b947cc2484ffb23bbafd58aa46b1a5c58cfbe888b01cf39fdab8d0ceaaf695(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a360dd571f33825fe94a1c525824de2b6b6956a728a48d2b2bdd61f6557e9e3d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__409ed79705ae4380a337e7bdf603a4ccf6d324f3ebe87024e49a3261703efc8c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e527f157396ba616a48da774b0d360a6f4aaff257be3460fdf3195f85dc119d2(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b995063066d133b223f91e57e786991501f7f6ef4db004beb2d18daeb8a65aa8(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80edead81e58717b2e65e007e33b02196e634c72111cd07c76b3f587de0f4f34(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedDatabasePostgresqlNetwork]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ba9c3d39eb1c44f562260266c493ed246f4ef7c0f77ccc1999be2f1591fea8a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d91f571ddaa3e094e149844de7c144597f83eb5aaca79f72a86cec6e58c672c3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__460f49c71e7ba9909b6c7e6724334fbc1b82ea4c0d018a7f0c42230222c6e7d8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33e124f5de2e3777f97e94b613d5f82b6b1ef5ddab810c1648eb135ec8fd4ca7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4085f8142c211fdc139fc6a946b712a7cf489b0e7bffdba7a3d0d330a30bd883(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1cccfea5a3b234cba4824b362afd23a009b35c8cfaa17da2f59f7e84412b8c0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedDatabasePostgresqlNetwork]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__970899e82ef0d640d5cb8230a8fae3d8913f2ea73e5763ea4b69f28dce477894(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3a6e4ddfd5e53444bf09e87427773d81f67b11732af145283f685298b5153e0(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1048670c405a391dca4b3526ff9ca8191643277f5ddca90dbe29dae88ed7dde3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab82061724a9896284d4068dffb73938dba936286a5eda3a45718e311572acf2(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0609ce7acd96a0e4a4ca9993aa7cda81130c9d4270192d88dd48b92d3771833f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a36fa4f1406f761c1d3d6a9cffbeed270912d248d4042be2221a9780f008111(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3da753e354ef908f815fa40182abc184639e86107112304380f0cdc2ba2755d6(
    value: typing.Optional[ManagedDatabasePostgresqlNodeStates],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6910d3220979fbcd86275a19c629678468755096ca15771873a4cee0a9a244d(
    *,
    admin_password: typing.Optional[builtins.str] = None,
    admin_username: typing.Optional[builtins.str] = None,
    automatic_utility_network_ip_filter: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    autovacuum_analyze_scale_factor: typing.Optional[jsii.Number] = None,
    autovacuum_analyze_threshold: typing.Optional[jsii.Number] = None,
    autovacuum_freeze_max_age: typing.Optional[jsii.Number] = None,
    autovacuum_max_workers: typing.Optional[jsii.Number] = None,
    autovacuum_naptime: typing.Optional[jsii.Number] = None,
    autovacuum_vacuum_cost_delay: typing.Optional[jsii.Number] = None,
    autovacuum_vacuum_cost_limit: typing.Optional[jsii.Number] = None,
    autovacuum_vacuum_scale_factor: typing.Optional[jsii.Number] = None,
    autovacuum_vacuum_threshold: typing.Optional[jsii.Number] = None,
    backup_hour: typing.Optional[jsii.Number] = None,
    backup_minute: typing.Optional[jsii.Number] = None,
    bgwriter_delay: typing.Optional[jsii.Number] = None,
    bgwriter_flush_after: typing.Optional[jsii.Number] = None,
    bgwriter_lru_maxpages: typing.Optional[jsii.Number] = None,
    bgwriter_lru_multiplier: typing.Optional[jsii.Number] = None,
    deadlock_timeout: typing.Optional[jsii.Number] = None,
    default_toast_compression: typing.Optional[builtins.str] = None,
    idle_in_transaction_session_timeout: typing.Optional[jsii.Number] = None,
    ip_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
    jit: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    log_autovacuum_min_duration: typing.Optional[jsii.Number] = None,
    log_error_verbosity: typing.Optional[builtins.str] = None,
    log_line_prefix: typing.Optional[builtins.str] = None,
    log_min_duration_statement: typing.Optional[jsii.Number] = None,
    log_temp_files: typing.Optional[jsii.Number] = None,
    max_connections: typing.Optional[jsii.Number] = None,
    max_files_per_process: typing.Optional[jsii.Number] = None,
    max_locks_per_transaction: typing.Optional[jsii.Number] = None,
    max_logical_replication_workers: typing.Optional[jsii.Number] = None,
    max_parallel_workers: typing.Optional[jsii.Number] = None,
    max_parallel_workers_per_gather: typing.Optional[jsii.Number] = None,
    max_pred_locks_per_transaction: typing.Optional[jsii.Number] = None,
    max_prepared_transactions: typing.Optional[jsii.Number] = None,
    max_replication_slots: typing.Optional[jsii.Number] = None,
    max_slot_wal_keep_size: typing.Optional[jsii.Number] = None,
    max_stack_depth: typing.Optional[jsii.Number] = None,
    max_standby_archive_delay: typing.Optional[jsii.Number] = None,
    max_standby_streaming_delay: typing.Optional[jsii.Number] = None,
    max_sync_workers_per_subscription: typing.Optional[jsii.Number] = None,
    max_wal_senders: typing.Optional[jsii.Number] = None,
    max_worker_processes: typing.Optional[jsii.Number] = None,
    migration: typing.Optional[typing.Union[ManagedDatabasePostgresqlPropertiesMigration, typing.Dict[builtins.str, typing.Any]]] = None,
    password_encryption: typing.Optional[builtins.str] = None,
    pgaudit: typing.Optional[typing.Union[ManagedDatabasePostgresqlPropertiesPgaudit, typing.Dict[builtins.str, typing.Any]]] = None,
    pgbouncer: typing.Optional[typing.Union[ManagedDatabasePostgresqlPropertiesPgbouncer, typing.Dict[builtins.str, typing.Any]]] = None,
    pglookout: typing.Optional[typing.Union[ManagedDatabasePostgresqlPropertiesPglookout, typing.Dict[builtins.str, typing.Any]]] = None,
    pg_partman_bgw_interval: typing.Optional[jsii.Number] = None,
    pg_partman_bgw_role: typing.Optional[builtins.str] = None,
    pg_stat_monitor_enable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    pg_stat_monitor_pgsm_enable_query_plan: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    pg_stat_monitor_pgsm_max_buckets: typing.Optional[jsii.Number] = None,
    pg_stat_statements_track: typing.Optional[builtins.str] = None,
    public_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    service_log: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    shared_buffers_percentage: typing.Optional[jsii.Number] = None,
    synchronous_replication: typing.Optional[builtins.str] = None,
    temp_file_limit: typing.Optional[jsii.Number] = None,
    timescaledb: typing.Optional[typing.Union[ManagedDatabasePostgresqlPropertiesTimescaledb, typing.Dict[builtins.str, typing.Any]]] = None,
    timezone: typing.Optional[builtins.str] = None,
    track_activity_query_size: typing.Optional[jsii.Number] = None,
    track_commit_timestamp: typing.Optional[builtins.str] = None,
    track_functions: typing.Optional[builtins.str] = None,
    track_io_timing: typing.Optional[builtins.str] = None,
    variant: typing.Optional[builtins.str] = None,
    version: typing.Optional[builtins.str] = None,
    wal_sender_timeout: typing.Optional[jsii.Number] = None,
    wal_writer_delay: typing.Optional[jsii.Number] = None,
    work_mem: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a22b07e9381a03b0e883019f9869d2e86afe1337164b3f40f42a65332f93686(
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

def _typecheckingstub__4c1cd6b016b3ecb62182c2c4b44e046bb68d9a8b41715e737aba7a40ab4e1637(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b35ea3bbc7714f1786f8de42e581bd9d0755d59208f76b03479dc828d8245f43(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3d28cbb40378d958cbd4f1486106b3f33d4fcb347c34e4cfe965dcbc84f6072(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ed77193308666d5a3848635d267e0d341fc69179190e0832fb81a48f162713c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a20cfd19af931dbf2350ffb4fb7828dc7d2993e5d8584a2ea8328dd07dc40bbd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fb4c8b4612f86674f4e64dd17d4ed079eecd07d785ab3841dc409b159a5e95c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0fdfd5c0b89db2edd92450c9ac53a11e1f3dd5d6210595996291472c6e80be5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b9b1430714b0435905f992cb1eaf06eb4fb5ef51814d7828c304129e683d5d1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02d3b89fb0ac87ce8d17953f5475d399eab9cc555961de1f9ce099be18c0c578(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__167fb42ea04e1b821e95e7693f524cc2b079cb09f33c63d1dbc80af39e37da15(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f46213f544334fa98fbf9d56573c816a8c7df86df770ee7114ad7be53e0e700(
    value: typing.Optional[ManagedDatabasePostgresqlPropertiesMigration],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd90a4ce70c5f20045cf9addde31aea1f70a84fb416d20f3285b17ca585a10e9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dac988dc10ea16fb9d73a6bdeae092b92a2168b105b9582d692594c7083e324f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0123a505cee8cef160f18f3716f895f89d5be5281c74f431861401dc632a8d56(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18323f68552123f0f23878838b830072c84a1d23d6ae5860aff23f18333b42ed(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a618a6d81df2b2decb7cfe9c114ac7a4b0bcb36d417cf676112d031e859d679f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c07cfc51fe1598362f03697b2b0bb8e9179fb54050e6fcfc8540c42b2e95348(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75489be2d1e658ac650ac29df5035521bb5a8082d17cfa3e793eaba19548d1b4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0635a8f3ceace0d0a4f6d5a43812c5632ab3de0c78310a9695579ff9c47d75a6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2db694007dd91d65c9b3b5ec8006f1756a4b6a931580bc7bdd21cb1086ab10b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04a29a145fc98ceabd22d030c911868b284a234fdceaf518a58943364e7d3c8d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7de5d23bbc4de2fa1bbe22a369eb8e374a5524f0bdfab27ed9c06916248712b6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__855b94ed8fdfeda7d578415566ffbb9c45fbcd24448de195e00f5cc8857772a7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8958a970bed1aabf8c821857f37ccd8cb9d367466198e4093e10cd22e96c40ec(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ad16c11d7070fcace393ac131f62b8b0e0102b11780c91c4ea8d6d4336999a0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cc1bdd7b35aa05f812e23d395f242921db855b5ddd67d2dad923b0720a01586(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4abda546f558372c3256e28f606948c39da36ec568a2210a313c740e85116faf(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__054e3bbb6bdffd7b026b893f24da5331dbf751d8d826c30bb55830fcce2bb046(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__256293bdd5d65032ca8ebf18ab8ead4e10a5b6e12bef228e145c36908d09d7d6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c01e6d51d8ebc918ea01fb3b38fda7c82e1ffb4870954be8caa2bace0da6f4b6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de06356f491efdf8ee9e6856971bbe3b723030300d3c58ed31e766b1757eafe9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73ebbe5188bca46451fe5d8822638d348d6eb864f47e78c4299a3402c7998da2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6dba37e80f1d633dc0ff7740e34d3436a607e8533fd984b35db99f9e51aca01c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__697351eead8e5b99283b4f51a672c2c230c8a65b858c6d540100961543d869e7(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41882650008f06177862191d7760a830e068e667281ec52a1e1549a31852c796(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e82677a9e7af4b821512bc43ce8271842e49c2228e0a3847da8a3734cde323b2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8880c1644800b0855d35ec4d3c944aecdfb9ad4087b81e8feea0006a6bf3a82(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__467136c784cb8d1bfbb9509da43f5ce9829d28b93ab2fa476f0cfafb238d1b7d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0cecd85bcbe97926ecd7cca39a7e4dda8834f2effc7babce590dbcc9a6602c9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de9268535c04a79b1d0411a6b438165d5304e769b7cdd4242e9d9c82424bf5d9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c34bafe7ac41fade6c3dd59c8fa03a2afbbc6f85746b5097e7f753f4547ea367(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdd98a86086d80cb220e3ecc3418eae2ccdcc18f32fac6371f2ec091ee3ce789(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f27ad9b336fa914b7f4988f5d7ceac0d1e092d4c2b6e57b36677e6a228f429a6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c279b6eac7f28b6d7389be2a71083aea90c51c198613f8a0c6520b9a6ab6d73(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c91ce9226feb4c2977dcb3017dbf66a49c371d8cdf19486236017558a0661a4a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bc487be24a34828a0eefb536e39c65556cebeb32288b19b1ae34785b056a055(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d66eec8374e9b3dfa88317c48088aa40fc980255ae534f0d0d88f19e6d33681(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de4edb189d4acf6c6bf2387f5a6c015e074a86b1230cf99fd46099dc0a6c4e68(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6454aeeb2e612fdcdfce7dcb2b1c2792da09410760d4b4473eba6ce4edc6310(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f019073bd42fc4fb9dd0e0b54f133e32c67aa3b2361c9fd2938cb96cd9e43db(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b405ac3b80bbd9ef2d693b6d4295c369a3356bb9beee08b413d5f87c324d5b1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__155ade29e0811bc668c05c926468f7bf5296983f586f8ae29bde0aeba831fc5c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1c986690e191392b25c5b73b4f4f8ddfcf47cff91b1892b7b4bcf0e5b32aae7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b7bad3f8fc9f998368f6d88dea78ac56390331ecb34b4988bb2073240532691(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bfbc4d3406b62bcf9e7516d2e9e3d6ea7c21a9e5d9c18b45d299aeb17ba91ec2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e948928e818da004176e363a2f0f2908db9b0ca2dc562efd6a932fd7ade5f0c1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6097c67500ebbf2161ac4c0f362f0cdd35e8a2bbd76d01dd9ada7d7d9ec618fc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e7c39d3398b89ecbde622d25d90b6c1a7c033dbecc8bd3b4ba1f10c9b8144f6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__626c47c64eb8f096c0e31d3afb2c0748c087c018ae25b94d949dee44878bce38(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0bffe3527ba3889a568bce7c605725e472374da1d243afd472b8096468cf50e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5523ea201642e452f29002110d74b8b38efc4324dc5b669c7ee3c267c7b1cb07(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb684ed91e21c6f7f74e81bdef8bf2d46eaa3480e927af8848a0adf8b2990be9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e670dd8e54887ee6075b3d7a487edc7d4c6b541ff5c00564faca1ba4fb7262c7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af63b1953469fa77f074a386cbdb4d14d32a7832bc188f6f31b113b817ded912(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82264e7ac32c533f8abc9673cd204798ae0fc1152b2a7fa39c0b72e00b689f27(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65f9cce4b47ad1802da63c41840db80ff48caa13fe45cc2320e8fc370bca7618(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__252938d2dbbcf472c760d211c8c1c9f4a70fb4fbe81a107143f04e7501063cb8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__864f11b50159d92edb254f40b28c601f4f2f8fbfa2a544ef89226e710ab8f55b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd8274d99148593585db96cd1e114dcd40f8f7ed508669b1614ee8207f47d06d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3de24251f7f91e60882212985b4e65c3b8d77594634528744daf6802444ac070(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00c081c35a8f2680b79c4f6761085903f7ee3216bb92d9a3d36225cb3154fd52(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c44285a408be26c3929f8e516cee6048ec7efe0d3edf360cc492ef4dd6820bea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a7c5008dfef3f45f791265f72267cff9cedc455080c735a9ba8e3bbe4e0456e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd80543a93be6e541c5b8705506b844f3cf06d8b8eee1b339788dfca1d295fb9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc64b26a05a3063a578b7f0bc6817c087f93f1eeaf4212422d39a4617ee30948(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e64f775ba944c88c15b262537a35bb9c5ab2af09ce61b822a8fd619261008fef(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d438f9a80427b9879f1e5fa484c2d14d14ad544bf655dc9b83603891fc2e17d5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f798d46e03ca466204e4eaf2c9e6caffb185597aeb92e958612f1f127c564ea0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__520a338727eb7d856b3b656bc7f18cdedc438461e851ce535758677490196542(
    value: typing.Optional[ManagedDatabasePostgresqlProperties],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ceddef9157916dec3e9a0146d7eedd65e39272ad64a94090ac97ce9eb4e638a6(
    *,
    feature_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    log: typing.Optional[typing.Sequence[builtins.str]] = None,
    log_catalog: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    log_client: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    log_level: typing.Optional[builtins.str] = None,
    log_max_string_length: typing.Optional[jsii.Number] = None,
    log_nested_statements: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    log_parameter: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    log_parameter_max_size: typing.Optional[jsii.Number] = None,
    log_relation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    log_rows: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    log_statement: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    log_statement_once: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    role: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__464ca482964593b0d9e773fbd6dc07d727fc64f0af5ecb299985f5926fe9926f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbc9b433486d9bb7d1609f8a5132fe20e78e3c0f5c752c920af98c9e7de822e1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d42260ac22d8d15c9b3103737e859b27c183e431b97bb47c1a2cb32f3ed5232(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2e01677919856bac39b08212f3a95dd303d385856121a095ea097d8627f226c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e85f22f31e95a82529a0182521fe54e51b95cc55171651188c909327a7cda591(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6b17d3021c92b2d92d85de2aa175a78950f3edb6630682261da5f055c1bd5fa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5289994fd6001603188306c40f7d768c770c8b24ac29b201562957f408410db(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79ba090e99b2ef9d8ed41d6e44ce66470ddcefe1c32d027e0463228cc96d6685(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce37f1d5b091e3bef4d0ceef4d0bd3d6e8c9d020ab9434f480ee27f96db29e67(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c637be970804d44fa68b279ab066787132117df8c2cf404436ab10521d07f616(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc52cfab3594e81eeda4e6dbe187d1c4a2e5e035649775d384a4fa2160772234(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5633b1a7e74d6a2c0b066feebb76ab2f159c97dc1f56b47afd171dcd2483c435(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7524618da50a3107d8f6d8db59750b885f5eee1808ede6defa9d3b53991a34c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06eb0435d6455a516aceb5fbf3ecdf75f11263abc7e24b00ccbb15d60e94be95(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f6a3198b0c922afc3600eaa8ef6e6ba0ab8816525f10d28f67fd6c2be9e00e8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8481bc4e1262a1119a3da0eb3f4597c912a4ac32d1819f992cc4c470b3e8272(
    value: typing.Optional[ManagedDatabasePostgresqlPropertiesPgaudit],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2862abffc43a442ad2bff1c444cf98fb770986970925fafb7cc295e2cc45a9b9(
    *,
    autodb_idle_timeout: typing.Optional[jsii.Number] = None,
    autodb_max_db_connections: typing.Optional[jsii.Number] = None,
    autodb_pool_mode: typing.Optional[builtins.str] = None,
    autodb_pool_size: typing.Optional[jsii.Number] = None,
    ignore_startup_parameters: typing.Optional[typing.Sequence[builtins.str]] = None,
    max_prepared_statements: typing.Optional[jsii.Number] = None,
    min_pool_size: typing.Optional[jsii.Number] = None,
    server_idle_timeout: typing.Optional[jsii.Number] = None,
    server_lifetime: typing.Optional[jsii.Number] = None,
    server_reset_query_always: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61222568dada92bfef5c5725c39b1b57b38d5ceff4bb0beb3340697754fe92a8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce972406e06643c117f973486aab7e9b90c2de0a19167dcc4a91d1f67c3be224(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f174d35ae6becea43c4005cf8d171a3f5b38e1e9ed961fd472ff71ace836a643(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c89625ebfc5b1171d9adb631a22f77b877b00db92269684183b9d62d5ca000e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6455db15790093dfe2a1d5908d16ee62da352ab2be9b7ed392cf201f8252bb8f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffa7e3d14d9a55b881ea76e07dd347874b2459e06c8d89905ba71ff8ffcd9791(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1714d88a07031186abba7bd75b3044a59c7bbe49477e83d5c20153eabd372c07(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0433626c85344b9838a6b512cde678d20b02d3792eaa058b4de2be4bc8009851(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f80b710e775e8ab14f4e4ab50e163f888e70bd3108cf6935ce365619a87b38b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc7d78e16970caa5cec1af6076b323b5bc850f89776553fc6522730bc5750ea1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ca0d1d22fc45834d7b10e43700bebb5a67d5f752e0dced7a3b20f0282010fdf(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9528ede7d75ae7969c77b9e4cec0539ada3f5505040b873b6594f6a2948a4823(
    value: typing.Optional[ManagedDatabasePostgresqlPropertiesPgbouncer],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd81ae3f527ba52eaf4f2d07e7187afc3b2328ed800858a2364717bdfe0081a9(
    *,
    max_failover_replication_time_lag: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3dc34eb16c0feb84003a8eeefbb09dab17f0a74e8b22043406c416ec43987274(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8283df738aae5d11534883b9b78ed5fef3c788a0f2073f06c598ca8dad4a6288(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a46bcae58aa1cd348a1a9371df5872df78258680d3dc6748e237e8bcb3597e8(
    value: typing.Optional[ManagedDatabasePostgresqlPropertiesPglookout],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71c8b11f8b53026baff50866f6d74787011a28fc791f639a52c7c58b6f897621(
    *,
    max_background_workers: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bbbda2af1005991302dae40f469de426075f1f91ac642daaf1883c5b91bdead(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23e67c9ed6769dafb2f62a8094ada00c7c96a2d32feb06b59a6403494e68d195(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf5f49a55ef153abaf9698cc84fa23749e5a65e92b79b9473d21eb8bf61b46e9(
    value: typing.Optional[ManagedDatabasePostgresqlPropertiesTimescaledb],
) -> None:
    """Type checking stubs"""
    pass
