from enum import Enum


class DeltaTableOperationType(Enum):
    """Mapping between Delta table operation types and their operation metric keys available in the Delta table history.

    Values of metric keys included in this mapping are reported using the
    logging capabilities of the Delta operations of the DeltaManager.

    See https://docs.databricks.com/delta/history.html for a complete list and
    description of available metrics for each operation type.
    """

    UPDATE = ["numUpdatedRows"]
    DELETE = ["numDeletedRows", "numRemovedFiles"]
    MERGE = ["numSourceRows", "numTargetRowsInserted", "numTargetRowsUpdated", "numTargetRowsDeleted", "numOutputRows"]
    WRITE = ["numOutputRows"]
    TRUNCATE = ["numRemovedFiles"]
    OPTIMIZE = ["numAddedFiles", "numRemovedFiles", "minFileSize", "p50FileSize", "maxFileSize"]
    VACUUM = ["numDeletedFiles"]
    STREAMING_UPDATE = ["numRemovedFiles", "numOutputRows", "numOutputBytes", "numAddedFiles"]
