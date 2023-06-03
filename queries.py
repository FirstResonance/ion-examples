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

CREATE_ROLE = """
    mutation CreateRole($input: CreateRoleInput!) {
        createRole(input: $input) {
            role {
                id name
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
            attributes {
                key
                type
                value
            }
            id
            description
            familyId
            labels
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
                datagridColumns {
                        edges {
                            node {
                                id
                                index
                                header
                                options
                                signoffRole {
                                    id
                                    name
                                }
                                type
                            }
                        }
                    }
                datagridRows {
                    edges {
                        node {
                            id
                            allowNotApplicable
                            index
                            required
                            values { value columnId type }
                        }
                    }
                }
                entityId
                id
                isDerivedStep
                isStandardStep
                leadTime
                locationId
                locationSubtypeId
                originStepId
                parentId
                position
                slateContent
                standardStep {
                    id
                }
                steps {
                    assets {
                        filename
                        id
                        s3Key
                        s3Bucket
                        downloadUrl
                    }
                    datagridColumns {
                        edges {
                            node {
                                id
                                index
                                header
                                options
                                signoffRole {
                                    id
                                    name
                                }
                                type
                            }
                        }
                    }
                    datagridRows {
                        edges {
                            node {
                                id
                                allowNotApplicable
                                index
                                required
                                values { value columnId type }
                            }
                        }
                    }
                    entityId
                    id
                    isDerivedStep
                    isStandardStep
                    leadTime
                    locationId
                    locationSubtypeId
                    originStepId
                    parentId
                    position
                    slateContent
                    standardStep {
                        id
                    }
                    title
                    type
                    upstreamStepIds
                    version
                    fields {
                        id
                        allowNotApplicable
                        allowedIonType
                        display
                        name
                        options
                        required
                        signoffRole {
                            id
                            name
                        }
                        type
                        unit
                        validations {
                            functionId
                            fieldId
                        }
                    }
                }
                title
                type
                upstreamStepIds
                version
                fields {
                    id
                    allowNotApplicable
                    allowedIonType
                    display
                    name
                    options
                    required
                    signoffRole {
                        id
                        name
                    }
                    type
                    unit
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
                familyId
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
                    columns {
                        editable
                        header
                        type
                        id
                        prevId
                        unit
                        options 
                    }
                    rows { id prevId data }
                }
                entityId
                _etag
                familyId
                id
                isDerivedStep
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


GET_PART_INVENTORY = """
    query PartInventory($id: ID!) {
        partInventory(id: $id) {
            _etag
            id
            quantity
            status
            part {
                description
                partNumber
                revision
            }
            quantity
            abomItems {
                id
                _etag
                quantity
            }
        }
    }
"""

UPDATE_PART_INVENTORY = """
    mutation UpdatePartInventory($input: UpdatePartInventoryInput!) {
        updatePartInventory(input: $input) {
            partInventory {
                _etag
                id
                part {
                    description
                    partNumber
                    revision
                }
                quantity
            }
        }
    }
"""

ADD_LABEL_TO_PROCEDURE_FAMILY = """
    mutation AddLabelToProcedureFamily($input: LabelToProcedureFamilyInput!) {
        addLabelToProcedureFamily(input: $input) {
            labelId familyId
        }
    }
"""

CREATE_LABEL = """
    mutation CreateLabel($input: CreateLabelInput!) {
        createLabel(input: $input) {
            label {
                id value _etag createdById updatedById
            }
        }
    }
"""

GET_LABELS = """
    query GetLabels($filters: LabelsInputFilters) {
        labels(filters: $filters) {
            edges {
                node {
                    id
                    _etag
                    value
                    createdById
                    updatedById
                }
            }
        }
    }
"""

CREATE_STEP_FIELD = """
    mutation CreateStepField($input: CreateStepFieldInput!) {
        createStepField(input: $input) {
            stepField {
                _etag
                allowNotApplicable
                allowedIonType
                createdById
                id
                name
                part { partNumber }
                partSubtype { name }
                peerReviewRequired
                signoffRole { id name }
                stepId
                type
                unit
                updatedById
            }
        }
    }
