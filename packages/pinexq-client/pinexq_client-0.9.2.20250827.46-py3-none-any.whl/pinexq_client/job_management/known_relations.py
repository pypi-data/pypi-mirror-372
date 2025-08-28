from enum import StrEnum


class Relations(StrEnum):
    SELF = "self"
    ITEM = "item"
    DOWNLOAD = "Download"
    CREATED_RESSOURCE = "created-resource"
    USED_TAGS = "UsedTags"

    # query pagination
    FIRST = "first"
    PREVIOUS = "previous"
    NEXT = "next"
    LAST = "last"
    ALL = "all"

    # job
    PARENT_JOB = "ParentJob"
    SELECTED_PROCESSING_STEP = "SelectedProcessingStep"
    INPUT_DATASLOT = "InputDataSlot"
    OUTPUT_DATASLOT = "OutputDataSlot"

    # workdata
    PRODUCED_BY_JOB = "ProducedByJob"
    PRODUCED_BY_PROCESSING_STEP = "ProducedByProcessingStep"

    # dataslots
    SELECTED = "Selected"
    ASSIGNED = "Assigned"

    # info
    CURRENT_USER = "CurrentUser"
