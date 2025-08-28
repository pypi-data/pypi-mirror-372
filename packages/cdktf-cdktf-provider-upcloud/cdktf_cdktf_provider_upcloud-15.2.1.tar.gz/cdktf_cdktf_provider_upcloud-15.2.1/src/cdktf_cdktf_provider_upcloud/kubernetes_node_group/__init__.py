r'''
# `upcloud_kubernetes_node_group`

Refer to the Terraform Registry for docs: [`upcloud_kubernetes_node_group`](https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group).
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


class KubernetesNodeGroup(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.kubernetesNodeGroup.KubernetesNodeGroup",
):
    '''Represents a {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group upcloud_kubernetes_node_group}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cluster: builtins.str,
        name: builtins.str,
        node_count: jsii.Number,
        plan: builtins.str,
        anti_affinity: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cloud_native_plan: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["KubernetesNodeGroupCloudNativePlan", typing.Dict[builtins.str, typing.Any]]]]] = None,
        custom_plan: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["KubernetesNodeGroupCustomPlan", typing.Dict[builtins.str, typing.Any]]]]] = None,
        gpu_plan: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["KubernetesNodeGroupGpuPlan", typing.Dict[builtins.str, typing.Any]]]]] = None,
        kubelet_args: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["KubernetesNodeGroupKubeletArgs", typing.Dict[builtins.str, typing.Any]]]]] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        ssh_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        storage_encryption: typing.Optional[builtins.str] = None,
        taint: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["KubernetesNodeGroupTaint", typing.Dict[builtins.str, typing.Any]]]]] = None,
        utility_network_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group upcloud_kubernetes_node_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster: UUID of the cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#cluster KubernetesNodeGroup#cluster}
        :param name: The name of the node group. Needs to be unique within a cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#name KubernetesNodeGroup#name}
        :param node_count: Amount of nodes to provision in the node group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#node_count KubernetesNodeGroup#node_count}
        :param plan: The server plan used for the node group. You can list available plans with ``upctl server plans``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#plan KubernetesNodeGroup#plan}
        :param anti_affinity: If set to true, nodes in this group will be placed on separate compute hosts. Please note that anti-affinity policy is considered 'best effort' and enabling it does not fully guarantee that the nodes will end up on different hardware. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#anti_affinity KubernetesNodeGroup#anti_affinity}
        :param cloud_native_plan: cloud_native_plan block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#cloud_native_plan KubernetesNodeGroup#cloud_native_plan}
        :param custom_plan: custom_plan block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#custom_plan KubernetesNodeGroup#custom_plan}
        :param gpu_plan: gpu_plan block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#gpu_plan KubernetesNodeGroup#gpu_plan}
        :param kubelet_args: kubelet_args block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#kubelet_args KubernetesNodeGroup#kubelet_args}
        :param labels: User defined key-value pairs to classify the node_group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#labels KubernetesNodeGroup#labels}
        :param ssh_keys: You can optionally select SSH keys to be added as authorized keys to the nodes in this node group. This allows you to connect to the nodes via SSH once they are running. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#ssh_keys KubernetesNodeGroup#ssh_keys}
        :param storage_encryption: The storage encryption strategy to use for the nodes in this group. If not set, the cluster's storage encryption strategy will be used, if applicable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#storage_encryption KubernetesNodeGroup#storage_encryption}
        :param taint: taint block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#taint KubernetesNodeGroup#taint}
        :param utility_network_access: If set to false, nodes in this group will not have access to utility network. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#utility_network_access KubernetesNodeGroup#utility_network_access}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8bbcd241d9ab4cfd557f0a030c928c51f93c7d6d9f343e0bcdbdda3cbc8065e3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = KubernetesNodeGroupConfig(
            cluster=cluster,
            name=name,
            node_count=node_count,
            plan=plan,
            anti_affinity=anti_affinity,
            cloud_native_plan=cloud_native_plan,
            custom_plan=custom_plan,
            gpu_plan=gpu_plan,
            kubelet_args=kubelet_args,
            labels=labels,
            ssh_keys=ssh_keys,
            storage_encryption=storage_encryption,
            taint=taint,
            utility_network_access=utility_network_access,
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
        '''Generates CDKTF code for importing a KubernetesNodeGroup resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the KubernetesNodeGroup to import.
        :param import_from_id: The id of the existing KubernetesNodeGroup that should be imported. Refer to the {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the KubernetesNodeGroup to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e4418f3bc7d50550f1d889edee827b87fd9884602972643c6b82f110049ba71)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putCloudNativePlan")
    def put_cloud_native_plan(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["KubernetesNodeGroupCloudNativePlan", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac2f10d642c0079d30e463561c2878e59777f101807a48a08ccb9a8933285e30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCloudNativePlan", [value]))

    @jsii.member(jsii_name="putCustomPlan")
    def put_custom_plan(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["KubernetesNodeGroupCustomPlan", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__710eeb24e681bc1abd473c02c09c72cd25116f5c53784cd07b46e161d215c56f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCustomPlan", [value]))

    @jsii.member(jsii_name="putGpuPlan")
    def put_gpu_plan(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["KubernetesNodeGroupGpuPlan", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c17e1903eed937df8e22fb46de08949295493fcc3197086a410959cf85bd4e98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putGpuPlan", [value]))

    @jsii.member(jsii_name="putKubeletArgs")
    def put_kubelet_args(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["KubernetesNodeGroupKubeletArgs", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32e3828076130e1cbd29ccb900f4d6ed322c27ffe5fa92f4dab04d41c7227a1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putKubeletArgs", [value]))

    @jsii.member(jsii_name="putTaint")
    def put_taint(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["KubernetesNodeGroupTaint", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__374acc0d3de361c5076be47a8876b2f5870798afcd9887148234d9685257a419)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTaint", [value]))

    @jsii.member(jsii_name="resetAntiAffinity")
    def reset_anti_affinity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAntiAffinity", []))

    @jsii.member(jsii_name="resetCloudNativePlan")
    def reset_cloud_native_plan(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudNativePlan", []))

    @jsii.member(jsii_name="resetCustomPlan")
    def reset_custom_plan(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomPlan", []))

    @jsii.member(jsii_name="resetGpuPlan")
    def reset_gpu_plan(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGpuPlan", []))

    @jsii.member(jsii_name="resetKubeletArgs")
    def reset_kubelet_args(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKubeletArgs", []))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetSshKeys")
    def reset_ssh_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSshKeys", []))

    @jsii.member(jsii_name="resetStorageEncryption")
    def reset_storage_encryption(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageEncryption", []))

    @jsii.member(jsii_name="resetTaint")
    def reset_taint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTaint", []))

    @jsii.member(jsii_name="resetUtilityNetworkAccess")
    def reset_utility_network_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUtilityNetworkAccess", []))

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
    @jsii.member(jsii_name="cloudNativePlan")
    def cloud_native_plan(self) -> "KubernetesNodeGroupCloudNativePlanList":
        return typing.cast("KubernetesNodeGroupCloudNativePlanList", jsii.get(self, "cloudNativePlan"))

    @builtins.property
    @jsii.member(jsii_name="customPlan")
    def custom_plan(self) -> "KubernetesNodeGroupCustomPlanList":
        return typing.cast("KubernetesNodeGroupCustomPlanList", jsii.get(self, "customPlan"))

    @builtins.property
    @jsii.member(jsii_name="gpuPlan")
    def gpu_plan(self) -> "KubernetesNodeGroupGpuPlanList":
        return typing.cast("KubernetesNodeGroupGpuPlanList", jsii.get(self, "gpuPlan"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="kubeletArgs")
    def kubelet_args(self) -> "KubernetesNodeGroupKubeletArgsList":
        return typing.cast("KubernetesNodeGroupKubeletArgsList", jsii.get(self, "kubeletArgs"))

    @builtins.property
    @jsii.member(jsii_name="taint")
    def taint(self) -> "KubernetesNodeGroupTaintList":
        return typing.cast("KubernetesNodeGroupTaintList", jsii.get(self, "taint"))

    @builtins.property
    @jsii.member(jsii_name="antiAffinityInput")
    def anti_affinity_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "antiAffinityInput"))

    @builtins.property
    @jsii.member(jsii_name="cloudNativePlanInput")
    def cloud_native_plan_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["KubernetesNodeGroupCloudNativePlan"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["KubernetesNodeGroupCloudNativePlan"]]], jsii.get(self, "cloudNativePlanInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterInput")
    def cluster_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterInput"))

    @builtins.property
    @jsii.member(jsii_name="customPlanInput")
    def custom_plan_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["KubernetesNodeGroupCustomPlan"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["KubernetesNodeGroupCustomPlan"]]], jsii.get(self, "customPlanInput"))

    @builtins.property
    @jsii.member(jsii_name="gpuPlanInput")
    def gpu_plan_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["KubernetesNodeGroupGpuPlan"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["KubernetesNodeGroupGpuPlan"]]], jsii.get(self, "gpuPlanInput"))

    @builtins.property
    @jsii.member(jsii_name="kubeletArgsInput")
    def kubelet_args_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["KubernetesNodeGroupKubeletArgs"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["KubernetesNodeGroupKubeletArgs"]]], jsii.get(self, "kubeletArgsInput"))

    @builtins.property
    @jsii.member(jsii_name="labelsInput")
    def labels_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "labelsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="nodeCountInput")
    def node_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "nodeCountInput"))

    @builtins.property
    @jsii.member(jsii_name="planInput")
    def plan_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "planInput"))

    @builtins.property
    @jsii.member(jsii_name="sshKeysInput")
    def ssh_keys_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "sshKeysInput"))

    @builtins.property
    @jsii.member(jsii_name="storageEncryptionInput")
    def storage_encryption_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageEncryptionInput"))

    @builtins.property
    @jsii.member(jsii_name="taintInput")
    def taint_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["KubernetesNodeGroupTaint"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["KubernetesNodeGroupTaint"]]], jsii.get(self, "taintInput"))

    @builtins.property
    @jsii.member(jsii_name="utilityNetworkAccessInput")
    def utility_network_access_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "utilityNetworkAccessInput"))

    @builtins.property
    @jsii.member(jsii_name="antiAffinity")
    def anti_affinity(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "antiAffinity"))

    @anti_affinity.setter
    def anti_affinity(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e621946f83e58f50c483b681d6a00e44ec81d2dccf1a4f8dafde9e0fb59d55b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "antiAffinity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cluster"))

    @cluster.setter
    def cluster(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__251ecefce0fab4086841f5905fdd68a5182667a221b0cf9910dbc14eee214671)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cluster", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fccb7b922d5d84e539f4c8817753636ee4b2f0dec095ea9ff13030c9d7a17d58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "labels", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02535264f80e698e5cf251336456b8c83e944521501b454ed690a5d74067c620)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nodeCount")
    def node_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "nodeCount"))

    @node_count.setter
    def node_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8670cbb382adf592bc5d0f3e42c4e96d4326983d0e4fe93743648b2ff3d09e74)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nodeCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="plan")
    def plan(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "plan"))

    @plan.setter
    def plan(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd9b94a7a760e7688eaafae17051a6d3f96c6ab95a43f2ccc57fa9c2e964189b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "plan", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sshKeys")
    def ssh_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "sshKeys"))

    @ssh_keys.setter
    def ssh_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3caf64b524bd36e4019e89ade967c6b4e62d55fddf7a8f9e9ed8118d38383759)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sshKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storageEncryption")
    def storage_encryption(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageEncryption"))

    @storage_encryption.setter
    def storage_encryption(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4b669e48a3836306fe80e34225d241ad384a8351e76d8d7b17ffdd8544edf45)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageEncryption", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="utilityNetworkAccess")
    def utility_network_access(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "utilityNetworkAccess"))

    @utility_network_access.setter
    def utility_network_access(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c2a3afca29e180734047644aa682bae1b7fbd5aacc3d234ed7616ba415f5fb6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "utilityNetworkAccess", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.kubernetesNodeGroup.KubernetesNodeGroupCloudNativePlan",
    jsii_struct_bases=[],
    name_mapping={"storage_size": "storageSize", "storage_tier": "storageTier"},
)
class KubernetesNodeGroupCloudNativePlan:
    def __init__(
        self,
        *,
        storage_size: typing.Optional[jsii.Number] = None,
        storage_tier: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param storage_size: The size of the storage device in gigabytes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#storage_size KubernetesNodeGroup#storage_size}
        :param storage_tier: The storage tier to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#storage_tier KubernetesNodeGroup#storage_tier}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5438388f4032834938f080084c7ae0430cf33858715d18b4e84c3c8b7d99c583)
            check_type(argname="argument storage_size", value=storage_size, expected_type=type_hints["storage_size"])
            check_type(argname="argument storage_tier", value=storage_tier, expected_type=type_hints["storage_tier"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if storage_size is not None:
            self._values["storage_size"] = storage_size
        if storage_tier is not None:
            self._values["storage_tier"] = storage_tier

    @builtins.property
    def storage_size(self) -> typing.Optional[jsii.Number]:
        '''The size of the storage device in gigabytes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#storage_size KubernetesNodeGroup#storage_size}
        '''
        result = self._values.get("storage_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def storage_tier(self) -> typing.Optional[builtins.str]:
        '''The storage tier to use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#storage_tier KubernetesNodeGroup#storage_tier}
        '''
        result = self._values.get("storage_tier")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KubernetesNodeGroupCloudNativePlan(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class KubernetesNodeGroupCloudNativePlanList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.kubernetesNodeGroup.KubernetesNodeGroupCloudNativePlanList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8a5a3a16968d45ac84e9b283e63c8c906bd70e1a328640d5e7126d46a1c1fdd1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "KubernetesNodeGroupCloudNativePlanOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fe0c17e964827460fc66444ceb9d46776f4128115267f70dfc0ed4bfcb85920)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("KubernetesNodeGroupCloudNativePlanOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d97187bd0b82a71876e431a81398d9cc1dc821d2610692158cc56a31a863789)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ae893d1d0df821f4f21d426fa80e3eb1d46fa1bbbc724b73e68a3bde2309032c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__beb64ca1f717b4814637a6a29fa9ec5a455b360ac7185bac86f30c38c43272e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[KubernetesNodeGroupCloudNativePlan]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[KubernetesNodeGroupCloudNativePlan]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[KubernetesNodeGroupCloudNativePlan]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d82a371178e1731f4d1566a0c16e13ea3970cdd9188d838221dcd62f32757793)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class KubernetesNodeGroupCloudNativePlanOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.kubernetesNodeGroup.KubernetesNodeGroupCloudNativePlanOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5aaf5281cf9fc6a97d4533c0769d0346349b54e0f7716d35e13101df78d13b1d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetStorageSize")
    def reset_storage_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageSize", []))

    @jsii.member(jsii_name="resetStorageTier")
    def reset_storage_tier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageTier", []))

    @builtins.property
    @jsii.member(jsii_name="storageSizeInput")
    def storage_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "storageSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="storageTierInput")
    def storage_tier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageTierInput"))

    @builtins.property
    @jsii.member(jsii_name="storageSize")
    def storage_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "storageSize"))

    @storage_size.setter
    def storage_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27f7ff508be8287499998f03c15d925e630d2e4e2a70ed3d542615d30fa9bf2d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storageTier")
    def storage_tier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageTier"))

    @storage_tier.setter
    def storage_tier(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38df547be63e43097329d5785a3b9c86f9f334cd3b597e3faffc1473e6c3087c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageTier", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, KubernetesNodeGroupCloudNativePlan]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, KubernetesNodeGroupCloudNativePlan]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, KubernetesNodeGroupCloudNativePlan]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb41ddc5a5a4d49616d4a8b63583841ac403b22e7f09d2806b25388722eb66a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.kubernetesNodeGroup.KubernetesNodeGroupConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "cluster": "cluster",
        "name": "name",
        "node_count": "nodeCount",
        "plan": "plan",
        "anti_affinity": "antiAffinity",
        "cloud_native_plan": "cloudNativePlan",
        "custom_plan": "customPlan",
        "gpu_plan": "gpuPlan",
        "kubelet_args": "kubeletArgs",
        "labels": "labels",
        "ssh_keys": "sshKeys",
        "storage_encryption": "storageEncryption",
        "taint": "taint",
        "utility_network_access": "utilityNetworkAccess",
    },
)
class KubernetesNodeGroupConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        cluster: builtins.str,
        name: builtins.str,
        node_count: jsii.Number,
        plan: builtins.str,
        anti_affinity: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cloud_native_plan: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[KubernetesNodeGroupCloudNativePlan, typing.Dict[builtins.str, typing.Any]]]]] = None,
        custom_plan: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["KubernetesNodeGroupCustomPlan", typing.Dict[builtins.str, typing.Any]]]]] = None,
        gpu_plan: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["KubernetesNodeGroupGpuPlan", typing.Dict[builtins.str, typing.Any]]]]] = None,
        kubelet_args: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["KubernetesNodeGroupKubeletArgs", typing.Dict[builtins.str, typing.Any]]]]] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        ssh_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        storage_encryption: typing.Optional[builtins.str] = None,
        taint: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["KubernetesNodeGroupTaint", typing.Dict[builtins.str, typing.Any]]]]] = None,
        utility_network_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param cluster: UUID of the cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#cluster KubernetesNodeGroup#cluster}
        :param name: The name of the node group. Needs to be unique within a cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#name KubernetesNodeGroup#name}
        :param node_count: Amount of nodes to provision in the node group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#node_count KubernetesNodeGroup#node_count}
        :param plan: The server plan used for the node group. You can list available plans with ``upctl server plans``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#plan KubernetesNodeGroup#plan}
        :param anti_affinity: If set to true, nodes in this group will be placed on separate compute hosts. Please note that anti-affinity policy is considered 'best effort' and enabling it does not fully guarantee that the nodes will end up on different hardware. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#anti_affinity KubernetesNodeGroup#anti_affinity}
        :param cloud_native_plan: cloud_native_plan block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#cloud_native_plan KubernetesNodeGroup#cloud_native_plan}
        :param custom_plan: custom_plan block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#custom_plan KubernetesNodeGroup#custom_plan}
        :param gpu_plan: gpu_plan block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#gpu_plan KubernetesNodeGroup#gpu_plan}
        :param kubelet_args: kubelet_args block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#kubelet_args KubernetesNodeGroup#kubelet_args}
        :param labels: User defined key-value pairs to classify the node_group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#labels KubernetesNodeGroup#labels}
        :param ssh_keys: You can optionally select SSH keys to be added as authorized keys to the nodes in this node group. This allows you to connect to the nodes via SSH once they are running. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#ssh_keys KubernetesNodeGroup#ssh_keys}
        :param storage_encryption: The storage encryption strategy to use for the nodes in this group. If not set, the cluster's storage encryption strategy will be used, if applicable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#storage_encryption KubernetesNodeGroup#storage_encryption}
        :param taint: taint block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#taint KubernetesNodeGroup#taint}
        :param utility_network_access: If set to false, nodes in this group will not have access to utility network. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#utility_network_access KubernetesNodeGroup#utility_network_access}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2489ae5bd3c17ee9de104387734150d3686d0bce3df0c0db5244751c51da43c4)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument node_count", value=node_count, expected_type=type_hints["node_count"])
            check_type(argname="argument plan", value=plan, expected_type=type_hints["plan"])
            check_type(argname="argument anti_affinity", value=anti_affinity, expected_type=type_hints["anti_affinity"])
            check_type(argname="argument cloud_native_plan", value=cloud_native_plan, expected_type=type_hints["cloud_native_plan"])
            check_type(argname="argument custom_plan", value=custom_plan, expected_type=type_hints["custom_plan"])
            check_type(argname="argument gpu_plan", value=gpu_plan, expected_type=type_hints["gpu_plan"])
            check_type(argname="argument kubelet_args", value=kubelet_args, expected_type=type_hints["kubelet_args"])
            check_type(argname="argument labels", value=labels, expected_type=type_hints["labels"])
            check_type(argname="argument ssh_keys", value=ssh_keys, expected_type=type_hints["ssh_keys"])
            check_type(argname="argument storage_encryption", value=storage_encryption, expected_type=type_hints["storage_encryption"])
            check_type(argname="argument taint", value=taint, expected_type=type_hints["taint"])
            check_type(argname="argument utility_network_access", value=utility_network_access, expected_type=type_hints["utility_network_access"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster": cluster,
            "name": name,
            "node_count": node_count,
            "plan": plan,
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
        if anti_affinity is not None:
            self._values["anti_affinity"] = anti_affinity
        if cloud_native_plan is not None:
            self._values["cloud_native_plan"] = cloud_native_plan
        if custom_plan is not None:
            self._values["custom_plan"] = custom_plan
        if gpu_plan is not None:
            self._values["gpu_plan"] = gpu_plan
        if kubelet_args is not None:
            self._values["kubelet_args"] = kubelet_args
        if labels is not None:
            self._values["labels"] = labels
        if ssh_keys is not None:
            self._values["ssh_keys"] = ssh_keys
        if storage_encryption is not None:
            self._values["storage_encryption"] = storage_encryption
        if taint is not None:
            self._values["taint"] = taint
        if utility_network_access is not None:
            self._values["utility_network_access"] = utility_network_access

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
    def cluster(self) -> builtins.str:
        '''UUID of the cluster.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#cluster KubernetesNodeGroup#cluster}
        '''
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the node group. Needs to be unique within a cluster.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#name KubernetesNodeGroup#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def node_count(self) -> jsii.Number:
        '''Amount of nodes to provision in the node group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#node_count KubernetesNodeGroup#node_count}
        '''
        result = self._values.get("node_count")
        assert result is not None, "Required property 'node_count' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def plan(self) -> builtins.str:
        '''The server plan used for the node group. You can list available plans with ``upctl server plans``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#plan KubernetesNodeGroup#plan}
        '''
        result = self._values.get("plan")
        assert result is not None, "Required property 'plan' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def anti_affinity(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set to true, nodes in this group will be placed on separate compute hosts.

        Please note that anti-affinity policy is considered 'best effort' and enabling it does not fully guarantee that the nodes will end up on different hardware.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#anti_affinity KubernetesNodeGroup#anti_affinity}
        '''
        result = self._values.get("anti_affinity")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def cloud_native_plan(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[KubernetesNodeGroupCloudNativePlan]]]:
        '''cloud_native_plan block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#cloud_native_plan KubernetesNodeGroup#cloud_native_plan}
        '''
        result = self._values.get("cloud_native_plan")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[KubernetesNodeGroupCloudNativePlan]]], result)

    @builtins.property
    def custom_plan(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["KubernetesNodeGroupCustomPlan"]]]:
        '''custom_plan block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#custom_plan KubernetesNodeGroup#custom_plan}
        '''
        result = self._values.get("custom_plan")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["KubernetesNodeGroupCustomPlan"]]], result)

    @builtins.property
    def gpu_plan(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["KubernetesNodeGroupGpuPlan"]]]:
        '''gpu_plan block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#gpu_plan KubernetesNodeGroup#gpu_plan}
        '''
        result = self._values.get("gpu_plan")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["KubernetesNodeGroupGpuPlan"]]], result)

    @builtins.property
    def kubelet_args(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["KubernetesNodeGroupKubeletArgs"]]]:
        '''kubelet_args block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#kubelet_args KubernetesNodeGroup#kubelet_args}
        '''
        result = self._values.get("kubelet_args")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["KubernetesNodeGroupKubeletArgs"]]], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''User defined key-value pairs to classify the node_group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#labels KubernetesNodeGroup#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def ssh_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''You can optionally select SSH keys to be added as authorized keys to the nodes in this node group.

        This allows you to connect to the nodes via SSH once they are running.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#ssh_keys KubernetesNodeGroup#ssh_keys}
        '''
        result = self._values.get("ssh_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def storage_encryption(self) -> typing.Optional[builtins.str]:
        '''The storage encryption strategy to use for the nodes in this group.

        If not set, the cluster's storage encryption strategy will be used, if applicable.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#storage_encryption KubernetesNodeGroup#storage_encryption}
        '''
        result = self._values.get("storage_encryption")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def taint(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["KubernetesNodeGroupTaint"]]]:
        '''taint block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#taint KubernetesNodeGroup#taint}
        '''
        result = self._values.get("taint")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["KubernetesNodeGroupTaint"]]], result)

    @builtins.property
    def utility_network_access(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set to false, nodes in this group will not have access to utility network.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#utility_network_access KubernetesNodeGroup#utility_network_access}
        '''
        result = self._values.get("utility_network_access")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KubernetesNodeGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.kubernetesNodeGroup.KubernetesNodeGroupCustomPlan",
    jsii_struct_bases=[],
    name_mapping={
        "cores": "cores",
        "memory": "memory",
        "storage_size": "storageSize",
        "storage_tier": "storageTier",
    },
)
class KubernetesNodeGroupCustomPlan:
    def __init__(
        self,
        *,
        cores: jsii.Number,
        memory: jsii.Number,
        storage_size: jsii.Number,
        storage_tier: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cores: The number of CPU cores dedicated to individual node group nodes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#cores KubernetesNodeGroup#cores}
        :param memory: The amount of memory in megabytes to assign to individual node group node. Value needs to be divisible by 1024. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#memory KubernetesNodeGroup#memory}
        :param storage_size: The size of the storage device in gigabytes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#storage_size KubernetesNodeGroup#storage_size}
        :param storage_tier: The storage tier to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#storage_tier KubernetesNodeGroup#storage_tier}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73a7225f6a5b39ce9f22f470a4b39f4020d9c2babc3a4001d90f5a255e45917c)
            check_type(argname="argument cores", value=cores, expected_type=type_hints["cores"])
            check_type(argname="argument memory", value=memory, expected_type=type_hints["memory"])
            check_type(argname="argument storage_size", value=storage_size, expected_type=type_hints["storage_size"])
            check_type(argname="argument storage_tier", value=storage_tier, expected_type=type_hints["storage_tier"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cores": cores,
            "memory": memory,
            "storage_size": storage_size,
        }
        if storage_tier is not None:
            self._values["storage_tier"] = storage_tier

    @builtins.property
    def cores(self) -> jsii.Number:
        '''The number of CPU cores dedicated to individual node group nodes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#cores KubernetesNodeGroup#cores}
        '''
        result = self._values.get("cores")
        assert result is not None, "Required property 'cores' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def memory(self) -> jsii.Number:
        '''The amount of memory in megabytes to assign to individual node group node.

        Value needs to be divisible by 1024.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#memory KubernetesNodeGroup#memory}
        '''
        result = self._values.get("memory")
        assert result is not None, "Required property 'memory' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def storage_size(self) -> jsii.Number:
        '''The size of the storage device in gigabytes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#storage_size KubernetesNodeGroup#storage_size}
        '''
        result = self._values.get("storage_size")
        assert result is not None, "Required property 'storage_size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def storage_tier(self) -> typing.Optional[builtins.str]:
        '''The storage tier to use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#storage_tier KubernetesNodeGroup#storage_tier}
        '''
        result = self._values.get("storage_tier")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KubernetesNodeGroupCustomPlan(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class KubernetesNodeGroupCustomPlanList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.kubernetesNodeGroup.KubernetesNodeGroupCustomPlanList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b550730c152cdd521877d4cd4a76b2d1f548d64a196dbde61f47c82b091e854a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "KubernetesNodeGroupCustomPlanOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad2db79018ca305418ade3285985b0c22792d72ade4279a8d56d4cc611707192)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("KubernetesNodeGroupCustomPlanOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__146491c26357a66d3726100bdae7a85cd1ce3f9d133170c7b888e4371863e15b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__981f0a78ff74ee055d79706678f7855b237a9c0e1fa4f77d6f528bc29b193924)
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
            type_hints = typing.get_type_hints(_typecheckingstub__de8e36f34a796164d1d848fa9ee03d21d32d20da9d69b2969c70bd64366fc15e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[KubernetesNodeGroupCustomPlan]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[KubernetesNodeGroupCustomPlan]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[KubernetesNodeGroupCustomPlan]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15bf7d5bcd50f8e0b7df457f502a8bb9362ca3bf6ab8c3190246a91e31ac4fb9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class KubernetesNodeGroupCustomPlanOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.kubernetesNodeGroup.KubernetesNodeGroupCustomPlanOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8d2b117bf11d56c5c2ad00b1177ef138495c9f14ccd650ff5fcac5bedc510e7f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetStorageTier")
    def reset_storage_tier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageTier", []))

    @builtins.property
    @jsii.member(jsii_name="coresInput")
    def cores_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "coresInput"))

    @builtins.property
    @jsii.member(jsii_name="memoryInput")
    def memory_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "memoryInput"))

    @builtins.property
    @jsii.member(jsii_name="storageSizeInput")
    def storage_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "storageSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="storageTierInput")
    def storage_tier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageTierInput"))

    @builtins.property
    @jsii.member(jsii_name="cores")
    def cores(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cores"))

    @cores.setter
    def cores(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15878cdb5de9a8700102ae207bdd26c19d28bebbb88e918a78101ee82831a764)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cores", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memory")
    def memory(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memory"))

    @memory.setter
    def memory(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c63d931f4ac068dc3819c8179015a8c83a41a8032a345678fcc3e6da49734aeb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memory", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storageSize")
    def storage_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "storageSize"))

    @storage_size.setter
    def storage_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5657fcbc706cb9657327d1390116d8b8349d44ebea2c09586646bfd32bee67b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storageTier")
    def storage_tier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageTier"))

    @storage_tier.setter
    def storage_tier(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b087d3351ca31ac1af59c32711d8f4d022346ac4bccf9ec972df910ff8c4e5a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageTier", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, KubernetesNodeGroupCustomPlan]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, KubernetesNodeGroupCustomPlan]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, KubernetesNodeGroupCustomPlan]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7a11f561e4b919a685206286a7eed09483e309fbeeea066dff67583e94f0c7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.kubernetesNodeGroup.KubernetesNodeGroupGpuPlan",
    jsii_struct_bases=[],
    name_mapping={"storage_size": "storageSize", "storage_tier": "storageTier"},
)
class KubernetesNodeGroupGpuPlan:
    def __init__(
        self,
        *,
        storage_size: typing.Optional[jsii.Number] = None,
        storage_tier: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param storage_size: The size of the storage device in gigabytes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#storage_size KubernetesNodeGroup#storage_size}
        :param storage_tier: The storage tier to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#storage_tier KubernetesNodeGroup#storage_tier}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fa7e5803de5175f0817ac85027aef2f8dcff8f820ba557a589bd58117442345)
            check_type(argname="argument storage_size", value=storage_size, expected_type=type_hints["storage_size"])
            check_type(argname="argument storage_tier", value=storage_tier, expected_type=type_hints["storage_tier"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if storage_size is not None:
            self._values["storage_size"] = storage_size
        if storage_tier is not None:
            self._values["storage_tier"] = storage_tier

    @builtins.property
    def storage_size(self) -> typing.Optional[jsii.Number]:
        '''The size of the storage device in gigabytes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#storage_size KubernetesNodeGroup#storage_size}
        '''
        result = self._values.get("storage_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def storage_tier(self) -> typing.Optional[builtins.str]:
        '''The storage tier to use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#storage_tier KubernetesNodeGroup#storage_tier}
        '''
        result = self._values.get("storage_tier")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KubernetesNodeGroupGpuPlan(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class KubernetesNodeGroupGpuPlanList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.kubernetesNodeGroup.KubernetesNodeGroupGpuPlanList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7b1116523b1a8f7cf2e4f21456b1e8c24a959cc22b4d33b2606bac63063972ed)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "KubernetesNodeGroupGpuPlanOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3bd2c3bdaf3a8a8a1c8bde2bae997a172480ee2fd03a9886261c781f02bd8511)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("KubernetesNodeGroupGpuPlanOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6d3362daab3ef72b55a53261618f6b4143936663c170097004850acc51fc7ba)
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
            type_hints = typing.get_type_hints(_typecheckingstub__96ed86b311e36730c9fc332c1931b6642d6014d1fb2b09cb9ca90a24a941f6d7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0c6b4a7ed698dfe86f81922561ac8dfd3e04fb00556732cbd2db190868c8f559)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[KubernetesNodeGroupGpuPlan]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[KubernetesNodeGroupGpuPlan]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[KubernetesNodeGroupGpuPlan]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56435d3f02cd0ef23c6f01ed04f7701d16a65a25ab90cce603c19e6145a084f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class KubernetesNodeGroupGpuPlanOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.kubernetesNodeGroup.KubernetesNodeGroupGpuPlanOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4f1b7b6a41a17a31b8f915354ea57f1454e9ab1791768481ef8af39e44c85950)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetStorageSize")
    def reset_storage_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageSize", []))

    @jsii.member(jsii_name="resetStorageTier")
    def reset_storage_tier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageTier", []))

    @builtins.property
    @jsii.member(jsii_name="storageSizeInput")
    def storage_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "storageSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="storageTierInput")
    def storage_tier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageTierInput"))

    @builtins.property
    @jsii.member(jsii_name="storageSize")
    def storage_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "storageSize"))

    @storage_size.setter
    def storage_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12bc49b7146309b28c7a7a7d7b2bb4d9dd5dd90208d75989bac24002fa035032)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storageTier")
    def storage_tier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageTier"))

    @storage_tier.setter
    def storage_tier(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31a5992622b650da62b9685feb2241ec0c685dd517de9ef9205aa8049a237604)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageTier", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, KubernetesNodeGroupGpuPlan]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, KubernetesNodeGroupGpuPlan]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, KubernetesNodeGroupGpuPlan]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1e103e18c79ba9829a5353d403edb5702433cfe99ad39fe8da3d311d8c22dd0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.kubernetesNodeGroup.KubernetesNodeGroupKubeletArgs",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class KubernetesNodeGroupKubeletArgs:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: Kubelet argument key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#key KubernetesNodeGroup#key}
        :param value: Kubelet argument value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#value KubernetesNodeGroup#value}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__842da686c29c5adfe37f8e21bb7186ee26ad8d4d70cd1e8579de468f13543803)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Kubelet argument key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#key KubernetesNodeGroup#key}
        '''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Kubelet argument value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#value KubernetesNodeGroup#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KubernetesNodeGroupKubeletArgs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class KubernetesNodeGroupKubeletArgsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.kubernetesNodeGroup.KubernetesNodeGroupKubeletArgsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e77d29d892ab28ae50ac4262b7332db2cbe370cd4ca1efaa114fcdec6f5c57c5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "KubernetesNodeGroupKubeletArgsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa6ca723d3e26a5237e5153600b91c17e1a3c31853e088a9dadfdb48d53f9a5a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("KubernetesNodeGroupKubeletArgsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d60a7931de3e6139c97132bbd4c81870d3180a358bed18644632ac607d888e3f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b5025cd233c716e72c1b250acb3ef1951eb10755b75d25b900bb1ea9665b5824)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1da00c07635920f592f81dd8a1b5edbf670c685a0f0da4b6eab167085109616b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[KubernetesNodeGroupKubeletArgs]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[KubernetesNodeGroupKubeletArgs]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[KubernetesNodeGroupKubeletArgs]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a532fbf34887c150c2e5b1c80c46135e3c5fc280956c03a0f00097f4441c53f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class KubernetesNodeGroupKubeletArgsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.kubernetesNodeGroup.KubernetesNodeGroupKubeletArgsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f2fb6ce4916be3e5e9096d3c5734710a960470e81aa83a263b22f51942b6c1f3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0ca93e23304fb9d3092b6e042d7017f88c72f85e9ad92d73052c5eea4030011)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__190c6fb08627f568dbff911b8ba8f0a445d8de7960b43dbcd5b8df5a922d2537)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, KubernetesNodeGroupKubeletArgs]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, KubernetesNodeGroupKubeletArgs]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, KubernetesNodeGroupKubeletArgs]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e8923d78289695708ec2e55a09b1595632c8cae49ff31863f2e4bbde79aac87)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.kubernetesNodeGroup.KubernetesNodeGroupTaint",
    jsii_struct_bases=[],
    name_mapping={"effect": "effect", "key": "key", "value": "value"},
)
class KubernetesNodeGroupTaint:
    def __init__(
        self,
        *,
        effect: builtins.str,
        key: builtins.str,
        value: builtins.str,
    ) -> None:
        '''
        :param effect: Taint effect. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#effect KubernetesNodeGroup#effect}
        :param key: Taint key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#key KubernetesNodeGroup#key}
        :param value: Taint value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#value KubernetesNodeGroup#value}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea59ebf2232eca6d3573e469ce94ebcc61818a93352ae4370837428874ad8b8e)
            check_type(argname="argument effect", value=effect, expected_type=type_hints["effect"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "effect": effect,
            "key": key,
            "value": value,
        }

    @builtins.property
    def effect(self) -> builtins.str:
        '''Taint effect.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#effect KubernetesNodeGroup#effect}
        '''
        result = self._values.get("effect")
        assert result is not None, "Required property 'effect' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key(self) -> builtins.str:
        '''Taint key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#key KubernetesNodeGroup#key}
        '''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Taint value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs/resources/kubernetes_node_group#value KubernetesNodeGroup#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KubernetesNodeGroupTaint(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class KubernetesNodeGroupTaintList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.kubernetesNodeGroup.KubernetesNodeGroupTaintList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ced2e8f57a270b9e3b65f3e6dce4744a50a37c2fd167cc05fa3cf3c196ad923b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "KubernetesNodeGroupTaintOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbf03c718d4d6a6f12757ac57ca746adc9fbe2fcd3eef0260defffcadcf2dcc5)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("KubernetesNodeGroupTaintOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a653dbd7825419038762384e3dd6c1d35788318e615eb2113999140ca65d66af)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b4ee5f41b3ba7599860324eea4d5d76c6689c846f4d728520696478cdf35c51c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a54ae18ac5c83380be8ee636436df8ec2171a507975c17e6b26b5fe263cf4680)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[KubernetesNodeGroupTaint]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[KubernetesNodeGroupTaint]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[KubernetesNodeGroupTaint]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2b3c89670f740885f361407f1e60afdaa764dae180511c09280eee471d90ae7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class KubernetesNodeGroupTaintOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.kubernetesNodeGroup.KubernetesNodeGroupTaintOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9dd4a8354b794acedc53d938312c383d959e5a57e7799bce1de1ea672134d368)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="effectInput")
    def effect_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "effectInput"))

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="effect")
    def effect(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "effect"))

    @effect.setter
    def effect(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aae6c80211b753dde976506b8fdaaaeb52317752c965fa8f71e691ab195c694a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "effect", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55a026e007716eba12ee4e36307b091738d1cfd97602f2c5522ad02b04e0f132)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60c2f44434e8c966994b706bcde3d60ee6d488bc1150d9deb3e9a555a19dee0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, KubernetesNodeGroupTaint]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, KubernetesNodeGroupTaint]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, KubernetesNodeGroupTaint]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a11735bbf7d5e4dd383fb927e6bf80821b4d25f117c173b310cfc837a25c7f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "KubernetesNodeGroup",
    "KubernetesNodeGroupCloudNativePlan",
    "KubernetesNodeGroupCloudNativePlanList",
    "KubernetesNodeGroupCloudNativePlanOutputReference",
    "KubernetesNodeGroupConfig",
    "KubernetesNodeGroupCustomPlan",
    "KubernetesNodeGroupCustomPlanList",
    "KubernetesNodeGroupCustomPlanOutputReference",
    "KubernetesNodeGroupGpuPlan",
    "KubernetesNodeGroupGpuPlanList",
    "KubernetesNodeGroupGpuPlanOutputReference",
    "KubernetesNodeGroupKubeletArgs",
    "KubernetesNodeGroupKubeletArgsList",
    "KubernetesNodeGroupKubeletArgsOutputReference",
    "KubernetesNodeGroupTaint",
    "KubernetesNodeGroupTaintList",
    "KubernetesNodeGroupTaintOutputReference",
]

