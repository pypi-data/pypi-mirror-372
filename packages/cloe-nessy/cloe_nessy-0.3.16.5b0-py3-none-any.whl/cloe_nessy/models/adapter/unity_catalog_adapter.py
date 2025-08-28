from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from cloe_nessy.logging.logger_mixin import LoggerMixin
from cloe_nessy.models import ForeignKey

from ...session import SessionManager
from ..catalog import Catalog
from ..column import Column
from ..schema import Schema
from ..table import Table


class UnityCatalogAdapter(LoggerMixin):
    """Acts as a translator between Unity Catalog metadata and Nessy Models."""

    def __init__(self, spark: SparkSession | None = None):
        """Initializes the UnityCatalogAdapter class."""
        self._spark = spark or SessionManager.get_spark_session()
        self._console_logger = self.get_console_logger()
        self._catalogs = self.get_catalogs()

    def _execute_sql(self, query):
        """Execute a SQL query and return a DataFrame.

        This wrapper is used for better testability.

        Returns:
            The resulting DataFrame after executing the SQL query.
        """
        return self._spark.sql(query)

    def get_catalogs(self) -> list[Catalog]:
        """Retrieve a list of catalogs with their associated metadata.

        Returns:
            A list of `Catalog` objects.
        """
        df = self._execute_sql("SHOW CATALOGS")
        catalogs = []
        for catalog in df.collect():
            name = catalog["catalog"]
            catalog_metadata = self._execute_sql(f"DESCRIBE CATALOG EXTENDED {name}")
            pivoted_metadata = catalog_metadata.withColumn("dummy", F.lit("dummy"))
            pivoted_df = pivoted_metadata.groupBy("dummy").pivot("info_name").agg(F.first("info_value"))
            catalog_owner = pivoted_df.collect()[0]["Owner"]
            comment = pivoted_df.collect()[0]["Comment"]
            catalogs.append(Catalog(name=name, owner=catalog_owner, comment=comment))
        return catalogs

    def get_catalog_by_name(self, name: str) -> Catalog | None:
        """Returns a Catalog by its name.

        Args:
            name: The name of the Catalog.

        Returns:
            The Catalog with the specified name.
        """
        for catalog in self._catalogs:
            if catalog.name == name:
                return catalog
        self._console_logger.warning(f"No catalog found with name: {name}")
        return None

    def get_catalog_schemas(self, catalog: str | Catalog) -> list[Schema]:
        """Collects all schemas in a given catalog.

        Args:
            catalog: The catalog from which the schemas are to be collected.

        Returns:
            A list of `Schema` objects.
        """
        schemas = []
        if isinstance(catalog, Catalog):
            catalog = catalog.name
        schemas_df = self._execute_sql(f"SELECT * FROM {catalog}.information_schema.schemata").collect()

        for schema in schemas_df:
            schemas.append(
                Schema(
                    name=schema["schema_name"],
                    catalog=catalog,
                    comment=schema["comment"],
                ),
            )
        return schemas

    def get_schema_by_name(self, catalog: str | Catalog, name: str) -> Schema | None:
        """Retrieve a schema by its name from a specified catalog.

        Args:
            catalog: The catalog from which to retrieve the schema.
                This can be either a string representing the catalog name or a
                `Catalog` object.
            name: The name of the schema to retrieve.

        Returns:
            The `Schema` object if found, otherwise `None`.
        """
        if isinstance(catalog, Catalog):
            catalog = catalog.name
        schemas = self.get_catalog_schemas(catalog)
        for schema in schemas:
            if schema.name == name:
                schema = self.add_tables_to_schema(catalog, schema)
                return schema

        self._console_logger.warning(f"No Schema in Catalog [ '{catalog}' ] found with name [ '{name}' ]")
        return None

    def get_table_by_name(self, table_identifier: str) -> Table | None:
        """Retrieve a table by it's name."""
        if len(table_identifier.split(".")) != 3:
            raise ValueError("The identifier must be in the format 'catalog.schema.table'")

        catalog_name, schema_name, table_name = table_identifier.split(".")
        table_metadata_df = self._execute_sql(
            f"""
            SELECT * FROM {catalog_name}.information_schema.tables
                WHERE table_catalog == '{catalog_name}'
                AND table_schema == '{schema_name}'
                AND table_name == '{table_name}'
                AND table_type <> 'VIEW'
            """,
        )
        if not table_metadata_df.head(1):
            table = None
        else:
            table_metadata = table_metadata_df.collect()[0]
            table_tags_list = self._execute_sql(
                f"""
                SELECT tag_name, tag_value FROM {catalog_name}.information_schema.table_tags
                    WHERE catalog_name == '{catalog_name}'
                    AND schema_name == '{schema_name}'
                    AND table_name == '{table_name}'
                """,
            ).collect()
            table_tags = {r["tag_name"]: r["tag_value"] for r in table_tags_list}
            table = Table(
                identifier=table_identifier,
                data_source_format=table_metadata["data_source_format"],
                business_properties=table_tags,
                storage_path=table_metadata["storage_path"],
                columns=[],
                is_external=table_metadata["table_type"] != "MANAGED",
            )
            table = self.add_columns_to_table(table)
        return table

    def add_tables_to_schema(self, catalog: str | Catalog, schema: str | Schema) -> Schema:
        """Add tables to a schema within a specified catalog.

        This method retrieves all tables within the specified schema and catalog,
        and adds them to the `Schema` object. The schema is updated with `Table`
        objects containing details about each table.

        Args:
            catalog: The catalog containing the schema. This can be
                either a string representing the catalog name or a `Catalog` object.
            schema: The schema to which tables will be added. This
                can be either a string representing the schema name or a `Schema`
                object.

        Returns:
            The updated `Schema` object with tables added.
        """
        if isinstance(catalog, Catalog):
            catalog_name = catalog.name
        else:
            catalog_name = catalog
        if isinstance(schema, str):
            schema_obj = self.get_schema_by_name(catalog_name, schema)
            if schema_obj is None:
                raise ValueError(f"Schema {schema} not found in catalog {catalog_name}.")
        else:
            schema_obj = schema
        tables_df = self._execute_sql(
            f"SELECT * FROM {catalog_name}.information_schema.tables WHERE table_catalog == '{catalog_name}' AND table_schema == '{schema_obj.name}' AND table_type <> 'VIEW'",
        ).collect()
        for table_row in tables_df:
            table_name = table_row["table_name"]
            table_tags_list = self._execute_sql(
                f"""SELECT tag_name, tag_value FROM {catalog_name}.information_schema.table_tags
                                           WHERE
                                                catalog_name == '{catalog_name}'
                                            AND schema_name == '{schema_obj.name}'
                                            AND table_name == '{table_name}'
                                           """,
            ).collect()
            table_tags = {r["tag_name"]: r["tag_value"] for r in table_tags_list}

            table = Table(
                data_source_format=table_row["data_source_format"],
                identifier=f"{catalog}.{schema_obj.name}.{table_name}",
                business_properties=table_tags,
                columns=[],
            )
            table = self.add_columns_to_table(table)
            schema_obj.add_table(table)
        return schema_obj

    def add_columns_to_table(self, table: Table) -> Table:
        """Add columns to a table by retrieving column metadata from the information schema.

        This method retrieves column details for the specified `table` from the
        information schema and adds `Column` objects to the `Table`. It also identifies
        primary key columns for the table.

        Args:
            table: The `Table` object to which columns will be added. The
                `Table` object must have its `identifier` attribute set.

        Returns:
            The updated `Table` object with columns added.
        """
        if not table.identifier:
            raise ValueError("Please set the Identifier of the Table to use this method.")
        cols_df = self._execute_sql(
            f"""
            SELECT * FROM {table.catalog}.information_schema.columns
                WHERE table_name == '{table.name}'
                AND table_schema == '{table.schema}'
                ORDER BY ordinal_position
            """,
        ).collect()
        partition_cols_indexed = {}
        for col_row in cols_df:
            generated = "GENERATED ALWAYS AS IDENTITY" if col_row["is_identity"] == "YES" else None
            table.add_column(
                Column(
                    name=col_row["column_name"],
                    data_type=col_row["data_type"],
                    default_value=col_row["column_default"],
                    generated=generated,
                    nullable=col_row["is_nullable"] == "YES",
                ),
            )
            if col_row["partition_index"] is not None:
                partition_cols_indexed.update({str(col_row["partition_index"]): col_row["column_name"]})
        partitioned_by = [val for _, val in sorted(partition_cols_indexed.items())]
        if partitioned_by:
            table.liquid_clustering = False
            table.partition_by = partitioned_by
        table = self._identify_pk_columns(table)
        table = self._identify_fk_constraints(table)
        return table

    def _identify_pk_columns(self, table: Table) -> Table:
        result = self._execute_sql(
            f"""
                SELECT A.column_name
                FROM {table.catalog}.information_schema.key_column_usage AS A
                JOIN {table.catalog}.information_schema.table_constraints AS B
                    USING (constraint_catalog, constraint_schema, constraint_name)
                WHERE
                    A.table_catalog = '{table.catalog}'
                AND A.table_schema = '{table.schema}'
                AND A.table_name = '{table.name}'
                AND B.constraint_type = 'PRIMARY KEY'
            """,
        ).collect()
        table.composite_primary_key = [col_row["column_name"] for col_row in result]
        return table

    def _identify_fk_constraints(self, table: Table) -> Table:
        result = self._execute_sql(
            f"""
                SELECT
                concat_ws(".", C.table_catalog, C.table_schema, C.table_name) as source_table_identifier,
                C.column_name as source_column,
                concat_ws(".", B.table_catalog, B.table_schema, B.table_name) as parent_table_identifier,
                B.column_name as parent_column
                -- fk_option currently not supported
                -- ,concat_ws(" ",D.match_option, "ON UPDATE", D.update_rule, "ON DELETE", D.delete_rule) AS fk_options
                FROM {table.catalog}.information_schema.table_constraints AS A
                LEFT JOIN {table.catalog}.information_schema.constraint_column_usage AS B USING(constraint_name)
                LEFT JOIN {table.catalog}.information_schema.key_column_usage AS C USING(constraint_name)
                -- LEFT JOIN {table.catalog}.information_schema.referential_constraints AS D USING(constraint_name)
                WHERE
                    A.table_catalog == '{table.catalog}'
                AND A.table_schema = '{table.schema}'
                AND A.table_name == '{table.name}'
                AND A.constraint_type == "FOREIGN KEY"
            """,
        ).collect()
        table.foreign_keys = [
            ForeignKey(
                foreign_key_columns=fk_row["source_column"],
                parent_table=fk_row["parent_table_identifier"],
                parent_columns=fk_row["parent_column"],
            )
            for fk_row in result
        ]
        return table
