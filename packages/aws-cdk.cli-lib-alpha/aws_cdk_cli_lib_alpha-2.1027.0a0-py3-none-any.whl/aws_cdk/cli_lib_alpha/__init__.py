r'''
# AWS CDK CLI Library (deprecated)

<!--BEGIN STABILITY BANNER-->---


![@aws-cdk/cli-lib-lpha: Deprecated](https://img.shields.io/badge/@aws--cdk/cli--lib--alpha-deprectated-red.svg?style=for-the-badge)

> This package has been deprecated in favor of [@aws-cdk/toolkit-lib](https://github.com/aws/aws-cdk-cli/issues/155),
> a newer approach providing similar functionality to what this package offered.
> Please migrate as soon as possible.
> For any migration problems, please open [an issue](https://github.com/aws/aws-cdk-cli/issues/new/choose).
> We are committed to supporting the same feature set that this package offered.

---
<!--END STABILITY BANNER-->

## ⚠️ Deprecated module

This package is has been deprecated.
Already published versions can be used, but no support is provided whatsoever and we will soon stop publishing new versions.

Instead, please use [@aws-cdk/toolkit-lib](https://github.com/aws/aws-cdk-cli/issues/155).

## Overview

Provides a library to interact with the AWS CDK CLI programmatically from jsii supported languages.
Currently the package includes implementations for:

* `cdk deploy`
* `cdk synth`
* `cdk bootstrap`
* `cdk destroy`
* `cdk list`

## Known issues

* **JavaScript/TypeScript only**\
  The jsii packages are currently not in a working state.
* **No useful return values**\
  All output is currently printed to stdout/stderr
* **Missing or Broken options**\
  Some CLI options might not be available in this package or broken

Due to the deprecation of the package, this issues will not be resolved.

## Setup

### AWS CDK app directory

Obtain an `AwsCdkCli` class from an AWS CDK app directory (containing a `cdk.json` file):

```python
cli = AwsCdkCli.from_cdk_app_directory("/path/to/cdk/app")
```

### Cloud Assembly Directory Producer

You can also create `AwsCdkCli` from a class implementing `ICloudAssemblyDirectoryProducer`.
AWS CDK apps might need to be synthesized multiple times with additional context values before they are ready.

The `produce()` method of the `ICloudAssemblyDirectoryProducer` interface provides this multi-pass ability.
It is invoked with the context values of the current iteration and should use these values to synthesize a Cloud Assembly.
The return value is the path to the assembly directory.

A basic implementation would look like this:

```python
@jsii.implements(ICloudAssemblyDirectoryProducer)
class MyProducer:
    def produce(self, context):
        app = cdk.App(context=context)
        stack = cdk.Stack(app)
        return app.synth().directory
```

For all features (e.g. lookups) to work correctly, `cdk.App()` must be instantiated with the received `context` values.
Since it is not possible to update the context of an app, it must be created as part of the `produce()` method.

The producer can than be used like this:

```python
cli = AwsCdkCli.from_cloud_assembly_directory_producer(MyProducer())
```

## Commands

### list

```python
# await this asynchronous method call using a language feature
cli.list()
```

### synth

```python
# await this asynchronous method call using a language feature
cli.synth(
    stacks=["MyTestStack"]
)
```

### bootstrap

```python
# await this asynchronous method call using a language feature
cli.bootstrap()
```

### deploy

```python
# await this asynchronous method call using a language feature
cli.deploy(
    stacks=["MyTestStack"]
)
```

### destroy

```python
# await this asynchronous method call using a language feature
cli.destroy(
    stacks=["MyTestStack"]
)
```
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


@jsii.data_type(
    jsii_type="@aws-cdk/cli-lib-alpha.CdkAppDirectoryProps",
    jsii_struct_bases=[],
    name_mapping={"app": "app", "output": "output"},
)
class CdkAppDirectoryProps:
    def __init__(
        self,
        *,
        app: typing.Optional[builtins.str] = None,
        output: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(deprecated) Configuration for creating a CLI from an AWS CDK App directory.

        :param app: (deprecated) Command-line for executing your app or a cloud assembly directory e.g. "node bin/my-app.js" or "cdk.out". Default: - read from cdk.json
        :param output: (deprecated) Emits the synthesized cloud assembly into a directory. Default: cdk.out

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4cbd6d84e56b51ee4f66f530481eb49b7f94fb112b3e02f0973628fb7e3ec22b)
            check_type(argname="argument app", value=app, expected_type=type_hints["app"])
            check_type(argname="argument output", value=output, expected_type=type_hints["output"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if app is not None:
            self._values["app"] = app
        if output is not None:
            self._values["output"] = output

    @builtins.property
    def app(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Command-line for executing your app or a cloud assembly directory e.g. "node bin/my-app.js" or "cdk.out".

        :default: - read from cdk.json

        :stability: deprecated
        '''
        result = self._values.get("app")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def output(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Emits the synthesized cloud assembly into a directory.

        :default: cdk.out

        :stability: deprecated
        '''
        result = self._values.get("output")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CdkAppDirectoryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/cli-lib-alpha.HotswapMode")
class HotswapMode(enum.Enum):
    '''
    :stability: deprecated
    '''

    FALL_BACK = "FALL_BACK"
    '''(deprecated) Will fall back to CloudFormation when a non-hotswappable change is detected.

    :stability: deprecated
    '''
    HOTSWAP_ONLY = "HOTSWAP_ONLY"
    '''(deprecated) Will not fall back to CloudFormation when a non-hotswappable change is detected.

    :stability: deprecated
    '''
    FULL_DEPLOYMENT = "FULL_DEPLOYMENT"
    '''(deprecated) Will not attempt to hotswap anything and instead go straight to CloudFormation.

    :stability: deprecated
    '''


@jsii.interface(jsii_type="@aws-cdk/cli-lib-alpha.IAwsCdkCli")
class IAwsCdkCli(typing_extensions.Protocol):
    '''(deprecated) AWS CDK CLI operations.

    :stability: deprecated
    '''

    @jsii.member(jsii_name="bootstrap")
    def bootstrap(
        self,
        *,
        bootstrap_bucket_name: typing.Optional[builtins.str] = None,
        bootstrap_customer_key: typing.Optional[builtins.str] = None,
        bootstrap_kms_key_id: typing.Optional[builtins.str] = None,
        cfn_execution_policy: typing.Optional[builtins.str] = None,
        custom_permissions_boundary: typing.Optional[builtins.str] = None,
        environments: typing.Optional[typing.Sequence[builtins.str]] = None,
        example_permissions_boundary: typing.Optional[builtins.bool] = None,
        execute: typing.Optional[builtins.bool] = None,
        force: typing.Optional[builtins.bool] = None,
        public_access_block_configuration: typing.Optional[builtins.str] = None,
        qualifier: typing.Optional[builtins.str] = None,
        show_template: typing.Optional[builtins.bool] = None,
        template: typing.Optional[builtins.str] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        toolkit_stack_name: typing.Optional[builtins.str] = None,
        trust: typing.Optional[builtins.str] = None,
        trust_for_lookup: typing.Optional[builtins.str] = None,
        use_previous_parameters: typing.Optional[builtins.bool] = None,
        asset_metadata: typing.Optional[builtins.bool] = None,
        ca_bundle_path: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.bool] = None,
        context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        debug: typing.Optional[builtins.bool] = None,
        ec2_creds: typing.Optional[builtins.bool] = None,
        ignore_errors: typing.Optional[builtins.bool] = None,
        json: typing.Optional[builtins.bool] = None,
        lookups: typing.Optional[builtins.bool] = None,
        notices: typing.Optional[builtins.bool] = None,
        path_metadata: typing.Optional[builtins.bool] = None,
        profile: typing.Optional[builtins.str] = None,
        proxy: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        stacks: typing.Optional[typing.Sequence[builtins.str]] = None,
        staging: typing.Optional[builtins.bool] = None,
        strict: typing.Optional[builtins.bool] = None,
        trace: typing.Optional[builtins.bool] = None,
        verbose: typing.Optional[builtins.bool] = None,
        version_reporting: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(deprecated) cdk bootstrap.

        :param bootstrap_bucket_name: (deprecated) The name of the CDK toolkit bucket; bucket will be created and must not exist Default: - auto-generated CloudFormation name
        :param bootstrap_customer_key: (deprecated) Create a Customer Master Key (CMK) for the bootstrap bucket (you will be charged but can customize permissions, modern bootstrapping only). Default: undefined
        :param bootstrap_kms_key_id: (deprecated) AWS KMS master key ID used for the SSE-KMS encryption. Default: undefined
        :param cfn_execution_policy: (deprecated) The Managed Policy ARNs that should be attached to the role performing deployments into this environment (may be repeated, modern bootstrapping only). Default: - none
        :param custom_permissions_boundary: (deprecated) Use the permissions boundary specified by name. Default: undefined
        :param environments: (deprecated) The target AWS environments to deploy the bootstrap stack to. Uses the following format: ``aws://<account-id>/<region>`` Default: - Bootstrap all environments referenced in the CDK app or determine an environment from local configuration.
        :param example_permissions_boundary: (deprecated) Use the example permissions boundary. Default: undefined
        :param execute: (deprecated) Whether to execute ChangeSet (--no-execute will NOT execute the ChangeSet). Default: true
        :param force: (deprecated) Always bootstrap even if it would downgrade template version. Default: false
        :param public_access_block_configuration: (deprecated) Block public access configuration on CDK toolkit bucket (enabled by default). Default: undefined
        :param qualifier: (deprecated) String which must be unique for each bootstrap stack. You must configure it on your CDK app if you change this from the default. Default: undefined
        :param show_template: (deprecated) Instead of actual bootstrapping, print the current CLI's bootstrapping template to stdout for customization. Default: false
        :param template: (deprecated) Use the template from the given file instead of the built-in one (use --show-template to obtain an example).
        :param termination_protection: (deprecated) Toggle CloudFormation termination protection on the bootstrap stacks. Default: false
        :param toolkit_stack_name: (deprecated) The name of the CDK toolkit stack to create.
        :param trust: (deprecated) The AWS account IDs that should be trusted to perform deployments into this environment (may be repeated, modern bootstrapping only). Default: undefined
        :param trust_for_lookup: (deprecated) The AWS account IDs that should be trusted to look up values in this environment (may be repeated, modern bootstrapping only). Default: undefined
        :param use_previous_parameters: (deprecated) Use previous values for existing parameters (you must specify all parameters on every deployment if this is disabled). Default: true
        :param asset_metadata: (deprecated) Include "aws:asset:*" CloudFormation metadata for resources that use assets. Default: true
        :param ca_bundle_path: (deprecated) Path to CA certificate to use when validating HTTPS requests. Default: - read from AWS_CA_BUNDLE environment variable
        :param color: (deprecated) Show colors and other style from console output. Default: - ``true`` unless the environment variable ``NO_COLOR`` is set
        :param context: (deprecated) Additional context. Default: - no additional context
        :param debug: (deprecated) enable emission of additional debugging information, such as creation stack traces of tokens. Default: false
        :param ec2_creds: (deprecated) Force trying to fetch EC2 instance credentials. Default: - guess EC2 instance status
        :param ignore_errors: (deprecated) Ignores synthesis errors, which will likely produce an invalid output. Default: false
        :param json: (deprecated) Use JSON output instead of YAML when templates are printed to STDOUT. Default: false
        :param lookups: (deprecated) Perform context lookups. Synthesis fails if this is disabled and context lookups need to be performed Default: true
        :param notices: (deprecated) Show relevant notices. Default: true
        :param path_metadata: (deprecated) Include "aws:cdk:path" CloudFormation metadata for each resource. Default: true
        :param profile: (deprecated) Use the indicated AWS profile as the default environment. Default: - no profile is used
        :param proxy: (deprecated) Use the indicated proxy. Will read from HTTPS_PROXY environment if specified Default: - no proxy
        :param role_arn: (deprecated) Role to pass to CloudFormation for deployment. Default: - use the bootstrap cfn-exec role
        :param stacks: (deprecated) List of stacks to deploy. Default: - all stacks
        :param staging: (deprecated) Copy assets to the output directory. Needed for local debugging the source files with SAM CLI Default: false
        :param strict: (deprecated) Do not construct stacks with warnings. Default: false
        :param trace: (deprecated) Print trace for stack warnings. Default: false
        :param verbose: (deprecated) show debug logs. Default: false
        :param version_reporting: (deprecated) Include "AWS::CDK::Metadata" resource in synthesized templates. Default: true

        :stability: deprecated
        '''
        ...

    @jsii.member(jsii_name="deploy")
    def deploy(
        self,
        *,
        asset_parallelism: typing.Optional[builtins.bool] = None,
        asset_prebuild: typing.Optional[builtins.bool] = None,
        change_set_name: typing.Optional[builtins.str] = None,
        ci: typing.Optional[builtins.bool] = None,
        concurrency: typing.Optional[jsii.Number] = None,
        exclusively: typing.Optional[builtins.bool] = None,
        execute: typing.Optional[builtins.bool] = None,
        force: typing.Optional[builtins.bool] = None,
        hotswap: typing.Optional[HotswapMode] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        outputs_file: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        progress: typing.Optional["StackActivityProgress"] = None,
        require_approval: typing.Optional["RequireApproval"] = None,
        reuse_assets: typing.Optional[typing.Sequence[builtins.str]] = None,
        rollback: typing.Optional[builtins.bool] = None,
        toolkit_stack_name: typing.Optional[builtins.str] = None,
        use_previous_parameters: typing.Optional[builtins.bool] = None,
        asset_metadata: typing.Optional[builtins.bool] = None,
        ca_bundle_path: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.bool] = None,
        context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        debug: typing.Optional[builtins.bool] = None,
        ec2_creds: typing.Optional[builtins.bool] = None,
        ignore_errors: typing.Optional[builtins.bool] = None,
        json: typing.Optional[builtins.bool] = None,
        lookups: typing.Optional[builtins.bool] = None,
        notices: typing.Optional[builtins.bool] = None,
        path_metadata: typing.Optional[builtins.bool] = None,
        profile: typing.Optional[builtins.str] = None,
        proxy: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        stacks: typing.Optional[typing.Sequence[builtins.str]] = None,
        staging: typing.Optional[builtins.bool] = None,
        strict: typing.Optional[builtins.bool] = None,
        trace: typing.Optional[builtins.bool] = None,
        verbose: typing.Optional[builtins.bool] = None,
        version_reporting: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(deprecated) cdk deploy.

        :param asset_parallelism: (deprecated) Whether to build/publish assets in parallel. Default: false
        :param asset_prebuild: (deprecated) Whether to build all assets before deploying the first stack (useful for failing Docker builds). Default: true
        :param change_set_name: (deprecated) Optional name to use for the CloudFormation change set. If not provided, a name will be generated automatically. Default: - auto generate a name
        :param ci: (deprecated) Whether we are on a CI system. Default: - ``false`` unless the environment variable ``CI`` is set
        :param concurrency: (deprecated) Maximum number of simultaneous deployments (dependency permitting) to execute. Default: 1
        :param exclusively: (deprecated) Only perform action on the given stack. Default: false
        :param execute: (deprecated) Whether to execute the ChangeSet Not providing ``execute`` parameter will result in execution of ChangeSet. Default: true
        :param force: (deprecated) Always deploy, even if templates are identical. Default: false
        :param hotswap: 
        :param notification_arns: (deprecated) ARNs of SNS topics that CloudFormation will notify with stack related events. Default: - no notifications
        :param outputs_file: (deprecated) Path to file where stack outputs will be written after a successful deploy as JSON. Default: - Outputs are not written to any file
        :param parameters: (deprecated) Additional parameters for CloudFormation at deploy time. Default: {}
        :param progress: (deprecated) Display mode for stack activity events. The default in the CLI is StackActivityProgress.BAR. But since this is an API it makes more sense to set the default to StackActivityProgress.EVENTS Default: StackActivityProgress.EVENTS
        :param require_approval: (deprecated) What kind of security changes require approval. Default: RequireApproval.NEVER
        :param reuse_assets: (deprecated) Reuse the assets with the given asset IDs. Default: - do not reuse assets
        :param rollback: (deprecated) Rollback failed deployments. Default: true
        :param toolkit_stack_name: (deprecated) Name of the toolkit stack to use/deploy. Default: CDKToolkit
        :param use_previous_parameters: (deprecated) Use previous values for unspecified parameters. If not set, all parameters must be specified for every deployment. Default: true
        :param asset_metadata: (deprecated) Include "aws:asset:*" CloudFormation metadata for resources that use assets. Default: true
        :param ca_bundle_path: (deprecated) Path to CA certificate to use when validating HTTPS requests. Default: - read from AWS_CA_BUNDLE environment variable
        :param color: (deprecated) Show colors and other style from console output. Default: - ``true`` unless the environment variable ``NO_COLOR`` is set
        :param context: (deprecated) Additional context. Default: - no additional context
        :param debug: (deprecated) enable emission of additional debugging information, such as creation stack traces of tokens. Default: false
        :param ec2_creds: (deprecated) Force trying to fetch EC2 instance credentials. Default: - guess EC2 instance status
        :param ignore_errors: (deprecated) Ignores synthesis errors, which will likely produce an invalid output. Default: false
        :param json: (deprecated) Use JSON output instead of YAML when templates are printed to STDOUT. Default: false
        :param lookups: (deprecated) Perform context lookups. Synthesis fails if this is disabled and context lookups need to be performed Default: true
        :param notices: (deprecated) Show relevant notices. Default: true
        :param path_metadata: (deprecated) Include "aws:cdk:path" CloudFormation metadata for each resource. Default: true
        :param profile: (deprecated) Use the indicated AWS profile as the default environment. Default: - no profile is used
        :param proxy: (deprecated) Use the indicated proxy. Will read from HTTPS_PROXY environment if specified Default: - no proxy
        :param role_arn: (deprecated) Role to pass to CloudFormation for deployment. Default: - use the bootstrap cfn-exec role
        :param stacks: (deprecated) List of stacks to deploy. Default: - all stacks
        :param staging: (deprecated) Copy assets to the output directory. Needed for local debugging the source files with SAM CLI Default: false
        :param strict: (deprecated) Do not construct stacks with warnings. Default: false
        :param trace: (deprecated) Print trace for stack warnings. Default: false
        :param verbose: (deprecated) show debug logs. Default: false
        :param version_reporting: (deprecated) Include "AWS::CDK::Metadata" resource in synthesized templates. Default: true

        :stability: deprecated
        '''
        ...

    @jsii.member(jsii_name="destroy")
    def destroy(
        self,
        *,
        exclusively: typing.Optional[builtins.bool] = None,
        require_approval: typing.Optional[builtins.bool] = None,
        asset_metadata: typing.Optional[builtins.bool] = None,
        ca_bundle_path: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.bool] = None,
        context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        debug: typing.Optional[builtins.bool] = None,
        ec2_creds: typing.Optional[builtins.bool] = None,
        ignore_errors: typing.Optional[builtins.bool] = None,
        json: typing.Optional[builtins.bool] = None,
        lookups: typing.Optional[builtins.bool] = None,
        notices: typing.Optional[builtins.bool] = None,
        path_metadata: typing.Optional[builtins.bool] = None,
        profile: typing.Optional[builtins.str] = None,
        proxy: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        stacks: typing.Optional[typing.Sequence[builtins.str]] = None,
        staging: typing.Optional[builtins.bool] = None,
        strict: typing.Optional[builtins.bool] = None,
        trace: typing.Optional[builtins.bool] = None,
        verbose: typing.Optional[builtins.bool] = None,
        version_reporting: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(deprecated) cdk destroy.

        :param exclusively: (deprecated) Only destroy the given stack. Default: false
        :param require_approval: (deprecated) Should the script prompt for approval before destroying stacks. Default: false
        :param asset_metadata: (deprecated) Include "aws:asset:*" CloudFormation metadata for resources that use assets. Default: true
        :param ca_bundle_path: (deprecated) Path to CA certificate to use when validating HTTPS requests. Default: - read from AWS_CA_BUNDLE environment variable
        :param color: (deprecated) Show colors and other style from console output. Default: - ``true`` unless the environment variable ``NO_COLOR`` is set
        :param context: (deprecated) Additional context. Default: - no additional context
        :param debug: (deprecated) enable emission of additional debugging information, such as creation stack traces of tokens. Default: false
        :param ec2_creds: (deprecated) Force trying to fetch EC2 instance credentials. Default: - guess EC2 instance status
        :param ignore_errors: (deprecated) Ignores synthesis errors, which will likely produce an invalid output. Default: false
        :param json: (deprecated) Use JSON output instead of YAML when templates are printed to STDOUT. Default: false
        :param lookups: (deprecated) Perform context lookups. Synthesis fails if this is disabled and context lookups need to be performed Default: true
        :param notices: (deprecated) Show relevant notices. Default: true
        :param path_metadata: (deprecated) Include "aws:cdk:path" CloudFormation metadata for each resource. Default: true
        :param profile: (deprecated) Use the indicated AWS profile as the default environment. Default: - no profile is used
        :param proxy: (deprecated) Use the indicated proxy. Will read from HTTPS_PROXY environment if specified Default: - no proxy
        :param role_arn: (deprecated) Role to pass to CloudFormation for deployment. Default: - use the bootstrap cfn-exec role
        :param stacks: (deprecated) List of stacks to deploy. Default: - all stacks
        :param staging: (deprecated) Copy assets to the output directory. Needed for local debugging the source files with SAM CLI Default: false
        :param strict: (deprecated) Do not construct stacks with warnings. Default: false
        :param trace: (deprecated) Print trace for stack warnings. Default: false
        :param verbose: (deprecated) show debug logs. Default: false
        :param version_reporting: (deprecated) Include "AWS::CDK::Metadata" resource in synthesized templates. Default: true

        :stability: deprecated
        '''
        ...

    @jsii.member(jsii_name="list")
    def list(
        self,
        *,
        long: typing.Optional[builtins.bool] = None,
        asset_metadata: typing.Optional[builtins.bool] = None,
        ca_bundle_path: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.bool] = None,
        context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        debug: typing.Optional[builtins.bool] = None,
        ec2_creds: typing.Optional[builtins.bool] = None,
        ignore_errors: typing.Optional[builtins.bool] = None,
        json: typing.Optional[builtins.bool] = None,
        lookups: typing.Optional[builtins.bool] = None,
        notices: typing.Optional[builtins.bool] = None,
        path_metadata: typing.Optional[builtins.bool] = None,
        profile: typing.Optional[builtins.str] = None,
        proxy: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        stacks: typing.Optional[typing.Sequence[builtins.str]] = None,
        staging: typing.Optional[builtins.bool] = None,
        strict: typing.Optional[builtins.bool] = None,
        trace: typing.Optional[builtins.bool] = None,
        verbose: typing.Optional[builtins.bool] = None,
        version_reporting: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(deprecated) cdk list.

        :param long: (deprecated) Display environment information for each stack. Default: false
        :param asset_metadata: (deprecated) Include "aws:asset:*" CloudFormation metadata for resources that use assets. Default: true
        :param ca_bundle_path: (deprecated) Path to CA certificate to use when validating HTTPS requests. Default: - read from AWS_CA_BUNDLE environment variable
        :param color: (deprecated) Show colors and other style from console output. Default: - ``true`` unless the environment variable ``NO_COLOR`` is set
        :param context: (deprecated) Additional context. Default: - no additional context
        :param debug: (deprecated) enable emission of additional debugging information, such as creation stack traces of tokens. Default: false
        :param ec2_creds: (deprecated) Force trying to fetch EC2 instance credentials. Default: - guess EC2 instance status
        :param ignore_errors: (deprecated) Ignores synthesis errors, which will likely produce an invalid output. Default: false
        :param json: (deprecated) Use JSON output instead of YAML when templates are printed to STDOUT. Default: false
        :param lookups: (deprecated) Perform context lookups. Synthesis fails if this is disabled and context lookups need to be performed Default: true
        :param notices: (deprecated) Show relevant notices. Default: true
        :param path_metadata: (deprecated) Include "aws:cdk:path" CloudFormation metadata for each resource. Default: true
        :param profile: (deprecated) Use the indicated AWS profile as the default environment. Default: - no profile is used
        :param proxy: (deprecated) Use the indicated proxy. Will read from HTTPS_PROXY environment if specified Default: - no proxy
        :param role_arn: (deprecated) Role to pass to CloudFormation for deployment. Default: - use the bootstrap cfn-exec role
        :param stacks: (deprecated) List of stacks to deploy. Default: - all stacks
        :param staging: (deprecated) Copy assets to the output directory. Needed for local debugging the source files with SAM CLI Default: false
        :param strict: (deprecated) Do not construct stacks with warnings. Default: false
        :param trace: (deprecated) Print trace for stack warnings. Default: false
        :param verbose: (deprecated) show debug logs. Default: false
        :param version_reporting: (deprecated) Include "AWS::CDK::Metadata" resource in synthesized templates. Default: true

        :stability: deprecated
        '''
        ...

    @jsii.member(jsii_name="synth")
    def synth(
        self,
        *,
        exclusively: typing.Optional[builtins.bool] = None,
        quiet: typing.Optional[builtins.bool] = None,
        validation: typing.Optional[builtins.bool] = None,
        asset_metadata: typing.Optional[builtins.bool] = None,
        ca_bundle_path: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.bool] = None,
        context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        debug: typing.Optional[builtins.bool] = None,
        ec2_creds: typing.Optional[builtins.bool] = None,
        ignore_errors: typing.Optional[builtins.bool] = None,
        json: typing.Optional[builtins.bool] = None,
        lookups: typing.Optional[builtins.bool] = None,
        notices: typing.Optional[builtins.bool] = None,
        path_metadata: typing.Optional[builtins.bool] = None,
        profile: typing.Optional[builtins.str] = None,
        proxy: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        stacks: typing.Optional[typing.Sequence[builtins.str]] = None,
        staging: typing.Optional[builtins.bool] = None,
        strict: typing.Optional[builtins.bool] = None,
        trace: typing.Optional[builtins.bool] = None,
        verbose: typing.Optional[builtins.bool] = None,
        version_reporting: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(deprecated) cdk synth.

        :param exclusively: (deprecated) Only synthesize the given stack. Default: false
        :param quiet: (deprecated) Do not output CloudFormation Template to stdout. Default: false;
        :param validation: (deprecated) After synthesis, validate stacks with the "validateOnSynth" attribute set (can also be controlled with CDK_VALIDATION). Default: true;
        :param asset_metadata: (deprecated) Include "aws:asset:*" CloudFormation metadata for resources that use assets. Default: true
        :param ca_bundle_path: (deprecated) Path to CA certificate to use when validating HTTPS requests. Default: - read from AWS_CA_BUNDLE environment variable
        :param color: (deprecated) Show colors and other style from console output. Default: - ``true`` unless the environment variable ``NO_COLOR`` is set
        :param context: (deprecated) Additional context. Default: - no additional context
        :param debug: (deprecated) enable emission of additional debugging information, such as creation stack traces of tokens. Default: false
        :param ec2_creds: (deprecated) Force trying to fetch EC2 instance credentials. Default: - guess EC2 instance status
        :param ignore_errors: (deprecated) Ignores synthesis errors, which will likely produce an invalid output. Default: false
        :param json: (deprecated) Use JSON output instead of YAML when templates are printed to STDOUT. Default: false
        :param lookups: (deprecated) Perform context lookups. Synthesis fails if this is disabled and context lookups need to be performed Default: true
        :param notices: (deprecated) Show relevant notices. Default: true
        :param path_metadata: (deprecated) Include "aws:cdk:path" CloudFormation metadata for each resource. Default: true
        :param profile: (deprecated) Use the indicated AWS profile as the default environment. Default: - no profile is used
        :param proxy: (deprecated) Use the indicated proxy. Will read from HTTPS_PROXY environment if specified Default: - no proxy
        :param role_arn: (deprecated) Role to pass to CloudFormation for deployment. Default: - use the bootstrap cfn-exec role
        :param stacks: (deprecated) List of stacks to deploy. Default: - all stacks
        :param staging: (deprecated) Copy assets to the output directory. Needed for local debugging the source files with SAM CLI Default: false
        :param strict: (deprecated) Do not construct stacks with warnings. Default: false
        :param trace: (deprecated) Print trace for stack warnings. Default: false
        :param verbose: (deprecated) show debug logs. Default: false
        :param version_reporting: (deprecated) Include "AWS::CDK::Metadata" resource in synthesized templates. Default: true

        :stability: deprecated
        '''
        ...


class _IAwsCdkCliProxy:
    '''(deprecated) AWS CDK CLI operations.

    :stability: deprecated
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/cli-lib-alpha.IAwsCdkCli"

    @jsii.member(jsii_name="bootstrap")
    def bootstrap(
        self,
        *,
        bootstrap_bucket_name: typing.Optional[builtins.str] = None,
        bootstrap_customer_key: typing.Optional[builtins.str] = None,
        bootstrap_kms_key_id: typing.Optional[builtins.str] = None,
        cfn_execution_policy: typing.Optional[builtins.str] = None,
        custom_permissions_boundary: typing.Optional[builtins.str] = None,
        environments: typing.Optional[typing.Sequence[builtins.str]] = None,
        example_permissions_boundary: typing.Optional[builtins.bool] = None,
        execute: typing.Optional[builtins.bool] = None,
        force: typing.Optional[builtins.bool] = None,
        public_access_block_configuration: typing.Optional[builtins.str] = None,
        qualifier: typing.Optional[builtins.str] = None,
        show_template: typing.Optional[builtins.bool] = None,
        template: typing.Optional[builtins.str] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        toolkit_stack_name: typing.Optional[builtins.str] = None,
        trust: typing.Optional[builtins.str] = None,
        trust_for_lookup: typing.Optional[builtins.str] = None,
        use_previous_parameters: typing.Optional[builtins.bool] = None,
        asset_metadata: typing.Optional[builtins.bool] = None,
        ca_bundle_path: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.bool] = None,
        context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        debug: typing.Optional[builtins.bool] = None,
        ec2_creds: typing.Optional[builtins.bool] = None,
        ignore_errors: typing.Optional[builtins.bool] = None,
        json: typing.Optional[builtins.bool] = None,
        lookups: typing.Optional[builtins.bool] = None,
        notices: typing.Optional[builtins.bool] = None,
        path_metadata: typing.Optional[builtins.bool] = None,
        profile: typing.Optional[builtins.str] = None,
        proxy: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        stacks: typing.Optional[typing.Sequence[builtins.str]] = None,
        staging: typing.Optional[builtins.bool] = None,
        strict: typing.Optional[builtins.bool] = None,
        trace: typing.Optional[builtins.bool] = None,
        verbose: typing.Optional[builtins.bool] = None,
        version_reporting: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(deprecated) cdk bootstrap.

        :param bootstrap_bucket_name: (deprecated) The name of the CDK toolkit bucket; bucket will be created and must not exist Default: - auto-generated CloudFormation name
        :param bootstrap_customer_key: (deprecated) Create a Customer Master Key (CMK) for the bootstrap bucket (you will be charged but can customize permissions, modern bootstrapping only). Default: undefined
        :param bootstrap_kms_key_id: (deprecated) AWS KMS master key ID used for the SSE-KMS encryption. Default: undefined
        :param cfn_execution_policy: (deprecated) The Managed Policy ARNs that should be attached to the role performing deployments into this environment (may be repeated, modern bootstrapping only). Default: - none
        :param custom_permissions_boundary: (deprecated) Use the permissions boundary specified by name. Default: undefined
        :param environments: (deprecated) The target AWS environments to deploy the bootstrap stack to. Uses the following format: ``aws://<account-id>/<region>`` Default: - Bootstrap all environments referenced in the CDK app or determine an environment from local configuration.
        :param example_permissions_boundary: (deprecated) Use the example permissions boundary. Default: undefined
        :param execute: (deprecated) Whether to execute ChangeSet (--no-execute will NOT execute the ChangeSet). Default: true
        :param force: (deprecated) Always bootstrap even if it would downgrade template version. Default: false
        :param public_access_block_configuration: (deprecated) Block public access configuration on CDK toolkit bucket (enabled by default). Default: undefined
        :param qualifier: (deprecated) String which must be unique for each bootstrap stack. You must configure it on your CDK app if you change this from the default. Default: undefined
        :param show_template: (deprecated) Instead of actual bootstrapping, print the current CLI's bootstrapping template to stdout for customization. Default: false
        :param template: (deprecated) Use the template from the given file instead of the built-in one (use --show-template to obtain an example).
        :param termination_protection: (deprecated) Toggle CloudFormation termination protection on the bootstrap stacks. Default: false
        :param toolkit_stack_name: (deprecated) The name of the CDK toolkit stack to create.
        :param trust: (deprecated) The AWS account IDs that should be trusted to perform deployments into this environment (may be repeated, modern bootstrapping only). Default: undefined
        :param trust_for_lookup: (deprecated) The AWS account IDs that should be trusted to look up values in this environment (may be repeated, modern bootstrapping only). Default: undefined
        :param use_previous_parameters: (deprecated) Use previous values for existing parameters (you must specify all parameters on every deployment if this is disabled). Default: true
        :param asset_metadata: (deprecated) Include "aws:asset:*" CloudFormation metadata for resources that use assets. Default: true
        :param ca_bundle_path: (deprecated) Path to CA certificate to use when validating HTTPS requests. Default: - read from AWS_CA_BUNDLE environment variable
        :param color: (deprecated) Show colors and other style from console output. Default: - ``true`` unless the environment variable ``NO_COLOR`` is set
        :param context: (deprecated) Additional context. Default: - no additional context
        :param debug: (deprecated) enable emission of additional debugging information, such as creation stack traces of tokens. Default: false
        :param ec2_creds: (deprecated) Force trying to fetch EC2 instance credentials. Default: - guess EC2 instance status
        :param ignore_errors: (deprecated) Ignores synthesis errors, which will likely produce an invalid output. Default: false
        :param json: (deprecated) Use JSON output instead of YAML when templates are printed to STDOUT. Default: false
        :param lookups: (deprecated) Perform context lookups. Synthesis fails if this is disabled and context lookups need to be performed Default: true
        :param notices: (deprecated) Show relevant notices. Default: true
        :param path_metadata: (deprecated) Include "aws:cdk:path" CloudFormation metadata for each resource. Default: true
        :param profile: (deprecated) Use the indicated AWS profile as the default environment. Default: - no profile is used
        :param proxy: (deprecated) Use the indicated proxy. Will read from HTTPS_PROXY environment if specified Default: - no proxy
        :param role_arn: (deprecated) Role to pass to CloudFormation for deployment. Default: - use the bootstrap cfn-exec role
        :param stacks: (deprecated) List of stacks to deploy. Default: - all stacks
        :param staging: (deprecated) Copy assets to the output directory. Needed for local debugging the source files with SAM CLI Default: false
        :param strict: (deprecated) Do not construct stacks with warnings. Default: false
        :param trace: (deprecated) Print trace for stack warnings. Default: false
        :param verbose: (deprecated) show debug logs. Default: false
        :param version_reporting: (deprecated) Include "AWS::CDK::Metadata" resource in synthesized templates. Default: true

        :stability: deprecated
        '''
        options = BootstrapOptions(
            bootstrap_bucket_name=bootstrap_bucket_name,
            bootstrap_customer_key=bootstrap_customer_key,
            bootstrap_kms_key_id=bootstrap_kms_key_id,
            cfn_execution_policy=cfn_execution_policy,
            custom_permissions_boundary=custom_permissions_boundary,
            environments=environments,
            example_permissions_boundary=example_permissions_boundary,
            execute=execute,
            force=force,
            public_access_block_configuration=public_access_block_configuration,
            qualifier=qualifier,
            show_template=show_template,
            template=template,
            termination_protection=termination_protection,
            toolkit_stack_name=toolkit_stack_name,
            trust=trust,
            trust_for_lookup=trust_for_lookup,
            use_previous_parameters=use_previous_parameters,
            asset_metadata=asset_metadata,
            ca_bundle_path=ca_bundle_path,
            color=color,
            context=context,
            debug=debug,
            ec2_creds=ec2_creds,
            ignore_errors=ignore_errors,
            json=json,
            lookups=lookups,
            notices=notices,
            path_metadata=path_metadata,
            profile=profile,
            proxy=proxy,
            role_arn=role_arn,
            stacks=stacks,
            staging=staging,
            strict=strict,
            trace=trace,
            verbose=verbose,
            version_reporting=version_reporting,
        )

        return typing.cast(None, jsii.invoke(self, "bootstrap", [options]))

    @jsii.member(jsii_name="deploy")
    def deploy(
        self,
        *,
        asset_parallelism: typing.Optional[builtins.bool] = None,
        asset_prebuild: typing.Optional[builtins.bool] = None,
        change_set_name: typing.Optional[builtins.str] = None,
        ci: typing.Optional[builtins.bool] = None,
        concurrency: typing.Optional[jsii.Number] = None,
        exclusively: typing.Optional[builtins.bool] = None,
        execute: typing.Optional[builtins.bool] = None,
        force: typing.Optional[builtins.bool] = None,
        hotswap: typing.Optional[HotswapMode] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        outputs_file: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        progress: typing.Optional["StackActivityProgress"] = None,
        require_approval: typing.Optional["RequireApproval"] = None,
        reuse_assets: typing.Optional[typing.Sequence[builtins.str]] = None,
        rollback: typing.Optional[builtins.bool] = None,
        toolkit_stack_name: typing.Optional[builtins.str] = None,
        use_previous_parameters: typing.Optional[builtins.bool] = None,
        asset_metadata: typing.Optional[builtins.bool] = None,
        ca_bundle_path: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.bool] = None,
        context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        debug: typing.Optional[builtins.bool] = None,
        ec2_creds: typing.Optional[builtins.bool] = None,
        ignore_errors: typing.Optional[builtins.bool] = None,
        json: typing.Optional[builtins.bool] = None,
        lookups: typing.Optional[builtins.bool] = None,
        notices: typing.Optional[builtins.bool] = None,
        path_metadata: typing.Optional[builtins.bool] = None,
        profile: typing.Optional[builtins.str] = None,
        proxy: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        stacks: typing.Optional[typing.Sequence[builtins.str]] = None,
        staging: typing.Optional[builtins.bool] = None,
        strict: typing.Optional[builtins.bool] = None,
        trace: typing.Optional[builtins.bool] = None,
        verbose: typing.Optional[builtins.bool] = None,
        version_reporting: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(deprecated) cdk deploy.

        :param asset_parallelism: (deprecated) Whether to build/publish assets in parallel. Default: false
        :param asset_prebuild: (deprecated) Whether to build all assets before deploying the first stack (useful for failing Docker builds). Default: true
        :param change_set_name: (deprecated) Optional name to use for the CloudFormation change set. If not provided, a name will be generated automatically. Default: - auto generate a name
        :param ci: (deprecated) Whether we are on a CI system. Default: - ``false`` unless the environment variable ``CI`` is set
        :param concurrency: (deprecated) Maximum number of simultaneous deployments (dependency permitting) to execute. Default: 1
        :param exclusively: (deprecated) Only perform action on the given stack. Default: false
        :param execute: (deprecated) Whether to execute the ChangeSet Not providing ``execute`` parameter will result in execution of ChangeSet. Default: true
        :param force: (deprecated) Always deploy, even if templates are identical. Default: false
        :param hotswap: 
        :param notification_arns: (deprecated) ARNs of SNS topics that CloudFormation will notify with stack related events. Default: - no notifications
        :param outputs_file: (deprecated) Path to file where stack outputs will be written after a successful deploy as JSON. Default: - Outputs are not written to any file
        :param parameters: (deprecated) Additional parameters for CloudFormation at deploy time. Default: {}
        :param progress: (deprecated) Display mode for stack activity events. The default in the CLI is StackActivityProgress.BAR. But since this is an API it makes more sense to set the default to StackActivityProgress.EVENTS Default: StackActivityProgress.EVENTS
        :param require_approval: (deprecated) What kind of security changes require approval. Default: RequireApproval.NEVER
        :param reuse_assets: (deprecated) Reuse the assets with the given asset IDs. Default: - do not reuse assets
        :param rollback: (deprecated) Rollback failed deployments. Default: true
        :param toolkit_stack_name: (deprecated) Name of the toolkit stack to use/deploy. Default: CDKToolkit
        :param use_previous_parameters: (deprecated) Use previous values for unspecified parameters. If not set, all parameters must be specified for every deployment. Default: true
        :param asset_metadata: (deprecated) Include "aws:asset:*" CloudFormation metadata for resources that use assets. Default: true
        :param ca_bundle_path: (deprecated) Path to CA certificate to use when validating HTTPS requests. Default: - read from AWS_CA_BUNDLE environment variable
        :param color: (deprecated) Show colors and other style from console output. Default: - ``true`` unless the environment variable ``NO_COLOR`` is set
        :param context: (deprecated) Additional context. Default: - no additional context
        :param debug: (deprecated) enable emission of additional debugging information, such as creation stack traces of tokens. Default: false
        :param ec2_creds: (deprecated) Force trying to fetch EC2 instance credentials. Default: - guess EC2 instance status
        :param ignore_errors: (deprecated) Ignores synthesis errors, which will likely produce an invalid output. Default: false
        :param json: (deprecated) Use JSON output instead of YAML when templates are printed to STDOUT. Default: false
        :param lookups: (deprecated) Perform context lookups. Synthesis fails if this is disabled and context lookups need to be performed Default: true
        :param notices: (deprecated) Show relevant notices. Default: true
        :param path_metadata: (deprecated) Include "aws:cdk:path" CloudFormation metadata for each resource. Default: true
        :param profile: (deprecated) Use the indicated AWS profile as the default environment. Default: - no profile is used
        :param proxy: (deprecated) Use the indicated proxy. Will read from HTTPS_PROXY environment if specified Default: - no proxy
        :param role_arn: (deprecated) Role to pass to CloudFormation for deployment. Default: - use the bootstrap cfn-exec role
        :param stacks: (deprecated) List of stacks to deploy. Default: - all stacks
        :param staging: (deprecated) Copy assets to the output directory. Needed for local debugging the source files with SAM CLI Default: false
        :param strict: (deprecated) Do not construct stacks with warnings. Default: false
        :param trace: (deprecated) Print trace for stack warnings. Default: false
        :param verbose: (deprecated) show debug logs. Default: false
        :param version_reporting: (deprecated) Include "AWS::CDK::Metadata" resource in synthesized templates. Default: true

        :stability: deprecated
        '''
        options = DeployOptions(
            asset_parallelism=asset_parallelism,
            asset_prebuild=asset_prebuild,
            change_set_name=change_set_name,
            ci=ci,
            concurrency=concurrency,
            exclusively=exclusively,
            execute=execute,
            force=force,
            hotswap=hotswap,
            notification_arns=notification_arns,
            outputs_file=outputs_file,
            parameters=parameters,
            progress=progress,
            require_approval=require_approval,
            reuse_assets=reuse_assets,
            rollback=rollback,
            toolkit_stack_name=toolkit_stack_name,
            use_previous_parameters=use_previous_parameters,
            asset_metadata=asset_metadata,
            ca_bundle_path=ca_bundle_path,
            color=color,
            context=context,
            debug=debug,
            ec2_creds=ec2_creds,
            ignore_errors=ignore_errors,
            json=json,
            lookups=lookups,
            notices=notices,
            path_metadata=path_metadata,
            profile=profile,
            proxy=proxy,
            role_arn=role_arn,
            stacks=stacks,
            staging=staging,
            strict=strict,
            trace=trace,
            verbose=verbose,
            version_reporting=version_reporting,
        )

        return typing.cast(None, jsii.invoke(self, "deploy", [options]))

    @jsii.member(jsii_name="destroy")
    def destroy(
        self,
        *,
        exclusively: typing.Optional[builtins.bool] = None,
        require_approval: typing.Optional[builtins.bool] = None,
        asset_metadata: typing.Optional[builtins.bool] = None,
        ca_bundle_path: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.bool] = None,
        context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        debug: typing.Optional[builtins.bool] = None,
        ec2_creds: typing.Optional[builtins.bool] = None,
        ignore_errors: typing.Optional[builtins.bool] = None,
        json: typing.Optional[builtins.bool] = None,
        lookups: typing.Optional[builtins.bool] = None,
        notices: typing.Optional[builtins.bool] = None,
        path_metadata: typing.Optional[builtins.bool] = None,
        profile: typing.Optional[builtins.str] = None,
        proxy: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        stacks: typing.Optional[typing.Sequence[builtins.str]] = None,
        staging: typing.Optional[builtins.bool] = None,
        strict: typing.Optional[builtins.bool] = None,
        trace: typing.Optional[builtins.bool] = None,
        verbose: typing.Optional[builtins.bool] = None,
        version_reporting: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(deprecated) cdk destroy.

        :param exclusively: (deprecated) Only destroy the given stack. Default: false
        :param require_approval: (deprecated) Should the script prompt for approval before destroying stacks. Default: false
        :param asset_metadata: (deprecated) Include "aws:asset:*" CloudFormation metadata for resources that use assets. Default: true
        :param ca_bundle_path: (deprecated) Path to CA certificate to use when validating HTTPS requests. Default: - read from AWS_CA_BUNDLE environment variable
        :param color: (deprecated) Show colors and other style from console output. Default: - ``true`` unless the environment variable ``NO_COLOR`` is set
        :param context: (deprecated) Additional context. Default: - no additional context
        :param debug: (deprecated) enable emission of additional debugging information, such as creation stack traces of tokens. Default: false
        :param ec2_creds: (deprecated) Force trying to fetch EC2 instance credentials. Default: - guess EC2 instance status
        :param ignore_errors: (deprecated) Ignores synthesis errors, which will likely produce an invalid output. Default: false
        :param json: (deprecated) Use JSON output instead of YAML when templates are printed to STDOUT. Default: false
        :param lookups: (deprecated) Perform context lookups. Synthesis fails if this is disabled and context lookups need to be performed Default: true
        :param notices: (deprecated) Show relevant notices. Default: true
        :param path_metadata: (deprecated) Include "aws:cdk:path" CloudFormation metadata for each resource. Default: true
        :param profile: (deprecated) Use the indicated AWS profile as the default environment. Default: - no profile is used
        :param proxy: (deprecated) Use the indicated proxy. Will read from HTTPS_PROXY environment if specified Default: - no proxy
        :param role_arn: (deprecated) Role to pass to CloudFormation for deployment. Default: - use the bootstrap cfn-exec role
        :param stacks: (deprecated) List of stacks to deploy. Default: - all stacks
        :param staging: (deprecated) Copy assets to the output directory. Needed for local debugging the source files with SAM CLI Default: false
        :param strict: (deprecated) Do not construct stacks with warnings. Default: false
        :param trace: (deprecated) Print trace for stack warnings. Default: false
        :param verbose: (deprecated) show debug logs. Default: false
        :param version_reporting: (deprecated) Include "AWS::CDK::Metadata" resource in synthesized templates. Default: true

        :stability: deprecated
        '''
        options = DestroyOptions(
            exclusively=exclusively,
            require_approval=require_approval,
            asset_metadata=asset_metadata,
            ca_bundle_path=ca_bundle_path,
            color=color,
            context=context,
            debug=debug,
            ec2_creds=ec2_creds,
            ignore_errors=ignore_errors,
            json=json,
            lookups=lookups,
            notices=notices,
            path_metadata=path_metadata,
            profile=profile,
            proxy=proxy,
            role_arn=role_arn,
            stacks=stacks,
            staging=staging,
            strict=strict,
            trace=trace,
            verbose=verbose,
            version_reporting=version_reporting,
        )

        return typing.cast(None, jsii.invoke(self, "destroy", [options]))

    @jsii.member(jsii_name="list")
    def list(
        self,
        *,
        long: typing.Optional[builtins.bool] = None,
        asset_metadata: typing.Optional[builtins.bool] = None,
        ca_bundle_path: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.bool] = None,
        context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        debug: typing.Optional[builtins.bool] = None,
        ec2_creds: typing.Optional[builtins.bool] = None,
        ignore_errors: typing.Optional[builtins.bool] = None,
        json: typing.Optional[builtins.bool] = None,
        lookups: typing.Optional[builtins.bool] = None,
        notices: typing.Optional[builtins.bool] = None,
        path_metadata: typing.Optional[builtins.bool] = None,
        profile: typing.Optional[builtins.str] = None,
        proxy: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        stacks: typing.Optional[typing.Sequence[builtins.str]] = None,
        staging: typing.Optional[builtins.bool] = None,
        strict: typing.Optional[builtins.bool] = None,
        trace: typing.Optional[builtins.bool] = None,
        verbose: typing.Optional[builtins.bool] = None,
        version_reporting: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(deprecated) cdk list.

        :param long: (deprecated) Display environment information for each stack. Default: false
        :param asset_metadata: (deprecated) Include "aws:asset:*" CloudFormation metadata for resources that use assets. Default: true
        :param ca_bundle_path: (deprecated) Path to CA certificate to use when validating HTTPS requests. Default: - read from AWS_CA_BUNDLE environment variable
        :param color: (deprecated) Show colors and other style from console output. Default: - ``true`` unless the environment variable ``NO_COLOR`` is set
        :param context: (deprecated) Additional context. Default: - no additional context
        :param debug: (deprecated) enable emission of additional debugging information, such as creation stack traces of tokens. Default: false
        :param ec2_creds: (deprecated) Force trying to fetch EC2 instance credentials. Default: - guess EC2 instance status
        :param ignore_errors: (deprecated) Ignores synthesis errors, which will likely produce an invalid output. Default: false
        :param json: (deprecated) Use JSON output instead of YAML when templates are printed to STDOUT. Default: false
        :param lookups: (deprecated) Perform context lookups. Synthesis fails if this is disabled and context lookups need to be performed Default: true
        :param notices: (deprecated) Show relevant notices. Default: true
        :param path_metadata: (deprecated) Include "aws:cdk:path" CloudFormation metadata for each resource. Default: true
        :param profile: (deprecated) Use the indicated AWS profile as the default environment. Default: - no profile is used
        :param proxy: (deprecated) Use the indicated proxy. Will read from HTTPS_PROXY environment if specified Default: - no proxy
        :param role_arn: (deprecated) Role to pass to CloudFormation for deployment. Default: - use the bootstrap cfn-exec role
        :param stacks: (deprecated) List of stacks to deploy. Default: - all stacks
        :param staging: (deprecated) Copy assets to the output directory. Needed for local debugging the source files with SAM CLI Default: false
        :param strict: (deprecated) Do not construct stacks with warnings. Default: false
        :param trace: (deprecated) Print trace for stack warnings. Default: false
        :param verbose: (deprecated) show debug logs. Default: false
        :param version_reporting: (deprecated) Include "AWS::CDK::Metadata" resource in synthesized templates. Default: true

        :stability: deprecated
        '''
        options = ListOptions(
            long=long,
            asset_metadata=asset_metadata,
            ca_bundle_path=ca_bundle_path,
            color=color,
            context=context,
            debug=debug,
            ec2_creds=ec2_creds,
            ignore_errors=ignore_errors,
            json=json,
            lookups=lookups,
            notices=notices,
            path_metadata=path_metadata,
            profile=profile,
            proxy=proxy,
            role_arn=role_arn,
            stacks=stacks,
            staging=staging,
            strict=strict,
            trace=trace,
            verbose=verbose,
            version_reporting=version_reporting,
        )

        return typing.cast(None, jsii.invoke(self, "list", [options]))

    @jsii.member(jsii_name="synth")
    def synth(
        self,
        *,
        exclusively: typing.Optional[builtins.bool] = None,
        quiet: typing.Optional[builtins.bool] = None,
        validation: typing.Optional[builtins.bool] = None,
        asset_metadata: typing.Optional[builtins.bool] = None,
        ca_bundle_path: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.bool] = None,
        context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        debug: typing.Optional[builtins.bool] = None,
        ec2_creds: typing.Optional[builtins.bool] = None,
        ignore_errors: typing.Optional[builtins.bool] = None,
        json: typing.Optional[builtins.bool] = None,
        lookups: typing.Optional[builtins.bool] = None,
        notices: typing.Optional[builtins.bool] = None,
        path_metadata: typing.Optional[builtins.bool] = None,
        profile: typing.Optional[builtins.str] = None,
        proxy: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        stacks: typing.Optional[typing.Sequence[builtins.str]] = None,
        staging: typing.Optional[builtins.bool] = None,
        strict: typing.Optional[builtins.bool] = None,
        trace: typing.Optional[builtins.bool] = None,
        verbose: typing.Optional[builtins.bool] = None,
        version_reporting: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(deprecated) cdk synth.

        :param exclusively: (deprecated) Only synthesize the given stack. Default: false
        :param quiet: (deprecated) Do not output CloudFormation Template to stdout. Default: false;
        :param validation: (deprecated) After synthesis, validate stacks with the "validateOnSynth" attribute set (can also be controlled with CDK_VALIDATION). Default: true;
        :param asset_metadata: (deprecated) Include "aws:asset:*" CloudFormation metadata for resources that use assets. Default: true
        :param ca_bundle_path: (deprecated) Path to CA certificate to use when validating HTTPS requests. Default: - read from AWS_CA_BUNDLE environment variable
        :param color: (deprecated) Show colors and other style from console output. Default: - ``true`` unless the environment variable ``NO_COLOR`` is set
        :param context: (deprecated) Additional context. Default: - no additional context
        :param debug: (deprecated) enable emission of additional debugging information, such as creation stack traces of tokens. Default: false
        :param ec2_creds: (deprecated) Force trying to fetch EC2 instance credentials. Default: - guess EC2 instance status
        :param ignore_errors: (deprecated) Ignores synthesis errors, which will likely produce an invalid output. Default: false
        :param json: (deprecated) Use JSON output instead of YAML when templates are printed to STDOUT. Default: false
        :param lookups: (deprecated) Perform context lookups. Synthesis fails if this is disabled and context lookups need to be performed Default: true
        :param notices: (deprecated) Show relevant notices. Default: true
        :param path_metadata: (deprecated) Include "aws:cdk:path" CloudFormation metadata for each resource. Default: true
        :param profile: (deprecated) Use the indicated AWS profile as the default environment. Default: - no profile is used
        :param proxy: (deprecated) Use the indicated proxy. Will read from HTTPS_PROXY environment if specified Default: - no proxy
        :param role_arn: (deprecated) Role to pass to CloudFormation for deployment. Default: - use the bootstrap cfn-exec role
        :param stacks: (deprecated) List of stacks to deploy. Default: - all stacks
        :param staging: (deprecated) Copy assets to the output directory. Needed for local debugging the source files with SAM CLI Default: false
        :param strict: (deprecated) Do not construct stacks with warnings. Default: false
        :param trace: (deprecated) Print trace for stack warnings. Default: false
        :param verbose: (deprecated) show debug logs. Default: false
        :param version_reporting: (deprecated) Include "AWS::CDK::Metadata" resource in synthesized templates. Default: true

        :stability: deprecated
        '''
        options = SynthOptions(
            exclusively=exclusively,
            quiet=quiet,
            validation=validation,
            asset_metadata=asset_metadata,
            ca_bundle_path=ca_bundle_path,
            color=color,
            context=context,
            debug=debug,
            ec2_creds=ec2_creds,
            ignore_errors=ignore_errors,
            json=json,
            lookups=lookups,
            notices=notices,
            path_metadata=path_metadata,
            profile=profile,
            proxy=proxy,
            role_arn=role_arn,
            stacks=stacks,
            staging=staging,
            strict=strict,
            trace=trace,
            verbose=verbose,
            version_reporting=version_reporting,
        )

        return typing.cast(None, jsii.invoke(self, "synth", [options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAwsCdkCli).__jsii_proxy_class__ = lambda : _IAwsCdkCliProxy


@jsii.interface(jsii_type="@aws-cdk/cli-lib-alpha.ICloudAssemblyDirectoryProducer")
class ICloudAssemblyDirectoryProducer(typing_extensions.Protocol):
    '''(deprecated) A class returning the path to a Cloud Assembly Directory when its ``produce`` method is invoked with the current context  AWS CDK apps might need to be synthesized multiple times with additional context values before they are ready.

    When running the CLI from inside a directory, this is implemented by invoking the app multiple times.
    Here the ``produce()`` method provides this multi-pass ability.

    :stability: deprecated
    '''

    @builtins.property
    @jsii.member(jsii_name="workingDirectory")
    def working_directory(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The working directory used to run the Cloud Assembly from.

        This is were a ``cdk.context.json`` files will be written.

        :default: - current working directory

        :stability: deprecated
        '''
        ...

    @working_directory.setter
    def working_directory(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @jsii.member(jsii_name="produce")
    def produce(
        self,
        context: typing.Mapping[builtins.str, typing.Any],
    ) -> builtins.str:
        '''(deprecated) Synthesize a Cloud Assembly directory for a given context.

        For all features to work correctly, ``cdk.App()`` must be instantiated with the received context values in the method body.
        Usually obtained similar to this::

           @jsii.implements(ICloudAssemblyDirectoryProducer)
           class MyProducer:
               def produce(self, context):
                   app = cdk.App(context=context)
                   # create stacks here
                   return app.synth().directory

        :param context: -

        :stability: deprecated
        '''
        ...


class _ICloudAssemblyDirectoryProducerProxy:
    '''(deprecated) A class returning the path to a Cloud Assembly Directory when its ``produce`` method is invoked with the current context  AWS CDK apps might need to be synthesized multiple times with additional context values before they are ready.

    When running the CLI from inside a directory, this is implemented by invoking the app multiple times.
    Here the ``produce()`` method provides this multi-pass ability.

    :stability: deprecated
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/cli-lib-alpha.ICloudAssemblyDirectoryProducer"

    @builtins.property
    @jsii.member(jsii_name="workingDirectory")
    def working_directory(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The working directory used to run the Cloud Assembly from.

        This is were a ``cdk.context.json`` files will be written.

        :default: - current working directory

        :stability: deprecated
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workingDirectory"))

    @working_directory.setter
    def working_directory(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9976532bf553edb535766f6931bb19ad82ff334216dc84b704ebfaac651639ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workingDirectory", value) # pyright: ignore[reportArgumentType]

    @jsii.member(jsii_name="produce")
    def produce(
        self,
        context: typing.Mapping[builtins.str, typing.Any],
    ) -> builtins.str:
        '''(deprecated) Synthesize a Cloud Assembly directory for a given context.

        For all features to work correctly, ``cdk.App()`` must be instantiated with the received context values in the method body.
        Usually obtained similar to this::

           @jsii.implements(ICloudAssemblyDirectoryProducer)
           class MyProducer:
               def produce(self, context):
                   app = cdk.App(context=context)
                   # create stacks here
                   return app.synth().directory

        :param context: -

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f63d29a3ec4b39699f97d7f6c338a9273fb37e7f52b8479fb6419f38447dd194)
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(builtins.str, jsii.invoke(self, "produce", [context]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ICloudAssemblyDirectoryProducer).__jsii_proxy_class__ = lambda : _ICloudAssemblyDirectoryProducerProxy


@jsii.enum(jsii_type="@aws-cdk/cli-lib-alpha.RequireApproval")
class RequireApproval(enum.Enum):
    '''(deprecated) In what scenarios should the CLI ask for approval.

    :stability: deprecated
    '''

    NEVER = "NEVER"
    '''(deprecated) Never ask for approval.

    :stability: deprecated
    '''
    ANYCHANGE = "ANYCHANGE"
    '''(deprecated) Prompt for approval for any type  of change to the stack.

    :stability: deprecated
    '''
    BROADENING = "BROADENING"
    '''(deprecated) Only prompt for approval if there are security related changes.

    :stability: deprecated
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/cli-lib-alpha.SharedOptions",
    jsii_struct_bases=[],
    name_mapping={
        "asset_metadata": "assetMetadata",
        "ca_bundle_path": "caBundlePath",
        "color": "color",
        "context": "context",
        "debug": "debug",
        "ec2_creds": "ec2Creds",
        "ignore_errors": "ignoreErrors",
        "json": "json",
        "lookups": "lookups",
        "notices": "notices",
        "path_metadata": "pathMetadata",
        "profile": "profile",
        "proxy": "proxy",
        "role_arn": "roleArn",
        "stacks": "stacks",
        "staging": "staging",
        "strict": "strict",
        "trace": "trace",
        "verbose": "verbose",
        "version_reporting": "versionReporting",
    },
)
class SharedOptions:
    def __init__(
        self,
        *,
        asset_metadata: typing.Optional[builtins.bool] = None,
        ca_bundle_path: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.bool] = None,
        context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        debug: typing.Optional[builtins.bool] = None,
        ec2_creds: typing.Optional[builtins.bool] = None,
        ignore_errors: typing.Optional[builtins.bool] = None,
        json: typing.Optional[builtins.bool] = None,
        lookups: typing.Optional[builtins.bool] = None,
        notices: typing.Optional[builtins.bool] = None,
        path_metadata: typing.Optional[builtins.bool] = None,
        profile: typing.Optional[builtins.str] = None,
        proxy: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        stacks: typing.Optional[typing.Sequence[builtins.str]] = None,
        staging: typing.Optional[builtins.bool] = None,
        strict: typing.Optional[builtins.bool] = None,
        trace: typing.Optional[builtins.bool] = None,
        verbose: typing.Optional[builtins.bool] = None,
        version_reporting: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(deprecated) AWS CDK CLI options that apply to all commands.

        :param asset_metadata: (deprecated) Include "aws:asset:*" CloudFormation metadata for resources that use assets. Default: true
        :param ca_bundle_path: (deprecated) Path to CA certificate to use when validating HTTPS requests. Default: - read from AWS_CA_BUNDLE environment variable
        :param color: (deprecated) Show colors and other style from console output. Default: - ``true`` unless the environment variable ``NO_COLOR`` is set
        :param context: (deprecated) Additional context. Default: - no additional context
        :param debug: (deprecated) enable emission of additional debugging information, such as creation stack traces of tokens. Default: false
        :param ec2_creds: (deprecated) Force trying to fetch EC2 instance credentials. Default: - guess EC2 instance status
        :param ignore_errors: (deprecated) Ignores synthesis errors, which will likely produce an invalid output. Default: false
        :param json: (deprecated) Use JSON output instead of YAML when templates are printed to STDOUT. Default: false
        :param lookups: (deprecated) Perform context lookups. Synthesis fails if this is disabled and context lookups need to be performed Default: true
        :param notices: (deprecated) Show relevant notices. Default: true
        :param path_metadata: (deprecated) Include "aws:cdk:path" CloudFormation metadata for each resource. Default: true
        :param profile: (deprecated) Use the indicated AWS profile as the default environment. Default: - no profile is used
        :param proxy: (deprecated) Use the indicated proxy. Will read from HTTPS_PROXY environment if specified Default: - no proxy
        :param role_arn: (deprecated) Role to pass to CloudFormation for deployment. Default: - use the bootstrap cfn-exec role
        :param stacks: (deprecated) List of stacks to deploy. Default: - all stacks
        :param staging: (deprecated) Copy assets to the output directory. Needed for local debugging the source files with SAM CLI Default: false
        :param strict: (deprecated) Do not construct stacks with warnings. Default: false
        :param trace: (deprecated) Print trace for stack warnings. Default: false
        :param verbose: (deprecated) show debug logs. Default: false
        :param version_reporting: (deprecated) Include "AWS::CDK::Metadata" resource in synthesized templates. Default: true

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f041eafd3001a42690905ce9565eef958505cd6d0e775d559e6fbec53b407984)
            check_type(argname="argument asset_metadata", value=asset_metadata, expected_type=type_hints["asset_metadata"])
            check_type(argname="argument ca_bundle_path", value=ca_bundle_path, expected_type=type_hints["ca_bundle_path"])
            check_type(argname="argument color", value=color, expected_type=type_hints["color"])
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
            check_type(argname="argument debug", value=debug, expected_type=type_hints["debug"])
            check_type(argname="argument ec2_creds", value=ec2_creds, expected_type=type_hints["ec2_creds"])
            check_type(argname="argument ignore_errors", value=ignore_errors, expected_type=type_hints["ignore_errors"])
            check_type(argname="argument json", value=json, expected_type=type_hints["json"])
            check_type(argname="argument lookups", value=lookups, expected_type=type_hints["lookups"])
            check_type(argname="argument notices", value=notices, expected_type=type_hints["notices"])
            check_type(argname="argument path_metadata", value=path_metadata, expected_type=type_hints["path_metadata"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
            check_type(argname="argument proxy", value=proxy, expected_type=type_hints["proxy"])
            check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
            check_type(argname="argument stacks", value=stacks, expected_type=type_hints["stacks"])
            check_type(argname="argument staging", value=staging, expected_type=type_hints["staging"])
            check_type(argname="argument strict", value=strict, expected_type=type_hints["strict"])
            check_type(argname="argument trace", value=trace, expected_type=type_hints["trace"])
            check_type(argname="argument verbose", value=verbose, expected_type=type_hints["verbose"])
            check_type(argname="argument version_reporting", value=version_reporting, expected_type=type_hints["version_reporting"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if asset_metadata is not None:
            self._values["asset_metadata"] = asset_metadata
        if ca_bundle_path is not None:
            self._values["ca_bundle_path"] = ca_bundle_path
        if color is not None:
            self._values["color"] = color
        if context is not None:
            self._values["context"] = context
        if debug is not None:
            self._values["debug"] = debug
        if ec2_creds is not None:
            self._values["ec2_creds"] = ec2_creds
        if ignore_errors is not None:
            self._values["ignore_errors"] = ignore_errors
        if json is not None:
            self._values["json"] = json
        if lookups is not None:
            self._values["lookups"] = lookups
        if notices is not None:
            self._values["notices"] = notices
        if path_metadata is not None:
            self._values["path_metadata"] = path_metadata
        if profile is not None:
            self._values["profile"] = profile
        if proxy is not None:
            self._values["proxy"] = proxy
        if role_arn is not None:
            self._values["role_arn"] = role_arn
        if stacks is not None:
            self._values["stacks"] = stacks
        if staging is not None:
            self._values["staging"] = staging
        if strict is not None:
            self._values["strict"] = strict
        if trace is not None:
            self._values["trace"] = trace
        if verbose is not None:
            self._values["verbose"] = verbose
        if version_reporting is not None:
            self._values["version_reporting"] = version_reporting

    @builtins.property
    def asset_metadata(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Include "aws:asset:*" CloudFormation metadata for resources that use assets.

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("asset_metadata")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ca_bundle_path(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Path to CA certificate to use when validating HTTPS requests.

        :default: - read from AWS_CA_BUNDLE environment variable

        :stability: deprecated
        '''
        result = self._values.get("ca_bundle_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def color(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Show colors and other style from console output.

        :default: - ``true`` unless the environment variable ``NO_COLOR`` is set

        :stability: deprecated
        '''
        result = self._values.get("color")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def context(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(deprecated) Additional context.

        :default: - no additional context

        :stability: deprecated
        '''
        result = self._values.get("context")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def debug(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) enable emission of additional debugging information, such as creation stack traces of tokens.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("debug")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ec2_creds(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Force trying to fetch EC2 instance credentials.

        :default: - guess EC2 instance status

        :stability: deprecated
        '''
        result = self._values.get("ec2_creds")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ignore_errors(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Ignores synthesis errors, which will likely produce an invalid output.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("ignore_errors")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def json(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Use JSON output instead of YAML when templates are printed to STDOUT.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("json")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def lookups(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Perform context lookups.

        Synthesis fails if this is disabled and context lookups need
        to be performed

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("lookups")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def notices(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Show relevant notices.

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("notices")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def path_metadata(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Include "aws:cdk:path" CloudFormation metadata for each resource.

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("path_metadata")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def profile(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Use the indicated AWS profile as the default environment.

        :default: - no profile is used

        :stability: deprecated
        '''
        result = self._values.get("profile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def proxy(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Use the indicated proxy.

        Will read from
        HTTPS_PROXY environment if specified

        :default: - no proxy

        :stability: deprecated
        '''
        result = self._values.get("proxy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role_arn(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Role to pass to CloudFormation for deployment.

        :default: - use the bootstrap cfn-exec role

        :stability: deprecated
        '''
        result = self._values.get("role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stacks(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(deprecated) List of stacks to deploy.

        :default: - all stacks

        :stability: deprecated
        '''
        result = self._values.get("stacks")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def staging(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Copy assets to the output directory.

        Needed for local debugging the source files with SAM CLI

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("staging")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def strict(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Do not construct stacks with warnings.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("strict")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def trace(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Print trace for stack warnings.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("trace")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def verbose(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) show debug logs.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("verbose")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def version_reporting(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Include "AWS::CDK::Metadata" resource in synthesized templates.

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("version_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SharedOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/cli-lib-alpha.StackActivityProgress")
class StackActivityProgress(enum.Enum):
    '''(deprecated) Supported display modes for stack deployment activity.

    :stability: deprecated
    '''

    BAR = "BAR"
    '''(deprecated) Displays a progress bar with only the events for the resource currently being deployed.

    :stability: deprecated
    '''
    EVENTS = "EVENTS"
    '''(deprecated) Displays complete history with all CloudFormation stack events.

    :stability: deprecated
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/cli-lib-alpha.SynthOptions",
    jsii_struct_bases=[SharedOptions],
    name_mapping={
        "asset_metadata": "assetMetadata",
        "ca_bundle_path": "caBundlePath",
        "color": "color",
        "context": "context",
        "debug": "debug",
        "ec2_creds": "ec2Creds",
        "ignore_errors": "ignoreErrors",
        "json": "json",
        "lookups": "lookups",
        "notices": "notices",
        "path_metadata": "pathMetadata",
        "profile": "profile",
        "proxy": "proxy",
        "role_arn": "roleArn",
        "stacks": "stacks",
        "staging": "staging",
        "strict": "strict",
        "trace": "trace",
        "verbose": "verbose",
        "version_reporting": "versionReporting",
        "exclusively": "exclusively",
        "quiet": "quiet",
        "validation": "validation",
    },
)
class SynthOptions(SharedOptions):
    def __init__(
        self,
        *,
        asset_metadata: typing.Optional[builtins.bool] = None,
        ca_bundle_path: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.bool] = None,
        context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        debug: typing.Optional[builtins.bool] = None,
        ec2_creds: typing.Optional[builtins.bool] = None,
        ignore_errors: typing.Optional[builtins.bool] = None,
        json: typing.Optional[builtins.bool] = None,
        lookups: typing.Optional[builtins.bool] = None,
        notices: typing.Optional[builtins.bool] = None,
        path_metadata: typing.Optional[builtins.bool] = None,
        profile: typing.Optional[builtins.str] = None,
        proxy: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        stacks: typing.Optional[typing.Sequence[builtins.str]] = None,
        staging: typing.Optional[builtins.bool] = None,
        strict: typing.Optional[builtins.bool] = None,
        trace: typing.Optional[builtins.bool] = None,
        verbose: typing.Optional[builtins.bool] = None,
        version_reporting: typing.Optional[builtins.bool] = None,
        exclusively: typing.Optional[builtins.bool] = None,
        quiet: typing.Optional[builtins.bool] = None,
        validation: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(deprecated) Options to use with cdk synth.

        :param asset_metadata: (deprecated) Include "aws:asset:*" CloudFormation metadata for resources that use assets. Default: true
        :param ca_bundle_path: (deprecated) Path to CA certificate to use when validating HTTPS requests. Default: - read from AWS_CA_BUNDLE environment variable
        :param color: (deprecated) Show colors and other style from console output. Default: - ``true`` unless the environment variable ``NO_COLOR`` is set
        :param context: (deprecated) Additional context. Default: - no additional context
        :param debug: (deprecated) enable emission of additional debugging information, such as creation stack traces of tokens. Default: false
        :param ec2_creds: (deprecated) Force trying to fetch EC2 instance credentials. Default: - guess EC2 instance status
        :param ignore_errors: (deprecated) Ignores synthesis errors, which will likely produce an invalid output. Default: false
        :param json: (deprecated) Use JSON output instead of YAML when templates are printed to STDOUT. Default: false
        :param lookups: (deprecated) Perform context lookups. Synthesis fails if this is disabled and context lookups need to be performed Default: true
        :param notices: (deprecated) Show relevant notices. Default: true
        :param path_metadata: (deprecated) Include "aws:cdk:path" CloudFormation metadata for each resource. Default: true
        :param profile: (deprecated) Use the indicated AWS profile as the default environment. Default: - no profile is used
        :param proxy: (deprecated) Use the indicated proxy. Will read from HTTPS_PROXY environment if specified Default: - no proxy
        :param role_arn: (deprecated) Role to pass to CloudFormation for deployment. Default: - use the bootstrap cfn-exec role
        :param stacks: (deprecated) List of stacks to deploy. Default: - all stacks
        :param staging: (deprecated) Copy assets to the output directory. Needed for local debugging the source files with SAM CLI Default: false
        :param strict: (deprecated) Do not construct stacks with warnings. Default: false
        :param trace: (deprecated) Print trace for stack warnings. Default: false
        :param verbose: (deprecated) show debug logs. Default: false
        :param version_reporting: (deprecated) Include "AWS::CDK::Metadata" resource in synthesized templates. Default: true
        :param exclusively: (deprecated) Only synthesize the given stack. Default: false
        :param quiet: (deprecated) Do not output CloudFormation Template to stdout. Default: false;
        :param validation: (deprecated) After synthesis, validate stacks with the "validateOnSynth" attribute set (can also be controlled with CDK_VALIDATION). Default: true;

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ed6f82891326f3fc3393abc8d6e60990c311ca40ba298491e4428557a66a843)
            check_type(argname="argument asset_metadata", value=asset_metadata, expected_type=type_hints["asset_metadata"])
            check_type(argname="argument ca_bundle_path", value=ca_bundle_path, expected_type=type_hints["ca_bundle_path"])
            check_type(argname="argument color", value=color, expected_type=type_hints["color"])
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
            check_type(argname="argument debug", value=debug, expected_type=type_hints["debug"])
            check_type(argname="argument ec2_creds", value=ec2_creds, expected_type=type_hints["ec2_creds"])
            check_type(argname="argument ignore_errors", value=ignore_errors, expected_type=type_hints["ignore_errors"])
            check_type(argname="argument json", value=json, expected_type=type_hints["json"])
            check_type(argname="argument lookups", value=lookups, expected_type=type_hints["lookups"])
            check_type(argname="argument notices", value=notices, expected_type=type_hints["notices"])
            check_type(argname="argument path_metadata", value=path_metadata, expected_type=type_hints["path_metadata"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
            check_type(argname="argument proxy", value=proxy, expected_type=type_hints["proxy"])
            check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
            check_type(argname="argument stacks", value=stacks, expected_type=type_hints["stacks"])
            check_type(argname="argument staging", value=staging, expected_type=type_hints["staging"])
            check_type(argname="argument strict", value=strict, expected_type=type_hints["strict"])
            check_type(argname="argument trace", value=trace, expected_type=type_hints["trace"])
            check_type(argname="argument verbose", value=verbose, expected_type=type_hints["verbose"])
            check_type(argname="argument version_reporting", value=version_reporting, expected_type=type_hints["version_reporting"])
            check_type(argname="argument exclusively", value=exclusively, expected_type=type_hints["exclusively"])
            check_type(argname="argument quiet", value=quiet, expected_type=type_hints["quiet"])
            check_type(argname="argument validation", value=validation, expected_type=type_hints["validation"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if asset_metadata is not None:
            self._values["asset_metadata"] = asset_metadata
        if ca_bundle_path is not None:
            self._values["ca_bundle_path"] = ca_bundle_path
        if color is not None:
            self._values["color"] = color
        if context is not None:
            self._values["context"] = context
        if debug is not None:
            self._values["debug"] = debug
        if ec2_creds is not None:
            self._values["ec2_creds"] = ec2_creds
        if ignore_errors is not None:
            self._values["ignore_errors"] = ignore_errors
        if json is not None:
            self._values["json"] = json
        if lookups is not None:
            self._values["lookups"] = lookups
        if notices is not None:
            self._values["notices"] = notices
        if path_metadata is not None:
            self._values["path_metadata"] = path_metadata
        if profile is not None:
            self._values["profile"] = profile
        if proxy is not None:
            self._values["proxy"] = proxy
        if role_arn is not None:
            self._values["role_arn"] = role_arn
        if stacks is not None:
            self._values["stacks"] = stacks
        if staging is not None:
            self._values["staging"] = staging
        if strict is not None:
            self._values["strict"] = strict
        if trace is not None:
            self._values["trace"] = trace
        if verbose is not None:
            self._values["verbose"] = verbose
        if version_reporting is not None:
            self._values["version_reporting"] = version_reporting
        if exclusively is not None:
            self._values["exclusively"] = exclusively
        if quiet is not None:
            self._values["quiet"] = quiet
        if validation is not None:
            self._values["validation"] = validation

    @builtins.property
    def asset_metadata(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Include "aws:asset:*" CloudFormation metadata for resources that use assets.

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("asset_metadata")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ca_bundle_path(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Path to CA certificate to use when validating HTTPS requests.

        :default: - read from AWS_CA_BUNDLE environment variable

        :stability: deprecated
        '''
        result = self._values.get("ca_bundle_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def color(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Show colors and other style from console output.

        :default: - ``true`` unless the environment variable ``NO_COLOR`` is set

        :stability: deprecated
        '''
        result = self._values.get("color")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def context(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(deprecated) Additional context.

        :default: - no additional context

        :stability: deprecated
        '''
        result = self._values.get("context")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def debug(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) enable emission of additional debugging information, such as creation stack traces of tokens.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("debug")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ec2_creds(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Force trying to fetch EC2 instance credentials.

        :default: - guess EC2 instance status

        :stability: deprecated
        '''
        result = self._values.get("ec2_creds")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ignore_errors(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Ignores synthesis errors, which will likely produce an invalid output.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("ignore_errors")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def json(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Use JSON output instead of YAML when templates are printed to STDOUT.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("json")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def lookups(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Perform context lookups.

        Synthesis fails if this is disabled and context lookups need
        to be performed

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("lookups")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def notices(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Show relevant notices.

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("notices")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def path_metadata(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Include "aws:cdk:path" CloudFormation metadata for each resource.

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("path_metadata")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def profile(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Use the indicated AWS profile as the default environment.

        :default: - no profile is used

        :stability: deprecated
        '''
        result = self._values.get("profile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def proxy(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Use the indicated proxy.

        Will read from
        HTTPS_PROXY environment if specified

        :default: - no proxy

        :stability: deprecated
        '''
        result = self._values.get("proxy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role_arn(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Role to pass to CloudFormation for deployment.

        :default: - use the bootstrap cfn-exec role

        :stability: deprecated
        '''
        result = self._values.get("role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stacks(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(deprecated) List of stacks to deploy.

        :default: - all stacks

        :stability: deprecated
        '''
        result = self._values.get("stacks")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def staging(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Copy assets to the output directory.

        Needed for local debugging the source files with SAM CLI

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("staging")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def strict(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Do not construct stacks with warnings.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("strict")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def trace(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Print trace for stack warnings.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("trace")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def verbose(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) show debug logs.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("verbose")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def version_reporting(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Include "AWS::CDK::Metadata" resource in synthesized templates.

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("version_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def exclusively(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Only synthesize the given stack.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("exclusively")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def quiet(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Do not output CloudFormation Template to stdout.

        :default: false;

        :stability: deprecated
        '''
        result = self._values.get("quiet")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def validation(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) After synthesis, validate stacks with the "validateOnSynth" attribute set (can also be controlled with CDK_VALIDATION).

        :default: true;

        :stability: deprecated
        '''
        result = self._values.get("validation")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SynthOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IAwsCdkCli)
class AwsCdkCli(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cli-lib-alpha.AwsCdkCli"):
    '''(deprecated) Provides a programmatic interface for interacting with the AWS CDK CLI.

    :stability: deprecated
    '''

    @jsii.member(jsii_name="fromCdkAppDirectory")
    @builtins.classmethod
    def from_cdk_app_directory(
        cls,
        directory: typing.Optional[builtins.str] = None,
        *,
        app: typing.Optional[builtins.str] = None,
        output: typing.Optional[builtins.str] = None,
    ) -> "AwsCdkCli":
        '''(deprecated) Create the CLI from a directory containing an AWS CDK app.

        :param directory: - the directory of the AWS CDK app. Defaults to the current working directory.
        :param app: (deprecated) Command-line for executing your app or a cloud assembly directory e.g. "node bin/my-app.js" or "cdk.out". Default: - read from cdk.json
        :param output: (deprecated) Emits the synthesized cloud assembly into a directory. Default: cdk.out

        :return: an instance of ``AwsCdkCli``

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8a4a48e6e27d586c5dd41502dccff564a5fedcc9367e37550ec6c2e9af643ff)
            check_type(argname="argument directory", value=directory, expected_type=type_hints["directory"])
        props = CdkAppDirectoryProps(app=app, output=output)

        return typing.cast("AwsCdkCli", jsii.sinvoke(cls, "fromCdkAppDirectory", [directory, props]))

    @jsii.member(jsii_name="fromCloudAssemblyDirectoryProducer")
    @builtins.classmethod
    def from_cloud_assembly_directory_producer(
        cls,
        producer: ICloudAssemblyDirectoryProducer,
    ) -> "AwsCdkCli":
        '''(deprecated) Create the CLI from a CloudAssemblyDirectoryProducer.

        :param producer: -

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9bfa499e48a3fc09d071d19e318c0bc809314da2a23cf1b26886e4c5890f959)
            check_type(argname="argument producer", value=producer, expected_type=type_hints["producer"])
        return typing.cast("AwsCdkCli", jsii.sinvoke(cls, "fromCloudAssemblyDirectoryProducer", [producer]))

    @jsii.member(jsii_name="bootstrap")
    def bootstrap(
        self,
        *,
        bootstrap_bucket_name: typing.Optional[builtins.str] = None,
        bootstrap_customer_key: typing.Optional[builtins.str] = None,
        bootstrap_kms_key_id: typing.Optional[builtins.str] = None,
        cfn_execution_policy: typing.Optional[builtins.str] = None,
        custom_permissions_boundary: typing.Optional[builtins.str] = None,
        environments: typing.Optional[typing.Sequence[builtins.str]] = None,
        example_permissions_boundary: typing.Optional[builtins.bool] = None,
        execute: typing.Optional[builtins.bool] = None,
        force: typing.Optional[builtins.bool] = None,
        public_access_block_configuration: typing.Optional[builtins.str] = None,
        qualifier: typing.Optional[builtins.str] = None,
        show_template: typing.Optional[builtins.bool] = None,
        template: typing.Optional[builtins.str] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        toolkit_stack_name: typing.Optional[builtins.str] = None,
        trust: typing.Optional[builtins.str] = None,
        trust_for_lookup: typing.Optional[builtins.str] = None,
        use_previous_parameters: typing.Optional[builtins.bool] = None,
        asset_metadata: typing.Optional[builtins.bool] = None,
        ca_bundle_path: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.bool] = None,
        context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        debug: typing.Optional[builtins.bool] = None,
        ec2_creds: typing.Optional[builtins.bool] = None,
        ignore_errors: typing.Optional[builtins.bool] = None,
        json: typing.Optional[builtins.bool] = None,
        lookups: typing.Optional[builtins.bool] = None,
        notices: typing.Optional[builtins.bool] = None,
        path_metadata: typing.Optional[builtins.bool] = None,
        profile: typing.Optional[builtins.str] = None,
        proxy: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        stacks: typing.Optional[typing.Sequence[builtins.str]] = None,
        staging: typing.Optional[builtins.bool] = None,
        strict: typing.Optional[builtins.bool] = None,
        trace: typing.Optional[builtins.bool] = None,
        verbose: typing.Optional[builtins.bool] = None,
        version_reporting: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(deprecated) cdk bootstrap.

        :param bootstrap_bucket_name: (deprecated) The name of the CDK toolkit bucket; bucket will be created and must not exist Default: - auto-generated CloudFormation name
        :param bootstrap_customer_key: (deprecated) Create a Customer Master Key (CMK) for the bootstrap bucket (you will be charged but can customize permissions, modern bootstrapping only). Default: undefined
        :param bootstrap_kms_key_id: (deprecated) AWS KMS master key ID used for the SSE-KMS encryption. Default: undefined
        :param cfn_execution_policy: (deprecated) The Managed Policy ARNs that should be attached to the role performing deployments into this environment (may be repeated, modern bootstrapping only). Default: - none
        :param custom_permissions_boundary: (deprecated) Use the permissions boundary specified by name. Default: undefined
        :param environments: (deprecated) The target AWS environments to deploy the bootstrap stack to. Uses the following format: ``aws://<account-id>/<region>`` Default: - Bootstrap all environments referenced in the CDK app or determine an environment from local configuration.
        :param example_permissions_boundary: (deprecated) Use the example permissions boundary. Default: undefined
        :param execute: (deprecated) Whether to execute ChangeSet (--no-execute will NOT execute the ChangeSet). Default: true
        :param force: (deprecated) Always bootstrap even if it would downgrade template version. Default: false
        :param public_access_block_configuration: (deprecated) Block public access configuration on CDK toolkit bucket (enabled by default). Default: undefined
        :param qualifier: (deprecated) String which must be unique for each bootstrap stack. You must configure it on your CDK app if you change this from the default. Default: undefined
        :param show_template: (deprecated) Instead of actual bootstrapping, print the current CLI's bootstrapping template to stdout for customization. Default: false
        :param template: (deprecated) Use the template from the given file instead of the built-in one (use --show-template to obtain an example).
        :param termination_protection: (deprecated) Toggle CloudFormation termination protection on the bootstrap stacks. Default: false
        :param toolkit_stack_name: (deprecated) The name of the CDK toolkit stack to create.
        :param trust: (deprecated) The AWS account IDs that should be trusted to perform deployments into this environment (may be repeated, modern bootstrapping only). Default: undefined
        :param trust_for_lookup: (deprecated) The AWS account IDs that should be trusted to look up values in this environment (may be repeated, modern bootstrapping only). Default: undefined
        :param use_previous_parameters: (deprecated) Use previous values for existing parameters (you must specify all parameters on every deployment if this is disabled). Default: true
        :param asset_metadata: (deprecated) Include "aws:asset:*" CloudFormation metadata for resources that use assets. Default: true
        :param ca_bundle_path: (deprecated) Path to CA certificate to use when validating HTTPS requests. Default: - read from AWS_CA_BUNDLE environment variable
        :param color: (deprecated) Show colors and other style from console output. Default: - ``true`` unless the environment variable ``NO_COLOR`` is set
        :param context: (deprecated) Additional context. Default: - no additional context
        :param debug: (deprecated) enable emission of additional debugging information, such as creation stack traces of tokens. Default: false
        :param ec2_creds: (deprecated) Force trying to fetch EC2 instance credentials. Default: - guess EC2 instance status
        :param ignore_errors: (deprecated) Ignores synthesis errors, which will likely produce an invalid output. Default: false
        :param json: (deprecated) Use JSON output instead of YAML when templates are printed to STDOUT. Default: false
        :param lookups: (deprecated) Perform context lookups. Synthesis fails if this is disabled and context lookups need to be performed Default: true
        :param notices: (deprecated) Show relevant notices. Default: true
        :param path_metadata: (deprecated) Include "aws:cdk:path" CloudFormation metadata for each resource. Default: true
        :param profile: (deprecated) Use the indicated AWS profile as the default environment. Default: - no profile is used
        :param proxy: (deprecated) Use the indicated proxy. Will read from HTTPS_PROXY environment if specified Default: - no proxy
        :param role_arn: (deprecated) Role to pass to CloudFormation for deployment. Default: - use the bootstrap cfn-exec role
        :param stacks: (deprecated) List of stacks to deploy. Default: - all stacks
        :param staging: (deprecated) Copy assets to the output directory. Needed for local debugging the source files with SAM CLI Default: false
        :param strict: (deprecated) Do not construct stacks with warnings. Default: false
        :param trace: (deprecated) Print trace for stack warnings. Default: false
        :param verbose: (deprecated) show debug logs. Default: false
        :param version_reporting: (deprecated) Include "AWS::CDK::Metadata" resource in synthesized templates. Default: true

        :stability: deprecated
        '''
        options = BootstrapOptions(
            bootstrap_bucket_name=bootstrap_bucket_name,
            bootstrap_customer_key=bootstrap_customer_key,
            bootstrap_kms_key_id=bootstrap_kms_key_id,
            cfn_execution_policy=cfn_execution_policy,
            custom_permissions_boundary=custom_permissions_boundary,
            environments=environments,
            example_permissions_boundary=example_permissions_boundary,
            execute=execute,
            force=force,
            public_access_block_configuration=public_access_block_configuration,
            qualifier=qualifier,
            show_template=show_template,
            template=template,
            termination_protection=termination_protection,
            toolkit_stack_name=toolkit_stack_name,
            trust=trust,
            trust_for_lookup=trust_for_lookup,
            use_previous_parameters=use_previous_parameters,
            asset_metadata=asset_metadata,
            ca_bundle_path=ca_bundle_path,
            color=color,
            context=context,
            debug=debug,
            ec2_creds=ec2_creds,
            ignore_errors=ignore_errors,
            json=json,
            lookups=lookups,
            notices=notices,
            path_metadata=path_metadata,
            profile=profile,
            proxy=proxy,
            role_arn=role_arn,
            stacks=stacks,
            staging=staging,
            strict=strict,
            trace=trace,
            verbose=verbose,
            version_reporting=version_reporting,
        )

        return typing.cast(None, jsii.ainvoke(self, "bootstrap", [options]))

    @jsii.member(jsii_name="deploy")
    def deploy(
        self,
        *,
        asset_parallelism: typing.Optional[builtins.bool] = None,
        asset_prebuild: typing.Optional[builtins.bool] = None,
        change_set_name: typing.Optional[builtins.str] = None,
        ci: typing.Optional[builtins.bool] = None,
        concurrency: typing.Optional[jsii.Number] = None,
        exclusively: typing.Optional[builtins.bool] = None,
        execute: typing.Optional[builtins.bool] = None,
        force: typing.Optional[builtins.bool] = None,
        hotswap: typing.Optional[HotswapMode] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        outputs_file: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        progress: typing.Optional[StackActivityProgress] = None,
        require_approval: typing.Optional[RequireApproval] = None,
        reuse_assets: typing.Optional[typing.Sequence[builtins.str]] = None,
        rollback: typing.Optional[builtins.bool] = None,
        toolkit_stack_name: typing.Optional[builtins.str] = None,
        use_previous_parameters: typing.Optional[builtins.bool] = None,
        asset_metadata: typing.Optional[builtins.bool] = None,
        ca_bundle_path: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.bool] = None,
        context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        debug: typing.Optional[builtins.bool] = None,
        ec2_creds: typing.Optional[builtins.bool] = None,
        ignore_errors: typing.Optional[builtins.bool] = None,
        json: typing.Optional[builtins.bool] = None,
        lookups: typing.Optional[builtins.bool] = None,
        notices: typing.Optional[builtins.bool] = None,
        path_metadata: typing.Optional[builtins.bool] = None,
        profile: typing.Optional[builtins.str] = None,
        proxy: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        stacks: typing.Optional[typing.Sequence[builtins.str]] = None,
        staging: typing.Optional[builtins.bool] = None,
        strict: typing.Optional[builtins.bool] = None,
        trace: typing.Optional[builtins.bool] = None,
        verbose: typing.Optional[builtins.bool] = None,
        version_reporting: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(deprecated) cdk deploy.

        :param asset_parallelism: (deprecated) Whether to build/publish assets in parallel. Default: false
        :param asset_prebuild: (deprecated) Whether to build all assets before deploying the first stack (useful for failing Docker builds). Default: true
        :param change_set_name: (deprecated) Optional name to use for the CloudFormation change set. If not provided, a name will be generated automatically. Default: - auto generate a name
        :param ci: (deprecated) Whether we are on a CI system. Default: - ``false`` unless the environment variable ``CI`` is set
        :param concurrency: (deprecated) Maximum number of simultaneous deployments (dependency permitting) to execute. Default: 1
        :param exclusively: (deprecated) Only perform action on the given stack. Default: false
        :param execute: (deprecated) Whether to execute the ChangeSet Not providing ``execute`` parameter will result in execution of ChangeSet. Default: true
        :param force: (deprecated) Always deploy, even if templates are identical. Default: false
        :param hotswap: 
        :param notification_arns: (deprecated) ARNs of SNS topics that CloudFormation will notify with stack related events. Default: - no notifications
        :param outputs_file: (deprecated) Path to file where stack outputs will be written after a successful deploy as JSON. Default: - Outputs are not written to any file
        :param parameters: (deprecated) Additional parameters for CloudFormation at deploy time. Default: {}
        :param progress: (deprecated) Display mode for stack activity events. The default in the CLI is StackActivityProgress.BAR. But since this is an API it makes more sense to set the default to StackActivityProgress.EVENTS Default: StackActivityProgress.EVENTS
        :param require_approval: (deprecated) What kind of security changes require approval. Default: RequireApproval.NEVER
        :param reuse_assets: (deprecated) Reuse the assets with the given asset IDs. Default: - do not reuse assets
        :param rollback: (deprecated) Rollback failed deployments. Default: true
        :param toolkit_stack_name: (deprecated) Name of the toolkit stack to use/deploy. Default: CDKToolkit
        :param use_previous_parameters: (deprecated) Use previous values for unspecified parameters. If not set, all parameters must be specified for every deployment. Default: true
        :param asset_metadata: (deprecated) Include "aws:asset:*" CloudFormation metadata for resources that use assets. Default: true
        :param ca_bundle_path: (deprecated) Path to CA certificate to use when validating HTTPS requests. Default: - read from AWS_CA_BUNDLE environment variable
        :param color: (deprecated) Show colors and other style from console output. Default: - ``true`` unless the environment variable ``NO_COLOR`` is set
        :param context: (deprecated) Additional context. Default: - no additional context
        :param debug: (deprecated) enable emission of additional debugging information, such as creation stack traces of tokens. Default: false
        :param ec2_creds: (deprecated) Force trying to fetch EC2 instance credentials. Default: - guess EC2 instance status
        :param ignore_errors: (deprecated) Ignores synthesis errors, which will likely produce an invalid output. Default: false
        :param json: (deprecated) Use JSON output instead of YAML when templates are printed to STDOUT. Default: false
        :param lookups: (deprecated) Perform context lookups. Synthesis fails if this is disabled and context lookups need to be performed Default: true
        :param notices: (deprecated) Show relevant notices. Default: true
        :param path_metadata: (deprecated) Include "aws:cdk:path" CloudFormation metadata for each resource. Default: true
        :param profile: (deprecated) Use the indicated AWS profile as the default environment. Default: - no profile is used
        :param proxy: (deprecated) Use the indicated proxy. Will read from HTTPS_PROXY environment if specified Default: - no proxy
        :param role_arn: (deprecated) Role to pass to CloudFormation for deployment. Default: - use the bootstrap cfn-exec role
        :param stacks: (deprecated) List of stacks to deploy. Default: - all stacks
        :param staging: (deprecated) Copy assets to the output directory. Needed for local debugging the source files with SAM CLI Default: false
        :param strict: (deprecated) Do not construct stacks with warnings. Default: false
        :param trace: (deprecated) Print trace for stack warnings. Default: false
        :param verbose: (deprecated) show debug logs. Default: false
        :param version_reporting: (deprecated) Include "AWS::CDK::Metadata" resource in synthesized templates. Default: true

        :stability: deprecated
        '''
        options = DeployOptions(
            asset_parallelism=asset_parallelism,
            asset_prebuild=asset_prebuild,
            change_set_name=change_set_name,
            ci=ci,
            concurrency=concurrency,
            exclusively=exclusively,
            execute=execute,
            force=force,
            hotswap=hotswap,
            notification_arns=notification_arns,
            outputs_file=outputs_file,
            parameters=parameters,
            progress=progress,
            require_approval=require_approval,
            reuse_assets=reuse_assets,
            rollback=rollback,
            toolkit_stack_name=toolkit_stack_name,
            use_previous_parameters=use_previous_parameters,
            asset_metadata=asset_metadata,
            ca_bundle_path=ca_bundle_path,
            color=color,
            context=context,
            debug=debug,
            ec2_creds=ec2_creds,
            ignore_errors=ignore_errors,
            json=json,
            lookups=lookups,
            notices=notices,
            path_metadata=path_metadata,
            profile=profile,
            proxy=proxy,
            role_arn=role_arn,
            stacks=stacks,
            staging=staging,
            strict=strict,
            trace=trace,
            verbose=verbose,
            version_reporting=version_reporting,
        )

        return typing.cast(None, jsii.ainvoke(self, "deploy", [options]))

    @jsii.member(jsii_name="destroy")
    def destroy(
        self,
        *,
        exclusively: typing.Optional[builtins.bool] = None,
        require_approval: typing.Optional[builtins.bool] = None,
        asset_metadata: typing.Optional[builtins.bool] = None,
        ca_bundle_path: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.bool] = None,
        context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        debug: typing.Optional[builtins.bool] = None,
        ec2_creds: typing.Optional[builtins.bool] = None,
        ignore_errors: typing.Optional[builtins.bool] = None,
        json: typing.Optional[builtins.bool] = None,
        lookups: typing.Optional[builtins.bool] = None,
        notices: typing.Optional[builtins.bool] = None,
        path_metadata: typing.Optional[builtins.bool] = None,
        profile: typing.Optional[builtins.str] = None,
        proxy: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        stacks: typing.Optional[typing.Sequence[builtins.str]] = None,
        staging: typing.Optional[builtins.bool] = None,
        strict: typing.Optional[builtins.bool] = None,
        trace: typing.Optional[builtins.bool] = None,
        verbose: typing.Optional[builtins.bool] = None,
        version_reporting: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(deprecated) cdk destroy.

        :param exclusively: (deprecated) Only destroy the given stack. Default: false
        :param require_approval: (deprecated) Should the script prompt for approval before destroying stacks. Default: false
        :param asset_metadata: (deprecated) Include "aws:asset:*" CloudFormation metadata for resources that use assets. Default: true
        :param ca_bundle_path: (deprecated) Path to CA certificate to use when validating HTTPS requests. Default: - read from AWS_CA_BUNDLE environment variable
        :param color: (deprecated) Show colors and other style from console output. Default: - ``true`` unless the environment variable ``NO_COLOR`` is set
        :param context: (deprecated) Additional context. Default: - no additional context
        :param debug: (deprecated) enable emission of additional debugging information, such as creation stack traces of tokens. Default: false
        :param ec2_creds: (deprecated) Force trying to fetch EC2 instance credentials. Default: - guess EC2 instance status
        :param ignore_errors: (deprecated) Ignores synthesis errors, which will likely produce an invalid output. Default: false
        :param json: (deprecated) Use JSON output instead of YAML when templates are printed to STDOUT. Default: false
        :param lookups: (deprecated) Perform context lookups. Synthesis fails if this is disabled and context lookups need to be performed Default: true
        :param notices: (deprecated) Show relevant notices. Default: true
        :param path_metadata: (deprecated) Include "aws:cdk:path" CloudFormation metadata for each resource. Default: true
        :param profile: (deprecated) Use the indicated AWS profile as the default environment. Default: - no profile is used
        :param proxy: (deprecated) Use the indicated proxy. Will read from HTTPS_PROXY environment if specified Default: - no proxy
        :param role_arn: (deprecated) Role to pass to CloudFormation for deployment. Default: - use the bootstrap cfn-exec role
        :param stacks: (deprecated) List of stacks to deploy. Default: - all stacks
        :param staging: (deprecated) Copy assets to the output directory. Needed for local debugging the source files with SAM CLI Default: false
        :param strict: (deprecated) Do not construct stacks with warnings. Default: false
        :param trace: (deprecated) Print trace for stack warnings. Default: false
        :param verbose: (deprecated) show debug logs. Default: false
        :param version_reporting: (deprecated) Include "AWS::CDK::Metadata" resource in synthesized templates. Default: true

        :stability: deprecated
        '''
        options = DestroyOptions(
            exclusively=exclusively,
            require_approval=require_approval,
            asset_metadata=asset_metadata,
            ca_bundle_path=ca_bundle_path,
            color=color,
            context=context,
            debug=debug,
            ec2_creds=ec2_creds,
            ignore_errors=ignore_errors,
            json=json,
            lookups=lookups,
            notices=notices,
            path_metadata=path_metadata,
            profile=profile,
            proxy=proxy,
            role_arn=role_arn,
            stacks=stacks,
            staging=staging,
            strict=strict,
            trace=trace,
            verbose=verbose,
            version_reporting=version_reporting,
        )

        return typing.cast(None, jsii.ainvoke(self, "destroy", [options]))

    @jsii.member(jsii_name="list")
    def list(
        self,
        *,
        long: typing.Optional[builtins.bool] = None,
        asset_metadata: typing.Optional[builtins.bool] = None,
        ca_bundle_path: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.bool] = None,
        context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        debug: typing.Optional[builtins.bool] = None,
        ec2_creds: typing.Optional[builtins.bool] = None,
        ignore_errors: typing.Optional[builtins.bool] = None,
        json: typing.Optional[builtins.bool] = None,
        lookups: typing.Optional[builtins.bool] = None,
        notices: typing.Optional[builtins.bool] = None,
        path_metadata: typing.Optional[builtins.bool] = None,
        profile: typing.Optional[builtins.str] = None,
        proxy: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        stacks: typing.Optional[typing.Sequence[builtins.str]] = None,
        staging: typing.Optional[builtins.bool] = None,
        strict: typing.Optional[builtins.bool] = None,
        trace: typing.Optional[builtins.bool] = None,
        verbose: typing.Optional[builtins.bool] = None,
        version_reporting: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(deprecated) cdk list.

        :param long: (deprecated) Display environment information for each stack. Default: false
        :param asset_metadata: (deprecated) Include "aws:asset:*" CloudFormation metadata for resources that use assets. Default: true
        :param ca_bundle_path: (deprecated) Path to CA certificate to use when validating HTTPS requests. Default: - read from AWS_CA_BUNDLE environment variable
        :param color: (deprecated) Show colors and other style from console output. Default: - ``true`` unless the environment variable ``NO_COLOR`` is set
        :param context: (deprecated) Additional context. Default: - no additional context
        :param debug: (deprecated) enable emission of additional debugging information, such as creation stack traces of tokens. Default: false
        :param ec2_creds: (deprecated) Force trying to fetch EC2 instance credentials. Default: - guess EC2 instance status
        :param ignore_errors: (deprecated) Ignores synthesis errors, which will likely produce an invalid output. Default: false
        :param json: (deprecated) Use JSON output instead of YAML when templates are printed to STDOUT. Default: false
        :param lookups: (deprecated) Perform context lookups. Synthesis fails if this is disabled and context lookups need to be performed Default: true
        :param notices: (deprecated) Show relevant notices. Default: true
        :param path_metadata: (deprecated) Include "aws:cdk:path" CloudFormation metadata for each resource. Default: true
        :param profile: (deprecated) Use the indicated AWS profile as the default environment. Default: - no profile is used
        :param proxy: (deprecated) Use the indicated proxy. Will read from HTTPS_PROXY environment if specified Default: - no proxy
        :param role_arn: (deprecated) Role to pass to CloudFormation for deployment. Default: - use the bootstrap cfn-exec role
        :param stacks: (deprecated) List of stacks to deploy. Default: - all stacks
        :param staging: (deprecated) Copy assets to the output directory. Needed for local debugging the source files with SAM CLI Default: false
        :param strict: (deprecated) Do not construct stacks with warnings. Default: false
        :param trace: (deprecated) Print trace for stack warnings. Default: false
        :param verbose: (deprecated) show debug logs. Default: false
        :param version_reporting: (deprecated) Include "AWS::CDK::Metadata" resource in synthesized templates. Default: true

        :stability: deprecated
        '''
        options = ListOptions(
            long=long,
            asset_metadata=asset_metadata,
            ca_bundle_path=ca_bundle_path,
            color=color,
            context=context,
            debug=debug,
            ec2_creds=ec2_creds,
            ignore_errors=ignore_errors,
            json=json,
            lookups=lookups,
            notices=notices,
            path_metadata=path_metadata,
            profile=profile,
            proxy=proxy,
            role_arn=role_arn,
            stacks=stacks,
            staging=staging,
            strict=strict,
            trace=trace,
            verbose=verbose,
            version_reporting=version_reporting,
        )

        return typing.cast(None, jsii.ainvoke(self, "list", [options]))

    @jsii.member(jsii_name="synth")
    def synth(
        self,
        *,
        exclusively: typing.Optional[builtins.bool] = None,
        quiet: typing.Optional[builtins.bool] = None,
        validation: typing.Optional[builtins.bool] = None,
        asset_metadata: typing.Optional[builtins.bool] = None,
        ca_bundle_path: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.bool] = None,
        context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        debug: typing.Optional[builtins.bool] = None,
        ec2_creds: typing.Optional[builtins.bool] = None,
        ignore_errors: typing.Optional[builtins.bool] = None,
        json: typing.Optional[builtins.bool] = None,
        lookups: typing.Optional[builtins.bool] = None,
        notices: typing.Optional[builtins.bool] = None,
        path_metadata: typing.Optional[builtins.bool] = None,
        profile: typing.Optional[builtins.str] = None,
        proxy: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        stacks: typing.Optional[typing.Sequence[builtins.str]] = None,
        staging: typing.Optional[builtins.bool] = None,
        strict: typing.Optional[builtins.bool] = None,
        trace: typing.Optional[builtins.bool] = None,
        verbose: typing.Optional[builtins.bool] = None,
        version_reporting: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(deprecated) cdk synth.

        :param exclusively: (deprecated) Only synthesize the given stack. Default: false
        :param quiet: (deprecated) Do not output CloudFormation Template to stdout. Default: false;
        :param validation: (deprecated) After synthesis, validate stacks with the "validateOnSynth" attribute set (can also be controlled with CDK_VALIDATION). Default: true;
        :param asset_metadata: (deprecated) Include "aws:asset:*" CloudFormation metadata for resources that use assets. Default: true
        :param ca_bundle_path: (deprecated) Path to CA certificate to use when validating HTTPS requests. Default: - read from AWS_CA_BUNDLE environment variable
        :param color: (deprecated) Show colors and other style from console output. Default: - ``true`` unless the environment variable ``NO_COLOR`` is set
        :param context: (deprecated) Additional context. Default: - no additional context
        :param debug: (deprecated) enable emission of additional debugging information, such as creation stack traces of tokens. Default: false
        :param ec2_creds: (deprecated) Force trying to fetch EC2 instance credentials. Default: - guess EC2 instance status
        :param ignore_errors: (deprecated) Ignores synthesis errors, which will likely produce an invalid output. Default: false
        :param json: (deprecated) Use JSON output instead of YAML when templates are printed to STDOUT. Default: false
        :param lookups: (deprecated) Perform context lookups. Synthesis fails if this is disabled and context lookups need to be performed Default: true
        :param notices: (deprecated) Show relevant notices. Default: true
        :param path_metadata: (deprecated) Include "aws:cdk:path" CloudFormation metadata for each resource. Default: true
        :param profile: (deprecated) Use the indicated AWS profile as the default environment. Default: - no profile is used
        :param proxy: (deprecated) Use the indicated proxy. Will read from HTTPS_PROXY environment if specified Default: - no proxy
        :param role_arn: (deprecated) Role to pass to CloudFormation for deployment. Default: - use the bootstrap cfn-exec role
        :param stacks: (deprecated) List of stacks to deploy. Default: - all stacks
        :param staging: (deprecated) Copy assets to the output directory. Needed for local debugging the source files with SAM CLI Default: false
        :param strict: (deprecated) Do not construct stacks with warnings. Default: false
        :param trace: (deprecated) Print trace for stack warnings. Default: false
        :param verbose: (deprecated) show debug logs. Default: false
        :param version_reporting: (deprecated) Include "AWS::CDK::Metadata" resource in synthesized templates. Default: true

        :stability: deprecated
        '''
        options = SynthOptions(
            exclusively=exclusively,
            quiet=quiet,
            validation=validation,
            asset_metadata=asset_metadata,
            ca_bundle_path=ca_bundle_path,
            color=color,
            context=context,
            debug=debug,
            ec2_creds=ec2_creds,
            ignore_errors=ignore_errors,
            json=json,
            lookups=lookups,
            notices=notices,
            path_metadata=path_metadata,
            profile=profile,
            proxy=proxy,
            role_arn=role_arn,
            stacks=stacks,
            staging=staging,
            strict=strict,
            trace=trace,
            verbose=verbose,
            version_reporting=version_reporting,
        )

        return typing.cast(None, jsii.ainvoke(self, "synth", [options]))


@jsii.data_type(
    jsii_type="@aws-cdk/cli-lib-alpha.BootstrapOptions",
    jsii_struct_bases=[SharedOptions],
    name_mapping={
        "asset_metadata": "assetMetadata",
        "ca_bundle_path": "caBundlePath",
        "color": "color",
        "context": "context",
        "debug": "debug",
        "ec2_creds": "ec2Creds",
        "ignore_errors": "ignoreErrors",
        "json": "json",
        "lookups": "lookups",
        "notices": "notices",
        "path_metadata": "pathMetadata",
        "profile": "profile",
        "proxy": "proxy",
        "role_arn": "roleArn",
        "stacks": "stacks",
        "staging": "staging",
        "strict": "strict",
        "trace": "trace",
        "verbose": "verbose",
        "version_reporting": "versionReporting",
        "bootstrap_bucket_name": "bootstrapBucketName",
        "bootstrap_customer_key": "bootstrapCustomerKey",
        "bootstrap_kms_key_id": "bootstrapKmsKeyId",
        "cfn_execution_policy": "cfnExecutionPolicy",
        "custom_permissions_boundary": "customPermissionsBoundary",
        "environments": "environments",
        "example_permissions_boundary": "examplePermissionsBoundary",
        "execute": "execute",
        "force": "force",
        "public_access_block_configuration": "publicAccessBlockConfiguration",
        "qualifier": "qualifier",
        "show_template": "showTemplate",
        "template": "template",
        "termination_protection": "terminationProtection",
        "toolkit_stack_name": "toolkitStackName",
        "trust": "trust",
        "trust_for_lookup": "trustForLookup",
        "use_previous_parameters": "usePreviousParameters",
    },
)
class BootstrapOptions(SharedOptions):
    def __init__(
        self,
        *,
        asset_metadata: typing.Optional[builtins.bool] = None,
        ca_bundle_path: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.bool] = None,
        context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        debug: typing.Optional[builtins.bool] = None,
        ec2_creds: typing.Optional[builtins.bool] = None,
        ignore_errors: typing.Optional[builtins.bool] = None,
        json: typing.Optional[builtins.bool] = None,
        lookups: typing.Optional[builtins.bool] = None,
        notices: typing.Optional[builtins.bool] = None,
        path_metadata: typing.Optional[builtins.bool] = None,
        profile: typing.Optional[builtins.str] = None,
        proxy: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        stacks: typing.Optional[typing.Sequence[builtins.str]] = None,
        staging: typing.Optional[builtins.bool] = None,
        strict: typing.Optional[builtins.bool] = None,
        trace: typing.Optional[builtins.bool] = None,
        verbose: typing.Optional[builtins.bool] = None,
        version_reporting: typing.Optional[builtins.bool] = None,
        bootstrap_bucket_name: typing.Optional[builtins.str] = None,
        bootstrap_customer_key: typing.Optional[builtins.str] = None,
        bootstrap_kms_key_id: typing.Optional[builtins.str] = None,
        cfn_execution_policy: typing.Optional[builtins.str] = None,
        custom_permissions_boundary: typing.Optional[builtins.str] = None,
        environments: typing.Optional[typing.Sequence[builtins.str]] = None,
        example_permissions_boundary: typing.Optional[builtins.bool] = None,
        execute: typing.Optional[builtins.bool] = None,
        force: typing.Optional[builtins.bool] = None,
        public_access_block_configuration: typing.Optional[builtins.str] = None,
        qualifier: typing.Optional[builtins.str] = None,
        show_template: typing.Optional[builtins.bool] = None,
        template: typing.Optional[builtins.str] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        toolkit_stack_name: typing.Optional[builtins.str] = None,
        trust: typing.Optional[builtins.str] = None,
        trust_for_lookup: typing.Optional[builtins.str] = None,
        use_previous_parameters: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(deprecated) Options to use with cdk bootstrap.

        :param asset_metadata: (deprecated) Include "aws:asset:*" CloudFormation metadata for resources that use assets. Default: true
        :param ca_bundle_path: (deprecated) Path to CA certificate to use when validating HTTPS requests. Default: - read from AWS_CA_BUNDLE environment variable
        :param color: (deprecated) Show colors and other style from console output. Default: - ``true`` unless the environment variable ``NO_COLOR`` is set
        :param context: (deprecated) Additional context. Default: - no additional context
        :param debug: (deprecated) enable emission of additional debugging information, such as creation stack traces of tokens. Default: false
        :param ec2_creds: (deprecated) Force trying to fetch EC2 instance credentials. Default: - guess EC2 instance status
        :param ignore_errors: (deprecated) Ignores synthesis errors, which will likely produce an invalid output. Default: false
        :param json: (deprecated) Use JSON output instead of YAML when templates are printed to STDOUT. Default: false
        :param lookups: (deprecated) Perform context lookups. Synthesis fails if this is disabled and context lookups need to be performed Default: true
        :param notices: (deprecated) Show relevant notices. Default: true
        :param path_metadata: (deprecated) Include "aws:cdk:path" CloudFormation metadata for each resource. Default: true
        :param profile: (deprecated) Use the indicated AWS profile as the default environment. Default: - no profile is used
        :param proxy: (deprecated) Use the indicated proxy. Will read from HTTPS_PROXY environment if specified Default: - no proxy
        :param role_arn: (deprecated) Role to pass to CloudFormation for deployment. Default: - use the bootstrap cfn-exec role
        :param stacks: (deprecated) List of stacks to deploy. Default: - all stacks
        :param staging: (deprecated) Copy assets to the output directory. Needed for local debugging the source files with SAM CLI Default: false
        :param strict: (deprecated) Do not construct stacks with warnings. Default: false
        :param trace: (deprecated) Print trace for stack warnings. Default: false
        :param verbose: (deprecated) show debug logs. Default: false
        :param version_reporting: (deprecated) Include "AWS::CDK::Metadata" resource in synthesized templates. Default: true
        :param bootstrap_bucket_name: (deprecated) The name of the CDK toolkit bucket; bucket will be created and must not exist Default: - auto-generated CloudFormation name
        :param bootstrap_customer_key: (deprecated) Create a Customer Master Key (CMK) for the bootstrap bucket (you will be charged but can customize permissions, modern bootstrapping only). Default: undefined
        :param bootstrap_kms_key_id: (deprecated) AWS KMS master key ID used for the SSE-KMS encryption. Default: undefined
        :param cfn_execution_policy: (deprecated) The Managed Policy ARNs that should be attached to the role performing deployments into this environment (may be repeated, modern bootstrapping only). Default: - none
        :param custom_permissions_boundary: (deprecated) Use the permissions boundary specified by name. Default: undefined
        :param environments: (deprecated) The target AWS environments to deploy the bootstrap stack to. Uses the following format: ``aws://<account-id>/<region>`` Default: - Bootstrap all environments referenced in the CDK app or determine an environment from local configuration.
        :param example_permissions_boundary: (deprecated) Use the example permissions boundary. Default: undefined
        :param execute: (deprecated) Whether to execute ChangeSet (--no-execute will NOT execute the ChangeSet). Default: true
        :param force: (deprecated) Always bootstrap even if it would downgrade template version. Default: false
        :param public_access_block_configuration: (deprecated) Block public access configuration on CDK toolkit bucket (enabled by default). Default: undefined
        :param qualifier: (deprecated) String which must be unique for each bootstrap stack. You must configure it on your CDK app if you change this from the default. Default: undefined
        :param show_template: (deprecated) Instead of actual bootstrapping, print the current CLI's bootstrapping template to stdout for customization. Default: false
        :param template: (deprecated) Use the template from the given file instead of the built-in one (use --show-template to obtain an example).
        :param termination_protection: (deprecated) Toggle CloudFormation termination protection on the bootstrap stacks. Default: false
        :param toolkit_stack_name: (deprecated) The name of the CDK toolkit stack to create.
        :param trust: (deprecated) The AWS account IDs that should be trusted to perform deployments into this environment (may be repeated, modern bootstrapping only). Default: undefined
        :param trust_for_lookup: (deprecated) The AWS account IDs that should be trusted to look up values in this environment (may be repeated, modern bootstrapping only). Default: undefined
        :param use_previous_parameters: (deprecated) Use previous values for existing parameters (you must specify all parameters on every deployment if this is disabled). Default: true

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__301cfa1f6f197da85fa27bad052a38a0837341d7d0e1901658cbcaf1c29d6582)
            check_type(argname="argument asset_metadata", value=asset_metadata, expected_type=type_hints["asset_metadata"])
            check_type(argname="argument ca_bundle_path", value=ca_bundle_path, expected_type=type_hints["ca_bundle_path"])
            check_type(argname="argument color", value=color, expected_type=type_hints["color"])
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
            check_type(argname="argument debug", value=debug, expected_type=type_hints["debug"])
            check_type(argname="argument ec2_creds", value=ec2_creds, expected_type=type_hints["ec2_creds"])
            check_type(argname="argument ignore_errors", value=ignore_errors, expected_type=type_hints["ignore_errors"])
            check_type(argname="argument json", value=json, expected_type=type_hints["json"])
            check_type(argname="argument lookups", value=lookups, expected_type=type_hints["lookups"])
            check_type(argname="argument notices", value=notices, expected_type=type_hints["notices"])
            check_type(argname="argument path_metadata", value=path_metadata, expected_type=type_hints["path_metadata"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
            check_type(argname="argument proxy", value=proxy, expected_type=type_hints["proxy"])
            check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
            check_type(argname="argument stacks", value=stacks, expected_type=type_hints["stacks"])
            check_type(argname="argument staging", value=staging, expected_type=type_hints["staging"])
            check_type(argname="argument strict", value=strict, expected_type=type_hints["strict"])
            check_type(argname="argument trace", value=trace, expected_type=type_hints["trace"])
            check_type(argname="argument verbose", value=verbose, expected_type=type_hints["verbose"])
            check_type(argname="argument version_reporting", value=version_reporting, expected_type=type_hints["version_reporting"])
            check_type(argname="argument bootstrap_bucket_name", value=bootstrap_bucket_name, expected_type=type_hints["bootstrap_bucket_name"])
            check_type(argname="argument bootstrap_customer_key", value=bootstrap_customer_key, expected_type=type_hints["bootstrap_customer_key"])
            check_type(argname="argument bootstrap_kms_key_id", value=bootstrap_kms_key_id, expected_type=type_hints["bootstrap_kms_key_id"])
            check_type(argname="argument cfn_execution_policy", value=cfn_execution_policy, expected_type=type_hints["cfn_execution_policy"])
            check_type(argname="argument custom_permissions_boundary", value=custom_permissions_boundary, expected_type=type_hints["custom_permissions_boundary"])
            check_type(argname="argument environments", value=environments, expected_type=type_hints["environments"])
            check_type(argname="argument example_permissions_boundary", value=example_permissions_boundary, expected_type=type_hints["example_permissions_boundary"])
            check_type(argname="argument execute", value=execute, expected_type=type_hints["execute"])
            check_type(argname="argument force", value=force, expected_type=type_hints["force"])
            check_type(argname="argument public_access_block_configuration", value=public_access_block_configuration, expected_type=type_hints["public_access_block_configuration"])
            check_type(argname="argument qualifier", value=qualifier, expected_type=type_hints["qualifier"])
            check_type(argname="argument show_template", value=show_template, expected_type=type_hints["show_template"])
            check_type(argname="argument template", value=template, expected_type=type_hints["template"])
            check_type(argname="argument termination_protection", value=termination_protection, expected_type=type_hints["termination_protection"])
            check_type(argname="argument toolkit_stack_name", value=toolkit_stack_name, expected_type=type_hints["toolkit_stack_name"])
            check_type(argname="argument trust", value=trust, expected_type=type_hints["trust"])
            check_type(argname="argument trust_for_lookup", value=trust_for_lookup, expected_type=type_hints["trust_for_lookup"])
            check_type(argname="argument use_previous_parameters", value=use_previous_parameters, expected_type=type_hints["use_previous_parameters"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if asset_metadata is not None:
            self._values["asset_metadata"] = asset_metadata
        if ca_bundle_path is not None:
            self._values["ca_bundle_path"] = ca_bundle_path
        if color is not None:
            self._values["color"] = color
        if context is not None:
            self._values["context"] = context
        if debug is not None:
            self._values["debug"] = debug
        if ec2_creds is not None:
            self._values["ec2_creds"] = ec2_creds
        if ignore_errors is not None:
            self._values["ignore_errors"] = ignore_errors
        if json is not None:
            self._values["json"] = json
        if lookups is not None:
            self._values["lookups"] = lookups
        if notices is not None:
            self._values["notices"] = notices
        if path_metadata is not None:
            self._values["path_metadata"] = path_metadata
        if profile is not None:
            self._values["profile"] = profile
        if proxy is not None:
            self._values["proxy"] = proxy
        if role_arn is not None:
            self._values["role_arn"] = role_arn
        if stacks is not None:
            self._values["stacks"] = stacks
        if staging is not None:
            self._values["staging"] = staging
        if strict is not None:
            self._values["strict"] = strict
        if trace is not None:
            self._values["trace"] = trace
        if verbose is not None:
            self._values["verbose"] = verbose
        if version_reporting is not None:
            self._values["version_reporting"] = version_reporting
        if bootstrap_bucket_name is not None:
            self._values["bootstrap_bucket_name"] = bootstrap_bucket_name
        if bootstrap_customer_key is not None:
            self._values["bootstrap_customer_key"] = bootstrap_customer_key
        if bootstrap_kms_key_id is not None:
            self._values["bootstrap_kms_key_id"] = bootstrap_kms_key_id
        if cfn_execution_policy is not None:
            self._values["cfn_execution_policy"] = cfn_execution_policy
        if custom_permissions_boundary is not None:
            self._values["custom_permissions_boundary"] = custom_permissions_boundary
        if environments is not None:
            self._values["environments"] = environments
        if example_permissions_boundary is not None:
            self._values["example_permissions_boundary"] = example_permissions_boundary
        if execute is not None:
            self._values["execute"] = execute
        if force is not None:
            self._values["force"] = force
        if public_access_block_configuration is not None:
            self._values["public_access_block_configuration"] = public_access_block_configuration
        if qualifier is not None:
            self._values["qualifier"] = qualifier
        if show_template is not None:
            self._values["show_template"] = show_template
        if template is not None:
            self._values["template"] = template
        if termination_protection is not None:
            self._values["termination_protection"] = termination_protection
        if toolkit_stack_name is not None:
            self._values["toolkit_stack_name"] = toolkit_stack_name
        if trust is not None:
            self._values["trust"] = trust
        if trust_for_lookup is not None:
            self._values["trust_for_lookup"] = trust_for_lookup
        if use_previous_parameters is not None:
            self._values["use_previous_parameters"] = use_previous_parameters

    @builtins.property
    def asset_metadata(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Include "aws:asset:*" CloudFormation metadata for resources that use assets.

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("asset_metadata")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ca_bundle_path(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Path to CA certificate to use when validating HTTPS requests.

        :default: - read from AWS_CA_BUNDLE environment variable

        :stability: deprecated
        '''
        result = self._values.get("ca_bundle_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def color(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Show colors and other style from console output.

        :default: - ``true`` unless the environment variable ``NO_COLOR`` is set

        :stability: deprecated
        '''
        result = self._values.get("color")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def context(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(deprecated) Additional context.

        :default: - no additional context

        :stability: deprecated
        '''
        result = self._values.get("context")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def debug(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) enable emission of additional debugging information, such as creation stack traces of tokens.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("debug")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ec2_creds(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Force trying to fetch EC2 instance credentials.

        :default: - guess EC2 instance status

        :stability: deprecated
        '''
        result = self._values.get("ec2_creds")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ignore_errors(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Ignores synthesis errors, which will likely produce an invalid output.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("ignore_errors")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def json(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Use JSON output instead of YAML when templates are printed to STDOUT.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("json")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def lookups(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Perform context lookups.

        Synthesis fails if this is disabled and context lookups need
        to be performed

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("lookups")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def notices(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Show relevant notices.

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("notices")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def path_metadata(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Include "aws:cdk:path" CloudFormation metadata for each resource.

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("path_metadata")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def profile(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Use the indicated AWS profile as the default environment.

        :default: - no profile is used

        :stability: deprecated
        '''
        result = self._values.get("profile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def proxy(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Use the indicated proxy.

        Will read from
        HTTPS_PROXY environment if specified

        :default: - no proxy

        :stability: deprecated
        '''
        result = self._values.get("proxy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role_arn(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Role to pass to CloudFormation for deployment.

        :default: - use the bootstrap cfn-exec role

        :stability: deprecated
        '''
        result = self._values.get("role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stacks(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(deprecated) List of stacks to deploy.

        :default: - all stacks

        :stability: deprecated
        '''
        result = self._values.get("stacks")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def staging(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Copy assets to the output directory.

        Needed for local debugging the source files with SAM CLI

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("staging")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def strict(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Do not construct stacks with warnings.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("strict")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def trace(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Print trace for stack warnings.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("trace")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def verbose(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) show debug logs.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("verbose")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def version_reporting(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Include "AWS::CDK::Metadata" resource in synthesized templates.

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("version_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def bootstrap_bucket_name(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The name of the CDK toolkit bucket;

        bucket will be created and
        must not exist

        :default: - auto-generated CloudFormation name

        :stability: deprecated
        '''
        result = self._values.get("bootstrap_bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bootstrap_customer_key(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Create a Customer Master Key (CMK) for the bootstrap bucket (you will be charged but can customize permissions, modern bootstrapping only).

        :default: undefined

        :stability: deprecated
        '''
        result = self._values.get("bootstrap_customer_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bootstrap_kms_key_id(self) -> typing.Optional[builtins.str]:
        '''(deprecated) AWS KMS master key ID used for the SSE-KMS encryption.

        :default: undefined

        :stability: deprecated
        '''
        result = self._values.get("bootstrap_kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cfn_execution_policy(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The Managed Policy ARNs that should be attached to the role performing deployments into this environment (may be repeated, modern bootstrapping only).

        :default: - none

        :stability: deprecated
        '''
        result = self._values.get("cfn_execution_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_permissions_boundary(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Use the permissions boundary specified by name.

        :default: undefined

        :stability: deprecated
        '''
        result = self._values.get("custom_permissions_boundary")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environments(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(deprecated) The target AWS environments to deploy the bootstrap stack to.

        Uses the following format: ``aws://<account-id>/<region>``

        :default: - Bootstrap all environments referenced in the CDK app or determine an environment from local configuration.

        :stability: deprecated

        Example::

            "aws://123456789012/us-east-1"
        '''
        result = self._values.get("environments")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def example_permissions_boundary(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Use the example permissions boundary.

        :default: undefined

        :stability: deprecated
        '''
        result = self._values.get("example_permissions_boundary")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def execute(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Whether to execute ChangeSet (--no-execute will NOT execute the ChangeSet).

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("execute")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def force(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Always bootstrap even if it would downgrade template version.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("force")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def public_access_block_configuration(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Block public access configuration on CDK toolkit bucket (enabled by default).

        :default: undefined

        :stability: deprecated
        '''
        result = self._values.get("public_access_block_configuration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def qualifier(self) -> typing.Optional[builtins.str]:
        '''(deprecated) String which must be unique for each bootstrap stack.

        You
        must configure it on your CDK app if you change this
        from the default.

        :default: undefined

        :stability: deprecated
        '''
        result = self._values.get("qualifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def show_template(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Instead of actual bootstrapping, print the current CLI's bootstrapping template to stdout for customization.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("show_template")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def template(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Use the template from the given file instead of the built-in one (use --show-template to obtain an example).

        :stability: deprecated
        '''
        result = self._values.get("template")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def termination_protection(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Toggle CloudFormation termination protection on the bootstrap stacks.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def toolkit_stack_name(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The name of the CDK toolkit stack to create.

        :stability: deprecated
        '''
        result = self._values.get("toolkit_stack_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def trust(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The AWS account IDs that should be trusted to perform deployments into this environment (may be repeated, modern bootstrapping only).

        :default: undefined

        :stability: deprecated
        '''
        result = self._values.get("trust")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def trust_for_lookup(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The AWS account IDs that should be trusted to look up values in this environment (may be repeated, modern bootstrapping only).

        :default: undefined

        :stability: deprecated
        '''
        result = self._values.get("trust_for_lookup")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_previous_parameters(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Use previous values for existing parameters (you must specify all parameters on every deployment if this is disabled).

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("use_previous_parameters")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BootstrapOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/cli-lib-alpha.DeployOptions",
    jsii_struct_bases=[SharedOptions],
    name_mapping={
        "asset_metadata": "assetMetadata",
        "ca_bundle_path": "caBundlePath",
        "color": "color",
        "context": "context",
        "debug": "debug",
        "ec2_creds": "ec2Creds",
        "ignore_errors": "ignoreErrors",
        "json": "json",
        "lookups": "lookups",
        "notices": "notices",
        "path_metadata": "pathMetadata",
        "profile": "profile",
        "proxy": "proxy",
        "role_arn": "roleArn",
        "stacks": "stacks",
        "staging": "staging",
        "strict": "strict",
        "trace": "trace",
        "verbose": "verbose",
        "version_reporting": "versionReporting",
        "asset_parallelism": "assetParallelism",
        "asset_prebuild": "assetPrebuild",
        "change_set_name": "changeSetName",
        "ci": "ci",
        "concurrency": "concurrency",
        "exclusively": "exclusively",
        "execute": "execute",
        "force": "force",
        "hotswap": "hotswap",
        "notification_arns": "notificationArns",
        "outputs_file": "outputsFile",
        "parameters": "parameters",
        "progress": "progress",
        "require_approval": "requireApproval",
        "reuse_assets": "reuseAssets",
        "rollback": "rollback",
        "toolkit_stack_name": "toolkitStackName",
        "use_previous_parameters": "usePreviousParameters",
    },
)
class DeployOptions(SharedOptions):
    def __init__(
        self,
        *,
        asset_metadata: typing.Optional[builtins.bool] = None,
        ca_bundle_path: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.bool] = None,
        context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        debug: typing.Optional[builtins.bool] = None,
        ec2_creds: typing.Optional[builtins.bool] = None,
        ignore_errors: typing.Optional[builtins.bool] = None,
        json: typing.Optional[builtins.bool] = None,
        lookups: typing.Optional[builtins.bool] = None,
        notices: typing.Optional[builtins.bool] = None,
        path_metadata: typing.Optional[builtins.bool] = None,
        profile: typing.Optional[builtins.str] = None,
        proxy: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        stacks: typing.Optional[typing.Sequence[builtins.str]] = None,
        staging: typing.Optional[builtins.bool] = None,
        strict: typing.Optional[builtins.bool] = None,
        trace: typing.Optional[builtins.bool] = None,
        verbose: typing.Optional[builtins.bool] = None,
        version_reporting: typing.Optional[builtins.bool] = None,
        asset_parallelism: typing.Optional[builtins.bool] = None,
        asset_prebuild: typing.Optional[builtins.bool] = None,
        change_set_name: typing.Optional[builtins.str] = None,
        ci: typing.Optional[builtins.bool] = None,
        concurrency: typing.Optional[jsii.Number] = None,
        exclusively: typing.Optional[builtins.bool] = None,
        execute: typing.Optional[builtins.bool] = None,
        force: typing.Optional[builtins.bool] = None,
        hotswap: typing.Optional[HotswapMode] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        outputs_file: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        progress: typing.Optional[StackActivityProgress] = None,
        require_approval: typing.Optional[RequireApproval] = None,
        reuse_assets: typing.Optional[typing.Sequence[builtins.str]] = None,
        rollback: typing.Optional[builtins.bool] = None,
        toolkit_stack_name: typing.Optional[builtins.str] = None,
        use_previous_parameters: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(deprecated) Options to use with cdk deploy.

        :param asset_metadata: (deprecated) Include "aws:asset:*" CloudFormation metadata for resources that use assets. Default: true
        :param ca_bundle_path: (deprecated) Path to CA certificate to use when validating HTTPS requests. Default: - read from AWS_CA_BUNDLE environment variable
        :param color: (deprecated) Show colors and other style from console output. Default: - ``true`` unless the environment variable ``NO_COLOR`` is set
        :param context: (deprecated) Additional context. Default: - no additional context
        :param debug: (deprecated) enable emission of additional debugging information, such as creation stack traces of tokens. Default: false
        :param ec2_creds: (deprecated) Force trying to fetch EC2 instance credentials. Default: - guess EC2 instance status
        :param ignore_errors: (deprecated) Ignores synthesis errors, which will likely produce an invalid output. Default: false
        :param json: (deprecated) Use JSON output instead of YAML when templates are printed to STDOUT. Default: false
        :param lookups: (deprecated) Perform context lookups. Synthesis fails if this is disabled and context lookups need to be performed Default: true
        :param notices: (deprecated) Show relevant notices. Default: true
        :param path_metadata: (deprecated) Include "aws:cdk:path" CloudFormation metadata for each resource. Default: true
        :param profile: (deprecated) Use the indicated AWS profile as the default environment. Default: - no profile is used
        :param proxy: (deprecated) Use the indicated proxy. Will read from HTTPS_PROXY environment if specified Default: - no proxy
        :param role_arn: (deprecated) Role to pass to CloudFormation for deployment. Default: - use the bootstrap cfn-exec role
        :param stacks: (deprecated) List of stacks to deploy. Default: - all stacks
        :param staging: (deprecated) Copy assets to the output directory. Needed for local debugging the source files with SAM CLI Default: false
        :param strict: (deprecated) Do not construct stacks with warnings. Default: false
        :param trace: (deprecated) Print trace for stack warnings. Default: false
        :param verbose: (deprecated) show debug logs. Default: false
        :param version_reporting: (deprecated) Include "AWS::CDK::Metadata" resource in synthesized templates. Default: true
        :param asset_parallelism: (deprecated) Whether to build/publish assets in parallel. Default: false
        :param asset_prebuild: (deprecated) Whether to build all assets before deploying the first stack (useful for failing Docker builds). Default: true
        :param change_set_name: (deprecated) Optional name to use for the CloudFormation change set. If not provided, a name will be generated automatically. Default: - auto generate a name
        :param ci: (deprecated) Whether we are on a CI system. Default: - ``false`` unless the environment variable ``CI`` is set
        :param concurrency: (deprecated) Maximum number of simultaneous deployments (dependency permitting) to execute. Default: 1
        :param exclusively: (deprecated) Only perform action on the given stack. Default: false
        :param execute: (deprecated) Whether to execute the ChangeSet Not providing ``execute`` parameter will result in execution of ChangeSet. Default: true
        :param force: (deprecated) Always deploy, even if templates are identical. Default: false
        :param hotswap: 
        :param notification_arns: (deprecated) ARNs of SNS topics that CloudFormation will notify with stack related events. Default: - no notifications
        :param outputs_file: (deprecated) Path to file where stack outputs will be written after a successful deploy as JSON. Default: - Outputs are not written to any file
        :param parameters: (deprecated) Additional parameters for CloudFormation at deploy time. Default: {}
        :param progress: (deprecated) Display mode for stack activity events. The default in the CLI is StackActivityProgress.BAR. But since this is an API it makes more sense to set the default to StackActivityProgress.EVENTS Default: StackActivityProgress.EVENTS
        :param require_approval: (deprecated) What kind of security changes require approval. Default: RequireApproval.NEVER
        :param reuse_assets: (deprecated) Reuse the assets with the given asset IDs. Default: - do not reuse assets
        :param rollback: (deprecated) Rollback failed deployments. Default: true
        :param toolkit_stack_name: (deprecated) Name of the toolkit stack to use/deploy. Default: CDKToolkit
        :param use_previous_parameters: (deprecated) Use previous values for unspecified parameters. If not set, all parameters must be specified for every deployment. Default: true

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b018eeefbacd83149d0e1a84a6c871f9439b9b3ae192abb0cdb3973220e72861)
            check_type(argname="argument asset_metadata", value=asset_metadata, expected_type=type_hints["asset_metadata"])
            check_type(argname="argument ca_bundle_path", value=ca_bundle_path, expected_type=type_hints["ca_bundle_path"])
            check_type(argname="argument color", value=color, expected_type=type_hints["color"])
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
            check_type(argname="argument debug", value=debug, expected_type=type_hints["debug"])
            check_type(argname="argument ec2_creds", value=ec2_creds, expected_type=type_hints["ec2_creds"])
            check_type(argname="argument ignore_errors", value=ignore_errors, expected_type=type_hints["ignore_errors"])
            check_type(argname="argument json", value=json, expected_type=type_hints["json"])
            check_type(argname="argument lookups", value=lookups, expected_type=type_hints["lookups"])
            check_type(argname="argument notices", value=notices, expected_type=type_hints["notices"])
            check_type(argname="argument path_metadata", value=path_metadata, expected_type=type_hints["path_metadata"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
            check_type(argname="argument proxy", value=proxy, expected_type=type_hints["proxy"])
            check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
            check_type(argname="argument stacks", value=stacks, expected_type=type_hints["stacks"])
            check_type(argname="argument staging", value=staging, expected_type=type_hints["staging"])
            check_type(argname="argument strict", value=strict, expected_type=type_hints["strict"])
            check_type(argname="argument trace", value=trace, expected_type=type_hints["trace"])
            check_type(argname="argument verbose", value=verbose, expected_type=type_hints["verbose"])
            check_type(argname="argument version_reporting", value=version_reporting, expected_type=type_hints["version_reporting"])
            check_type(argname="argument asset_parallelism", value=asset_parallelism, expected_type=type_hints["asset_parallelism"])
            check_type(argname="argument asset_prebuild", value=asset_prebuild, expected_type=type_hints["asset_prebuild"])
            check_type(argname="argument change_set_name", value=change_set_name, expected_type=type_hints["change_set_name"])
            check_type(argname="argument ci", value=ci, expected_type=type_hints["ci"])
            check_type(argname="argument concurrency", value=concurrency, expected_type=type_hints["concurrency"])
            check_type(argname="argument exclusively", value=exclusively, expected_type=type_hints["exclusively"])
            check_type(argname="argument execute", value=execute, expected_type=type_hints["execute"])
            check_type(argname="argument force", value=force, expected_type=type_hints["force"])
            check_type(argname="argument hotswap", value=hotswap, expected_type=type_hints["hotswap"])
            check_type(argname="argument notification_arns", value=notification_arns, expected_type=type_hints["notification_arns"])
            check_type(argname="argument outputs_file", value=outputs_file, expected_type=type_hints["outputs_file"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
            check_type(argname="argument progress", value=progress, expected_type=type_hints["progress"])
            check_type(argname="argument require_approval", value=require_approval, expected_type=type_hints["require_approval"])
            check_type(argname="argument reuse_assets", value=reuse_assets, expected_type=type_hints["reuse_assets"])
            check_type(argname="argument rollback", value=rollback, expected_type=type_hints["rollback"])
            check_type(argname="argument toolkit_stack_name", value=toolkit_stack_name, expected_type=type_hints["toolkit_stack_name"])
            check_type(argname="argument use_previous_parameters", value=use_previous_parameters, expected_type=type_hints["use_previous_parameters"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if asset_metadata is not None:
            self._values["asset_metadata"] = asset_metadata
        if ca_bundle_path is not None:
            self._values["ca_bundle_path"] = ca_bundle_path
        if color is not None:
            self._values["color"] = color
        if context is not None:
            self._values["context"] = context
        if debug is not None:
            self._values["debug"] = debug
        if ec2_creds is not None:
            self._values["ec2_creds"] = ec2_creds
        if ignore_errors is not None:
            self._values["ignore_errors"] = ignore_errors
        if json is not None:
            self._values["json"] = json
        if lookups is not None:
            self._values["lookups"] = lookups
        if notices is not None:
            self._values["notices"] = notices
        if path_metadata is not None:
            self._values["path_metadata"] = path_metadata
        if profile is not None:
            self._values["profile"] = profile
        if proxy is not None:
            self._values["proxy"] = proxy
        if role_arn is not None:
            self._values["role_arn"] = role_arn
        if stacks is not None:
            self._values["stacks"] = stacks
        if staging is not None:
            self._values["staging"] = staging
        if strict is not None:
            self._values["strict"] = strict
        if trace is not None:
            self._values["trace"] = trace
        if verbose is not None:
            self._values["verbose"] = verbose
        if version_reporting is not None:
            self._values["version_reporting"] = version_reporting
        if asset_parallelism is not None:
            self._values["asset_parallelism"] = asset_parallelism
        if asset_prebuild is not None:
            self._values["asset_prebuild"] = asset_prebuild
        if change_set_name is not None:
            self._values["change_set_name"] = change_set_name
        if ci is not None:
            self._values["ci"] = ci
        if concurrency is not None:
            self._values["concurrency"] = concurrency
        if exclusively is not None:
            self._values["exclusively"] = exclusively
        if execute is not None:
            self._values["execute"] = execute
        if force is not None:
            self._values["force"] = force
        if hotswap is not None:
            self._values["hotswap"] = hotswap
        if notification_arns is not None:
            self._values["notification_arns"] = notification_arns
        if outputs_file is not None:
            self._values["outputs_file"] = outputs_file
        if parameters is not None:
            self._values["parameters"] = parameters
        if progress is not None:
            self._values["progress"] = progress
        if require_approval is not None:
            self._values["require_approval"] = require_approval
        if reuse_assets is not None:
            self._values["reuse_assets"] = reuse_assets
        if rollback is not None:
            self._values["rollback"] = rollback
        if toolkit_stack_name is not None:
            self._values["toolkit_stack_name"] = toolkit_stack_name
        if use_previous_parameters is not None:
            self._values["use_previous_parameters"] = use_previous_parameters

    @builtins.property
    def asset_metadata(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Include "aws:asset:*" CloudFormation metadata for resources that use assets.

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("asset_metadata")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ca_bundle_path(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Path to CA certificate to use when validating HTTPS requests.

        :default: - read from AWS_CA_BUNDLE environment variable

        :stability: deprecated
        '''
        result = self._values.get("ca_bundle_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def color(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Show colors and other style from console output.

        :default: - ``true`` unless the environment variable ``NO_COLOR`` is set

        :stability: deprecated
        '''
        result = self._values.get("color")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def context(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(deprecated) Additional context.

        :default: - no additional context

        :stability: deprecated
        '''
        result = self._values.get("context")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def debug(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) enable emission of additional debugging information, such as creation stack traces of tokens.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("debug")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ec2_creds(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Force trying to fetch EC2 instance credentials.

        :default: - guess EC2 instance status

        :stability: deprecated
        '''
        result = self._values.get("ec2_creds")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ignore_errors(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Ignores synthesis errors, which will likely produce an invalid output.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("ignore_errors")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def json(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Use JSON output instead of YAML when templates are printed to STDOUT.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("json")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def lookups(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Perform context lookups.

        Synthesis fails if this is disabled and context lookups need
        to be performed

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("lookups")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def notices(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Show relevant notices.

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("notices")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def path_metadata(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Include "aws:cdk:path" CloudFormation metadata for each resource.

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("path_metadata")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def profile(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Use the indicated AWS profile as the default environment.

        :default: - no profile is used

        :stability: deprecated
        '''
        result = self._values.get("profile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def proxy(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Use the indicated proxy.

        Will read from
        HTTPS_PROXY environment if specified

        :default: - no proxy

        :stability: deprecated
        '''
        result = self._values.get("proxy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role_arn(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Role to pass to CloudFormation for deployment.

        :default: - use the bootstrap cfn-exec role

        :stability: deprecated
        '''
        result = self._values.get("role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stacks(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(deprecated) List of stacks to deploy.

        :default: - all stacks

        :stability: deprecated
        '''
        result = self._values.get("stacks")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def staging(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Copy assets to the output directory.

        Needed for local debugging the source files with SAM CLI

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("staging")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def strict(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Do not construct stacks with warnings.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("strict")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def trace(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Print trace for stack warnings.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("trace")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def verbose(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) show debug logs.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("verbose")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def version_reporting(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Include "AWS::CDK::Metadata" resource in synthesized templates.

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("version_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def asset_parallelism(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Whether to build/publish assets in parallel.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("asset_parallelism")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def asset_prebuild(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Whether to build all assets before deploying the first stack (useful for failing Docker builds).

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("asset_prebuild")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def change_set_name(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Optional name to use for the CloudFormation change set.

        If not provided, a name will be generated automatically.

        :default: - auto generate a name

        :stability: deprecated
        '''
        result = self._values.get("change_set_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ci(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Whether we are on a CI system.

        :default: - ``false`` unless the environment variable ``CI`` is set

        :stability: deprecated
        '''
        result = self._values.get("ci")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def concurrency(self) -> typing.Optional[jsii.Number]:
        '''(deprecated) Maximum number of simultaneous deployments (dependency permitting) to execute.

        :default: 1

        :stability: deprecated
        '''
        result = self._values.get("concurrency")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def exclusively(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Only perform action on the given stack.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("exclusively")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def execute(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Whether to execute the ChangeSet Not providing ``execute`` parameter will result in execution of ChangeSet.

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("execute")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def force(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Always deploy, even if templates are identical.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("force")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def hotswap(self) -> typing.Optional[HotswapMode]:
        '''
        :stability: deprecated
        '''
        result = self._values.get("hotswap")
        return typing.cast(typing.Optional[HotswapMode], result)

    @builtins.property
    def notification_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(deprecated) ARNs of SNS topics that CloudFormation will notify with stack related events.

        :default: - no notifications

        :stability: deprecated
        '''
        result = self._values.get("notification_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def outputs_file(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Path to file where stack outputs will be written after a successful deploy as JSON.

        :default: - Outputs are not written to any file

        :stability: deprecated
        '''
        result = self._values.get("outputs_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(deprecated) Additional parameters for CloudFormation at deploy time.

        :default: {}

        :stability: deprecated
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def progress(self) -> typing.Optional[StackActivityProgress]:
        '''(deprecated) Display mode for stack activity events.

        The default in the CLI is StackActivityProgress.BAR. But since this is an API
        it makes more sense to set the default to StackActivityProgress.EVENTS

        :default: StackActivityProgress.EVENTS

        :stability: deprecated
        '''
        result = self._values.get("progress")
        return typing.cast(typing.Optional[StackActivityProgress], result)

    @builtins.property
    def require_approval(self) -> typing.Optional[RequireApproval]:
        '''(deprecated) What kind of security changes require approval.

        :default: RequireApproval.NEVER

        :stability: deprecated
        '''
        result = self._values.get("require_approval")
        return typing.cast(typing.Optional[RequireApproval], result)

    @builtins.property
    def reuse_assets(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(deprecated) Reuse the assets with the given asset IDs.

        :default: - do not reuse assets

        :stability: deprecated
        '''
        result = self._values.get("reuse_assets")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def rollback(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Rollback failed deployments.

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("rollback")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def toolkit_stack_name(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Name of the toolkit stack to use/deploy.

        :default: CDKToolkit

        :stability: deprecated
        '''
        result = self._values.get("toolkit_stack_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_previous_parameters(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Use previous values for unspecified parameters.

        If not set, all parameters must be specified for every deployment.

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("use_previous_parameters")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DeployOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/cli-lib-alpha.DestroyOptions",
    jsii_struct_bases=[SharedOptions],
    name_mapping={
        "asset_metadata": "assetMetadata",
        "ca_bundle_path": "caBundlePath",
        "color": "color",
        "context": "context",
        "debug": "debug",
        "ec2_creds": "ec2Creds",
        "ignore_errors": "ignoreErrors",
        "json": "json",
        "lookups": "lookups",
        "notices": "notices",
        "path_metadata": "pathMetadata",
        "profile": "profile",
        "proxy": "proxy",
        "role_arn": "roleArn",
        "stacks": "stacks",
        "staging": "staging",
        "strict": "strict",
        "trace": "trace",
        "verbose": "verbose",
        "version_reporting": "versionReporting",
        "exclusively": "exclusively",
        "require_approval": "requireApproval",
    },
)
class DestroyOptions(SharedOptions):
    def __init__(
        self,
        *,
        asset_metadata: typing.Optional[builtins.bool] = None,
        ca_bundle_path: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.bool] = None,
        context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        debug: typing.Optional[builtins.bool] = None,
        ec2_creds: typing.Optional[builtins.bool] = None,
        ignore_errors: typing.Optional[builtins.bool] = None,
        json: typing.Optional[builtins.bool] = None,
        lookups: typing.Optional[builtins.bool] = None,
        notices: typing.Optional[builtins.bool] = None,
        path_metadata: typing.Optional[builtins.bool] = None,
        profile: typing.Optional[builtins.str] = None,
        proxy: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        stacks: typing.Optional[typing.Sequence[builtins.str]] = None,
        staging: typing.Optional[builtins.bool] = None,
        strict: typing.Optional[builtins.bool] = None,
        trace: typing.Optional[builtins.bool] = None,
        verbose: typing.Optional[builtins.bool] = None,
        version_reporting: typing.Optional[builtins.bool] = None,
        exclusively: typing.Optional[builtins.bool] = None,
        require_approval: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(deprecated) Options to use with cdk destroy.

        :param asset_metadata: (deprecated) Include "aws:asset:*" CloudFormation metadata for resources that use assets. Default: true
        :param ca_bundle_path: (deprecated) Path to CA certificate to use when validating HTTPS requests. Default: - read from AWS_CA_BUNDLE environment variable
        :param color: (deprecated) Show colors and other style from console output. Default: - ``true`` unless the environment variable ``NO_COLOR`` is set
        :param context: (deprecated) Additional context. Default: - no additional context
        :param debug: (deprecated) enable emission of additional debugging information, such as creation stack traces of tokens. Default: false
        :param ec2_creds: (deprecated) Force trying to fetch EC2 instance credentials. Default: - guess EC2 instance status
        :param ignore_errors: (deprecated) Ignores synthesis errors, which will likely produce an invalid output. Default: false
        :param json: (deprecated) Use JSON output instead of YAML when templates are printed to STDOUT. Default: false
        :param lookups: (deprecated) Perform context lookups. Synthesis fails if this is disabled and context lookups need to be performed Default: true
        :param notices: (deprecated) Show relevant notices. Default: true
        :param path_metadata: (deprecated) Include "aws:cdk:path" CloudFormation metadata for each resource. Default: true
        :param profile: (deprecated) Use the indicated AWS profile as the default environment. Default: - no profile is used
        :param proxy: (deprecated) Use the indicated proxy. Will read from HTTPS_PROXY environment if specified Default: - no proxy
        :param role_arn: (deprecated) Role to pass to CloudFormation for deployment. Default: - use the bootstrap cfn-exec role
        :param stacks: (deprecated) List of stacks to deploy. Default: - all stacks
        :param staging: (deprecated) Copy assets to the output directory. Needed for local debugging the source files with SAM CLI Default: false
        :param strict: (deprecated) Do not construct stacks with warnings. Default: false
        :param trace: (deprecated) Print trace for stack warnings. Default: false
        :param verbose: (deprecated) show debug logs. Default: false
        :param version_reporting: (deprecated) Include "AWS::CDK::Metadata" resource in synthesized templates. Default: true
        :param exclusively: (deprecated) Only destroy the given stack. Default: false
        :param require_approval: (deprecated) Should the script prompt for approval before destroying stacks. Default: false

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb8504825518b32dce06268837b8bd1235a5475c17aab74a6939b8404467e09c)
            check_type(argname="argument asset_metadata", value=asset_metadata, expected_type=type_hints["asset_metadata"])
            check_type(argname="argument ca_bundle_path", value=ca_bundle_path, expected_type=type_hints["ca_bundle_path"])
            check_type(argname="argument color", value=color, expected_type=type_hints["color"])
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
            check_type(argname="argument debug", value=debug, expected_type=type_hints["debug"])
            check_type(argname="argument ec2_creds", value=ec2_creds, expected_type=type_hints["ec2_creds"])
            check_type(argname="argument ignore_errors", value=ignore_errors, expected_type=type_hints["ignore_errors"])
            check_type(argname="argument json", value=json, expected_type=type_hints["json"])
            check_type(argname="argument lookups", value=lookups, expected_type=type_hints["lookups"])
            check_type(argname="argument notices", value=notices, expected_type=type_hints["notices"])
            check_type(argname="argument path_metadata", value=path_metadata, expected_type=type_hints["path_metadata"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
            check_type(argname="argument proxy", value=proxy, expected_type=type_hints["proxy"])
            check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
            check_type(argname="argument stacks", value=stacks, expected_type=type_hints["stacks"])
            check_type(argname="argument staging", value=staging, expected_type=type_hints["staging"])
            check_type(argname="argument strict", value=strict, expected_type=type_hints["strict"])
            check_type(argname="argument trace", value=trace, expected_type=type_hints["trace"])
            check_type(argname="argument verbose", value=verbose, expected_type=type_hints["verbose"])
            check_type(argname="argument version_reporting", value=version_reporting, expected_type=type_hints["version_reporting"])
            check_type(argname="argument exclusively", value=exclusively, expected_type=type_hints["exclusively"])
            check_type(argname="argument require_approval", value=require_approval, expected_type=type_hints["require_approval"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if asset_metadata is not None:
            self._values["asset_metadata"] = asset_metadata
        if ca_bundle_path is not None:
            self._values["ca_bundle_path"] = ca_bundle_path
        if color is not None:
            self._values["color"] = color
        if context is not None:
            self._values["context"] = context
        if debug is not None:
            self._values["debug"] = debug
        if ec2_creds is not None:
            self._values["ec2_creds"] = ec2_creds
        if ignore_errors is not None:
            self._values["ignore_errors"] = ignore_errors
        if json is not None:
            self._values["json"] = json
        if lookups is not None:
            self._values["lookups"] = lookups
        if notices is not None:
            self._values["notices"] = notices
        if path_metadata is not None:
            self._values["path_metadata"] = path_metadata
        if profile is not None:
            self._values["profile"] = profile
        if proxy is not None:
            self._values["proxy"] = proxy
        if role_arn is not None:
            self._values["role_arn"] = role_arn
        if stacks is not None:
            self._values["stacks"] = stacks
        if staging is not None:
            self._values["staging"] = staging
        if strict is not None:
            self._values["strict"] = strict
        if trace is not None:
            self._values["trace"] = trace
        if verbose is not None:
            self._values["verbose"] = verbose
        if version_reporting is not None:
            self._values["version_reporting"] = version_reporting
        if exclusively is not None:
            self._values["exclusively"] = exclusively
        if require_approval is not None:
            self._values["require_approval"] = require_approval

    @builtins.property
    def asset_metadata(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Include "aws:asset:*" CloudFormation metadata for resources that use assets.

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("asset_metadata")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ca_bundle_path(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Path to CA certificate to use when validating HTTPS requests.

        :default: - read from AWS_CA_BUNDLE environment variable

        :stability: deprecated
        '''
        result = self._values.get("ca_bundle_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def color(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Show colors and other style from console output.

        :default: - ``true`` unless the environment variable ``NO_COLOR`` is set

        :stability: deprecated
        '''
        result = self._values.get("color")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def context(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(deprecated) Additional context.

        :default: - no additional context

        :stability: deprecated
        '''
        result = self._values.get("context")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def debug(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) enable emission of additional debugging information, such as creation stack traces of tokens.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("debug")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ec2_creds(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Force trying to fetch EC2 instance credentials.

        :default: - guess EC2 instance status

        :stability: deprecated
        '''
        result = self._values.get("ec2_creds")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ignore_errors(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Ignores synthesis errors, which will likely produce an invalid output.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("ignore_errors")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def json(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Use JSON output instead of YAML when templates are printed to STDOUT.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("json")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def lookups(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Perform context lookups.

        Synthesis fails if this is disabled and context lookups need
        to be performed

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("lookups")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def notices(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Show relevant notices.

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("notices")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def path_metadata(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Include "aws:cdk:path" CloudFormation metadata for each resource.

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("path_metadata")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def profile(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Use the indicated AWS profile as the default environment.

        :default: - no profile is used

        :stability: deprecated
        '''
        result = self._values.get("profile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def proxy(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Use the indicated proxy.

        Will read from
        HTTPS_PROXY environment if specified

        :default: - no proxy

        :stability: deprecated
        '''
        result = self._values.get("proxy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role_arn(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Role to pass to CloudFormation for deployment.

        :default: - use the bootstrap cfn-exec role

        :stability: deprecated
        '''
        result = self._values.get("role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stacks(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(deprecated) List of stacks to deploy.

        :default: - all stacks

        :stability: deprecated
        '''
        result = self._values.get("stacks")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def staging(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Copy assets to the output directory.

        Needed for local debugging the source files with SAM CLI

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("staging")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def strict(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Do not construct stacks with warnings.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("strict")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def trace(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Print trace for stack warnings.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("trace")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def verbose(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) show debug logs.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("verbose")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def version_reporting(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Include "AWS::CDK::Metadata" resource in synthesized templates.

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("version_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def exclusively(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Only destroy the given stack.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("exclusively")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def require_approval(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Should the script prompt for approval before destroying stacks.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("require_approval")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DestroyOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/cli-lib-alpha.ListOptions",
    jsii_struct_bases=[SharedOptions],
    name_mapping={
        "asset_metadata": "assetMetadata",
        "ca_bundle_path": "caBundlePath",
        "color": "color",
        "context": "context",
        "debug": "debug",
        "ec2_creds": "ec2Creds",
        "ignore_errors": "ignoreErrors",
        "json": "json",
        "lookups": "lookups",
        "notices": "notices",
        "path_metadata": "pathMetadata",
        "profile": "profile",
        "proxy": "proxy",
        "role_arn": "roleArn",
        "stacks": "stacks",
        "staging": "staging",
        "strict": "strict",
        "trace": "trace",
        "verbose": "verbose",
        "version_reporting": "versionReporting",
        "long": "long",
    },
)
class ListOptions(SharedOptions):
    def __init__(
        self,
        *,
        asset_metadata: typing.Optional[builtins.bool] = None,
        ca_bundle_path: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.bool] = None,
        context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        debug: typing.Optional[builtins.bool] = None,
        ec2_creds: typing.Optional[builtins.bool] = None,
        ignore_errors: typing.Optional[builtins.bool] = None,
        json: typing.Optional[builtins.bool] = None,
        lookups: typing.Optional[builtins.bool] = None,
        notices: typing.Optional[builtins.bool] = None,
        path_metadata: typing.Optional[builtins.bool] = None,
        profile: typing.Optional[builtins.str] = None,
        proxy: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        stacks: typing.Optional[typing.Sequence[builtins.str]] = None,
        staging: typing.Optional[builtins.bool] = None,
        strict: typing.Optional[builtins.bool] = None,
        trace: typing.Optional[builtins.bool] = None,
        verbose: typing.Optional[builtins.bool] = None,
        version_reporting: typing.Optional[builtins.bool] = None,
        long: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(deprecated) Options for cdk list.

        :param asset_metadata: (deprecated) Include "aws:asset:*" CloudFormation metadata for resources that use assets. Default: true
        :param ca_bundle_path: (deprecated) Path to CA certificate to use when validating HTTPS requests. Default: - read from AWS_CA_BUNDLE environment variable
        :param color: (deprecated) Show colors and other style from console output. Default: - ``true`` unless the environment variable ``NO_COLOR`` is set
        :param context: (deprecated) Additional context. Default: - no additional context
        :param debug: (deprecated) enable emission of additional debugging information, such as creation stack traces of tokens. Default: false
        :param ec2_creds: (deprecated) Force trying to fetch EC2 instance credentials. Default: - guess EC2 instance status
        :param ignore_errors: (deprecated) Ignores synthesis errors, which will likely produce an invalid output. Default: false
        :param json: (deprecated) Use JSON output instead of YAML when templates are printed to STDOUT. Default: false
        :param lookups: (deprecated) Perform context lookups. Synthesis fails if this is disabled and context lookups need to be performed Default: true
        :param notices: (deprecated) Show relevant notices. Default: true
        :param path_metadata: (deprecated) Include "aws:cdk:path" CloudFormation metadata for each resource. Default: true
        :param profile: (deprecated) Use the indicated AWS profile as the default environment. Default: - no profile is used
        :param proxy: (deprecated) Use the indicated proxy. Will read from HTTPS_PROXY environment if specified Default: - no proxy
        :param role_arn: (deprecated) Role to pass to CloudFormation for deployment. Default: - use the bootstrap cfn-exec role
        :param stacks: (deprecated) List of stacks to deploy. Default: - all stacks
        :param staging: (deprecated) Copy assets to the output directory. Needed for local debugging the source files with SAM CLI Default: false
        :param strict: (deprecated) Do not construct stacks with warnings. Default: false
        :param trace: (deprecated) Print trace for stack warnings. Default: false
        :param verbose: (deprecated) show debug logs. Default: false
        :param version_reporting: (deprecated) Include "AWS::CDK::Metadata" resource in synthesized templates. Default: true
        :param long: (deprecated) Display environment information for each stack. Default: false

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__575197495f8637b0bb3d7fc7a95255a1f1da44a6d0762896a3b96b629419cdd0)
            check_type(argname="argument asset_metadata", value=asset_metadata, expected_type=type_hints["asset_metadata"])
            check_type(argname="argument ca_bundle_path", value=ca_bundle_path, expected_type=type_hints["ca_bundle_path"])
            check_type(argname="argument color", value=color, expected_type=type_hints["color"])
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
            check_type(argname="argument debug", value=debug, expected_type=type_hints["debug"])
            check_type(argname="argument ec2_creds", value=ec2_creds, expected_type=type_hints["ec2_creds"])
            check_type(argname="argument ignore_errors", value=ignore_errors, expected_type=type_hints["ignore_errors"])
            check_type(argname="argument json", value=json, expected_type=type_hints["json"])
            check_type(argname="argument lookups", value=lookups, expected_type=type_hints["lookups"])
            check_type(argname="argument notices", value=notices, expected_type=type_hints["notices"])
            check_type(argname="argument path_metadata", value=path_metadata, expected_type=type_hints["path_metadata"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
            check_type(argname="argument proxy", value=proxy, expected_type=type_hints["proxy"])
            check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
            check_type(argname="argument stacks", value=stacks, expected_type=type_hints["stacks"])
            check_type(argname="argument staging", value=staging, expected_type=type_hints["staging"])
            check_type(argname="argument strict", value=strict, expected_type=type_hints["strict"])
            check_type(argname="argument trace", value=trace, expected_type=type_hints["trace"])
            check_type(argname="argument verbose", value=verbose, expected_type=type_hints["verbose"])
            check_type(argname="argument version_reporting", value=version_reporting, expected_type=type_hints["version_reporting"])
            check_type(argname="argument long", value=long, expected_type=type_hints["long"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if asset_metadata is not None:
            self._values["asset_metadata"] = asset_metadata
        if ca_bundle_path is not None:
            self._values["ca_bundle_path"] = ca_bundle_path
        if color is not None:
            self._values["color"] = color
        if context is not None:
            self._values["context"] = context
        if debug is not None:
            self._values["debug"] = debug
        if ec2_creds is not None:
            self._values["ec2_creds"] = ec2_creds
        if ignore_errors is not None:
            self._values["ignore_errors"] = ignore_errors
        if json is not None:
            self._values["json"] = json
        if lookups is not None:
            self._values["lookups"] = lookups
        if notices is not None:
            self._values["notices"] = notices
        if path_metadata is not None:
            self._values["path_metadata"] = path_metadata
        if profile is not None:
            self._values["profile"] = profile
        if proxy is not None:
            self._values["proxy"] = proxy
        if role_arn is not None:
            self._values["role_arn"] = role_arn
        if stacks is not None:
            self._values["stacks"] = stacks
        if staging is not None:
            self._values["staging"] = staging
        if strict is not None:
            self._values["strict"] = strict
        if trace is not None:
            self._values["trace"] = trace
        if verbose is not None:
            self._values["verbose"] = verbose
        if version_reporting is not None:
            self._values["version_reporting"] = version_reporting
        if long is not None:
            self._values["long"] = long

    @builtins.property
    def asset_metadata(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Include "aws:asset:*" CloudFormation metadata for resources that use assets.

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("asset_metadata")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ca_bundle_path(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Path to CA certificate to use when validating HTTPS requests.

        :default: - read from AWS_CA_BUNDLE environment variable

        :stability: deprecated
        '''
        result = self._values.get("ca_bundle_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def color(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Show colors and other style from console output.

        :default: - ``true`` unless the environment variable ``NO_COLOR`` is set

        :stability: deprecated
        '''
        result = self._values.get("color")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def context(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(deprecated) Additional context.

        :default: - no additional context

        :stability: deprecated
        '''
        result = self._values.get("context")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def debug(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) enable emission of additional debugging information, such as creation stack traces of tokens.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("debug")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ec2_creds(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Force trying to fetch EC2 instance credentials.

        :default: - guess EC2 instance status

        :stability: deprecated
        '''
        result = self._values.get("ec2_creds")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ignore_errors(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Ignores synthesis errors, which will likely produce an invalid output.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("ignore_errors")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def json(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Use JSON output instead of YAML when templates are printed to STDOUT.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("json")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def lookups(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Perform context lookups.

        Synthesis fails if this is disabled and context lookups need
        to be performed

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("lookups")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def notices(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Show relevant notices.

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("notices")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def path_metadata(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Include "aws:cdk:path" CloudFormation metadata for each resource.

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("path_metadata")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def profile(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Use the indicated AWS profile as the default environment.

        :default: - no profile is used

        :stability: deprecated
        '''
        result = self._values.get("profile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def proxy(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Use the indicated proxy.

        Will read from
        HTTPS_PROXY environment if specified

        :default: - no proxy

        :stability: deprecated
        '''
        result = self._values.get("proxy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role_arn(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Role to pass to CloudFormation for deployment.

        :default: - use the bootstrap cfn-exec role

        :stability: deprecated
        '''
        result = self._values.get("role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stacks(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(deprecated) List of stacks to deploy.

        :default: - all stacks

        :stability: deprecated
        '''
        result = self._values.get("stacks")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def staging(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Copy assets to the output directory.

        Needed for local debugging the source files with SAM CLI

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("staging")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def strict(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Do not construct stacks with warnings.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("strict")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def trace(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Print trace for stack warnings.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("trace")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def verbose(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) show debug logs.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("verbose")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def version_reporting(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Include "AWS::CDK::Metadata" resource in synthesized templates.

        :default: true

        :stability: deprecated
        '''
        result = self._values.get("version_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def long(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Display environment information for each stack.

        :default: false

        :stability: deprecated
        '''
        result = self._values.get("long")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ListOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AwsCdkCli",
    "BootstrapOptions",
    "CdkAppDirectoryProps",
    "DeployOptions",
    "DestroyOptions",
    "HotswapMode",
    "IAwsCdkCli",
    "ICloudAssemblyDirectoryProducer",
    "ListOptions",
    "RequireApproval",
    "SharedOptions",
    "StackActivityProgress",
    "SynthOptions",
]

publication.publish()

def _typecheckingstub__4cbd6d84e56b51ee4f66f530481eb49b7f94fb112b3e02f0973628fb7e3ec22b(
    *,
    app: typing.Optional[builtins.str] = None,
    output: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9976532bf553edb535766f6931bb19ad82ff334216dc84b704ebfaac651639ff(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f63d29a3ec4b39699f97d7f6c338a9273fb37e7f52b8479fb6419f38447dd194(
    context: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f041eafd3001a42690905ce9565eef958505cd6d0e775d559e6fbec53b407984(
    *,
    asset_metadata: typing.Optional[builtins.bool] = None,
    ca_bundle_path: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.bool] = None,
    context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    debug: typing.Optional[builtins.bool] = None,
    ec2_creds: typing.Optional[builtins.bool] = None,
    ignore_errors: typing.Optional[builtins.bool] = None,
    json: typing.Optional[builtins.bool] = None,
    lookups: typing.Optional[builtins.bool] = None,
    notices: typing.Optional[builtins.bool] = None,
    path_metadata: typing.Optional[builtins.bool] = None,
    profile: typing.Optional[builtins.str] = None,
    proxy: typing.Optional[builtins.str] = None,
    role_arn: typing.Optional[builtins.str] = None,
    stacks: typing.Optional[typing.Sequence[builtins.str]] = None,
    staging: typing.Optional[builtins.bool] = None,
    strict: typing.Optional[builtins.bool] = None,
    trace: typing.Optional[builtins.bool] = None,
    verbose: typing.Optional[builtins.bool] = None,
    version_reporting: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ed6f82891326f3fc3393abc8d6e60990c311ca40ba298491e4428557a66a843(
    *,
    asset_metadata: typing.Optional[builtins.bool] = None,
    ca_bundle_path: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.bool] = None,
    context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    debug: typing.Optional[builtins.bool] = None,
    ec2_creds: typing.Optional[builtins.bool] = None,
    ignore_errors: typing.Optional[builtins.bool] = None,
    json: typing.Optional[builtins.bool] = None,
    lookups: typing.Optional[builtins.bool] = None,
    notices: typing.Optional[builtins.bool] = None,
    path_metadata: typing.Optional[builtins.bool] = None,
    profile: typing.Optional[builtins.str] = None,
    proxy: typing.Optional[builtins.str] = None,
    role_arn: typing.Optional[builtins.str] = None,
    stacks: typing.Optional[typing.Sequence[builtins.str]] = None,
    staging: typing.Optional[builtins.bool] = None,
    strict: typing.Optional[builtins.bool] = None,
    trace: typing.Optional[builtins.bool] = None,
    verbose: typing.Optional[builtins.bool] = None,
    version_reporting: typing.Optional[builtins.bool] = None,
    exclusively: typing.Optional[builtins.bool] = None,
    quiet: typing.Optional[builtins.bool] = None,
    validation: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8a4a48e6e27d586c5dd41502dccff564a5fedcc9367e37550ec6c2e9af643ff(
    directory: typing.Optional[builtins.str] = None,
    *,
    app: typing.Optional[builtins.str] = None,
    output: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9bfa499e48a3fc09d071d19e318c0bc809314da2a23cf1b26886e4c5890f959(
    producer: ICloudAssemblyDirectoryProducer,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__301cfa1f6f197da85fa27bad052a38a0837341d7d0e1901658cbcaf1c29d6582(
    *,
    asset_metadata: typing.Optional[builtins.bool] = None,
    ca_bundle_path: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.bool] = None,
    context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    debug: typing.Optional[builtins.bool] = None,
    ec2_creds: typing.Optional[builtins.bool] = None,
    ignore_errors: typing.Optional[builtins.bool] = None,
    json: typing.Optional[builtins.bool] = None,
    lookups: typing.Optional[builtins.bool] = None,
    notices: typing.Optional[builtins.bool] = None,
    path_metadata: typing.Optional[builtins.bool] = None,
    profile: typing.Optional[builtins.str] = None,
    proxy: typing.Optional[builtins.str] = None,
    role_arn: typing.Optional[builtins.str] = None,
    stacks: typing.Optional[typing.Sequence[builtins.str]] = None,
    staging: typing.Optional[builtins.bool] = None,
    strict: typing.Optional[builtins.bool] = None,
    trace: typing.Optional[builtins.bool] = None,
    verbose: typing.Optional[builtins.bool] = None,
    version_reporting: typing.Optional[builtins.bool] = None,
    bootstrap_bucket_name: typing.Optional[builtins.str] = None,
    bootstrap_customer_key: typing.Optional[builtins.str] = None,
    bootstrap_kms_key_id: typing.Optional[builtins.str] = None,
    cfn_execution_policy: typing.Optional[builtins.str] = None,
    custom_permissions_boundary: typing.Optional[builtins.str] = None,
    environments: typing.Optional[typing.Sequence[builtins.str]] = None,
    example_permissions_boundary: typing.Optional[builtins.bool] = None,
    execute: typing.Optional[builtins.bool] = None,
    force: typing.Optional[builtins.bool] = None,
    public_access_block_configuration: typing.Optional[builtins.str] = None,
    qualifier: typing.Optional[builtins.str] = None,
    show_template: typing.Optional[builtins.bool] = None,
    template: typing.Optional[builtins.str] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
    toolkit_stack_name: typing.Optional[builtins.str] = None,
    trust: typing.Optional[builtins.str] = None,
    trust_for_lookup: typing.Optional[builtins.str] = None,
    use_previous_parameters: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b018eeefbacd83149d0e1a84a6c871f9439b9b3ae192abb0cdb3973220e72861(
    *,
    asset_metadata: typing.Optional[builtins.bool] = None,
    ca_bundle_path: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.bool] = None,
    context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    debug: typing.Optional[builtins.bool] = None,
    ec2_creds: typing.Optional[builtins.bool] = None,
    ignore_errors: typing.Optional[builtins.bool] = None,
    json: typing.Optional[builtins.bool] = None,
    lookups: typing.Optional[builtins.bool] = None,
    notices: typing.Optional[builtins.bool] = None,
    path_metadata: typing.Optional[builtins.bool] = None,
    profile: typing.Optional[builtins.str] = None,
    proxy: typing.Optional[builtins.str] = None,
    role_arn: typing.Optional[builtins.str] = None,
    stacks: typing.Optional[typing.Sequence[builtins.str]] = None,
    staging: typing.Optional[builtins.bool] = None,
    strict: typing.Optional[builtins.bool] = None,
    trace: typing.Optional[builtins.bool] = None,
    verbose: typing.Optional[builtins.bool] = None,
    version_reporting: typing.Optional[builtins.bool] = None,
    asset_parallelism: typing.Optional[builtins.bool] = None,
    asset_prebuild: typing.Optional[builtins.bool] = None,
    change_set_name: typing.Optional[builtins.str] = None,
    ci: typing.Optional[builtins.bool] = None,
    concurrency: typing.Optional[jsii.Number] = None,
    exclusively: typing.Optional[builtins.bool] = None,
    execute: typing.Optional[builtins.bool] = None,
    force: typing.Optional[builtins.bool] = None,
    hotswap: typing.Optional[HotswapMode] = None,
    notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    outputs_file: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    progress: typing.Optional[StackActivityProgress] = None,
    require_approval: typing.Optional[RequireApproval] = None,
    reuse_assets: typing.Optional[typing.Sequence[builtins.str]] = None,
    rollback: typing.Optional[builtins.bool] = None,
    toolkit_stack_name: typing.Optional[builtins.str] = None,
    use_previous_parameters: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb8504825518b32dce06268837b8bd1235a5475c17aab74a6939b8404467e09c(
    *,
    asset_metadata: typing.Optional[builtins.bool] = None,
    ca_bundle_path: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.bool] = None,
    context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    debug: typing.Optional[builtins.bool] = None,
    ec2_creds: typing.Optional[builtins.bool] = None,
    ignore_errors: typing.Optional[builtins.bool] = None,
    json: typing.Optional[builtins.bool] = None,
    lookups: typing.Optional[builtins.bool] = None,
    notices: typing.Optional[builtins.bool] = None,
    path_metadata: typing.Optional[builtins.bool] = None,
    profile: typing.Optional[builtins.str] = None,
    proxy: typing.Optional[builtins.str] = None,
    role_arn: typing.Optional[builtins.str] = None,
    stacks: typing.Optional[typing.Sequence[builtins.str]] = None,
    staging: typing.Optional[builtins.bool] = None,
    strict: typing.Optional[builtins.bool] = None,
    trace: typing.Optional[builtins.bool] = None,
    verbose: typing.Optional[builtins.bool] = None,
    version_reporting: typing.Optional[builtins.bool] = None,
    exclusively: typing.Optional[builtins.bool] = None,
    require_approval: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__575197495f8637b0bb3d7fc7a95255a1f1da44a6d0762896a3b96b629419cdd0(
    *,
    asset_metadata: typing.Optional[builtins.bool] = None,
    ca_bundle_path: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.bool] = None,
    context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    debug: typing.Optional[builtins.bool] = None,
    ec2_creds: typing.Optional[builtins.bool] = None,
    ignore_errors: typing.Optional[builtins.bool] = None,
    json: typing.Optional[builtins.bool] = None,
    lookups: typing.Optional[builtins.bool] = None,
    notices: typing.Optional[builtins.bool] = None,
    path_metadata: typing.Optional[builtins.bool] = None,
    profile: typing.Optional[builtins.str] = None,
    proxy: typing.Optional[builtins.str] = None,
    role_arn: typing.Optional[builtins.str] = None,
    stacks: typing.Optional[typing.Sequence[builtins.str]] = None,
    staging: typing.Optional[builtins.bool] = None,
    strict: typing.Optional[builtins.bool] = None,
    trace: typing.Optional[builtins.bool] = None,
    verbose: typing.Optional[builtins.bool] = None,
    version_reporting: typing.Optional[builtins.bool] = None,
    long: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass
