# ion API examples
Example use cases of the ion GraphQL API.

## Authentication
You will need a client ID and a client secret to authenticate to the API. See documentation [here](https://manual.firstresonance.io/api/access-tokens). You may want to override the API you are writing to with the following environment variables.

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

