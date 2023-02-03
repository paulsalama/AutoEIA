# API Models

This module contains all of the data models using in the EIA REST API. These
models are defined using `pydantic`, which is a library for marshalling JSON
data and performing arbitrary validation, leveraging Python types.

## Creating a new Job type

To create a new Job called FooJob, first open `job.py` in this module and add a
new value in JobType corresponding to your new Job's name. Our job is named Foo
so we will add a line `FOO = "FOO"`.

Now create a new file in this module. In this example, we will name the file
`foo_job.py`.

Within `foo_job.py`, you must create 4 classes that will correspond to different
parts of the Job's representation:

1. `FooJobInputs`: This corresponds to the raw data that must be provided for
   this job in order for a Worker to be able to have enough information to
   complete the Job. For our FooJob, let's say it just requires a number, X.
   This result in the following code:

   ```
   class FooJobInputs(BaseModel):
       x: number
   ```
1. `CreateFooJobInput`: This is a boilerplate type needed to wrap `FooJobInputs`
   so that the API can know how to identify this input as being of type FooJob.

   ```
   class CreateShadowStudyJobInput(BaseJobInput):
       job_type: Literal[JobType.FOO] = JobType.FOO
       inputs: FooJobInputs
   ```
1. `FooJobOutputs`: This is the raw data that a Worker must provide in order to
   complete this Job. Let's just say this requires a number, Y.

   ```
   class FooJobOutputs(BaseModel):
       y: number
   ```
1. `FooJob`: This is the specification for how the job will be represented in
   the database. It inherits some fields from superclasses so we just have to
   specify the Job Type, the inputs and the outputs.

   ```
   class FooJob(BaseJob):
       job_type: Literal[JobType.FOO] = JobType.FOO
       inputs: FooJobInputs
       outputs: Optional[FooJobOutputs] = None
   ```

Now, within `__init__.py`, Bew sure to add these new classes to the
corresponding type Unions: `JobInput`, `CreateJobInput`, `JobOutput`, and `Job`.

That's it!
