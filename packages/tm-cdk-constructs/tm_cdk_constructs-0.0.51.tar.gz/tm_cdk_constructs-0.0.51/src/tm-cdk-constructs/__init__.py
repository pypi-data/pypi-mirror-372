r'''
# CDK construct lib

Welcome to Toumoro's AWS Service Wrapper CDK Construct Library! This library is designed to make it easy and efficient to deploy and manage AWS services within your CDK projects. Whether you're provisioning infrastructure for a simple web application or orchestrating a complex cloud-native architecture, this library aims to streamline your development process by providing high-level constructs for common AWS services.

## Features

* Simplified Service Provisioning: Easily create and configure AWS services using intuitive CDK constructs.
* Best Practices Built-In: Leverage pre-configured settings and defaults based on AWS best practices to ensure reliable and secure deployments.
* Modular and Extensible: Compose your infrastructure using modular constructs, allowing for flexibility and reusability across projects.

# Contributing to CDK Construct Toumoro

[Contributing](CONTRIBUTING.md)

# Examples

[Examples](examples/README.md)

# Documentation API

[API](API.md)

# Developpement Guide

[AWS CDK Design Guidelines](https://github.com/aws/aws-cdk/blob/main/docs/DESIGN_GUIDELINES.md)

## Naming Conventions

1. *Prefixes*:

   * *Cfn* for CloudFormation resources.
   * *Fn* for constructs generating CloudFormation functions.
   * *As* for abstract classes.
   * *I* for interfaces.
   * *Vpc* for constructs related to Virtual Private Cloud.
   * *Lambda* for constructs related to AWS Lambda.
   * Example: CfnStack, FnSub, Aspects, IVpc, VpcNetwork, LambdaFunction.
2. *Construct Names*:

   * Use descriptive names that reflect the purpose of the construct.
   * CamelCase for multi-word names.
   * Avoid abbreviations unless they are widely understood.
   * Example: VpcBasic, RdsAuroraMysqlServerLess.
3. *Property Names*:

   * Follow AWS resource naming conventions where applicable.
   * Use camelCase for property names.
   * Use clear and concise names that reflect the purpose of the property.
   * Example: bucketName, vpcId, functionName.
4. *Method Names*:

   * Use verbs or verb phrases to describe actions performed by methods.
   * Use camelCase.
   * Example: addBucketPolicy, createVpc, invokeLambda.
5. *Interface Names*:

   * Interfaces begging uppercase I are reserverd to AWS CDK library.
   * Start with an prefix TmI
   * Use clear and descriptive names.
   * Example: TmIInstance, TmISecurityGroup, TmIVpc.
6. *Module Names*:

   * Use lowercase with hyphens for separating words.
   * Be descriptive but concise.
   * Follow a hierarchy if necessary, e.g., aws-cdk.aws_s3 for S3-related constructs.
   * Example: aws-cdk.aws_s3, aws-cdk.aws_ec2, aws-cdk.aws_lambda.
7. *Variable Names*:

   * Use descriptive names.
   * CamelCase for multi-word names.
   * Keep variable names concise but meaningful.
   * Example: instanceCount, subnetIds, roleArn.
8. *Enum and Constant Names*:

   * Use uppercase for constants.
   * CamelCase for multi-word names.
   * Be descriptive about the purpose of the constant or enum.
   * Example: MAX_RETRIES, HTTP_STATUS_CODES, VPC_CONFIG.
9. *File Names*:

   * Use lowercase with hyphens for separating words.
   * Reflect the content of the file.
   * Include version numbers if necessary.
   * Example: s3-bucket-stack.ts, vpc-network.ts, lambda-function.ts.
10. *Documentation Comments*:

    * Use JSDoc or similar conventions to provide clear documentation for each construct, method, property, etc.
    * Ensure that the documentation is up-to-date and accurately reflects the purpose and usage of the code.
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

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_certificatemanager as _aws_cdk_aws_certificatemanager_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_ecs as _aws_cdk_aws_ecs_ceddda9d
import aws_cdk.aws_ecs_patterns as _aws_cdk_aws_ecs_patterns_ceddda9d
import aws_cdk.aws_elasticache as _aws_cdk_aws_elasticache_ceddda9d
import aws_cdk.aws_elasticloadbalancingv2 as _aws_cdk_aws_elasticloadbalancingv2_ceddda9d
import aws_cdk.aws_events as _aws_cdk_aws_events_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_rds as _aws_cdk_aws_rds_ceddda9d
import aws_cdk.aws_route53 as _aws_cdk_aws_route53_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.pipelines as _aws_cdk_pipelines_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.interface(jsii_type="tm-cdk-constructs.IAnsiblePlaybookEc2Props")
class IAnsiblePlaybookEc2Props(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="gitHubBranch")
    def git_hub_branch(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @git_hub_branch.setter
    def git_hub_branch(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="gitHubOwner")
    def git_hub_owner(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @git_hub_owner.setter
    def git_hub_owner(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="gitHubPath")
    def git_hub_path(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @git_hub_path.setter
    def git_hub_path(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="gitHubRepository")
    def git_hub_repository(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @git_hub_repository.setter
    def git_hub_repository(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="gitHubTokenSsmSecure")
    def git_hub_token_ssm_secure(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @git_hub_token_ssm_secure.setter
    def git_hub_token_ssm_secure(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="playbookFile")
    def playbook_file(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @playbook_file.setter
    def playbook_file(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="tagTargetKey")
    def tag_target_key(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @tag_target_key.setter
    def tag_target_key(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="tagTargetValue")
    def tag_target_value(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @tag_target_value.setter
    def tag_target_value(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IAnsiblePlaybookEc2PropsProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "tm-cdk-constructs.IAnsiblePlaybookEc2Props"

    @builtins.property
    @jsii.member(jsii_name="gitHubBranch")
    def git_hub_branch(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gitHubBranch"))

    @git_hub_branch.setter
    def git_hub_branch(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1a903c19542e4352765dcd8d7b1f56a6384d1d87f7e0f467d8dabb1cc6d22ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gitHubBranch", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gitHubOwner")
    def git_hub_owner(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gitHubOwner"))

    @git_hub_owner.setter
    def git_hub_owner(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83e58a3cc4f1663dc2f2d963060c4f836501ed3bd692e67dd798d40affc6f4b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gitHubOwner", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gitHubPath")
    def git_hub_path(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gitHubPath"))

    @git_hub_path.setter
    def git_hub_path(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f71e6a9866bd308daaa460b4d0746c78d83208367163e1d12e0fc74564f7a85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gitHubPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gitHubRepository")
    def git_hub_repository(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gitHubRepository"))

    @git_hub_repository.setter
    def git_hub_repository(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36649a5ca8045fe85e6c1359daaf2a451d8d26653d94430bc7585f772be0c23e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gitHubRepository", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gitHubTokenSsmSecure")
    def git_hub_token_ssm_secure(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gitHubTokenSsmSecure"))

    @git_hub_token_ssm_secure.setter
    def git_hub_token_ssm_secure(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__683916488da7e0e69f1c09c3ad97064949559068c07bab11ded3e343a5865b6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gitHubTokenSsmSecure", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="playbookFile")
    def playbook_file(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "playbookFile"))

    @playbook_file.setter
    def playbook_file(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b059d160412d3c557f5d6a2fe32da0d0d3c08585954048fddd1fd2a9a573e001)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "playbookFile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tagTargetKey")
    def tag_target_key(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tagTargetKey"))

    @tag_target_key.setter
    def tag_target_key(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f63059b634ff1179395c346fc3b3a79affcbf4362e001e1aa88a9c5f2aab4f44)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagTargetKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tagTargetValue")
    def tag_target_value(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tagTargetValue"))

    @tag_target_value.setter
    def tag_target_value(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__060fbc8c38b993593f46abadd9e52ce939a4915e541206d0a2ab546b1c7198d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagTargetValue", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAnsiblePlaybookEc2Props).__jsii_proxy_class__ = lambda : _IAnsiblePlaybookEc2PropsProxy


@jsii.interface(jsii_type="tm-cdk-constructs.IIEcsDeploymentHookProps")
class IIEcsDeploymentHookProps(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="command")
    def command(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @command.setter
    def command(self, value: typing.List[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="containerName")
    def container_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @container_name.setter
    def container_name(self, value: builtins.str) -> None:
        ...


class _IIEcsDeploymentHookPropsProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "tm-cdk-constructs.IIEcsDeploymentHookProps"

    @builtins.property
    @jsii.member(jsii_name="command")
    def command(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "command"))

    @command.setter
    def command(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ead78d7548ad9ea41e83897677e686c66cd9123caf1358155a1d718a05415036)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "command", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="containerName")
    def container_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "containerName"))

    @container_name.setter
    def container_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__715c932dfcfddfe301fa304b45c0127f1c51f06c2a5266f69307c1100b71aa68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "containerName", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IIEcsDeploymentHookProps).__jsii_proxy_class__ = lambda : _IIEcsDeploymentHookPropsProxy


@jsii.interface(jsii_type="tm-cdk-constructs.IIefsVolumes")
class IIefsVolumes(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @name.setter
    def name(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @path.setter
    def path(self, value: builtins.str) -> None:
        ...


class _IIefsVolumesProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "tm-cdk-constructs.IIefsVolumes"

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fe18738b936c980e7bedaeb70d95f218e08417b1ba172150eabc40179c8ce0f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__119ccde770251ce59b3a03156371764d318f9589399c47e463f7676a53020a76)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IIefsVolumes).__jsii_proxy_class__ = lambda : _IIefsVolumesProxy


@jsii.interface(jsii_type="tm-cdk-constructs.IPatchManagerProps")
class IPatchManagerProps(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="commandUpdate")
    def command_update(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @command_update.setter
    def command_update(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="cronScheduleFullUpdates")
    def cron_schedule_full_updates(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @cron_schedule_full_updates.setter
    def cron_schedule_full_updates(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="cronScheduleUpdates")
    def cron_schedule_updates(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @cron_schedule_updates.setter
    def cron_schedule_updates(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="operatingSystem")
    def operating_system(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @operating_system.setter
    def operating_system(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="tagPatchGroup")
    def tag_patch_group(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @tag_patch_group.setter
    def tag_patch_group(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IPatchManagerPropsProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "tm-cdk-constructs.IPatchManagerProps"

    @builtins.property
    @jsii.member(jsii_name="commandUpdate")
    def command_update(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commandUpdate"))

    @command_update.setter
    def command_update(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81a01a570b69a60eee6f3e69e8cbcd87347e34a40d40e8b0e66809c5cdc26618)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "commandUpdate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cronScheduleFullUpdates")
    def cron_schedule_full_updates(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cronScheduleFullUpdates"))

    @cron_schedule_full_updates.setter
    def cron_schedule_full_updates(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42431f5a113b2458c40fce9933a4c212544cb69a108aab4db9a387397aea33d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cronScheduleFullUpdates", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cronScheduleUpdates")
    def cron_schedule_updates(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cronScheduleUpdates"))

    @cron_schedule_updates.setter
    def cron_schedule_updates(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d778cbf0a2091e9238bc92f3b64dfd317cc8c20a70dc36bcb0bb9e6cfe99c329)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cronScheduleUpdates", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operatingSystem")
    def operating_system(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "operatingSystem"))

    @operating_system.setter
    def operating_system(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8366273bde17123e69e9e8bf15d532faeb6a1fa2ab02de466c10bdd5dda35887)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operatingSystem", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tagPatchGroup")
    def tag_patch_group(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tagPatchGroup"))

    @tag_patch_group.setter
    def tag_patch_group(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd0ad356ec36574ec933d246bdf9491f636b0a214adacafeb702df23cd668b72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagPatchGroup", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPatchManagerProps).__jsii_proxy_class__ = lambda : _IPatchManagerPropsProxy


@jsii.interface(jsii_type="tm-cdk-constructs.IRedisClusterProps")
class IRedisClusterProps(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="envName")
    def env_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @env_name.setter
    def env_name(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''
        :stability: experimental
        '''
        ...

    @vpc.setter
    def vpc(self, value: _aws_cdk_aws_ec2_ceddda9d.IVpc) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="allowFrom")
    def allow_from(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''
        :stability: experimental
        '''
        ...

    @allow_from.setter
    def allow_from(
        self,
        value: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="allowFromConstructs")
    def allow_from_constructs(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ec2_ceddda9d.IConnectable]]:
        '''
        :stability: experimental
        '''
        ...

    @allow_from_constructs.setter
    def allow_from_constructs(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ec2_ceddda9d.IConnectable]],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="automaticFailoverEnabled")
    def automatic_failover_enabled(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        ...

    @automatic_failover_enabled.setter
    def automatic_failover_enabled(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="autoMinorVersionUpgrade")
    def auto_minor_version_upgrade(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        ...

    @auto_minor_version_upgrade.setter
    def auto_minor_version_upgrade(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="cacheNodeType")
    def cache_node_type(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @cache_node_type.setter
    def cache_node_type(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="clusterMode")
    def cluster_mode(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @cluster_mode.setter
    def cluster_mode(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="engine")
    def engine(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @engine.setter
    def engine(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="engineVersion")
    def engine_version(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @engine_version.setter
    def engine_version(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="globalReplicationGroupId")
    def global_replication_group_id(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @global_replication_group_id.setter
    def global_replication_group_id(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="multiAzEnabled")
    def multi_az_enabled(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        ...

    @multi_az_enabled.setter
    def multi_az_enabled(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="replicasPerNodeGroup")
    def replicas_per_node_group(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        ...

    @replicas_per_node_group.setter
    def replicas_per_node_group(self, value: typing.Optional[jsii.Number]) -> None:
        ...


class _IRedisClusterPropsProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "tm-cdk-constructs.IRedisClusterProps"

    @builtins.property
    @jsii.member(jsii_name="envName")
    def env_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "envName"))

    @env_name.setter
    def env_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cbcfc13fcd8c944ff3ef99ae7bab32e7d45e5cc28cecec726f0744c8a0d9559)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "envName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.get(self, "vpc"))

    @vpc.setter
    def vpc(self, value: _aws_cdk_aws_ec2_ceddda9d.IVpc) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21f30d07501dce4ff4ca3b2bc308d1794827451589a0083de583c78481bf9c5d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vpc", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowFrom")
    def allow_from(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], jsii.get(self, "allowFrom"))

    @allow_from.setter
    def allow_from(
        self,
        value: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d828e10fefb31677c87894f5994eb46d80bc67eb143d270ec0fed818c84af5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowFrom", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowFromConstructs")
    def allow_from_constructs(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ec2_ceddda9d.IConnectable]]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ec2_ceddda9d.IConnectable]], jsii.get(self, "allowFromConstructs"))

    @allow_from_constructs.setter
    def allow_from_constructs(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ec2_ceddda9d.IConnectable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dac7cb7192347a4a936a3d02b0161c916be9cad3fa629b43c5bf706d5e1f4f05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowFromConstructs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="automaticFailoverEnabled")
    def automatic_failover_enabled(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "automaticFailoverEnabled"))

    @automatic_failover_enabled.setter
    def automatic_failover_enabled(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2bdcce7b655de820ab2c54af62438017ffc4f1949a24578a11c2e28943acdb11)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "automaticFailoverEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autoMinorVersionUpgrade")
    def auto_minor_version_upgrade(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "autoMinorVersionUpgrade"))

    @auto_minor_version_upgrade.setter
    def auto_minor_version_upgrade(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5cfb68ddfdbb88436eebd8dfea20e7bd1cbc9bd9384a0356d1b31b4410cddf1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoMinorVersionUpgrade", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cacheNodeType")
    def cache_node_type(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cacheNodeType"))

    @cache_node_type.setter
    def cache_node_type(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15c8078499519dc59ee806fcf7820d7aaf5a3a371dfcdab144ac9c105694af15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cacheNodeType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterMode")
    def cluster_mode(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterMode"))

    @cluster_mode.setter
    def cluster_mode(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00b8129d6b92784234bf579641c5dc59310fc55315c12754750f50824794f818)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="engine")
    def engine(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "engine"))

    @engine.setter
    def engine(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7845b660f76e0ef3d2be1a3839c141ee259af497e5dcd36033af73a60bda0c64)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "engine", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="engineVersion")
    def engine_version(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "engineVersion"))

    @engine_version.setter
    def engine_version(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fe79cf362cbd588b230640aa31bc6934a14764b7a438d73026f1582367acf9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "engineVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="globalReplicationGroupId")
    def global_replication_group_id(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "globalReplicationGroupId"))

    @global_replication_group_id.setter
    def global_replication_group_id(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8b0acc8f2000364664e53319e1c14cd07770cc9addd325794746b2d6d8f93bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "globalReplicationGroupId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="multiAzEnabled")
    def multi_az_enabled(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "multiAzEnabled"))

    @multi_az_enabled.setter
    def multi_az_enabled(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66192cb7ea51e3252e8c6fac831b9d9fb359e9897448b590313a0646828fe2d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "multiAzEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="replicasPerNodeGroup")
    def replicas_per_node_group(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "replicasPerNodeGroup"))

    @replicas_per_node_group.setter
    def replicas_per_node_group(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__501bdc3ec60ce9982e10ae2cceb69b61a322996849fe4295f6bf6fb9be0971af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "replicasPerNodeGroup", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IRedisClusterProps).__jsii_proxy_class__ = lambda : _IRedisClusterPropsProxy


@jsii.interface(jsii_type="tm-cdk-constructs.ITmEcsDeploymentHookProps")
class ITmEcsDeploymentHookProps(typing_extensions.Protocol):
    '''(experimental) Props for ``TmEcsDeploymentHook``.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> _aws_cdk_aws_ecs_ceddda9d.ICluster:
        '''(experimental) The ECS cluster where the task will be run.

        :stability: experimental
        '''
        ...

    @cluster.setter
    def cluster(self, value: _aws_cdk_aws_ecs_ceddda9d.ICluster) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="command")
    def command(self) -> typing.List[builtins.str]:
        '''(experimental) The command to run in the container.

        This should be an array of strings, where the first element is the command and the subsequent elements are its arguments.

        :stability: experimental
        '''
        ...

    @command.setter
    def command(self, value: typing.List[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="containerName")
    def container_name(self) -> builtins.str:
        '''(experimental) The name of the container in the task definition.

        :stability: experimental
        '''
        ...

    @container_name.setter
    def container_name(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="securityGroups")
    def security_groups(self) -> typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''(experimental) The security groups to associate with the task.

        :stability: experimental
        '''
        ...

    @security_groups.setter
    def security_groups(
        self,
        value: typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="subnets")
    def subnets(self) -> typing.List[_aws_cdk_aws_ec2_ceddda9d.ISubnet]:
        '''(experimental) The subnets where the task will be launched.

        :stability: experimental
        '''
        ...

    @subnets.setter
    def subnets(self, value: typing.List[_aws_cdk_aws_ec2_ceddda9d.ISubnet]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="taskDefinition")
    def task_definition(self) -> _aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition:
        '''(experimental) The ECS task definition to run.

        :stability: experimental
        '''
        ...

    @task_definition.setter
    def task_definition(
        self,
        value: _aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition,
    ) -> None:
        ...


class _ITmEcsDeploymentHookPropsProxy:
    '''(experimental) Props for ``TmEcsDeploymentHook``.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "tm-cdk-constructs.ITmEcsDeploymentHookProps"

    @builtins.property
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> _aws_cdk_aws_ecs_ceddda9d.ICluster:
        '''(experimental) The ECS cluster where the task will be run.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.ICluster, jsii.get(self, "cluster"))

    @cluster.setter
    def cluster(self, value: _aws_cdk_aws_ecs_ceddda9d.ICluster) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20578dcbba1061b4b4d2d2e2df7883c22fb6a07d778f71446e07576d97ca151a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cluster", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="command")
    def command(self) -> typing.List[builtins.str]:
        '''(experimental) The command to run in the container.

        This should be an array of strings, where the first element is the command and the subsequent elements are its arguments.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "command"))

    @command.setter
    def command(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1226c2b955f55700a12fda7e98d36b6ab4e16198bc3de6b401182da2b7d46ee3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "command", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="containerName")
    def container_name(self) -> builtins.str:
        '''(experimental) The name of the container in the task definition.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "containerName"))

    @container_name.setter
    def container_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fa90c86569346a9ddbb1b5060130a99a7389f526aa8c5cac44b03ba56810ab3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "containerName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="securityGroups")
    def security_groups(self) -> typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''(experimental) The security groups to associate with the task.

        :stability: experimental
        '''
        return typing.cast(typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], jsii.get(self, "securityGroups"))

    @security_groups.setter
    def security_groups(
        self,
        value: typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d169b5c8de437cf5b054b95142ef10ebc85b6c73b8b9a77625cd12037f6714d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "securityGroups", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subnets")
    def subnets(self) -> typing.List[_aws_cdk_aws_ec2_ceddda9d.ISubnet]:
        '''(experimental) The subnets where the task will be launched.

        :stability: experimental
        '''
        return typing.cast(typing.List[_aws_cdk_aws_ec2_ceddda9d.ISubnet], jsii.get(self, "subnets"))

    @subnets.setter
    def subnets(self, value: typing.List[_aws_cdk_aws_ec2_ceddda9d.ISubnet]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b4f82c53e1215b1126124f86481689b59a8bfa28f1f5d3e6c23b6a05f33b001)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subnets", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="taskDefinition")
    def task_definition(self) -> _aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition:
        '''(experimental) The ECS task definition to run.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition, jsii.get(self, "taskDefinition"))

    @task_definition.setter
    def task_definition(
        self,
        value: _aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93f64adcaed947aa09410194d2fd63d85795c91df72aeb6021f41a492a674327)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "taskDefinition", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ITmEcsDeploymentHookProps).__jsii_proxy_class__ = lambda : _ITmEcsDeploymentHookPropsProxy


class TmAnsiblePlaybookEc2(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="tm-cdk-constructs.TmAnsiblePlaybookEc2",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: IAnsiblePlaybookEc2Props,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88c5c692c89dfe1c3959a8a9ad871be28c75e88573d8dd44f9bbea85bf74c8bd)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])


class TmApplicationLoadBalancedFargateService(
    _aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedFargateService,
    metaclass=jsii.JSIIMeta,
    jsii_type="tm-cdk-constructs.TmApplicationLoadBalancedFargateService",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        build_context_path: builtins.str,
        build_dockerfile: builtins.str,
        build_container_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        container_port: typing.Optional[jsii.Number] = None,
        custom_http_header_value: typing.Optional[builtins.str] = None,
        ecs_deployment_hook_props: typing.Optional[IIEcsDeploymentHookProps] = None,
        efs_volumes: typing.Optional[typing.Sequence[IIefsVolumes]] = None,
        max_task_count: typing.Optional[jsii.Number] = None,
        min_task_count: typing.Optional[jsii.Number] = None,
        scheduled_task_schedule_expression: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
        scheduled_tasks_command: typing.Optional[builtins.str] = None,
        secrets: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ecs_ceddda9d.Secret]] = None,
        assign_public_ip: typing.Optional[builtins.bool] = None,
        container_cpu: typing.Optional[jsii.Number] = None,
        container_memory_limit_mib: typing.Optional[jsii.Number] = None,
        health_check: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        task_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        capacity_provider_strategies: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy, typing.Dict[builtins.str, typing.Any]]]] = None,
        certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
        circuit_breaker: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker, typing.Dict[builtins.str, typing.Any]]] = None,
        cloud_map_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        cluster: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster] = None,
        deployment_controller: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentController, typing.Dict[builtins.str, typing.Any]]] = None,
        desired_count: typing.Optional[jsii.Number] = None,
        domain_name: typing.Optional[builtins.str] = None,
        domain_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
        enable_ecs_managed_tags: typing.Optional[builtins.bool] = None,
        enable_execute_command: typing.Optional[builtins.bool] = None,
        health_check_grace_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        ip_address_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IpAddressType] = None,
        listener_port: typing.Optional[jsii.Number] = None,
        load_balancer: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer] = None,
        load_balancer_name: typing.Optional[builtins.str] = None,
        max_healthy_percent: typing.Optional[jsii.Number] = None,
        min_healthy_percent: typing.Optional[jsii.Number] = None,
        open_listener: typing.Optional[builtins.bool] = None,
        propagate_tags: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
        protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
        protocol_version: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion] = None,
        public_load_balancer: typing.Optional[builtins.bool] = None,
        record_type: typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedServiceRecordType] = None,
        redirect_http: typing.Optional[builtins.bool] = None,
        service_name: typing.Optional[builtins.str] = None,
        ssl_policy: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy] = None,
        target_protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
        task_image_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        cpu: typing.Optional[jsii.Number] = None,
        ephemeral_storage_gib: typing.Optional[jsii.Number] = None,
        memory_limit_mib: typing.Optional[jsii.Number] = None,
        platform_version: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion] = None,
        runtime_platform: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform, typing.Dict[builtins.str, typing.Any]]] = None,
        task_definition: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param build_context_path: 
        :param build_dockerfile: 
        :param build_container_args: 
        :param container_port: (experimental) The container port.
        :param custom_http_header_value: (experimental) Custom http header value.
        :param ecs_deployment_hook_props: 
        :param efs_volumes: 
        :param max_task_count: (experimental) The maximum number of task.
        :param min_task_count: (experimental) The minumun number od tasks.
        :param scheduled_task_schedule_expression: 
        :param scheduled_tasks_command: 
        :param secrets: 
        :param assign_public_ip: Determines whether the service will be assigned a public IP address. Default: false
        :param container_cpu: The minimum number of CPU units to reserve for the container. Default: - No minimum CPU units reserved.
        :param container_memory_limit_mib: The amount (in MiB) of memory to present to the container. If your container attempts to exceed the allocated memory, the container is terminated. Default: - No memory limit.
        :param health_check: The health check command and associated configuration parameters for the container. Default: - Health check configuration from container.
        :param security_groups: The security groups to associate with the service. If you do not specify a security group, a new security group is created. Default: - A new security group is created.
        :param task_subnets: The subnets to associate with the service. Default: - Public subnets if ``assignPublicIp`` is set, otherwise the first available one of Private, Isolated, Public, in that order.
        :param capacity_provider_strategies: A list of Capacity Provider strategies used to place a service. Default: - undefined
        :param certificate: Certificate Manager certificate to associate with the load balancer. Setting this option will set the load balancer protocol to HTTPS. Default: - No certificate associated with the load balancer, if using the HTTP protocol. For HTTPS, a DNS-validated certificate will be created for the load balancer's specified domain name if a domain name and domain zone are specified.
        :param circuit_breaker: Whether to enable the deployment circuit breaker. If this property is defined, circuit breaker will be implicitly enabled. Default: - disabled
        :param cloud_map_options: The options for configuring an Amazon ECS service to use service discovery. Default: - AWS Cloud Map service discovery is not enabled.
        :param cluster: The name of the cluster that hosts the service. If a cluster is specified, the vpc construct should be omitted. Alternatively, you can omit both cluster and vpc. Default: - create a new cluster; if both cluster and vpc are omitted, a new VPC will be created for you.
        :param deployment_controller: Specifies which deployment controller to use for the service. For more information, see `Amazon ECS Deployment Types <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-types.html>`_ Default: - Rolling update (ECS)
        :param desired_count: The desired number of instantiations of the task definition to keep running on the service. The minimum value is 1 Default: - The default is 1 for all new services and uses the existing service's desired count when updating an existing service.
        :param domain_name: The domain name for the service, e.g. "api.example.com.". Default: - No domain name.
        :param domain_zone: The Route53 hosted zone for the domain, e.g. "example.com.". Default: - No Route53 hosted domain zone.
        :param enable_ecs_managed_tags: Specifies whether to enable Amazon ECS managed tags for the tasks within the service. For more information, see `Tagging Your Amazon ECS Resources <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-using-tags.html>`_ Default: false
        :param enable_execute_command: Whether ECS Exec should be enabled. Default: - false
        :param health_check_grace_period: The period of time, in seconds, that the Amazon ECS service scheduler ignores unhealthy Elastic Load Balancing target health checks after a task has first started. Default: - defaults to 60 seconds if at least one load balancer is in-use and it is not already set
        :param idle_timeout: The load balancer idle timeout, in seconds. Can be between 1 and 4000 seconds Default: - CloudFormation sets idle timeout to 60 seconds
        :param ip_address_type: The type of IP address to use. Default: - IpAddressType.IPV4
        :param listener_port: Listener port of the application load balancer that will serve traffic to the service. Default: - The default listener port is determined from the protocol (port 80 for HTTP, port 443 for HTTPS). A domain name and zone must be also be specified if using HTTPS.
        :param load_balancer: The application load balancer that will serve traffic to the service. The VPC attribute of a load balancer must be specified for it to be used to create a new service with this pattern. [disable-awslint:ref-via-interface] Default: - a new load balancer will be created.
        :param load_balancer_name: Name of the load balancer. Default: - Automatically generated name.
        :param max_healthy_percent: The maximum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that can run in a service during a deployment. Default: - 100 if daemon, otherwise 200
        :param min_healthy_percent: The minimum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that must continue to run and remain healthy during a deployment. Default: - 0 if daemon, otherwise 50
        :param open_listener: Determines whether or not the Security Group for the Load Balancer's Listener will be open to all traffic by default. Default: true -- The security group allows ingress from all IP addresses.
        :param propagate_tags: Specifies whether to propagate the tags from the task definition or the service to the tasks in the service. Tags can only be propagated to the tasks within the service during service creation. Default: - none
        :param protocol: The protocol for connections from clients to the load balancer. The load balancer port is determined from the protocol (port 80 for HTTP, port 443 for HTTPS). If HTTPS, either a certificate or domain name and domain zone must also be specified. Default: HTTP. If a certificate is specified, the protocol will be set by default to HTTPS.
        :param protocol_version: The protocol version to use. Default: ApplicationProtocolVersion.HTTP1
        :param public_load_balancer: Determines whether the Load Balancer will be internet-facing. Default: true
        :param record_type: Specifies whether the Route53 record should be a CNAME, an A record using the Alias feature or no record at all. This is useful if you need to work with DNS systems that do not support alias records. Default: ApplicationLoadBalancedServiceRecordType.ALIAS
        :param redirect_http: Specifies whether the load balancer should redirect traffic on port 80 to port 443 to support HTTP->HTTPS redirects This is only valid if the protocol of the ALB is HTTPS. Default: false
        :param service_name: The name of the service. Default: - CloudFormation-generated name.
        :param ssl_policy: The security policy that defines which ciphers and protocols are supported by the ALB Listener. Default: - The recommended elastic load balancing security policy
        :param target_protocol: The protocol for connections from the load balancer to the ECS tasks. The default target port is determined from the protocol (port 80 for HTTP, port 443 for HTTPS). Default: HTTP.
        :param task_image_options: The properties required to create a new task definition. TaskDefinition or TaskImageOptions must be specified, but not both. Default: none
        :param vpc: The VPC where the container instances will be launched or the elastic network interfaces (ENIs) will be deployed. If a vpc is specified, the cluster construct should be omitted. Alternatively, you can omit both vpc and cluster. Default: - uses the VPC defined in the cluster or creates a new VPC.
        :param cpu: The number of cpu units used by the task. Valid values, which determines your range of valid values for the memory parameter: 256 (.25 vCPU) - Available memory values: 0.5GB, 1GB, 2GB 512 (.5 vCPU) - Available memory values: 1GB, 2GB, 3GB, 4GB 1024 (1 vCPU) - Available memory values: 2GB, 3GB, 4GB, 5GB, 6GB, 7GB, 8GB 2048 (2 vCPU) - Available memory values: Between 4GB and 16GB in 1GB increments 4096 (4 vCPU) - Available memory values: Between 8GB and 30GB in 1GB increments 8192 (8 vCPU) - Available memory values: Between 16GB and 60GB in 4GB increments 16384 (16 vCPU) - Available memory values: Between 32GB and 120GB in 8GB increments This default is set in the underlying FargateTaskDefinition construct. Default: 256
        :param ephemeral_storage_gib: The amount (in GiB) of ephemeral storage to be allocated to the task. The minimum supported value is ``21`` GiB and the maximum supported value is ``200`` GiB. Only supported in Fargate platform version 1.4.0 or later. Default: Undefined, in which case, the task will receive 20GiB ephemeral storage.
        :param memory_limit_mib: The amount (in MiB) of memory used by the task. This field is required and you must use one of the following values, which determines your range of valid values for the cpu parameter: 512 (0.5 GB), 1024 (1 GB), 2048 (2 GB) - Available cpu values: 256 (.25 vCPU) 1024 (1 GB), 2048 (2 GB), 3072 (3 GB), 4096 (4 GB) - Available cpu values: 512 (.5 vCPU) 2048 (2 GB), 3072 (3 GB), 4096 (4 GB), 5120 (5 GB), 6144 (6 GB), 7168 (7 GB), 8192 (8 GB) - Available cpu values: 1024 (1 vCPU) Between 4096 (4 GB) and 16384 (16 GB) in increments of 1024 (1 GB) - Available cpu values: 2048 (2 vCPU) Between 8192 (8 GB) and 30720 (30 GB) in increments of 1024 (1 GB) - Available cpu values: 4096 (4 vCPU) Between 16384 (16 GB) and 61440 (60 GB) in increments of 4096 (4 GB) - Available cpu values: 8192 (8 vCPU) Between 32768 (32 GB) and 122880 (120 GB) in increments of 8192 (8 GB) - Available cpu values: 16384 (16 vCPU) This default is set in the underlying FargateTaskDefinition construct. Default: 512
        :param platform_version: The platform version on which to run your service. If one is not specified, the LATEST platform version is used by default. For more information, see `AWS Fargate Platform Versions <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html>`_ in the Amazon Elastic Container Service Developer Guide. Default: Latest
        :param runtime_platform: The runtime platform of the task definition. Default: - If the property is undefined, ``operatingSystemFamily`` is LINUX and ``cpuArchitecture`` is X86_64
        :param task_definition: The task definition to use for tasks in the service. TaskDefinition or TaskImageOptions must be specified, but not both. [disable-awslint:ref-via-interface] Default: - none

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__276f6d9198fa95fbf00df2891bf40732c0442075150996813b42fc40406667ee)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = TmApplicationLoadBalancedFargateServiceProps(
            build_context_path=build_context_path,
            build_dockerfile=build_dockerfile,
            build_container_args=build_container_args,
            container_port=container_port,
            custom_http_header_value=custom_http_header_value,
            ecs_deployment_hook_props=ecs_deployment_hook_props,
            efs_volumes=efs_volumes,
            max_task_count=max_task_count,
            min_task_count=min_task_count,
            scheduled_task_schedule_expression=scheduled_task_schedule_expression,
            scheduled_tasks_command=scheduled_tasks_command,
            secrets=secrets,
            assign_public_ip=assign_public_ip,
            container_cpu=container_cpu,
            container_memory_limit_mib=container_memory_limit_mib,
            health_check=health_check,
            security_groups=security_groups,
            task_subnets=task_subnets,
            capacity_provider_strategies=capacity_provider_strategies,
            certificate=certificate,
            circuit_breaker=circuit_breaker,
            cloud_map_options=cloud_map_options,
            cluster=cluster,
            deployment_controller=deployment_controller,
            desired_count=desired_count,
            domain_name=domain_name,
            domain_zone=domain_zone,
            enable_ecs_managed_tags=enable_ecs_managed_tags,
            enable_execute_command=enable_execute_command,
            health_check_grace_period=health_check_grace_period,
            idle_timeout=idle_timeout,
            ip_address_type=ip_address_type,
            listener_port=listener_port,
            load_balancer=load_balancer,
            load_balancer_name=load_balancer_name,
            max_healthy_percent=max_healthy_percent,
            min_healthy_percent=min_healthy_percent,
            open_listener=open_listener,
            propagate_tags=propagate_tags,
            protocol=protocol,
            protocol_version=protocol_version,
            public_load_balancer=public_load_balancer,
            record_type=record_type,
            redirect_http=redirect_http,
            service_name=service_name,
            ssl_policy=ssl_policy,
            target_protocol=target_protocol,
            task_image_options=task_image_options,
            vpc=vpc,
            cpu=cpu,
            ephemeral_storage_gib=ephemeral_storage_gib,
            memory_limit_mib=memory_limit_mib,
            platform_version=platform_version,
            runtime_platform=runtime_platform,
            task_definition=task_definition,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="tm-cdk-constructs.TmApplicationLoadBalancedFargateServiceProps",
    jsii_struct_bases=[
        _aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedFargateServiceProps
    ],
    name_mapping={
        "capacity_provider_strategies": "capacityProviderStrategies",
        "certificate": "certificate",
        "circuit_breaker": "circuitBreaker",
        "cloud_map_options": "cloudMapOptions",
        "cluster": "cluster",
        "deployment_controller": "deploymentController",
        "desired_count": "desiredCount",
        "domain_name": "domainName",
        "domain_zone": "domainZone",
        "enable_ecs_managed_tags": "enableECSManagedTags",
        "enable_execute_command": "enableExecuteCommand",
        "health_check_grace_period": "healthCheckGracePeriod",
        "idle_timeout": "idleTimeout",
        "ip_address_type": "ipAddressType",
        "listener_port": "listenerPort",
        "load_balancer": "loadBalancer",
        "load_balancer_name": "loadBalancerName",
        "max_healthy_percent": "maxHealthyPercent",
        "min_healthy_percent": "minHealthyPercent",
        "open_listener": "openListener",
        "propagate_tags": "propagateTags",
        "protocol": "protocol",
        "protocol_version": "protocolVersion",
        "public_load_balancer": "publicLoadBalancer",
        "record_type": "recordType",
        "redirect_http": "redirectHTTP",
        "service_name": "serviceName",
        "ssl_policy": "sslPolicy",
        "target_protocol": "targetProtocol",
        "task_image_options": "taskImageOptions",
        "vpc": "vpc",
        "cpu": "cpu",
        "ephemeral_storage_gib": "ephemeralStorageGiB",
        "memory_limit_mib": "memoryLimitMiB",
        "platform_version": "platformVersion",
        "runtime_platform": "runtimePlatform",
        "task_definition": "taskDefinition",
        "assign_public_ip": "assignPublicIp",
        "container_cpu": "containerCpu",
        "container_memory_limit_mib": "containerMemoryLimitMiB",
        "health_check": "healthCheck",
        "security_groups": "securityGroups",
        "task_subnets": "taskSubnets",
        "build_context_path": "buildContextPath",
        "build_dockerfile": "buildDockerfile",
        "build_container_args": "buildContainerArgs",
        "container_port": "containerPort",
        "custom_http_header_value": "customHttpHeaderValue",
        "ecs_deployment_hook_props": "ecsDeploymentHookProps",
        "efs_volumes": "efsVolumes",
        "max_task_count": "maxTaskCount",
        "min_task_count": "minTaskCount",
        "scheduled_task_schedule_expression": "scheduledTaskScheduleExpression",
        "scheduled_tasks_command": "scheduledTasksCommand",
        "secrets": "secrets",
    },
)
class TmApplicationLoadBalancedFargateServiceProps(
    _aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedFargateServiceProps,
):
    def __init__(
        self,
        *,
        capacity_provider_strategies: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy, typing.Dict[builtins.str, typing.Any]]]] = None,
        certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
        circuit_breaker: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker, typing.Dict[builtins.str, typing.Any]]] = None,
        cloud_map_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        cluster: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster] = None,
        deployment_controller: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentController, typing.Dict[builtins.str, typing.Any]]] = None,
        desired_count: typing.Optional[jsii.Number] = None,
        domain_name: typing.Optional[builtins.str] = None,
        domain_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
        enable_ecs_managed_tags: typing.Optional[builtins.bool] = None,
        enable_execute_command: typing.Optional[builtins.bool] = None,
        health_check_grace_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        ip_address_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IpAddressType] = None,
        listener_port: typing.Optional[jsii.Number] = None,
        load_balancer: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer] = None,
        load_balancer_name: typing.Optional[builtins.str] = None,
        max_healthy_percent: typing.Optional[jsii.Number] = None,
        min_healthy_percent: typing.Optional[jsii.Number] = None,
        open_listener: typing.Optional[builtins.bool] = None,
        propagate_tags: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
        protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
        protocol_version: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion] = None,
        public_load_balancer: typing.Optional[builtins.bool] = None,
        record_type: typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedServiceRecordType] = None,
        redirect_http: typing.Optional[builtins.bool] = None,
        service_name: typing.Optional[builtins.str] = None,
        ssl_policy: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy] = None,
        target_protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
        task_image_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        cpu: typing.Optional[jsii.Number] = None,
        ephemeral_storage_gib: typing.Optional[jsii.Number] = None,
        memory_limit_mib: typing.Optional[jsii.Number] = None,
        platform_version: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion] = None,
        runtime_platform: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform, typing.Dict[builtins.str, typing.Any]]] = None,
        task_definition: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition] = None,
        assign_public_ip: typing.Optional[builtins.bool] = None,
        container_cpu: typing.Optional[jsii.Number] = None,
        container_memory_limit_mib: typing.Optional[jsii.Number] = None,
        health_check: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        task_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        build_context_path: builtins.str,
        build_dockerfile: builtins.str,
        build_container_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        container_port: typing.Optional[jsii.Number] = None,
        custom_http_header_value: typing.Optional[builtins.str] = None,
        ecs_deployment_hook_props: typing.Optional[IIEcsDeploymentHookProps] = None,
        efs_volumes: typing.Optional[typing.Sequence[IIefsVolumes]] = None,
        max_task_count: typing.Optional[jsii.Number] = None,
        min_task_count: typing.Optional[jsii.Number] = None,
        scheduled_task_schedule_expression: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
        scheduled_tasks_command: typing.Optional[builtins.str] = None,
        secrets: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ecs_ceddda9d.Secret]] = None,
    ) -> None:
        '''(experimental) Represents the configuration for an ecsPatterns.

        :param capacity_provider_strategies: A list of Capacity Provider strategies used to place a service. Default: - undefined
        :param certificate: Certificate Manager certificate to associate with the load balancer. Setting this option will set the load balancer protocol to HTTPS. Default: - No certificate associated with the load balancer, if using the HTTP protocol. For HTTPS, a DNS-validated certificate will be created for the load balancer's specified domain name if a domain name and domain zone are specified.
        :param circuit_breaker: Whether to enable the deployment circuit breaker. If this property is defined, circuit breaker will be implicitly enabled. Default: - disabled
        :param cloud_map_options: The options for configuring an Amazon ECS service to use service discovery. Default: - AWS Cloud Map service discovery is not enabled.
        :param cluster: The name of the cluster that hosts the service. If a cluster is specified, the vpc construct should be omitted. Alternatively, you can omit both cluster and vpc. Default: - create a new cluster; if both cluster and vpc are omitted, a new VPC will be created for you.
        :param deployment_controller: Specifies which deployment controller to use for the service. For more information, see `Amazon ECS Deployment Types <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-types.html>`_ Default: - Rolling update (ECS)
        :param desired_count: The desired number of instantiations of the task definition to keep running on the service. The minimum value is 1 Default: - The default is 1 for all new services and uses the existing service's desired count when updating an existing service.
        :param domain_name: The domain name for the service, e.g. "api.example.com.". Default: - No domain name.
        :param domain_zone: The Route53 hosted zone for the domain, e.g. "example.com.". Default: - No Route53 hosted domain zone.
        :param enable_ecs_managed_tags: Specifies whether to enable Amazon ECS managed tags for the tasks within the service. For more information, see `Tagging Your Amazon ECS Resources <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-using-tags.html>`_ Default: false
        :param enable_execute_command: Whether ECS Exec should be enabled. Default: - false
        :param health_check_grace_period: The period of time, in seconds, that the Amazon ECS service scheduler ignores unhealthy Elastic Load Balancing target health checks after a task has first started. Default: - defaults to 60 seconds if at least one load balancer is in-use and it is not already set
        :param idle_timeout: The load balancer idle timeout, in seconds. Can be between 1 and 4000 seconds Default: - CloudFormation sets idle timeout to 60 seconds
        :param ip_address_type: The type of IP address to use. Default: - IpAddressType.IPV4
        :param listener_port: Listener port of the application load balancer that will serve traffic to the service. Default: - The default listener port is determined from the protocol (port 80 for HTTP, port 443 for HTTPS). A domain name and zone must be also be specified if using HTTPS.
        :param load_balancer: The application load balancer that will serve traffic to the service. The VPC attribute of a load balancer must be specified for it to be used to create a new service with this pattern. [disable-awslint:ref-via-interface] Default: - a new load balancer will be created.
        :param load_balancer_name: Name of the load balancer. Default: - Automatically generated name.
        :param max_healthy_percent: The maximum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that can run in a service during a deployment. Default: - 100 if daemon, otherwise 200
        :param min_healthy_percent: The minimum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that must continue to run and remain healthy during a deployment. Default: - 0 if daemon, otherwise 50
        :param open_listener: Determines whether or not the Security Group for the Load Balancer's Listener will be open to all traffic by default. Default: true -- The security group allows ingress from all IP addresses.
        :param propagate_tags: Specifies whether to propagate the tags from the task definition or the service to the tasks in the service. Tags can only be propagated to the tasks within the service during service creation. Default: - none
        :param protocol: The protocol for connections from clients to the load balancer. The load balancer port is determined from the protocol (port 80 for HTTP, port 443 for HTTPS). If HTTPS, either a certificate or domain name and domain zone must also be specified. Default: HTTP. If a certificate is specified, the protocol will be set by default to HTTPS.
        :param protocol_version: The protocol version to use. Default: ApplicationProtocolVersion.HTTP1
        :param public_load_balancer: Determines whether the Load Balancer will be internet-facing. Default: true
        :param record_type: Specifies whether the Route53 record should be a CNAME, an A record using the Alias feature or no record at all. This is useful if you need to work with DNS systems that do not support alias records. Default: ApplicationLoadBalancedServiceRecordType.ALIAS
        :param redirect_http: Specifies whether the load balancer should redirect traffic on port 80 to port 443 to support HTTP->HTTPS redirects This is only valid if the protocol of the ALB is HTTPS. Default: false
        :param service_name: The name of the service. Default: - CloudFormation-generated name.
        :param ssl_policy: The security policy that defines which ciphers and protocols are supported by the ALB Listener. Default: - The recommended elastic load balancing security policy
        :param target_protocol: The protocol for connections from the load balancer to the ECS tasks. The default target port is determined from the protocol (port 80 for HTTP, port 443 for HTTPS). Default: HTTP.
        :param task_image_options: The properties required to create a new task definition. TaskDefinition or TaskImageOptions must be specified, but not both. Default: none
        :param vpc: The VPC where the container instances will be launched or the elastic network interfaces (ENIs) will be deployed. If a vpc is specified, the cluster construct should be omitted. Alternatively, you can omit both vpc and cluster. Default: - uses the VPC defined in the cluster or creates a new VPC.
        :param cpu: The number of cpu units used by the task. Valid values, which determines your range of valid values for the memory parameter: 256 (.25 vCPU) - Available memory values: 0.5GB, 1GB, 2GB 512 (.5 vCPU) - Available memory values: 1GB, 2GB, 3GB, 4GB 1024 (1 vCPU) - Available memory values: 2GB, 3GB, 4GB, 5GB, 6GB, 7GB, 8GB 2048 (2 vCPU) - Available memory values: Between 4GB and 16GB in 1GB increments 4096 (4 vCPU) - Available memory values: Between 8GB and 30GB in 1GB increments 8192 (8 vCPU) - Available memory values: Between 16GB and 60GB in 4GB increments 16384 (16 vCPU) - Available memory values: Between 32GB and 120GB in 8GB increments This default is set in the underlying FargateTaskDefinition construct. Default: 256
        :param ephemeral_storage_gib: The amount (in GiB) of ephemeral storage to be allocated to the task. The minimum supported value is ``21`` GiB and the maximum supported value is ``200`` GiB. Only supported in Fargate platform version 1.4.0 or later. Default: Undefined, in which case, the task will receive 20GiB ephemeral storage.
        :param memory_limit_mib: The amount (in MiB) of memory used by the task. This field is required and you must use one of the following values, which determines your range of valid values for the cpu parameter: 512 (0.5 GB), 1024 (1 GB), 2048 (2 GB) - Available cpu values: 256 (.25 vCPU) 1024 (1 GB), 2048 (2 GB), 3072 (3 GB), 4096 (4 GB) - Available cpu values: 512 (.5 vCPU) 2048 (2 GB), 3072 (3 GB), 4096 (4 GB), 5120 (5 GB), 6144 (6 GB), 7168 (7 GB), 8192 (8 GB) - Available cpu values: 1024 (1 vCPU) Between 4096 (4 GB) and 16384 (16 GB) in increments of 1024 (1 GB) - Available cpu values: 2048 (2 vCPU) Between 8192 (8 GB) and 30720 (30 GB) in increments of 1024 (1 GB) - Available cpu values: 4096 (4 vCPU) Between 16384 (16 GB) and 61440 (60 GB) in increments of 4096 (4 GB) - Available cpu values: 8192 (8 vCPU) Between 32768 (32 GB) and 122880 (120 GB) in increments of 8192 (8 GB) - Available cpu values: 16384 (16 vCPU) This default is set in the underlying FargateTaskDefinition construct. Default: 512
        :param platform_version: The platform version on which to run your service. If one is not specified, the LATEST platform version is used by default. For more information, see `AWS Fargate Platform Versions <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html>`_ in the Amazon Elastic Container Service Developer Guide. Default: Latest
        :param runtime_platform: The runtime platform of the task definition. Default: - If the property is undefined, ``operatingSystemFamily`` is LINUX and ``cpuArchitecture`` is X86_64
        :param task_definition: The task definition to use for tasks in the service. TaskDefinition or TaskImageOptions must be specified, but not both. [disable-awslint:ref-via-interface] Default: - none
        :param assign_public_ip: Determines whether the service will be assigned a public IP address. Default: false
        :param container_cpu: The minimum number of CPU units to reserve for the container. Default: - No minimum CPU units reserved.
        :param container_memory_limit_mib: The amount (in MiB) of memory to present to the container. If your container attempts to exceed the allocated memory, the container is terminated. Default: - No memory limit.
        :param health_check: The health check command and associated configuration parameters for the container. Default: - Health check configuration from container.
        :param security_groups: The security groups to associate with the service. If you do not specify a security group, a new security group is created. Default: - A new security group is created.
        :param task_subnets: The subnets to associate with the service. Default: - Public subnets if ``assignPublicIp`` is set, otherwise the first available one of Private, Isolated, Public, in that order.
        :param build_context_path: 
        :param build_dockerfile: 
        :param build_container_args: 
        :param container_port: (experimental) The container port.
        :param custom_http_header_value: (experimental) Custom http header value.
        :param ecs_deployment_hook_props: 
        :param efs_volumes: 
        :param max_task_count: (experimental) The maximum number of task.
        :param min_task_count: (experimental) The minumun number od tasks.
        :param scheduled_task_schedule_expression: 
        :param scheduled_tasks_command: 
        :param secrets: 

        :stability: experimental
        '''
        if isinstance(circuit_breaker, dict):
            circuit_breaker = _aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker(**circuit_breaker)
        if isinstance(cloud_map_options, dict):
            cloud_map_options = _aws_cdk_aws_ecs_ceddda9d.CloudMapOptions(**cloud_map_options)
        if isinstance(deployment_controller, dict):
            deployment_controller = _aws_cdk_aws_ecs_ceddda9d.DeploymentController(**deployment_controller)
        if isinstance(task_image_options, dict):
            task_image_options = _aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions(**task_image_options)
        if isinstance(runtime_platform, dict):
            runtime_platform = _aws_cdk_aws_ecs_ceddda9d.RuntimePlatform(**runtime_platform)
        if isinstance(health_check, dict):
            health_check = _aws_cdk_aws_ecs_ceddda9d.HealthCheck(**health_check)
        if isinstance(task_subnets, dict):
            task_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**task_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1dda355626d26bd05dee708afc45defd28861f9a33472bb8ec239ff3cd194d88)
            check_type(argname="argument capacity_provider_strategies", value=capacity_provider_strategies, expected_type=type_hints["capacity_provider_strategies"])
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument circuit_breaker", value=circuit_breaker, expected_type=type_hints["circuit_breaker"])
            check_type(argname="argument cloud_map_options", value=cloud_map_options, expected_type=type_hints["cloud_map_options"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument deployment_controller", value=deployment_controller, expected_type=type_hints["deployment_controller"])
            check_type(argname="argument desired_count", value=desired_count, expected_type=type_hints["desired_count"])
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument domain_zone", value=domain_zone, expected_type=type_hints["domain_zone"])
            check_type(argname="argument enable_ecs_managed_tags", value=enable_ecs_managed_tags, expected_type=type_hints["enable_ecs_managed_tags"])
            check_type(argname="argument enable_execute_command", value=enable_execute_command, expected_type=type_hints["enable_execute_command"])
            check_type(argname="argument health_check_grace_period", value=health_check_grace_period, expected_type=type_hints["health_check_grace_period"])
            check_type(argname="argument idle_timeout", value=idle_timeout, expected_type=type_hints["idle_timeout"])
            check_type(argname="argument ip_address_type", value=ip_address_type, expected_type=type_hints["ip_address_type"])
            check_type(argname="argument listener_port", value=listener_port, expected_type=type_hints["listener_port"])
            check_type(argname="argument load_balancer", value=load_balancer, expected_type=type_hints["load_balancer"])
            check_type(argname="argument load_balancer_name", value=load_balancer_name, expected_type=type_hints["load_balancer_name"])
            check_type(argname="argument max_healthy_percent", value=max_healthy_percent, expected_type=type_hints["max_healthy_percent"])
            check_type(argname="argument min_healthy_percent", value=min_healthy_percent, expected_type=type_hints["min_healthy_percent"])
            check_type(argname="argument open_listener", value=open_listener, expected_type=type_hints["open_listener"])
            check_type(argname="argument propagate_tags", value=propagate_tags, expected_type=type_hints["propagate_tags"])
            check_type(argname="argument protocol", value=protocol, expected_type=type_hints["protocol"])
            check_type(argname="argument protocol_version", value=protocol_version, expected_type=type_hints["protocol_version"])
            check_type(argname="argument public_load_balancer", value=public_load_balancer, expected_type=type_hints["public_load_balancer"])
            check_type(argname="argument record_type", value=record_type, expected_type=type_hints["record_type"])
            check_type(argname="argument redirect_http", value=redirect_http, expected_type=type_hints["redirect_http"])
            check_type(argname="argument service_name", value=service_name, expected_type=type_hints["service_name"])
            check_type(argname="argument ssl_policy", value=ssl_policy, expected_type=type_hints["ssl_policy"])
            check_type(argname="argument target_protocol", value=target_protocol, expected_type=type_hints["target_protocol"])
            check_type(argname="argument task_image_options", value=task_image_options, expected_type=type_hints["task_image_options"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument cpu", value=cpu, expected_type=type_hints["cpu"])
            check_type(argname="argument ephemeral_storage_gib", value=ephemeral_storage_gib, expected_type=type_hints["ephemeral_storage_gib"])
            check_type(argname="argument memory_limit_mib", value=memory_limit_mib, expected_type=type_hints["memory_limit_mib"])
            check_type(argname="argument platform_version", value=platform_version, expected_type=type_hints["platform_version"])
            check_type(argname="argument runtime_platform", value=runtime_platform, expected_type=type_hints["runtime_platform"])
            check_type(argname="argument task_definition", value=task_definition, expected_type=type_hints["task_definition"])
            check_type(argname="argument assign_public_ip", value=assign_public_ip, expected_type=type_hints["assign_public_ip"])
            check_type(argname="argument container_cpu", value=container_cpu, expected_type=type_hints["container_cpu"])
            check_type(argname="argument container_memory_limit_mib", value=container_memory_limit_mib, expected_type=type_hints["container_memory_limit_mib"])
            check_type(argname="argument health_check", value=health_check, expected_type=type_hints["health_check"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument task_subnets", value=task_subnets, expected_type=type_hints["task_subnets"])
            check_type(argname="argument build_context_path", value=build_context_path, expected_type=type_hints["build_context_path"])
            check_type(argname="argument build_dockerfile", value=build_dockerfile, expected_type=type_hints["build_dockerfile"])
            check_type(argname="argument build_container_args", value=build_container_args, expected_type=type_hints["build_container_args"])
            check_type(argname="argument container_port", value=container_port, expected_type=type_hints["container_port"])
            check_type(argname="argument custom_http_header_value", value=custom_http_header_value, expected_type=type_hints["custom_http_header_value"])
            check_type(argname="argument ecs_deployment_hook_props", value=ecs_deployment_hook_props, expected_type=type_hints["ecs_deployment_hook_props"])
            check_type(argname="argument efs_volumes", value=efs_volumes, expected_type=type_hints["efs_volumes"])
            check_type(argname="argument max_task_count", value=max_task_count, expected_type=type_hints["max_task_count"])
            check_type(argname="argument min_task_count", value=min_task_count, expected_type=type_hints["min_task_count"])
            check_type(argname="argument scheduled_task_schedule_expression", value=scheduled_task_schedule_expression, expected_type=type_hints["scheduled_task_schedule_expression"])
            check_type(argname="argument scheduled_tasks_command", value=scheduled_tasks_command, expected_type=type_hints["scheduled_tasks_command"])
            check_type(argname="argument secrets", value=secrets, expected_type=type_hints["secrets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "build_context_path": build_context_path,
            "build_dockerfile": build_dockerfile,
        }
        if capacity_provider_strategies is not None:
            self._values["capacity_provider_strategies"] = capacity_provider_strategies
        if certificate is not None:
            self._values["certificate"] = certificate
        if circuit_breaker is not None:
            self._values["circuit_breaker"] = circuit_breaker
        if cloud_map_options is not None:
            self._values["cloud_map_options"] = cloud_map_options
        if cluster is not None:
            self._values["cluster"] = cluster
        if deployment_controller is not None:
            self._values["deployment_controller"] = deployment_controller
        if desired_count is not None:
            self._values["desired_count"] = desired_count
        if domain_name is not None:
            self._values["domain_name"] = domain_name
        if domain_zone is not None:
            self._values["domain_zone"] = domain_zone
        if enable_ecs_managed_tags is not None:
            self._values["enable_ecs_managed_tags"] = enable_ecs_managed_tags
        if enable_execute_command is not None:
            self._values["enable_execute_command"] = enable_execute_command
        if health_check_grace_period is not None:
            self._values["health_check_grace_period"] = health_check_grace_period
        if idle_timeout is not None:
            self._values["idle_timeout"] = idle_timeout
        if ip_address_type is not None:
            self._values["ip_address_type"] = ip_address_type
        if listener_port is not None:
            self._values["listener_port"] = listener_port
        if load_balancer is not None:
            self._values["load_balancer"] = load_balancer
        if load_balancer_name is not None:
            self._values["load_balancer_name"] = load_balancer_name
        if max_healthy_percent is not None:
            self._values["max_healthy_percent"] = max_healthy_percent
        if min_healthy_percent is not None:
            self._values["min_healthy_percent"] = min_healthy_percent
        if open_listener is not None:
            self._values["open_listener"] = open_listener
        if propagate_tags is not None:
            self._values["propagate_tags"] = propagate_tags
        if protocol is not None:
            self._values["protocol"] = protocol
        if protocol_version is not None:
            self._values["protocol_version"] = protocol_version
        if public_load_balancer is not None:
            self._values["public_load_balancer"] = public_load_balancer
        if record_type is not None:
            self._values["record_type"] = record_type
        if redirect_http is not None:
            self._values["redirect_http"] = redirect_http
        if service_name is not None:
            self._values["service_name"] = service_name
        if ssl_policy is not None:
            self._values["ssl_policy"] = ssl_policy
        if target_protocol is not None:
            self._values["target_protocol"] = target_protocol
        if task_image_options is not None:
            self._values["task_image_options"] = task_image_options
        if vpc is not None:
            self._values["vpc"] = vpc
        if cpu is not None:
            self._values["cpu"] = cpu
        if ephemeral_storage_gib is not None:
            self._values["ephemeral_storage_gib"] = ephemeral_storage_gib
        if memory_limit_mib is not None:
            self._values["memory_limit_mib"] = memory_limit_mib
        if platform_version is not None:
            self._values["platform_version"] = platform_version
        if runtime_platform is not None:
            self._values["runtime_platform"] = runtime_platform
        if task_definition is not None:
            self._values["task_definition"] = task_definition
        if assign_public_ip is not None:
            self._values["assign_public_ip"] = assign_public_ip
        if container_cpu is not None:
            self._values["container_cpu"] = container_cpu
        if container_memory_limit_mib is not None:
            self._values["container_memory_limit_mib"] = container_memory_limit_mib
        if health_check is not None:
            self._values["health_check"] = health_check
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if task_subnets is not None:
            self._values["task_subnets"] = task_subnets
        if build_container_args is not None:
            self._values["build_container_args"] = build_container_args
        if container_port is not None:
            self._values["container_port"] = container_port
        if custom_http_header_value is not None:
            self._values["custom_http_header_value"] = custom_http_header_value
        if ecs_deployment_hook_props is not None:
            self._values["ecs_deployment_hook_props"] = ecs_deployment_hook_props
        if efs_volumes is not None:
            self._values["efs_volumes"] = efs_volumes
        if max_task_count is not None:
            self._values["max_task_count"] = max_task_count
        if min_task_count is not None:
            self._values["min_task_count"] = min_task_count
        if scheduled_task_schedule_expression is not None:
            self._values["scheduled_task_schedule_expression"] = scheduled_task_schedule_expression
        if scheduled_tasks_command is not None:
            self._values["scheduled_tasks_command"] = scheduled_tasks_command
        if secrets is not None:
            self._values["secrets"] = secrets

    @builtins.property
    def capacity_provider_strategies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy]]:
        '''A list of Capacity Provider strategies used to place a service.

        :default: - undefined
        '''
        result = self._values.get("capacity_provider_strategies")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy]], result)

    @builtins.property
    def certificate(
        self,
    ) -> typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate]:
        '''Certificate Manager certificate to associate with the load balancer.

        Setting this option will set the load balancer protocol to HTTPS.

        :default:

        - No certificate associated with the load balancer, if using
        the HTTP protocol. For HTTPS, a DNS-validated certificate will be
        created for the load balancer's specified domain name if a domain name
        and domain zone are specified.
        '''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate], result)

    @builtins.property
    def circuit_breaker(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker]:
        '''Whether to enable the deployment circuit breaker.

        If this property is defined, circuit breaker will be implicitly
        enabled.

        :default: - disabled
        '''
        result = self._values.get("circuit_breaker")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker], result)

    @builtins.property
    def cloud_map_options(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions]:
        '''The options for configuring an Amazon ECS service to use service discovery.

        :default: - AWS Cloud Map service discovery is not enabled.
        '''
        result = self._values.get("cloud_map_options")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions], result)

    @builtins.property
    def cluster(self) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster]:
        '''The name of the cluster that hosts the service.

        If a cluster is specified, the vpc construct should be omitted. Alternatively, you can omit both cluster and vpc.

        :default: - create a new cluster; if both cluster and vpc are omitted, a new VPC will be created for you.
        '''
        result = self._values.get("cluster")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster], result)

    @builtins.property
    def deployment_controller(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.DeploymentController]:
        '''Specifies which deployment controller to use for the service.

        For more information, see
        `Amazon ECS Deployment Types <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-types.html>`_

        :default: - Rolling update (ECS)
        '''
        result = self._values.get("deployment_controller")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.DeploymentController], result)

    @builtins.property
    def desired_count(self) -> typing.Optional[jsii.Number]:
        '''The desired number of instantiations of the task definition to keep running on the service.

        The minimum value is 1

        :default:

        - The default is 1 for all new services and uses the existing service's desired count
        when updating an existing service.
        '''
        result = self._values.get("desired_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def domain_name(self) -> typing.Optional[builtins.str]:
        '''The domain name for the service, e.g. "api.example.com.".

        :default: - No domain name.
        '''
        result = self._values.get("domain_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_zone(self) -> typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone]:
        '''The Route53 hosted zone for the domain, e.g. "example.com.".

        :default: - No Route53 hosted domain zone.
        '''
        result = self._values.get("domain_zone")
        return typing.cast(typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone], result)

    @builtins.property
    def enable_ecs_managed_tags(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether to enable Amazon ECS managed tags for the tasks within the service.

        For more information, see
        `Tagging Your Amazon ECS Resources <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-using-tags.html>`_

        :default: false
        '''
        result = self._values.get("enable_ecs_managed_tags")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_execute_command(self) -> typing.Optional[builtins.bool]:
        '''Whether ECS Exec should be enabled.

        :default: - false
        '''
        result = self._values.get("enable_execute_command")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def health_check_grace_period(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The period of time, in seconds, that the Amazon ECS service scheduler ignores unhealthy Elastic Load Balancing target health checks after a task has first started.

        :default: - defaults to 60 seconds if at least one load balancer is in-use and it is not already set
        '''
        result = self._values.get("health_check_grace_period")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def idle_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The load balancer idle timeout, in seconds.

        Can be between 1 and 4000 seconds

        :default: - CloudFormation sets idle timeout to 60 seconds
        '''
        result = self._values.get("idle_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def ip_address_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IpAddressType]:
        '''The type of IP address to use.

        :default: - IpAddressType.IPV4
        '''
        result = self._values.get("ip_address_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IpAddressType], result)

    @builtins.property
    def listener_port(self) -> typing.Optional[jsii.Number]:
        '''Listener port of the application load balancer that will serve traffic to the service.

        :default:

        - The default listener port is determined from the protocol (port 80 for HTTP,
        port 443 for HTTPS). A domain name and zone must be also be specified if using HTTPS.
        '''
        result = self._values.get("listener_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def load_balancer(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer]:
        '''The application load balancer that will serve traffic to the service.

        The VPC attribute of a load balancer must be specified for it to be used
        to create a new service with this pattern.

        [disable-awslint:ref-via-interface]

        :default: - a new load balancer will be created.
        '''
        result = self._values.get("load_balancer")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer], result)

    @builtins.property
    def load_balancer_name(self) -> typing.Optional[builtins.str]:
        '''Name of the load balancer.

        :default: - Automatically generated name.
        '''
        result = self._values.get("load_balancer_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_healthy_percent(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that can run in a service during a deployment.

        :default: - 100 if daemon, otherwise 200
        '''
        result = self._values.get("max_healthy_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_healthy_percent(self) -> typing.Optional[jsii.Number]:
        '''The minimum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that must continue to run and remain healthy during a deployment.

        :default: - 0 if daemon, otherwise 50
        '''
        result = self._values.get("min_healthy_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def open_listener(self) -> typing.Optional[builtins.bool]:
        '''Determines whether or not the Security Group for the Load Balancer's Listener will be open to all traffic by default.

        :default: true -- The security group allows ingress from all IP addresses.
        '''
        result = self._values.get("open_listener")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def propagate_tags(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource]:
        '''Specifies whether to propagate the tags from the task definition or the service to the tasks in the service.

        Tags can only be propagated to the tasks within the service during service creation.

        :default: - none
        '''
        result = self._values.get("propagate_tags")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource], result)

    @builtins.property
    def protocol(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol]:
        '''The protocol for connections from clients to the load balancer.

        The load balancer port is determined from the protocol (port 80 for
        HTTP, port 443 for HTTPS).  If HTTPS, either a certificate or domain
        name and domain zone must also be specified.

        :default:

        HTTP. If a certificate is specified, the protocol will be
        set by default to HTTPS.
        '''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol], result)

    @builtins.property
    def protocol_version(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion]:
        '''The protocol version to use.

        :default: ApplicationProtocolVersion.HTTP1
        '''
        result = self._values.get("protocol_version")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion], result)

    @builtins.property
    def public_load_balancer(self) -> typing.Optional[builtins.bool]:
        '''Determines whether the Load Balancer will be internet-facing.

        :default: true
        '''
        result = self._values.get("public_load_balancer")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def record_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedServiceRecordType]:
        '''Specifies whether the Route53 record should be a CNAME, an A record using the Alias feature or no record at all.

        This is useful if you need to work with DNS systems that do not support alias records.

        :default: ApplicationLoadBalancedServiceRecordType.ALIAS
        '''
        result = self._values.get("record_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedServiceRecordType], result)

    @builtins.property
    def redirect_http(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether the load balancer should redirect traffic on port 80 to port 443 to support HTTP->HTTPS redirects This is only valid if the protocol of the ALB is HTTPS.

        :default: false
        '''
        result = self._values.get("redirect_http")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def service_name(self) -> typing.Optional[builtins.str]:
        '''The name of the service.

        :default: - CloudFormation-generated name.
        '''
        result = self._values.get("service_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssl_policy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy]:
        '''The security policy that defines which ciphers and protocols are supported by the ALB Listener.

        :default: - The recommended elastic load balancing security policy
        '''
        result = self._values.get("ssl_policy")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy], result)

    @builtins.property
    def target_protocol(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol]:
        '''The protocol for connections from the load balancer to the ECS tasks.

        The default target port is determined from the protocol (port 80 for
        HTTP, port 443 for HTTPS).

        :default: HTTP.
        '''
        result = self._values.get("target_protocol")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol], result)

    @builtins.property
    def task_image_options(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions]:
        '''The properties required to create a new task definition.

        TaskDefinition or TaskImageOptions must be specified, but not both.

        :default: none
        '''
        result = self._values.get("task_image_options")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''The VPC where the container instances will be launched or the elastic network interfaces (ENIs) will be deployed.

        If a vpc is specified, the cluster construct should be omitted. Alternatively, you can omit both vpc and cluster.

        :default: - uses the VPC defined in the cluster or creates a new VPC.
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def cpu(self) -> typing.Optional[jsii.Number]:
        '''The number of cpu units used by the task.

        Valid values, which determines your range of valid values for the memory parameter:

        256 (.25 vCPU) - Available memory values: 0.5GB, 1GB, 2GB

        512 (.5 vCPU) - Available memory values: 1GB, 2GB, 3GB, 4GB

        1024 (1 vCPU) - Available memory values: 2GB, 3GB, 4GB, 5GB, 6GB, 7GB, 8GB

        2048 (2 vCPU) - Available memory values: Between 4GB and 16GB in 1GB increments

        4096 (4 vCPU) - Available memory values: Between 8GB and 30GB in 1GB increments

        8192 (8 vCPU) - Available memory values: Between 16GB and 60GB in 4GB increments

        16384 (16 vCPU) - Available memory values: Between 32GB and 120GB in 8GB increments

        This default is set in the underlying FargateTaskDefinition construct.

        :default: 256
        '''
        result = self._values.get("cpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ephemeral_storage_gib(self) -> typing.Optional[jsii.Number]:
        '''The amount (in GiB) of ephemeral storage to be allocated to the task.

        The minimum supported value is ``21`` GiB and the maximum supported value is ``200`` GiB.

        Only supported in Fargate platform version 1.4.0 or later.

        :default: Undefined, in which case, the task will receive 20GiB ephemeral storage.
        '''
        result = self._values.get("ephemeral_storage_gib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_limit_mib(self) -> typing.Optional[jsii.Number]:
        '''The amount (in MiB) of memory used by the task.

        This field is required and you must use one of the following values, which determines your range of valid values
        for the cpu parameter:

        512 (0.5 GB), 1024 (1 GB), 2048 (2 GB) - Available cpu values: 256 (.25 vCPU)

        1024 (1 GB), 2048 (2 GB), 3072 (3 GB), 4096 (4 GB) - Available cpu values: 512 (.5 vCPU)

        2048 (2 GB), 3072 (3 GB), 4096 (4 GB), 5120 (5 GB), 6144 (6 GB), 7168 (7 GB), 8192 (8 GB) - Available cpu values: 1024 (1 vCPU)

        Between 4096 (4 GB) and 16384 (16 GB) in increments of 1024 (1 GB) - Available cpu values: 2048 (2 vCPU)

        Between 8192 (8 GB) and 30720 (30 GB) in increments of 1024 (1 GB) - Available cpu values: 4096 (4 vCPU)

        Between 16384 (16 GB) and 61440 (60 GB) in increments of 4096 (4 GB) - Available cpu values: 8192 (8 vCPU)

        Between 32768 (32 GB) and 122880 (120 GB) in increments of 8192 (8 GB) - Available cpu values: 16384 (16 vCPU)

        This default is set in the underlying FargateTaskDefinition construct.

        :default: 512
        '''
        result = self._values.get("memory_limit_mib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def platform_version(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion]:
        '''The platform version on which to run your service.

        If one is not specified, the LATEST platform version is used by default. For more information, see
        `AWS Fargate Platform Versions <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html>`_
        in the Amazon Elastic Container Service Developer Guide.

        :default: Latest
        '''
        result = self._values.get("platform_version")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion], result)

    @builtins.property
    def runtime_platform(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform]:
        '''The runtime platform of the task definition.

        :default: - If the property is undefined, ``operatingSystemFamily`` is LINUX and ``cpuArchitecture`` is X86_64
        '''
        result = self._values.get("runtime_platform")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform], result)

    @builtins.property
    def task_definition(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition]:
        '''The task definition to use for tasks in the service. TaskDefinition or TaskImageOptions must be specified, but not both.

        [disable-awslint:ref-via-interface]

        :default: - none
        '''
        result = self._values.get("task_definition")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition], result)

    @builtins.property
    def assign_public_ip(self) -> typing.Optional[builtins.bool]:
        '''Determines whether the service will be assigned a public IP address.

        :default: false
        '''
        result = self._values.get("assign_public_ip")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def container_cpu(self) -> typing.Optional[jsii.Number]:
        '''The minimum number of CPU units to reserve for the container.

        :default: - No minimum CPU units reserved.
        '''
        result = self._values.get("container_cpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def container_memory_limit_mib(self) -> typing.Optional[jsii.Number]:
        '''The amount (in MiB) of memory to present to the container.

        If your container attempts to exceed the allocated memory, the container
        is terminated.

        :default: - No memory limit.
        '''
        result = self._values.get("container_memory_limit_mib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def health_check(self) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.HealthCheck]:
        '''The health check command and associated configuration parameters for the container.

        :default: - Health check configuration from container.
        '''
        result = self._values.get("health_check")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.HealthCheck], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''The security groups to associate with the service.

        If you do not specify a security group, a new security group is created.

        :default: - A new security group is created.
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def task_subnets(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''The subnets to associate with the service.

        :default: - Public subnets if ``assignPublicIp`` is set, otherwise the first available one of Private, Isolated, Public, in that order.
        '''
        result = self._values.get("task_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def build_context_path(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("build_context_path")
        assert result is not None, "Required property 'build_context_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def build_dockerfile(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("build_dockerfile")
        assert result is not None, "Required property 'build_dockerfile' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def build_container_args(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("build_container_args")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def container_port(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The container port.

        :stability: experimental
        '''
        result = self._values.get("container_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def custom_http_header_value(self) -> typing.Optional[builtins.str]:
        '''(experimental) Custom http header value.

        :stability: experimental
        '''
        result = self._values.get("custom_http_header_value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ecs_deployment_hook_props(self) -> typing.Optional[IIEcsDeploymentHookProps]:
        '''
        :stability: experimental
        '''
        result = self._values.get("ecs_deployment_hook_props")
        return typing.cast(typing.Optional[IIEcsDeploymentHookProps], result)

    @builtins.property
    def efs_volumes(self) -> typing.Optional[typing.List[IIefsVolumes]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("efs_volumes")
        return typing.cast(typing.Optional[typing.List[IIefsVolumes]], result)

    @builtins.property
    def max_task_count(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum number of task.

        :stability: experimental
        '''
        result = self._values.get("max_task_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_task_count(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The minumun number od tasks.

        :stability: experimental
        '''
        result = self._values.get("min_task_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def scheduled_task_schedule_expression(
        self,
    ) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule]:
        '''
        :stability: experimental
        '''
        result = self._values.get("scheduled_task_schedule_expression")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule], result)

    @builtins.property
    def scheduled_tasks_command(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("scheduled_tasks_command")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secrets(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ecs_ceddda9d.Secret]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("secrets")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ecs_ceddda9d.Secret]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TmApplicationLoadBalancedFargateServiceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TmEcsDeploymentHook(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="tm-cdk-constructs.TmEcsDeploymentHook",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: ITmEcsDeploymentHookProps,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e199dd5d2e264a2fa0e6a8304ff929cd50b23b16f3b48934a93d88d6a26bd6d7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])


class TmElasticacheRedisCluster(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="tm-cdk-constructs.TmElasticacheRedisCluster",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: IRedisClusterProps,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a3a11708e6393483d682acaf674337b7936f6184040624914ace3482b03b7af)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> _aws_cdk_aws_elasticache_ceddda9d.CfnReplicationGroup:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_elasticache_ceddda9d.CfnReplicationGroup, jsii.get(self, "cluster"))

    @builtins.property
    @jsii.member(jsii_name="securityGroup")
    def security_group(self) -> _aws_cdk_aws_ec2_ceddda9d.SecurityGroup:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SecurityGroup, jsii.get(self, "securityGroup"))

    @builtins.property
    @jsii.member(jsii_name="subnetGroup")
    def subnet_group(self) -> _aws_cdk_aws_elasticache_ceddda9d.CfnSubnetGroup:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_elasticache_ceddda9d.CfnSubnetGroup, jsii.get(self, "subnetGroup"))

    @builtins.property
    @jsii.member(jsii_name="parameterGroup")
    def parameter_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticache_ceddda9d.CfnParameterGroup]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticache_ceddda9d.CfnParameterGroup], jsii.get(self, "parameterGroup"))


