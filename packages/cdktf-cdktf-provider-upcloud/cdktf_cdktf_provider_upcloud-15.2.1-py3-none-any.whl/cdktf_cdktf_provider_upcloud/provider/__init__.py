r'''
# `provider`

Refer to the Terraform Registry for docs: [`upcloud`](https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs).
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


class UpcloudProvider(
    _cdktf_9a9027ec.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.provider.UpcloudProvider",
):
    '''Represents a {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs upcloud}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        alias: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        request_timeout_sec: typing.Optional[jsii.Number] = None,
        retry_max: typing.Optional[jsii.Number] = None,
        retry_wait_max_sec: typing.Optional[jsii.Number] = None,
        retry_wait_min_sec: typing.Optional[jsii.Number] = None,
        token: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs upcloud} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param alias: Alias name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs#alias UpcloudProvider#alias}
        :param password: Password for UpCloud API user. Can also be configured using the ``UPCLOUD_PASSWORD`` environment variable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs#password UpcloudProvider#password}
        :param request_timeout_sec: The duration (in seconds) that the provider waits for an HTTP request towards UpCloud API to complete. Defaults to 120 seconds Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs#request_timeout_sec UpcloudProvider#request_timeout_sec}
        :param retry_max: Maximum number of retries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs#retry_max UpcloudProvider#retry_max}
        :param retry_wait_max_sec: Maximum time to wait between retries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs#retry_wait_max_sec UpcloudProvider#retry_wait_max_sec}
        :param retry_wait_min_sec: Minimum time to wait between retries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs#retry_wait_min_sec UpcloudProvider#retry_wait_min_sec}
        :param token: Token for authenticating to UpCloud API. Can also be configured using the ``UPCLOUD_TOKEN`` environment variable or using the system keyring. Use ``upctl account login`` command to save a token to the system keyring. (EXPERIMENTAL) Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs#token UpcloudProvider#token}
        :param username: UpCloud username with API access. Can also be configured using the ``UPCLOUD_USERNAME`` environment variable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs#username UpcloudProvider#username}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__786d7492fb6ccdc4fc75b22452f182f0009c6f7041f055f198f8ab4750003c16)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = UpcloudProviderConfig(
            alias=alias,
            password=password,
            request_timeout_sec=request_timeout_sec,
            retry_max=retry_max,
            retry_wait_max_sec=retry_wait_max_sec,
            retry_wait_min_sec=retry_wait_min_sec,
            token=token,
            username=username,
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
        '''Generates CDKTF code for importing a UpcloudProvider resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the UpcloudProvider to import.
        :param import_from_id: The id of the existing UpcloudProvider that should be imported. Refer to the {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the UpcloudProvider to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1628005c128e139344030e5187700e17d5703e65a1ed60eb45ad4f09bac925d5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetRequestTimeoutSec")
    def reset_request_timeout_sec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequestTimeoutSec", []))

    @jsii.member(jsii_name="resetRetryMax")
    def reset_retry_max(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetryMax", []))

    @jsii.member(jsii_name="resetRetryWaitMaxSec")
    def reset_retry_wait_max_sec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetryWaitMaxSec", []))

    @jsii.member(jsii_name="resetRetryWaitMinSec")
    def reset_retry_wait_min_sec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetryWaitMinSec", []))

    @jsii.member(jsii_name="resetToken")
    def reset_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetToken", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

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
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="requestTimeoutSecInput")
    def request_timeout_sec_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "requestTimeoutSecInput"))

    @builtins.property
    @jsii.member(jsii_name="retryMaxInput")
    def retry_max_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retryMaxInput"))

    @builtins.property
    @jsii.member(jsii_name="retryWaitMaxSecInput")
    def retry_wait_max_sec_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retryWaitMaxSecInput"))

    @builtins.property
    @jsii.member(jsii_name="retryWaitMinSecInput")
    def retry_wait_min_sec_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retryWaitMinSecInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenInput")
    def token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="alias")
    def alias(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e945ae0cadd024f4b089068aefbe16b016f51e1f64cc6f1e8850982caaae4a34)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "password"))

    @password.setter
    def password(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7468e4559193a961ddd25362db32f9c861bcc46838550615e263ebc1a73453cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requestTimeoutSec")
    def request_timeout_sec(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "requestTimeoutSec"))

    @request_timeout_sec.setter
    def request_timeout_sec(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__287057d3016cfed3607f43e0805d362c5d2f2ee791a47dbdd378f3bbe989604b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requestTimeoutSec", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retryMax")
    def retry_max(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retryMax"))

    @retry_max.setter
    def retry_max(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e4a81c76bc2199b17a918d1471a4c63e1c00ecb3f395413787eba9b56b6498b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retryMax", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retryWaitMaxSec")
    def retry_wait_max_sec(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retryWaitMaxSec"))

    @retry_wait_max_sec.setter
    def retry_wait_max_sec(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b81aaca05e740634c669da4f51e9846126f057b96daa7a573168193975e920ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retryWaitMaxSec", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retryWaitMinSec")
    def retry_wait_min_sec(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retryWaitMinSec"))

    @retry_wait_min_sec.setter
    def retry_wait_min_sec(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49c748eec266d9d5bc8e7a25a10e42de6548f3fcf8b2fadc433e055280bc7303)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retryWaitMinSec", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="token")
    def token(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "token"))

    @token.setter
    def token(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d29a5224d1a254258edc7ad8071e53f50ce334f5e5f9c3f72c0124ec933a3924)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "token", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "username"))

    @username.setter
    def username(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73bdbfe36f31accc3b6a6dcba3205f0ac50aaaa3f363bff894bdc84e137fc234)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.provider.UpcloudProviderConfig",
    jsii_struct_bases=[],
    name_mapping={
        "alias": "alias",
        "password": "password",
        "request_timeout_sec": "requestTimeoutSec",
        "retry_max": "retryMax",
        "retry_wait_max_sec": "retryWaitMaxSec",
        "retry_wait_min_sec": "retryWaitMinSec",
        "token": "token",
        "username": "username",
    },
)
class UpcloudProviderConfig:
    def __init__(
        self,
        *,
        alias: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        request_timeout_sec: typing.Optional[jsii.Number] = None,
        retry_max: typing.Optional[jsii.Number] = None,
        retry_wait_max_sec: typing.Optional[jsii.Number] = None,
        retry_wait_min_sec: typing.Optional[jsii.Number] = None,
        token: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param alias: Alias name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs#alias UpcloudProvider#alias}
        :param password: Password for UpCloud API user. Can also be configured using the ``UPCLOUD_PASSWORD`` environment variable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs#password UpcloudProvider#password}
        :param request_timeout_sec: The duration (in seconds) that the provider waits for an HTTP request towards UpCloud API to complete. Defaults to 120 seconds Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs#request_timeout_sec UpcloudProvider#request_timeout_sec}
        :param retry_max: Maximum number of retries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs#retry_max UpcloudProvider#retry_max}
        :param retry_wait_max_sec: Maximum time to wait between retries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs#retry_wait_max_sec UpcloudProvider#retry_wait_max_sec}
        :param retry_wait_min_sec: Minimum time to wait between retries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs#retry_wait_min_sec UpcloudProvider#retry_wait_min_sec}
        :param token: Token for authenticating to UpCloud API. Can also be configured using the ``UPCLOUD_TOKEN`` environment variable or using the system keyring. Use ``upctl account login`` command to save a token to the system keyring. (EXPERIMENTAL) Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs#token UpcloudProvider#token}
        :param username: UpCloud username with API access. Can also be configured using the ``UPCLOUD_USERNAME`` environment variable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs#username UpcloudProvider#username}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e59a8dbe0e889be0d58fa19f6443e5c6def71ffe937d944a0b10dbe3c74b4005)
            check_type(argname="argument alias", value=alias, expected_type=type_hints["alias"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument request_timeout_sec", value=request_timeout_sec, expected_type=type_hints["request_timeout_sec"])
            check_type(argname="argument retry_max", value=retry_max, expected_type=type_hints["retry_max"])
            check_type(argname="argument retry_wait_max_sec", value=retry_wait_max_sec, expected_type=type_hints["retry_wait_max_sec"])
            check_type(argname="argument retry_wait_min_sec", value=retry_wait_min_sec, expected_type=type_hints["retry_wait_min_sec"])
            check_type(argname="argument token", value=token, expected_type=type_hints["token"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if alias is not None:
            self._values["alias"] = alias
        if password is not None:
            self._values["password"] = password
        if request_timeout_sec is not None:
            self._values["request_timeout_sec"] = request_timeout_sec
        if retry_max is not None:
            self._values["retry_max"] = retry_max
        if retry_wait_max_sec is not None:
            self._values["retry_wait_max_sec"] = retry_wait_max_sec
        if retry_wait_min_sec is not None:
            self._values["retry_wait_min_sec"] = retry_wait_min_sec
        if token is not None:
            self._values["token"] = token
        if username is not None:
            self._values["username"] = username

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs#alias UpcloudProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''Password for UpCloud API user. Can also be configured using the ``UPCLOUD_PASSWORD`` environment variable.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs#password UpcloudProvider#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def request_timeout_sec(self) -> typing.Optional[jsii.Number]:
        '''The duration (in seconds) that the provider waits for an HTTP request towards UpCloud API to complete.

        Defaults to 120 seconds

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs#request_timeout_sec UpcloudProvider#request_timeout_sec}
        '''
        result = self._values.get("request_timeout_sec")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def retry_max(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of retries.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs#retry_max UpcloudProvider#retry_max}
        '''
        result = self._values.get("retry_max")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def retry_wait_max_sec(self) -> typing.Optional[jsii.Number]:
        '''Maximum time to wait between retries.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs#retry_wait_max_sec UpcloudProvider#retry_wait_max_sec}
        '''
        result = self._values.get("retry_wait_max_sec")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def retry_wait_min_sec(self) -> typing.Optional[jsii.Number]:
        '''Minimum time to wait between retries.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs#retry_wait_min_sec UpcloudProvider#retry_wait_min_sec}
        '''
        result = self._values.get("retry_wait_min_sec")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token(self) -> typing.Optional[builtins.str]:
        '''Token for authenticating to UpCloud API.

        Can also be configured using the ``UPCLOUD_TOKEN`` environment variable or using the system keyring. Use ``upctl account login`` command to save a token to the system keyring. (EXPERIMENTAL)

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs#token UpcloudProvider#token}
        '''
        result = self._values.get("token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''UpCloud username with API access. Can also be configured using the ``UPCLOUD_USERNAME`` environment variable.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/upcloudltd/upcloud/5.24.1/docs#username UpcloudProvider#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UpcloudProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "UpcloudProvider",
    "UpcloudProviderConfig",
]

