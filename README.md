# AutoEIA

Automated Environmental Impact Assessment - Code and Architecture

## Quick Start

You must have the following installed on your development machine:

1. [AWS CDK](https://github.com/aws/aws-cdk)
1. [Poetry](https://python-poetry.org/docs/)
1. [Docker](https://docs.docker.com/desktop/install/mac-install/)

Then run the following commands from the root of the repo:

```
poetry install
poetry run cdk synth
```

If this runs without error, then you're all set!

## Useful commands

- `cdk ls` list all stacks in the app
- `cdk synth` emits the synthesized CloudFormation template
- `cdk deploy` deploy this stack to your default AWS account/region
- `cdk diff` compare deployed stack with current state
- `cdk docs` open CDK documentation

## Design

### Glossary

- **Job**: a unit of work to be completed, with schema-defined inputs and
  outputs according to its Job Type.
- **Requester**: A user that requests a specific Job on a set of provided
  inputs.
- **Worker**: A user that is equipped to complete a Job and furnish the
  accompanying outputs of the Job's completion.
- **Auditer**: A user that has read-only permissions to view Job artifacts for
  the purposes of verifying work done.

### Overview

The main interface is a REST API. The general rationale of the system is to
provide a platform for Requesters to submit Jobs, which can then be completed by
Workers. The artifacts of these jobs are then stored in perpetuity, and can be
accessed by the Requester or by Auditers. The API also manages permissions
between the various actors in the system.

See the automatically-generated documentation for a more detailed description of
the endpoints, as well as the specific analysis types supported.

Infrastructure is modeled using the AWS CDK in Python. Dependencies are managed
using `poetry`.

### Data Storage

Job metadata is stored in an DynamoDB instance. Its schema is the following:

```yaml
Job:
    id: str
    inputs: any
    outputs: any
    type: JobType
    status: NOT_STARTED | IN_PROGRESS | SUCCEEDED | FAILED
```

## TODO:

[ ] Implement permissioned API