class TmPatchManager(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="tm-cdk-constructs.TmPatchManager",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: IPatchManagerProps,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__940308e655d0615a415ab199fc1b92548ab09b9aecad8931705ef7e151d3a4ec)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])


class TmPipeline(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="tm-cdk-constructs.TmPipeline",
):
    '''(experimental) A CDK construct that creates a CodePipeline.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        pipeline_name: builtins.str,
        repo_branch: builtins.str,
        repo_name: builtins.str,
        primary_output_directory: typing.Optional[builtins.str] = None,
        synth_command: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Constructs a new instance of the PipelineCdk class.

        :param scope: The parent construct.
        :param id: The name of the construct.
        :param pipeline_name: (experimental) The name of the pipeline.
        :param repo_branch: (experimental) The branch of the repository to use.
        :param repo_name: (experimental) The name of the repository.
        :param primary_output_directory: (experimental) The primary output directory.
        :param synth_command: (experimental) The command to run in the synth step.

        :default: - No default properties.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a993414424d3e58108b1515d1ae43df55fcea9a5bf26c77d45647cea67364f8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = TmPipelineProps(
            pipeline_name=pipeline_name,
            repo_branch=repo_branch,
            repo_name=repo_name,
            primary_output_directory=primary_output_directory,
            synth_command=synth_command,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="pipeline")
    def pipeline(self) -> _aws_cdk_pipelines_ceddda9d.CodePipeline:
        '''(experimental) The CodePipeline created by the construct.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_pipelines_ceddda9d.CodePipeline, jsii.get(self, "pipeline"))


