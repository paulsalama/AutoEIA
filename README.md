# AutoEIA

Automated Environmental Impact Assessment - Code and Architecture

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

[ ] Shop around for existing Job Management solutions
[ ] Implement Job Queue
[ ] Implement permissionless API (`POST /jobs`, `GET /jobs/:id`, `POST /jobs/:id/complete`)
[ ] Implement permissioned API