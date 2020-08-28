import argparse
from getpass import getpass
from api import Api
import queries


def get_runs_from_procedure_id(api: Api, procedure_id: int) -> list:
    """
    Query ION API for all run ids associated with a particular procedure.

    Args:
        api (Api): API instance to send authenticated requests
        procedure_id (int): ID of procedure runs were created from

    Returns:
        list: All run ids associated with given procedure_id
    """
    runs_query = {
        'query': queries.GET_RUNS,
        'variables': {'filters': {'procedureId': {'eq': procedure_id}}}
    }
    runs = api.request(runs_query)
    return [run['node']['id'] for run in runs['data']['runs']['edges']]


def create_run_step(api: Api, run_id: int, title: str, content: str=None) -> dict:
    """
    Create a new step with status of REDLINE for a specific run.

    Args:
        api (Api): API instance to send authenticated requests
        run_id (int): ID of run to attach new step to
        title (str): Title of new step
        content (str, optional): Step content. Defaults to None.

    Returns:
        dict: Fields of newly created step
    """
    create_step = {
        'query': queries.CREATE_RUN_STEP,
        'variables': {'input': {
            'title': title,
            'runId': run_id
        }}
    }
    run_step = api.request(create_step)
    return run_step['data']['createRunStep']['step']


def create_run_step_field(api: Api, run_step_id: int, name: str,
                          type: str, required: bool=False) -> dict:
    """
    Create a run step field for a run step that is in redline.

    Args:
        api (Api): API instance to send authenticated requests
        run_step_id (int): ID of run step to attach field to
        name (str): Name of the newly created field
        type (str): Field type. Must be one of the following enumerated strings.
                    [STRING, NUMBER, BOOLEAN, SELECT, SIGNOFF, MULTISELECT,
                     DATETIME, FILE_ATTACHMENT]
        required (bool, optional): Is field required. Defaults to False.

    Returns:
        dict: Values of newly created run step field
    """
    create_field = {
        'query': queries.CREATE_RUN_STEP_FIELD,
        'variables': {'input': {
            'runStepId': run_step_id,
            'name': name,
            'type': type,
            'required': required
        }}
    }
    run_step_field = api.request(create_field)
    return run_step_field['data']['createRunStepField']['runStepField']


def update_run_step_status(api: Api, run_step: dict, status: str) -> dict:
    """
    Update the status of a run step.

    Args:
        api (Api): API instance to send authenticated requests
        run_step (dict): Dict of values related to run step, must have _etag and id keys
        status (str): New status for run step. Must be one of the following values
                      [TODO, IN_PROGRESS, COMPLETE, REDLINE, HOLD, FAILED, CANCELED]

    Returns:
        dict: Updated fields for run step.
    """
    update_run_step = {
        'query': queries.UPDATE_RUN_STEP,
        'variables': {'input': {
            'id': run_step['id'],
            'status': status,
            'etag': run_step['_etag']
        }}
    }
    run_step = api.request(update_run_step)
    return run_step['data']['updateRunStep']['runStep']


def update_run_step_field_value(api: Api, run_step_field: dict, value) -> dict:
    """


    Args:
        api (Api): API instance to send authenticated requests
        run_step_field (dict): Dict of values related to run step field,
                               must have _etag and id keys
        value (): Value to set for run step field. Value type must match field type.

    Returns:
        dict: Updated values for run step field
    """
    update_run_step_field = {
        'query': queries.UPDATE_RUN_STEP_FIELD_VALUE,
        'variables': {'input': {
            'id': run_step_field['id'],
            'value': value,
            'etag': run_step_field['_etag']
        }}
    }
    run_step_field = api.request(update_run_step_field)
    return run_step_field['data']['updateRunStepFieldValue']['runStepField']


def update_runs_with_new_info(api: Api, procedure_id: int) -> None:
    """
    Update existing runs with new info by creating and filling new run steps and run step fields.

    Args:
        api (Api): API instance to send authenticated requests
        procedure_id (int): ID of procedure which runs were created from
    """
    # Query all runs created from a specific procedure
    runs = get_runs_from_procedure_id(api, procedure_id)
    # For each run in the returned list of runs
    for run_id in runs:
        # Create a run step to capture new data related to run
        # Newly created run steps default to the status of REDLINE
        # Fill in the appropriate title and optionally pass step content
        run_step = create_run_step(api=api, run_id=run_id, title='title', content='wow')
        # Create a new field for the new run step
        # In the example we create a required run step field with values of type string
        run_step_field = create_run_step_field(api=api, run_step_id=run_step['id'],
                                               name='name', type='STRING', required=True)
        # To complete a redline within ION change the status of step associated with
        # the redline to have a status of TODO
        run_step = update_run_step_status(api=api, run_step=run_step, status='TODO')
        # Now that the redline is complete we move the run step status to IN_PROGRESS
        # in order to fill out the new fields we created
        run_step = update_run_step_status(api=api, run_step=run_step, status='IN_PROGRESS')
        # Fill the value for the newly created field
        run_step_field = update_run_step_field_value(api=api, run_step_field=run_step_field,
                                                     value='value')
        # Once we have filled the new fields, set the run step status to COMPLETE
        run_step = update_run_step_status(api=api, run_step=run_step, status='COMPLETE')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Update runs related to a procedure with new steps and fields.')
    parser.add_argument('procedure_id', type=int,
                        help='ID of procedure that runs were created from.')
    parser.add_argument('--client_id', type=str, help='Your API client ID')
    args = parser.parse_args()
    client_secret = getpass('Client secret: ')
    if not args.client_id or not client_secret:
        raise argparse.ArgumentError('Must input client ID and '
                                     'client secret to run import')
    api = Api(client_id=args.client_id, client_secret=client_secret)
    update_runs_with_new_info(api, args.procedure_id)
