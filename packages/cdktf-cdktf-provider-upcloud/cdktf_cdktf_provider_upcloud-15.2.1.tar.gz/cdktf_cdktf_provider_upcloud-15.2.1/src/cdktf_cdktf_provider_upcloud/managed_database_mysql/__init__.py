r'''
# `upcloud_managed_database_mysql`

Refer to the Terraform Registry for docs: [`upcloud_managed_database_mysql`](https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql).
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


class ManagedDatabaseMysql(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseMysql.ManagedDatabaseMysql",
):
    '''Represents a {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql upcloud_managed_database_mysql}.'''

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
        network: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedDatabaseMysqlNetwork", typing.Dict[builtins.str, typing.Any]]]]] = None,
        powered: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        properties: typing.Optional[typing.Union["ManagedDatabaseMysqlProperties", typing.Dict[builtins.str, typing.Any]]] = None,
        termination_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql upcloud_managed_database_mysql} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Name of the service. The name is used as a prefix for the logical hostname. Must be unique within an account Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#name ManagedDatabaseMysql#name}
        :param plan: Service plan to use. This determines how much resources the instance will have. You can list available plans with ``upctl database plans <type>``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#plan ManagedDatabaseMysql#plan}
        :param title: Title of a managed database instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#title ManagedDatabaseMysql#title}
        :param zone: Zone where the instance resides, e.g. ``de-fra1``. You can list available zones with ``upctl zone list``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#zone ManagedDatabaseMysql#zone}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#id ManagedDatabaseMysql#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param labels: User defined key-value pairs to classify the managed database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#labels ManagedDatabaseMysql#labels}
        :param maintenance_window_dow: Maintenance window day of week. Lower case weekday name (monday, tuesday, ...). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#maintenance_window_dow ManagedDatabaseMysql#maintenance_window_dow}
        :param maintenance_window_time: Maintenance window UTC time in hh:mm:ss format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#maintenance_window_time ManagedDatabaseMysql#maintenance_window_time}
        :param network: network block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#network ManagedDatabaseMysql#network}
        :param powered: The administrative power state of the service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#powered ManagedDatabaseMysql#powered}
        :param properties: properties block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#properties ManagedDatabaseMysql#properties}
        :param termination_protection: If set to true, prevents the managed service from being powered off, or deleted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#termination_protection ManagedDatabaseMysql#termination_protection}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__958e87e9d4c67c8f4dc9a92e0864dd5ec7b73c3fe017b196cd999a20a67aec35)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ManagedDatabaseMysqlConfig(
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
        '''Generates CDKTF code for importing a ManagedDatabaseMysql resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ManagedDatabaseMysql to import.
        :param import_from_id: The id of the existing ManagedDatabaseMysql that should be imported. Refer to the {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ManagedDatabaseMysql to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc745a4a2be4154ae040b4398757488ee2a87a34d3b8c1e1f51b52a2a2f60166)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putNetwork")
    def put_network(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedDatabaseMysqlNetwork", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a62fc7161400d7b4f860d59782c7df65db78aee0396e1926e60cae30f5d85e4f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNetwork", [value]))

    @jsii.member(jsii_name="putProperties")
    def put_properties(
        self,
        *,
        admin_password: typing.Optional[builtins.str] = None,
        admin_username: typing.Optional[builtins.str] = None,
        automatic_utility_network_ip_filter: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        backup_hour: typing.Optional[jsii.Number] = None,
        backup_minute: typing.Optional[jsii.Number] = None,
        binlog_retention_period: typing.Optional[jsii.Number] = None,
        connect_timeout: typing.Optional[jsii.Number] = None,
        default_time_zone: typing.Optional[builtins.str] = None,
        group_concat_max_len: typing.Optional[jsii.Number] = None,
        information_schema_stats_expiry: typing.Optional[jsii.Number] = None,
        innodb_change_buffer_max_size: typing.Optional[jsii.Number] = None,
        innodb_flush_neighbors: typing.Optional[jsii.Number] = None,
        innodb_ft_min_token_size: typing.Optional[jsii.Number] = None,
        innodb_ft_server_stopword_table: typing.Optional[builtins.str] = None,
        innodb_lock_wait_timeout: typing.Optional[jsii.Number] = None,
        innodb_log_buffer_size: typing.Optional[jsii.Number] = None,
        innodb_online_alter_log_max_size: typing.Optional[jsii.Number] = None,
        innodb_print_all_deadlocks: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        innodb_read_io_threads: typing.Optional[jsii.Number] = None,
        innodb_rollback_on_timeout: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        innodb_thread_concurrency: typing.Optional[jsii.Number] = None,
        innodb_write_io_threads: typing.Optional[jsii.Number] = None,
        interactive_timeout: typing.Optional[jsii.Number] = None,
        internal_tmp_mem_storage_engine: typing.Optional[builtins.str] = None,
        ip_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
        log_output: typing.Optional[builtins.str] = None,
        long_query_time: typing.Optional[jsii.Number] = None,
        max_allowed_packet: typing.Optional[jsii.Number] = None,
        max_heap_table_size: typing.Optional[jsii.Number] = None,
        migration: typing.Optional[typing.Union["ManagedDatabaseMysqlPropertiesMigration", typing.Dict[builtins.str, typing.Any]]] = None,
        mysql_incremental_backup: typing.Optional[typing.Union["ManagedDatabaseMysqlPropertiesMysqlIncrementalBackup", typing.Dict[builtins.str, typing.Any]]] = None,
        net_buffer_length: typing.Optional[jsii.Number] = None,
        net_read_timeout: typing.Optional[jsii.Number] = None,
        net_write_timeout: typing.Optional[jsii.Number] = None,
        public_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        service_log: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        slow_query_log: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sort_buffer_size: typing.Optional[jsii.Number] = None,
        sql_mode: typing.Optional[builtins.str] = None,
        sql_require_primary_key: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tmp_table_size: typing.Optional[jsii.Number] = None,
        version: typing.Optional[builtins.str] = None,
        wait_timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param admin_password: Custom password for admin user. Defaults to random string. This must be set only when a new service is being created. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#admin_password ManagedDatabaseMysql#admin_password}
        :param admin_username: Custom username for admin user. This must be set only when a new service is being created. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#admin_username ManagedDatabaseMysql#admin_username}
        :param automatic_utility_network_ip_filter: Automatic utility network IP Filter. Automatically allow connections from servers in the utility network within the same zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#automatic_utility_network_ip_filter ManagedDatabaseMysql#automatic_utility_network_ip_filter}
        :param backup_hour: The hour of day (in UTC) when backup for the service is started. New backup is only started if previous backup has already completed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#backup_hour ManagedDatabaseMysql#backup_hour}
        :param backup_minute: The minute of an hour when backup for the service is started. New backup is only started if previous backup has already completed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#backup_minute ManagedDatabaseMysql#backup_minute}
        :param binlog_retention_period: The minimum amount of time in seconds to keep binlog entries before deletion. This may be extended for services that require binlog entries for longer than the default for example if using the MySQL Debezium Kafka connector. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#binlog_retention_period ManagedDatabaseMysql#binlog_retention_period}
        :param connect_timeout: The number of seconds that the mysqld server waits for a connect packet before responding with Bad handshake. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#connect_timeout ManagedDatabaseMysql#connect_timeout}
        :param default_time_zone: Default server time zone as an offset from UTC (from -12:00 to +12:00), a time zone name, or 'SYSTEM' to use the MySQL server default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#default_time_zone ManagedDatabaseMysql#default_time_zone}
        :param group_concat_max_len: The maximum permitted result length in bytes for the GROUP_CONCAT() function. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#group_concat_max_len ManagedDatabaseMysql#group_concat_max_len}
        :param information_schema_stats_expiry: The time, in seconds, before cached statistics expire. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#information_schema_stats_expiry ManagedDatabaseMysql#information_schema_stats_expiry}
        :param innodb_change_buffer_max_size: Maximum size for the InnoDB change buffer, as a percentage of the total size of the buffer pool. Default is 25. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_change_buffer_max_size ManagedDatabaseMysql#innodb_change_buffer_max_size}
        :param innodb_flush_neighbors: Specifies whether flushing a page from the InnoDB buffer pool also flushes other dirty pages in the same extent (default is 1): 0 - dirty pages in the same extent are not flushed, 1 - flush contiguous dirty pages in the same extent, 2 - flush dirty pages in the same extent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_flush_neighbors ManagedDatabaseMysql#innodb_flush_neighbors}
        :param innodb_ft_min_token_size: Minimum length of words that are stored in an InnoDB FULLTEXT index. Changing this parameter will lead to a restart of the MySQL service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_ft_min_token_size ManagedDatabaseMysql#innodb_ft_min_token_size}
        :param innodb_ft_server_stopword_table: This option is used to specify your own InnoDB FULLTEXT index stopword list for all InnoDB tables. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_ft_server_stopword_table ManagedDatabaseMysql#innodb_ft_server_stopword_table}
        :param innodb_lock_wait_timeout: The length of time in seconds an InnoDB transaction waits for a row lock before giving up. Default is 120. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_lock_wait_timeout ManagedDatabaseMysql#innodb_lock_wait_timeout}
        :param innodb_log_buffer_size: The size in bytes of the buffer that InnoDB uses to write to the log files on disk. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_log_buffer_size ManagedDatabaseMysql#innodb_log_buffer_size}
        :param innodb_online_alter_log_max_size: The upper limit in bytes on the size of the temporary log files used during online DDL operations for InnoDB tables. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_online_alter_log_max_size ManagedDatabaseMysql#innodb_online_alter_log_max_size}
        :param innodb_print_all_deadlocks: When enabled, information about all deadlocks in InnoDB user transactions is recorded in the error log. Disabled by default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_print_all_deadlocks ManagedDatabaseMysql#innodb_print_all_deadlocks}
        :param innodb_read_io_threads: The number of I/O threads for read operations in InnoDB. Default is 4. Changing this parameter will lead to a restart of the MySQL service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_read_io_threads ManagedDatabaseMysql#innodb_read_io_threads}
        :param innodb_rollback_on_timeout: When enabled a transaction timeout causes InnoDB to abort and roll back the entire transaction. Changing this parameter will lead to a restart of the MySQL service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_rollback_on_timeout ManagedDatabaseMysql#innodb_rollback_on_timeout}
        :param innodb_thread_concurrency: Defines the maximum number of threads permitted inside of InnoDB. Default is 0 (infinite concurrency - no limit). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_thread_concurrency ManagedDatabaseMysql#innodb_thread_concurrency}
        :param innodb_write_io_threads: The number of I/O threads for write operations in InnoDB. Default is 4. Changing this parameter will lead to a restart of the MySQL service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_write_io_threads ManagedDatabaseMysql#innodb_write_io_threads}
        :param interactive_timeout: The number of seconds the server waits for activity on an interactive connection before closing it. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#interactive_timeout ManagedDatabaseMysql#interactive_timeout}
        :param internal_tmp_mem_storage_engine: The storage engine for in-memory internal temporary tables. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#internal_tmp_mem_storage_engine ManagedDatabaseMysql#internal_tmp_mem_storage_engine}
        :param ip_filter: IP filter. Allow incoming connections from CIDR address block, e.g. '10.20.0.0/16'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#ip_filter ManagedDatabaseMysql#ip_filter}
        :param log_output: The slow log output destination when slow_query_log is ON. To enable MySQL AI Insights, choose INSIGHTS. To use MySQL AI Insights and the mysql.slow_log table at the same time, choose INSIGHTS,TABLE. To only use the mysql.slow_log table, choose TABLE. To silence slow logs, choose NONE. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#log_output ManagedDatabaseMysql#log_output}
        :param long_query_time: The slow_query_logs work as SQL statements that take more than long_query_time seconds to execute. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#long_query_time ManagedDatabaseMysql#long_query_time}
        :param max_allowed_packet: Size of the largest message in bytes that can be received by the server. Default is 67108864 (64M). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#max_allowed_packet ManagedDatabaseMysql#max_allowed_packet}
        :param max_heap_table_size: Limits the size of internal in-memory tables. Also set tmp_table_size. Default is 16777216 (16M). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#max_heap_table_size ManagedDatabaseMysql#max_heap_table_size}
        :param migration: migration block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#migration ManagedDatabaseMysql#migration}
        :param mysql_incremental_backup: mysql_incremental_backup block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#mysql_incremental_backup ManagedDatabaseMysql#mysql_incremental_backup}
        :param net_buffer_length: Start sizes of connection buffer and result buffer. Default is 16384 (16K). Changing this parameter will lead to a restart of the MySQL service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#net_buffer_length ManagedDatabaseMysql#net_buffer_length}
        :param net_read_timeout: The number of seconds to wait for more data from a connection before aborting the read. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#net_read_timeout ManagedDatabaseMysql#net_read_timeout}
        :param net_write_timeout: The number of seconds to wait for a block to be written to a connection before aborting the write. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#net_write_timeout ManagedDatabaseMysql#net_write_timeout}
        :param public_access: Public Access. Allow access to the service from the public Internet. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#public_access ManagedDatabaseMysql#public_access}
        :param service_log: Service logging. Store logs for the service so that they are available in the HTTP API and console. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#service_log ManagedDatabaseMysql#service_log}
        :param slow_query_log: Slow query log enables capturing of slow queries. Setting slow_query_log to false also truncates the mysql.slow_log table. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#slow_query_log ManagedDatabaseMysql#slow_query_log}
        :param sort_buffer_size: Sort buffer size in bytes for ORDER BY optimization. Default is 262144 (256K). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#sort_buffer_size ManagedDatabaseMysql#sort_buffer_size}
        :param sql_mode: Global SQL mode. Set to empty to use MySQL server defaults. When creating a new service and not setting this field Aiven default SQL mode (strict, SQL standard compliant) will be assigned. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#sql_mode ManagedDatabaseMysql#sql_mode}
        :param sql_require_primary_key: Require primary key to be defined for new tables or old tables modified with ALTER TABLE and fail if missing. It is recommended to always have primary keys because various functionality may break if any large table is missing them. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#sql_require_primary_key ManagedDatabaseMysql#sql_require_primary_key}
        :param tmp_table_size: Limits the size of internal in-memory tables. Also set max_heap_table_size. Default is 16777216 (16M). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#tmp_table_size ManagedDatabaseMysql#tmp_table_size}
        :param version: MySQL major version. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#version ManagedDatabaseMysql#version}
        :param wait_timeout: The number of seconds the server waits for activity on a noninteractive connection before closing it. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#wait_timeout ManagedDatabaseMysql#wait_timeout}
        '''
        value = ManagedDatabaseMysqlProperties(
            admin_password=admin_password,
            admin_username=admin_username,
            automatic_utility_network_ip_filter=automatic_utility_network_ip_filter,
            backup_hour=backup_hour,
            backup_minute=backup_minute,
            binlog_retention_period=binlog_retention_period,
            connect_timeout=connect_timeout,
            default_time_zone=default_time_zone,
            group_concat_max_len=group_concat_max_len,
            information_schema_stats_expiry=information_schema_stats_expiry,
            innodb_change_buffer_max_size=innodb_change_buffer_max_size,
            innodb_flush_neighbors=innodb_flush_neighbors,
            innodb_ft_min_token_size=innodb_ft_min_token_size,
            innodb_ft_server_stopword_table=innodb_ft_server_stopword_table,
            innodb_lock_wait_timeout=innodb_lock_wait_timeout,
            innodb_log_buffer_size=innodb_log_buffer_size,
            innodb_online_alter_log_max_size=innodb_online_alter_log_max_size,
            innodb_print_all_deadlocks=innodb_print_all_deadlocks,
            innodb_read_io_threads=innodb_read_io_threads,
            innodb_rollback_on_timeout=innodb_rollback_on_timeout,
            innodb_thread_concurrency=innodb_thread_concurrency,
            innodb_write_io_threads=innodb_write_io_threads,
            interactive_timeout=interactive_timeout,
            internal_tmp_mem_storage_engine=internal_tmp_mem_storage_engine,
            ip_filter=ip_filter,
            log_output=log_output,
            long_query_time=long_query_time,
            max_allowed_packet=max_allowed_packet,
            max_heap_table_size=max_heap_table_size,
            migration=migration,
            mysql_incremental_backup=mysql_incremental_backup,
            net_buffer_length=net_buffer_length,
            net_read_timeout=net_read_timeout,
            net_write_timeout=net_write_timeout,
            public_access=public_access,
            service_log=service_log,
            slow_query_log=slow_query_log,
            sort_buffer_size=sort_buffer_size,
            sql_mode=sql_mode,
            sql_require_primary_key=sql_require_primary_key,
            tmp_table_size=tmp_table_size,
            version=version,
            wait_timeout=wait_timeout,
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
    def components(self) -> "ManagedDatabaseMysqlComponentsList":
        return typing.cast("ManagedDatabaseMysqlComponentsList", jsii.get(self, "components"))

    @builtins.property
    @jsii.member(jsii_name="network")
    def network(self) -> "ManagedDatabaseMysqlNetworkList":
        return typing.cast("ManagedDatabaseMysqlNetworkList", jsii.get(self, "network"))

    @builtins.property
    @jsii.member(jsii_name="nodeStates")
    def node_states(self) -> "ManagedDatabaseMysqlNodeStatesList":
        return typing.cast("ManagedDatabaseMysqlNodeStatesList", jsii.get(self, "nodeStates"))

    @builtins.property
    @jsii.member(jsii_name="primaryDatabase")
    def primary_database(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "primaryDatabase"))

    @builtins.property
    @jsii.member(jsii_name="properties")
    def properties(self) -> "ManagedDatabaseMysqlPropertiesOutputReference":
        return typing.cast("ManagedDatabaseMysqlPropertiesOutputReference", jsii.get(self, "properties"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedDatabaseMysqlNetwork"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedDatabaseMysqlNetwork"]]], jsii.get(self, "networkInput"))

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
    def properties_input(self) -> typing.Optional["ManagedDatabaseMysqlProperties"]:
        return typing.cast(typing.Optional["ManagedDatabaseMysqlProperties"], jsii.get(self, "propertiesInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__e7a4fb60d1135c0f8631d36600a5812527c23ae3a5aa4b793722b50e65fd246d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fcb88e825a08094ea35b5029118afc3cd252fe3cb6af4672e840930dae68ffb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "labels", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowDow")
    def maintenance_window_dow(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maintenanceWindowDow"))

    @maintenance_window_dow.setter
    def maintenance_window_dow(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48df4258c07649eccd564db2bfea58f2d8c6e7775d42e302c4732ba2a3bfa35e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maintenanceWindowDow", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowTime")
    def maintenance_window_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maintenanceWindowTime"))

    @maintenance_window_time.setter
    def maintenance_window_time(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10c67ec6c447fed554dbe7abe9233193df48d93398b1a1c03b2cc52fc4a56f21)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maintenanceWindowTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b3317f4107eb3f0324a64874708fab95f67e816faecf7678312b22212af296f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="plan")
    def plan(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "plan"))

    @plan.setter
    def plan(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a44dc38d52585561bb352263c2d4c0c7166d02e7d2ba26b1f06b0827bd1645c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__beb13051c8d159249aa225bdbcf28aeb76bc85a1aae08e9c31f60dfe116dfecc)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8c9f7e6065020fa925bf719fbd0aa777653e104f39664706dabe6a435de915cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terminationProtection", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @title.setter
    def title(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7141cc36a0c3b744c0e90aacfea1d6055f2e1bb6d23321a515475bd8c72cec64)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "title", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zone")
    def zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zone"))

    @zone.setter
    def zone(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7732a2cf2cda58a00518cf2d610dba1c27c5673a60c4385a62472ceb732076d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zone", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseMysql.ManagedDatabaseMysqlComponents",
    jsii_struct_bases=[],
    name_mapping={},
)
class ManagedDatabaseMysqlComponents:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseMysqlComponents(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseMysqlComponentsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseMysql.ManagedDatabaseMysqlComponentsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__34b41667608ff4cd5e9008da8d533f9c668a11f12f74531e6d80da050862de08)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ManagedDatabaseMysqlComponentsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__688fdae24b26e710345c109b7473013f94e8839a01038fa5240f646ae832ee6a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ManagedDatabaseMysqlComponentsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80d18976397eb5bc969ead28206ee1c2ebb44271012265fe7c6bc2410af32085)
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
            type_hints = typing.get_type_hints(_typecheckingstub__017d94a1bed5a80567186f11930d76599611f085d87754b6317c3f1d30eac0f1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__deb58afab231debdc3de38ded6700565608b4d5e89d03bcdea43e26c8f29e2cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class ManagedDatabaseMysqlComponentsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseMysql.ManagedDatabaseMysqlComponentsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1ec6165c0e005f2cdab8e4bf91377627b2fee91a4c49330a894a38d618cb266d)
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
    def internal_value(self) -> typing.Optional[ManagedDatabaseMysqlComponents]:
        return typing.cast(typing.Optional[ManagedDatabaseMysqlComponents], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseMysqlComponents],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae4277256ebc37247795b9bcfd0b223c65762e3553860601183ea80dd360dc0d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseMysql.ManagedDatabaseMysqlConfig",
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
class ManagedDatabaseMysqlConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        network: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedDatabaseMysqlNetwork", typing.Dict[builtins.str, typing.Any]]]]] = None,
        powered: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        properties: typing.Optional[typing.Union["ManagedDatabaseMysqlProperties", typing.Dict[builtins.str, typing.Any]]] = None,
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
        :param name: Name of the service. The name is used as a prefix for the logical hostname. Must be unique within an account Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#name ManagedDatabaseMysql#name}
        :param plan: Service plan to use. This determines how much resources the instance will have. You can list available plans with ``upctl database plans <type>``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#plan ManagedDatabaseMysql#plan}
        :param title: Title of a managed database instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#title ManagedDatabaseMysql#title}
        :param zone: Zone where the instance resides, e.g. ``de-fra1``. You can list available zones with ``upctl zone list``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#zone ManagedDatabaseMysql#zone}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#id ManagedDatabaseMysql#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param labels: User defined key-value pairs to classify the managed database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#labels ManagedDatabaseMysql#labels}
        :param maintenance_window_dow: Maintenance window day of week. Lower case weekday name (monday, tuesday, ...). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#maintenance_window_dow ManagedDatabaseMysql#maintenance_window_dow}
        :param maintenance_window_time: Maintenance window UTC time in hh:mm:ss format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#maintenance_window_time ManagedDatabaseMysql#maintenance_window_time}
        :param network: network block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#network ManagedDatabaseMysql#network}
        :param powered: The administrative power state of the service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#powered ManagedDatabaseMysql#powered}
        :param properties: properties block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#properties ManagedDatabaseMysql#properties}
        :param termination_protection: If set to true, prevents the managed service from being powered off, or deleted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#termination_protection ManagedDatabaseMysql#termination_protection}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(properties, dict):
            properties = ManagedDatabaseMysqlProperties(**properties)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10b2894ddd0553e9581d0116772434efafda3295976e9367656213631c5dc624)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#name ManagedDatabaseMysql#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def plan(self) -> builtins.str:
        '''Service plan to use.

        This determines how much resources the instance will have. You can list available plans with ``upctl database plans <type>``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#plan ManagedDatabaseMysql#plan}
        '''
        result = self._values.get("plan")
        assert result is not None, "Required property 'plan' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''Title of a managed database instance.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#title ManagedDatabaseMysql#title}
        '''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def zone(self) -> builtins.str:
        '''Zone where the instance resides, e.g. ``de-fra1``. You can list available zones with ``upctl zone list``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#zone ManagedDatabaseMysql#zone}
        '''
        result = self._values.get("zone")
        assert result is not None, "Required property 'zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#id ManagedDatabaseMysql#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''User defined key-value pairs to classify the managed database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#labels ManagedDatabaseMysql#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def maintenance_window_dow(self) -> typing.Optional[builtins.str]:
        '''Maintenance window day of week. Lower case weekday name (monday, tuesday, ...).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#maintenance_window_dow ManagedDatabaseMysql#maintenance_window_dow}
        '''
        result = self._values.get("maintenance_window_dow")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maintenance_window_time(self) -> typing.Optional[builtins.str]:
        '''Maintenance window UTC time in hh:mm:ss format.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#maintenance_window_time ManagedDatabaseMysql#maintenance_window_time}
        '''
        result = self._values.get("maintenance_window_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedDatabaseMysqlNetwork"]]]:
        '''network block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#network ManagedDatabaseMysql#network}
        '''
        result = self._values.get("network")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedDatabaseMysqlNetwork"]]], result)

    @builtins.property
    def powered(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''The administrative power state of the service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#powered ManagedDatabaseMysql#powered}
        '''
        result = self._values.get("powered")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def properties(self) -> typing.Optional["ManagedDatabaseMysqlProperties"]:
        '''properties block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#properties ManagedDatabaseMysql#properties}
        '''
        result = self._values.get("properties")
        return typing.cast(typing.Optional["ManagedDatabaseMysqlProperties"], result)

    @builtins.property
    def termination_protection(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set to true, prevents the managed service from being powered off, or deleted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#termination_protection ManagedDatabaseMysql#termination_protection}
        '''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseMysqlConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseMysql.ManagedDatabaseMysqlNetwork",
    jsii_struct_bases=[],
    name_mapping={"family": "family", "name": "name", "type": "type", "uuid": "uuid"},
)
class ManagedDatabaseMysqlNetwork:
    def __init__(
        self,
        *,
        family: builtins.str,
        name: builtins.str,
        type: builtins.str,
        uuid: builtins.str,
    ) -> None:
        '''
        :param family: Network family. Currently only ``IPv4`` is supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#family ManagedDatabaseMysql#family}
        :param name: The name of the network. Must be unique within the service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#name ManagedDatabaseMysql#name}
        :param type: The type of the network. Must be private. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#type ManagedDatabaseMysql#type}
        :param uuid: Private network UUID. Must reside in the same zone as the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#uuid ManagedDatabaseMysql#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74301fe81253b8784b9afba8d3a1dda97ee52965714102f2fb71f3cda82c72d9)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#family ManagedDatabaseMysql#family}
        '''
        result = self._values.get("family")
        assert result is not None, "Required property 'family' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the network. Must be unique within the service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#name ManagedDatabaseMysql#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''The type of the network. Must be private.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#type ManagedDatabaseMysql#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def uuid(self) -> builtins.str:
        '''Private network UUID. Must reside in the same zone as the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#uuid ManagedDatabaseMysql#uuid}
        '''
        result = self._values.get("uuid")
        assert result is not None, "Required property 'uuid' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseMysqlNetwork(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseMysqlNetworkList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseMysql.ManagedDatabaseMysqlNetworkList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__53c76b9a36fa2c5763e2ef8caea118bd60028c1ba65bcd4a2bf797076f44e2f7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ManagedDatabaseMysqlNetworkOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__127d61284845f513acef2e7d6fe15b6f6cc76e910f2d89ece042176d8bef7967)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ManagedDatabaseMysqlNetworkOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6f90b60425a2e38d3af43a492643c17d866cb129ac68edbb3072b9614eb3113)
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
            type_hints = typing.get_type_hints(_typecheckingstub__00c8b7b77f169dfb8910e16238b1e78991dc8e7e37374ca83ca93de027477e5c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f21cfe7d74b33287ba0ab770e586d1d2ccf031bf53abb32c3632361e3061f6a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedDatabaseMysqlNetwork]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedDatabaseMysqlNetwork]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedDatabaseMysqlNetwork]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94c97a6da3042ffb69736a0b72c58cc97a1025de77ce3dea7b71a494beeb8ca7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ManagedDatabaseMysqlNetworkOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseMysql.ManagedDatabaseMysqlNetworkOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2dd5c3a8b28af9ee2d43d563baf32e395fe43a74440a5ce7f47afaec5e1a113a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__32b05c92713a900a94460be120f24b5ea22785668076ee827760f5d736e28ec7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "family", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__927d6daa33e2f827191036084c87fe58d852f38b6a3609825470a2d55c533dc2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1327b0d72083b5bdf8929efed7cdf969a5d3933e8d9b5192dff0931eb3ba6a9b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05b71e4f1fb19a4fffec705975e756f2280605d835c59bdd94a71df18627a8bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedDatabaseMysqlNetwork]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedDatabaseMysqlNetwork]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedDatabaseMysqlNetwork]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afce920649c215f1f7f3adde9483ce3407c61af39dfacb0bcaa881777aa4f8dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseMysql.ManagedDatabaseMysqlNodeStates",
    jsii_struct_bases=[],
    name_mapping={},
)
class ManagedDatabaseMysqlNodeStates:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseMysqlNodeStates(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseMysqlNodeStatesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseMysql.ManagedDatabaseMysqlNodeStatesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__989e2763cac47db0558f0e09bb2669c13639bb78716a422e8f8c4eb11ef4418a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ManagedDatabaseMysqlNodeStatesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03bece7009f60e171555f364ad6c8bd3ebd4909c341071b47f847719e5090152)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ManagedDatabaseMysqlNodeStatesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6bc42894cd75446060a318bed07cb53e96f5e05d71db1adc1e71664475609f06)
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
            type_hints = typing.get_type_hints(_typecheckingstub__41e9094332f45eaa5d58fe2d5d98992caaa8fba697503fe24ff24b0640684980)
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
            type_hints = typing.get_type_hints(_typecheckingstub__287baddcdede19148df005876a5ab7752a44533620e042b8c358bd67bd66bc48)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class ManagedDatabaseMysqlNodeStatesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseMysql.ManagedDatabaseMysqlNodeStatesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0fa4e7b4eb3edbb0a4e64637e5c937e026f3ebdf8313cb45509c105223b6f1ad)
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
    def internal_value(self) -> typing.Optional[ManagedDatabaseMysqlNodeStates]:
        return typing.cast(typing.Optional[ManagedDatabaseMysqlNodeStates], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseMysqlNodeStates],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b164fbe1f2de1cd7f849e6d1a275455f99e36b5fea9891f0c6efac51327f5e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseMysql.ManagedDatabaseMysqlProperties",
    jsii_struct_bases=[],
    name_mapping={
        "admin_password": "adminPassword",
        "admin_username": "adminUsername",
        "automatic_utility_network_ip_filter": "automaticUtilityNetworkIpFilter",
        "backup_hour": "backupHour",
        "backup_minute": "backupMinute",
        "binlog_retention_period": "binlogRetentionPeriod",
        "connect_timeout": "connectTimeout",
        "default_time_zone": "defaultTimeZone",
        "group_concat_max_len": "groupConcatMaxLen",
        "information_schema_stats_expiry": "informationSchemaStatsExpiry",
        "innodb_change_buffer_max_size": "innodbChangeBufferMaxSize",
        "innodb_flush_neighbors": "innodbFlushNeighbors",
        "innodb_ft_min_token_size": "innodbFtMinTokenSize",
        "innodb_ft_server_stopword_table": "innodbFtServerStopwordTable",
        "innodb_lock_wait_timeout": "innodbLockWaitTimeout",
        "innodb_log_buffer_size": "innodbLogBufferSize",
        "innodb_online_alter_log_max_size": "innodbOnlineAlterLogMaxSize",
        "innodb_print_all_deadlocks": "innodbPrintAllDeadlocks",
        "innodb_read_io_threads": "innodbReadIoThreads",
        "innodb_rollback_on_timeout": "innodbRollbackOnTimeout",
        "innodb_thread_concurrency": "innodbThreadConcurrency",
        "innodb_write_io_threads": "innodbWriteIoThreads",
        "interactive_timeout": "interactiveTimeout",
        "internal_tmp_mem_storage_engine": "internalTmpMemStorageEngine",
        "ip_filter": "ipFilter",
        "log_output": "logOutput",
        "long_query_time": "longQueryTime",
        "max_allowed_packet": "maxAllowedPacket",
        "max_heap_table_size": "maxHeapTableSize",
        "migration": "migration",
        "mysql_incremental_backup": "mysqlIncrementalBackup",
        "net_buffer_length": "netBufferLength",
        "net_read_timeout": "netReadTimeout",
        "net_write_timeout": "netWriteTimeout",
        "public_access": "publicAccess",
        "service_log": "serviceLog",
        "slow_query_log": "slowQueryLog",
        "sort_buffer_size": "sortBufferSize",
        "sql_mode": "sqlMode",
        "sql_require_primary_key": "sqlRequirePrimaryKey",
        "tmp_table_size": "tmpTableSize",
        "version": "version",
        "wait_timeout": "waitTimeout",
    },
)
class ManagedDatabaseMysqlProperties:
    def __init__(
        self,
        *,
        admin_password: typing.Optional[builtins.str] = None,
        admin_username: typing.Optional[builtins.str] = None,
        automatic_utility_network_ip_filter: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        backup_hour: typing.Optional[jsii.Number] = None,
        backup_minute: typing.Optional[jsii.Number] = None,
        binlog_retention_period: typing.Optional[jsii.Number] = None,
        connect_timeout: typing.Optional[jsii.Number] = None,
        default_time_zone: typing.Optional[builtins.str] = None,
        group_concat_max_len: typing.Optional[jsii.Number] = None,
        information_schema_stats_expiry: typing.Optional[jsii.Number] = None,
        innodb_change_buffer_max_size: typing.Optional[jsii.Number] = None,
        innodb_flush_neighbors: typing.Optional[jsii.Number] = None,
        innodb_ft_min_token_size: typing.Optional[jsii.Number] = None,
        innodb_ft_server_stopword_table: typing.Optional[builtins.str] = None,
        innodb_lock_wait_timeout: typing.Optional[jsii.Number] = None,
        innodb_log_buffer_size: typing.Optional[jsii.Number] = None,
        innodb_online_alter_log_max_size: typing.Optional[jsii.Number] = None,
        innodb_print_all_deadlocks: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        innodb_read_io_threads: typing.Optional[jsii.Number] = None,
        innodb_rollback_on_timeout: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        innodb_thread_concurrency: typing.Optional[jsii.Number] = None,
        innodb_write_io_threads: typing.Optional[jsii.Number] = None,
        interactive_timeout: typing.Optional[jsii.Number] = None,
        internal_tmp_mem_storage_engine: typing.Optional[builtins.str] = None,
        ip_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
        log_output: typing.Optional[builtins.str] = None,
        long_query_time: typing.Optional[jsii.Number] = None,
        max_allowed_packet: typing.Optional[jsii.Number] = None,
        max_heap_table_size: typing.Optional[jsii.Number] = None,
        migration: typing.Optional[typing.Union["ManagedDatabaseMysqlPropertiesMigration", typing.Dict[builtins.str, typing.Any]]] = None,
        mysql_incremental_backup: typing.Optional[typing.Union["ManagedDatabaseMysqlPropertiesMysqlIncrementalBackup", typing.Dict[builtins.str, typing.Any]]] = None,
        net_buffer_length: typing.Optional[jsii.Number] = None,
        net_read_timeout: typing.Optional[jsii.Number] = None,
        net_write_timeout: typing.Optional[jsii.Number] = None,
        public_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        service_log: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        slow_query_log: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sort_buffer_size: typing.Optional[jsii.Number] = None,
        sql_mode: typing.Optional[builtins.str] = None,
        sql_require_primary_key: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tmp_table_size: typing.Optional[jsii.Number] = None,
        version: typing.Optional[builtins.str] = None,
        wait_timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param admin_password: Custom password for admin user. Defaults to random string. This must be set only when a new service is being created. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#admin_password ManagedDatabaseMysql#admin_password}
        :param admin_username: Custom username for admin user. This must be set only when a new service is being created. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#admin_username ManagedDatabaseMysql#admin_username}
        :param automatic_utility_network_ip_filter: Automatic utility network IP Filter. Automatically allow connections from servers in the utility network within the same zone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#automatic_utility_network_ip_filter ManagedDatabaseMysql#automatic_utility_network_ip_filter}
        :param backup_hour: The hour of day (in UTC) when backup for the service is started. New backup is only started if previous backup has already completed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#backup_hour ManagedDatabaseMysql#backup_hour}
        :param backup_minute: The minute of an hour when backup for the service is started. New backup is only started if previous backup has already completed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#backup_minute ManagedDatabaseMysql#backup_minute}
        :param binlog_retention_period: The minimum amount of time in seconds to keep binlog entries before deletion. This may be extended for services that require binlog entries for longer than the default for example if using the MySQL Debezium Kafka connector. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#binlog_retention_period ManagedDatabaseMysql#binlog_retention_period}
        :param connect_timeout: The number of seconds that the mysqld server waits for a connect packet before responding with Bad handshake. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#connect_timeout ManagedDatabaseMysql#connect_timeout}
        :param default_time_zone: Default server time zone as an offset from UTC (from -12:00 to +12:00), a time zone name, or 'SYSTEM' to use the MySQL server default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#default_time_zone ManagedDatabaseMysql#default_time_zone}
        :param group_concat_max_len: The maximum permitted result length in bytes for the GROUP_CONCAT() function. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#group_concat_max_len ManagedDatabaseMysql#group_concat_max_len}
        :param information_schema_stats_expiry: The time, in seconds, before cached statistics expire. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#information_schema_stats_expiry ManagedDatabaseMysql#information_schema_stats_expiry}
        :param innodb_change_buffer_max_size: Maximum size for the InnoDB change buffer, as a percentage of the total size of the buffer pool. Default is 25. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_change_buffer_max_size ManagedDatabaseMysql#innodb_change_buffer_max_size}
        :param innodb_flush_neighbors: Specifies whether flushing a page from the InnoDB buffer pool also flushes other dirty pages in the same extent (default is 1): 0 - dirty pages in the same extent are not flushed, 1 - flush contiguous dirty pages in the same extent, 2 - flush dirty pages in the same extent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_flush_neighbors ManagedDatabaseMysql#innodb_flush_neighbors}
        :param innodb_ft_min_token_size: Minimum length of words that are stored in an InnoDB FULLTEXT index. Changing this parameter will lead to a restart of the MySQL service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_ft_min_token_size ManagedDatabaseMysql#innodb_ft_min_token_size}
        :param innodb_ft_server_stopword_table: This option is used to specify your own InnoDB FULLTEXT index stopword list for all InnoDB tables. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_ft_server_stopword_table ManagedDatabaseMysql#innodb_ft_server_stopword_table}
        :param innodb_lock_wait_timeout: The length of time in seconds an InnoDB transaction waits for a row lock before giving up. Default is 120. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_lock_wait_timeout ManagedDatabaseMysql#innodb_lock_wait_timeout}
        :param innodb_log_buffer_size: The size in bytes of the buffer that InnoDB uses to write to the log files on disk. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_log_buffer_size ManagedDatabaseMysql#innodb_log_buffer_size}
        :param innodb_online_alter_log_max_size: The upper limit in bytes on the size of the temporary log files used during online DDL operations for InnoDB tables. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_online_alter_log_max_size ManagedDatabaseMysql#innodb_online_alter_log_max_size}
        :param innodb_print_all_deadlocks: When enabled, information about all deadlocks in InnoDB user transactions is recorded in the error log. Disabled by default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_print_all_deadlocks ManagedDatabaseMysql#innodb_print_all_deadlocks}
        :param innodb_read_io_threads: The number of I/O threads for read operations in InnoDB. Default is 4. Changing this parameter will lead to a restart of the MySQL service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_read_io_threads ManagedDatabaseMysql#innodb_read_io_threads}
        :param innodb_rollback_on_timeout: When enabled a transaction timeout causes InnoDB to abort and roll back the entire transaction. Changing this parameter will lead to a restart of the MySQL service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_rollback_on_timeout ManagedDatabaseMysql#innodb_rollback_on_timeout}
        :param innodb_thread_concurrency: Defines the maximum number of threads permitted inside of InnoDB. Default is 0 (infinite concurrency - no limit). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_thread_concurrency ManagedDatabaseMysql#innodb_thread_concurrency}
        :param innodb_write_io_threads: The number of I/O threads for write operations in InnoDB. Default is 4. Changing this parameter will lead to a restart of the MySQL service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_write_io_threads ManagedDatabaseMysql#innodb_write_io_threads}
        :param interactive_timeout: The number of seconds the server waits for activity on an interactive connection before closing it. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#interactive_timeout ManagedDatabaseMysql#interactive_timeout}
        :param internal_tmp_mem_storage_engine: The storage engine for in-memory internal temporary tables. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#internal_tmp_mem_storage_engine ManagedDatabaseMysql#internal_tmp_mem_storage_engine}
        :param ip_filter: IP filter. Allow incoming connections from CIDR address block, e.g. '10.20.0.0/16'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#ip_filter ManagedDatabaseMysql#ip_filter}
        :param log_output: The slow log output destination when slow_query_log is ON. To enable MySQL AI Insights, choose INSIGHTS. To use MySQL AI Insights and the mysql.slow_log table at the same time, choose INSIGHTS,TABLE. To only use the mysql.slow_log table, choose TABLE. To silence slow logs, choose NONE. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#log_output ManagedDatabaseMysql#log_output}
        :param long_query_time: The slow_query_logs work as SQL statements that take more than long_query_time seconds to execute. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#long_query_time ManagedDatabaseMysql#long_query_time}
        :param max_allowed_packet: Size of the largest message in bytes that can be received by the server. Default is 67108864 (64M). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#max_allowed_packet ManagedDatabaseMysql#max_allowed_packet}
        :param max_heap_table_size: Limits the size of internal in-memory tables. Also set tmp_table_size. Default is 16777216 (16M). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#max_heap_table_size ManagedDatabaseMysql#max_heap_table_size}
        :param migration: migration block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#migration ManagedDatabaseMysql#migration}
        :param mysql_incremental_backup: mysql_incremental_backup block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#mysql_incremental_backup ManagedDatabaseMysql#mysql_incremental_backup}
        :param net_buffer_length: Start sizes of connection buffer and result buffer. Default is 16384 (16K). Changing this parameter will lead to a restart of the MySQL service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#net_buffer_length ManagedDatabaseMysql#net_buffer_length}
        :param net_read_timeout: The number of seconds to wait for more data from a connection before aborting the read. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#net_read_timeout ManagedDatabaseMysql#net_read_timeout}
        :param net_write_timeout: The number of seconds to wait for a block to be written to a connection before aborting the write. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#net_write_timeout ManagedDatabaseMysql#net_write_timeout}
        :param public_access: Public Access. Allow access to the service from the public Internet. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#public_access ManagedDatabaseMysql#public_access}
        :param service_log: Service logging. Store logs for the service so that they are available in the HTTP API and console. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#service_log ManagedDatabaseMysql#service_log}
        :param slow_query_log: Slow query log enables capturing of slow queries. Setting slow_query_log to false also truncates the mysql.slow_log table. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#slow_query_log ManagedDatabaseMysql#slow_query_log}
        :param sort_buffer_size: Sort buffer size in bytes for ORDER BY optimization. Default is 262144 (256K). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#sort_buffer_size ManagedDatabaseMysql#sort_buffer_size}
        :param sql_mode: Global SQL mode. Set to empty to use MySQL server defaults. When creating a new service and not setting this field Aiven default SQL mode (strict, SQL standard compliant) will be assigned. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#sql_mode ManagedDatabaseMysql#sql_mode}
        :param sql_require_primary_key: Require primary key to be defined for new tables or old tables modified with ALTER TABLE and fail if missing. It is recommended to always have primary keys because various functionality may break if any large table is missing them. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#sql_require_primary_key ManagedDatabaseMysql#sql_require_primary_key}
        :param tmp_table_size: Limits the size of internal in-memory tables. Also set max_heap_table_size. Default is 16777216 (16M). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#tmp_table_size ManagedDatabaseMysql#tmp_table_size}
        :param version: MySQL major version. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#version ManagedDatabaseMysql#version}
        :param wait_timeout: The number of seconds the server waits for activity on a noninteractive connection before closing it. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#wait_timeout ManagedDatabaseMysql#wait_timeout}
        '''
        if isinstance(migration, dict):
            migration = ManagedDatabaseMysqlPropertiesMigration(**migration)
        if isinstance(mysql_incremental_backup, dict):
            mysql_incremental_backup = ManagedDatabaseMysqlPropertiesMysqlIncrementalBackup(**mysql_incremental_backup)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce2580325d4e3944249fb431ec4736f99b4a41b6ee968fc06ae03aecf4930601)
            check_type(argname="argument admin_password", value=admin_password, expected_type=type_hints["admin_password"])
            check_type(argname="argument admin_username", value=admin_username, expected_type=type_hints["admin_username"])
            check_type(argname="argument automatic_utility_network_ip_filter", value=automatic_utility_network_ip_filter, expected_type=type_hints["automatic_utility_network_ip_filter"])
            check_type(argname="argument backup_hour", value=backup_hour, expected_type=type_hints["backup_hour"])
            check_type(argname="argument backup_minute", value=backup_minute, expected_type=type_hints["backup_minute"])
            check_type(argname="argument binlog_retention_period", value=binlog_retention_period, expected_type=type_hints["binlog_retention_period"])
            check_type(argname="argument connect_timeout", value=connect_timeout, expected_type=type_hints["connect_timeout"])
            check_type(argname="argument default_time_zone", value=default_time_zone, expected_type=type_hints["default_time_zone"])
            check_type(argname="argument group_concat_max_len", value=group_concat_max_len, expected_type=type_hints["group_concat_max_len"])
            check_type(argname="argument information_schema_stats_expiry", value=information_schema_stats_expiry, expected_type=type_hints["information_schema_stats_expiry"])
            check_type(argname="argument innodb_change_buffer_max_size", value=innodb_change_buffer_max_size, expected_type=type_hints["innodb_change_buffer_max_size"])
            check_type(argname="argument innodb_flush_neighbors", value=innodb_flush_neighbors, expected_type=type_hints["innodb_flush_neighbors"])
            check_type(argname="argument innodb_ft_min_token_size", value=innodb_ft_min_token_size, expected_type=type_hints["innodb_ft_min_token_size"])
            check_type(argname="argument innodb_ft_server_stopword_table", value=innodb_ft_server_stopword_table, expected_type=type_hints["innodb_ft_server_stopword_table"])
            check_type(argname="argument innodb_lock_wait_timeout", value=innodb_lock_wait_timeout, expected_type=type_hints["innodb_lock_wait_timeout"])
            check_type(argname="argument innodb_log_buffer_size", value=innodb_log_buffer_size, expected_type=type_hints["innodb_log_buffer_size"])
            check_type(argname="argument innodb_online_alter_log_max_size", value=innodb_online_alter_log_max_size, expected_type=type_hints["innodb_online_alter_log_max_size"])
            check_type(argname="argument innodb_print_all_deadlocks", value=innodb_print_all_deadlocks, expected_type=type_hints["innodb_print_all_deadlocks"])
            check_type(argname="argument innodb_read_io_threads", value=innodb_read_io_threads, expected_type=type_hints["innodb_read_io_threads"])
            check_type(argname="argument innodb_rollback_on_timeout", value=innodb_rollback_on_timeout, expected_type=type_hints["innodb_rollback_on_timeout"])
            check_type(argname="argument innodb_thread_concurrency", value=innodb_thread_concurrency, expected_type=type_hints["innodb_thread_concurrency"])
            check_type(argname="argument innodb_write_io_threads", value=innodb_write_io_threads, expected_type=type_hints["innodb_write_io_threads"])
            check_type(argname="argument interactive_timeout", value=interactive_timeout, expected_type=type_hints["interactive_timeout"])
            check_type(argname="argument internal_tmp_mem_storage_engine", value=internal_tmp_mem_storage_engine, expected_type=type_hints["internal_tmp_mem_storage_engine"])
            check_type(argname="argument ip_filter", value=ip_filter, expected_type=type_hints["ip_filter"])
            check_type(argname="argument log_output", value=log_output, expected_type=type_hints["log_output"])
            check_type(argname="argument long_query_time", value=long_query_time, expected_type=type_hints["long_query_time"])
            check_type(argname="argument max_allowed_packet", value=max_allowed_packet, expected_type=type_hints["max_allowed_packet"])
            check_type(argname="argument max_heap_table_size", value=max_heap_table_size, expected_type=type_hints["max_heap_table_size"])
            check_type(argname="argument migration", value=migration, expected_type=type_hints["migration"])
            check_type(argname="argument mysql_incremental_backup", value=mysql_incremental_backup, expected_type=type_hints["mysql_incremental_backup"])
            check_type(argname="argument net_buffer_length", value=net_buffer_length, expected_type=type_hints["net_buffer_length"])
            check_type(argname="argument net_read_timeout", value=net_read_timeout, expected_type=type_hints["net_read_timeout"])
            check_type(argname="argument net_write_timeout", value=net_write_timeout, expected_type=type_hints["net_write_timeout"])
            check_type(argname="argument public_access", value=public_access, expected_type=type_hints["public_access"])
            check_type(argname="argument service_log", value=service_log, expected_type=type_hints["service_log"])
            check_type(argname="argument slow_query_log", value=slow_query_log, expected_type=type_hints["slow_query_log"])
            check_type(argname="argument sort_buffer_size", value=sort_buffer_size, expected_type=type_hints["sort_buffer_size"])
            check_type(argname="argument sql_mode", value=sql_mode, expected_type=type_hints["sql_mode"])
            check_type(argname="argument sql_require_primary_key", value=sql_require_primary_key, expected_type=type_hints["sql_require_primary_key"])
            check_type(argname="argument tmp_table_size", value=tmp_table_size, expected_type=type_hints["tmp_table_size"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            check_type(argname="argument wait_timeout", value=wait_timeout, expected_type=type_hints["wait_timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if admin_password is not None:
            self._values["admin_password"] = admin_password
        if admin_username is not None:
            self._values["admin_username"] = admin_username
        if automatic_utility_network_ip_filter is not None:
            self._values["automatic_utility_network_ip_filter"] = automatic_utility_network_ip_filter
        if backup_hour is not None:
            self._values["backup_hour"] = backup_hour
        if backup_minute is not None:
            self._values["backup_minute"] = backup_minute
        if binlog_retention_period is not None:
            self._values["binlog_retention_period"] = binlog_retention_period
        if connect_timeout is not None:
            self._values["connect_timeout"] = connect_timeout
        if default_time_zone is not None:
            self._values["default_time_zone"] = default_time_zone
        if group_concat_max_len is not None:
            self._values["group_concat_max_len"] = group_concat_max_len
        if information_schema_stats_expiry is not None:
            self._values["information_schema_stats_expiry"] = information_schema_stats_expiry
        if innodb_change_buffer_max_size is not None:
            self._values["innodb_change_buffer_max_size"] = innodb_change_buffer_max_size
        if innodb_flush_neighbors is not None:
            self._values["innodb_flush_neighbors"] = innodb_flush_neighbors
        if innodb_ft_min_token_size is not None:
            self._values["innodb_ft_min_token_size"] = innodb_ft_min_token_size
        if innodb_ft_server_stopword_table is not None:
            self._values["innodb_ft_server_stopword_table"] = innodb_ft_server_stopword_table
        if innodb_lock_wait_timeout is not None:
            self._values["innodb_lock_wait_timeout"] = innodb_lock_wait_timeout
        if innodb_log_buffer_size is not None:
            self._values["innodb_log_buffer_size"] = innodb_log_buffer_size
        if innodb_online_alter_log_max_size is not None:
            self._values["innodb_online_alter_log_max_size"] = innodb_online_alter_log_max_size
        if innodb_print_all_deadlocks is not None:
            self._values["innodb_print_all_deadlocks"] = innodb_print_all_deadlocks
        if innodb_read_io_threads is not None:
            self._values["innodb_read_io_threads"] = innodb_read_io_threads
        if innodb_rollback_on_timeout is not None:
            self._values["innodb_rollback_on_timeout"] = innodb_rollback_on_timeout
        if innodb_thread_concurrency is not None:
            self._values["innodb_thread_concurrency"] = innodb_thread_concurrency
        if innodb_write_io_threads is not None:
            self._values["innodb_write_io_threads"] = innodb_write_io_threads
        if interactive_timeout is not None:
            self._values["interactive_timeout"] = interactive_timeout
        if internal_tmp_mem_storage_engine is not None:
            self._values["internal_tmp_mem_storage_engine"] = internal_tmp_mem_storage_engine
        if ip_filter is not None:
            self._values["ip_filter"] = ip_filter
        if log_output is not None:
            self._values["log_output"] = log_output
        if long_query_time is not None:
            self._values["long_query_time"] = long_query_time
        if max_allowed_packet is not None:
            self._values["max_allowed_packet"] = max_allowed_packet
        if max_heap_table_size is not None:
            self._values["max_heap_table_size"] = max_heap_table_size
        if migration is not None:
            self._values["migration"] = migration
        if mysql_incremental_backup is not None:
            self._values["mysql_incremental_backup"] = mysql_incremental_backup
        if net_buffer_length is not None:
            self._values["net_buffer_length"] = net_buffer_length
        if net_read_timeout is not None:
            self._values["net_read_timeout"] = net_read_timeout
        if net_write_timeout is not None:
            self._values["net_write_timeout"] = net_write_timeout
        if public_access is not None:
            self._values["public_access"] = public_access
        if service_log is not None:
            self._values["service_log"] = service_log
        if slow_query_log is not None:
            self._values["slow_query_log"] = slow_query_log
        if sort_buffer_size is not None:
            self._values["sort_buffer_size"] = sort_buffer_size
        if sql_mode is not None:
            self._values["sql_mode"] = sql_mode
        if sql_require_primary_key is not None:
            self._values["sql_require_primary_key"] = sql_require_primary_key
        if tmp_table_size is not None:
            self._values["tmp_table_size"] = tmp_table_size
        if version is not None:
            self._values["version"] = version
        if wait_timeout is not None:
            self._values["wait_timeout"] = wait_timeout

    @builtins.property
    def admin_password(self) -> typing.Optional[builtins.str]:
        '''Custom password for admin user.

        Defaults to random string. This must be set only when a new service is being created.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#admin_password ManagedDatabaseMysql#admin_password}
        '''
        result = self._values.get("admin_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def admin_username(self) -> typing.Optional[builtins.str]:
        '''Custom username for admin user. This must be set only when a new service is being created.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#admin_username ManagedDatabaseMysql#admin_username}
        '''
        result = self._values.get("admin_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def automatic_utility_network_ip_filter(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Automatic utility network IP Filter. Automatically allow connections from servers in the utility network within the same zone.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#automatic_utility_network_ip_filter ManagedDatabaseMysql#automatic_utility_network_ip_filter}
        '''
        result = self._values.get("automatic_utility_network_ip_filter")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def backup_hour(self) -> typing.Optional[jsii.Number]:
        '''The hour of day (in UTC) when backup for the service is started.

        New backup is only started if previous backup has already completed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#backup_hour ManagedDatabaseMysql#backup_hour}
        '''
        result = self._values.get("backup_hour")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def backup_minute(self) -> typing.Optional[jsii.Number]:
        '''The minute of an hour when backup for the service is started.

        New backup is only started if previous backup has already completed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#backup_minute ManagedDatabaseMysql#backup_minute}
        '''
        result = self._values.get("backup_minute")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def binlog_retention_period(self) -> typing.Optional[jsii.Number]:
        '''The minimum amount of time in seconds to keep binlog entries before deletion.

        This may be extended for services that require binlog entries for longer than the default for example if using the MySQL Debezium Kafka connector.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#binlog_retention_period ManagedDatabaseMysql#binlog_retention_period}
        '''
        result = self._values.get("binlog_retention_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def connect_timeout(self) -> typing.Optional[jsii.Number]:
        '''The number of seconds that the mysqld server waits for a connect packet before responding with Bad handshake.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#connect_timeout ManagedDatabaseMysql#connect_timeout}
        '''
        result = self._values.get("connect_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def default_time_zone(self) -> typing.Optional[builtins.str]:
        '''Default server time zone as an offset from UTC (from -12:00 to +12:00), a time zone name, or 'SYSTEM' to use the MySQL server default.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#default_time_zone ManagedDatabaseMysql#default_time_zone}
        '''
        result = self._values.get("default_time_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def group_concat_max_len(self) -> typing.Optional[jsii.Number]:
        '''The maximum permitted result length in bytes for the GROUP_CONCAT() function.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#group_concat_max_len ManagedDatabaseMysql#group_concat_max_len}
        '''
        result = self._values.get("group_concat_max_len")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def information_schema_stats_expiry(self) -> typing.Optional[jsii.Number]:
        '''The time, in seconds, before cached statistics expire.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#information_schema_stats_expiry ManagedDatabaseMysql#information_schema_stats_expiry}
        '''
        result = self._values.get("information_schema_stats_expiry")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def innodb_change_buffer_max_size(self) -> typing.Optional[jsii.Number]:
        '''Maximum size for the InnoDB change buffer, as a percentage of the total size of the buffer pool.

        Default is 25.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_change_buffer_max_size ManagedDatabaseMysql#innodb_change_buffer_max_size}
        '''
        result = self._values.get("innodb_change_buffer_max_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def innodb_flush_neighbors(self) -> typing.Optional[jsii.Number]:
        '''Specifies whether flushing a page from the InnoDB buffer pool also flushes other dirty pages in the same extent (default is 1): 0 - dirty pages in the same extent are not flushed, 1 - flush contiguous dirty pages in the same extent, 2 - flush dirty pages in the same extent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_flush_neighbors ManagedDatabaseMysql#innodb_flush_neighbors}
        '''
        result = self._values.get("innodb_flush_neighbors")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def innodb_ft_min_token_size(self) -> typing.Optional[jsii.Number]:
        '''Minimum length of words that are stored in an InnoDB FULLTEXT index.

        Changing this parameter will lead to a restart of the MySQL service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_ft_min_token_size ManagedDatabaseMysql#innodb_ft_min_token_size}
        '''
        result = self._values.get("innodb_ft_min_token_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def innodb_ft_server_stopword_table(self) -> typing.Optional[builtins.str]:
        '''This option is used to specify your own InnoDB FULLTEXT index stopword list for all InnoDB tables.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_ft_server_stopword_table ManagedDatabaseMysql#innodb_ft_server_stopword_table}
        '''
        result = self._values.get("innodb_ft_server_stopword_table")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def innodb_lock_wait_timeout(self) -> typing.Optional[jsii.Number]:
        '''The length of time in seconds an InnoDB transaction waits for a row lock before giving up.

        Default is 120.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_lock_wait_timeout ManagedDatabaseMysql#innodb_lock_wait_timeout}
        '''
        result = self._values.get("innodb_lock_wait_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def innodb_log_buffer_size(self) -> typing.Optional[jsii.Number]:
        '''The size in bytes of the buffer that InnoDB uses to write to the log files on disk.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_log_buffer_size ManagedDatabaseMysql#innodb_log_buffer_size}
        '''
        result = self._values.get("innodb_log_buffer_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def innodb_online_alter_log_max_size(self) -> typing.Optional[jsii.Number]:
        '''The upper limit in bytes on the size of the temporary log files used during online DDL operations for InnoDB tables.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_online_alter_log_max_size ManagedDatabaseMysql#innodb_online_alter_log_max_size}
        '''
        result = self._values.get("innodb_online_alter_log_max_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def innodb_print_all_deadlocks(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''When enabled, information about all deadlocks in InnoDB user transactions is recorded in the error log. Disabled by default.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_print_all_deadlocks ManagedDatabaseMysql#innodb_print_all_deadlocks}
        '''
        result = self._values.get("innodb_print_all_deadlocks")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def innodb_read_io_threads(self) -> typing.Optional[jsii.Number]:
        '''The number of I/O threads for read operations in InnoDB.

        Default is 4. Changing this parameter will lead to a restart of the MySQL service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_read_io_threads ManagedDatabaseMysql#innodb_read_io_threads}
        '''
        result = self._values.get("innodb_read_io_threads")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def innodb_rollback_on_timeout(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''When enabled a transaction timeout causes InnoDB to abort and roll back the entire transaction.

        Changing this parameter will lead to a restart of the MySQL service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_rollback_on_timeout ManagedDatabaseMysql#innodb_rollback_on_timeout}
        '''
        result = self._values.get("innodb_rollback_on_timeout")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def innodb_thread_concurrency(self) -> typing.Optional[jsii.Number]:
        '''Defines the maximum number of threads permitted inside of InnoDB. Default is 0 (infinite concurrency - no limit).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_thread_concurrency ManagedDatabaseMysql#innodb_thread_concurrency}
        '''
        result = self._values.get("innodb_thread_concurrency")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def innodb_write_io_threads(self) -> typing.Optional[jsii.Number]:
        '''The number of I/O threads for write operations in InnoDB.

        Default is 4. Changing this parameter will lead to a restart of the MySQL service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#innodb_write_io_threads ManagedDatabaseMysql#innodb_write_io_threads}
        '''
        result = self._values.get("innodb_write_io_threads")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def interactive_timeout(self) -> typing.Optional[jsii.Number]:
        '''The number of seconds the server waits for activity on an interactive connection before closing it.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#interactive_timeout ManagedDatabaseMysql#interactive_timeout}
        '''
        result = self._values.get("interactive_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def internal_tmp_mem_storage_engine(self) -> typing.Optional[builtins.str]:
        '''The storage engine for in-memory internal temporary tables.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#internal_tmp_mem_storage_engine ManagedDatabaseMysql#internal_tmp_mem_storage_engine}
        '''
        result = self._values.get("internal_tmp_mem_storage_engine")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ip_filter(self) -> typing.Optional[typing.List[builtins.str]]:
        '''IP filter. Allow incoming connections from CIDR address block, e.g. '10.20.0.0/16'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#ip_filter ManagedDatabaseMysql#ip_filter}
        '''
        result = self._values.get("ip_filter")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def log_output(self) -> typing.Optional[builtins.str]:
        '''The slow log output destination when slow_query_log is ON.

        To enable MySQL AI Insights, choose INSIGHTS. To use MySQL AI Insights and the mysql.slow_log table at the same time, choose INSIGHTS,TABLE. To only use the mysql.slow_log table, choose TABLE. To silence slow logs, choose NONE.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#log_output ManagedDatabaseMysql#log_output}
        '''
        result = self._values.get("log_output")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def long_query_time(self) -> typing.Optional[jsii.Number]:
        '''The slow_query_logs work as SQL statements that take more than long_query_time seconds to execute.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#long_query_time ManagedDatabaseMysql#long_query_time}
        '''
        result = self._values.get("long_query_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_allowed_packet(self) -> typing.Optional[jsii.Number]:
        '''Size of the largest message in bytes that can be received by the server. Default is 67108864 (64M).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#max_allowed_packet ManagedDatabaseMysql#max_allowed_packet}
        '''
        result = self._values.get("max_allowed_packet")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_heap_table_size(self) -> typing.Optional[jsii.Number]:
        '''Limits the size of internal in-memory tables. Also set tmp_table_size. Default is 16777216 (16M).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#max_heap_table_size ManagedDatabaseMysql#max_heap_table_size}
        '''
        result = self._values.get("max_heap_table_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def migration(self) -> typing.Optional["ManagedDatabaseMysqlPropertiesMigration"]:
        '''migration block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#migration ManagedDatabaseMysql#migration}
        '''
        result = self._values.get("migration")
        return typing.cast(typing.Optional["ManagedDatabaseMysqlPropertiesMigration"], result)

    @builtins.property
    def mysql_incremental_backup(
        self,
    ) -> typing.Optional["ManagedDatabaseMysqlPropertiesMysqlIncrementalBackup"]:
        '''mysql_incremental_backup block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#mysql_incremental_backup ManagedDatabaseMysql#mysql_incremental_backup}
        '''
        result = self._values.get("mysql_incremental_backup")
        return typing.cast(typing.Optional["ManagedDatabaseMysqlPropertiesMysqlIncrementalBackup"], result)

    @builtins.property
    def net_buffer_length(self) -> typing.Optional[jsii.Number]:
        '''Start sizes of connection buffer and result buffer.

        Default is 16384 (16K). Changing this parameter will lead to a restart of the MySQL service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#net_buffer_length ManagedDatabaseMysql#net_buffer_length}
        '''
        result = self._values.get("net_buffer_length")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def net_read_timeout(self) -> typing.Optional[jsii.Number]:
        '''The number of seconds to wait for more data from a connection before aborting the read.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#net_read_timeout ManagedDatabaseMysql#net_read_timeout}
        '''
        result = self._values.get("net_read_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def net_write_timeout(self) -> typing.Optional[jsii.Number]:
        '''The number of seconds to wait for a block to be written to a connection before aborting the write.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#net_write_timeout ManagedDatabaseMysql#net_write_timeout}
        '''
        result = self._values.get("net_write_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def public_access(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Public Access. Allow access to the service from the public Internet.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#public_access ManagedDatabaseMysql#public_access}
        '''
        result = self._values.get("public_access")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def service_log(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Service logging. Store logs for the service so that they are available in the HTTP API and console.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#service_log ManagedDatabaseMysql#service_log}
        '''
        result = self._values.get("service_log")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def slow_query_log(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Slow query log enables capturing of slow queries. Setting slow_query_log to false also truncates the mysql.slow_log table.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#slow_query_log ManagedDatabaseMysql#slow_query_log}
        '''
        result = self._values.get("slow_query_log")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def sort_buffer_size(self) -> typing.Optional[jsii.Number]:
        '''Sort buffer size in bytes for ORDER BY optimization. Default is 262144 (256K).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#sort_buffer_size ManagedDatabaseMysql#sort_buffer_size}
        '''
        result = self._values.get("sort_buffer_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def sql_mode(self) -> typing.Optional[builtins.str]:
        '''Global SQL mode.

        Set to empty to use MySQL server defaults. When creating a new service and not setting this field Aiven default SQL mode (strict, SQL standard compliant) will be assigned.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#sql_mode ManagedDatabaseMysql#sql_mode}
        '''
        result = self._values.get("sql_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sql_require_primary_key(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Require primary key to be defined for new tables or old tables modified with ALTER TABLE and fail if missing.

        It is recommended to always have primary keys because various functionality may break if any large table is missing them.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#sql_require_primary_key ManagedDatabaseMysql#sql_require_primary_key}
        '''
        result = self._values.get("sql_require_primary_key")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tmp_table_size(self) -> typing.Optional[jsii.Number]:
        '''Limits the size of internal in-memory tables. Also set max_heap_table_size. Default is 16777216 (16M).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#tmp_table_size ManagedDatabaseMysql#tmp_table_size}
        '''
        result = self._values.get("tmp_table_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''MySQL major version.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#version ManagedDatabaseMysql#version}
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def wait_timeout(self) -> typing.Optional[jsii.Number]:
        '''The number of seconds the server waits for activity on a noninteractive connection before closing it.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#wait_timeout ManagedDatabaseMysql#wait_timeout}
        '''
        result = self._values.get("wait_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseMysqlProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseMysql.ManagedDatabaseMysqlPropertiesMigration",
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
class ManagedDatabaseMysqlPropertiesMigration:
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
        :param dbname: Database name for bootstrapping the initial connection. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#dbname ManagedDatabaseMysql#dbname}
        :param host: Hostname or IP address of the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#host ManagedDatabaseMysql#host}
        :param ignore_dbs: Comma-separated list of databases, which should be ignored during migration (supported by MySQL and PostgreSQL only at the moment). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#ignore_dbs ManagedDatabaseMysql#ignore_dbs}
        :param ignore_roles: Comma-separated list of database roles, which should be ignored during migration (supported by PostgreSQL only at the moment). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#ignore_roles ManagedDatabaseMysql#ignore_roles}
        :param method: The migration method to be used (currently supported only by Redis, Dragonfly, MySQL and PostgreSQL service types). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#method ManagedDatabaseMysql#method}
        :param password: Password for authentication with the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#password ManagedDatabaseMysql#password}
        :param port: Port number of the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#port ManagedDatabaseMysql#port}
        :param ssl: The server where to migrate data from is secured with SSL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#ssl ManagedDatabaseMysql#ssl}
        :param username: User name for authentication with the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#username ManagedDatabaseMysql#username}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee5a974af6d286f0c9f5d3877bba799be0317b62fea7a2094229566a454f29ae)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#dbname ManagedDatabaseMysql#dbname}
        '''
        result = self._values.get("dbname")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def host(self) -> typing.Optional[builtins.str]:
        '''Hostname or IP address of the server where to migrate data from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#host ManagedDatabaseMysql#host}
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ignore_dbs(self) -> typing.Optional[builtins.str]:
        '''Comma-separated list of databases, which should be ignored during migration (supported by MySQL and PostgreSQL only at the moment).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#ignore_dbs ManagedDatabaseMysql#ignore_dbs}
        '''
        result = self._values.get("ignore_dbs")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ignore_roles(self) -> typing.Optional[builtins.str]:
        '''Comma-separated list of database roles, which should be ignored during migration (supported by PostgreSQL only at the moment).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#ignore_roles ManagedDatabaseMysql#ignore_roles}
        '''
        result = self._values.get("ignore_roles")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def method(self) -> typing.Optional[builtins.str]:
        '''The migration method to be used (currently supported only by Redis, Dragonfly, MySQL and PostgreSQL service types).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#method ManagedDatabaseMysql#method}
        '''
        result = self._values.get("method")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''Password for authentication with the server where to migrate data from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#password ManagedDatabaseMysql#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''Port number of the server where to migrate data from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#port ManagedDatabaseMysql#port}
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ssl(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''The server where to migrate data from is secured with SSL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#ssl ManagedDatabaseMysql#ssl}
        '''
        result = self._values.get("ssl")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''User name for authentication with the server where to migrate data from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#username ManagedDatabaseMysql#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseMysqlPropertiesMigration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseMysqlPropertiesMigrationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseMysql.ManagedDatabaseMysqlPropertiesMigrationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6a01fc1b8e4fe6076b8d9bd954ccaba985925db529af16e76d918c88b96b4663)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ed74acd004a8935099f52967944968cb588e434802de042e76563b2d3662a147)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dbname", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01962d74812e4792ed317a7081fc6b520bffc4c243c3b97aba89b51005d035a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ignoreDbs")
    def ignore_dbs(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ignoreDbs"))

    @ignore_dbs.setter
    def ignore_dbs(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8317a24c10ef2071420b92dfe3c216bab96b5b38b359c59911d72c6053b5b60c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ignoreDbs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ignoreRoles")
    def ignore_roles(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ignoreRoles"))

    @ignore_roles.setter
    def ignore_roles(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83e243984a5d4e4adcc47a7f5ca7da671145c65dfe5b14eccf70edc058f064ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ignoreRoles", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "method"))

    @method.setter
    def method(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f26b3e2a45bc82a02636d9a7680ead48319e322e80c13fd16d7903680e47f553)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "method", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd6b4044cd38e70ec4e0635fadb1f1ec5e57e12d13a8b2866cfb7a39398e99bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3b76b32ace200420e536521de4f6fa3bba38a583e70cee38558f93a74579bbf)
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
            type_hints = typing.get_type_hints(_typecheckingstub__13b5262b5f856305124efe73b5fd349ba8e06aca56657419960a8b0a617e25cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ssl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa2b1683b14f90dc010901dec71bf384b67aaa37568f2c9dd270e7fb8eca2230)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseMysqlPropertiesMigration]:
        return typing.cast(typing.Optional[ManagedDatabaseMysqlPropertiesMigration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseMysqlPropertiesMigration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14ec505c37370540c64c79ea9b2bfc9828b39dfd6ffbaf4ac56000b8528d5cbd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.managedDatabaseMysql.ManagedDatabaseMysqlPropertiesMysqlIncrementalBackup",
    jsii_struct_bases=[],
    name_mapping={
        "enabled": "enabled",
        "full_backup_week_schedule": "fullBackupWeekSchedule",
    },
)
class ManagedDatabaseMysqlPropertiesMysqlIncrementalBackup:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        full_backup_week_schedule: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Enable incremental backups. Enable periodic incremental backups. When enabled, full_backup_week_schedule must be set. Incremental backups only store changes since the last backup, making them faster and more storage-efficient than full backups. This is particularly useful for large databases where daily full backups would be too time-consuming or expensive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#enabled ManagedDatabaseMysql#enabled}
        :param full_backup_week_schedule: Full backup week schedule. Comma-separated list of days of the week when full backups should be created. Valid values: mon, tue, wed, thu, fri, sat, sun. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#full_backup_week_schedule ManagedDatabaseMysql#full_backup_week_schedule}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1964e1dfe21845d236cd3d7cace81e77064622d963b8c0cd67bd1f44641d8232)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument full_backup_week_schedule", value=full_backup_week_schedule, expected_type=type_hints["full_backup_week_schedule"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if full_backup_week_schedule is not None:
            self._values["full_backup_week_schedule"] = full_backup_week_schedule

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable incremental backups.

        Enable periodic incremental backups. When enabled, full_backup_week_schedule must be set. Incremental backups only store changes since the last backup, making them faster and more storage-efficient than full backups. This is particularly useful for large databases where daily full backups would be too time-consuming or expensive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#enabled ManagedDatabaseMysql#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def full_backup_week_schedule(self) -> typing.Optional[builtins.str]:
        '''Full backup week schedule.

        Comma-separated list of days of the week when full backups should be created. Valid values: mon, tue, wed, thu, fri, sat, sun.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#full_backup_week_schedule ManagedDatabaseMysql#full_backup_week_schedule}
        '''
        result = self._values.get("full_backup_week_schedule")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseMysqlPropertiesMysqlIncrementalBackup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseMysqlPropertiesMysqlIncrementalBackupOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseMysql.ManagedDatabaseMysqlPropertiesMysqlIncrementalBackupOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fb845a6b5012c2b17a325a96ad64118ca2a3a1421e9e96b57cafc7d17b34f292)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetFullBackupWeekSchedule")
    def reset_full_backup_week_schedule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFullBackupWeekSchedule", []))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="fullBackupWeekScheduleInput")
    def full_backup_week_schedule_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fullBackupWeekScheduleInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__4e00ca2cc46f9276d43329a202dba92fa69a8cab98988d3fa72c39ec0911feaf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="fullBackupWeekSchedule")
    def full_backup_week_schedule(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fullBackupWeekSchedule"))

    @full_backup_week_schedule.setter
    def full_backup_week_schedule(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38553b4e914ae923324afea74d0c621150923b235a44022144561c25951346cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fullBackupWeekSchedule", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseMysqlPropertiesMysqlIncrementalBackup]:
        return typing.cast(typing.Optional[ManagedDatabaseMysqlPropertiesMysqlIncrementalBackup], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseMysqlPropertiesMysqlIncrementalBackup],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b885de8733f78cdb8686c81eedaff62ae0a5632ea7e5c1b4383953b8359ff7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ManagedDatabaseMysqlPropertiesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.managedDatabaseMysql.ManagedDatabaseMysqlPropertiesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4dd4ed80cb9fd34d7d226704675ed2775db5ea2ccb1b933269edb7e0acd9c4fd)
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
        :param dbname: Database name for bootstrapping the initial connection. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#dbname ManagedDatabaseMysql#dbname}
        :param host: Hostname or IP address of the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#host ManagedDatabaseMysql#host}
        :param ignore_dbs: Comma-separated list of databases, which should be ignored during migration (supported by MySQL and PostgreSQL only at the moment). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#ignore_dbs ManagedDatabaseMysql#ignore_dbs}
        :param ignore_roles: Comma-separated list of database roles, which should be ignored during migration (supported by PostgreSQL only at the moment). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#ignore_roles ManagedDatabaseMysql#ignore_roles}
        :param method: The migration method to be used (currently supported only by Redis, Dragonfly, MySQL and PostgreSQL service types). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#method ManagedDatabaseMysql#method}
        :param password: Password for authentication with the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#password ManagedDatabaseMysql#password}
        :param port: Port number of the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#port ManagedDatabaseMysql#port}
        :param ssl: The server where to migrate data from is secured with SSL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#ssl ManagedDatabaseMysql#ssl}
        :param username: User name for authentication with the server where to migrate data from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#username ManagedDatabaseMysql#username}
        '''
        value = ManagedDatabaseMysqlPropertiesMigration(
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

    @jsii.member(jsii_name="putMysqlIncrementalBackup")
    def put_mysql_incremental_backup(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        full_backup_week_schedule: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Enable incremental backups. Enable periodic incremental backups. When enabled, full_backup_week_schedule must be set. Incremental backups only store changes since the last backup, making them faster and more storage-efficient than full backups. This is particularly useful for large databases where daily full backups would be too time-consuming or expensive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#enabled ManagedDatabaseMysql#enabled}
        :param full_backup_week_schedule: Full backup week schedule. Comma-separated list of days of the week when full backups should be created. Valid values: mon, tue, wed, thu, fri, sat, sun. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/managed_database_mysql#full_backup_week_schedule ManagedDatabaseMysql#full_backup_week_schedule}
        '''
        value = ManagedDatabaseMysqlPropertiesMysqlIncrementalBackup(
            enabled=enabled, full_backup_week_schedule=full_backup_week_schedule
        )

        return typing.cast(None, jsii.invoke(self, "putMysqlIncrementalBackup", [value]))

    @jsii.member(jsii_name="resetAdminPassword")
    def reset_admin_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdminPassword", []))

    @jsii.member(jsii_name="resetAdminUsername")
    def reset_admin_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdminUsername", []))

    @jsii.member(jsii_name="resetAutomaticUtilityNetworkIpFilter")
    def reset_automatic_utility_network_ip_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutomaticUtilityNetworkIpFilter", []))

    @jsii.member(jsii_name="resetBackupHour")
    def reset_backup_hour(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupHour", []))

    @jsii.member(jsii_name="resetBackupMinute")
    def reset_backup_minute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupMinute", []))

    @jsii.member(jsii_name="resetBinlogRetentionPeriod")
    def reset_binlog_retention_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBinlogRetentionPeriod", []))

    @jsii.member(jsii_name="resetConnectTimeout")
    def reset_connect_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectTimeout", []))

    @jsii.member(jsii_name="resetDefaultTimeZone")
    def reset_default_time_zone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultTimeZone", []))

    @jsii.member(jsii_name="resetGroupConcatMaxLen")
    def reset_group_concat_max_len(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGroupConcatMaxLen", []))

    @jsii.member(jsii_name="resetInformationSchemaStatsExpiry")
    def reset_information_schema_stats_expiry(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInformationSchemaStatsExpiry", []))

    @jsii.member(jsii_name="resetInnodbChangeBufferMaxSize")
    def reset_innodb_change_buffer_max_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInnodbChangeBufferMaxSize", []))

    @jsii.member(jsii_name="resetInnodbFlushNeighbors")
    def reset_innodb_flush_neighbors(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInnodbFlushNeighbors", []))

    @jsii.member(jsii_name="resetInnodbFtMinTokenSize")
    def reset_innodb_ft_min_token_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInnodbFtMinTokenSize", []))

    @jsii.member(jsii_name="resetInnodbFtServerStopwordTable")
    def reset_innodb_ft_server_stopword_table(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInnodbFtServerStopwordTable", []))

    @jsii.member(jsii_name="resetInnodbLockWaitTimeout")
    def reset_innodb_lock_wait_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInnodbLockWaitTimeout", []))

    @jsii.member(jsii_name="resetInnodbLogBufferSize")
    def reset_innodb_log_buffer_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInnodbLogBufferSize", []))

    @jsii.member(jsii_name="resetInnodbOnlineAlterLogMaxSize")
    def reset_innodb_online_alter_log_max_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInnodbOnlineAlterLogMaxSize", []))

    @jsii.member(jsii_name="resetInnodbPrintAllDeadlocks")
    def reset_innodb_print_all_deadlocks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInnodbPrintAllDeadlocks", []))

    @jsii.member(jsii_name="resetInnodbReadIoThreads")
    def reset_innodb_read_io_threads(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInnodbReadIoThreads", []))

    @jsii.member(jsii_name="resetInnodbRollbackOnTimeout")
    def reset_innodb_rollback_on_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInnodbRollbackOnTimeout", []))

    @jsii.member(jsii_name="resetInnodbThreadConcurrency")
    def reset_innodb_thread_concurrency(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInnodbThreadConcurrency", []))

    @jsii.member(jsii_name="resetInnodbWriteIoThreads")
    def reset_innodb_write_io_threads(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInnodbWriteIoThreads", []))

    @jsii.member(jsii_name="resetInteractiveTimeout")
    def reset_interactive_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInteractiveTimeout", []))

    @jsii.member(jsii_name="resetInternalTmpMemStorageEngine")
    def reset_internal_tmp_mem_storage_engine(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInternalTmpMemStorageEngine", []))

    @jsii.member(jsii_name="resetIpFilter")
    def reset_ip_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpFilter", []))

    @jsii.member(jsii_name="resetLogOutput")
    def reset_log_output(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogOutput", []))

    @jsii.member(jsii_name="resetLongQueryTime")
    def reset_long_query_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLongQueryTime", []))

    @jsii.member(jsii_name="resetMaxAllowedPacket")
    def reset_max_allowed_packet(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxAllowedPacket", []))

    @jsii.member(jsii_name="resetMaxHeapTableSize")
    def reset_max_heap_table_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxHeapTableSize", []))

    @jsii.member(jsii_name="resetMigration")
    def reset_migration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMigration", []))

    @jsii.member(jsii_name="resetMysqlIncrementalBackup")
    def reset_mysql_incremental_backup(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMysqlIncrementalBackup", []))

    @jsii.member(jsii_name="resetNetBufferLength")
    def reset_net_buffer_length(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetBufferLength", []))

    @jsii.member(jsii_name="resetNetReadTimeout")
    def reset_net_read_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetReadTimeout", []))

    @jsii.member(jsii_name="resetNetWriteTimeout")
    def reset_net_write_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetWriteTimeout", []))

    @jsii.member(jsii_name="resetPublicAccess")
    def reset_public_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicAccess", []))

    @jsii.member(jsii_name="resetServiceLog")
    def reset_service_log(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceLog", []))

    @jsii.member(jsii_name="resetSlowQueryLog")
    def reset_slow_query_log(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSlowQueryLog", []))

    @jsii.member(jsii_name="resetSortBufferSize")
    def reset_sort_buffer_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSortBufferSize", []))

    @jsii.member(jsii_name="resetSqlMode")
    def reset_sql_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSqlMode", []))

    @jsii.member(jsii_name="resetSqlRequirePrimaryKey")
    def reset_sql_require_primary_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSqlRequirePrimaryKey", []))

    @jsii.member(jsii_name="resetTmpTableSize")
    def reset_tmp_table_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTmpTableSize", []))

    @jsii.member(jsii_name="resetVersion")
    def reset_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersion", []))

    @jsii.member(jsii_name="resetWaitTimeout")
    def reset_wait_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWaitTimeout", []))

    @builtins.property
    @jsii.member(jsii_name="migration")
    def migration(self) -> ManagedDatabaseMysqlPropertiesMigrationOutputReference:
        return typing.cast(ManagedDatabaseMysqlPropertiesMigrationOutputReference, jsii.get(self, "migration"))

    @builtins.property
    @jsii.member(jsii_name="mysqlIncrementalBackup")
    def mysql_incremental_backup(
        self,
    ) -> ManagedDatabaseMysqlPropertiesMysqlIncrementalBackupOutputReference:
        return typing.cast(ManagedDatabaseMysqlPropertiesMysqlIncrementalBackupOutputReference, jsii.get(self, "mysqlIncrementalBackup"))

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
    @jsii.member(jsii_name="backupHourInput")
    def backup_hour_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "backupHourInput"))

    @builtins.property
    @jsii.member(jsii_name="backupMinuteInput")
    def backup_minute_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "backupMinuteInput"))

    @builtins.property
    @jsii.member(jsii_name="binlogRetentionPeriodInput")
    def binlog_retention_period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "binlogRetentionPeriodInput"))

    @builtins.property
    @jsii.member(jsii_name="connectTimeoutInput")
    def connect_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "connectTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultTimeZoneInput")
    def default_time_zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultTimeZoneInput"))

    @builtins.property
    @jsii.member(jsii_name="groupConcatMaxLenInput")
    def group_concat_max_len_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "groupConcatMaxLenInput"))

    @builtins.property
    @jsii.member(jsii_name="informationSchemaStatsExpiryInput")
    def information_schema_stats_expiry_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "informationSchemaStatsExpiryInput"))

    @builtins.property
    @jsii.member(jsii_name="innodbChangeBufferMaxSizeInput")
    def innodb_change_buffer_max_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "innodbChangeBufferMaxSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="innodbFlushNeighborsInput")
    def innodb_flush_neighbors_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "innodbFlushNeighborsInput"))

    @builtins.property
    @jsii.member(jsii_name="innodbFtMinTokenSizeInput")
    def innodb_ft_min_token_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "innodbFtMinTokenSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="innodbFtServerStopwordTableInput")
    def innodb_ft_server_stopword_table_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "innodbFtServerStopwordTableInput"))

    @builtins.property
    @jsii.member(jsii_name="innodbLockWaitTimeoutInput")
    def innodb_lock_wait_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "innodbLockWaitTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="innodbLogBufferSizeInput")
    def innodb_log_buffer_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "innodbLogBufferSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="innodbOnlineAlterLogMaxSizeInput")
    def innodb_online_alter_log_max_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "innodbOnlineAlterLogMaxSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="innodbPrintAllDeadlocksInput")
    def innodb_print_all_deadlocks_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "innodbPrintAllDeadlocksInput"))

    @builtins.property
    @jsii.member(jsii_name="innodbReadIoThreadsInput")
    def innodb_read_io_threads_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "innodbReadIoThreadsInput"))

    @builtins.property
    @jsii.member(jsii_name="innodbRollbackOnTimeoutInput")
    def innodb_rollback_on_timeout_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "innodbRollbackOnTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="innodbThreadConcurrencyInput")
    def innodb_thread_concurrency_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "innodbThreadConcurrencyInput"))

    @builtins.property
    @jsii.member(jsii_name="innodbWriteIoThreadsInput")
    def innodb_write_io_threads_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "innodbWriteIoThreadsInput"))

    @builtins.property
    @jsii.member(jsii_name="interactiveTimeoutInput")
    def interactive_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "interactiveTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="internalTmpMemStorageEngineInput")
    def internal_tmp_mem_storage_engine_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "internalTmpMemStorageEngineInput"))

    @builtins.property
    @jsii.member(jsii_name="ipFilterInput")
    def ip_filter_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ipFilterInput"))

    @builtins.property
    @jsii.member(jsii_name="logOutputInput")
    def log_output_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logOutputInput"))

    @builtins.property
    @jsii.member(jsii_name="longQueryTimeInput")
    def long_query_time_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "longQueryTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="maxAllowedPacketInput")
    def max_allowed_packet_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxAllowedPacketInput"))

    @builtins.property
    @jsii.member(jsii_name="maxHeapTableSizeInput")
    def max_heap_table_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxHeapTableSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="migrationInput")
    def migration_input(
        self,
    ) -> typing.Optional[ManagedDatabaseMysqlPropertiesMigration]:
        return typing.cast(typing.Optional[ManagedDatabaseMysqlPropertiesMigration], jsii.get(self, "migrationInput"))

    @builtins.property
    @jsii.member(jsii_name="mysqlIncrementalBackupInput")
    def mysql_incremental_backup_input(
        self,
    ) -> typing.Optional[ManagedDatabaseMysqlPropertiesMysqlIncrementalBackup]:
        return typing.cast(typing.Optional[ManagedDatabaseMysqlPropertiesMysqlIncrementalBackup], jsii.get(self, "mysqlIncrementalBackupInput"))

    @builtins.property
    @jsii.member(jsii_name="netBufferLengthInput")
    def net_buffer_length_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "netBufferLengthInput"))

    @builtins.property
    @jsii.member(jsii_name="netReadTimeoutInput")
    def net_read_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "netReadTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="netWriteTimeoutInput")
    def net_write_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "netWriteTimeoutInput"))

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
    @jsii.member(jsii_name="slowQueryLogInput")
    def slow_query_log_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "slowQueryLogInput"))

    @builtins.property
    @jsii.member(jsii_name="sortBufferSizeInput")
    def sort_buffer_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sortBufferSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="sqlModeInput")
    def sql_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sqlModeInput"))

    @builtins.property
    @jsii.member(jsii_name="sqlRequirePrimaryKeyInput")
    def sql_require_primary_key_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "sqlRequirePrimaryKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="tmpTableSizeInput")
    def tmp_table_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "tmpTableSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property
    @jsii.member(jsii_name="waitTimeoutInput")
    def wait_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "waitTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="adminPassword")
    def admin_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adminPassword"))

    @admin_password.setter
    def admin_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4eff5f4868d5bb12ae52075fad32cc522ff4d67c1f0725343b65ceccf3d26131)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "adminPassword", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="adminUsername")
    def admin_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adminUsername"))

    @admin_username.setter
    def admin_username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6ecefb7a241c029a6f8bdf60f03bc1c901031688d400c73e2077054204b2d4d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0077171c6793e105b57c58f26c5eccab995b513ae21d2edd5eb376835c26fb57)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "automaticUtilityNetworkIpFilter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backupHour")
    def backup_hour(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "backupHour"))

    @backup_hour.setter
    def backup_hour(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bfda925789726fc478fb6e9c25ed310b3c2d5d0d2eb38e33f3f06991670b1fc0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backupHour", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backupMinute")
    def backup_minute(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "backupMinute"))

    @backup_minute.setter
    def backup_minute(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8387e10b822b051ef1d7d248d600bc6a627ce3d53ef51bdb3d35baa6c8a9c79)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backupMinute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="binlogRetentionPeriod")
    def binlog_retention_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "binlogRetentionPeriod"))

    @binlog_retention_period.setter
    def binlog_retention_period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__adb2b7fe28d35ffbd5dc61b42e471da9235b519934c0cf2b54e66a6cba2769d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "binlogRetentionPeriod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="connectTimeout")
    def connect_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "connectTimeout"))

    @connect_timeout.setter
    def connect_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__244c5cca2f2bb6b2cbf36edfebcd16134288c4f0cdcd06fc9bc5e887138a6533)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultTimeZone")
    def default_time_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultTimeZone"))

    @default_time_zone.setter
    def default_time_zone(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c24961559469f2c54fad02db5d36db8f2be6223c7d562b818f83fd070c49503f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultTimeZone", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="groupConcatMaxLen")
    def group_concat_max_len(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "groupConcatMaxLen"))

    @group_concat_max_len.setter
    def group_concat_max_len(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e434daac5f96db599fa63ee8f3950fca6a852291747a0d175f039361c9765872)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "groupConcatMaxLen", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="informationSchemaStatsExpiry")
    def information_schema_stats_expiry(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "informationSchemaStatsExpiry"))

    @information_schema_stats_expiry.setter
    def information_schema_stats_expiry(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a88a50f90b2c7002fe3db3e94a4ea87c7423326f9aa1ce934da5a129f5bf3c17)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "informationSchemaStatsExpiry", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="innodbChangeBufferMaxSize")
    def innodb_change_buffer_max_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "innodbChangeBufferMaxSize"))

    @innodb_change_buffer_max_size.setter
    def innodb_change_buffer_max_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3746ba590c0ee59f4ebd0fc2a77ca7c2351bc1f348d60cfb3cd712bca687743)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "innodbChangeBufferMaxSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="innodbFlushNeighbors")
    def innodb_flush_neighbors(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "innodbFlushNeighbors"))

    @innodb_flush_neighbors.setter
    def innodb_flush_neighbors(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__feb5034ec10b5b26fc8e3b8128725a5f19fa53e4a0fc95855cddab729dd93e6a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "innodbFlushNeighbors", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="innodbFtMinTokenSize")
    def innodb_ft_min_token_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "innodbFtMinTokenSize"))

    @innodb_ft_min_token_size.setter
    def innodb_ft_min_token_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__157f20e90e8a5fdf1e18b16ba297d2b6e248258f423cd9546f20ea5a1321d001)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "innodbFtMinTokenSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="innodbFtServerStopwordTable")
    def innodb_ft_server_stopword_table(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "innodbFtServerStopwordTable"))

    @innodb_ft_server_stopword_table.setter
    def innodb_ft_server_stopword_table(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49588ac2cf49f2d73a79f0f70ae6ed4a8f60a8eaf1f827f99c0c1ddab9fceffb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "innodbFtServerStopwordTable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="innodbLockWaitTimeout")
    def innodb_lock_wait_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "innodbLockWaitTimeout"))

    @innodb_lock_wait_timeout.setter
    def innodb_lock_wait_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8805feb0a905d8bb176cdd8478ef200d24902405aa6c969241c6feb3fa51c558)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "innodbLockWaitTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="innodbLogBufferSize")
    def innodb_log_buffer_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "innodbLogBufferSize"))

    @innodb_log_buffer_size.setter
    def innodb_log_buffer_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4836318ace4b5113ec6900a579bfbfdb9eef4e5b61285ca8a2e35a5eb19c8d9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "innodbLogBufferSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="innodbOnlineAlterLogMaxSize")
    def innodb_online_alter_log_max_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "innodbOnlineAlterLogMaxSize"))

    @innodb_online_alter_log_max_size.setter
    def innodb_online_alter_log_max_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63fe9f771fba7af459b76c36f0a04274b20a86290be56a2f7ae3ceaef8819752)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "innodbOnlineAlterLogMaxSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="innodbPrintAllDeadlocks")
    def innodb_print_all_deadlocks(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "innodbPrintAllDeadlocks"))

    @innodb_print_all_deadlocks.setter
    def innodb_print_all_deadlocks(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7769a033f5366008076bb4ef7b8919e72819d5ddc0e454d3ef11e133205c37a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "innodbPrintAllDeadlocks", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="innodbReadIoThreads")
    def innodb_read_io_threads(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "innodbReadIoThreads"))

    @innodb_read_io_threads.setter
    def innodb_read_io_threads(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__290d8e8fa2c8d1dc4cc1d8c88e345dad38aa92a1fea90ed574d033ddcf8f5002)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "innodbReadIoThreads", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="innodbRollbackOnTimeout")
    def innodb_rollback_on_timeout(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "innodbRollbackOnTimeout"))

    @innodb_rollback_on_timeout.setter
    def innodb_rollback_on_timeout(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c11180360ba295b9f58a8b122c238af9812b0690ae4ff10ec71d92ab0d22ae4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "innodbRollbackOnTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="innodbThreadConcurrency")
    def innodb_thread_concurrency(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "innodbThreadConcurrency"))

    @innodb_thread_concurrency.setter
    def innodb_thread_concurrency(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcc986e128bf332cd06fd464c2a5585373baca759c9251263454173a2fc9b76f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "innodbThreadConcurrency", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="innodbWriteIoThreads")
    def innodb_write_io_threads(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "innodbWriteIoThreads"))

    @innodb_write_io_threads.setter
    def innodb_write_io_threads(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__445b0b8ad0a5511a9ee649231ead8b458ebd595ed181e7125236de52cd994f63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "innodbWriteIoThreads", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="interactiveTimeout")
    def interactive_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "interactiveTimeout"))

    @interactive_timeout.setter
    def interactive_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7ae88e786b8f906e86e53fac22e5a36d705e4669a5b3666b6887fb5711c0c77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "interactiveTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalTmpMemStorageEngine")
    def internal_tmp_mem_storage_engine(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "internalTmpMemStorageEngine"))

    @internal_tmp_mem_storage_engine.setter
    def internal_tmp_mem_storage_engine(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fd6b53bbf642281b0c693d7bc5e4d74286630c223315e934132f731948f3da1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalTmpMemStorageEngine", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipFilter")
    def ip_filter(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ipFilter"))

    @ip_filter.setter
    def ip_filter(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62d1186ba338160863d0f6ca2b6a930329e5a12f1766e1a56c6310b1a82b309b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipFilter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logOutput")
    def log_output(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logOutput"))

    @log_output.setter
    def log_output(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd74b822d5bffe20b4e08b8e008bdf292388bf335c14fe7d958a38c2866e0189)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logOutput", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="longQueryTime")
    def long_query_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "longQueryTime"))

    @long_query_time.setter
    def long_query_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f1f337cf4d9efc75ecd5295ef8ec9b2114e9409e0f743fc9cff9d37adbe5d93)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "longQueryTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxAllowedPacket")
    def max_allowed_packet(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxAllowedPacket"))

    @max_allowed_packet.setter
    def max_allowed_packet(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2d632aa9b0e2406312012c1cee1c53f68ed87a9a3ebb403f82dc0c902336c78)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxAllowedPacket", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxHeapTableSize")
    def max_heap_table_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxHeapTableSize"))

    @max_heap_table_size.setter
    def max_heap_table_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba739f0bae2ab6909061790026a04e7da9eec4d3e9c8703fda506687f42e5cc0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxHeapTableSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="netBufferLength")
    def net_buffer_length(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "netBufferLength"))

    @net_buffer_length.setter
    def net_buffer_length(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0a040f8c2b33ac991cfe7b731460da1ecc8bab940cb58a30c67f101eb64bd7b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "netBufferLength", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="netReadTimeout")
    def net_read_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "netReadTimeout"))

    @net_read_timeout.setter
    def net_read_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3d32e5573df63e11c69495b478bc001c2ed85ddd03d593da5ecdfce22282ae0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "netReadTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="netWriteTimeout")
    def net_write_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "netWriteTimeout"))

    @net_write_timeout.setter
    def net_write_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a3c79c909087d181e7f57ae35f51997dda8c0b4d6e22e17bdac74319cb1b694)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "netWriteTimeout", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__f0c7a48b8afc4486c1ed957a0b6ee942cf9d81126fb4c501e657ffbc32023a14)
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
            type_hints = typing.get_type_hints(_typecheckingstub__82329f86254d0f011ea44eda334ce520aac47b19d38a1f8284d24d309a640a31)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceLog", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="slowQueryLog")
    def slow_query_log(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "slowQueryLog"))

    @slow_query_log.setter
    def slow_query_log(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00f5ea01b27fd60b6ec439436eb79d5e007e0a6b0434c19b0a353c64ef989768)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "slowQueryLog", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sortBufferSize")
    def sort_buffer_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sortBufferSize"))

    @sort_buffer_size.setter
    def sort_buffer_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__454284c4d62429bbfb3990c93433c9fb60e9e3d69eee5b61d2b6538ea74c83b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sortBufferSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sqlMode")
    def sql_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sqlMode"))

    @sql_mode.setter
    def sql_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c937bd0437ff728ad468d59cd2f18f0dd99bdb5ddcb838518e146db72fb76ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sqlMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sqlRequirePrimaryKey")
    def sql_require_primary_key(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "sqlRequirePrimaryKey"))

    @sql_require_primary_key.setter
    def sql_require_primary_key(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb564b1b6a7a67f152de9a5baf1c9b00517aaa656a156837ff104367f809673e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sqlRequirePrimaryKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tmpTableSize")
    def tmp_table_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tmpTableSize"))

    @tmp_table_size.setter
    def tmp_table_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c2d839cc9c7bdb6e36ed25e9bc4de414e41a83ebefda4cfe9cd68c820eb097e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tmpTableSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb5a1560d7d0fa20b32fcb714ab971ef9b90ea20ab247751460b543c169066a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="waitTimeout")
    def wait_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "waitTimeout"))

    @wait_timeout.setter
    def wait_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b38f4600f98ee7be6bb71c72ce2612be3c1b2b8ded826ca388238b108bb20cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "waitTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ManagedDatabaseMysqlProperties]:
        return typing.cast(typing.Optional[ManagedDatabaseMysqlProperties], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseMysqlProperties],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2baaab4cfec9a45413f195dbf67b84628ad02d42383bf17f055f05297b03bb0f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ManagedDatabaseMysql",
    "ManagedDatabaseMysqlComponents",
    "ManagedDatabaseMysqlComponentsList",
    "ManagedDatabaseMysqlComponentsOutputReference",
    "ManagedDatabaseMysqlConfig",
    "ManagedDatabaseMysqlNetwork",
    "ManagedDatabaseMysqlNetworkList",
    "ManagedDatabaseMysqlNetworkOutputReference",
    "ManagedDatabaseMysqlNodeStates",
    "ManagedDatabaseMysqlNodeStatesList",
    "ManagedDatabaseMysqlNodeStatesOutputReference",
    "ManagedDatabaseMysqlProperties",
    "ManagedDatabaseMysqlPropertiesMigration",
    "ManagedDatabaseMysqlPropertiesMigrationOutputReference",
    "ManagedDatabaseMysqlPropertiesMysqlIncrementalBackup",
    "ManagedDatabaseMysqlPropertiesMysqlIncrementalBackupOutputReference",
    "ManagedDatabaseMysqlPropertiesOutputReference",
]

publication.publish()

def _typecheckingstub__958e87e9d4c67c8f4dc9a92e0864dd5ec7b73c3fe017b196cd999a20a67aec35(
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
    network: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedDatabaseMysqlNetwork, typing.Dict[builtins.str, typing.Any]]]]] = None,
    powered: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    properties: typing.Optional[typing.Union[ManagedDatabaseMysqlProperties, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__dc745a4a2be4154ae040b4398757488ee2a87a34d3b8c1e1f51b52a2a2f60166(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a62fc7161400d7b4f860d59782c7df65db78aee0396e1926e60cae30f5d85e4f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedDatabaseMysqlNetwork, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7a4fb60d1135c0f8631d36600a5812527c23ae3a5aa4b793722b50e65fd246d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fcb88e825a08094ea35b5029118afc3cd252fe3cb6af4672e840930dae68ffb(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48df4258c07649eccd564db2bfea58f2d8c6e7775d42e302c4732ba2a3bfa35e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10c67ec6c447fed554dbe7abe9233193df48d93398b1a1c03b2cc52fc4a56f21(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b3317f4107eb3f0324a64874708fab95f67e816faecf7678312b22212af296f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a44dc38d52585561bb352263c2d4c0c7166d02e7d2ba26b1f06b0827bd1645c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__beb13051c8d159249aa225bdbcf28aeb76bc85a1aae08e9c31f60dfe116dfecc(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c9f7e6065020fa925bf719fbd0aa777653e104f39664706dabe6a435de915cf(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7141cc36a0c3b744c0e90aacfea1d6055f2e1bb6d23321a515475bd8c72cec64(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7732a2cf2cda58a00518cf2d610dba1c27c5673a60c4385a62472ceb732076d4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34b41667608ff4cd5e9008da8d533f9c668a11f12f74531e6d80da050862de08(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__688fdae24b26e710345c109b7473013f94e8839a01038fa5240f646ae832ee6a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80d18976397eb5bc969ead28206ee1c2ebb44271012265fe7c6bc2410af32085(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__017d94a1bed5a80567186f11930d76599611f085d87754b6317c3f1d30eac0f1(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__deb58afab231debdc3de38ded6700565608b4d5e89d03bcdea43e26c8f29e2cc(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ec6165c0e005f2cdab8e4bf91377627b2fee91a4c49330a894a38d618cb266d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae4277256ebc37247795b9bcfd0b223c65762e3553860601183ea80dd360dc0d(
    value: typing.Optional[ManagedDatabaseMysqlComponents],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10b2894ddd0553e9581d0116772434efafda3295976e9367656213631c5dc624(
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
    network: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedDatabaseMysqlNetwork, typing.Dict[builtins.str, typing.Any]]]]] = None,
    powered: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    properties: typing.Optional[typing.Union[ManagedDatabaseMysqlProperties, typing.Dict[builtins.str, typing.Any]]] = None,
    termination_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74301fe81253b8784b9afba8d3a1dda97ee52965714102f2fb71f3cda82c72d9(
    *,
    family: builtins.str,
    name: builtins.str,
    type: builtins.str,
    uuid: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53c76b9a36fa2c5763e2ef8caea118bd60028c1ba65bcd4a2bf797076f44e2f7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__127d61284845f513acef2e7d6fe15b6f6cc76e910f2d89ece042176d8bef7967(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6f90b60425a2e38d3af43a492643c17d866cb129ac68edbb3072b9614eb3113(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00c8b7b77f169dfb8910e16238b1e78991dc8e7e37374ca83ca93de027477e5c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f21cfe7d74b33287ba0ab770e586d1d2ccf031bf53abb32c3632361e3061f6a8(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94c97a6da3042ffb69736a0b72c58cc97a1025de77ce3dea7b71a494beeb8ca7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedDatabaseMysqlNetwork]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2dd5c3a8b28af9ee2d43d563baf32e395fe43a74440a5ce7f47afaec5e1a113a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32b05c92713a900a94460be120f24b5ea22785668076ee827760f5d736e28ec7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__927d6daa33e2f827191036084c87fe58d852f38b6a3609825470a2d55c533dc2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1327b0d72083b5bdf8929efed7cdf969a5d3933e8d9b5192dff0931eb3ba6a9b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05b71e4f1fb19a4fffec705975e756f2280605d835c59bdd94a71df18627a8bc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afce920649c215f1f7f3adde9483ce3407c61af39dfacb0bcaa881777aa4f8dd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedDatabaseMysqlNetwork]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__989e2763cac47db0558f0e09bb2669c13639bb78716a422e8f8c4eb11ef4418a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03bece7009f60e171555f364ad6c8bd3ebd4909c341071b47f847719e5090152(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6bc42894cd75446060a318bed07cb53e96f5e05d71db1adc1e71664475609f06(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41e9094332f45eaa5d58fe2d5d98992caaa8fba697503fe24ff24b0640684980(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__287baddcdede19148df005876a5ab7752a44533620e042b8c358bd67bd66bc48(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fa4e7b4eb3edbb0a4e64637e5c937e026f3ebdf8313cb45509c105223b6f1ad(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b164fbe1f2de1cd7f849e6d1a275455f99e36b5fea9891f0c6efac51327f5e0(
    value: typing.Optional[ManagedDatabaseMysqlNodeStates],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce2580325d4e3944249fb431ec4736f99b4a41b6ee968fc06ae03aecf4930601(
    *,
    admin_password: typing.Optional[builtins.str] = None,
    admin_username: typing.Optional[builtins.str] = None,
    automatic_utility_network_ip_filter: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    backup_hour: typing.Optional[jsii.Number] = None,
    backup_minute: typing.Optional[jsii.Number] = None,
    binlog_retention_period: typing.Optional[jsii.Number] = None,
    connect_timeout: typing.Optional[jsii.Number] = None,
    default_time_zone: typing.Optional[builtins.str] = None,
    group_concat_max_len: typing.Optional[jsii.Number] = None,
    information_schema_stats_expiry: typing.Optional[jsii.Number] = None,
    innodb_change_buffer_max_size: typing.Optional[jsii.Number] = None,
    innodb_flush_neighbors: typing.Optional[jsii.Number] = None,
    innodb_ft_min_token_size: typing.Optional[jsii.Number] = None,
    innodb_ft_server_stopword_table: typing.Optional[builtins.str] = None,
    innodb_lock_wait_timeout: typing.Optional[jsii.Number] = None,
    innodb_log_buffer_size: typing.Optional[jsii.Number] = None,
    innodb_online_alter_log_max_size: typing.Optional[jsii.Number] = None,
    innodb_print_all_deadlocks: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    innodb_read_io_threads: typing.Optional[jsii.Number] = None,
    innodb_rollback_on_timeout: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    innodb_thread_concurrency: typing.Optional[jsii.Number] = None,
    innodb_write_io_threads: typing.Optional[jsii.Number] = None,
    interactive_timeout: typing.Optional[jsii.Number] = None,
    internal_tmp_mem_storage_engine: typing.Optional[builtins.str] = None,
    ip_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
    log_output: typing.Optional[builtins.str] = None,
    long_query_time: typing.Optional[jsii.Number] = None,
    max_allowed_packet: typing.Optional[jsii.Number] = None,
    max_heap_table_size: typing.Optional[jsii.Number] = None,
    migration: typing.Optional[typing.Union[ManagedDatabaseMysqlPropertiesMigration, typing.Dict[builtins.str, typing.Any]]] = None,
    mysql_incremental_backup: typing.Optional[typing.Union[ManagedDatabaseMysqlPropertiesMysqlIncrementalBackup, typing.Dict[builtins.str, typing.Any]]] = None,
    net_buffer_length: typing.Optional[jsii.Number] = None,
    net_read_timeout: typing.Optional[jsii.Number] = None,
    net_write_timeout: typing.Optional[jsii.Number] = None,
    public_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    service_log: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    slow_query_log: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sort_buffer_size: typing.Optional[jsii.Number] = None,
    sql_mode: typing.Optional[builtins.str] = None,
    sql_require_primary_key: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tmp_table_size: typing.Optional[jsii.Number] = None,
    version: typing.Optional[builtins.str] = None,
    wait_timeout: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee5a974af6d286f0c9f5d3877bba799be0317b62fea7a2094229566a454f29ae(
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

def _typecheckingstub__6a01fc1b8e4fe6076b8d9bd954ccaba985925db529af16e76d918c88b96b4663(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed74acd004a8935099f52967944968cb588e434802de042e76563b2d3662a147(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01962d74812e4792ed317a7081fc6b520bffc4c243c3b97aba89b51005d035a4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8317a24c10ef2071420b92dfe3c216bab96b5b38b359c59911d72c6053b5b60c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83e243984a5d4e4adcc47a7f5ca7da671145c65dfe5b14eccf70edc058f064ab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f26b3e2a45bc82a02636d9a7680ead48319e322e80c13fd16d7903680e47f553(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd6b4044cd38e70ec4e0635fadb1f1ec5e57e12d13a8b2866cfb7a39398e99bb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3b76b32ace200420e536521de4f6fa3bba38a583e70cee38558f93a74579bbf(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13b5262b5f856305124efe73b5fd349ba8e06aca56657419960a8b0a617e25cc(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa2b1683b14f90dc010901dec71bf384b67aaa37568f2c9dd270e7fb8eca2230(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14ec505c37370540c64c79ea9b2bfc9828b39dfd6ffbaf4ac56000b8528d5cbd(
    value: typing.Optional[ManagedDatabaseMysqlPropertiesMigration],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1964e1dfe21845d236cd3d7cace81e77064622d963b8c0cd67bd1f44641d8232(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    full_backup_week_schedule: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb845a6b5012c2b17a325a96ad64118ca2a3a1421e9e96b57cafc7d17b34f292(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e00ca2cc46f9276d43329a202dba92fa69a8cab98988d3fa72c39ec0911feaf(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38553b4e914ae923324afea74d0c621150923b235a44022144561c25951346cc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b885de8733f78cdb8686c81eedaff62ae0a5632ea7e5c1b4383953b8359ff7c(
    value: typing.Optional[ManagedDatabaseMysqlPropertiesMysqlIncrementalBackup],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4dd4ed80cb9fd34d7d226704675ed2775db5ea2ccb1b933269edb7e0acd9c4fd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4eff5f4868d5bb12ae52075fad32cc522ff4d67c1f0725343b65ceccf3d26131(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6ecefb7a241c029a6f8bdf60f03bc1c901031688d400c73e2077054204b2d4d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0077171c6793e105b57c58f26c5eccab995b513ae21d2edd5eb376835c26fb57(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bfda925789726fc478fb6e9c25ed310b3c2d5d0d2eb38e33f3f06991670b1fc0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8387e10b822b051ef1d7d248d600bc6a627ce3d53ef51bdb3d35baa6c8a9c79(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__adb2b7fe28d35ffbd5dc61b42e471da9235b519934c0cf2b54e66a6cba2769d3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__244c5cca2f2bb6b2cbf36edfebcd16134288c4f0cdcd06fc9bc5e887138a6533(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c24961559469f2c54fad02db5d36db8f2be6223c7d562b818f83fd070c49503f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e434daac5f96db599fa63ee8f3950fca6a852291747a0d175f039361c9765872(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a88a50f90b2c7002fe3db3e94a4ea87c7423326f9aa1ce934da5a129f5bf3c17(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3746ba590c0ee59f4ebd0fc2a77ca7c2351bc1f348d60cfb3cd712bca687743(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__feb5034ec10b5b26fc8e3b8128725a5f19fa53e4a0fc95855cddab729dd93e6a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__157f20e90e8a5fdf1e18b16ba297d2b6e248258f423cd9546f20ea5a1321d001(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49588ac2cf49f2d73a79f0f70ae6ed4a8f60a8eaf1f827f99c0c1ddab9fceffb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8805feb0a905d8bb176cdd8478ef200d24902405aa6c969241c6feb3fa51c558(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4836318ace4b5113ec6900a579bfbfdb9eef4e5b61285ca8a2e35a5eb19c8d9f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63fe9f771fba7af459b76c36f0a04274b20a86290be56a2f7ae3ceaef8819752(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7769a033f5366008076bb4ef7b8919e72819d5ddc0e454d3ef11e133205c37a6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__290d8e8fa2c8d1dc4cc1d8c88e345dad38aa92a1fea90ed574d033ddcf8f5002(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c11180360ba295b9f58a8b122c238af9812b0690ae4ff10ec71d92ab0d22ae4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcc986e128bf332cd06fd464c2a5585373baca759c9251263454173a2fc9b76f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__445b0b8ad0a5511a9ee649231ead8b458ebd595ed181e7125236de52cd994f63(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7ae88e786b8f906e86e53fac22e5a36d705e4669a5b3666b6887fb5711c0c77(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fd6b53bbf642281b0c693d7bc5e4d74286630c223315e934132f731948f3da1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62d1186ba338160863d0f6ca2b6a930329e5a12f1766e1a56c6310b1a82b309b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd74b822d5bffe20b4e08b8e008bdf292388bf335c14fe7d958a38c2866e0189(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f1f337cf4d9efc75ecd5295ef8ec9b2114e9409e0f743fc9cff9d37adbe5d93(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2d632aa9b0e2406312012c1cee1c53f68ed87a9a3ebb403f82dc0c902336c78(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba739f0bae2ab6909061790026a04e7da9eec4d3e9c8703fda506687f42e5cc0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0a040f8c2b33ac991cfe7b731460da1ecc8bab940cb58a30c67f101eb64bd7b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3d32e5573df63e11c69495b478bc001c2ed85ddd03d593da5ecdfce22282ae0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a3c79c909087d181e7f57ae35f51997dda8c0b4d6e22e17bdac74319cb1b694(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0c7a48b8afc4486c1ed957a0b6ee942cf9d81126fb4c501e657ffbc32023a14(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82329f86254d0f011ea44eda334ce520aac47b19d38a1f8284d24d309a640a31(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00f5ea01b27fd60b6ec439436eb79d5e007e0a6b0434c19b0a353c64ef989768(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__454284c4d62429bbfb3990c93433c9fb60e9e3d69eee5b61d2b6538ea74c83b2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c937bd0437ff728ad468d59cd2f18f0dd99bdb5ddcb838518e146db72fb76ba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb564b1b6a7a67f152de9a5baf1c9b00517aaa656a156837ff104367f809673e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c2d839cc9c7bdb6e36ed25e9bc4de414e41a83ebefda4cfe9cd68c820eb097e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb5a1560d7d0fa20b32fcb714ab971ef9b90ea20ab247751460b543c169066a7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b38f4600f98ee7be6bb71c72ce2612be3c1b2b8ded826ca388238b108bb20cd(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2baaab4cfec9a45413f195dbf67b84628ad02d42383bf17f055f05297b03bb0f(
    value: typing.Optional[ManagedDatabaseMysqlProperties],
) -> None:
    """Type checking stubs"""
    pass