@jsii.data_type(
    jsii_type="tm-cdk-constructs.TmPipelineProps",
    jsii_struct_bases=[],
    name_mapping={
        "pipeline_name": "pipelineName",
        "repo_branch": "repoBranch",
        "repo_name": "repoName",
        "primary_output_directory": "primaryOutputDirectory",
        "synth_command": "synthCommand",
    },
)
class TmPipelineProps:
    def __init__(
        self,
        *,
        pipeline_name: builtins.str,
        repo_branch: builtins.str,
        repo_name: builtins.str,
        primary_output_directory: typing.Optional[builtins.str] = None,
        synth_command: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param pipeline_name: (experimental) The name of the pipeline.
        :param repo_branch: (experimental) The branch of the repository to use.
        :param repo_name: (experimental) The name of the repository.
        :param primary_output_directory: (experimental) The primary output directory.
        :param synth_command: (experimental) The command to run in the synth step.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c90f448d2c851abcb766597516c1d94417ef3eed41e3bc82a985a84bd6ff2854)
            check_type(argname="argument pipeline_name", value=pipeline_name, expected_type=type_hints["pipeline_name"])
            check_type(argname="argument repo_branch", value=repo_branch, expected_type=type_hints["repo_branch"])
            check_type(argname="argument repo_name", value=repo_name, expected_type=type_hints["repo_name"])
            check_type(argname="argument primary_output_directory", value=primary_output_directory, expected_type=type_hints["primary_output_directory"])
            check_type(argname="argument synth_command", value=synth_command, expected_type=type_hints["synth_command"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "pipeline_name": pipeline_name,
            "repo_branch": repo_branch,
            "repo_name": repo_name,
        }
        if primary_output_directory is not None:
            self._values["primary_output_directory"] = primary_output_directory
        if synth_command is not None:
            self._values["synth_command"] = synth_command

    @builtins.property
    def pipeline_name(self) -> builtins.str:
        '''(experimental) The name of the pipeline.

        :stability: experimental
        '''
        result = self._values.get("pipeline_name")
        assert result is not None, "Required property 'pipeline_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repo_branch(self) -> builtins.str:
        '''(experimental) The branch of the repository to use.

        :stability: experimental
        '''
        result = self._values.get("repo_branch")
        assert result is not None, "Required property 'repo_branch' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repo_name(self) -> builtins.str:
        '''(experimental) The name of the repository.

        :stability: experimental
        '''
        result = self._values.get("repo_name")
        assert result is not None, "Required property 'repo_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def primary_output_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) The primary output directory.

        :stability: experimental
        '''
        result = self._values.get("primary_output_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def synth_command(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The command to run in the synth step.

        :stability: experimental
        '''
        result = self._values.get("synth_command")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TmPipelineProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TmRdsAuroraMysqlServerless(
    _aws_cdk_aws_rds_ceddda9d.DatabaseCluster,
    metaclass=jsii.JSIIMeta,
    jsii_type="tm-cdk-constructs.TmRdsAuroraMysqlServerless",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        enable_global: typing.Optional[builtins.bool] = None,
        engine: _aws_cdk_aws_rds_ceddda9d.IClusterEngine,
        auto_minor_version_upgrade: typing.Optional[builtins.bool] = None,
        backtrack_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        backup: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.BackupProps, typing.Dict[builtins.str, typing.Any]]] = None,
        cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
        cloudwatch_logs_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        cloudwatch_logs_retention_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        cluster_identifier: typing.Optional[builtins.str] = None,
        cluster_scailability_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.ClusterScailabilityType] = None,
        cluster_scalability_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.ClusterScalabilityType] = None,
        copy_tags_to_snapshot: typing.Optional[builtins.bool] = None,
        credentials: typing.Optional[_aws_cdk_aws_rds_ceddda9d.Credentials] = None,
        database_insights_mode: typing.Optional[_aws_cdk_aws_rds_ceddda9d.DatabaseInsightsMode] = None,
        default_database_name: typing.Optional[builtins.str] = None,
        deletion_protection: typing.Optional[builtins.bool] = None,
        domain: typing.Optional[builtins.str] = None,
        domain_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        enable_cluster_level_enhanced_monitoring: typing.Optional[builtins.bool] = None,
        enable_data_api: typing.Optional[builtins.bool] = None,
        enable_local_write_forwarding: typing.Optional[builtins.bool] = None,
        enable_performance_insights: typing.Optional[builtins.bool] = None,
        engine_lifecycle_support: typing.Optional[_aws_cdk_aws_rds_ceddda9d.EngineLifecycleSupport] = None,
        iam_authentication: typing.Optional[builtins.bool] = None,
        instance_identifier_base: typing.Optional[builtins.str] = None,
        instance_props: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.InstanceProps, typing.Dict[builtins.str, typing.Any]]] = None,
        instances: typing.Optional[jsii.Number] = None,
        instance_update_behaviour: typing.Optional[_aws_cdk_aws_rds_ceddda9d.InstanceUpdateBehaviour] = None,
        monitoring_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        monitoring_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        network_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.NetworkType] = None,
        parameter_group: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IParameterGroup] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        performance_insight_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        performance_insight_retention: typing.Optional[_aws_cdk_aws_rds_ceddda9d.PerformanceInsightRetention] = None,
        port: typing.Optional[jsii.Number] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        readers: typing.Optional[typing.Sequence[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        replication_source_identifier: typing.Optional[builtins.str] = None,
        s3_export_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
        s3_export_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        s3_import_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
        s3_import_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        serverless_v2_max_capacity: typing.Optional[jsii.Number] = None,
        serverless_v2_min_capacity: typing.Optional[jsii.Number] = None,
        storage_encrypted: typing.Optional[builtins.bool] = None,
        storage_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        storage_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.DBClusterStorageType] = None,
        subnet_group: typing.Optional[_aws_cdk_aws_rds_ceddda9d.ISubnetGroup] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        writer: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance] = None,
    ) -> None:
        '''(experimental) Represents a class that creates an RDS Aurora MySQL Serverless database cluster.

        :param scope: -
        :param id: -
        :param enable_global: (experimental) Enable the creation of a Global Cluster for the RDS cluster.
        :param engine: What kind of database to start.
        :param auto_minor_version_upgrade: Specifies whether minor engine upgrades are applied automatically to the DB cluster during the maintenance window. Default: true
        :param backtrack_window: The number of seconds to set a cluster's target backtrack window to. This feature is only supported by the Aurora MySQL database engine and cannot be enabled on existing clusters. Default: 0 seconds (no backtrack)
        :param backup: Backup settings. Default: - Backup retention period for automated backups is 1 day. Backup preferred window is set to a 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week.
        :param cloudwatch_logs_exports: The list of log types that need to be enabled for exporting to CloudWatch Logs. Default: - no log exports
        :param cloudwatch_logs_retention: The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``Infinity``. Default: - logs never expire
        :param cloudwatch_logs_retention_role: The IAM role for the Lambda function associated with the custom resource that sets the retention policy. Default: - a new role is created.
        :param cluster_identifier: An optional identifier for the cluster. Default: - A name is automatically generated.
        :param cluster_scailability_type: (deprecated) [Misspelled] Specifies the scalability mode of the Aurora DB cluster. Set LIMITLESS if you want to use a limitless database; otherwise, set it to STANDARD. Default: ClusterScailabilityType.STANDARD
        :param cluster_scalability_type: Specifies the scalability mode of the Aurora DB cluster. Set LIMITLESS if you want to use a limitless database; otherwise, set it to STANDARD. Default: ClusterScalabilityType.STANDARD
        :param copy_tags_to_snapshot: Whether to copy tags to the snapshot when a snapshot is created. Default: - true
        :param credentials: Credentials for the administrative user. Default: - A username of 'admin' (or 'postgres' for PostgreSQL) and SecretsManager-generated password
        :param database_insights_mode: The database insights mode. Default: - DatabaseInsightsMode.STANDARD when performance insights are enabled and Amazon Aurora engine is used, otherwise not set.
        :param default_database_name: Name of a database which is automatically created inside the cluster. Default: - Database is not created in cluster.
        :param deletion_protection: Indicates whether the DB cluster should have deletion protection enabled. Default: - true if ``removalPolicy`` is RETAIN, ``undefined`` otherwise, which will not enable deletion protection. To disable deletion protection after it has been enabled, you must explicitly set this value to ``false``.
        :param domain: Directory ID for associating the DB cluster with a specific Active Directory. Necessary for enabling Kerberos authentication. If specified, the DB cluster joins the given Active Directory, enabling Kerberos authentication. If not specified, the DB cluster will not be associated with any Active Directory, and Kerberos authentication will not be enabled. Default: - DB cluster is not associated with an Active Directory; Kerberos authentication is not enabled.
        :param domain_role: The IAM role to be used when making API calls to the Directory Service. The role needs the AWS-managed policy ``AmazonRDSDirectoryServiceAccess`` or equivalent. Default: - If ``DatabaseClusterBaseProps.domain`` is specified, a role with the ``AmazonRDSDirectoryServiceAccess`` policy is automatically created.
        :param enable_cluster_level_enhanced_monitoring: Whether to enable enhanced monitoring at the cluster level. If set to true, ``monitoringInterval`` and ``monitoringRole`` are applied to not the instances, but the cluster. ``monitoringInterval`` is required to be set if ``enableClusterLevelEnhancedMonitoring`` is set to true. Default: - When the ``monitoringInterval`` is set, enhanced monitoring is enabled for each instance.
        :param enable_data_api: Whether to enable the Data API for the cluster. Default: - false
        :param enable_local_write_forwarding: Whether read replicas can forward write operations to the writer DB instance in the DB cluster. This setting can only be enabled for Aurora MySQL 3.04 or higher, and for Aurora PostgreSQL 16.4 or higher (for version 16), 15.8 or higher (for version 15), and 14.13 or higher (for version 14). Default: false
        :param enable_performance_insights: Whether to enable Performance Insights for the DB cluster. Default: - false, unless ``performanceInsightRetention`` or ``performanceInsightEncryptionKey`` is set, or ``databaseInsightsMode`` is set to ``DatabaseInsightsMode.ADVANCED``.
        :param engine_lifecycle_support: The life cycle type for this DB cluster. Default: undefined - AWS RDS default setting is ``EngineLifecycleSupport.OPEN_SOURCE_RDS_EXTENDED_SUPPORT``
        :param iam_authentication: Whether to enable mapping of AWS Identity and Access Management (IAM) accounts to database accounts. Default: false
        :param instance_identifier_base: Base identifier for instances. Every replica is named by appending the replica number to this string, 1-based. Default: - clusterIdentifier is used with the word "Instance" appended. If clusterIdentifier is not provided, the identifier is automatically generated.
        :param instance_props: (deprecated) Settings for the individual instances that are launched.
        :param instances: (deprecated) How many replicas/instances to create. Has to be at least 1. Default: 2
        :param instance_update_behaviour: The ordering of updates for instances. Default: InstanceUpdateBehaviour.BULK
        :param monitoring_interval: The interval between points when Amazon RDS collects enhanced monitoring metrics. If you enable ``enableClusterLevelEnhancedMonitoring``, this property is applied to the cluster, otherwise it is applied to the instances. Default: - no enhanced monitoring
        :param monitoring_role: Role that will be used to manage DB monitoring. If you enable ``enableClusterLevelEnhancedMonitoring``, this property is applied to the cluster, otherwise it is applied to the instances. Default: - A role is automatically created for you
        :param network_type: The network type of the DB instance. Default: - IPV4
        :param parameter_group: Additional parameters to pass to the database engine. Default: - No parameter group.
        :param parameters: The parameters in the DBClusterParameterGroup to create automatically. You can only specify parameterGroup or parameters but not both. You need to use a versioned engine to auto-generate a DBClusterParameterGroup. Default: - None
        :param performance_insight_encryption_key: The AWS KMS key for encryption of Performance Insights data. Default: - default master key
        :param performance_insight_retention: The amount of time, in days, to retain Performance Insights data. If you set ``databaseInsightsMode`` to ``DatabaseInsightsMode.ADVANCED``, you must set this property to ``PerformanceInsightRetention.MONTHS_15``. Default: - 7
        :param port: What port to listen on. Default: - The default for the engine is used.
        :param preferred_maintenance_window: A preferred maintenance window day/time range. Should be specified as a range ddd:hh24:mi-ddd:hh24:mi (24H Clock UTC). Example: 'Sun:23:45-Mon:00:15' Default: - 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week.
        :param readers: A list of instances to create as cluster reader instances. Default: - no readers are created. The cluster will have a single writer/reader
        :param removal_policy: The removal policy to apply when the cluster and its instances are removed from the stack or replaced during an update. Default: - RemovalPolicy.SNAPSHOT (remove the cluster and instances, but retain a snapshot of the data)
        :param replication_source_identifier: The Amazon Resource Name (ARN) of the source DB instance or DB cluster if this DB cluster is created as a read replica. Cannot be used with credentials. Default: - This DB Cluster is not a read replica
        :param s3_export_buckets: S3 buckets that you want to load data into. This feature is only supported by the Aurora database engine. This property must not be used if ``s3ExportRole`` is used. For MySQL: Default: - None
        :param s3_export_role: Role that will be associated with this DB cluster to enable S3 export. This feature is only supported by the Aurora database engine. This property must not be used if ``s3ExportBuckets`` is used. To use this property with Aurora PostgreSQL, it must be configured with the S3 export feature enabled when creating the DatabaseClusterEngine For MySQL: Default: - New role is created if ``s3ExportBuckets`` is set, no role is defined otherwise
        :param s3_import_buckets: S3 buckets that you want to load data from. This feature is only supported by the Aurora database engine. This property must not be used if ``s3ImportRole`` is used. For MySQL: Default: - None
        :param s3_import_role: Role that will be associated with this DB cluster to enable S3 import. This feature is only supported by the Aurora database engine. This property must not be used if ``s3ImportBuckets`` is used. To use this property with Aurora PostgreSQL, it must be configured with the S3 import feature enabled when creating the DatabaseClusterEngine For MySQL: Default: - New role is created if ``s3ImportBuckets`` is set, no role is defined otherwise
        :param security_groups: Security group. Default: - a new security group is created.
        :param serverless_v2_max_capacity: The maximum number of Aurora capacity units (ACUs) for a DB instance in an Aurora Serverless v2 cluster. You can specify ACU values in half-step increments, such as 40, 40.5, 41, and so on. The largest value that you can use is 256. The maximum capacity must be higher than 0.5 ACUs. Default: 2
        :param serverless_v2_min_capacity: The minimum number of Aurora capacity units (ACUs) for a DB instance in an Aurora Serverless v2 cluster. You can specify ACU values in half-step increments, such as 8, 8.5, 9, and so on. The smallest value that you can use is 0. For Aurora versions that support the Aurora Serverless v2 auto-pause feature, the smallest value that you can use is 0. For versions that don't support Aurora Serverless v2 auto-pause, the smallest value that you can use is 0.5. Default: 0.5
        :param storage_encrypted: Whether to enable storage encryption. Default: - true if storageEncryptionKey is provided, false otherwise
        :param storage_encryption_key: The KMS key for storage encryption. If specified, ``storageEncrypted`` will be set to ``true``. Default: - if storageEncrypted is true then the default master key, no key otherwise
        :param storage_type: The storage type to be associated with the DB cluster. Default: - DBClusterStorageType.AURORA_IOPT1
        :param subnet_group: Existing subnet group for the cluster. Default: - a new subnet group will be created.
        :param vpc: What subnets to run the RDS instances in. Must be at least 2 subnets in two different AZs.
        :param vpc_subnets: Where to place the instances within the VPC. Default: - the Vpc default strategy if not specified.
        :param writer: The instance to use for the cluster writer. Default: - required if instanceProps is not provided

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc939679af82c57cdfc24824fb9ec6ef0580d01390aa5c263b878d67d4912115)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = TmRdsAuroraMysqlServerlessProps(
            enable_global=enable_global,
            engine=engine,
            auto_minor_version_upgrade=auto_minor_version_upgrade,
            backtrack_window=backtrack_window,
            backup=backup,
            cloudwatch_logs_exports=cloudwatch_logs_exports,
            cloudwatch_logs_retention=cloudwatch_logs_retention,
            cloudwatch_logs_retention_role=cloudwatch_logs_retention_role,
            cluster_identifier=cluster_identifier,
            cluster_scailability_type=cluster_scailability_type,
            cluster_scalability_type=cluster_scalability_type,
            copy_tags_to_snapshot=copy_tags_to_snapshot,
            credentials=credentials,
            database_insights_mode=database_insights_mode,
            default_database_name=default_database_name,
            deletion_protection=deletion_protection,
            domain=domain,
            domain_role=domain_role,
            enable_cluster_level_enhanced_monitoring=enable_cluster_level_enhanced_monitoring,
            enable_data_api=enable_data_api,
            enable_local_write_forwarding=enable_local_write_forwarding,
            enable_performance_insights=enable_performance_insights,
            engine_lifecycle_support=engine_lifecycle_support,
            iam_authentication=iam_authentication,
            instance_identifier_base=instance_identifier_base,
            instance_props=instance_props,
            instances=instances,
            instance_update_behaviour=instance_update_behaviour,
            monitoring_interval=monitoring_interval,
            monitoring_role=monitoring_role,
            network_type=network_type,
            parameter_group=parameter_group,
            parameters=parameters,
            performance_insight_encryption_key=performance_insight_encryption_key,
            performance_insight_retention=performance_insight_retention,
            port=port,
            preferred_maintenance_window=preferred_maintenance_window,
            readers=readers,
            removal_policy=removal_policy,
            replication_source_identifier=replication_source_identifier,
            s3_export_buckets=s3_export_buckets,
            s3_export_role=s3_export_role,
            s3_import_buckets=s3_import_buckets,
            s3_import_role=s3_import_role,
            security_groups=security_groups,
            serverless_v2_max_capacity=serverless_v2_max_capacity,
            serverless_v2_min_capacity=serverless_v2_min_capacity,
            storage_encrypted=storage_encrypted,
            storage_encryption_key=storage_encryption_key,
            storage_type=storage_type,
            subnet_group=subnet_group,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            writer=writer,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="tm-cdk-constructs.TmRdsAuroraMysqlServerlessProps",
    jsii_struct_bases=[_aws_cdk_aws_rds_ceddda9d.DatabaseClusterProps],
    name_mapping={
        "engine": "engine",
        "auto_minor_version_upgrade": "autoMinorVersionUpgrade",
        "backtrack_window": "backtrackWindow",
        "backup": "backup",
        "cloudwatch_logs_exports": "cloudwatchLogsExports",
        "cloudwatch_logs_retention": "cloudwatchLogsRetention",
        "cloudwatch_logs_retention_role": "cloudwatchLogsRetentionRole",
        "cluster_identifier": "clusterIdentifier",
        "cluster_scailability_type": "clusterScailabilityType",
        "cluster_scalability_type": "clusterScalabilityType",
        "copy_tags_to_snapshot": "copyTagsToSnapshot",
        "credentials": "credentials",
        "database_insights_mode": "databaseInsightsMode",
        "default_database_name": "defaultDatabaseName",
        "deletion_protection": "deletionProtection",
        "domain": "domain",
        "domain_role": "domainRole",
        "enable_cluster_level_enhanced_monitoring": "enableClusterLevelEnhancedMonitoring",
        "enable_data_api": "enableDataApi",
        "enable_local_write_forwarding": "enableLocalWriteForwarding",
        "enable_performance_insights": "enablePerformanceInsights",
        "engine_lifecycle_support": "engineLifecycleSupport",
        "iam_authentication": "iamAuthentication",
        "instance_identifier_base": "instanceIdentifierBase",
        "instance_props": "instanceProps",
        "instances": "instances",
        "instance_update_behaviour": "instanceUpdateBehaviour",
        "monitoring_interval": "monitoringInterval",
        "monitoring_role": "monitoringRole",
        "network_type": "networkType",
        "parameter_group": "parameterGroup",
        "parameters": "parameters",
        "performance_insight_encryption_key": "performanceInsightEncryptionKey",
        "performance_insight_retention": "performanceInsightRetention",
        "port": "port",
        "preferred_maintenance_window": "preferredMaintenanceWindow",
        "readers": "readers",
        "removal_policy": "removalPolicy",
        "replication_source_identifier": "replicationSourceIdentifier",
        "s3_export_buckets": "s3ExportBuckets",
        "s3_export_role": "s3ExportRole",
        "s3_import_buckets": "s3ImportBuckets",
        "s3_import_role": "s3ImportRole",
        "security_groups": "securityGroups",
        "serverless_v2_max_capacity": "serverlessV2MaxCapacity",
        "serverless_v2_min_capacity": "serverlessV2MinCapacity",
        "storage_encrypted": "storageEncrypted",
        "storage_encryption_key": "storageEncryptionKey",
        "storage_type": "storageType",
        "subnet_group": "subnetGroup",
        "vpc": "vpc",
        "vpc_subnets": "vpcSubnets",
        "writer": "writer",
        "enable_global": "enableGlobal",
    },
)
class TmRdsAuroraMysqlServerlessProps(_aws_cdk_aws_rds_ceddda9d.DatabaseClusterProps):
    def __init__(
        self,
        *,
        engine: _aws_cdk_aws_rds_ceddda9d.IClusterEngine,
        auto_minor_version_upgrade: typing.Optional[builtins.bool] = None,
        backtrack_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        backup: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.BackupProps, typing.Dict[builtins.str, typing.Any]]] = None,
        cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
        cloudwatch_logs_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        cloudwatch_logs_retention_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        cluster_identifier: typing.Optional[builtins.str] = None,
        cluster_scailability_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.ClusterScailabilityType] = None,
        cluster_scalability_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.ClusterScalabilityType] = None,
        copy_tags_to_snapshot: typing.Optional[builtins.bool] = None,
        credentials: typing.Optional[_aws_cdk_aws_rds_ceddda9d.Credentials] = None,
        database_insights_mode: typing.Optional[_aws_cdk_aws_rds_ceddda9d.DatabaseInsightsMode] = None,
        default_database_name: typing.Optional[builtins.str] = None,
        deletion_protection: typing.Optional[builtins.bool] = None,
        domain: typing.Optional[builtins.str] = None,
        domain_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        enable_cluster_level_enhanced_monitoring: typing.Optional[builtins.bool] = None,
        enable_data_api: typing.Optional[builtins.bool] = None,
        enable_local_write_forwarding: typing.Optional[builtins.bool] = None,
        enable_performance_insights: typing.Optional[builtins.bool] = None,
        engine_lifecycle_support: typing.Optional[_aws_cdk_aws_rds_ceddda9d.EngineLifecycleSupport] = None,
        iam_authentication: typing.Optional[builtins.bool] = None,
        instance_identifier_base: typing.Optional[builtins.str] = None,
        instance_props: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.InstanceProps, typing.Dict[builtins.str, typing.Any]]] = None,
        instances: typing.Optional[jsii.Number] = None,
        instance_update_behaviour: typing.Optional[_aws_cdk_aws_rds_ceddda9d.InstanceUpdateBehaviour] = None,
        monitoring_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        monitoring_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        network_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.NetworkType] = None,
        parameter_group: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IParameterGroup] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        performance_insight_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        performance_insight_retention: typing.Optional[_aws_cdk_aws_rds_ceddda9d.PerformanceInsightRetention] = None,
        port: typing.Optional[jsii.Number] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        readers: typing.Optional[typing.Sequence[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        replication_source_identifier: typing.Optional[builtins.str] = None,
        s3_export_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
        s3_export_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        s3_import_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
        s3_import_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        serverless_v2_max_capacity: typing.Optional[jsii.Number] = None,
        serverless_v2_min_capacity: typing.Optional[jsii.Number] = None,
        storage_encrypted: typing.Optional[builtins.bool] = None,
        storage_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        storage_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.DBClusterStorageType] = None,
        subnet_group: typing.Optional[_aws_cdk_aws_rds_ceddda9d.ISubnetGroup] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        writer: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance] = None,
        enable_global: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param engine: What kind of database to start.
        :param auto_minor_version_upgrade: Specifies whether minor engine upgrades are applied automatically to the DB cluster during the maintenance window. Default: true
        :param backtrack_window: The number of seconds to set a cluster's target backtrack window to. This feature is only supported by the Aurora MySQL database engine and cannot be enabled on existing clusters. Default: 0 seconds (no backtrack)
        :param backup: Backup settings. Default: - Backup retention period for automated backups is 1 day. Backup preferred window is set to a 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week.
        :param cloudwatch_logs_exports: The list of log types that need to be enabled for exporting to CloudWatch Logs. Default: - no log exports
        :param cloudwatch_logs_retention: The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``Infinity``. Default: - logs never expire
        :param cloudwatch_logs_retention_role: The IAM role for the Lambda function associated with the custom resource that sets the retention policy. Default: - a new role is created.
        :param cluster_identifier: An optional identifier for the cluster. Default: - A name is automatically generated.
        :param cluster_scailability_type: (deprecated) [Misspelled] Specifies the scalability mode of the Aurora DB cluster. Set LIMITLESS if you want to use a limitless database; otherwise, set it to STANDARD. Default: ClusterScailabilityType.STANDARD
        :param cluster_scalability_type: Specifies the scalability mode of the Aurora DB cluster. Set LIMITLESS if you want to use a limitless database; otherwise, set it to STANDARD. Default: ClusterScalabilityType.STANDARD
        :param copy_tags_to_snapshot: Whether to copy tags to the snapshot when a snapshot is created. Default: - true
        :param credentials: Credentials for the administrative user. Default: - A username of 'admin' (or 'postgres' for PostgreSQL) and SecretsManager-generated password
        :param database_insights_mode: The database insights mode. Default: - DatabaseInsightsMode.STANDARD when performance insights are enabled and Amazon Aurora engine is used, otherwise not set.
        :param default_database_name: Name of a database which is automatically created inside the cluster. Default: - Database is not created in cluster.
        :param deletion_protection: Indicates whether the DB cluster should have deletion protection enabled. Default: - true if ``removalPolicy`` is RETAIN, ``undefined`` otherwise, which will not enable deletion protection. To disable deletion protection after it has been enabled, you must explicitly set this value to ``false``.
        :param domain: Directory ID for associating the DB cluster with a specific Active Directory. Necessary for enabling Kerberos authentication. If specified, the DB cluster joins the given Active Directory, enabling Kerberos authentication. If not specified, the DB cluster will not be associated with any Active Directory, and Kerberos authentication will not be enabled. Default: - DB cluster is not associated with an Active Directory; Kerberos authentication is not enabled.
        :param domain_role: The IAM role to be used when making API calls to the Directory Service. The role needs the AWS-managed policy ``AmazonRDSDirectoryServiceAccess`` or equivalent. Default: - If ``DatabaseClusterBaseProps.domain`` is specified, a role with the ``AmazonRDSDirectoryServiceAccess`` policy is automatically created.
        :param enable_cluster_level_enhanced_monitoring: Whether to enable enhanced monitoring at the cluster level. If set to true, ``monitoringInterval`` and ``monitoringRole`` are applied to not the instances, but the cluster. ``monitoringInterval`` is required to be set if ``enableClusterLevelEnhancedMonitoring`` is set to true. Default: - When the ``monitoringInterval`` is set, enhanced monitoring is enabled for each instance.
        :param enable_data_api: Whether to enable the Data API for the cluster. Default: - false
        :param enable_local_write_forwarding: Whether read replicas can forward write operations to the writer DB instance in the DB cluster. This setting can only be enabled for Aurora MySQL 3.04 or higher, and for Aurora PostgreSQL 16.4 or higher (for version 16), 15.8 or higher (for version 15), and 14.13 or higher (for version 14). Default: false
        :param enable_performance_insights: Whether to enable Performance Insights for the DB cluster. Default: - false, unless ``performanceInsightRetention`` or ``performanceInsightEncryptionKey`` is set, or ``databaseInsightsMode`` is set to ``DatabaseInsightsMode.ADVANCED``.
        :param engine_lifecycle_support: The life cycle type for this DB cluster. Default: undefined - AWS RDS default setting is ``EngineLifecycleSupport.OPEN_SOURCE_RDS_EXTENDED_SUPPORT``
        :param iam_authentication: Whether to enable mapping of AWS Identity and Access Management (IAM) accounts to database accounts. Default: false
        :param instance_identifier_base: Base identifier for instances. Every replica is named by appending the replica number to this string, 1-based. Default: - clusterIdentifier is used with the word "Instance" appended. If clusterIdentifier is not provided, the identifier is automatically generated.
        :param instance_props: (deprecated) Settings for the individual instances that are launched.
        :param instances: (deprecated) How many replicas/instances to create. Has to be at least 1. Default: 2
        :param instance_update_behaviour: The ordering of updates for instances. Default: InstanceUpdateBehaviour.BULK
        :param monitoring_interval: The interval between points when Amazon RDS collects enhanced monitoring metrics. If you enable ``enableClusterLevelEnhancedMonitoring``, this property is applied to the cluster, otherwise it is applied to the instances. Default: - no enhanced monitoring
        :param monitoring_role: Role that will be used to manage DB monitoring. If you enable ``enableClusterLevelEnhancedMonitoring``, this property is applied to the cluster, otherwise it is applied to the instances. Default: - A role is automatically created for you
        :param network_type: The network type of the DB instance. Default: - IPV4
        :param parameter_group: Additional parameters to pass to the database engine. Default: - No parameter group.
        :param parameters: The parameters in the DBClusterParameterGroup to create automatically. You can only specify parameterGroup or parameters but not both. You need to use a versioned engine to auto-generate a DBClusterParameterGroup. Default: - None
        :param performance_insight_encryption_key: The AWS KMS key for encryption of Performance Insights data. Default: - default master key
        :param performance_insight_retention: The amount of time, in days, to retain Performance Insights data. If you set ``databaseInsightsMode`` to ``DatabaseInsightsMode.ADVANCED``, you must set this property to ``PerformanceInsightRetention.MONTHS_15``. Default: - 7
        :param port: What port to listen on. Default: - The default for the engine is used.
        :param preferred_maintenance_window: A preferred maintenance window day/time range. Should be specified as a range ddd:hh24:mi-ddd:hh24:mi (24H Clock UTC). Example: 'Sun:23:45-Mon:00:15' Default: - 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week.
        :param readers: A list of instances to create as cluster reader instances. Default: - no readers are created. The cluster will have a single writer/reader
        :param removal_policy: The removal policy to apply when the cluster and its instances are removed from the stack or replaced during an update. Default: - RemovalPolicy.SNAPSHOT (remove the cluster and instances, but retain a snapshot of the data)
        :param replication_source_identifier: The Amazon Resource Name (ARN) of the source DB instance or DB cluster if this DB cluster is created as a read replica. Cannot be used with credentials. Default: - This DB Cluster is not a read replica
        :param s3_export_buckets: S3 buckets that you want to load data into. This feature is only supported by the Aurora database engine. This property must not be used if ``s3ExportRole`` is used. For MySQL: Default: - None
        :param s3_export_role: Role that will be associated with this DB cluster to enable S3 export. This feature is only supported by the Aurora database engine. This property must not be used if ``s3ExportBuckets`` is used. To use this property with Aurora PostgreSQL, it must be configured with the S3 export feature enabled when creating the DatabaseClusterEngine For MySQL: Default: - New role is created if ``s3ExportBuckets`` is set, no role is defined otherwise
        :param s3_import_buckets: S3 buckets that you want to load data from. This feature is only supported by the Aurora database engine. This property must not be used if ``s3ImportRole`` is used. For MySQL: Default: - None
        :param s3_import_role: Role that will be associated with this DB cluster to enable S3 import. This feature is only supported by the Aurora database engine. This property must not be used if ``s3ImportBuckets`` is used. To use this property with Aurora PostgreSQL, it must be configured with the S3 import feature enabled when creating the DatabaseClusterEngine For MySQL: Default: - New role is created if ``s3ImportBuckets`` is set, no role is defined otherwise
        :param security_groups: Security group. Default: - a new security group is created.
        :param serverless_v2_max_capacity: The maximum number of Aurora capacity units (ACUs) for a DB instance in an Aurora Serverless v2 cluster. You can specify ACU values in half-step increments, such as 40, 40.5, 41, and so on. The largest value that you can use is 256. The maximum capacity must be higher than 0.5 ACUs. Default: 2
        :param serverless_v2_min_capacity: The minimum number of Aurora capacity units (ACUs) for a DB instance in an Aurora Serverless v2 cluster. You can specify ACU values in half-step increments, such as 8, 8.5, 9, and so on. The smallest value that you can use is 0. For Aurora versions that support the Aurora Serverless v2 auto-pause feature, the smallest value that you can use is 0. For versions that don't support Aurora Serverless v2 auto-pause, the smallest value that you can use is 0.5. Default: 0.5
        :param storage_encrypted: Whether to enable storage encryption. Default: - true if storageEncryptionKey is provided, false otherwise
        :param storage_encryption_key: The KMS key for storage encryption. If specified, ``storageEncrypted`` will be set to ``true``. Default: - if storageEncrypted is true then the default master key, no key otherwise
        :param storage_type: The storage type to be associated with the DB cluster. Default: - DBClusterStorageType.AURORA_IOPT1
        :param subnet_group: Existing subnet group for the cluster. Default: - a new subnet group will be created.
        :param vpc: What subnets to run the RDS instances in. Must be at least 2 subnets in two different AZs.
        :param vpc_subnets: Where to place the instances within the VPC. Default: - the Vpc default strategy if not specified.
        :param writer: The instance to use for the cluster writer. Default: - required if instanceProps is not provided
        :param enable_global: (experimental) Enable the creation of a Global Cluster for the RDS cluster.

        :stability: experimental
        '''
        if isinstance(backup, dict):
            backup = _aws_cdk_aws_rds_ceddda9d.BackupProps(**backup)
        if isinstance(instance_props, dict):
            instance_props = _aws_cdk_aws_rds_ceddda9d.InstanceProps(**instance_props)
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2eb6185862d0dbafb21639371b5cfdd31758e49cf957284e1d423cbd3bf7cc8a)
            check_type(argname="argument engine", value=engine, expected_type=type_hints["engine"])
            check_type(argname="argument auto_minor_version_upgrade", value=auto_minor_version_upgrade, expected_type=type_hints["auto_minor_version_upgrade"])
            check_type(argname="argument backtrack_window", value=backtrack_window, expected_type=type_hints["backtrack_window"])
            check_type(argname="argument backup", value=backup, expected_type=type_hints["backup"])
            check_type(argname="argument cloudwatch_logs_exports", value=cloudwatch_logs_exports, expected_type=type_hints["cloudwatch_logs_exports"])
            check_type(argname="argument cloudwatch_logs_retention", value=cloudwatch_logs_retention, expected_type=type_hints["cloudwatch_logs_retention"])
            check_type(argname="argument cloudwatch_logs_retention_role", value=cloudwatch_logs_retention_role, expected_type=type_hints["cloudwatch_logs_retention_role"])
            check_type(argname="argument cluster_identifier", value=cluster_identifier, expected_type=type_hints["cluster_identifier"])
            check_type(argname="argument cluster_scailability_type", value=cluster_scailability_type, expected_type=type_hints["cluster_scailability_type"])
            check_type(argname="argument cluster_scalability_type", value=cluster_scalability_type, expected_type=type_hints["cluster_scalability_type"])
            check_type(argname="argument copy_tags_to_snapshot", value=copy_tags_to_snapshot, expected_type=type_hints["copy_tags_to_snapshot"])
            check_type(argname="argument credentials", value=credentials, expected_type=type_hints["credentials"])
            check_type(argname="argument database_insights_mode", value=database_insights_mode, expected_type=type_hints["database_insights_mode"])
            check_type(argname="argument default_database_name", value=default_database_name, expected_type=type_hints["default_database_name"])
            check_type(argname="argument deletion_protection", value=deletion_protection, expected_type=type_hints["deletion_protection"])
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument domain_role", value=domain_role, expected_type=type_hints["domain_role"])
            check_type(argname="argument enable_cluster_level_enhanced_monitoring", value=enable_cluster_level_enhanced_monitoring, expected_type=type_hints["enable_cluster_level_enhanced_monitoring"])
            check_type(argname="argument enable_data_api", value=enable_data_api, expected_type=type_hints["enable_data_api"])
            check_type(argname="argument enable_local_write_forwarding", value=enable_local_write_forwarding, expected_type=type_hints["enable_local_write_forwarding"])
            check_type(argname="argument enable_performance_insights", value=enable_performance_insights, expected_type=type_hints["enable_performance_insights"])
            check_type(argname="argument engine_lifecycle_support", value=engine_lifecycle_support, expected_type=type_hints["engine_lifecycle_support"])
            check_type(argname="argument iam_authentication", value=iam_authentication, expected_type=type_hints["iam_authentication"])
            check_type(argname="argument instance_identifier_base", value=instance_identifier_base, expected_type=type_hints["instance_identifier_base"])
            check_type(argname="argument instance_props", value=instance_props, expected_type=type_hints["instance_props"])
            check_type(argname="argument instances", value=instances, expected_type=type_hints["instances"])
            check_type(argname="argument instance_update_behaviour", value=instance_update_behaviour, expected_type=type_hints["instance_update_behaviour"])
            check_type(argname="argument monitoring_interval", value=monitoring_interval, expected_type=type_hints["monitoring_interval"])
            check_type(argname="argument monitoring_role", value=monitoring_role, expected_type=type_hints["monitoring_role"])
            check_type(argname="argument network_type", value=network_type, expected_type=type_hints["network_type"])
            check_type(argname="argument parameter_group", value=parameter_group, expected_type=type_hints["parameter_group"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
            check_type(argname="argument performance_insight_encryption_key", value=performance_insight_encryption_key, expected_type=type_hints["performance_insight_encryption_key"])
            check_type(argname="argument performance_insight_retention", value=performance_insight_retention, expected_type=type_hints["performance_insight_retention"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument preferred_maintenance_window", value=preferred_maintenance_window, expected_type=type_hints["preferred_maintenance_window"])
            check_type(argname="argument readers", value=readers, expected_type=type_hints["readers"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument replication_source_identifier", value=replication_source_identifier, expected_type=type_hints["replication_source_identifier"])
            check_type(argname="argument s3_export_buckets", value=s3_export_buckets, expected_type=type_hints["s3_export_buckets"])
            check_type(argname="argument s3_export_role", value=s3_export_role, expected_type=type_hints["s3_export_role"])
            check_type(argname="argument s3_import_buckets", value=s3_import_buckets, expected_type=type_hints["s3_import_buckets"])
            check_type(argname="argument s3_import_role", value=s3_import_role, expected_type=type_hints["s3_import_role"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument serverless_v2_max_capacity", value=serverless_v2_max_capacity, expected_type=type_hints["serverless_v2_max_capacity"])
            check_type(argname="argument serverless_v2_min_capacity", value=serverless_v2_min_capacity, expected_type=type_hints["serverless_v2_min_capacity"])
            check_type(argname="argument storage_encrypted", value=storage_encrypted, expected_type=type_hints["storage_encrypted"])
            check_type(argname="argument storage_encryption_key", value=storage_encryption_key, expected_type=type_hints["storage_encryption_key"])
            check_type(argname="argument storage_type", value=storage_type, expected_type=type_hints["storage_type"])
            check_type(argname="argument subnet_group", value=subnet_group, expected_type=type_hints["subnet_group"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
            check_type(argname="argument writer", value=writer, expected_type=type_hints["writer"])
            check_type(argname="argument enable_global", value=enable_global, expected_type=type_hints["enable_global"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "engine": engine,
        }
        if auto_minor_version_upgrade is not None:
            self._values["auto_minor_version_upgrade"] = auto_minor_version_upgrade
        if backtrack_window is not None:
            self._values["backtrack_window"] = backtrack_window
        if backup is not None:
            self._values["backup"] = backup
        if cloudwatch_logs_exports is not None:
            self._values["cloudwatch_logs_exports"] = cloudwatch_logs_exports
        if cloudwatch_logs_retention is not None:
            self._values["cloudwatch_logs_retention"] = cloudwatch_logs_retention
        if cloudwatch_logs_retention_role is not None:
            self._values["cloudwatch_logs_retention_role"] = cloudwatch_logs_retention_role
        if cluster_identifier is not None:
            self._values["cluster_identifier"] = cluster_identifier
        if cluster_scailability_type is not None:
            self._values["cluster_scailability_type"] = cluster_scailability_type
        if cluster_scalability_type is not None:
            self._values["cluster_scalability_type"] = cluster_scalability_type
        if copy_tags_to_snapshot is not None:
            self._values["copy_tags_to_snapshot"] = copy_tags_to_snapshot
        if credentials is not None:
            self._values["credentials"] = credentials
        if database_insights_mode is not None:
            self._values["database_insights_mode"] = database_insights_mode
        if default_database_name is not None:
            self._values["default_database_name"] = default_database_name
        if deletion_protection is not None:
            self._values["deletion_protection"] = deletion_protection
        if domain is not None:
            self._values["domain"] = domain
        if domain_role is not None:
            self._values["domain_role"] = domain_role
        if enable_cluster_level_enhanced_monitoring is not None:
            self._values["enable_cluster_level_enhanced_monitoring"] = enable_cluster_level_enhanced_monitoring
        if enable_data_api is not None:
            self._values["enable_data_api"] = enable_data_api
        if enable_local_write_forwarding is not None:
            self._values["enable_local_write_forwarding"] = enable_local_write_forwarding
        if enable_performance_insights is not None:
            self._values["enable_performance_insights"] = enable_performance_insights
        if engine_lifecycle_support is not None:
            self._values["engine_lifecycle_support"] = engine_lifecycle_support
        if iam_authentication is not None:
            self._values["iam_authentication"] = iam_authentication
        if instance_identifier_base is not None:
            self._values["instance_identifier_base"] = instance_identifier_base
        if instance_props is not None:
            self._values["instance_props"] = instance_props
        if instances is not None:
            self._values["instances"] = instances
        if instance_update_behaviour is not None:
            self._values["instance_update_behaviour"] = instance_update_behaviour
        if monitoring_interval is not None:
            self._values["monitoring_interval"] = monitoring_interval
        if monitoring_role is not None:
            self._values["monitoring_role"] = monitoring_role
        if network_type is not None:
            self._values["network_type"] = network_type
        if parameter_group is not None:
            self._values["parameter_group"] = parameter_group
        if parameters is not None:
            self._values["parameters"] = parameters
        if performance_insight_encryption_key is not None:
            self._values["performance_insight_encryption_key"] = performance_insight_encryption_key
        if performance_insight_retention is not None:
            self._values["performance_insight_retention"] = performance_insight_retention
        if port is not None:
            self._values["port"] = port
        if preferred_maintenance_window is not None:
            self._values["preferred_maintenance_window"] = preferred_maintenance_window
        if readers is not None:
            self._values["readers"] = readers
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if replication_source_identifier is not None:
            self._values["replication_source_identifier"] = replication_source_identifier
        if s3_export_buckets is not None:
            self._values["s3_export_buckets"] = s3_export_buckets
        if s3_export_role is not None:
            self._values["s3_export_role"] = s3_export_role
        if s3_import_buckets is not None:
            self._values["s3_import_buckets"] = s3_import_buckets
        if s3_import_role is not None:
            self._values["s3_import_role"] = s3_import_role
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if serverless_v2_max_capacity is not None:
            self._values["serverless_v2_max_capacity"] = serverless_v2_max_capacity
        if serverless_v2_min_capacity is not None:
            self._values["serverless_v2_min_capacity"] = serverless_v2_min_capacity
        if storage_encrypted is not None:
            self._values["storage_encrypted"] = storage_encrypted
        if storage_encryption_key is not None:
            self._values["storage_encryption_key"] = storage_encryption_key
        if storage_type is not None:
            self._values["storage_type"] = storage_type
        if subnet_group is not None:
            self._values["subnet_group"] = subnet_group
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets
        if writer is not None:
            self._values["writer"] = writer
        if enable_global is not None:
            self._values["enable_global"] = enable_global

    @builtins.property
    def engine(self) -> _aws_cdk_aws_rds_ceddda9d.IClusterEngine:
        '''What kind of database to start.'''
        result = self._values.get("engine")
        assert result is not None, "Required property 'engine' is missing"
        return typing.cast(_aws_cdk_aws_rds_ceddda9d.IClusterEngine, result)

    @builtins.property
    def auto_minor_version_upgrade(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether minor engine upgrades are applied automatically to the DB cluster during the maintenance window.

        :default: true
        '''
        result = self._values.get("auto_minor_version_upgrade")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def backtrack_window(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The number of seconds to set a cluster's target backtrack window to.

        This feature is only supported by the Aurora MySQL database engine and
        cannot be enabled on existing clusters.

        :default: 0 seconds (no backtrack)

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraMySQL.Managing.Backtrack.html
        '''
        result = self._values.get("backtrack_window")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def backup(self) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.BackupProps]:
        '''Backup settings.

        :default:

        - Backup retention period for automated backups is 1 day.
        Backup preferred window is set to a 30-minute window selected at random from an
        8-hour block of time for each AWS Region, occurring on a random day of the week.

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.html#USER_WorkingWithAutomatedBackups.BackupWindow
        '''
        result = self._values.get("backup")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.BackupProps], result)

    @builtins.property
    def cloudwatch_logs_exports(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The list of log types that need to be enabled for exporting to CloudWatch Logs.

        :default: - no log exports
        '''
        result = self._values.get("cloudwatch_logs_exports")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cloudwatch_logs_retention(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
        '''The number of days log events are kept in CloudWatch Logs.

        When updating
        this property, unsetting it doesn't remove the log retention policy. To
        remove the retention policy, set the value to ``Infinity``.

        :default: - logs never expire
        '''
        result = self._values.get("cloudwatch_logs_retention")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

    @builtins.property
    def cloudwatch_logs_retention_role(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM role for the Lambda function associated with the custom resource that sets the retention policy.

        :default: - a new role is created.
        '''
        result = self._values.get("cloudwatch_logs_retention_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def cluster_identifier(self) -> typing.Optional[builtins.str]:
        '''An optional identifier for the cluster.

        :default: - A name is automatically generated.
        '''
        result = self._values.get("cluster_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_scailability_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.ClusterScailabilityType]:
        '''(deprecated) [Misspelled] Specifies the scalability mode of the Aurora DB cluster.

        Set LIMITLESS if you want to use a limitless database; otherwise, set it to STANDARD.

        :default: ClusterScailabilityType.STANDARD

        :deprecated: Use clusterScalabilityType instead. This will be removed in the next major version.

        :stability: deprecated
        '''
        result = self._values.get("cluster_scailability_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.ClusterScailabilityType], result)

    @builtins.property
    def cluster_scalability_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.ClusterScalabilityType]:
        '''Specifies the scalability mode of the Aurora DB cluster.

        Set LIMITLESS if you want to use a limitless database; otherwise, set it to STANDARD.

        :default: ClusterScalabilityType.STANDARD
        '''
        result = self._values.get("cluster_scalability_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.ClusterScalabilityType], result)

    @builtins.property
    def copy_tags_to_snapshot(self) -> typing.Optional[builtins.bool]:
        '''Whether to copy tags to the snapshot when a snapshot is created.

        :default: - true
        '''
        result = self._values.get("copy_tags_to_snapshot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def credentials(self) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.Credentials]:
        '''Credentials for the administrative user.

        :default: - A username of 'admin' (or 'postgres' for PostgreSQL) and SecretsManager-generated password
        '''
        result = self._values.get("credentials")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.Credentials], result)

    @builtins.property
    def database_insights_mode(
        self,
    ) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.DatabaseInsightsMode]:
        '''The database insights mode.

        :default: - DatabaseInsightsMode.STANDARD when performance insights are enabled and Amazon Aurora engine is used, otherwise not set.
        '''
        result = self._values.get("database_insights_mode")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.DatabaseInsightsMode], result)

    @builtins.property
    def default_database_name(self) -> typing.Optional[builtins.str]:
        '''Name of a database which is automatically created inside the cluster.

        :default: - Database is not created in cluster.
        '''
        result = self._values.get("default_database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def deletion_protection(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether the DB cluster should have deletion protection enabled.

        :default:

        - true if ``removalPolicy`` is RETAIN, ``undefined`` otherwise, which will not enable deletion protection.
        To disable deletion protection after it has been enabled, you must explicitly set this value to ``false``.
        '''
        result = self._values.get("deletion_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def domain(self) -> typing.Optional[builtins.str]:
        '''Directory ID for associating the DB cluster with a specific Active Directory.

        Necessary for enabling Kerberos authentication. If specified, the DB cluster joins the given Active Directory, enabling Kerberos authentication.
        If not specified, the DB cluster will not be associated with any Active Directory, and Kerberos authentication will not be enabled.

        :default: - DB cluster is not associated with an Active Directory; Kerberos authentication is not enabled.
        '''
        result = self._values.get("domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM role to be used when making API calls to the Directory Service.

        The role needs the AWS-managed policy
        ``AmazonRDSDirectoryServiceAccess`` or equivalent.

        :default: - If ``DatabaseClusterBaseProps.domain`` is specified, a role with the ``AmazonRDSDirectoryServiceAccess`` policy is automatically created.
        '''
        result = self._values.get("domain_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def enable_cluster_level_enhanced_monitoring(
        self,
    ) -> typing.Optional[builtins.bool]:
        '''Whether to enable enhanced monitoring at the cluster level.

        If set to true, ``monitoringInterval`` and ``monitoringRole`` are applied to not the instances, but the cluster.
        ``monitoringInterval`` is required to be set if ``enableClusterLevelEnhancedMonitoring`` is set to true.

        :default: - When the ``monitoringInterval`` is set, enhanced monitoring is enabled for each instance.
        '''
        result = self._values.get("enable_cluster_level_enhanced_monitoring")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_data_api(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable the Data API for the cluster.

        :default: - false
        '''
        result = self._values.get("enable_data_api")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_local_write_forwarding(self) -> typing.Optional[builtins.bool]:
        '''Whether read replicas can forward write operations to the writer DB instance in the DB cluster.

        This setting can only be enabled for Aurora MySQL 3.04 or higher, and for Aurora PostgreSQL 16.4
        or higher (for version 16), 15.8 or higher (for version 15), and 14.13 or higher (for version 14).

        :default: false

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-postgresql-write-forwarding.html
        '''
        result = self._values.get("enable_local_write_forwarding")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_performance_insights(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable Performance Insights for the DB cluster.

        :default:

        - false, unless ``performanceInsightRetention`` or ``performanceInsightEncryptionKey`` is set,
        or ``databaseInsightsMode`` is set to ``DatabaseInsightsMode.ADVANCED``.
        '''
        result = self._values.get("enable_performance_insights")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def engine_lifecycle_support(
        self,
    ) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.EngineLifecycleSupport]:
        '''The life cycle type for this DB cluster.

        :default: undefined - AWS RDS default setting is ``EngineLifecycleSupport.OPEN_SOURCE_RDS_EXTENDED_SUPPORT``

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/extended-support.html
        '''
        result = self._values.get("engine_lifecycle_support")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.EngineLifecycleSupport], result)

    @builtins.property
    def iam_authentication(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable mapping of AWS Identity and Access Management (IAM) accounts to database accounts.

        :default: false
        '''
        result = self._values.get("iam_authentication")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def instance_identifier_base(self) -> typing.Optional[builtins.str]:
        '''Base identifier for instances.

        Every replica is named by appending the replica number to this string, 1-based.

        :default:

        - clusterIdentifier is used with the word "Instance" appended.
        If clusterIdentifier is not provided, the identifier is automatically generated.
        '''
        result = self._values.get("instance_identifier_base")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.InstanceProps]:
        '''(deprecated) Settings for the individual instances that are launched.

        :deprecated: - use writer and readers instead

        :stability: deprecated
        '''
        result = self._values.get("instance_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.InstanceProps], result)

    @builtins.property
    def instances(self) -> typing.Optional[jsii.Number]:
        '''(deprecated) How many replicas/instances to create.

        Has to be at least 1.

        :default: 2

        :deprecated: - use writer and readers instead

        :stability: deprecated
        '''
        result = self._values.get("instances")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def instance_update_behaviour(
        self,
    ) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.InstanceUpdateBehaviour]:
        '''The ordering of updates for instances.

        :default: InstanceUpdateBehaviour.BULK
        '''
        result = self._values.get("instance_update_behaviour")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.InstanceUpdateBehaviour], result)

    @builtins.property
    def monitoring_interval(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The interval between points when Amazon RDS collects enhanced monitoring metrics.

        If you enable ``enableClusterLevelEnhancedMonitoring``, this property is applied to the cluster,
        otherwise it is applied to the instances.

        :default: - no enhanced monitoring
        '''
        result = self._values.get("monitoring_interval")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def monitoring_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''Role that will be used to manage DB monitoring.

        If you enable ``enableClusterLevelEnhancedMonitoring``, this property is applied to the cluster,
        otherwise it is applied to the instances.

        :default: - A role is automatically created for you
        '''
        result = self._values.get("monitoring_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def network_type(self) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.NetworkType]:
        '''The network type of the DB instance.

        :default: - IPV4
        '''
        result = self._values.get("network_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.NetworkType], result)

    @builtins.property
    def parameter_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.IParameterGroup]:
        '''Additional parameters to pass to the database engine.

        :default: - No parameter group.
        '''
        result = self._values.get("parameter_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.IParameterGroup], result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The parameters in the DBClusterParameterGroup to create automatically.

        You can only specify parameterGroup or parameters but not both.
        You need to use a versioned engine to auto-generate a DBClusterParameterGroup.

        :default: - None
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def performance_insight_encryption_key(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The AWS KMS key for encryption of Performance Insights data.

        :default: - default master key
        '''
        result = self._values.get("performance_insight_encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def performance_insight_retention(
        self,
    ) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.PerformanceInsightRetention]:
        '''The amount of time, in days, to retain Performance Insights data.

        If you set ``databaseInsightsMode`` to ``DatabaseInsightsMode.ADVANCED``, you must set this property to ``PerformanceInsightRetention.MONTHS_15``.

        :default: - 7
        '''
        result = self._values.get("performance_insight_retention")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.PerformanceInsightRetention], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''What port to listen on.

        :default: - The default for the engine is used.
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def preferred_maintenance_window(self) -> typing.Optional[builtins.str]:
        '''A preferred maintenance window day/time range. Should be specified as a range ddd:hh24:mi-ddd:hh24:mi (24H Clock UTC).

        Example: 'Sun:23:45-Mon:00:15'

        :default:

        - 30-minute window selected at random from an 8-hour block of time for
        each AWS Region, occurring on a random day of the week.

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/USER_UpgradeDBInstance.Maintenance.html#Concepts.DBMaintenance
        '''
        result = self._values.get("preferred_maintenance_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def readers(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]]:
        '''A list of instances to create as cluster reader instances.

        :default: - no readers are created. The cluster will have a single writer/reader
        '''
        result = self._values.get("readers")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy to apply when the cluster and its instances are removed from the stack or replaced during an update.

        :default: - RemovalPolicy.SNAPSHOT (remove the cluster and instances, but retain a snapshot of the data)
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def replication_source_identifier(self) -> typing.Optional[builtins.str]:
        '''The Amazon Resource Name (ARN) of the source DB instance or DB cluster if this DB cluster is created as a read replica.

        Cannot be used with credentials.

        :default: - This DB Cluster is not a read replica
        '''
        result = self._values.get("replication_source_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_export_buckets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.IBucket]]:
        '''S3 buckets that you want to load data into. This feature is only supported by the Aurora database engine.

        This property must not be used if ``s3ExportRole`` is used.

        For MySQL:

        :default: - None

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/postgresql-s3-export.html
        '''
        result = self._values.get("s3_export_buckets")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.IBucket]], result)

    @builtins.property
    def s3_export_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''Role that will be associated with this DB cluster to enable S3 export.

        This feature is only supported by the Aurora database engine.

        This property must not be used if ``s3ExportBuckets`` is used.
        To use this property with Aurora PostgreSQL, it must be configured with the S3 export feature enabled when creating the DatabaseClusterEngine
        For MySQL:

        :default: - New role is created if ``s3ExportBuckets`` is set, no role is defined otherwise

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/postgresql-s3-export.html
        '''
        result = self._values.get("s3_export_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def s3_import_buckets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.IBucket]]:
        '''S3 buckets that you want to load data from. This feature is only supported by the Aurora database engine.

        This property must not be used if ``s3ImportRole`` is used.

        For MySQL:

        :default: - None

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraPostgreSQL.Migrating.html
        '''
        result = self._values.get("s3_import_buckets")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.IBucket]], result)

    @builtins.property
    def s3_import_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''Role that will be associated with this DB cluster to enable S3 import.

        This feature is only supported by the Aurora database engine.

        This property must not be used if ``s3ImportBuckets`` is used.
        To use this property with Aurora PostgreSQL, it must be configured with the S3 import feature enabled when creating the DatabaseClusterEngine
        For MySQL:

        :default: - New role is created if ``s3ImportBuckets`` is set, no role is defined otherwise

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraPostgreSQL.Migrating.html
        '''
        result = self._values.get("s3_import_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''Security group.

        :default: - a new security group is created.
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def serverless_v2_max_capacity(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of Aurora capacity units (ACUs) for a DB instance in an Aurora Serverless v2 cluster.

        You can specify ACU values in half-step increments, such as 40, 40.5, 41, and so on.
        The largest value that you can use is 256.

        The maximum capacity must be higher than 0.5 ACUs.

        :default: 2

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.setting-capacity.html#aurora-serverless-v2.max_capacity_considerations
        '''
        result = self._values.get("serverless_v2_max_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def serverless_v2_min_capacity(self) -> typing.Optional[jsii.Number]:
        '''The minimum number of Aurora capacity units (ACUs) for a DB instance in an Aurora Serverless v2 cluster.

        You can specify ACU values in half-step increments, such as 8, 8.5, 9, and so on.
        The smallest value that you can use is 0.

        For Aurora versions that support the Aurora Serverless v2 auto-pause feature, the smallest value that you can use is 0.
        For versions that don't support Aurora Serverless v2 auto-pause, the smallest value that you can use is 0.5.

        :default: 0.5

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.setting-capacity.html#aurora-serverless-v2.min_capacity_considerations
        '''
        result = self._values.get("serverless_v2_min_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def storage_encrypted(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable storage encryption.

        :default: - true if storageEncryptionKey is provided, false otherwise
        '''
        result = self._values.get("storage_encrypted")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def storage_encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The KMS key for storage encryption.

        If specified, ``storageEncrypted`` will be set to ``true``.

        :default: - if storageEncrypted is true then the default master key, no key otherwise
        '''
        result = self._values.get("storage_encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def storage_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.DBClusterStorageType]:
        '''The storage type to be associated with the DB cluster.

        :default: - DBClusterStorageType.AURORA_IOPT1
        '''
        result = self._values.get("storage_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.DBClusterStorageType], result)

    @builtins.property
    def subnet_group(self) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.ISubnetGroup]:
        '''Existing subnet group for the cluster.

        :default: - a new subnet group will be created.
        '''
        result = self._values.get("subnet_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.ISubnetGroup], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''What subnets to run the RDS instances in.

        Must be at least 2 subnets in two different AZs.
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''Where to place the instances within the VPC.

        :default: - the Vpc default strategy if not specified.
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def writer(self) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]:
        '''The instance to use for the cluster writer.

        :default: - required if instanceProps is not provided
        '''
        result = self._values.get("writer")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance], result)

    @builtins.property
    def enable_global(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable the creation of a Global Cluster for the RDS cluster.

        :stability: experimental
        '''
        result = self._values.get("enable_global")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TmRdsAuroraMysqlServerlessProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TmSolrEc2(
    _aws_cdk_aws_ec2_ceddda9d.Instance,
    metaclass=jsii.JSIIMeta,
    jsii_type="tm-cdk-constructs.TmSolrEc2",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        build_context_path: builtins.str,
        allow_from: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        build_container_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        build_dockerfile: typing.Optional[builtins.str] = None,
        ebs_volume_size: typing.Optional[jsii.Number] = None,
        hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
        record_name: typing.Optional[builtins.str] = None,
        solr_java_mem: typing.Optional[builtins.str] = None,
        solr_opts: typing.Optional[builtins.str] = None,
        solr_typo3_solr_enabled_cores: typing.Optional[builtins.str] = None,
        ssm_path_prefix: typing.Optional[builtins.str] = None,
        instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
        machine_image: _aws_cdk_aws_ec2_ceddda9d.IMachineImage,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        allow_all_ipv6_outbound: typing.Optional[builtins.bool] = None,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        associate_public_ip_address: typing.Optional[builtins.bool] = None,
        availability_zone: typing.Optional[builtins.str] = None,
        block_devices: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.BlockDevice, typing.Dict[builtins.str, typing.Any]]]] = None,
        credit_specification: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CpuCredits] = None,
        detailed_monitoring: typing.Optional[builtins.bool] = None,
        disable_api_termination: typing.Optional[builtins.bool] = None,
        ebs_optimized: typing.Optional[builtins.bool] = None,
        enclave_enabled: typing.Optional[builtins.bool] = None,
        hibernation_enabled: typing.Optional[builtins.bool] = None,
        init: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CloudFormationInit] = None,
        init_options: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.ApplyCloudFormationInitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        instance_initiated_shutdown_behavior: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceInitiatedShutdownBehavior] = None,
        instance_name: typing.Optional[builtins.str] = None,
        instance_profile: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IInstanceProfile] = None,
        ipv6_address_count: typing.Optional[jsii.Number] = None,
        key_name: typing.Optional[builtins.str] = None,
        key_pair: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair] = None,
        placement_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IPlacementGroup] = None,
        private_ip_address: typing.Optional[builtins.str] = None,
        propagate_tags_to_volume_on_creation: typing.Optional[builtins.bool] = None,
        require_imdsv2: typing.Optional[builtins.bool] = None,
        resource_signal_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        source_dest_check: typing.Optional[builtins.bool] = None,
        ssm_session_permissions: typing.Optional[builtins.bool] = None,
        user_data: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.UserData] = None,
        user_data_causes_replacement: typing.Optional[builtins.bool] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param build_context_path: 
        :param allow_from: 
        :param build_container_args: 
        :param build_dockerfile: 
        :param ebs_volume_size: 
        :param hosted_zone: 
        :param record_name: 
        :param solr_java_mem: 
        :param solr_opts: 
        :param solr_typo3_solr_enabled_cores: 
        :param ssm_path_prefix: 
        :param instance_type: Type of instance to launch.
        :param machine_image: AMI to launch.
        :param vpc: VPC to launch the instance in.
        :param allow_all_ipv6_outbound: Whether the instance could initiate IPv6 connections to anywhere by default. This property is only used when you do not provide a security group. Default: false
        :param allow_all_outbound: Whether the instance could initiate connections to anywhere by default. This property is only used when you do not provide a security group. Default: true
        :param associate_public_ip_address: Whether to associate a public IP address to the primary network interface attached to this instance. You cannot specify this property and ``ipv6AddressCount`` at the same time. Default: - public IP address is automatically assigned based on default behavior
        :param availability_zone: In which AZ to place the instance within the VPC. Default: - Random zone.
        :param block_devices: Specifies how block devices are exposed to the instance. You can specify virtual devices and EBS volumes. Each instance that is launched has an associated root device volume, either an Amazon EBS volume or an instance store volume. You can use block device mappings to specify additional EBS volumes or instance store volumes to attach to an instance when it is launched. Default: - Uses the block device mapping of the AMI
        :param credit_specification: Specifying the CPU credit type for burstable EC2 instance types (T2, T3, T3a, etc). The unlimited CPU credit option is not supported for T3 instances with a dedicated host. Default: - T2 instances are standard, while T3, T4g, and T3a instances are unlimited.
        :param detailed_monitoring: Whether "Detailed Monitoring" is enabled for this instance Keep in mind that Detailed Monitoring results in extra charges. Default: - false
        :param disable_api_termination: If true, the instance will not be able to be terminated using the Amazon EC2 console, CLI, or API. To change this attribute after launch, use `ModifyInstanceAttribute <https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_ModifyInstanceAttribute.html>`_. Alternatively, if you set InstanceInitiatedShutdownBehavior to terminate, you can terminate the instance by running the shutdown command from the instance. Default: false
        :param ebs_optimized: Indicates whether the instance is optimized for Amazon EBS I/O. This optimization provides dedicated throughput to Amazon EBS and an optimized configuration stack to provide optimal Amazon EBS I/O performance. This optimization isn't available with all instance types. Additional usage charges apply when using an EBS-optimized instance. Default: false
        :param enclave_enabled: Whether the instance is enabled for AWS Nitro Enclaves. Nitro Enclaves requires a Nitro-based virtualized parent instance with specific Intel/AMD with at least 4 vCPUs or Graviton with at least 2 vCPUs instance types and Linux/Windows host OS, while the enclave itself supports only Linux OS. You can't set both ``enclaveEnabled`` and ``hibernationEnabled`` to true on the same instance. Default: - false
        :param hibernation_enabled: Whether the instance is enabled for hibernation. You can't set both ``enclaveEnabled`` and ``hibernationEnabled`` to true on the same instance. Default: - false
        :param init: Apply the given CloudFormation Init configuration to the instance at startup. Default: - no CloudFormation init
        :param init_options: Use the given options for applying CloudFormation Init. Describes the configsets to use and the timeout to wait Default: - default options
        :param instance_initiated_shutdown_behavior: Indicates whether an instance stops or terminates when you initiate shutdown from the instance (using the operating system command for system shutdown). Default: InstanceInitiatedShutdownBehavior.STOP
        :param instance_name: The name of the instance. Default: - CDK generated name
        :param instance_profile: The instance profile used to pass role information to EC2 instances. Note: You can provide an instanceProfile or a role, but not both. Default: - No instance profile
        :param ipv6_address_count: The number of IPv6 addresses to associate with the primary network interface. Amazon EC2 chooses the IPv6 addresses from the range of your subnet. You cannot specify this property and ``associatePublicIpAddress`` at the same time. Default: - For instances associated with an IPv6 subnet, use 1; otherwise, use 0.
        :param key_name: (deprecated) Name of SSH keypair to grant access to instance. Default: - No SSH access will be possible.
        :param key_pair: The SSH keypair to grant access to the instance. Default: - No SSH access will be possible.
        :param placement_group: The placement group that you want to launch the instance into. Default: - no placement group will be used for this instance.
        :param private_ip_address: Defines a private IP address to associate with an instance. Private IP should be available within the VPC that the instance is build within. Default: - no association
        :param propagate_tags_to_volume_on_creation: Propagate the EC2 instance tags to the EBS volumes. Default: - false
        :param require_imdsv2: Whether IMDSv2 should be required on this instance. Default: - false
        :param resource_signal_timeout: The length of time to wait for the resourceSignalCount. The maximum value is 43200 (12 hours). Default: Duration.minutes(5)
        :param role: An IAM role to associate with the instance profile assigned to this Auto Scaling Group. The role must be assumable by the service principal ``ec2.amazonaws.com``: Note: You can provide an instanceProfile or a role, but not both. Default: - A role will automatically be created, it can be accessed via the ``role`` property
        :param security_group: Security Group to assign to this instance. Default: - create new security group
        :param source_dest_check: Specifies whether to enable an instance launched in a VPC to perform NAT. This controls whether source/destination checking is enabled on the instance. A value of true means that checking is enabled, and false means that checking is disabled. The value must be false for the instance to perform NAT. Default: true
        :param ssm_session_permissions: Add SSM session permissions to the instance role. Setting this to ``true`` adds the necessary permissions to connect to the instance using SSM Session Manager. You can do this from the AWS Console. NOTE: Setting this flag to ``true`` may not be enough by itself. You must also use an AMI that comes with the SSM Agent, or install the SSM Agent yourself. See `Working with SSM Agent <https://docs.aws.amazon.com/systems-manager/latest/userguide/ssm-agent.html>`_ in the SSM Developer Guide. Default: false
        :param user_data: Specific UserData to use. The UserData may still be mutated after creation. Default: - A UserData object appropriate for the MachineImage's Operating System is created.
        :param user_data_causes_replacement: Changes to the UserData force replacement. Depending the EC2 instance type, changing UserData either restarts the instance or replaces the instance. - Instance store-backed instances are replaced. - EBS-backed instances are restarted. By default, restarting does not execute the new UserData so you will need a different mechanism to ensure the instance is restarted. Setting this to ``true`` will make the instance's Logical ID depend on the UserData, which will cause CloudFormation to replace it if the UserData changes. Default: - true if ``initOptions`` is specified, false otherwise.
        :param vpc_subnets: Where to place the instance within the VPC. Default: - Private subnets.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e24b32fefe2274170cb6ddac9573e5872bec73f996a3f47c7b05cae2faa2de3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = TmSorlEc2Props(
            build_context_path=build_context_path,
            allow_from=allow_from,
            build_container_args=build_container_args,
            build_dockerfile=build_dockerfile,
            ebs_volume_size=ebs_volume_size,
            hosted_zone=hosted_zone,
            record_name=record_name,
            solr_java_mem=solr_java_mem,
            solr_opts=solr_opts,
            solr_typo3_solr_enabled_cores=solr_typo3_solr_enabled_cores,
            ssm_path_prefix=ssm_path_prefix,
            instance_type=instance_type,
            machine_image=machine_image,
            vpc=vpc,
            allow_all_ipv6_outbound=allow_all_ipv6_outbound,
            allow_all_outbound=allow_all_outbound,
            associate_public_ip_address=associate_public_ip_address,
            availability_zone=availability_zone,
            block_devices=block_devices,
            credit_specification=credit_specification,
            detailed_monitoring=detailed_monitoring,
            disable_api_termination=disable_api_termination,
            ebs_optimized=ebs_optimized,
            enclave_enabled=enclave_enabled,
            hibernation_enabled=hibernation_enabled,
            init=init,
            init_options=init_options,
            instance_initiated_shutdown_behavior=instance_initiated_shutdown_behavior,
            instance_name=instance_name,
            instance_profile=instance_profile,
            ipv6_address_count=ipv6_address_count,
            key_name=key_name,
            key_pair=key_pair,
            placement_group=placement_group,
            private_ip_address=private_ip_address,
            propagate_tags_to_volume_on_creation=propagate_tags_to_volume_on_creation,
            require_imdsv2=require_imdsv2,
            resource_signal_timeout=resource_signal_timeout,
            role=role,
            security_group=security_group,
            source_dest_check=source_dest_check,
            ssm_session_permissions=ssm_session_permissions,
            user_data=user_data,
            user_data_causes_replacement=user_data_causes_replacement,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="tm-cdk-constructs.TmSorlEc2Props",
    jsii_struct_bases=[_aws_cdk_aws_ec2_ceddda9d.InstanceProps],
    name_mapping={
        "instance_type": "instanceType",
        "machine_image": "machineImage",
        "vpc": "vpc",
        "allow_all_ipv6_outbound": "allowAllIpv6Outbound",
        "allow_all_outbound": "allowAllOutbound",
        "associate_public_ip_address": "associatePublicIpAddress",
        "availability_zone": "availabilityZone",
        "block_devices": "blockDevices",
        "credit_specification": "creditSpecification",
        "detailed_monitoring": "detailedMonitoring",
        "disable_api_termination": "disableApiTermination",
        "ebs_optimized": "ebsOptimized",
        "enclave_enabled": "enclaveEnabled",
        "hibernation_enabled": "hibernationEnabled",
        "init": "init",
        "init_options": "initOptions",
        "instance_initiated_shutdown_behavior": "instanceInitiatedShutdownBehavior",
        "instance_name": "instanceName",
        "instance_profile": "instanceProfile",
        "ipv6_address_count": "ipv6AddressCount",
        "key_name": "keyName",
        "key_pair": "keyPair",
        "placement_group": "placementGroup",
        "private_ip_address": "privateIpAddress",
        "propagate_tags_to_volume_on_creation": "propagateTagsToVolumeOnCreation",
        "require_imdsv2": "requireImdsv2",
        "resource_signal_timeout": "resourceSignalTimeout",
        "role": "role",
        "security_group": "securityGroup",
        "source_dest_check": "sourceDestCheck",
        "ssm_session_permissions": "ssmSessionPermissions",
        "user_data": "userData",
        "user_data_causes_replacement": "userDataCausesReplacement",
        "vpc_subnets": "vpcSubnets",
        "build_context_path": "buildContextPath",
        "allow_from": "allowFrom",
        "build_container_args": "buildContainerArgs",
        "build_dockerfile": "buildDockerfile",
        "ebs_volume_size": "ebsVolumeSize",
        "hosted_zone": "hostedZone",
        "record_name": "recordName",
        "solr_java_mem": "solrJavaMem",
        "solr_opts": "solrOpts",
        "solr_typo3_solr_enabled_cores": "solrTypo3SolrEnabledCores",
        "ssm_path_prefix": "ssmPathPrefix",
    },
)
class TmSorlEc2Props(_aws_cdk_aws_ec2_ceddda9d.InstanceProps):
    def __init__(
        self,
        *,
        instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
        machine_image: _aws_cdk_aws_ec2_ceddda9d.IMachineImage,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        allow_all_ipv6_outbound: typing.Optional[builtins.bool] = None,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        associate_public_ip_address: typing.Optional[builtins.bool] = None,
        availability_zone: typing.Optional[builtins.str] = None,
        block_devices: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.BlockDevice, typing.Dict[builtins.str, typing.Any]]]] = None,
        credit_specification: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CpuCredits] = None,
        detailed_monitoring: typing.Optional[builtins.bool] = None,
        disable_api_termination: typing.Optional[builtins.bool] = None,
        ebs_optimized: typing.Optional[builtins.bool] = None,
        enclave_enabled: typing.Optional[builtins.bool] = None,
        hibernation_enabled: typing.Optional[builtins.bool] = None,
        init: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CloudFormationInit] = None,
        init_options: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.ApplyCloudFormationInitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        instance_initiated_shutdown_behavior: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceInitiatedShutdownBehavior] = None,
        instance_name: typing.Optional[builtins.str] = None,
        instance_profile: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IInstanceProfile] = None,
        ipv6_address_count: typing.Optional[jsii.Number] = None,
        key_name: typing.Optional[builtins.str] = None,
        key_pair: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair] = None,
        placement_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IPlacementGroup] = None,
        private_ip_address: typing.Optional[builtins.str] = None,
        propagate_tags_to_volume_on_creation: typing.Optional[builtins.bool] = None,
        require_imdsv2: typing.Optional[builtins.bool] = None,
        resource_signal_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        source_dest_check: typing.Optional[builtins.bool] = None,
        ssm_session_permissions: typing.Optional[builtins.bool] = None,
        user_data: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.UserData] = None,
        user_data_causes_replacement: typing.Optional[builtins.bool] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        build_context_path: builtins.str,
        allow_from: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        build_container_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        build_dockerfile: typing.Optional[builtins.str] = None,
        ebs_volume_size: typing.Optional[jsii.Number] = None,
        hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
        record_name: typing.Optional[builtins.str] = None,
        solr_java_mem: typing.Optional[builtins.str] = None,
        solr_opts: typing.Optional[builtins.str] = None,
        solr_typo3_solr_enabled_cores: typing.Optional[builtins.str] = None,
        ssm_path_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param instance_type: Type of instance to launch.
        :param machine_image: AMI to launch.
        :param vpc: VPC to launch the instance in.
        :param allow_all_ipv6_outbound: Whether the instance could initiate IPv6 connections to anywhere by default. This property is only used when you do not provide a security group. Default: false
        :param allow_all_outbound: Whether the instance could initiate connections to anywhere by default. This property is only used when you do not provide a security group. Default: true
        :param associate_public_ip_address: Whether to associate a public IP address to the primary network interface attached to this instance. You cannot specify this property and ``ipv6AddressCount`` at the same time. Default: - public IP address is automatically assigned based on default behavior
        :param availability_zone: In which AZ to place the instance within the VPC. Default: - Random zone.
        :param block_devices: Specifies how block devices are exposed to the instance. You can specify virtual devices and EBS volumes. Each instance that is launched has an associated root device volume, either an Amazon EBS volume or an instance store volume. You can use block device mappings to specify additional EBS volumes or instance store volumes to attach to an instance when it is launched. Default: - Uses the block device mapping of the AMI
        :param credit_specification: Specifying the CPU credit type for burstable EC2 instance types (T2, T3, T3a, etc). The unlimited CPU credit option is not supported for T3 instances with a dedicated host. Default: - T2 instances are standard, while T3, T4g, and T3a instances are unlimited.
        :param detailed_monitoring: Whether "Detailed Monitoring" is enabled for this instance Keep in mind that Detailed Monitoring results in extra charges. Default: - false
        :param disable_api_termination: If true, the instance will not be able to be terminated using the Amazon EC2 console, CLI, or API. To change this attribute after launch, use `ModifyInstanceAttribute <https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_ModifyInstanceAttribute.html>`_. Alternatively, if you set InstanceInitiatedShutdownBehavior to terminate, you can terminate the instance by running the shutdown command from the instance. Default: false
        :param ebs_optimized: Indicates whether the instance is optimized for Amazon EBS I/O. This optimization provides dedicated throughput to Amazon EBS and an optimized configuration stack to provide optimal Amazon EBS I/O performance. This optimization isn't available with all instance types. Additional usage charges apply when using an EBS-optimized instance. Default: false
        :param enclave_enabled: Whether the instance is enabled for AWS Nitro Enclaves. Nitro Enclaves requires a Nitro-based virtualized parent instance with specific Intel/AMD with at least 4 vCPUs or Graviton with at least 2 vCPUs instance types and Linux/Windows host OS, while the enclave itself supports only Linux OS. You can't set both ``enclaveEnabled`` and ``hibernationEnabled`` to true on the same instance. Default: - false
        :param hibernation_enabled: Whether the instance is enabled for hibernation. You can't set both ``enclaveEnabled`` and ``hibernationEnabled`` to true on the same instance. Default: - false
        :param init: Apply the given CloudFormation Init configuration to the instance at startup. Default: - no CloudFormation init
        :param init_options: Use the given options for applying CloudFormation Init. Describes the configsets to use and the timeout to wait Default: - default options
        :param instance_initiated_shutdown_behavior: Indicates whether an instance stops or terminates when you initiate shutdown from the instance (using the operating system command for system shutdown). Default: InstanceInitiatedShutdownBehavior.STOP
        :param instance_name: The name of the instance. Default: - CDK generated name
        :param instance_profile: The instance profile used to pass role information to EC2 instances. Note: You can provide an instanceProfile or a role, but not both. Default: - No instance profile
        :param ipv6_address_count: The number of IPv6 addresses to associate with the primary network interface. Amazon EC2 chooses the IPv6 addresses from the range of your subnet. You cannot specify this property and ``associatePublicIpAddress`` at the same time. Default: - For instances associated with an IPv6 subnet, use 1; otherwise, use 0.
        :param key_name: (deprecated) Name of SSH keypair to grant access to instance. Default: - No SSH access will be possible.
        :param key_pair: The SSH keypair to grant access to the instance. Default: - No SSH access will be possible.
        :param placement_group: The placement group that you want to launch the instance into. Default: - no placement group will be used for this instance.
        :param private_ip_address: Defines a private IP address to associate with an instance. Private IP should be available within the VPC that the instance is build within. Default: - no association
        :param propagate_tags_to_volume_on_creation: Propagate the EC2 instance tags to the EBS volumes. Default: - false
        :param require_imdsv2: Whether IMDSv2 should be required on this instance. Default: - false
        :param resource_signal_timeout: The length of time to wait for the resourceSignalCount. The maximum value is 43200 (12 hours). Default: Duration.minutes(5)
        :param role: An IAM role to associate with the instance profile assigned to this Auto Scaling Group. The role must be assumable by the service principal ``ec2.amazonaws.com``: Note: You can provide an instanceProfile or a role, but not both. Default: - A role will automatically be created, it can be accessed via the ``role`` property
        :param security_group: Security Group to assign to this instance. Default: - create new security group
        :param source_dest_check: Specifies whether to enable an instance launched in a VPC to perform NAT. This controls whether source/destination checking is enabled on the instance. A value of true means that checking is enabled, and false means that checking is disabled. The value must be false for the instance to perform NAT. Default: true
        :param ssm_session_permissions: Add SSM session permissions to the instance role. Setting this to ``true`` adds the necessary permissions to connect to the instance using SSM Session Manager. You can do this from the AWS Console. NOTE: Setting this flag to ``true`` may not be enough by itself. You must also use an AMI that comes with the SSM Agent, or install the SSM Agent yourself. See `Working with SSM Agent <https://docs.aws.amazon.com/systems-manager/latest/userguide/ssm-agent.html>`_ in the SSM Developer Guide. Default: false
        :param user_data: Specific UserData to use. The UserData may still be mutated after creation. Default: - A UserData object appropriate for the MachineImage's Operating System is created.
        :param user_data_causes_replacement: Changes to the UserData force replacement. Depending the EC2 instance type, changing UserData either restarts the instance or replaces the instance. - Instance store-backed instances are replaced. - EBS-backed instances are restarted. By default, restarting does not execute the new UserData so you will need a different mechanism to ensure the instance is restarted. Setting this to ``true`` will make the instance's Logical ID depend on the UserData, which will cause CloudFormation to replace it if the UserData changes. Default: - true if ``initOptions`` is specified, false otherwise.
        :param vpc_subnets: Where to place the instance within the VPC. Default: - Private subnets.
        :param build_context_path: 
        :param allow_from: 
        :param build_container_args: 
        :param build_dockerfile: 
        :param ebs_volume_size: 
        :param hosted_zone: 
        :param record_name: 
        :param solr_java_mem: 
        :param solr_opts: 
        :param solr_typo3_solr_enabled_cores: 
        :param ssm_path_prefix: 

        :stability: experimental
        '''
        if isinstance(init_options, dict):
            init_options = _aws_cdk_aws_ec2_ceddda9d.ApplyCloudFormationInitOptions(**init_options)
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7efd22ab41d2580479d98ebbaedfaf8d813ce514136c726e5537193fbc894eb9)
            check_type(argname="argument instance_type", value=instance_type, expected_type=type_hints["instance_type"])
            check_type(argname="argument machine_image", value=machine_image, expected_type=type_hints["machine_image"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument allow_all_ipv6_outbound", value=allow_all_ipv6_outbound, expected_type=type_hints["allow_all_ipv6_outbound"])
            check_type(argname="argument allow_all_outbound", value=allow_all_outbound, expected_type=type_hints["allow_all_outbound"])
            check_type(argname="argument associate_public_ip_address", value=associate_public_ip_address, expected_type=type_hints["associate_public_ip_address"])
            check_type(argname="argument availability_zone", value=availability_zone, expected_type=type_hints["availability_zone"])
            check_type(argname="argument block_devices", value=block_devices, expected_type=type_hints["block_devices"])
            check_type(argname="argument credit_specification", value=credit_specification, expected_type=type_hints["credit_specification"])
            check_type(argname="argument detailed_monitoring", value=detailed_monitoring, expected_type=type_hints["detailed_monitoring"])
            check_type(argname="argument disable_api_termination", value=disable_api_termination, expected_type=type_hints["disable_api_termination"])
            check_type(argname="argument ebs_optimized", value=ebs_optimized, expected_type=type_hints["ebs_optimized"])
            check_type(argname="argument enclave_enabled", value=enclave_enabled, expected_type=type_hints["enclave_enabled"])
            check_type(argname="argument hibernation_enabled", value=hibernation_enabled, expected_type=type_hints["hibernation_enabled"])
            check_type(argname="argument init", value=init, expected_type=type_hints["init"])
            check_type(argname="argument init_options", value=init_options, expected_type=type_hints["init_options"])
            check_type(argname="argument instance_initiated_shutdown_behavior", value=instance_initiated_shutdown_behavior, expected_type=type_hints["instance_initiated_shutdown_behavior"])
            check_type(argname="argument instance_name", value=instance_name, expected_type=type_hints["instance_name"])
            check_type(argname="argument instance_profile", value=instance_profile, expected_type=type_hints["instance_profile"])
            check_type(argname="argument ipv6_address_count", value=ipv6_address_count, expected_type=type_hints["ipv6_address_count"])
            check_type(argname="argument key_name", value=key_name, expected_type=type_hints["key_name"])
            check_type(argname="argument key_pair", value=key_pair, expected_type=type_hints["key_pair"])
            check_type(argname="argument placement_group", value=placement_group, expected_type=type_hints["placement_group"])
            check_type(argname="argument private_ip_address", value=private_ip_address, expected_type=type_hints["private_ip_address"])
            check_type(argname="argument propagate_tags_to_volume_on_creation", value=propagate_tags_to_volume_on_creation, expected_type=type_hints["propagate_tags_to_volume_on_creation"])
            check_type(argname="argument require_imdsv2", value=require_imdsv2, expected_type=type_hints["require_imdsv2"])
            check_type(argname="argument resource_signal_timeout", value=resource_signal_timeout, expected_type=type_hints["resource_signal_timeout"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument source_dest_check", value=source_dest_check, expected_type=type_hints["source_dest_check"])
            check_type(argname="argument ssm_session_permissions", value=ssm_session_permissions, expected_type=type_hints["ssm_session_permissions"])
            check_type(argname="argument user_data", value=user_data, expected_type=type_hints["user_data"])
            check_type(argname="argument user_data_causes_replacement", value=user_data_causes_replacement, expected_type=type_hints["user_data_causes_replacement"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
            check_type(argname="argument build_context_path", value=build_context_path, expected_type=type_hints["build_context_path"])
            check_type(argname="argument allow_from", value=allow_from, expected_type=type_hints["allow_from"])
            check_type(argname="argument build_container_args", value=build_container_args, expected_type=type_hints["build_container_args"])
            check_type(argname="argument build_dockerfile", value=build_dockerfile, expected_type=type_hints["build_dockerfile"])
            check_type(argname="argument ebs_volume_size", value=ebs_volume_size, expected_type=type_hints["ebs_volume_size"])
            check_type(argname="argument hosted_zone", value=hosted_zone, expected_type=type_hints["hosted_zone"])
            check_type(argname="argument record_name", value=record_name, expected_type=type_hints["record_name"])
            check_type(argname="argument solr_java_mem", value=solr_java_mem, expected_type=type_hints["solr_java_mem"])
            check_type(argname="argument solr_opts", value=solr_opts, expected_type=type_hints["solr_opts"])
            check_type(argname="argument solr_typo3_solr_enabled_cores", value=solr_typo3_solr_enabled_cores, expected_type=type_hints["solr_typo3_solr_enabled_cores"])
            check_type(argname="argument ssm_path_prefix", value=ssm_path_prefix, expected_type=type_hints["ssm_path_prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instance_type": instance_type,
            "machine_image": machine_image,
            "vpc": vpc,
            "build_context_path": build_context_path,
        }
        if allow_all_ipv6_outbound is not None:
            self._values["allow_all_ipv6_outbound"] = allow_all_ipv6_outbound
        if allow_all_outbound is not None:
            self._values["allow_all_outbound"] = allow_all_outbound
        if associate_public_ip_address is not None:
            self._values["associate_public_ip_address"] = associate_public_ip_address
        if availability_zone is not None:
            self._values["availability_zone"] = availability_zone
        if block_devices is not None:
            self._values["block_devices"] = block_devices
        if credit_specification is not None:
            self._values["credit_specification"] = credit_specification
        if detailed_monitoring is not None:
            self._values["detailed_monitoring"] = detailed_monitoring
        if disable_api_termination is not None:
            self._values["disable_api_termination"] = disable_api_termination
        if ebs_optimized is not None:
            self._values["ebs_optimized"] = ebs_optimized
        if enclave_enabled is not None:
            self._values["enclave_enabled"] = enclave_enabled
        if hibernation_enabled is not None:
            self._values["hibernation_enabled"] = hibernation_enabled
        if init is not None:
            self._values["init"] = init
        if init_options is not None:
            self._values["init_options"] = init_options
        if instance_initiated_shutdown_behavior is not None:
            self._values["instance_initiated_shutdown_behavior"] = instance_initiated_shutdown_behavior
        if instance_name is not None:
            self._values["instance_name"] = instance_name
        if instance_profile is not None:
            self._values["instance_profile"] = instance_profile
        if ipv6_address_count is not None:
            self._values["ipv6_address_count"] = ipv6_address_count
        if key_name is not None:
            self._values["key_name"] = key_name
        if key_pair is not None:
            self._values["key_pair"] = key_pair
        if placement_group is not None:
            self._values["placement_group"] = placement_group
        if private_ip_address is not None:
            self._values["private_ip_address"] = private_ip_address
        if propagate_tags_to_volume_on_creation is not None:
            self._values["propagate_tags_to_volume_on_creation"] = propagate_tags_to_volume_on_creation
        if require_imdsv2 is not None:
            self._values["require_imdsv2"] = require_imdsv2
        if resource_signal_timeout is not None:
            self._values["resource_signal_timeout"] = resource_signal_timeout
        if role is not None:
            self._values["role"] = role
        if security_group is not None:
            self._values["security_group"] = security_group
        if source_dest_check is not None:
            self._values["source_dest_check"] = source_dest_check
        if ssm_session_permissions is not None:
            self._values["ssm_session_permissions"] = ssm_session_permissions
        if user_data is not None:
            self._values["user_data"] = user_data
        if user_data_causes_replacement is not None:
            self._values["user_data_causes_replacement"] = user_data_causes_replacement
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets
        if allow_from is not None:
            self._values["allow_from"] = allow_from
        if build_container_args is not None:
            self._values["build_container_args"] = build_container_args
        if build_dockerfile is not None:
            self._values["build_dockerfile"] = build_dockerfile
        if ebs_volume_size is not None:
            self._values["ebs_volume_size"] = ebs_volume_size
        if hosted_zone is not None:
            self._values["hosted_zone"] = hosted_zone
        if record_name is not None:
            self._values["record_name"] = record_name
        if solr_java_mem is not None:
            self._values["solr_java_mem"] = solr_java_mem
        if solr_opts is not None:
            self._values["solr_opts"] = solr_opts
        if solr_typo3_solr_enabled_cores is not None:
            self._values["solr_typo3_solr_enabled_cores"] = solr_typo3_solr_enabled_cores
        if ssm_path_prefix is not None:
            self._values["ssm_path_prefix"] = ssm_path_prefix

    @builtins.property
    def instance_type(self) -> _aws_cdk_aws_ec2_ceddda9d.InstanceType:
        '''Type of instance to launch.'''
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.InstanceType, result)

    @builtins.property
    def machine_image(self) -> _aws_cdk_aws_ec2_ceddda9d.IMachineImage:
        '''AMI to launch.'''
        result = self._values.get("machine_image")
        assert result is not None, "Required property 'machine_image' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IMachineImage, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''VPC to launch the instance in.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def allow_all_ipv6_outbound(self) -> typing.Optional[builtins.bool]:
        '''Whether the instance could initiate IPv6 connections to anywhere by default.

        This property is only used when you do not provide a security group.

        :default: false
        '''
        result = self._values.get("allow_all_ipv6_outbound")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def allow_all_outbound(self) -> typing.Optional[builtins.bool]:
        '''Whether the instance could initiate connections to anywhere by default.

        This property is only used when you do not provide a security group.

        :default: true
        '''
        result = self._values.get("allow_all_outbound")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def associate_public_ip_address(self) -> typing.Optional[builtins.bool]:
        '''Whether to associate a public IP address to the primary network interface attached to this instance.

        You cannot specify this property and ``ipv6AddressCount`` at the same time.

        :default: - public IP address is automatically assigned based on default behavior
        '''
        result = self._values.get("associate_public_ip_address")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def availability_zone(self) -> typing.Optional[builtins.str]:
        '''In which AZ to place the instance within the VPC.

        :default: - Random zone.
        '''
        result = self._values.get("availability_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def block_devices(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.BlockDevice]]:
        '''Specifies how block devices are exposed to the instance. You can specify virtual devices and EBS volumes.

        Each instance that is launched has an associated root device volume,
        either an Amazon EBS volume or an instance store volume.
        You can use block device mappings to specify additional EBS volumes or
        instance store volumes to attach to an instance when it is launched.

        :default: - Uses the block device mapping of the AMI

        :see: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/block-device-mapping-concepts.html
        '''
        result = self._values.get("block_devices")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.BlockDevice]], result)

    @builtins.property
    def credit_specification(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CpuCredits]:
        '''Specifying the CPU credit type for burstable EC2 instance types (T2, T3, T3a, etc).

        The unlimited CPU credit option is not supported for T3 instances with a dedicated host.

        :default: - T2 instances are standard, while T3, T4g, and T3a instances are unlimited.
        '''
        result = self._values.get("credit_specification")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CpuCredits], result)

    @builtins.property
    def detailed_monitoring(self) -> typing.Optional[builtins.bool]:
        '''Whether "Detailed Monitoring" is enabled for this instance Keep in mind that Detailed Monitoring results in extra charges.

        :default: - false

        :see: http://aws.amazon.com/cloudwatch/pricing/
        '''
        result = self._values.get("detailed_monitoring")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def disable_api_termination(self) -> typing.Optional[builtins.bool]:
        '''If true, the instance will not be able to be terminated using the Amazon EC2 console, CLI, or API.

        To change this attribute after launch, use `ModifyInstanceAttribute <https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_ModifyInstanceAttribute.html>`_.
        Alternatively, if you set InstanceInitiatedShutdownBehavior to terminate, you can terminate the instance
        by running the shutdown command from the instance.

        :default: false

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-instance.html#cfn-ec2-instance-disableapitermination
        '''
        result = self._values.get("disable_api_termination")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ebs_optimized(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether the instance is optimized for Amazon EBS I/O.

        This optimization provides dedicated throughput to Amazon EBS and an optimized configuration stack to provide optimal Amazon EBS I/O performance.
        This optimization isn't available with all instance types.
        Additional usage charges apply when using an EBS-optimized instance.

        :default: false
        '''
        result = self._values.get("ebs_optimized")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enclave_enabled(self) -> typing.Optional[builtins.bool]:
        '''Whether the instance is enabled for AWS Nitro Enclaves.

        Nitro Enclaves requires a Nitro-based virtualized parent instance with specific Intel/AMD with at least 4 vCPUs
        or Graviton with at least 2 vCPUs instance types and Linux/Windows host OS,
        while the enclave itself supports only Linux OS.

        You can't set both ``enclaveEnabled`` and ``hibernationEnabled`` to true on the same instance.

        :default: - false

        :see: https://docs.aws.amazon.com/enclaves/latest/user/nitro-enclave.html#nitro-enclave-reqs
        '''
        result = self._values.get("enclave_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def hibernation_enabled(self) -> typing.Optional[builtins.bool]:
        '''Whether the instance is enabled for hibernation.

        You can't set both ``enclaveEnabled`` and ``hibernationEnabled`` to true on the same instance.

        :default: - false

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-hibernationoptions.html
        '''
        result = self._values.get("hibernation_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def init(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CloudFormationInit]:
        '''Apply the given CloudFormation Init configuration to the instance at startup.

        :default: - no CloudFormation init
        '''
        result = self._values.get("init")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CloudFormationInit], result)

    @builtins.property
    def init_options(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ApplyCloudFormationInitOptions]:
        '''Use the given options for applying CloudFormation Init.

        Describes the configsets to use and the timeout to wait

        :default: - default options
        '''
        result = self._values.get("init_options")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ApplyCloudFormationInitOptions], result)

    @builtins.property
    def instance_initiated_shutdown_behavior(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceInitiatedShutdownBehavior]:
        '''Indicates whether an instance stops or terminates when you initiate shutdown from the instance (using the operating system command for system shutdown).

        :default: InstanceInitiatedShutdownBehavior.STOP

        :see: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/terminating-instances.html#Using_ChangingInstanceInitiatedShutdownBehavior
        '''
        result = self._values.get("instance_initiated_shutdown_behavior")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceInitiatedShutdownBehavior], result)

    @builtins.property
    def instance_name(self) -> typing.Optional[builtins.str]:
        '''The name of the instance.

        :default: - CDK generated name
        '''
        result = self._values.get("instance_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_profile(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IInstanceProfile]:
        '''The instance profile used to pass role information to EC2 instances.

        Note: You can provide an instanceProfile or a role, but not both.

        :default: - No instance profile
        '''
        result = self._values.get("instance_profile")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IInstanceProfile], result)

    @builtins.property
    def ipv6_address_count(self) -> typing.Optional[jsii.Number]:
        '''The number of IPv6 addresses to associate with the primary network interface.

        Amazon EC2 chooses the IPv6 addresses from the range of your subnet.

        You cannot specify this property and ``associatePublicIpAddress`` at the same time.

        :default: - For instances associated with an IPv6 subnet, use 1; otherwise, use 0.
        '''
        result = self._values.get("ipv6_address_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def key_name(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Name of SSH keypair to grant access to instance.

        :default: - No SSH access will be possible.

        :deprecated: - Use ``keyPair`` instead - https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2-readme.html#using-an-existing-ec2-key-pair

        :stability: deprecated
        '''
        result = self._values.get("key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_pair(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair]:
        '''The SSH keypair to grant access to the instance.

        :default: - No SSH access will be possible.
        '''
        result = self._values.get("key_pair")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair], result)

    @builtins.property
    def placement_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IPlacementGroup]:
        '''The placement group that you want to launch the instance into.

        :default: - no placement group will be used for this instance.
        '''
        result = self._values.get("placement_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IPlacementGroup], result)

    @builtins.property
    def private_ip_address(self) -> typing.Optional[builtins.str]:
        '''Defines a private IP address to associate with an instance.

        Private IP should be available within the VPC that the instance is build within.

        :default: - no association
        '''
        result = self._values.get("private_ip_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def propagate_tags_to_volume_on_creation(self) -> typing.Optional[builtins.bool]:
        '''Propagate the EC2 instance tags to the EBS volumes.

        :default: - false
        '''
        result = self._values.get("propagate_tags_to_volume_on_creation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def require_imdsv2(self) -> typing.Optional[builtins.bool]:
        '''Whether IMDSv2 should be required on this instance.

        :default: - false
        '''
        result = self._values.get("require_imdsv2")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def resource_signal_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The length of time to wait for the resourceSignalCount.

        The maximum value is 43200 (12 hours).

        :default: Duration.minutes(5)
        '''
        result = self._values.get("resource_signal_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''An IAM role to associate with the instance profile assigned to this Auto Scaling Group.

        The role must be assumable by the service principal ``ec2.amazonaws.com``:
        Note: You can provide an instanceProfile or a role, but not both.

        :default: - A role will automatically be created, it can be accessed via the ``role`` property

        Example::

            const role = new iam.Role(this, 'MyRole', {
              assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com')
            });
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''Security Group to assign to this instance.

        :default: - create new security group
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def source_dest_check(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether to enable an instance launched in a VPC to perform NAT.

        This controls whether source/destination checking is enabled on the instance.
        A value of true means that checking is enabled, and false means that checking is disabled.
        The value must be false for the instance to perform NAT.

        :default: true
        '''
        result = self._values.get("source_dest_check")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ssm_session_permissions(self) -> typing.Optional[builtins.bool]:
        '''Add SSM session permissions to the instance role.

        Setting this to ``true`` adds the necessary permissions to connect
        to the instance using SSM Session Manager. You can do this
        from the AWS Console.

        NOTE: Setting this flag to ``true`` may not be enough by itself.
        You must also use an AMI that comes with the SSM Agent, or install
        the SSM Agent yourself. See
        `Working with SSM Agent <https://docs.aws.amazon.com/systems-manager/latest/userguide/ssm-agent.html>`_
        in the SSM Developer Guide.

        :default: false
        '''
        result = self._values.get("ssm_session_permissions")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def user_data(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.UserData]:
        '''Specific UserData to use.

        The UserData may still be mutated after creation.

        :default:

        - A UserData object appropriate for the MachineImage's
        Operating System is created.
        '''
        result = self._values.get("user_data")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.UserData], result)

    @builtins.property
    def user_data_causes_replacement(self) -> typing.Optional[builtins.bool]:
        '''Changes to the UserData force replacement.

        Depending the EC2 instance type, changing UserData either
        restarts the instance or replaces the instance.

        - Instance store-backed instances are replaced.
        - EBS-backed instances are restarted.

        By default, restarting does not execute the new UserData so you
        will need a different mechanism to ensure the instance is restarted.

        Setting this to ``true`` will make the instance's Logical ID depend on the
        UserData, which will cause CloudFormation to replace it if the UserData
        changes.

        :default: - true if ``initOptions`` is specified, false otherwise.
        '''
        result = self._values.get("user_data_causes_replacement")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''Where to place the instance within the VPC.

        :default: - Private subnets.
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def build_context_path(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("build_context_path")
        assert result is not None, "Required property 'build_context_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allow_from(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''
        :stability: experimental
        '''
        result = self._values.get("allow_from")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def build_container_args(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("build_container_args")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def build_dockerfile(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("build_dockerfile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ebs_volume_size(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("ebs_volume_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def hosted_zone(self) -> typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone]:
        '''
        :stability: experimental
        '''
        result = self._values.get("hosted_zone")
        return typing.cast(typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone], result)

    @builtins.property
    def record_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("record_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def solr_java_mem(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("solr_java_mem")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def solr_opts(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("solr_opts")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def solr_typo3_solr_enabled_cores(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("solr_typo3_solr_enabled_cores")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssm_path_prefix(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("ssm_path_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TmSorlEc2Props(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TmVpcBase(
    _aws_cdk_aws_ec2_ceddda9d.Vpc,
    metaclass=jsii.JSIIMeta,
    jsii_type="tm-cdk-constructs.TmVpcBase",
):
    '''(experimental) A VPC construct that creates a VPC with public and private subnets.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        range_cidr: builtins.str,
        enable_endpoints: typing.Optional[typing.Sequence[builtins.str]] = None,
        availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        cidr: typing.Optional[builtins.str] = None,
        create_internet_gateway: typing.Optional[builtins.bool] = None,
        default_instance_tenancy: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.DefaultInstanceTenancy] = None,
        enable_dns_hostnames: typing.Optional[builtins.bool] = None,
        enable_dns_support: typing.Optional[builtins.bool] = None,
        flow_logs: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.FlowLogOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        gateway_endpoints: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.GatewayVpcEndpointOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        ip_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses] = None,
        ip_protocol: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IpProtocol] = None,
        ipv6_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpv6Addresses] = None,
        max_azs: typing.Optional[jsii.Number] = None,
        nat_gateway_provider: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.NatProvider] = None,
        nat_gateways: typing.Optional[jsii.Number] = None,
        nat_gateway_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        reserved_azs: typing.Optional[jsii.Number] = None,
        restrict_default_security_group: typing.Optional[builtins.bool] = None,
        subnet_configuration: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
        vpc_name: typing.Optional[builtins.str] = None,
        vpn_connections: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpnConnectionOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        vpn_gateway: typing.Optional[builtins.bool] = None,
        vpn_gateway_asn: typing.Optional[jsii.Number] = None,
        vpn_route_propagation: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''(experimental) The VPC created by the construct.

        :param scope: -
        :param id: -
        :param range_cidr: (experimental) The CIDR block for the VPC.
        :param enable_endpoints: (experimental) Indicates whether to enable the S3 endpoint for the VPC.
        :param availability_zones: Availability zones this VPC spans. Specify this option only if you do not specify ``maxAzs``. Default: - a subset of AZs of the stack
        :param cidr: (deprecated) The CIDR range to use for the VPC, e.g. '10.0.0.0/16'. Should be a minimum of /28 and maximum size of /16. The range will be split across all subnets per Availability Zone. Default: Vpc.DEFAULT_CIDR_RANGE
        :param create_internet_gateway: If set to false then disable the creation of the default internet gateway. Default: true
        :param default_instance_tenancy: The default tenancy of instances launched into the VPC. By setting this to dedicated tenancy, instances will be launched on hardware dedicated to a single AWS customer, unless specifically specified at instance launch time. Please note, not all instance types are usable with Dedicated tenancy. Default: DefaultInstanceTenancy.Default (shared) tenancy
        :param enable_dns_hostnames: Indicates whether the instances launched in the VPC get public DNS hostnames. If this attribute is true, instances in the VPC get public DNS hostnames, but only if the enableDnsSupport attribute is also set to true. Default: true
        :param enable_dns_support: Indicates whether the DNS resolution is supported for the VPC. If this attribute is false, the Amazon-provided DNS server in the VPC that resolves public DNS hostnames to IP addresses is not enabled. If this attribute is true, queries to the Amazon provided DNS server at the 169.254.169.253 IP address, or the reserved IP address at the base of the VPC IPv4 network range plus two will succeed. Default: true
        :param flow_logs: Flow logs to add to this VPC. Default: - No flow logs.
        :param gateway_endpoints: Gateway endpoints to add to this VPC. Default: - None.
        :param ip_addresses: The Provider to use to allocate IPv4 Space to your VPC. Options include static allocation or from a pool. Note this is specific to IPv4 addresses. Default: ec2.IpAddresses.cidr
        :param ip_protocol: The protocol of the vpc. Options are IPv4 only or dual stack. Default: IpProtocol.IPV4_ONLY
        :param ipv6_addresses: The Provider to use to allocate IPv6 Space to your VPC. Options include amazon provided CIDR block. Note this is specific to IPv6 addresses. Default: Ipv6Addresses.amazonProvided
        :param max_azs: Define the maximum number of AZs to use in this region. If the region has more AZs than you want to use (for example, because of EIP limits), pick a lower number here. The AZs will be sorted and picked from the start of the list. If you pick a higher number than the number of AZs in the region, all AZs in the region will be selected. To use "all AZs" available to your account, use a high number (such as 99). Be aware that environment-agnostic stacks will be created with access to only 2 AZs, so to use more than 2 AZs, be sure to specify the account and region on your stack. Specify this option only if you do not specify ``availabilityZones``. Default: 3
        :param nat_gateway_provider: What type of NAT provider to use. Select between NAT gateways or NAT instances. NAT gateways may not be available in all AWS regions. Default: NatProvider.gateway()
        :param nat_gateways: The number of NAT Gateways/Instances to create. The type of NAT gateway or instance will be determined by the ``natGatewayProvider`` parameter. You can set this number lower than the number of Availability Zones in your VPC in order to save on NAT cost. Be aware you may be charged for cross-AZ data traffic instead. Default: - One NAT gateway/instance per Availability Zone
        :param nat_gateway_subnets: Configures the subnets which will have NAT Gateways/Instances. You can pick a specific group of subnets by specifying the group name; the picked subnets must be public subnets. Only necessary if you have more than one public subnet group. Default: - All public subnets.
        :param reserved_azs: Define the number of AZs to reserve. When specified, the IP space is reserved for the azs but no actual resources are provisioned. Default: 0
        :param restrict_default_security_group: If set to true then the default inbound & outbound rules will be removed from the default security group. Default: true if '@aws-cdk/aws-ec2:restrictDefaultSecurityGroup' is enabled, false otherwise
        :param subnet_configuration: Configure the subnets to build for each AZ. Each entry in this list configures a Subnet Group; each group will contain a subnet for each Availability Zone. For example, if you want 1 public subnet, 1 private subnet, and 1 isolated subnet in each AZ provide the following:: new ec2.Vpc(this, 'VPC', { subnetConfiguration: [ { cidrMask: 24, name: 'ingress', subnetType: ec2.SubnetType.PUBLIC, }, { cidrMask: 24, name: 'application', subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS, }, { cidrMask: 28, name: 'rds', subnetType: ec2.SubnetType.PRIVATE_ISOLATED, } ] }); Default: - The VPC CIDR will be evenly divided between 1 public and 1 private subnet per AZ.
        :param vpc_name: The VPC name. Since the VPC resource doesn't support providing a physical name, the value provided here will be recorded in the ``Name`` tag Default: this.node.path
        :param vpn_connections: VPN connections to this VPC. Default: - No connections.
        :param vpn_gateway: Indicates whether a VPN gateway should be created and attached to this VPC. Default: - true when vpnGatewayAsn or vpnConnections is specified
        :param vpn_gateway_asn: The private Autonomous System Number (ASN) for the VPN gateway. Default: - Amazon default ASN.
        :param vpn_route_propagation: Where to propagate VPN routes. Default: - On the route tables associated with private subnets. If no private subnets exists, isolated subnets are used. If no isolated subnets exists, public subnets are used.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbbf384773ee5d4094012bcdf005cac4c749df363829f0efba57bdfc122d59a1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = TmVpcProps(
            range_cidr=range_cidr,
            enable_endpoints=enable_endpoints,
            availability_zones=availability_zones,
            cidr=cidr,
            create_internet_gateway=create_internet_gateway,
            default_instance_tenancy=default_instance_tenancy,
            enable_dns_hostnames=enable_dns_hostnames,
            enable_dns_support=enable_dns_support,
            flow_logs=flow_logs,
            gateway_endpoints=gateway_endpoints,
            ip_addresses=ip_addresses,
            ip_protocol=ip_protocol,
            ipv6_addresses=ipv6_addresses,
            max_azs=max_azs,
            nat_gateway_provider=nat_gateway_provider,
            nat_gateways=nat_gateways,
            nat_gateway_subnets=nat_gateway_subnets,
            reserved_azs=reserved_azs,
            restrict_default_security_group=restrict_default_security_group,
            subnet_configuration=subnet_configuration,
            vpc_name=vpc_name,
            vpn_connections=vpn_connections,
            vpn_gateway=vpn_gateway,
            vpn_gateway_asn=vpn_gateway_asn,
            vpn_route_propagation=vpn_route_propagation,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="tm-cdk-constructs.TmVpcProps",
    jsii_struct_bases=[_aws_cdk_aws_ec2_ceddda9d.VpcProps],
    name_mapping={
        "availability_zones": "availabilityZones",
        "cidr": "cidr",
        "create_internet_gateway": "createInternetGateway",
        "default_instance_tenancy": "defaultInstanceTenancy",
        "enable_dns_hostnames": "enableDnsHostnames",
        "enable_dns_support": "enableDnsSupport",
        "flow_logs": "flowLogs",
        "gateway_endpoints": "gatewayEndpoints",
        "ip_addresses": "ipAddresses",
        "ip_protocol": "ipProtocol",
        "ipv6_addresses": "ipv6Addresses",
        "max_azs": "maxAzs",
        "nat_gateway_provider": "natGatewayProvider",
        "nat_gateways": "natGateways",
        "nat_gateway_subnets": "natGatewaySubnets",
        "reserved_azs": "reservedAzs",
        "restrict_default_security_group": "restrictDefaultSecurityGroup",
        "subnet_configuration": "subnetConfiguration",
        "vpc_name": "vpcName",
        "vpn_connections": "vpnConnections",
        "vpn_gateway": "vpnGateway",
        "vpn_gateway_asn": "vpnGatewayAsn",
        "vpn_route_propagation": "vpnRoutePropagation",
        "range_cidr": "rangeCidr",
        "enable_endpoints": "enableEndpoints",
    },
)
class TmVpcProps(_aws_cdk_aws_ec2_ceddda9d.VpcProps):
    def __init__(
        self,
        *,
        availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        cidr: typing.Optional[builtins.str] = None,
        create_internet_gateway: typing.Optional[builtins.bool] = None,
        default_instance_tenancy: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.DefaultInstanceTenancy] = None,
        enable_dns_hostnames: typing.Optional[builtins.bool] = None,
        enable_dns_support: typing.Optional[builtins.bool] = None,
        flow_logs: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.FlowLogOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        gateway_endpoints: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.GatewayVpcEndpointOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        ip_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses] = None,
        ip_protocol: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IpProtocol] = None,
        ipv6_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpv6Addresses] = None,
        max_azs: typing.Optional[jsii.Number] = None,
        nat_gateway_provider: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.NatProvider] = None,
        nat_gateways: typing.Optional[jsii.Number] = None,
        nat_gateway_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        reserved_azs: typing.Optional[jsii.Number] = None,
        restrict_default_security_group: typing.Optional[builtins.bool] = None,
        subnet_configuration: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
        vpc_name: typing.Optional[builtins.str] = None,
        vpn_connections: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpnConnectionOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        vpn_gateway: typing.Optional[builtins.bool] = None,
        vpn_gateway_asn: typing.Optional[jsii.Number] = None,
        vpn_route_propagation: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]]] = None,
        range_cidr: builtins.str,
        enable_endpoints: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Represents the configuration for a VPC.

        :param availability_zones: Availability zones this VPC spans. Specify this option only if you do not specify ``maxAzs``. Default: - a subset of AZs of the stack
        :param cidr: (deprecated) The CIDR range to use for the VPC, e.g. '10.0.0.0/16'. Should be a minimum of /28 and maximum size of /16. The range will be split across all subnets per Availability Zone. Default: Vpc.DEFAULT_CIDR_RANGE
        :param create_internet_gateway: If set to false then disable the creation of the default internet gateway. Default: true
        :param default_instance_tenancy: The default tenancy of instances launched into the VPC. By setting this to dedicated tenancy, instances will be launched on hardware dedicated to a single AWS customer, unless specifically specified at instance launch time. Please note, not all instance types are usable with Dedicated tenancy. Default: DefaultInstanceTenancy.Default (shared) tenancy
        :param enable_dns_hostnames: Indicates whether the instances launched in the VPC get public DNS hostnames. If this attribute is true, instances in the VPC get public DNS hostnames, but only if the enableDnsSupport attribute is also set to true. Default: true
        :param enable_dns_support: Indicates whether the DNS resolution is supported for the VPC. If this attribute is false, the Amazon-provided DNS server in the VPC that resolves public DNS hostnames to IP addresses is not enabled. If this attribute is true, queries to the Amazon provided DNS server at the 169.254.169.253 IP address, or the reserved IP address at the base of the VPC IPv4 network range plus two will succeed. Default: true
        :param flow_logs: Flow logs to add to this VPC. Default: - No flow logs.
        :param gateway_endpoints: Gateway endpoints to add to this VPC. Default: - None.
        :param ip_addresses: The Provider to use to allocate IPv4 Space to your VPC. Options include static allocation or from a pool. Note this is specific to IPv4 addresses. Default: ec2.IpAddresses.cidr
        :param ip_protocol: The protocol of the vpc. Options are IPv4 only or dual stack. Default: IpProtocol.IPV4_ONLY
        :param ipv6_addresses: The Provider to use to allocate IPv6 Space to your VPC. Options include amazon provided CIDR block. Note this is specific to IPv6 addresses. Default: Ipv6Addresses.amazonProvided
        :param max_azs: Define the maximum number of AZs to use in this region. If the region has more AZs than you want to use (for example, because of EIP limits), pick a lower number here. The AZs will be sorted and picked from the start of the list. If you pick a higher number than the number of AZs in the region, all AZs in the region will be selected. To use "all AZs" available to your account, use a high number (such as 99). Be aware that environment-agnostic stacks will be created with access to only 2 AZs, so to use more than 2 AZs, be sure to specify the account and region on your stack. Specify this option only if you do not specify ``availabilityZones``. Default: 3
        :param nat_gateway_provider: What type of NAT provider to use. Select between NAT gateways or NAT instances. NAT gateways may not be available in all AWS regions. Default: NatProvider.gateway()
        :param nat_gateways: The number of NAT Gateways/Instances to create. The type of NAT gateway or instance will be determined by the ``natGatewayProvider`` parameter. You can set this number lower than the number of Availability Zones in your VPC in order to save on NAT cost. Be aware you may be charged for cross-AZ data traffic instead. Default: - One NAT gateway/instance per Availability Zone
        :param nat_gateway_subnets: Configures the subnets which will have NAT Gateways/Instances. You can pick a specific group of subnets by specifying the group name; the picked subnets must be public subnets. Only necessary if you have more than one public subnet group. Default: - All public subnets.
        :param reserved_azs: Define the number of AZs to reserve. When specified, the IP space is reserved for the azs but no actual resources are provisioned. Default: 0
        :param restrict_default_security_group: If set to true then the default inbound & outbound rules will be removed from the default security group. Default: true if '@aws-cdk/aws-ec2:restrictDefaultSecurityGroup' is enabled, false otherwise
        :param subnet_configuration: Configure the subnets to build for each AZ. Each entry in this list configures a Subnet Group; each group will contain a subnet for each Availability Zone. For example, if you want 1 public subnet, 1 private subnet, and 1 isolated subnet in each AZ provide the following:: new ec2.Vpc(this, 'VPC', { subnetConfiguration: [ { cidrMask: 24, name: 'ingress', subnetType: ec2.SubnetType.PUBLIC, }, { cidrMask: 24, name: 'application', subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS, }, { cidrMask: 28, name: 'rds', subnetType: ec2.SubnetType.PRIVATE_ISOLATED, } ] }); Default: - The VPC CIDR will be evenly divided between 1 public and 1 private subnet per AZ.
        :param vpc_name: The VPC name. Since the VPC resource doesn't support providing a physical name, the value provided here will be recorded in the ``Name`` tag Default: this.node.path
        :param vpn_connections: VPN connections to this VPC. Default: - No connections.
        :param vpn_gateway: Indicates whether a VPN gateway should be created and attached to this VPC. Default: - true when vpnGatewayAsn or vpnConnections is specified
        :param vpn_gateway_asn: The private Autonomous System Number (ASN) for the VPN gateway. Default: - Amazon default ASN.
        :param vpn_route_propagation: Where to propagate VPN routes. Default: - On the route tables associated with private subnets. If no private subnets exists, isolated subnets are used. If no isolated subnets exists, public subnets are used.
        :param range_cidr: (experimental) The CIDR block for the VPC.
        :param enable_endpoints: (experimental) Indicates whether to enable the S3 endpoint for the VPC.

        :stability: experimental
        '''
        if isinstance(nat_gateway_subnets, dict):
            nat_gateway_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**nat_gateway_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6215cfcb5e410d0a1155ca30efab18d6b3cf0f425461591df31e65ec5978275e)
            check_type(argname="argument availability_zones", value=availability_zones, expected_type=type_hints["availability_zones"])
            check_type(argname="argument cidr", value=cidr, expected_type=type_hints["cidr"])
            check_type(argname="argument create_internet_gateway", value=create_internet_gateway, expected_type=type_hints["create_internet_gateway"])
            check_type(argname="argument default_instance_tenancy", value=default_instance_tenancy, expected_type=type_hints["default_instance_tenancy"])
            check_type(argname="argument enable_dns_hostnames", value=enable_dns_hostnames, expected_type=type_hints["enable_dns_hostnames"])
            check_type(argname="argument enable_dns_support", value=enable_dns_support, expected_type=type_hints["enable_dns_support"])
            check_type(argname="argument flow_logs", value=flow_logs, expected_type=type_hints["flow_logs"])
            check_type(argname="argument gateway_endpoints", value=gateway_endpoints, expected_type=type_hints["gateway_endpoints"])
            check_type(argname="argument ip_addresses", value=ip_addresses, expected_type=type_hints["ip_addresses"])
            check_type(argname="argument ip_protocol", value=ip_protocol, expected_type=type_hints["ip_protocol"])
            check_type(argname="argument ipv6_addresses", value=ipv6_addresses, expected_type=type_hints["ipv6_addresses"])
            check_type(argname="argument max_azs", value=max_azs, expected_type=type_hints["max_azs"])
            check_type(argname="argument nat_gateway_provider", value=nat_gateway_provider, expected_type=type_hints["nat_gateway_provider"])
            check_type(argname="argument nat_gateways", value=nat_gateways, expected_type=type_hints["nat_gateways"])
            check_type(argname="argument nat_gateway_subnets", value=nat_gateway_subnets, expected_type=type_hints["nat_gateway_subnets"])
            check_type(argname="argument reserved_azs", value=reserved_azs, expected_type=type_hints["reserved_azs"])
            check_type(argname="argument restrict_default_security_group", value=restrict_default_security_group, expected_type=type_hints["restrict_default_security_group"])
            check_type(argname="argument subnet_configuration", value=subnet_configuration, expected_type=type_hints["subnet_configuration"])
            check_type(argname="argument vpc_name", value=vpc_name, expected_type=type_hints["vpc_name"])
            check_type(argname="argument vpn_connections", value=vpn_connections, expected_type=type_hints["vpn_connections"])
            check_type(argname="argument vpn_gateway", value=vpn_gateway, expected_type=type_hints["vpn_gateway"])
            check_type(argname="argument vpn_gateway_asn", value=vpn_gateway_asn, expected_type=type_hints["vpn_gateway_asn"])
            check_type(argname="argument vpn_route_propagation", value=vpn_route_propagation, expected_type=type_hints["vpn_route_propagation"])
            check_type(argname="argument range_cidr", value=range_cidr, expected_type=type_hints["range_cidr"])
            check_type(argname="argument enable_endpoints", value=enable_endpoints, expected_type=type_hints["enable_endpoints"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "range_cidr": range_cidr,
        }
        if availability_zones is not None:
            self._values["availability_zones"] = availability_zones
        if cidr is not None:
            self._values["cidr"] = cidr
        if create_internet_gateway is not None:
            self._values["create_internet_gateway"] = create_internet_gateway
        if default_instance_tenancy is not None:
            self._values["default_instance_tenancy"] = default_instance_tenancy
        if enable_dns_hostnames is not None:
            self._values["enable_dns_hostnames"] = enable_dns_hostnames
        if enable_dns_support is not None:
            self._values["enable_dns_support"] = enable_dns_support
        if flow_logs is not None:
            self._values["flow_logs"] = flow_logs
        if gateway_endpoints is not None:
            self._values["gateway_endpoints"] = gateway_endpoints
        if ip_addresses is not None:
            self._values["ip_addresses"] = ip_addresses
        if ip_protocol is not None:
            self._values["ip_protocol"] = ip_protocol
        if ipv6_addresses is not None:
            self._values["ipv6_addresses"] = ipv6_addresses
        if max_azs is not None:
            self._values["max_azs"] = max_azs
        if nat_gateway_provider is not None:
            self._values["nat_gateway_provider"] = nat_gateway_provider
        if nat_gateways is not None:
            self._values["nat_gateways"] = nat_gateways
        if nat_gateway_subnets is not None:
            self._values["nat_gateway_subnets"] = nat_gateway_subnets
        if reserved_azs is not None:
            self._values["reserved_azs"] = reserved_azs
        if restrict_default_security_group is not None:
            self._values["restrict_default_security_group"] = restrict_default_security_group
        if subnet_configuration is not None:
            self._values["subnet_configuration"] = subnet_configuration
        if vpc_name is not None:
            self._values["vpc_name"] = vpc_name
        if vpn_connections is not None:
            self._values["vpn_connections"] = vpn_connections
        if vpn_gateway is not None:
            self._values["vpn_gateway"] = vpn_gateway
        if vpn_gateway_asn is not None:
            self._values["vpn_gateway_asn"] = vpn_gateway_asn
        if vpn_route_propagation is not None:
            self._values["vpn_route_propagation"] = vpn_route_propagation
        if enable_endpoints is not None:
            self._values["enable_endpoints"] = enable_endpoints

    @builtins.property
    def availability_zones(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Availability zones this VPC spans.

        Specify this option only if you do not specify ``maxAzs``.

        :default: - a subset of AZs of the stack
        '''
        result = self._values.get("availability_zones")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cidr(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The CIDR range to use for the VPC, e.g. '10.0.0.0/16'.

        Should be a minimum of /28 and maximum size of /16. The range will be
        split across all subnets per Availability Zone.

        :default: Vpc.DEFAULT_CIDR_RANGE

        :deprecated: Use ipAddresses instead

        :stability: deprecated
        '''
        result = self._values.get("cidr")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def create_internet_gateway(self) -> typing.Optional[builtins.bool]:
        '''If set to false then disable the creation of the default internet gateway.

        :default: true
        '''
        result = self._values.get("create_internet_gateway")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def default_instance_tenancy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.DefaultInstanceTenancy]:
        '''The default tenancy of instances launched into the VPC.

        By setting this to dedicated tenancy, instances will be launched on
        hardware dedicated to a single AWS customer, unless specifically specified
        at instance launch time. Please note, not all instance types are usable
        with Dedicated tenancy.

        :default: DefaultInstanceTenancy.Default (shared) tenancy
        '''
        result = self._values.get("default_instance_tenancy")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.DefaultInstanceTenancy], result)

    @builtins.property
    def enable_dns_hostnames(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether the instances launched in the VPC get public DNS hostnames.

        If this attribute is true, instances in the VPC get public DNS hostnames,
        but only if the enableDnsSupport attribute is also set to true.

        :default: true
        '''
        result = self._values.get("enable_dns_hostnames")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_dns_support(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether the DNS resolution is supported for the VPC.

        If this attribute is false, the Amazon-provided DNS server in the VPC that
        resolves public DNS hostnames to IP addresses is not enabled. If this
        attribute is true, queries to the Amazon provided DNS server at the
        169.254.169.253 IP address, or the reserved IP address at the base of the
        VPC IPv4 network range plus two will succeed.

        :default: true
        '''
        result = self._values.get("enable_dns_support")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def flow_logs(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ec2_ceddda9d.FlowLogOptions]]:
        '''Flow logs to add to this VPC.

        :default: - No flow logs.
        '''
        result = self._values.get("flow_logs")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ec2_ceddda9d.FlowLogOptions]], result)

    @builtins.property
    def gateway_endpoints(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ec2_ceddda9d.GatewayVpcEndpointOptions]]:
        '''Gateway endpoints to add to this VPC.

        :default: - None.
        '''
        result = self._values.get("gateway_endpoints")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ec2_ceddda9d.GatewayVpcEndpointOptions]], result)

    @builtins.property
    def ip_addresses(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses]:
        '''The Provider to use to allocate IPv4 Space to your VPC.

        Options include static allocation or from a pool.

        Note this is specific to IPv4 addresses.

        :default: ec2.IpAddresses.cidr
        '''
        result = self._values.get("ip_addresses")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses], result)

    @builtins.property
    def ip_protocol(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IpProtocol]:
        '''The protocol of the vpc.

        Options are IPv4 only or dual stack.

        :default: IpProtocol.IPV4_ONLY
        '''
        result = self._values.get("ip_protocol")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IpProtocol], result)

    @builtins.property
    def ipv6_addresses(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpv6Addresses]:
        '''The Provider to use to allocate IPv6 Space to your VPC.

        Options include amazon provided CIDR block.

        Note this is specific to IPv6 addresses.

        :default: Ipv6Addresses.amazonProvided
        '''
        result = self._values.get("ipv6_addresses")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpv6Addresses], result)

    @builtins.property
    def max_azs(self) -> typing.Optional[jsii.Number]:
        '''Define the maximum number of AZs to use in this region.

        If the region has more AZs than you want to use (for example, because of
        EIP limits), pick a lower number here. The AZs will be sorted and picked
        from the start of the list.

        If you pick a higher number than the number of AZs in the region, all AZs
        in the region will be selected. To use "all AZs" available to your
        account, use a high number (such as 99).

        Be aware that environment-agnostic stacks will be created with access to
        only 2 AZs, so to use more than 2 AZs, be sure to specify the account and
        region on your stack.

        Specify this option only if you do not specify ``availabilityZones``.

        :default: 3
        '''
        result = self._values.get("max_azs")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def nat_gateway_provider(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.NatProvider]:
        '''What type of NAT provider to use.

        Select between NAT gateways or NAT instances. NAT gateways
        may not be available in all AWS regions.

        :default: NatProvider.gateway()
        '''
        result = self._values.get("nat_gateway_provider")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.NatProvider], result)

    @builtins.property
    def nat_gateways(self) -> typing.Optional[jsii.Number]:
        '''The number of NAT Gateways/Instances to create.

        The type of NAT gateway or instance will be determined by the
        ``natGatewayProvider`` parameter.

        You can set this number lower than the number of Availability Zones in your
        VPC in order to save on NAT cost. Be aware you may be charged for
        cross-AZ data traffic instead.

        :default: - One NAT gateway/instance per Availability Zone
        '''
        result = self._values.get("nat_gateways")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def nat_gateway_subnets(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''Configures the subnets which will have NAT Gateways/Instances.

        You can pick a specific group of subnets by specifying the group name;
        the picked subnets must be public subnets.

        Only necessary if you have more than one public subnet group.

        :default: - All public subnets.
        '''
        result = self._values.get("nat_gateway_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def reserved_azs(self) -> typing.Optional[jsii.Number]:
        '''Define the number of AZs to reserve.

        When specified, the IP space is reserved for the azs but no actual
        resources are provisioned.

        :default: 0
        '''
        result = self._values.get("reserved_azs")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def restrict_default_security_group(self) -> typing.Optional[builtins.bool]:
        '''If set to true then the default inbound & outbound rules will be removed from the default security group.

        :default: true if '@aws-cdk/aws-ec2:restrictDefaultSecurityGroup' is enabled, false otherwise
        '''
        result = self._values.get("restrict_default_security_group")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def subnet_configuration(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.SubnetConfiguration]]:
        '''Configure the subnets to build for each AZ.

        Each entry in this list configures a Subnet Group; each group will contain a
        subnet for each Availability Zone.

        For example, if you want 1 public subnet, 1 private subnet, and 1 isolated
        subnet in each AZ provide the following::

           new ec2.Vpc(this, 'VPC', {
             subnetConfiguration: [
                {
                  cidrMask: 24,
                  name: 'ingress',
                  subnetType: ec2.SubnetType.PUBLIC,
                },
                {
                  cidrMask: 24,
                  name: 'application',
                  subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
                },
                {
                  cidrMask: 28,
                  name: 'rds',
                  subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
                }
             ]
           });

        :default:

        - The VPC CIDR will be evenly divided between 1 public and 1
        private subnet per AZ.
        '''
        result = self._values.get("subnet_configuration")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.SubnetConfiguration]], result)

    @builtins.property
    def vpc_name(self) -> typing.Optional[builtins.str]:
        '''The VPC name.

        Since the VPC resource doesn't support providing a physical name, the value provided here will be recorded in the ``Name`` tag

        :default: this.node.path
        '''
        result = self._values.get("vpc_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpn_connections(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ec2_ceddda9d.VpnConnectionOptions]]:
        '''VPN connections to this VPC.

        :default: - No connections.
        '''
        result = self._values.get("vpn_connections")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ec2_ceddda9d.VpnConnectionOptions]], result)

    @builtins.property
    def vpn_gateway(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether a VPN gateway should be created and attached to this VPC.

        :default: - true when vpnGatewayAsn or vpnConnections is specified
        '''
        result = self._values.get("vpn_gateway")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def vpn_gateway_asn(self) -> typing.Optional[jsii.Number]:
        '''The private Autonomous System Number (ASN) for the VPN gateway.

        :default: - Amazon default ASN.
        '''
        result = self._values.get("vpn_gateway_asn")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vpn_route_propagation(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]]:
        '''Where to propagate VPN routes.

        :default:

        - On the route tables associated with private subnets. If no
        private subnets exists, isolated subnets are used. If no isolated subnets
        exists, public subnets are used.
        '''
        result = self._values.get("vpn_route_propagation")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]], result)

    @builtins.property
    def range_cidr(self) -> builtins.str:
        '''(experimental) The CIDR block for the VPC.

        :stability: experimental
        '''
        result = self._values.get("range_cidr")
        assert result is not None, "Required property 'range_cidr' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def enable_endpoints(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Indicates whether to enable the S3 endpoint for the VPC.

        :stability: experimental
        '''
        result = self._values.get("enable_endpoints")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TmVpcProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "IAnsiblePlaybookEc2Props",
    "IIEcsDeploymentHookProps",
    "IIefsVolumes",
    "IPatchManagerProps",
    "IRedisClusterProps",
    "ITmEcsDeploymentHookProps",
    "TmAnsiblePlaybookEc2",
    "TmApplicationLoadBalancedFargateService",
    "TmApplicationLoadBalancedFargateServiceProps",
    "TmEcsDeploymentHook",
    "TmElasticacheRedisCluster",
    "TmPatchManager",
    "TmPipeline",
    "TmPipelineProps",
    "TmRdsAuroraMysqlServerless",
    "TmRdsAuroraMysqlServerlessProps",
    "TmSolrEc2",
    "TmSorlEc2Props",
    "TmVpcBase",
    "TmVpcProps",
]

publication.publish()

def _typecheckingstub__f1a903c19542e4352765dcd8d7b1f56a6384d1d87f7e0f467d8dabb1cc6d22ea(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83e58a3cc4f1663dc2f2d963060c4f836501ed3bd692e67dd798d40affc6f4b8(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f71e6a9866bd308daaa460b4d0746c78d83208367163e1d12e0fc74564f7a85(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36649a5ca8045fe85e6c1359daaf2a451d8d26653d94430bc7585f772be0c23e(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__683916488da7e0e69f1c09c3ad97064949559068c07bab11ded3e343a5865b6d(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b059d160412d3c557f5d6a2fe32da0d0d3c08585954048fddd1fd2a9a573e001(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f63059b634ff1179395c346fc3b3a79affcbf4362e001e1aa88a9c5f2aab4f44(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__060fbc8c38b993593f46abadd9e52ce939a4915e541206d0a2ab546b1c7198d3(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ead78d7548ad9ea41e83897677e686c66cd9123caf1358155a1d718a05415036(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__715c932dfcfddfe301fa304b45c0127f1c51f06c2a5266f69307c1100b71aa68(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fe18738b936c980e7bedaeb70d95f218e08417b1ba172150eabc40179c8ce0f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__119ccde770251ce59b3a03156371764d318f9589399c47e463f7676a53020a76(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81a01a570b69a60eee6f3e69e8cbcd87347e34a40d40e8b0e66809c5cdc26618(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42431f5a113b2458c40fce9933a4c212544cb69a108aab4db9a387397aea33d2(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d778cbf0a2091e9238bc92f3b64dfd317cc8c20a70dc36bcb0bb9e6cfe99c329(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8366273bde17123e69e9e8bf15d532faeb6a1fa2ab02de466c10bdd5dda35887(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd0ad356ec36574ec933d246bdf9491f636b0a214adacafeb702df23cd668b72(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cbcfc13fcd8c944ff3ef99ae7bab32e7d45e5cc28cecec726f0744c8a0d9559(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21f30d07501dce4ff4ca3b2bc308d1794827451589a0083de583c78481bf9c5d(
    value: _aws_cdk_aws_ec2_ceddda9d.IVpc,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d828e10fefb31677c87894f5994eb46d80bc67eb143d270ec0fed818c84af5b(
    value: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dac7cb7192347a4a936a3d02b0161c916be9cad3fa629b43c5bf706d5e1f4f05(
    value: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ec2_ceddda9d.IConnectable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bdcce7b655de820ab2c54af62438017ffc4f1949a24578a11c2e28943acdb11(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5cfb68ddfdbb88436eebd8dfea20e7bd1cbc9bd9384a0356d1b31b4410cddf1(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15c8078499519dc59ee806fcf7820d7aaf5a3a371dfcdab144ac9c105694af15(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00b8129d6b92784234bf579641c5dc59310fc55315c12754750f50824794f818(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7845b660f76e0ef3d2be1a3839c141ee259af497e5dcd36033af73a60bda0c64(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fe79cf362cbd588b230640aa31bc6934a14764b7a438d73026f1582367acf9f(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8b0acc8f2000364664e53319e1c14cd07770cc9addd325794746b2d6d8f93bd(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66192cb7ea51e3252e8c6fac831b9d9fb359e9897448b590313a0646828fe2d0(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__501bdc3ec60ce9982e10ae2cceb69b61a322996849fe4295f6bf6fb9be0971af(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20578dcbba1061b4b4d2d2e2df7883c22fb6a07d778f71446e07576d97ca151a(
    value: _aws_cdk_aws_ecs_ceddda9d.ICluster,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1226c2b955f55700a12fda7e98d36b6ab4e16198bc3de6b401182da2b7d46ee3(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fa90c86569346a9ddbb1b5060130a99a7389f526aa8c5cac44b03ba56810ab3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d169b5c8de437cf5b054b95142ef10ebc85b6c73b8b9a77625cd12037f6714d(
    value: typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b4f82c53e1215b1126124f86481689b59a8bfa28f1f5d3e6c23b6a05f33b001(
    value: typing.List[_aws_cdk_aws_ec2_ceddda9d.ISubnet],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93f64adcaed947aa09410194d2fd63d85795c91df72aeb6021f41a492a674327(
    value: _aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88c5c692c89dfe1c3959a8a9ad871be28c75e88573d8dd44f9bbea85bf74c8bd(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: IAnsiblePlaybookEc2Props,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__276f6d9198fa95fbf00df2891bf40732c0442075150996813b42fc40406667ee(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    build_context_path: builtins.str,
    build_dockerfile: builtins.str,
    build_container_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    container_port: typing.Optional[jsii.Number] = None,
    custom_http_header_value: typing.Optional[builtins.str] = None,
    ecs_deployment_hook_props: typing.Optional[IIEcsDeploymentHookProps] = None,
    efs_volumes: typing.Optional[typing.Sequence[IIefsVolumes]] = None,
    max_task_count: typing.Optional[jsii.Number] = None,
    min_task_count: typing.Optional[jsii.Number] = None,
    scheduled_task_schedule_expression: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    scheduled_tasks_command: typing.Optional[builtins.str] = None,
    secrets: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ecs_ceddda9d.Secret]] = None,
    assign_public_ip: typing.Optional[builtins.bool] = None,
    container_cpu: typing.Optional[jsii.Number] = None,
    container_memory_limit_mib: typing.Optional[jsii.Number] = None,
    health_check: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    task_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    capacity_provider_strategies: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy, typing.Dict[builtins.str, typing.Any]]]] = None,
    certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
    circuit_breaker: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker, typing.Dict[builtins.str, typing.Any]]] = None,
    cloud_map_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    cluster: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster] = None,
    deployment_controller: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentController, typing.Dict[builtins.str, typing.Any]]] = None,
    desired_count: typing.Optional[jsii.Number] = None,
    domain_name: typing.Optional[builtins.str] = None,
    domain_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
    enable_ecs_managed_tags: typing.Optional[builtins.bool] = None,
    enable_execute_command: typing.Optional[builtins.bool] = None,
    health_check_grace_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ip_address_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IpAddressType] = None,
    listener_port: typing.Optional[jsii.Number] = None,
    load_balancer: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer] = None,
    load_balancer_name: typing.Optional[builtins.str] = None,
    max_healthy_percent: typing.Optional[jsii.Number] = None,
    min_healthy_percent: typing.Optional[jsii.Number] = None,
    open_listener: typing.Optional[builtins.bool] = None,
    propagate_tags: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
    protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
    protocol_version: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion] = None,
    public_load_balancer: typing.Optional[builtins.bool] = None,
    record_type: typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedServiceRecordType] = None,
    redirect_http: typing.Optional[builtins.bool] = None,
    service_name: typing.Optional[builtins.str] = None,
    ssl_policy: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy] = None,
    target_protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
    task_image_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    cpu: typing.Optional[jsii.Number] = None,
    ephemeral_storage_gib: typing.Optional[jsii.Number] = None,
    memory_limit_mib: typing.Optional[jsii.Number] = None,
    platform_version: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion] = None,
    runtime_platform: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform, typing.Dict[builtins.str, typing.Any]]] = None,
    task_definition: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1dda355626d26bd05dee708afc45defd28861f9a33472bb8ec239ff3cd194d88(
    *,
    capacity_provider_strategies: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy, typing.Dict[builtins.str, typing.Any]]]] = None,
    certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
    circuit_breaker: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker, typing.Dict[builtins.str, typing.Any]]] = None,
    cloud_map_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    cluster: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster] = None,
    deployment_controller: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentController, typing.Dict[builtins.str, typing.Any]]] = None,
    desired_count: typing.Optional[jsii.Number] = None,
    domain_name: typing.Optional[builtins.str] = None,
    domain_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
    enable_ecs_managed_tags: typing.Optional[builtins.bool] = None,
    enable_execute_command: typing.Optional[builtins.bool] = None,
    health_check_grace_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ip_address_type: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IpAddressType] = None,
    listener_port: typing.Optional[jsii.Number] = None,
    load_balancer: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer] = None,
    load_balancer_name: typing.Optional[builtins.str] = None,
    max_healthy_percent: typing.Optional[jsii.Number] = None,
    min_healthy_percent: typing.Optional[jsii.Number] = None,
    open_listener: typing.Optional[builtins.bool] = None,
    propagate_tags: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
    protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
    protocol_version: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion] = None,
    public_load_balancer: typing.Optional[builtins.bool] = None,
    record_type: typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedServiceRecordType] = None,
    redirect_http: typing.Optional[builtins.bool] = None,
    service_name: typing.Optional[builtins.str] = None,
    ssl_policy: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy] = None,
    target_protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
    task_image_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    cpu: typing.Optional[jsii.Number] = None,
    ephemeral_storage_gib: typing.Optional[jsii.Number] = None,
    memory_limit_mib: typing.Optional[jsii.Number] = None,
    platform_version: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion] = None,
    runtime_platform: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform, typing.Dict[builtins.str, typing.Any]]] = None,
    task_definition: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition] = None,
    assign_public_ip: typing.Optional[builtins.bool] = None,
    container_cpu: typing.Optional[jsii.Number] = None,
    container_memory_limit_mib: typing.Optional[jsii.Number] = None,
    health_check: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    task_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    build_context_path: builtins.str,
    build_dockerfile: builtins.str,
    build_container_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    container_port: typing.Optional[jsii.Number] = None,
    custom_http_header_value: typing.Optional[builtins.str] = None,
    ecs_deployment_hook_props: typing.Optional[IIEcsDeploymentHookProps] = None,
    efs_volumes: typing.Optional[typing.Sequence[IIefsVolumes]] = None,
    max_task_count: typing.Optional[jsii.Number] = None,
    min_task_count: typing.Optional[jsii.Number] = None,
    scheduled_task_schedule_expression: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    scheduled_tasks_command: typing.Optional[builtins.str] = None,
    secrets: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ecs_ceddda9d.Secret]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e199dd5d2e264a2fa0e6a8304ff929cd50b23b16f3b48934a93d88d6a26bd6d7(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: ITmEcsDeploymentHookProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a3a11708e6393483d682acaf674337b7936f6184040624914ace3482b03b7af(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: IRedisClusterProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__940308e655d0615a415ab199fc1b92548ab09b9aecad8931705ef7e151d3a4ec(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: IPatchManagerProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a993414424d3e58108b1515d1ae43df55fcea9a5bf26c77d45647cea67364f8(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    pipeline_name: builtins.str,
    repo_branch: builtins.str,
    repo_name: builtins.str,
    primary_output_directory: typing.Optional[builtins.str] = None,
    synth_command: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c90f448d2c851abcb766597516c1d94417ef3eed41e3bc82a985a84bd6ff2854(
    *,
    pipeline_name: builtins.str,
    repo_branch: builtins.str,
    repo_name: builtins.str,
    primary_output_directory: typing.Optional[builtins.str] = None,
    synth_command: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc939679af82c57cdfc24824fb9ec6ef0580d01390aa5c263b878d67d4912115(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    enable_global: typing.Optional[builtins.bool] = None,
    engine: _aws_cdk_aws_rds_ceddda9d.IClusterEngine,
    auto_minor_version_upgrade: typing.Optional[builtins.bool] = None,
    backtrack_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    backup: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.BackupProps, typing.Dict[builtins.str, typing.Any]]] = None,
    cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
    cloudwatch_logs_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    cloudwatch_logs_retention_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    cluster_identifier: typing.Optional[builtins.str] = None,
    cluster_scailability_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.ClusterScailabilityType] = None,
    cluster_scalability_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.ClusterScalabilityType] = None,
    copy_tags_to_snapshot: typing.Optional[builtins.bool] = None,
    credentials: typing.Optional[_aws_cdk_aws_rds_ceddda9d.Credentials] = None,
    database_insights_mode: typing.Optional[_aws_cdk_aws_rds_ceddda9d.DatabaseInsightsMode] = None,
    default_database_name: typing.Optional[builtins.str] = None,
    deletion_protection: typing.Optional[builtins.bool] = None,
    domain: typing.Optional[builtins.str] = None,
    domain_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    enable_cluster_level_enhanced_monitoring: typing.Optional[builtins.bool] = None,
    enable_data_api: typing.Optional[builtins.bool] = None,
    enable_local_write_forwarding: typing.Optional[builtins.bool] = None,
    enable_performance_insights: typing.Optional[builtins.bool] = None,
    engine_lifecycle_support: typing.Optional[_aws_cdk_aws_rds_ceddda9d.EngineLifecycleSupport] = None,
    iam_authentication: typing.Optional[builtins.bool] = None,
    instance_identifier_base: typing.Optional[builtins.str] = None,
    instance_props: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.InstanceProps, typing.Dict[builtins.str, typing.Any]]] = None,
    instances: typing.Optional[jsii.Number] = None,
    instance_update_behaviour: typing.Optional[_aws_cdk_aws_rds_ceddda9d.InstanceUpdateBehaviour] = None,
    monitoring_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    monitoring_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    network_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.NetworkType] = None,
    parameter_group: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IParameterGroup] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    performance_insight_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    performance_insight_retention: typing.Optional[_aws_cdk_aws_rds_ceddda9d.PerformanceInsightRetention] = None,
    port: typing.Optional[jsii.Number] = None,
    preferred_maintenance_window: typing.Optional[builtins.str] = None,
    readers: typing.Optional[typing.Sequence[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    replication_source_identifier: typing.Optional[builtins.str] = None,
    s3_export_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
    s3_export_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    s3_import_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
    s3_import_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    serverless_v2_max_capacity: typing.Optional[jsii.Number] = None,
    serverless_v2_min_capacity: typing.Optional[jsii.Number] = None,
    storage_encrypted: typing.Optional[builtins.bool] = None,
    storage_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    storage_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.DBClusterStorageType] = None,
    subnet_group: typing.Optional[_aws_cdk_aws_rds_ceddda9d.ISubnetGroup] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    writer: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2eb6185862d0dbafb21639371b5cfdd31758e49cf957284e1d423cbd3bf7cc8a(
    *,
    engine: _aws_cdk_aws_rds_ceddda9d.IClusterEngine,
    auto_minor_version_upgrade: typing.Optional[builtins.bool] = None,
    backtrack_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    backup: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.BackupProps, typing.Dict[builtins.str, typing.Any]]] = None,
    cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
    cloudwatch_logs_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    cloudwatch_logs_retention_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    cluster_identifier: typing.Optional[builtins.str] = None,
    cluster_scailability_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.ClusterScailabilityType] = None,
    cluster_scalability_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.ClusterScalabilityType] = None,
    copy_tags_to_snapshot: typing.Optional[builtins.bool] = None,
    credentials: typing.Optional[_aws_cdk_aws_rds_ceddda9d.Credentials] = None,
    database_insights_mode: typing.Optional[_aws_cdk_aws_rds_ceddda9d.DatabaseInsightsMode] = None,
    default_database_name: typing.Optional[builtins.str] = None,
    deletion_protection: typing.Optional[builtins.bool] = None,
    domain: typing.Optional[builtins.str] = None,
    domain_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    enable_cluster_level_enhanced_monitoring: typing.Optional[builtins.bool] = None,
    enable_data_api: typing.Optional[builtins.bool] = None,
    enable_local_write_forwarding: typing.Optional[builtins.bool] = None,
    enable_performance_insights: typing.Optional[builtins.bool] = None,
    engine_lifecycle_support: typing.Optional[_aws_cdk_aws_rds_ceddda9d.EngineLifecycleSupport] = None,
    iam_authentication: typing.Optional[builtins.bool] = None,
    instance_identifier_base: typing.Optional[builtins.str] = None,
    instance_props: typing.Optional[typing.Union[_aws_cdk_aws_rds_ceddda9d.InstanceProps, typing.Dict[builtins.str, typing.Any]]] = None,
    instances: typing.Optional[jsii.Number] = None,
    instance_update_behaviour: typing.Optional[_aws_cdk_aws_rds_ceddda9d.InstanceUpdateBehaviour] = None,
    monitoring_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    monitoring_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    network_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.NetworkType] = None,
    parameter_group: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IParameterGroup] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    performance_insight_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    performance_insight_retention: typing.Optional[_aws_cdk_aws_rds_ceddda9d.PerformanceInsightRetention] = None,
    port: typing.Optional[jsii.Number] = None,
    preferred_maintenance_window: typing.Optional[builtins.str] = None,
    readers: typing.Optional[typing.Sequence[_aws_cdk_aws_rds_ceddda9d.IClusterInstance]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    replication_source_identifier: typing.Optional[builtins.str] = None,
    s3_export_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
    s3_export_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    s3_import_buckets: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.IBucket]] = None,
    s3_import_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    serverless_v2_max_capacity: typing.Optional[jsii.Number] = None,
    serverless_v2_min_capacity: typing.Optional[jsii.Number] = None,
    storage_encrypted: typing.Optional[builtins.bool] = None,
    storage_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    storage_type: typing.Optional[_aws_cdk_aws_rds_ceddda9d.DBClusterStorageType] = None,
    subnet_group: typing.Optional[_aws_cdk_aws_rds_ceddda9d.ISubnetGroup] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    writer: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IClusterInstance] = None,
    enable_global: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e24b32fefe2274170cb6ddac9573e5872bec73f996a3f47c7b05cae2faa2de3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    build_context_path: builtins.str,
    allow_from: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    build_container_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    build_dockerfile: typing.Optional[builtins.str] = None,
    ebs_volume_size: typing.Optional[jsii.Number] = None,
    hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
    record_name: typing.Optional[builtins.str] = None,
    solr_java_mem: typing.Optional[builtins.str] = None,
    solr_opts: typing.Optional[builtins.str] = None,
    solr_typo3_solr_enabled_cores: typing.Optional[builtins.str] = None,
    ssm_path_prefix: typing.Optional[builtins.str] = None,
    instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
    machine_image: _aws_cdk_aws_ec2_ceddda9d.IMachineImage,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    allow_all_ipv6_outbound: typing.Optional[builtins.bool] = None,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    associate_public_ip_address: typing.Optional[builtins.bool] = None,
    availability_zone: typing.Optional[builtins.str] = None,
    block_devices: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.BlockDevice, typing.Dict[builtins.str, typing.Any]]]] = None,
    credit_specification: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CpuCredits] = None,
    detailed_monitoring: typing.Optional[builtins.bool] = None,
    disable_api_termination: typing.Optional[builtins.bool] = None,
    ebs_optimized: typing.Optional[builtins.bool] = None,
    enclave_enabled: typing.Optional[builtins.bool] = None,
    hibernation_enabled: typing.Optional[builtins.bool] = None,
    init: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CloudFormationInit] = None,
    init_options: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.ApplyCloudFormationInitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    instance_initiated_shutdown_behavior: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceInitiatedShutdownBehavior] = None,
    instance_name: typing.Optional[builtins.str] = None,
    instance_profile: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IInstanceProfile] = None,
    ipv6_address_count: typing.Optional[jsii.Number] = None,
    key_name: typing.Optional[builtins.str] = None,
    key_pair: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair] = None,
    placement_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IPlacementGroup] = None,
    private_ip_address: typing.Optional[builtins.str] = None,
    propagate_tags_to_volume_on_creation: typing.Optional[builtins.bool] = None,
    require_imdsv2: typing.Optional[builtins.bool] = None,
    resource_signal_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    source_dest_check: typing.Optional[builtins.bool] = None,
    ssm_session_permissions: typing.Optional[builtins.bool] = None,
    user_data: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.UserData] = None,
    user_data_causes_replacement: typing.Optional[builtins.bool] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7efd22ab41d2580479d98ebbaedfaf8d813ce514136c726e5537193fbc894eb9(
    *,
    instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
    machine_image: _aws_cdk_aws_ec2_ceddda9d.IMachineImage,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    allow_all_ipv6_outbound: typing.Optional[builtins.bool] = None,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    associate_public_ip_address: typing.Optional[builtins.bool] = None,
    availability_zone: typing.Optional[builtins.str] = None,
    block_devices: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.BlockDevice, typing.Dict[builtins.str, typing.Any]]]] = None,
    credit_specification: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CpuCredits] = None,
    detailed_monitoring: typing.Optional[builtins.bool] = None,
    disable_api_termination: typing.Optional[builtins.bool] = None,
    ebs_optimized: typing.Optional[builtins.bool] = None,
    enclave_enabled: typing.Optional[builtins.bool] = None,
    hibernation_enabled: typing.Optional[builtins.bool] = None,
    init: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CloudFormationInit] = None,
    init_options: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.ApplyCloudFormationInitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    instance_initiated_shutdown_behavior: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceInitiatedShutdownBehavior] = None,
    instance_name: typing.Optional[builtins.str] = None,
    instance_profile: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IInstanceProfile] = None,
    ipv6_address_count: typing.Optional[jsii.Number] = None,
    key_name: typing.Optional[builtins.str] = None,
    key_pair: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair] = None,
    placement_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IPlacementGroup] = None,
    private_ip_address: typing.Optional[builtins.str] = None,
    propagate_tags_to_volume_on_creation: typing.Optional[builtins.bool] = None,
    require_imdsv2: typing.Optional[builtins.bool] = None,
    resource_signal_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    source_dest_check: typing.Optional[builtins.bool] = None,
    ssm_session_permissions: typing.Optional[builtins.bool] = None,
    user_data: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.UserData] = None,
    user_data_causes_replacement: typing.Optional[builtins.bool] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    build_context_path: builtins.str,
    allow_from: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    build_container_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    build_dockerfile: typing.Optional[builtins.str] = None,
    ebs_volume_size: typing.Optional[jsii.Number] = None,
    hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
    record_name: typing.Optional[builtins.str] = None,
    solr_java_mem: typing.Optional[builtins.str] = None,
    solr_opts: typing.Optional[builtins.str] = None,
    solr_typo3_solr_enabled_cores: typing.Optional[builtins.str] = None,
    ssm_path_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbbf384773ee5d4094012bcdf005cac4c749df363829f0efba57bdfc122d59a1(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    range_cidr: builtins.str,
    enable_endpoints: typing.Optional[typing.Sequence[builtins.str]] = None,
    availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
    cidr: typing.Optional[builtins.str] = None,
    create_internet_gateway: typing.Optional[builtins.bool] = None,
    default_instance_tenancy: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.DefaultInstanceTenancy] = None,
    enable_dns_hostnames: typing.Optional[builtins.bool] = None,
    enable_dns_support: typing.Optional[builtins.bool] = None,
    flow_logs: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.FlowLogOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
    gateway_endpoints: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.GatewayVpcEndpointOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
    ip_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses] = None,
    ip_protocol: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IpProtocol] = None,
    ipv6_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpv6Addresses] = None,
    max_azs: typing.Optional[jsii.Number] = None,
    nat_gateway_provider: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.NatProvider] = None,
    nat_gateways: typing.Optional[jsii.Number] = None,
    nat_gateway_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    reserved_azs: typing.Optional[jsii.Number] = None,
    restrict_default_security_group: typing.Optional[builtins.bool] = None,
    subnet_configuration: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
    vpc_name: typing.Optional[builtins.str] = None,
    vpn_connections: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpnConnectionOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
    vpn_gateway: typing.Optional[builtins.bool] = None,
    vpn_gateway_asn: typing.Optional[jsii.Number] = None,
    vpn_route_propagation: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6215cfcb5e410d0a1155ca30efab18d6b3cf0f425461591df31e65ec5978275e(
    *,
    availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
    cidr: typing.Optional[builtins.str] = None,
    create_internet_gateway: typing.Optional[builtins.bool] = None,
    default_instance_tenancy: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.DefaultInstanceTenancy] = None,
    enable_dns_hostnames: typing.Optional[builtins.bool] = None,
    enable_dns_support: typing.Optional[builtins.bool] = None,
    flow_logs: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.FlowLogOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
    gateway_endpoints: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.GatewayVpcEndpointOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
    ip_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses] = None,
    ip_protocol: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IpProtocol] = None,
    ipv6_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpv6Addresses] = None,
    max_azs: typing.Optional[jsii.Number] = None,
    nat_gateway_provider: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.NatProvider] = None,
    nat_gateways: typing.Optional[jsii.Number] = None,
    nat_gateway_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    reserved_azs: typing.Optional[jsii.Number] = None,
    restrict_default_security_group: typing.Optional[builtins.bool] = None,
    subnet_configuration: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
    vpc_name: typing.Optional[builtins.str] = None,
    vpn_connections: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpnConnectionOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
    vpn_gateway: typing.Optional[builtins.bool] = None,
    vpn_gateway_asn: typing.Optional[jsii.Number] = None,
    vpn_route_propagation: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]]] = None,
    range_cidr: builtins.str,
    enable_endpoints: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
