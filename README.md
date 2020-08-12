# ion API examples
Example use cases of the ION GraphQL API.

## Authentication
You will need a client ID and a client secret to authenticate to the API. You can get your client ID and secret by contacting First Resonance (software@firstresonance.io). You may want to override the API you are writing to with the following environment variables.

If you are targeting a non-production API, set `ION_API_URI` to the API you are writing to and set your  `ION_API_AUDIENCE` to the API audience for the target API.

## Setup

System dependencies:
- Python
- pip
- virtualenv

Create a virtualenv and activate it:

```
virtualenv -p python3 ion_examples
source ./ion_examples/bin/activate
```

Then, install the dependencies:

```
pip install -r requirements.txt
```

# Examples

## Alter Completed Runs
This example script demonstrates how to alter a set of runs that were created from a common procedure. The function `update_runs_with_new_info` includes detailed comments about how the script alters each run. This script could help a user associate additional information which was not available at the time of run completion.