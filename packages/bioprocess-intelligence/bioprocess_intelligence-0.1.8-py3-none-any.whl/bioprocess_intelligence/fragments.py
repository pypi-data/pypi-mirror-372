"""GraphQL fragments for Bioprocess Intelligence client."""

CORE_OWNER_FIELDS = """
    fragment CoreOwnerFields on UserType {
        id
        username
        firstName
        lastName
        email
    }
"""

CORE_COLLECTION_FIELDS = """
    fragment CoreCollectionFields on TopicType {
        id
        name
        description
        numProcesses
        permissionMode
        userPermissions
        imageB64
        needsCalculation
        teamDataStandardsEnabled
        organizationDataStandardsEnabled
        owner {
            ...CoreOwnerFields
        }
        team {
            id
            name
            userPermissions
        }
    }
"""

CORE_PROCESS_FIELDS = """
    fragment CoreProcessFields on ProcessType {
        id
        name
        description
        startTime
        endTime
        lastUpdated
        qualityScore
        qualityMessages
        calculationDate
        calculationNeeded
        topic {
            id
            name
            team {
                id
                name
            }
            mediaSet {
                id
                name
            }
            userPermissions
        }
    }
"""

CORE_PARAMETER_FIELDS = """
    fragment CoreParameterFields on ParameterType {
        id
        name
        value
        units
        description
        calculator {
            id
            name
        }
        dataStandard {
            id
            name
            level
        }
    }
"""

CORE_METADATA_FIELDS = """
    fragment CoreMetadataFields on MetaDataType {
        id
        name
        value
        description
        type
        valueString
        valueMedia {
            id
            name
        }
        dataStandard {
            id
            name
            level
        }
    }
"""

CORE_VARIABLE_FIELDS = """
    fragment CoreVariableFields on VariableType {
        id
        name
        description
        units
        vartype
        calculator {
            id
            name
        }
        dataStandard {
            id
            name
            level
        }
    }
"""

CORE_VARIABLE_FIELDS_WITH_DATA = """
    fragment CoreVariableFieldsWithData on VariableType {
        ...CoreVariableFields
        time
        data
        processTime
    }
"""

CORE_NOTE_FIELDS = """
    fragment CoreNoteFields on NoteType {
        id
        note
        processTime
        user {
            id
            username
        }
    }
"""

CORE_CALCULATOR_FIELDS = """
    fragment CoreCalculatorFields on CalculatorType {
        id
        order
        name
        description
        calcfunction
        expression
        level
        message
        enabled
        calculatorSave {
            id
            calculatorSet {
                id
                name
                order
            }
        }
    }
"""