publication.publish()

def _typecheckingstub__8bbcd241d9ab4cfd557f0a030c928c51f93c7d6d9f343e0bcdbdda3cbc8065e3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cluster: builtins.str,
    name: builtins.str,
    node_count: jsii.Number,
    plan: builtins.str,
    anti_affinity: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cloud_native_plan: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[KubernetesNodeGroupCloudNativePlan, typing.Dict[builtins.str, typing.Any]]]]] = None,
    custom_plan: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[KubernetesNodeGroupCustomPlan, typing.Dict[builtins.str, typing.Any]]]]] = None,
    gpu_plan: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[KubernetesNodeGroupGpuPlan, typing.Dict[builtins.str, typing.Any]]]]] = None,
    kubelet_args: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[KubernetesNodeGroupKubeletArgs, typing.Dict[builtins.str, typing.Any]]]]] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ssh_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    storage_encryption: typing.Optional[builtins.str] = None,
    taint: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[KubernetesNodeGroupTaint, typing.Dict[builtins.str, typing.Any]]]]] = None,
    utility_network_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__8e4418f3bc7d50550f1d889edee827b87fd9884602972643c6b82f110049ba71(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac2f10d642c0079d30e463561c2878e59777f101807a48a08ccb9a8933285e30(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[KubernetesNodeGroupCloudNativePlan, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__710eeb24e681bc1abd473c02c09c72cd25116f5c53784cd07b46e161d215c56f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[KubernetesNodeGroupCustomPlan, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c17e1903eed937df8e22fb46de08949295493fcc3197086a410959cf85bd4e98(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[KubernetesNodeGroupGpuPlan, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32e3828076130e1cbd29ccb900f4d6ed322c27ffe5fa92f4dab04d41c7227a1f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[KubernetesNodeGroupKubeletArgs, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__374acc0d3de361c5076be47a8876b2f5870798afcd9887148234d9685257a419(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[KubernetesNodeGroupTaint, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e621946f83e58f50c483b681d6a00e44ec81d2dccf1a4f8dafde9e0fb59d55b4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__251ecefce0fab4086841f5905fdd68a5182667a221b0cf9910dbc14eee214671(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fccb7b922d5d84e539f4c8817753636ee4b2f0dec095ea9ff13030c9d7a17d58(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02535264f80e698e5cf251336456b8c83e944521501b454ed690a5d74067c620(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8670cbb382adf592bc5d0f3e42c4e96d4326983d0e4fe93743648b2ff3d09e74(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd9b94a7a760e7688eaafae17051a6d3f96c6ab95a43f2ccc57fa9c2e964189b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3caf64b524bd36e4019e89ade967c6b4e62d55fddf7a8f9e9ed8118d38383759(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4b669e48a3836306fe80e34225d241ad384a8351e76d8d7b17ffdd8544edf45(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c2a3afca29e180734047644aa682bae1b7fbd5aacc3d234ed7616ba415f5fb6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5438388f4032834938f080084c7ae0430cf33858715d18b4e84c3c8b7d99c583(
    *,
    storage_size: typing.Optional[jsii.Number] = None,
    storage_tier: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a5a3a16968d45ac84e9b283e63c8c906bd70e1a328640d5e7126d46a1c1fdd1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fe0c17e964827460fc66444ceb9d46776f4128115267f70dfc0ed4bfcb85920(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d97187bd0b82a71876e431a81398d9cc1dc821d2610692158cc56a31a863789(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae893d1d0df821f4f21d426fa80e3eb1d46fa1bbbc724b73e68a3bde2309032c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__beb64ca1f717b4814637a6a29fa9ec5a455b360ac7185bac86f30c38c43272e8(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d82a371178e1731f4d1566a0c16e13ea3970cdd9188d838221dcd62f32757793(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[KubernetesNodeGroupCloudNativePlan]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5aaf5281cf9fc6a97d4533c0769d0346349b54e0f7716d35e13101df78d13b1d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27f7ff508be8287499998f03c15d925e630d2e4e2a70ed3d542615d30fa9bf2d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38df547be63e43097329d5785a3b9c86f9f334cd3b597e3faffc1473e6c3087c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb41ddc5a5a4d49616d4a8b63583841ac403b22e7f09d2806b25388722eb66a5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, KubernetesNodeGroupCloudNativePlan]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2489ae5bd3c17ee9de104387734150d3686d0bce3df0c0db5244751c51da43c4(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cluster: builtins.str,
    name: builtins.str,
    node_count: jsii.Number,
    plan: builtins.str,
    anti_affinity: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cloud_native_plan: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[KubernetesNodeGroupCloudNativePlan, typing.Dict[builtins.str, typing.Any]]]]] = None,
    custom_plan: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[KubernetesNodeGroupCustomPlan, typing.Dict[builtins.str, typing.Any]]]]] = None,
    gpu_plan: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[KubernetesNodeGroupGpuPlan, typing.Dict[builtins.str, typing.Any]]]]] = None,
    kubelet_args: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[KubernetesNodeGroupKubeletArgs, typing.Dict[builtins.str, typing.Any]]]]] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ssh_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    storage_encryption: typing.Optional[builtins.str] = None,
    taint: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[KubernetesNodeGroupTaint, typing.Dict[builtins.str, typing.Any]]]]] = None,
    utility_network_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73a7225f6a5b39ce9f22f470a4b39f4020d9c2babc3a4001d90f5a255e45917c(
    *,
    cores: jsii.Number,
    memory: jsii.Number,
    storage_size: jsii.Number,
    storage_tier: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b550730c152cdd521877d4cd4a76b2d1f548d64a196dbde61f47c82b091e854a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad2db79018ca305418ade3285985b0c22792d72ade4279a8d56d4cc611707192(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__146491c26357a66d3726100bdae7a85cd1ce3f9d133170c7b888e4371863e15b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__981f0a78ff74ee055d79706678f7855b237a9c0e1fa4f77d6f528bc29b193924(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de8e36f34a796164d1d848fa9ee03d21d32d20da9d69b2969c70bd64366fc15e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15bf7d5bcd50f8e0b7df457f502a8bb9362ca3bf6ab8c3190246a91e31ac4fb9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[KubernetesNodeGroupCustomPlan]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d2b117bf11d56c5c2ad00b1177ef138495c9f14ccd650ff5fcac5bedc510e7f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15878cdb5de9a8700102ae207bdd26c19d28bebbb88e918a78101ee82831a764(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c63d931f4ac068dc3819c8179015a8c83a41a8032a345678fcc3e6da49734aeb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5657fcbc706cb9657327d1390116d8b8349d44ebea2c09586646bfd32bee67b2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b087d3351ca31ac1af59c32711d8f4d022346ac4bccf9ec972df910ff8c4e5a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7a11f561e4b919a685206286a7eed09483e309fbeeea066dff67583e94f0c7a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, KubernetesNodeGroupCustomPlan]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fa7e5803de5175f0817ac85027aef2f8dcff8f820ba557a589bd58117442345(
    *,
    storage_size: typing.Optional[jsii.Number] = None,
    storage_tier: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b1116523b1a8f7cf2e4f21456b1e8c24a959cc22b4d33b2606bac63063972ed(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bd2c3bdaf3a8a8a1c8bde2bae997a172480ee2fd03a9886261c781f02bd8511(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6d3362daab3ef72b55a53261618f6b4143936663c170097004850acc51fc7ba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96ed86b311e36730c9fc332c1931b6642d6014d1fb2b09cb9ca90a24a941f6d7(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c6b4a7ed698dfe86f81922561ac8dfd3e04fb00556732cbd2db190868c8f559(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56435d3f02cd0ef23c6f01ed04f7701d16a65a25ab90cce603c19e6145a084f6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[KubernetesNodeGroupGpuPlan]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f1b7b6a41a17a31b8f915354ea57f1454e9ab1791768481ef8af39e44c85950(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12bc49b7146309b28c7a7a7d7b2bb4d9dd5dd90208d75989bac24002fa035032(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31a5992622b650da62b9685feb2241ec0c685dd517de9ef9205aa8049a237604(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1e103e18c79ba9829a5353d403edb5702433cfe99ad39fe8da3d311d8c22dd0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, KubernetesNodeGroupGpuPlan]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__842da686c29c5adfe37f8e21bb7186ee26ad8d4d70cd1e8579de468f13543803(
    *,
    key: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e77d29d892ab28ae50ac4262b7332db2cbe370cd4ca1efaa114fcdec6f5c57c5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa6ca723d3e26a5237e5153600b91c17e1a3c31853e088a9dadfdb48d53f9a5a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d60a7931de3e6139c97132bbd4c81870d3180a358bed18644632ac607d888e3f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5025cd233c716e72c1b250acb3ef1951eb10755b75d25b900bb1ea9665b5824(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1da00c07635920f592f81dd8a1b5edbf670c685a0f0da4b6eab167085109616b(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a532fbf34887c150c2e5b1c80c46135e3c5fc280956c03a0f00097f4441c53f7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[KubernetesNodeGroupKubeletArgs]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2fb6ce4916be3e5e9096d3c5734710a960470e81aa83a263b22f51942b6c1f3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0ca93e23304fb9d3092b6e042d7017f88c72f85e9ad92d73052c5eea4030011(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__190c6fb08627f568dbff911b8ba8f0a445d8de7960b43dbcd5b8df5a922d2537(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e8923d78289695708ec2e55a09b1595632c8cae49ff31863f2e4bbde79aac87(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, KubernetesNodeGroupKubeletArgs]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea59ebf2232eca6d3573e469ce94ebcc61818a93352ae4370837428874ad8b8e(
    *,
    effect: builtins.str,
    key: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ced2e8f57a270b9e3b65f3e6dce4744a50a37c2fd167cc05fa3cf3c196ad923b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbf03c718d4d6a6f12757ac57ca746adc9fbe2fcd3eef0260defffcadcf2dcc5(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a653dbd7825419038762384e3dd6c1d35788318e615eb2113999140ca65d66af(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4ee5f41b3ba7599860324eea4d5d76c6689c846f4d728520696478cdf35c51c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a54ae18ac5c83380be8ee636436df8ec2171a507975c17e6b26b5fe263cf4680(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2b3c89670f740885f361407f1e60afdaa764dae180511c09280eee471d90ae7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[KubernetesNodeGroupTaint]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9dd4a8354b794acedc53d938312c383d959e5a57e7799bce1de1ea672134d368(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aae6c80211b753dde976506b8fdaaaeb52317752c965fa8f71e691ab195c694a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55a026e007716eba12ee4e36307b091738d1cfd97602f2c5522ad02b04e0f132(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60c2f44434e8c966994b706bcde3d60ee6d488bc1150d9deb3e9a555a19dee0b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a11735bbf7d5e4dd383fb927e6bf80821b4d25f117c173b310cfc837a25c7f4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, KubernetesNodeGroupTaint]],
) -> None:
    """Type checking stubs"""
    pass
