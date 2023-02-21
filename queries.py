"""GraphQL Query and Mutation constants."""

GET_RUNS = """
    query GetRuns($filters: RunsInputFilters, $sort: [RunSortEnum]) {
        runs(sort: $sort, filters: $filters) {
            edges{node {
                id title procedureId
            }}
        }
    }
"""

GET_RUN = """
    query GetRun($id: ID!) {
        run(id: $id) {
        id steps {
            id
            position
            entityId
        }
        }
    }
"""

CREATE_RUN_STEP = """
    mutation CreateRunStep($input: CreateRunStepInput!) {
        createRunStep(input: $input) {
            step {
                id title content createdById status _etag
            }
        }
    }
"""


CREATE_RUN_STEP_FIELD = """
    mutation CreateRunStepField($input: CreateRunStepFieldInput!) {
        createRunStepField(input: $input) {
            runStepField {
                id name type value _etag
            }
        }
    }
"""

UPDATE_RUN_STEP_FIELD_VALUE = """
    mutation UpdateRunStepFieldValue($input: UpdateRunStepFieldValueInput!) {
        updateRunStepFieldValue(input: $input) {
            runStepField {
                id name type value _etag
            }
        }
    }
"""


UPDATE_RUN_STEP = """
    mutation UpdateRunStep($input: UpdateRunStepInput!) {
        updateRunStep(input: $input) {
            runStep {
                id status title _etag content
            }
        }
    }
"""

GET_PERMISSION_GROUPS = """
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
"""

GET_ROLES = """
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
"""

GET_TEAMS = """
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
"""

ATTACH_PERMISSION_GROUP_TO_ROLE = """
    mutation AttachPermissionGroupToRole($input: PermissionGroupToRoleInput!) {
        attachPermissionGroupToRole(input: $input) {
            role {
                id
                name
            }
        }
    }
"""

ADD_USER_TO_TEAM = """
    mutation AddUserToTeam($input: TeamToUserInput!) {
        addUserToTeam(input: $input) {
            teamId
            userId
        }
    }
"""

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

CREATE_MBOM_ITEM_REFERENCE_DESIGNATOR = """
    mutation($input: CreateMBomItemReferenceDesignatorInput!){
        createMbomItemReferenceDesignator(input: $input){
            mbomItemReferenceDesignator {
                _etag
                id
                mbomItemId
                value
            }
        }
    }
"""

GET_PROCEDURE = """
    query GetProcedure($id: ID!) {
        procedure(id: $id) {
            id
            description
            type
            title
            steps {
                assets {
                    filename
                    id
                    s3Key
                    s3Bucket
                    downloadUrl
                }
                entityId
                id
                leadTime
                locationId
                locationSubtypeId
                parentId
                position
                slateContent
                title
                type
                fields {
                    id
                    type
                    allowNotApplicable
                    allowedIonType
                    options
                    validations {
                        functionId
                        fieldId
                    }
                }
            }
        }
    }
"""

CREATE_PROCEDURE = """
    mutation CreateProcedure(
        $title: String!,
        $description: String,
        $exportControlled: Boolean,
        $type: Proceduretypeenum
    ) {
        createProcedure(
            title: $title,
            description: $description,
            exportControlled: $exportControlled,
            type: $type
        ) {
            procedure {
                id
            }
        }
    }
"""

CREATE_STEP = """
    mutation CreateStep($input: CreateStepInput!) {
        createStep(input:  $input) {
            step {
                attributes { key type value }
                content
                createdById
                datagrid {
                    columns { editable header type id prevId unit signoffRoleId options }
                    rows { id prevId data }
                }
                entityId
                _etag
                familyId
                id
                isStandardStep
                leadTime
                location { id name }
                locationSubtype { id name }
                parent { id title position }
                position
                procedureId
                slateContent
                standardStepStatus
                title
                type
                updatedById
            }
        }
    }
"""


CREATE_FILE_ATTACHMENT = """
    mutation CreateFileAttachment($input: CreateFileAttachmentInput!) {
        createFileAttachment(input: $input) {
            fileAttachment {
                id
                entityId
                filename
                contentType
                s3Bucket
            }
            uploadUrl
        }
    }
"""

CREATE_ASSET = """
    mutation CreateAsset($input: CreateFileAttachmentInput!) {
        createAsset(input: $input) {
            fileAttachment { id s3Key s3Bucket entityId filename contentType }
            uploadUrl
        }
    }
"""

UPDATE_STEP = """
    mutation UpdateStep($input: UpdateStepInput!) {
        updateStep(input: $input) {
            step {
                _etag
                attributes { key type value }
                content
                createdById
                datagrid {
                    columns { editable header type id unit signoffRoleId options prevId }
                    rows { id prevId data }
                }
                id
                leadTime
                location { id name }
                parent { id title position }
                position
                procedure { steps { position } }
                slateContent
                standardStepStatus
                title
                type
                updatedById
            }
        }
    }
"""

GET_FILE_ATTACHMENT = """
    query FileAttachment($id: ID!) {
        fileAttachment(id: $id) {
            downloadUrl
            filename
            id
            integrationFetchUrl
            integrationId
            s3Bucket
            s3Key
            url
        }
    }
"""