"""

CREATE_DATAGRID_COLUMN = """
    mutation CreateDatagridColumn($input: CreateDatagridColumnInput!) {
        createDatagridColumn(input: $input) {
            datagridColumn {
                LastSessionId
                editable
                header
                id
                index
                options
                runStepId
                settable
                signoffRoleId
                stepId
                type
                unit
            }
        }
    }
"""

CREATE_DATAGRID_ROW = """
    mutation CreateDatagridRow($input: CreateDatagridRowInput!) {
        createDatagridRow(input: $input) {
            datagridRow {
                id
                index
                required
                runStepId
                stepId
            }
        }
    }
"""

SET_DATAGRID_VALUE = """
    mutation SetDatagridValue($input: SetDatagridValueInput!) {
        setDatagridValue(input: $input) {
            datagridValue {
                _etag
                columnId
                id
                ionValue {
                    ... on User {
                        id
                        email
                    }
                }
                notApplicable
                rowId
                type
                value
            }
        }
    }
"""

CREATE_STEP_EDGE = """
    mutation CreateStepEdge($stepId: ID!, $upstreamStepId: ID!) {
        createStepEdge(input: {stepId: $stepId, upstreamStepId: $upstreamStepId}) {
            stepEdge {
                id stepId upstreamStepId createdById updatedById
            }
        }
    }
"""

GET_STEP = """
    query Step($id: ID!) {
        step(id: $id) {
            assets {
                filename
                id
                s3Key
                s3Bucket
                downloadUrl
            }
            datagridColumns {
                edges {
                    node {
                        id
                        index
                        header
                        options
                        signoffRole {
                            id
                            name
                        } 
                        type
                    }
                }
            }
            datagridRows {
                edges {
                    node {
                        id
                        allowNotApplicable
                        index
                        required
                        values { value columnId type }
                    }
                }
            }
            entityId
            id
            isDerivedStep
            isStandardStep
            leadTime
            locationId
            locationSubtypeId
            originStepId
            parentId
            position
            slateContent
            standardStep {
                id
            }
            steps {
                assets {
                    filename
                    id
                    s3Key
                    s3Bucket
                    downloadUrl
                }
                datagridColumns {
                    edges {
                        node {
                            id
                            index
                            header
                            options
                            signoffRole {
                                id
                                name
                            } 
                            type
                        }
                    }
                }
                datagridRows {
                    edges {
                        node {
                            id
                            allowNotApplicable
                            index
                            required
                            values { value columnId type }
                        }
                    }
                }
                entityId
                id
                isDerivedStep
                isStandardStep
                leadTime
                locationId
                locationSubtypeId
                originStepId
                parentId
                position
                slateContent
                standardStep {
                    id
                }
                title
                type
                upstreamStepIds
                version
                fields {
                    id
                    allowNotApplicable
                    allowedIonType
                    display
                    name
                    options
                    required
                    signoffRole {
                        id
                        name
                    }
                    type
                    unit
                    validations {
                        functionId
                        fieldId
                    }
                }
            }
            title
            type
            upstreamStepIds
            version
            fields {
                id
                allowNotApplicable
                allowedIonType
                display
                name
                options
                required
                signoffRole {
                    id
                    name
                }
                type
                unit
                validations {
                    functionId
                    fieldId
                }
            }
        }  
    }
