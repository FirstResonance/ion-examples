"""GraphQL Query and Mutation constants."""

GET_RUNS = '''
query GetRuns($filters: RunsInputFilters, $sort: [RunSortEnum]) {
    runs(sort: $sort, filters: $filters) {
        edges{node {
            id title procedureId
        }}
    }
}
'''


CREATE_RUN_STEP = '''
    mutation CreateRunStep($input: CreateRunStepInput!) {
        createRunStep(input: $input) {
            step {
                id title content createdById status _etag
            }
        }
    }
'''


CREATE_RUN_STEP_FIELD = '''
    mutation CreateRunStepField($input: CreateRunStepFieldInput!) {
        createRunStepField(input: $input) {
            runStepField {
                id name type value _etag
            }
        }
    }
'''

UPDATE_RUN_STEP_FIELD_VALUE = '''
    mutation UpdateRunStepFieldValue($input: UpdateRunStepFieldValueInput!) {
        updateRunStepFieldValue(input: $input) {
            runStepField {
                id name type value _etag
            }
        }
    }
'''


UPDATE_RUN_STEP = '''
    mutation UpdateRunStep($input: UpdateRunStepInput!) {
        updateRunStep(input: $input) {
            runStep {
                id status title _etag content
            }
        }
    }
'''