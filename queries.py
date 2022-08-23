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

GET_RUN = '''
query GetRun($id: ID!) {
	run(id: $id) {
	  id steps {
	    id
        position
        entityId
	  }
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

CREATE_FILE_ATTACHMENT = '''
mutation CreateFileAttachment($input: CreateFileAttachmentInput!) {
    createFileAttachment(input: $input) {
        uploadUrl
    }
}
'''

GET_PERMISSION_GROUPS = '''
query GetPermissionGroups($filters: PermissionGroupsInputFilters, $sort: [PermissionGroupSortEnum]) {
  permissionGroups(sort: $sort, filters: $filters) {
    edges {
      node {
        id
        name
        family
      }
    }
  }
}
'''

GET_ROLES = '''
query GetRoles($filters: RolesInputFilters) {
    roles(filters: $filters) {
        edges {
            node {
                id
                name
            }
        }
    }
}
'''

GET_TEAMS = '''
query GetTeams($filters: TeamsInputFilters) {
    teams(filters: $filters) {
        edges {
            node {
                id
                name
                roles {
                    id
                    name
                }
                supervisorId
                users { id }
            }
        }
    }
}
'''

ATTACH_PERMISSION_GROUP_TO_ROLE = '''
mutation AttachPermissionGroupToRole($input: PermissionGroupToRoleInput!) {
    attachPermissionGroupToRole(input: $input) {
        role {
            id
            name
        }
    }
}
'''

ADD_USER_TO_TEAM = '''
mutation AddUserToTeam($input: TeamToUserInput!) {
    addUserToTeam(input: $input) {
        teamId
        userId
    }
}
'''

GET_USERS = """
query GetUsers($filters: UserInputFilters, $sort: [UserSortEnum]) {
    users(sort: $sort, filters: $filters) {
        edges{
            node {
                id
                name
                organizationId
                roles {
                    id
                    name
                }
            }
        }
    }
}
"""