"""

GET_STEPS = """
    query getSteps($filters: StepsFilters, $sort: [StepSortEnum]) {
        steps(filters: $filters, sort: $sort) {
            edges {
                node {
                    assets {
                        filename
                        id
                        s3Key
                        s3Bucket
                        downloadUrl
                    }
                    datagridColumns {
                        edges {
                            node {
                                id
                                index
                                header
                                options
                                signoffRole {
                                    id
                                    name
                                } 
                                type
                            }
                        }
                    }
                    datagridRows {
                        edges {
                            node {
                                id
                                allowNotApplicable
                                index
                                required
                                values { value columnId type }
                            }
                        }
                    }
                    entityId
                    id
                    isDerivedStep
                    isStandardStep
                    leadTime
                    locationId
                    locationSubtypeId
                    originStepId
                    parentId
                    position
                    slateContent
                    standardStep {
                        id
                    }
                    steps {
                        assets {
                            filename
                            id
                            s3Key
                            s3Bucket
                            downloadUrl
                        }
                        datagridColumns {
                            edges {
                                node {
                                    id
                                    index
                                    header
                                    options
                                    signoffRole {
                                        id
                                        name
                                    } 
                                    type
                                }
                            }
                        }
                        datagridRows {
                            edges {
                                node {
                                    id
                                    allowNotApplicable
                                    index
                                    required
                                    values { value columnId type }
                                }
                            }
                        }
                        entityId
                        id
                        isDerivedStep
                        isStandardStep
                        leadTime
                        locationId
                        locationSubtypeId
                        originStepId
                        parentId
                        position
                        slateContent
                        standardStep {
                            id
                        }
                        title
                        type
                        upstreamStepIds
                        version
                        fields {
                            id
                            type
                            allowNotApplicable
                            allowedIonType
                            name
                            options
                            signoffRole {
                                id
                                name
                            }
                            validations {
                                functionId
                                fieldId
                            }
                        }
                    }
                    title
                    type
                    upstreamStepIds
                    version
                    fields {
                        id
                        type
                        allowNotApplicable
                        allowedIonType
                        name
                        options
                        signoffRole {
                            id
                            name
                        }
                        validations {
                            functionId
                            fieldId
                        }
                    }
                }
            }
        }  
    }
"""

COPY_STEP = """
mutation CopyStep($input: CopyStepInput!) {
    copyStep(input: $input) {
        step {
            assets { id }
            content
            familyId
            fields { id validations { functionId fieldId } }
            id
            labels { id value }
            isChildStandardStep
            isDerivedStep
            isStandardStep
            originStepId
            mbomItemAssociations {
                id
                mbomItemId
                step { procedureId }
                stepId
            }
            parentId
            position
            procedureId
            title
            slateContent
            standardStepFamilyId
            standardStepStatus
            steps {
                fields { id name }
                id
                isChildStandardStep
                isDerivedStep
                isStandardStep
                originStepId
                standardStepStatus
                title
            }
            version
            attributes {
                key type value
            }
        }
    }
}
"""

UPDATE_ABOM_ITEM = """
    mutation UpdateAbomItem($input: UpdateABomItemInput!) {
        updateAbomItem(input: $input) {
            abomItem {
                _etag
                id
                quantity
            }
        }
    }
"""

GET_LOCATION = """
    query GetLocation($id: ID!) {
        location(id: $id) {
            id
            name
            entityId
        }
    }
"""

CREATE_BARCODE_LABEL = """
    mutation createBarcodeLabel($input: CreateBarcodeLabelInput!) {
        createBarcodeLabel(input: $input) {
            barcodeLabel {
                barcode
            }
        }
    }
"""

GET_TEMPLATES = """
    query GetTemplates($filters: BarcodeTemplatesInputFilters!){
        barcodeTemplates(filters:$filters) {
            edges {
                node {
                    id
                    name
                    entityType
                }
            }
        }
    }
"""

DELETE_PURCHASE = """
    mutation deletePurchaseOrder($id:ID!, $etag:String!){
        deletePurchaseOrder(id:$id, etag:$etag){
            id
        }
    }
"""

GET_RECEIPTS = """
    query receipts($filters:ReceiptsInputFilters){
        receipts(filters: $filters) {
            edges {
                node {
                    id
                    _etag
                }
            }
        }
    }
"""

DELETE_RECEIPT = """
    mutation deleteReceipt($id:ID!, $etag:String!) {
        deleteReceipt(id:$id, etag:$etag) {
            id
        }
    }
"""

DELETE_PURCHASE_LINE = """
    mutation deletePurchaseOrderLine($id:ID!, $etag:String!){
        deletePurchaseOrderLine(id:$id,etag:$etag) {
            id 
        }
    }
"""

GET_PURCHASE_LINES = """ 
    query PurchaseOrderLines($filterss: PurchaseOrderLinesInputFilters) {
        purchaseOrderLines(filters: $filterss) {
            edges {
                node {
                    id
                    _etag
                }
            }
        }
    }
"""

GET_PURCHASES = """
    query PurchaseOrders($filterss: PurchaseOrdersInputFilters) {
        purchaseOrders(filters: $filterss) {
            edges {
                node {
                    id
                    _etag
                }
            }
        }
    }
"""
