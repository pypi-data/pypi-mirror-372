r'''
# CDKTF prebuilt bindings for UpCloudLtd/upcloud provider version 5.24.1

This repo builds and publishes the [Terraform upcloud provider](https://registry.terraform.io/providers/UpCloudLtd/upcloud/5.24.1/docs) bindings for [CDK for Terraform](https://cdk.tf).

## Available Packages

### NPM

The npm package is available at [https://www.npmjs.com/package/@cdktf/provider-upcloud](https://www.npmjs.com/package/@cdktf/provider-upcloud).

`npm install @cdktf/provider-upcloud`

### PyPI

The PyPI package is available at [https://pypi.org/project/cdktf-cdktf-provider-upcloud](https://pypi.org/project/cdktf-cdktf-provider-upcloud).

`pipenv install cdktf-cdktf-provider-upcloud`

### Nuget

The Nuget package is available at [https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Upcloud](https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Upcloud).

`dotnet add package HashiCorp.Cdktf.Providers.Upcloud`

### Maven

The Maven package is available at [https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-upcloud](https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-upcloud).

```
<dependency>
    <groupId>com.hashicorp</groupId>
    <artifactId>cdktf-provider-upcloud</artifactId>
    <version>[REPLACE WITH DESIRED VERSION]</version>
</dependency>
```

### Go

The go package is generated into the [`github.com/cdktf/cdktf-provider-upcloud-go`](https://github.com/cdktf/cdktf-provider-upcloud-go) package.

`go get github.com/cdktf/cdktf-provider-upcloud-go/upcloud/<version>`

Where `<version>` is the version of the prebuilt provider you would like to use e.g. `v11`. The full module name can be found
within the [go.mod](https://github.com/cdktf/cdktf-provider-upcloud-go/blob/main/upcloud/go.mod#L1) file.

## Docs

Find auto-generated docs for this provider here:

* [Typescript](./docs/API.typescript.md)
* [Python](./docs/API.python.md)
* [Java](./docs/API.java.md)
* [C#](./docs/API.csharp.md)
* [Go](./docs/API.go.md)

You can also visit a hosted version of the documentation on [constructs.dev](https://constructs.dev/packages/@cdktf/provider-upcloud).

## Versioning

This project is explicitly not tracking the Terraform upcloud provider version 1:1. In fact, it always tracks `latest` of `~> 5.0` with every release. If there are scenarios where you explicitly have to pin your provider version, you can do so by [generating the provider constructs manually](https://cdk.tf/imports).

These are the upstream dependencies:

* [CDK for Terraform](https://cdk.tf)
* [Terraform upcloud provider](https://registry.terraform.io/providers/UpCloudLtd/upcloud/5.24.1)
* [Terraform Engine](https://terraform.io)

If there are breaking changes (backward incompatible) in any of the above, the major version of this project will be bumped.

## Features / Issues / Bugs

Please report bugs and issues to the [CDK for Terraform](https://cdk.tf) project:

* [Create bug report](https://cdk.tf/bug)
* [Create feature request](https://cdk.tf/feature)

## Contributing

### Projen

This is mostly based on [Projen](https://github.com/projen/projen), which takes care of generating the entire repository.

### cdktf-provider-project based on Projen

There's a custom [project builder](https://github.com/cdktf/cdktf-provider-project) which encapsulate the common settings for all `cdktf` prebuilt providers.

### Provider Version

The provider version can be adjusted in [./.projenrc.js](./.projenrc.js).

### Repository Management

The repository is managed by [CDKTF Repository Manager](https://github.com/cdktf/cdktf-repository-manager/).
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

from ._jsii import *

__all__ = [
    "data_upcloud_hosts",
    "data_upcloud_ip_addresses",
    "data_upcloud_kubernetes_cluster",
    "data_upcloud_load_balancer_dns_challenge_domain",
    "data_upcloud_managed_database_mysql_sessions",
    "data_upcloud_managed_database_opensearch_indices",
    "data_upcloud_managed_database_postgresql_sessions",
    "data_upcloud_managed_database_redis_sessions",
    "data_upcloud_managed_database_valkey_sessions",
    "data_upcloud_managed_object_storage_policies",
    "data_upcloud_managed_object_storage_regions",
    "data_upcloud_networks",
    "data_upcloud_storage",
    "data_upcloud_tags",
    "data_upcloud_zone",
    "data_upcloud_zones",
    "firewall_rules",
    "floating_ip_address",
    "gateway",
    "gateway_connection",
    "gateway_connection_tunnel",
    "kubernetes_cluster",
    "kubernetes_node_group",
    "loadbalancer",
    "loadbalancer_backend",
    "loadbalancer_backend_tls_config",
    "loadbalancer_dynamic_backend_member",
    "loadbalancer_dynamic_certificate_bundle",
    "loadbalancer_frontend",
    "loadbalancer_frontend_rule",
    "loadbalancer_frontend_tls_config",
    "loadbalancer_manual_certificate_bundle",
    "loadbalancer_resolver",
    "loadbalancer_static_backend_member",
    "managed_database_logical_database",
    "managed_database_mysql",
    "managed_database_opensearch",
    "managed_database_postgresql",
    "managed_database_redis",
    "managed_database_user",
    "managed_database_valkey",
    "managed_object_storage",
    "managed_object_storage_bucket",
    "managed_object_storage_custom_domain",
    "managed_object_storage_policy",
    "managed_object_storage_user",
    "managed_object_storage_user_access_key",
    "managed_object_storage_user_policy",
    "network",
    "network_peering",
    "object_storage",
    "provider",
    "router",
    "server",
    "server_group",
    "storage",
    "storage_backup",
    "storage_template",
    "tag",
]

publication.publish()

# Loading modules to ensure their types are registered with the jsii runtime library
from . import data_upcloud_hosts
from . import data_upcloud_ip_addresses
from . import data_upcloud_kubernetes_cluster
from . import data_upcloud_load_balancer_dns_challenge_domain
from . import data_upcloud_managed_database_mysql_sessions
from . import data_upcloud_managed_database_opensearch_indices
from . import data_upcloud_managed_database_postgresql_sessions
from . import data_upcloud_managed_database_redis_sessions
from . import data_upcloud_managed_database_valkey_sessions
from . import data_upcloud_managed_object_storage_policies
from . import data_upcloud_managed_object_storage_regions
from . import data_upcloud_networks
from . import data_upcloud_storage
from . import data_upcloud_tags
from . import data_upcloud_zone
from . import data_upcloud_zones
from . import firewall_rules
from . import floating_ip_address
from . import gateway
from . import gateway_connection
from . import gateway_connection_tunnel
from . import kubernetes_cluster
from . import kubernetes_node_group
from . import loadbalancer
from . import loadbalancer_backend
from . import loadbalancer_backend_tls_config
from . import loadbalancer_dynamic_backend_member
from . import loadbalancer_dynamic_certificate_bundle
from . import loadbalancer_frontend
from . import loadbalancer_frontend_rule
from . import loadbalancer_frontend_tls_config
from . import loadbalancer_manual_certificate_bundle
from . import loadbalancer_resolver
from . import loadbalancer_static_backend_member
from . import managed_database_logical_database
from . import managed_database_mysql
from . import managed_database_opensearch
from . import managed_database_postgresql
from . import managed_database_redis
from . import managed_database_user
from . import managed_database_valkey
from . import managed_object_storage
from . import managed_object_storage_bucket
from . import managed_object_storage_custom_domain
from . import managed_object_storage_policy
from . import managed_object_storage_user
from . import managed_object_storage_user_access_key
from . import managed_object_storage_user_policy
from . import network
from . import network_peering
from . import object_storage
from . import provider
from . import router
from . import server
from . import server_group
from . import storage
from . import storage_backup
from . import storage_template
from . import tag
