r'''
# cognito-ses-domain

CDK construct that:

* Verifies an SES domain identity (Route53 hosted zone lookup & DNS records)
* (Optionally) Creates a Cognito Identity Pool + IAM Role permitting SES send actions
* (Optionally) Enables SES sending event logging to CloudWatch via the companion [`ses-cloudwatch`](https://www.npmjs.com/package/ses-cloudwatch) construct (Configuration Set + EventBridge rule + LogGroup)

The defaults are intentionally minimal: only the SES domain identity is created unless you opt-in to other capabilities.

> ℹ️ This repository is managed by **[projen](https://github.com/projen/projen)**. Do not edit generated files (like `package.json`, GitHub workflows, eslint configs) directly—make changes in `.projenrc.ts` and run `npx projen` to re-synthesize.

## Features

| Capability | Enabled By | Notes |
|------------|------------|-------|
| SES Domain Identity | always | Creates `AWS::SES::EmailIdentity` for the domain. |
| Cognito Identity Pool + Role/Policy | `createIdentityPool: true` | Grants authenticated users SES `Send*` permissions for the verified domain. Default is `false`. |
| SES Sending Event Logging | `sendingLogs` props provided | Wraps `ses-cloudwatch` to capture SES sending events to CloudWatch Logs. |

## Install

Add as a dependency to your construct library or CDK app (peer deps `aws-cdk-lib` and `constructs` required):

```bash
npm install cognito-ses-domain
# or
yarn add cognito-ses-domain
```

## Quick Start

```python
import { Stack } from 'aws-cdk-lib';
import * as cognito from 'aws-cdk-lib/aws-cognito';
import { SesDomainIdentity } from 'cognito-ses-domain';
import { aws_ses as ses } from 'aws-cdk-lib';

class MyStack extends Stack {
	constructor(scope: Construct, id: string) {
		super(scope, id, { env: { account: '123456789012', region: 'us-east-1' } });

		const userPool = new cognito.UserPool(this, 'UserPool');
		const client = userPool.addClient('Client');

		new SesDomainIdentity(this, 'SesDomainIdentity', {
			domain: 'example.com', // must exist in Route53 in this account/region
			userPool,
			userPoolClientId: client.userPoolClientId,
			// Optional: provision Identity Pool & role (defaults to false)
			createIdentityPool: true,
			// Optional: enable logging of SES sending events
			sendingLogs: {
				configurationSetName: 'my-ses-config',
				events: [ses.EmailSendingEvent.SEND, ses.EmailSendingEvent.DELIVERY],
			},
		});
	}
}
```

## Props

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `domain` | `string` | (required) | Domain to verify (must have a public hosted zone in Route53). |
| `userPool` | `cognito.IUserPool` | (required) | User Pool associated with email sending context. |
| `userPoolClientId` | `string` | (required) | User Pool client ID (used when creating Identity Pool). |
| `createIdentityPool` | `boolean` | `false` | Whether to create Identity Pool + role/policy for SES sending. |
| `sendingLogs` | `SesCloudWatchProps?` | `undefined` | Provide to enable SES sending event logging (Configuration Set + EventBridge rule + LogGroup). |

`sendingLogs` is passed directly to the `ses-cloudwatch` construct. See its README for full option docs (`logGroupName`, `configurationSetName`, `eventRuleName`, `events`).

## Outputs

| Output | Description |
|--------|-------------|
| `SesIdentityArnOutput` | ARN of the created SES identity. |
| `IdentityPoolIdOutput` | Identity Pool ID (only if `createIdentityPool: true`). |
| `SesConfigurationSetName` | Configuration set name (only if `sendingLogs.configurationSetName` provided). |

## Identity Pool Permissions

When `createIdentityPool` is true:

* A `Cognito::IdentityPool` is created referencing the supplied User Pool & client.
* An IAM Role is created with a policy granting: `ses:SendEmail`, `ses:SendRawEmail`, `ses:SendTemplatedEmail` on the verified domain identity.

Adjust or extend permissions by adding statements to the returned role (future enhancement: expose role as a property; contributions welcome).

## Logging SES Sending Events

Provide `sendingLogs` to create a configuration set and route selected SES sending events (default from `ses-cloudwatch`) through EventBridge into a CloudWatch LogGroup. Useful for deliverability monitoring and troubleshooting.

Example enabling only default SEND event:

```python
sendingLogs: {}
```

Example customizing events & log group name:

```python
sendingLogs: {
	logGroupName: 'ses-sending-events',
	events: [ses.EmailSendingEvent.SEND, ses.EmailSendingEvent.DELIVERY, ses.EmailSendingEvent.REJECT],
}
```

## Example Apps

TypeScript example: [`examples/typescript/`](./examples/typescript/)

Python example: [`examples/python/`](./examples/python/) (install the generated Python dist after running `npx projen package`).

The TypeScript example demonstrates:

* Creating a User Pool & client
* Using the construct with sending logs enabled and Identity Pool disabled by default

Examples are intentionally outside projen management (ignored via `.projenrc.ts`) so you can add multiple examples without affecting the library build.

Run the example (ensure you have a matching hosted zone and bootstrapped environment):

```bash
cd examples/typescript
npm install
export CDK_DEFAULT_ACCOUNT=123456789012
export CDK_DEFAULT_REGION=us-east-1
npm run synth
npm run deploy
```

To customize account/region you can also pass context: `npx cdk synth -c account=123456789012 -c region=us-east-1`.

## Contributing

This project is generated & maintained with [projen](https://github.com/projen/projen).

### Projen Overview

`/.projenrc.ts` defines the construct library configuration (jsii, publishing, dependencies). Running `npx projen` regenerates:

* `package.json` (scripts, deps, peer deps)
* `.projen/*` task & dependency metadata
* Lint/test configuration
* GitHub Actions (if enabled later)

Never hand-edit those generated files—your changes will be overwritten. Instead:

1. Edit `.projenrc.ts`
2. Run `npx projen`
3. Commit both your `.projenrc.ts` change and the synthesized outputs

To inspect available options for the construct project type, see the `AwsCdkConstructLibrary` API docs or run `npx projen new awscdk-construct --help` in a scratch directory.

### Contribution Workflow (Using Projen)

1. Fork & clone the repo.
2. Install dependencies: `npm install` (always do this before running any task).
3. Make changes:

   * For library logic – edit files under `src/`.
   * For generated config (lint rules, release settings, tasks) – edit `.projenrc.ts` (never hand-edit the generated artifacts).
4. Re-synthesize after modifying `.projenrc.ts`:

   ```bash
   npx projen
   ```
5. Fast feedback while coding:

   ```bash
   npx projen compile   # just jsii compile (fast, no tests)
   npx projen test      # jest + eslint
   ```
6. Before pushing / opening a PR run the full pipeline:

   ```bash
   npx projen build     # synth -> compile -> test -> docgen -> package
   ```
7. Commit BOTH your source changes and any regenerated files (e.g. `package.json`, `API.md`, `.projen/*`).
8. Open a pull request with a concise description and rationale.

Tip: Use `npx projen watch` during development to continuously recompile on change.

Common pitfalls:

* Forgetting to run `npx projen` after editing `.projenrc.ts` (CI will show drift).
* Editing generated files directly – they will be overwritten.
* Introducing constructs or aws-cdk-lib version drift in examples – rely on root versions when possible.

### Build & Test

```bash
git clone https://github.com/pablocano/cognito-ses-domain.git
cd cognito-ses-domain
npm install   # installs dev deps
npm run build # full projen build pipeline

# Or granular:
npm run compile   # jsii compile
npm test          # jest + eslint
```

### Common Tasks

| Task | Command | Description |
|------|---------|-------------|
| Synthesize project files | `npx projen` | Regenerates config files. |
| Compile | `npm run compile` | jsii compile to `lib/`. |
| Test | `npm test` | Jest + ESLint. |
| Package | `npm run package` | Builds distributable. |
| Upgrade deps | `npm run upgrade` | Applies dependency upgrades. |

### Adding Features

1. Modify source in `src/`.
2. Add/adjust tests in `test/` (100% coverage enforced in current setup).
3. Run `npm test`.
4. Open PR with a concise description and motivation.

### Releasing

Releases are automated through projen tasks (semantic versioning). A maintainer will run the release workflow; external contributors only need to focus on code + tests.

## Design Notes

* `createIdentityPool` defaults to `false` to avoid provisioning auth infrastructure unless explicitly required.
* Logging is opt-in via `sendingLogs` to keep minimal footprint by default.
* Hosted zone lookup uses `HostedZone.fromLookup` which requires the domain hosted zone to exist in the target account/region; for unit tests this is mocked.

## Development Workflow with Examples

The example app consumes the library via a relative file dependency (`file:../..`). After changing the library:

```bash
npm run compile   # at repo root
cd examples/typescript
npm run synth
```

If you add more examples, place them under `examples/<name>` and ensure they are not published (already excluded by `.npmignore`).

## License

Apache-2.0 © Merapar Technologies Group B.V.

---


Questions or ideas? Open an issue or PR — contributions are welcome.
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

import aws_cdk.aws_cognito as _aws_cdk_aws_cognito_ceddda9d
import constructs as _constructs_77d1e7e8
import ses_cloudwatch as _ses_cloudwatch_7f0db6a1


class SesDomainIdentity(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cognito-ses-domain.SesDomainIdentity",
):
    '''A CDK construct to create an SES domain identity.

    It can optionally create a Cognito Identity Pool and grant send permissions
    to a Cognito User Pool.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        domain: builtins.str,
        user_pool: _aws_cdk_aws_cognito_ceddda9d.IUserPool,
        user_pool_client_id: builtins.str,
        create_identity_pool: typing.Optional[builtins.bool] = None,
        sending_logs: typing.Optional[typing.Union[_ses_cloudwatch_7f0db6a1.SesCloudWatchProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param domain: The domain to use for the SES identity. This domain must exist as a public hosted zone in Route 53.
        :param user_pool: The Cognito User Pool that will be granted permission to send emails.
        :param user_pool_client_id: The client ID of the user pool client. This is needed to associate the user pool with the identity pool.
        :param create_identity_pool: Determines whether to create a Cognito Identity Pool and the associated IAM Role to grant users permission to send emails. Set this to ``true`` if your application users need to send emails via SES. Set this to ``false`` if you only need to create the verified SES domain identity, for example, to configure the User Pool's own email settings (e.g., for password resets). Default: false
        :param sending_logs: Optional configuration to enable SES sending event logging powered by the ``ses-cloudwatch`` construct. If provided, a configuration set, EventBridge rule, destination and LogGroup are created. Omit (leave undefined) to disable sending event logs.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8fee7532843327d4787f997ce7ae2afda3995cb5ccb08a7742a74ba40bd22602)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SesDomainIdentityProps(
            domain=domain,
            user_pool=user_pool,
            user_pool_client_id=user_pool_client_id,
            create_identity_pool=create_identity_pool,
            sending_logs=sending_logs,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="identityArn")
    def identity_arn(self) -> builtins.str:
        '''The ARN of the created SES domain identity.'''
        return typing.cast(builtins.str, jsii.get(self, "identityArn"))

    @builtins.property
    @jsii.member(jsii_name="identityPoolId")
    def identity_pool_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the Cognito Identity Pool.

        This will only be populated if ``createIdentityPool`` is true.
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityPoolId"))

    @builtins.property
    @jsii.member(jsii_name="sesCloudWatch")
    def ses_cloud_watch(
        self,
    ) -> typing.Optional[_ses_cloudwatch_7f0db6a1.SesCloudWatch]:
        '''The SesCloudWatch helper construct instance if logging was enabled via ``sendingLogs``.'''
        return typing.cast(typing.Optional[_ses_cloudwatch_7f0db6a1.SesCloudWatch], jsii.get(self, "sesCloudWatch"))


@jsii.data_type(
    jsii_type="cognito-ses-domain.SesDomainIdentityProps",
    jsii_struct_bases=[],
    name_mapping={
        "domain": "domain",
        "user_pool": "userPool",
        "user_pool_client_id": "userPoolClientId",
        "create_identity_pool": "createIdentityPool",
        "sending_logs": "sendingLogs",
    },
)
class SesDomainIdentityProps:
    def __init__(
        self,
        *,
        domain: builtins.str,
        user_pool: _aws_cdk_aws_cognito_ceddda9d.IUserPool,
        user_pool_client_id: builtins.str,
        create_identity_pool: typing.Optional[builtins.bool] = None,
        sending_logs: typing.Optional[typing.Union[_ses_cloudwatch_7f0db6a1.SesCloudWatchProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Properties for the SesDomainIdentity construct.

        :param domain: The domain to use for the SES identity. This domain must exist as a public hosted zone in Route 53.
        :param user_pool: The Cognito User Pool that will be granted permission to send emails.
        :param user_pool_client_id: The client ID of the user pool client. This is needed to associate the user pool with the identity pool.
        :param create_identity_pool: Determines whether to create a Cognito Identity Pool and the associated IAM Role to grant users permission to send emails. Set this to ``true`` if your application users need to send emails via SES. Set this to ``false`` if you only need to create the verified SES domain identity, for example, to configure the User Pool's own email settings (e.g., for password resets). Default: false
        :param sending_logs: Optional configuration to enable SES sending event logging powered by the ``ses-cloudwatch`` construct. If provided, a configuration set, EventBridge rule, destination and LogGroup are created. Omit (leave undefined) to disable sending event logs.
        '''
        if isinstance(sending_logs, dict):
            sending_logs = _ses_cloudwatch_7f0db6a1.SesCloudWatchProps(**sending_logs)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a934b18eadc15bcfce00627f5432dad3696d4136ffe7e15af6106808c6151140)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument user_pool", value=user_pool, expected_type=type_hints["user_pool"])
            check_type(argname="argument user_pool_client_id", value=user_pool_client_id, expected_type=type_hints["user_pool_client_id"])
            check_type(argname="argument create_identity_pool", value=create_identity_pool, expected_type=type_hints["create_identity_pool"])
            check_type(argname="argument sending_logs", value=sending_logs, expected_type=type_hints["sending_logs"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain": domain,
            "user_pool": user_pool,
            "user_pool_client_id": user_pool_client_id,
        }
        if create_identity_pool is not None:
            self._values["create_identity_pool"] = create_identity_pool
        if sending_logs is not None:
            self._values["sending_logs"] = sending_logs

    @builtins.property
    def domain(self) -> builtins.str:
        '''The domain to use for the SES identity.

        This domain must exist as a public hosted zone in Route 53.
        '''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_pool(self) -> _aws_cdk_aws_cognito_ceddda9d.IUserPool:
        '''The Cognito User Pool that will be granted permission to send emails.'''
        result = self._values.get("user_pool")
        assert result is not None, "Required property 'user_pool' is missing"
        return typing.cast(_aws_cdk_aws_cognito_ceddda9d.IUserPool, result)

    @builtins.property
    def user_pool_client_id(self) -> builtins.str:
        '''The client ID of the user pool client.

        This is needed to associate the user pool with the identity pool.
        '''
        result = self._values.get("user_pool_client_id")
        assert result is not None, "Required property 'user_pool_client_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def create_identity_pool(self) -> typing.Optional[builtins.bool]:
        '''Determines whether to create a Cognito Identity Pool and the associated IAM Role to grant users permission to send emails.

        Set this to ``true`` if your application users need to send emails via SES.

        Set this to ``false`` if you only need to create the verified SES domain identity,
        for example, to configure the User Pool's own email settings (e.g., for password resets).

        :default: false
        '''
        result = self._values.get("create_identity_pool")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def sending_logs(
        self,
    ) -> typing.Optional[_ses_cloudwatch_7f0db6a1.SesCloudWatchProps]:
        '''Optional configuration to enable SES sending event logging powered by the ``ses-cloudwatch`` construct.

        If provided, a configuration set, EventBridge rule, destination and LogGroup are created.
        Omit (leave undefined) to disable sending event logs.
        '''
        result = self._values.get("sending_logs")
        return typing.cast(typing.Optional[_ses_cloudwatch_7f0db6a1.SesCloudWatchProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesDomainIdentityProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "SesDomainIdentity",
    "SesDomainIdentityProps",
]

publication.publish()

def _typecheckingstub__8fee7532843327d4787f997ce7ae2afda3995cb5ccb08a7742a74ba40bd22602(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    domain: builtins.str,
    user_pool: _aws_cdk_aws_cognito_ceddda9d.IUserPool,
    user_pool_client_id: builtins.str,
    create_identity_pool: typing.Optional[builtins.bool] = None,
    sending_logs: typing.Optional[typing.Union[_ses_cloudwatch_7f0db6a1.SesCloudWatchProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a934b18eadc15bcfce00627f5432dad3696d4136ffe7e15af6106808c6151140(
    *,
    domain: builtins.str,
    user_pool: _aws_cdk_aws_cognito_ceddda9d.IUserPool,
    user_pool_client_id: builtins.str,
    create_identity_pool: typing.Optional[builtins.bool] = None,
    sending_logs: typing.Optional[typing.Union[_ses_cloudwatch_7f0db6a1.SesCloudWatchProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass
