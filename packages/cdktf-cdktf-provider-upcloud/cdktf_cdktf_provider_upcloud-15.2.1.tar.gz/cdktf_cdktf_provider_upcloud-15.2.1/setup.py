import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdktf-cdktf-provider-upcloud",
    "version": "15.2.1",
    "description": "Prebuilt upcloud Provider for Terraform CDK (cdktf)",
    "license": "MPL-2.0",
    "url": "https://github.com/cdktf/cdktf-provider-upcloud.git",
    "long_description_content_type": "text/markdown",
    "author": "HashiCorp",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/cdktf/cdktf-provider-upcloud.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdktf_cdktf_provider_upcloud",
        "cdktf_cdktf_provider_upcloud._jsii",
        "cdktf_cdktf_provider_upcloud.data_upcloud_hosts",
        "cdktf_cdktf_provider_upcloud.data_upcloud_ip_addresses",
        "cdktf_cdktf_provider_upcloud.data_upcloud_kubernetes_cluster",
        "cdktf_cdktf_provider_upcloud.data_upcloud_load_balancer_dns_challenge_domain",
        "cdktf_cdktf_provider_upcloud.data_upcloud_managed_database_mysql_sessions",
        "cdktf_cdktf_provider_upcloud.data_upcloud_managed_database_opensearch_indices",
        "cdktf_cdktf_provider_upcloud.data_upcloud_managed_database_postgresql_sessions",
        "cdktf_cdktf_provider_upcloud.data_upcloud_managed_database_redis_sessions",
        "cdktf_cdktf_provider_upcloud.data_upcloud_managed_database_valkey_sessions",
        "cdktf_cdktf_provider_upcloud.data_upcloud_managed_object_storage_policies",
        "cdktf_cdktf_provider_upcloud.data_upcloud_managed_object_storage_regions",
        "cdktf_cdktf_provider_upcloud.data_upcloud_networks",
        "cdktf_cdktf_provider_upcloud.data_upcloud_storage",
        "cdktf_cdktf_provider_upcloud.data_upcloud_tags",
        "cdktf_cdktf_provider_upcloud.data_upcloud_zone",
        "cdktf_cdktf_provider_upcloud.data_upcloud_zones",
        "cdktf_cdktf_provider_upcloud.firewall_rules",
        "cdktf_cdktf_provider_upcloud.floating_ip_address",
        "cdktf_cdktf_provider_upcloud.gateway",
        "cdktf_cdktf_provider_upcloud.gateway_connection",
        "cdktf_cdktf_provider_upcloud.gateway_connection_tunnel",
        "cdktf_cdktf_provider_upcloud.kubernetes_cluster",
        "cdktf_cdktf_provider_upcloud.kubernetes_node_group",
        "cdktf_cdktf_provider_upcloud.loadbalancer",
        "cdktf_cdktf_provider_upcloud.loadbalancer_backend",
        "cdktf_cdktf_provider_upcloud.loadbalancer_backend_tls_config",
        "cdktf_cdktf_provider_upcloud.loadbalancer_dynamic_backend_member",
        "cdktf_cdktf_provider_upcloud.loadbalancer_dynamic_certificate_bundle",
        "cdktf_cdktf_provider_upcloud.loadbalancer_frontend",
        "cdktf_cdktf_provider_upcloud.loadbalancer_frontend_rule",
        "cdktf_cdktf_provider_upcloud.loadbalancer_frontend_tls_config",
        "cdktf_cdktf_provider_upcloud.loadbalancer_manual_certificate_bundle",
        "cdktf_cdktf_provider_upcloud.loadbalancer_resolver",
        "cdktf_cdktf_provider_upcloud.loadbalancer_static_backend_member",
        "cdktf_cdktf_provider_upcloud.managed_database_logical_database",
        "cdktf_cdktf_provider_upcloud.managed_database_mysql",
        "cdktf_cdktf_provider_upcloud.managed_database_opensearch",
        "cdktf_cdktf_provider_upcloud.managed_database_postgresql",
        "cdktf_cdktf_provider_upcloud.managed_database_redis",
        "cdktf_cdktf_provider_upcloud.managed_database_user",
        "cdktf_cdktf_provider_upcloud.managed_database_valkey",
        "cdktf_cdktf_provider_upcloud.managed_object_storage",
        "cdktf_cdktf_provider_upcloud.managed_object_storage_bucket",
        "cdktf_cdktf_provider_upcloud.managed_object_storage_custom_domain",
        "cdktf_cdktf_provider_upcloud.managed_object_storage_policy",
        "cdktf_cdktf_provider_upcloud.managed_object_storage_user",
        "cdktf_cdktf_provider_upcloud.managed_object_storage_user_access_key",
        "cdktf_cdktf_provider_upcloud.managed_object_storage_user_policy",
        "cdktf_cdktf_provider_upcloud.network",
        "cdktf_cdktf_provider_upcloud.network_peering",
        "cdktf_cdktf_provider_upcloud.object_storage",
        "cdktf_cdktf_provider_upcloud.provider",
        "cdktf_cdktf_provider_upcloud.router",
        "cdktf_cdktf_provider_upcloud.server",
        "cdktf_cdktf_provider_upcloud.server_group",
        "cdktf_cdktf_provider_upcloud.storage",
        "cdktf_cdktf_provider_upcloud.storage_backup",
        "cdktf_cdktf_provider_upcloud.storage_template",
        "cdktf_cdktf_provider_upcloud.tag"
    ],
    "package_data": {
        "cdktf_cdktf_provider_upcloud._jsii": [
            "provider-upcloud@15.2.1.jsii.tgz"
        ],
        "cdktf_cdktf_provider_upcloud": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "cdktf>=0.21.0, <0.22.0",
        "constructs>=10.4.2, <11.0.0",
        "jsii>=1.113.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