publication.publish()

def _typecheckingstub__786d7492fb6ccdc4fc75b22452f182f0009c6f7041f055f198f8ab4750003c16(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    alias: typing.Optional[builtins.str] = None,
    password: typing.Optional[builtins.str] = None,
    request_timeout_sec: typing.Optional[jsii.Number] = None,
    retry_max: typing.Optional[jsii.Number] = None,
    retry_wait_max_sec: typing.Optional[jsii.Number] = None,
    retry_wait_min_sec: typing.Optional[jsii.Number] = None,
    token: typing.Optional[builtins.str] = None,
    username: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1628005c128e139344030e5187700e17d5703e65a1ed60eb45ad4f09bac925d5(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e945ae0cadd024f4b089068aefbe16b016f51e1f64cc6f1e8850982caaae4a34(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7468e4559193a961ddd25362db32f9c861bcc46838550615e263ebc1a73453cc(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__287057d3016cfed3607f43e0805d362c5d2f2ee791a47dbdd378f3bbe989604b(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e4a81c76bc2199b17a918d1471a4c63e1c00ecb3f395413787eba9b56b6498b(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b81aaca05e740634c669da4f51e9846126f057b96daa7a573168193975e920ed(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49c748eec266d9d5bc8e7a25a10e42de6548f3fcf8b2fadc433e055280bc7303(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d29a5224d1a254258edc7ad8071e53f50ce334f5e5f9c3f72c0124ec933a3924(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73bdbfe36f31accc3b6a6dcba3205f0ac50aaaa3f363bff894bdc84e137fc234(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e59a8dbe0e889be0d58fa19f6443e5c6def71ffe937d944a0b10dbe3c74b4005(
    *,
    alias: typing.Optional[builtins.str] = None,
    password: typing.Optional[builtins.str] = None,
    request_timeout_sec: typing.Optional[jsii.Number] = None,
    retry_max: typing.Optional[jsii.Number] = None,
    retry_wait_max_sec: typing.Optional[jsii.Number] = None,
    retry_wait_min_sec: typing.Optional[jsii.Number] = None,
    token: typing.Optional[builtins.str] = None,
    username: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
