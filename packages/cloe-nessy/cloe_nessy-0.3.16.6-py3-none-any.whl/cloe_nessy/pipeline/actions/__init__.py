from enum import Enum

from ..pipeline_action import PipelineAction
from .read_api import ReadAPIAction
from .read_catalog_table import ReadCatalogTableAction
from .read_excel import ReadExcelAction
from .read_files import ReadFilesAction
from .read_metadata_yaml import ReadMetadataYAMLAction
from .transform_change_datatype import TransformChangeDatatypeAction
from .transform_clean_column_names import TransformCleanColumnNamesAction
from .transform_concat_columns import TransformConcatColumnsAction
from .transform_decode import TransformDecodeAction
from .transform_distinct import TransformDistinctAction
from .transform_filter import TransformFilterAction
from .transform_generic_sql import TransformSqlAction
from .transform_group_aggregate import TransformGroupAggregate
from .transform_hash_columns import TransformHashColumnsAction
from .transform_join import TransformJoinAction
from .transform_json_normalize import TransformJsonNormalize
from .transform_rename_columns import TransformRenameColumnsAction
from .transform_replace_values import TransformReplaceValuesAction
from .transform_select_columns import TransformSelectColumnsAction
from .transform_union import TransformUnionAction
from .write_catalog_table import WriteCatalogTableAction
from .write_delta_append import WriteDeltaAppendAction
from .write_delta_merge import WriteDeltaMergeAction
from .write_file import WriteFileAction

# Get all subclasses of PipelineAction defined in this submodule
pipeline_actions = {cls.name: cls for cls in PipelineAction.__subclasses__()}
# Register all subclasses dynamically as enum using their "name" attribute as
# key. We need to do this here, because otherwise we don't get all subclasses
# from a relative import of PipelineAction
PipelineActionType = Enum("PipelineActionType", pipeline_actions)  # type: ignore

__all__ = [
    "ReadAPIAction",
    "ReadCatalogTableAction",
    "ReadExcelAction",
    "ReadFilesAction",
    "ReadMetadataYAMLAction",
    "PipelineActionType",
    "TransformFilterAction",
    "TransformUnionAction",
    "TransformChangeDatatypeAction",
    "TransformCleanColumnNamesAction",
    "TransformConcatColumnsAction",
    "TransformDecodeAction",
    "TransformDistinctAction",
    "TransformSqlAction",
    "TransformGroupAggregate",
    "TransformJoinAction",
    "TransformJsonNormalize",
    "TransformRenameColumnsAction",
    "TransformReplaceValuesAction",
    "TransformSelectColumnsAction",
    "WriteCatalogTableAction",
    "WriteDeltaAppendAction",
    "WriteDeltaMergeAction",
    "WriteFileAction",
    "TransformHashColumnsAction",
]
