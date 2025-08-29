import base64
import json
import os.path
import sys
from abc import ABC
from time import time
import platform
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Coroutine, Literal, Optional, Union, cast, Type
from pydantic import BaseModel, Field, field_serializer, field_validator, ConfigDict, model_validator, computed_field
import pandas as pd

from practicuscore.core_def import PRTEng, PRTConn, CoreDef, OPResult


class PrtBaseModel(BaseModel):
    model_config = {
        "arbitrary_types_allowed": True,
        "protected_namespaces": (),
    }


class PRTValidator(ABC):
    @staticmethod
    def validate(pydantic_obj: BaseModel) -> tuple[str | None, str | None]:
        """
        Validates all fields on a UI enabled Pydantic model, *if only* it has # "validators" metadata.
        # "validators" can be a single tuple (lambda_func, "err message") OR a list of validation tuples
           i.e. use a single validator:
            some_field: int = field(
                metadata={
                    # "validators": (lambda x: x > 0, "Must be > 0")
                })
           OR multiple validators:
            some_field: int = field(
                metadata={
                    # "validators": [(lambda x: x > 0, "Must be > 0"),
                                   (lambda x: x < 10, "Must be < 10")]
                })
        :param pydantic_obj: The pydantic UI enabled object to validate. Must have validators defined
        :return: if a field has errors, (field name, error message) tuple. Or (None, None)
        """
        for fld_name in pydantic_obj.model_fields:
            fld = pydantic_obj.model_fields[fld_name]
            if fld.json_schema_extra is not None and "validators" in fld.json_schema_extra:  # type: ignore[operator]
                validator_or_validators = fld.json_schema_extra["validators"]  # type: ignore[index]

                if isinstance(validator_or_validators, tuple):
                    validators = [validator_or_validators]
                else:
                    validators = validator_or_validators  # type: ignore[assignment]
                for validator_tuple in validators:
                    assert isinstance(validator_tuple, tuple), (
                        "Validator must be a tuple in the form of (validator_lambda, 'error message')"
                    )
                    validator_func, validator_err_msg = validator_tuple
                    field_val = getattr(pydantic_obj, fld_name)
                    try:
                        failed = False
                        if not validator_func(field_val):
                            failed = True
                    except Exception as ex:
                        failed = True
                        validator_err_msg = (
                            f"Exception occurred while checking for '{validator_err_msg}', \nException: {ex}"
                        )

                    if failed:
                        return (
                            fld_name,
                            validator_err_msg,
                        )  # return info about *first* encountered issue

        return None, None  # no issues, nothing to return


class RequestMeta(PrtBaseModel):
    meta_type: str = "Request"
    meta_name: str = ""
    req_time: datetime | None = None
    req_core_v: str = CoreDef.CORE_VERSION
    req_os: str = platform.system()
    req_os_v: str = platform.release()
    req_py_minor_v: int = sys.version_info.minor


class PRTRequest(PrtBaseModel):
    # Creating a meta class here caused a nasty bug. meta became a shared object between child classes
    #   i.e. when __post_init() below updated meta_name for one type of Request class, al others got the new name
    # meta: RequestMeta = RequestMeta()
    meta: RequestMeta | None = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.meta is None:
            self.meta = RequestMeta()
        if not self.meta.meta_name:
            self.meta.meta_name = self.__class__.__name__.rsplit("Request", 1)[0]
        if not self.meta.req_time:
            self.meta.req_time = datetime.now(timezone.utc)

    @property
    def name(self) -> str:
        assert self.meta is not None
        return self.meta.meta_name


class ResponseMeta(PrtBaseModel):
    meta_type: str = "Response"
    meta_name: str = ""
    resp_node_v: str = ""  # assigned later right before sending to client
    resp_py_minor_v: int = sys.version_info.minor


class PRTResponse(PrtBaseModel):
    meta: ResponseMeta | None = None
    op_result: OPResult | None = None
    # The below are for WebSocket Bridge (Home) and renamed from _footer etc.
    # Pydantic v2 does not support field names that start with _
    prt_footer: dict | None = None
    prt_str_payload: str | None = None

    # meta: ResponseMeta = ResponseMeta()  Don't instantiate here. Read notes for PRTRequest

    def __init__(self, **data):
        super().__init__(**data)
        if self.meta is None:
            self.meta = ResponseMeta()
        if not self.meta.meta_name:
            self.meta.meta_name = self.__class__.__name__.rsplit("Response", 1)[0]

    @property
    def name(self) -> str:
        assert self.meta is not None
        return self.meta.meta_name


class EmptyResponse(PRTResponse):
    # used when there's an error, no response can be created and we hae op_result send back
    pass


# Connection configuration classes


class ConnConf(PrtBaseModel):
    """Base connection configuration class"""

    connection_type: PRTConn | None = None
    is_enriched: bool | None = None
    uuid: str | None = None
    ws_uuid: str | None = None
    ws_name: str | None = None
    sampling_method: str | None = None
    sample_size: int | None = None
    sample_size_app: int | None = None
    column_list: list[str] | None = None
    filter: str | None = None

    def __str__(self):
        return str(self.model_dump_json(exclude_none=True))

    def __repr__(self):
        return str(self)

    @property
    def enriched(self) -> bool:
        return bool(self.is_enriched) if self.is_enriched is not None else False

    @property
    def conn_type(self) -> PRTConn:
        assert self.connection_type is not None
        return self.connection_type

    @property
    def friendly_desc(self) -> str:
        # override with children class for a better user-friendly
        return str(self.connection_type)

    @property
    def friendly_long_desc(self) -> str:
        return self.friendly_desc

    def copy_secure(self) -> "ConnConf":
        import copy

        return copy.copy(self)

    def copy_with_credentials(self, credentials: dict | None = None) -> "ConnConf":
        return self.copy_secure()

    def apply_conf_to(self, other: "ConnConf"):
        self._apply_conf_to(other)
        self.is_enriched = True

    def _apply_conf_to(self, other: "ConnConf"):
        pass

    def internal_equals(self, other: "ConnConf") -> bool:
        pass

    def __eq__(self, other: "ConnConf") -> bool:
        if not isinstance(other, ConnConf):
            return False
        other = cast(ConnConf, other)
        equals = (
            self.conn_type == other.conn_type
            and self.sample_size == other.sample_size
            and self.sample_size_app == other.sample_size_app
            and self.column_list == other.column_list
            and self.filter == other.filter
        )
        if not equals:
            return False
        return self.internal_equals(other)


class InMemoryConnConf(ConnConf):
    """For in-memory data sources connection configuration"""

    connection_type: PRTConn = PRTConn.IN_MEMORY
    df: Optional[pd.DataFrame] = Field(default=None, exclude=True)

    def __repr__(self):
        return str(self)

    @property
    def friendly_desc(self) -> str:
        return "In memory dataframe"

    def internal_equals(self, other: "ConnConf") -> bool:
        if not isinstance(other, InMemoryConnConf):
            return False
        other = cast(InMemoryConnConf, other)
        try:
            if self.df is not None and other.df is not None:
                return self.df.equals(other.df)
            return False
        except Exception as ex:
            print(f"ERROR: Could not compare dataframes: {ex}")
        return False


class LocalFileConnConf(ConnConf):
    """Local files connection configuration"""

    connection_type: PRTConn = PRTConn.LOCAL_FILE
    file_path: str | None = Field(
        json_schema_extra={"auto_ui": True},
        default=None,
        title="File Path",
        description="Type path on local disk",
    )

    def __repr__(self):
        return str(self)

    @property
    def friendly_desc(self) -> str:
        try:
            if self.file_path:
                return os.path.splitext(os.path.basename(self.file_path))[0]
        except:
            pass

        return self.conn_type.lower()

    @property
    def friendly_long_desc(self) -> str:
        final_desc: str = str(self.file_path)
        if final_desc and len(final_desc) > 30:
            final_desc = f"{final_desc[:15]} ... {final_desc[-10:]}"
        return final_desc if final_desc else "?"

    def internal_equals(self, other: "ConnConf") -> bool:
        if not isinstance(other, LocalFileConnConf):
            return False
        other = cast(LocalFileConnConf, other)
        return self.file_path == other.file_path

    @property
    def is_prt_file(self) -> bool:
        if self.file_path:
            return str(self.file_path).endswith(CoreDef.APP_FILE_TYPE)
        return False


class WorkerFileConnConf(ConnConf):
    """Files on a worker connection configuration"""

    connection_type: PRTConn = PRTConn.WORKER_FILE
    file_path: str | None = Field(
        json_schema_extra={"auto_ui": True},
        default=None,
        title="File Path",
        description="Type path on Worker local disk. E.g. /home/ubuntu/data/file.csv",
    )

    def __repr__(self):
        return str(self)

    @property
    def friendly_desc(self) -> str:
        try:
            if self.file_path:
                return os.path.splitext(os.path.basename(self.file_path))[0]
        except:
            pass

        return self.conn_type.lower()

    @property
    def friendly_long_desc(self) -> str:
        final_desc: str = str(self.file_path)
        if final_desc and len(final_desc) > 30:
            final_desc = f"{final_desc[:15]} ... {final_desc[-10:]}"
        return final_desc if final_desc else "?"

    def internal_equals(self, other: "ConnConf") -> bool:
        if not isinstance(other, WorkerFileConnConf):
            return False
        other = cast(WorkerFileConnConf, other)
        return self.file_path == other.file_path

    @property
    def is_prt_file(self) -> bool:
        if self.file_path:
            return str(self.file_path).endswith(CoreDef.APP_FILE_TYPE)
        return False


class S3ConnConf(ConnConf):
    """AWS S3 or compatible object storage (e.g. Minio, CEPH, Google Cloud Storage) connection configuration"""

    connection_type: PRTConn = PRTConn.S3
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_session_token: str | None = None
    endpoint_url: str | None = None
    s3_bucket: str | None = None
    s3_keys: list[str] | None = None
    default_prefix: str | None = None

    def __repr__(self):
        return str(self)

    @property
    def friendly_desc(self) -> str:
        try:
            if self.s3_keys and len(self.s3_keys) >= 1:
                s3_key: str = str(list(self.s3_keys)[0])
                if s3_key.find(".") > -1:
                    return os.path.splitext(os.path.basename(s3_key))[0]
                else:
                    return os.path.basename(os.path.normpath(s3_key))
        except:
            pass
        return self.conn_type.lower()

    @property
    def friendly_long_desc(self) -> str:
        if self.s3_bucket:
            bucket_desc = f"s3://{self.s3_bucket}"
        else:
            # k8s currently send no bucket name..
            bucket_desc = "s3://_bucket_"
        keys_desc = "?"
        if self.s3_keys:
            if len(self.s3_keys) == 1:
                keys_desc = list(self.s3_keys)[0]
            else:
                keys_desc = f"{list(self.s3_keys)[0]} .."

        final_desc = f"{bucket_desc}/{keys_desc}"
        if len(final_desc) > 30:
            final_desc = f"{final_desc[:15]} ... {final_desc[-10:]}"
        return final_desc

    def copy_secure(self) -> ConnConf:
        copy_conn_conf = super().copy_secure()
        assert isinstance(copy_conn_conf, S3ConnConf)
        copy_conn_conf = cast(S3ConnConf, copy_conn_conf)
        copy_conn_conf.aws_access_key_id = None
        copy_conn_conf.aws_secret_access_key = None
        copy_conn_conf.aws_session_token = None
        return copy_conn_conf

    def copy_with_credentials(self, credentials: dict | None = None) -> ConnConf:
        copy_conn_conf = super().copy_secure()
        copy_conn_conf = cast(S3ConnConf, copy_conn_conf)
        if credentials is not None:
            if "aws_access_key_id" in credentials:
                copy_conn_conf.aws_access_key_id = str(credentials["aws_access_key_id"])
            if "aws_secret_access_key" in credentials:
                copy_conn_conf.aws_secret_access_key = str(credentials["aws_secret_access_key"])
            if "aws_session_token" in credentials:
                copy_conn_conf.aws_session_token = str(credentials["aws_session_token"])
        return copy_conn_conf

    def internal_equals(self, other: "ConnConf") -> bool:
        if not isinstance(other, S3ConnConf):
            return False
        other = cast(S3ConnConf, other)
        return (
            self.aws_access_key_id == other.aws_access_key_id
            and self.aws_secret_access_key == other.aws_secret_access_key
            and self.aws_session_token == other.aws_session_token
            and self.s3_bucket == other.s3_bucket
            and self.s3_keys == other.s3_keys
        )

    def _apply_conf_to(self, other: "ConnConf"):
        assert isinstance(other, S3ConnConf), "apply credentials failed. other must be S3ConnConf"
        other = cast(S3ConnConf, other)
        other.aws_access_key_id = self.aws_access_key_id
        other.aws_secret_access_key = self.aws_secret_access_key
        other.s3_bucket = self.s3_bucket
        other.endpoint_url = self.endpoint_url


class RelationalConnConf(ConnConf):
    """Base class for all relational data stores connection configuration"""

    sql_query: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "auto_display": False,
            "validators": (lambda x: x and len(x) > 0, "No SQL query provided"),  # type: ignore[dict-item]
        },
        default=None,
        title="SQL Query",
        description="SQL Query to execute",
    )

    target_table_name: str | None = None
    target_schema: str | None = None
    target_table_if_exists: str | None = None
    chunk_size: int | None = None
    prefer_db_api: bool | None = None

    def __repr__(self):
        return str(self)

    def _find_table_name(self, keyword: str) -> str | None:
        if self.sql_query:
            table_ind = str(self.sql_query).lower().find(f"{keyword} ") + len(f"{keyword} ")
            if table_ind > -1:
                desc = str(self.sql_query)[table_ind:].strip().lower()
                next_stop = desc.find(" ")
                if next_stop > -1:
                    desc = desc[:next_stop]
                next_stop = desc.find(",")
                if next_stop > -1:
                    desc = desc[:next_stop]
                next_stop = desc.find("\n")
                if next_stop > -1:
                    desc = desc[:next_stop]

                desc = desc.strip()
                if desc:
                    return desc
        return None

    @property
    def friendly_desc(self) -> str:
        try:
            table_name = self._find_table_name("from")
            if not table_name:
                table_name = self._find_table_name("into")

            if table_name:
                return table_name

            if self.sql_query:
                return str(self.sql_query)[:10] + f"{'..' if len(self.sql_query) > 10 else ''}"
        except:
            pass
        assert self.connection_type is not None
        return self.connection_type.lower()

    @property
    def friendly_long_desc(self) -> str:
        assert self.connection_type is not None
        table_name: str | None
        if self.target_table_name:
            table_name = self.target_table_name
            if self.target_schema:
                table_name = f"{self.target_schema}.{table_name}"
            return f"{self.connection_type.capitalize()} table: {table_name}"
        else:
            table_name = self._find_table_name("from")
            if not table_name:
                table_name = self._find_table_name("into")

            if self.target_schema and table_name:
                table_name = f"{self.target_schema}.{table_name}"

            desc = ""
            if table_name:
                desc = f": {table_name}"
            elif self.sql_query:
                desc += f": {str(self.sql_query)[:20]}{'...' if len(str(self.sql_query)) > 20 else ''}"
            desc = desc.replace("\n", " ")
            final_desc = f"{self.connection_type.capitalize()}{desc}"
            if len(final_desc) > 30:
                final_desc = f"{final_desc[:15]} ... {final_desc[-10:]}"
            return final_desc

    def internal_equals(self, other: "ConnConf") -> bool:
        if not isinstance(other, RelationalConnConf):
            return False
        other = cast(RelationalConnConf, other)
        return self.sql_query == other.sql_query and self.target_table_name == other.target_table_name


class SqLiteConnConf(RelationalConnConf):
    """SQLite connection configuration"""

    connection_type: PRTConn = PRTConn.SQLITE
    file_path: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default=CoreDef.NODE_HOME_PATH + "/samples/data/chinook.db",
        title="File Path",
        description="Type path on Worker local disk. E.g. /home/ubuntu/data/database.db",
    )

    def __repr__(self):
        return str(self)

    def internal_equals(self, other: "ConnConf") -> bool:
        if not isinstance(other, SqLiteConnConf):
            return False
        other = cast(SqLiteConnConf, other)
        return self.file_path == other.file_path

    def _apply_conf_to(self, other: "ConnConf"):
        assert isinstance(other, SqLiteConnConf), "apply credentials failed. other must be SqLiteConnConf"
        other = cast(SqLiteConnConf, other)
        other.file_path = self.file_path


class MYSQLConnConf(RelationalConnConf):
    """MYSQL connection configuration"""

    connection_type: PRTConn = PRTConn.MYSQL
    db_host: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Database Server Address",
        description="E.g. mydb.mycompany.com or 192.168.0.1",
    )
    db_name: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default=None,
        title="Database Name",
    )
    db_port: int | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: 1 <= int(x) <= 65_535, "Port must be between 1 and 65,535"),  # type: ignore[dict-item]
        },
        default=3306,
        title="Port",
    )
    user: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default=None,
        title="User Name",
    )
    password: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "is_password": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default=None,
        title="Password",
    )

    def __repr__(self):
        return str(self)

    def internal_equals(self, other: "ConnConf") -> bool:
        if not isinstance(other, MYSQLConnConf):
            return False
        other = cast(MYSQLConnConf, other)
        return (
            self.db_host == other.db_host
            and self.db_name == other.db_name
            and self.db_port == other.db_port
            and self.user == other.user
            and self.password == other.password
        )

    def _apply_conf_to(self, other: "MYSQLConnConf"):
        assert isinstance(other, MYSQLConnConf), "apply credentials failed. other must be MYSQLConnConf"
        other = cast(MYSQLConnConf, other)
        other.db_host = self.db_host
        other.db_name = self.db_name
        other.db_port = self.db_port
        other.user = self.user
        other.password = self.password


class PostgreSQLConnConf(RelationalConnConf):
    """PostgreSQL connection configuration"""

    connection_type: PRTConn = PRTConn.POSTGRESQL
    db_host: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default=None,
        title="Database Server Address",
        description="E.g. mydb.mycompany.com or 192.168.0.1",
    )
    db_name: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default=None,
        title="Database Name",
    )
    db_port: int | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: 1 <= int(x) <= 65_535, "Port must be between 1 and 65,535"),  # type: ignore[dict-item]
        },
        default=5432,
        title="Port",
    )
    user: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="User Name",
    )
    password: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "is_password": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Password",
    )

    def __repr__(self):
        return str(self)

    def internal_equals(self, other: "ConnConf") -> bool:
        if not isinstance(other, PostgreSQLConnConf):
            return False
        other = cast(PostgreSQLConnConf, other)
        return (
            self.db_host == other.db_host
            and self.db_name == other.db_name
            and self.db_port == other.db_port
            and self.user == other.user
            and self.password == other.password
        )

    def _apply_conf_to(self, other: "PostgreSQLConnConf"):
        assert isinstance(other, PostgreSQLConnConf), "apply credentials failed. other must be PostgreSQLConnConf"
        other = cast(PostgreSQLConnConf, other)
        other.db_host = self.db_host
        other.db_name = self.db_name
        other.db_port = self.db_port
        other.user = self.user
        other.password = self.password


class RedshiftConnConf(RelationalConnConf):
    """AWS Redshift connection configuration"""

    connection_type: PRTConn = PRTConn.REDSHIFT
    # redshift_db_address: str | None = None  # dummy
    db_host: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Database Server Address",
        description="E.g. mydb.mycompany.com or 192.168.0.1",
    )
    db_name: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Database Name",
    )
    db_port: int | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: 1 <= int(x) <= 65_535, "Port must be between 1 and 65,535"),  # type: ignore[dict-item]
        },
        default=5439,
        title="Port",
    )
    user: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="User Name",
    )
    password: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "is_password": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Password",
    )

    def __repr__(self):
        return str(self)

    def internal_equals(self, other: "ConnConf") -> bool:
        if not isinstance(other, RedshiftConnConf):
            return False
        other = cast(RedshiftConnConf, other)
        return (
            self.db_host == other.db_host
            and self.db_name == other.db_name
            and self.db_port == other.db_port
            and self.user == other.user
            and self.password == other.password
        )

    def _apply_conf_to(self, other: "RedshiftConnConf"):
        assert isinstance(other, RedshiftConnConf), "apply credentials failed. other must be RedshiftConnConf"
        other = cast(RedshiftConnConf, other)
        other.db_host = self.db_host
        other.db_name = self.db_name
        other.db_port = self.db_port
        other.user = self.user
        other.password = self.password


class SnowflakeConnConf(RelationalConnConf):
    """Snowflake connection configuration"""

    connection_type: PRTConn = PRTConn.SNOWFLAKE
    db_name: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Database Name",
    )
    db_schema: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Database Schema",
    )
    warehouse_name: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Warehouse Name",
    )
    user: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="User Name",
    )
    role: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Role",
    )
    account: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Account Name",
    )
    password: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "is_password": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default=None,
        title="Password",
    )

    def __repr__(self):
        return str(self)

    def internal_equals(self, other: "ConnConf") -> bool:
        if not isinstance(other, SnowflakeConnConf):
            return False
        other = cast(SnowflakeConnConf, other)
        return (
            self.db_name == other.db_name
            and self.db_schema == other.db_schema
            and self.warehouse_name == other.warehouse_name
            and self.user == other.user
            and self.role == other.role
            and self.account == other.account
            and self.password == other.password
        )

    def _apply_conf_to(self, other: "SnowflakeConnConf"):
        assert isinstance(other, SnowflakeConnConf), "apply credentials failed. other must be SnowflakeConnConf"
        other = cast(SnowflakeConnConf, other)
        other.db_name = self.db_name
        other.db_schema = self.db_schema
        other.warehouse_name = self.warehouse_name
        other.user = self.user
        other.role = self.role
        other.account = self.account
        other.password = self.password


class MSSQLConnConf(RelationalConnConf):
    """Microsoft SQL Server connection configuration"""

    connection_type: PRTConn = PRTConn.MSSQL
    # redshift_db_address: str | None = None  # dummy
    db_host: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Database Server Address",
        description="E.g. mydb.mycompany.com or 192.168.0.1",
    )
    db_name: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default=None,
        title="Database Name",
    )
    # driver: str | None = Field(
    #     json_schema_extra={
    #         "auto_ui": True
    #     },
    #    default=None,
    #    title="Driver Name",
    #                     default_value="SQL Server Native Client 10.0"),
    #     # "validators": (lambda x: x and len(x) > 0, "No value provided")
    # })
    db_port: int | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: 1 <= int(x) <= 65_535, "Port must be between 1 and 65,535"),  # type: ignore[dict-item]
        },
        default=1433,
        title="Port",
    )
    user: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="User Name",
    )
    password: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "is_password": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Password",
    )

    def __repr__(self):
        return str(self)

    def internal_equals(self, other: "ConnConf") -> bool:
        if not isinstance(other, MSSQLConnConf):
            return False
        other = cast(MSSQLConnConf, other)
        return (
            self.db_host == other.db_host
            and self.db_name == other.db_name
            and self.db_port == other.db_port
            and self.user == other.user
            and self.password == other.password
        )

    def _apply_conf_to(self, other: "MSSQLConnConf"):
        assert isinstance(other, MSSQLConnConf), "apply credentials failed. other must be MSSQLConnConf"
        other = cast(MSSQLConnConf, other)
        other.db_host = self.db_host
        other.db_name = self.db_name
        other.db_port = self.db_port
        other.user = self.user
        other.password = self.password


class OracleConnConf(RelationalConnConf):
    """Oracle DB or DWH connection configuration"""

    connection_type: PRTConn = PRTConn.ORACLE
    # redshift_db_address: str | None = None  # dummy
    db_host: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Database Server Address",
        description="E.g. mydb.mycompany.com or 192.168.0.1",
    )
    service_name: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Service Name",
    )
    sid: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "is_required": False,
        },
        default="",
        title="Sid",
    )
    db_port: int | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: 1 <= int(x) <= 65_535, "Port must be between 1 and 65,535"),  # type: ignore[dict-item]
        },
        default=1521,
        title="Port",
    )
    user: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="User Name",
    )
    password: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "is_password": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Password",
    )

    def __repr__(self):
        return str(self)

    def internal_equals(self, other: "ConnConf") -> bool:
        if not isinstance(other, OracleConnConf):
            return False
        other = cast(OracleConnConf, other)
        return (
            self.db_host == other.db_host
            and self.service_name == other.service_name
            and self.sid == other.sid
            and self.db_port == other.db_port
            and self.user == other.user
            and self.password == other.password
        )

    def _apply_conf_to(self, other: "OracleConnConf"):
        assert isinstance(other, OracleConnConf), "apply credentials failed. other must be OracleConnConf"
        other = cast(OracleConnConf, other)
        other.db_host = self.db_host
        other.service_name = self.service_name
        other.sid = self.sid
        other.db_port = self.db_port
        other.user = self.user
        other.password = self.password


class HiveConnConf(RelationalConnConf):
    """Hive connection configuration"""

    connection_type: PRTConn = PRTConn.HIVE
    db_host: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Database Server Address",
        description="E.g. mydb.mycompany.com or 192.168.0.1",
    )
    db_name: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Database Name",
    )
    db_port: int | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: 1 <= int(x) <= 65_535, "Port must be between 1 and 65,535"),  # type: ignore[dict-item]
        },
        default=10000,
        title="Port",
    )
    user: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="User Name",
    )
    password: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "is_password": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Password",
    )

    def __repr__(self):
        return str(self)

    def internal_equals(self, other: "ConnConf") -> bool:
        if not isinstance(other, HiveConnConf):
            return False
        other = cast(HiveConnConf, other)
        return (
            self.db_host == other.db_host
            and self.db_name == other.db_name
            and self.db_port == other.db_port
            and self.user == other.user
            and self.password == other.password
        )

    def _apply_conf_to(self, other: "HiveConnConf"):
        assert isinstance(other, HiveConnConf), "apply credentials failed. other must be HiveConnConf"
        other = cast(HiveConnConf, other)
        other.db_host = self.db_host
        other.db_name = self.db_name
        other.db_port = self.db_port
        other.user = self.user
        other.password = self.password


class ClouderaConnConf(RelationalConnConf):
    """Cloudera connection configuration"""

    connection_type: PRTConn = PRTConn.CLOUDERA
    host: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Cloudera Host",
    )
    port: int | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: 1 <= int(x) <= 65_535, "Port must be between 1 and 65,535"),  # type: ignore[dict-item]
        },
        default=21050,
        title="Port",
    )
    user: str | None = Field(
        json_schema_extra={"auto_ui": True},
        default="",
        title="User Name",
        # "validators": (lambda x: x and len(x) > 0, "No value provided"
    )
    password: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "is_password": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Password",
    )

    def __repr__(self):
        return str(self)

    def internal_equals(self, other: "ConnConf") -> bool:
        if not isinstance(other, ClouderaConnConf):
            return False
        other = cast(ClouderaConnConf, other)
        return (
            self.host == other.host
            and self.port == other.port
            and self.user == other.user
            and self.password == other.password
        )

    def _apply_conf_to(self, other: "ClouderaConnConf"):
        assert isinstance(other, ClouderaConnConf), "apply credentials failed. other must be ClouderaConnConf"
        other = cast(ClouderaConnConf, other)
        other.host = self.host
        other.port = self.port
        other.user = self.user
        other.password = self.password


class AthenaConnConf(RelationalConnConf):
    """AWS Athena connection configuration"""

    connection_type: PRTConn = PRTConn.ATHENA
    db_host: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Database Server Address",
        description="E.g. mydb.mycompany.com or 192.168.0.1",
    )
    db_name: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Database Name",
    )
    s3_dir: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="S3 Location",
    )
    db_port: int | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: 1 <= int(x) <= 65_535, "Port must be between 1 and 65,535"),  # type: ignore[dict-item]
        },
        default=443,
        title="Port",
    )
    access_key: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="AWS Access key ID",
    )
    secret_key: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "is_password": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="AWS Secret access key",
    )

    def __repr__(self):
        return str(self)

    def internal_equals(self, other: "ConnConf") -> bool:
        if not isinstance(other, AthenaConnConf):
            return False
        other = cast(AthenaConnConf, other)
        return (
            self.db_host == other.db_host
            and self.db_name == other.db_name
            and self.s3_dir == other.s3_dir
            and self.db_port == other.db_port
            and self.access_key == other.access_key
            and self.secret_key == other.secret_key
        )

    def _apply_conf_to(self, other: "AthenaConnConf"):
        assert isinstance(other, AthenaConnConf), "apply credentials failed. other must be AthenaConnConf"
        other = cast(AthenaConnConf, other)
        other.db_host = self.db_host
        other.db_name = self.db_name
        other.db_port = self.db_port
        other.s3_dir = self.s3_dir
        other.access_key = self.access_key
        other.secret_key = self.secret_key


class ElasticSearchConnConf(RelationalConnConf):
    """ElasticSearch connection configuration"""

    connection_type: PRTConn = PRTConn.ELASTICSEARCH
    db_host: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Database Server Address",
        description="E.g. test-2.latest-elasticsearch.abc-3.xyz.com or 192.168.0.1",
    )
    db_port: int | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: 1 <= int(x) <= 65_535, "Port must be between 1 and 65,535"),  # type: ignore[dict-item]
        },
        default="",
        title="Port",
    )
    user: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="User Name",
    )
    password: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "is_password": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Password",
    )

    def __repr__(self):
        return str(self)

    def internal_equals(self, other: "ConnConf") -> bool:
        if not isinstance(other, ElasticSearchConnConf):
            return False
        other = cast(ElasticSearchConnConf, other)
        return (
            self.db_host == other.db_host
            and self.db_port == other.db_port
            and self.user == other.user
            and self.password == other.password
        )

    def _apply_conf_to(self, other: "ElasticSearchConnConf"):
        assert isinstance(other, ElasticSearchConnConf), "apply credentials failed. other must be ElasticSearchConnConf"
        other = cast(ElasticSearchConnConf, other)
        other.db_host = self.db_host
        other.db_port = self.db_port
        other.user = self.user
        other.password = self.password


class OpenSearchConnConf(RelationalConnConf):
    """OpenSearch connection configuration"""

    connection_type: PRTConn = PRTConn.OPENSEARCH
    db_host: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Database Server Address",
        description="E.g. search-test-abcde.us-east-1.es.amazonaws.com",
    )
    db_port: int | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: 1 <= int(x) <= 65_535, "Port must be between 1 and 65,535"),  # type: ignore[dict-item]
        },
        default=443,
        title="Port",
    )
    user: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="User Name",
    )
    password: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "is_password": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Password",
    )

    def __repr__(self):
        return str(self)

    def internal_equals(self, other: "ConnConf") -> bool:
        if not isinstance(other, OpenSearchConnConf):
            return False
        other = cast(OpenSearchConnConf, other)
        return (
            self.db_host == other.db_host
            and self.db_port == other.db_port
            and self.user == other.user
            and self.password == other.password
        )

    def _apply_conf_to(self, other: "OpenSearchConnConf"):
        assert isinstance(other, OpenSearchConnConf), "apply credentials failed. other must be OpenSearchConnConf"
        other = cast(OpenSearchConnConf, other)
        other.db_host = self.db_host
        other.db_port = self.db_port
        other.user = self.user
        other.password = self.password


class TrinoConnConf(RelationalConnConf):
    """Trino connection configuration"""

    connection_type: PRTConn = PRTConn.TRINO
    db_host: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Database Server Address",
        description="E.g. localhost",
    )
    db_port: int | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: 1 <= int(x) <= 65_535, "Port must be between 1 and 65,535"),  # type: ignore[dict-item]
        },
        default=8080,
        title="Port",
    )
    catalog: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Catalog",
    )
    db_schema: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Schema",
    )
    user: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="User Name",
    )
    password: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "is_password": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Password",
    )

    def __repr__(self):
        return str(self)

    def internal_equals(self, other: "ConnConf") -> bool:
        if not isinstance(other, TrinoConnConf):
            return False
        other = cast(TrinoConnConf, other)
        return (
            self.db_host == other.db_host
            and self.db_port == other.db_port
            and self.catalog == other.catalog
            and self.db_schema == other.db_schema
            and self.user == other.user
            and self.password == other.password
        )

    def _apply_conf_to(self, other: "TrinoConnConf"):
        assert isinstance(other, TrinoConnConf), "apply credentials failed. other must be TrinoConnConf"
        other = cast(TrinoConnConf, other)
        other.db_host = self.db_host
        other.db_port = self.db_port
        other.catalog = self.catalog
        other.db_schema = self.db_schema
        other.user = self.user
        other.password = self.password


class DremioConnConf(RelationalConnConf):
    """Dremio connection configuration"""

    connection_type: PRTConn = PRTConn.DREMIO
    db_host: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Database Server Address",
        description="E.g. localhost",
    )
    db_port: int | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: 1 <= int(x) <= 65_535, "Port must be between 1 and 65,535"),  # type: ignore[dict-item]
        },
        default=31010,
        title="Port",
    )
    user: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="User Name",
    )
    password: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "is_password": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Password",
    )

    def __repr__(self):
        return str(self)

    def internal_equals(self, other: "ConnConf") -> bool:
        if not isinstance(other, DremioConnConf):
            return False
        other = cast(TrinoConnConf, other)
        return (
            self.db_host == other.db_host
            and self.db_port == other.db_port
            and self.user == other.user
            and self.password == other.password
        )

    def _apply_conf_to(self, other: "DremioConnConf"):
        assert isinstance(other, DremioConnConf), "apply credentials failed. other must be DremioConnConf"
        other = cast(DremioConnConf, other)
        other.db_host = self.db_host
        other.db_port = self.db_port
        other.user = self.user
        other.password = self.password


class HanaConnConf(RelationalConnConf):
    """SAP Hana connection configuration"""

    connection_type: PRTConn = PRTConn.HANA
    db_host: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Database Server Address",
    )
    db_port: int | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: 1 <= int(x) <= 65_535, "Port must be between 1 and 65,535"),  # type: ignore[dict-item]
        },
        default=39015,
        title="Port",
    )
    db_name: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "is_required": False,
        },
        default="",
        title="Database Name",
    )
    user: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="User Name",
    )
    password: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "is_password": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Password",
    )

    def __repr__(self):
        return str(self)

    def internal_equals(self, other: "ConnConf") -> bool:
        if not isinstance(other, HanaConnConf):
            return False
        other = cast(HanaConnConf, other)
        return (
            self.db_host == other.db_host
            and self.db_port == other.db_port
            and self.db_name == other.db_name
            and self.user == other.user
            and self.password == other.password
        )

    def _apply_conf_to(self, other: "HanaConnConf"):
        assert isinstance(other, HanaConnConf), "apply credentials failed. other must be HanaConnConf"
        other = cast(HanaConnConf, other)
        other.db_host = self.db_host
        other.db_port = self.db_port
        other.db_name = self.db_name
        other.user = self.user
        other.password = self.password


class TeradataConnConf(RelationalConnConf):
    """Teradata connection configuration"""

    connection_type: PRTConn = PRTConn.TERADATA
    db_host: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Database Server Address",
    )
    user: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="User Name",
    )
    password: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "is_password": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Password",
    )

    def __repr__(self):
        return str(self)

    def internal_equals(self, other: "ConnConf") -> bool:
        if not isinstance(other, TeradataConnConf):
            return False
        other = cast(TeradataConnConf, other)
        return self.db_host == other.db_host and self.user == other.user and self.password == other.password

    def _apply_conf_to(self, other: "TeradataConnConf"):
        assert isinstance(other, TeradataConnConf), "apply credentials failed. other must be TeradataConnConf"
        other = cast(TeradataConnConf, other)
        other.db_host = self.db_host
        other.user = self.user
        other.password = self.password


class Db2ConnConf(RelationalConnConf):
    """IBM DB2 connection configuration"""

    connection_type: PRTConn = PRTConn.DB2
    db_host: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Database Server Address",
    )
    db_port: int | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: 1 <= int(x) <= 65_535, "Port must be between 1 and 65,535"),  # type: ignore[dict-item]
        },
        default=39015,
        title="Port",
    )
    db_name: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Database Name",
    )
    user: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="User Name",
    )
    password: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "is_password": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Password",
    )

    def __repr__(self):
        return str(self)

    def internal_equals(self, other: "ConnConf") -> bool:
        if not isinstance(other, Db2ConnConf):
            return False
        other = cast(Db2ConnConf, other)
        return (
            self.db_host == other.db_host
            and self.db_port == other.db_port
            and self.db_name == other.db_name
            and self.user == other.user
            and self.password == other.password
        )

    def _apply_conf_to(self, other: "Db2ConnConf"):
        assert isinstance(other, Db2ConnConf), "apply credentials failed. other must be Db2ConnConf"
        other = cast(Db2ConnConf, other)
        other.db_host = self.db_host
        other.db_port = self.db_port
        other.db_name = self.db_name
        other.user = self.user
        other.password = self.password


class DynamoDBConnConf(RelationalConnConf):
    """AWS DynamoDB connection configuration"""

    connection_type: PRTConn = PRTConn.DYNAMODB
    access_key: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="AWS Access Key Id",
    )
    secret_key: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "is_password": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="AWS Secret Access Key",
    )
    region: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="AWS Region Name",
        description="E.g. us-east-1",
    )

    def __repr__(self):
        return str(self)

    def internal_equals(self, other: "ConnConf") -> bool:
        if not isinstance(other, DynamoDBConnConf):
            return False
        other = cast(DynamoDBConnConf, other)
        return (
            self.access_key == other.access_key and self.secret_key == other.secret_key and self.region == other.region
        )

    def _apply_conf_to(self, other: "DynamoDBConnConf"):
        assert isinstance(other, DynamoDBConnConf), "apply credentials failed. other must be DynamoDBConnConf"
        other = cast(DynamoDBConnConf, other)
        other.access_key = self.access_key
        other.secret_key = self.secret_key
        other.region = self.region


class CockroachDBConnConf(RelationalConnConf):
    """CockroachDB connection configuration"""

    connection_type: PRTConn = PRTConn.COCKROACHDB
    db_host: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Database Server Address",
    )
    db_port: int | None = Field(
        json_schema_extra={"auto_ui": True},
        default=26257,
        title="Port",
        # "validators": (lambda x: 1 <= int(x) <= 65_535, "Port must be between 1 and 65,535"
    )
    db_name: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Database Name",
    )
    user: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="User Name",
    )
    password: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "is_password": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Password",
    )

    def __repr__(self):
        return str(self)

    def internal_equals(self, other: "ConnConf") -> bool:
        if not isinstance(other, CockroachDBConnConf):
            return False
        other = cast(CockroachDBConnConf, other)
        return (
            self.db_host == other.db_host
            and self.db_port == other.db_port
            and self.db_name == other.db_name
            and self.user == other.user
            and self.password == other.password
        )

    def _apply_conf_to(self, other: "CockroachDBConnConf"):
        assert isinstance(other, CockroachDBConnConf), "apply credentials failed. other must be CockroachDBConnConf"
        other = cast(CockroachDBConnConf, other)
        other.db_host = self.db_host
        other.db_port = self.db_port
        other.db_name = self.db_name
        other.user = self.user
        other.password = self.password


class CustomDBConnConf(RelationalConnConf):
    """Custom sqlalchemy compatible connection configuration"""

    connection_type: PRTConn = PRTConn.CUSTOM_DB
    # redshift_db_address: str | None = None  # dummy
    conn_string: str | None = Field(
        json_schema_extra={
            "auto_ui": True,
            "validators": (lambda x: x and len(x) > 0, "No value provided"),  # type: ignore[dict-item]
        },
        default="",
        title="Connection String",
        description="Any SQLAlchemy compatible db conn str (might require driver installation)",
    )

    def __repr__(self):
        return str(self)

    def internal_equals(self, other: "ConnConf") -> bool:
        if not isinstance(other, CustomDBConnConf):
            return False
        other = cast(CustomDBConnConf, other)
        return self.conn_string == other.conn_string

    def _apply_conf_to(self, other: "CustomDBConnConf"):
        assert isinstance(other, CustomDBConnConf), "apply credentials failed. other must be CustomDBConnConf"
        other = cast(CustomDBConnConf, other)
        other.conn_string = self.conn_string


class ConnConfFactory:
    """Factory class to generate connection configuration classes using a dictionary, json or an instance of the subject class"""

    @staticmethod
    def create_or_get(conn_conf_json_dict_or_obj) -> ConnConf:
        # due to json serialization this method can get json, dict or actual class
        conn_conf: ConnConf | None
        if isinstance(conn_conf_json_dict_or_obj, str):
            import json

            conn_conf_json_dict_or_obj = json.loads(conn_conf_json_dict_or_obj)

        if isinstance(conn_conf_json_dict_or_obj, dict):
            if "connection_type" in conn_conf_json_dict_or_obj:
                conn_type_str = conn_conf_json_dict_or_obj["connection_type"]
            else:
                print(
                    "WARNING: Using _conn_type in connection json will be retired. Please replace this connection with a newer version"
                )
                # future: retire in 2024-12. _conn_type is legacy definition for connection_type
                conn_type_str = conn_conf_json_dict_or_obj["_conn_type"]
            if conn_type_str == PRTConn.LOCAL_FILE:
                conn_conf = LocalFileConnConf.model_validate(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.WORKER_FILE:
                conn_conf = WorkerFileConnConf.model_validate(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.S3:
                conn_conf = S3ConnConf.model_validate(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.SQLITE:
                conn_conf = SqLiteConnConf.model_validate(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.MYSQL:
                conn_conf = MYSQLConnConf.model_validate(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.POSTGRESQL:
                conn_conf = PostgreSQLConnConf.model_validate(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.REDSHIFT:
                conn_conf = RedshiftConnConf.model_validate(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.SNOWFLAKE:
                conn_conf = SnowflakeConnConf.model_validate(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.MSSQL:
                conn_conf = MSSQLConnConf.model_validate(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.ORACLE:
                conn_conf = OracleConnConf.model_validate(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.HIVE:
                conn_conf = HiveConnConf.model_validate(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.ATHENA:
                conn_conf = AthenaConnConf.model_validate(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.ELASTICSEARCH:
                conn_conf = ElasticSearchConnConf.model_validate(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.OPENSEARCH:
                conn_conf = OpenSearchConnConf.model_validate(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.TRINO:
                conn_conf = TrinoConnConf.model_validate(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.DREMIO:
                conn_conf = DremioConnConf.model_validate(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.HANA:
                conn_conf = HanaConnConf.model_validate(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.TERADATA:
                conn_conf = TeradataConnConf.model_validate(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.DB2:
                conn_conf = Db2ConnConf.model_validate(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.DYNAMODB:
                conn_conf = DynamoDBConnConf.model_validate(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.COCKROACHDB:
                conn_conf = CockroachDBConnConf.model_validate(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.CLOUDERA:
                conn_conf = ClouderaConnConf.model_validate(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.CUSTOM_DB:
                conn_conf = CustomDBConnConf.model_validate(conn_conf_json_dict_or_obj)
            else:
                raise AttributeError(f"Unknown connection type {conn_type_str}")
        elif issubclass(type(conn_conf_json_dict_or_obj), ConnConf):
            conn_conf = conn_conf_json_dict_or_obj
        else:
            raise SystemError(f"Unknown conn_conf type {type(conn_conf_json_dict_or_obj)}")

        if conn_conf is not None:
            return conn_conf
        else:
            raise SystemError(f"Unknown conn_conf {conn_conf_json_dict_or_obj}")


# Engine Configuration Classes


class EngConf(PrtBaseModel):
    eng_type: PRTEng | None = None


class AutoEngConf(EngConf):
    eng_type: PRTEng = PRTEng.AUTO


class PandasEngConf(EngConf):
    eng_type: PRTEng = PRTEng.PANDAS


class DaskEngConf(PandasEngConf):
    eng_type: PRTEng = PRTEng.DASK
    worker_count: int | None = None


class RapidsEngConf(PandasEngConf):
    eng_type: PRTEng = PRTEng.RAPIDS


class RapidsDaskEngConf(DaskEngConf):
    eng_type: PRTEng = PRTEng.RAPIDS_DASK
    worker_count: int | None = None


class SparkEngConf(PandasEngConf):
    eng_type: PRTEng = PRTEng.SPARK


class EngConfFactory:
    @staticmethod
    def create_or_get(eng_conf_json_dict_or_obj) -> EngConf:
        # due to json serialization this method can get json, dict or actual class
        if not eng_conf_json_dict_or_obj:
            return PandasEngConf()

        if isinstance(eng_conf_json_dict_or_obj, str):
            if eng_conf_json_dict_or_obj.strip().startswith("{"):
                import json

                eng_conf_json_dict_or_obj = json.loads(eng_conf_json_dict_or_obj)
            else:
                # simple engine name, might be coming from exported code library
                eng_conf_json_dict_or_obj = {"eng_type": eng_conf_json_dict_or_obj}

        if isinstance(eng_conf_json_dict_or_obj, EngConf):
            return eng_conf_json_dict_or_obj
        elif isinstance(eng_conf_json_dict_or_obj, dict):
            eng_type_str = str(eng_conf_json_dict_or_obj["eng_type"]).upper()
            if eng_type_str == PRTEng.AUTO:
                return AutoEngConf.model_validate(eng_conf_json_dict_or_obj)
            elif eng_type_str == PRTEng.PANDAS:
                return PandasEngConf.model_validate(eng_conf_json_dict_or_obj)
            elif eng_type_str == PRTEng.DASK:
                return DaskEngConf.model_validate(eng_conf_json_dict_or_obj)
            elif eng_type_str == PRTEng.RAPIDS:
                return RapidsEngConf.model_validate(eng_conf_json_dict_or_obj)
            elif eng_type_str == PRTEng.RAPIDS_DASK:
                return RapidsDaskEngConf.model_validate(eng_conf_json_dict_or_obj)
            elif eng_type_str == PRTEng.SPARK:
                return SparkEngConf.model_validate(eng_conf_json_dict_or_obj)
            else:
                raise AttributeError(f"Unknown engine type {eng_type_str}")
        elif isinstance(eng_conf_json_dict_or_obj, PRTEng):
            if eng_conf_json_dict_or_obj == PRTEng.AUTO:
                return AutoEngConf()
            elif eng_conf_json_dict_or_obj == PRTEng.PANDAS:
                return PandasEngConf()
            elif eng_conf_json_dict_or_obj == PRTEng.DASK:
                return DaskEngConf()
            elif eng_conf_json_dict_or_obj == PRTEng.RAPIDS:
                return RapidsEngConf()
            elif eng_conf_json_dict_or_obj == PRTEng.RAPIDS_DASK:
                return RapidsDaskEngConf()
            elif eng_conf_json_dict_or_obj == PRTEng.SPARK:
                return SparkEngConf()
            else:
                raise AttributeError(f"Unknown PRTEng type {eng_conf_json_dict_or_obj}")
        else:
            raise SystemError(f"Unknown eng_conf type {type(eng_conf_json_dict_or_obj)}")


class PRTDataRequest(PRTRequest):
    # ** History: we needed to add dict to this list since when dataclass_json could not figure out type
    #    it returns dict instead of actual class. need to override or use as dict.
    #    After Pydantic migration, we might not need this anymore.
    conn_conf: Optional[
        Union[
            ConnConf,
            WorkerFileConnConf,
            SqLiteConnConf,
            S3ConnConf,
            MYSQLConnConf,
            PostgreSQLConnConf,
            RedshiftConnConf,
            SnowflakeConnConf,
            MSSQLConnConf,
            OracleConnConf,
            HiveConnConf,
            AthenaConnConf,
            ElasticSearchConnConf,
            OpenSearchConnConf,
            TrinoConnConf,
            DremioConnConf,
            HanaConnConf,
            TeradataConnConf,
            Db2ConnConf,
            DynamoDBConnConf,
            CockroachDBConnConf,
            ClouderaConnConf,
            CustomDBConnConf,
            dict,
        ]
    ] = None

    eng_conf: Optional[
        Union[
            AutoEngConf,
            PandasEngConf,
            DaskEngConf,
            RapidsEngConf,
            RapidsDaskEngConf,
            SparkEngConf,
            dict,
        ]
    ] = None


class ConnConfClassFactory:
    @staticmethod
    def get_conn_conf_class(
        conn_type: PRTConn,
    ) -> Union[
        Type[WorkerFileConnConf],
        Type[S3ConnConf],
        Type[SqLiteConnConf],
        Type[PostgreSQLConnConf],
        Type[MYSQLConnConf],
        Type[RedshiftConnConf],
        Type[SnowflakeConnConf],
        Type[MSSQLConnConf],
        Type[OracleConnConf],
        Type[HiveConnConf],
        Type[AthenaConnConf],
        Type[ElasticSearchConnConf],
        Type[OpenSearchConnConf],
        Type[TrinoConnConf],
        Type[DremioConnConf],
        Type[HanaConnConf],
        Type[TeradataConnConf],
        Type[Db2ConnConf],
        Type[DynamoDBConnConf],
        Type[CockroachDBConnConf],
        Type[ClouderaConnConf],
        Type[CustomDBConnConf],
    ]:
        if conn_type == PRTConn.WORKER_FILE:
            return WorkerFileConnConf
        elif conn_type == PRTConn.S3:
            return S3ConnConf
        elif conn_type == PRTConn.SQLITE:
            return SqLiteConnConf
        elif conn_type == PRTConn.POSTGRESQL:
            return PostgreSQLConnConf
        elif conn_type == PRTConn.MYSQL:
            return MYSQLConnConf
        elif conn_type == PRTConn.REDSHIFT:
            return RedshiftConnConf
        elif conn_type == PRTConn.SNOWFLAKE:
            return SnowflakeConnConf
        elif conn_type == PRTConn.MSSQL:
            return MSSQLConnConf
        elif conn_type == PRTConn.ORACLE:
            return OracleConnConf
        elif conn_type == PRTConn.HIVE:
            return HiveConnConf
        elif conn_type == PRTConn.ATHENA:
            return AthenaConnConf
        elif conn_type == PRTConn.ELASTICSEARCH:
            return ElasticSearchConnConf
        elif conn_type == PRTConn.OPENSEARCH:
            return OpenSearchConnConf
        elif conn_type == PRTConn.TRINO:
            return TrinoConnConf
        elif conn_type == PRTConn.DREMIO:
            return DremioConnConf
        elif conn_type == PRTConn.HANA:
            return HanaConnConf
        elif conn_type == PRTConn.TERADATA:
            return TeradataConnConf
        elif conn_type == PRTConn.DB2:
            return Db2ConnConf
        elif conn_type == PRTConn.DYNAMODB:
            return DynamoDBConnConf
        elif conn_type == PRTConn.COCKROACHDB:
            return CockroachDBConnConf
        elif conn_type == PRTConn.CLOUDERA:
            return ClouderaConnConf
        elif conn_type == PRTConn.CUSTOM_DB:
            return CustomDBConnConf
        else:
            raise SystemError(f"Unable to find conn_conf class for conn_type :{conn_type.name}")


class DistJobType(str, Enum):
    """
    Represents the type of distributed job or cluster environment you want to create and manage.

    Different distributed frameworks have varying requirements and behaviors. By specifying a `DistJobType`,
    you inform the Practicus AI platform how to set up, start, and manage the underlying distributed environment.

    **Types:**
    - `python`: A generic Python-based distributed job.
    - `torch`: A PyTorch-based distributed training job.
    - `deepspeed`: A DeepSpeed-based distributed training job.
    - `fairscale`: A FairScale-based distributed training job.
    - `horovod`: A Horovod-based distributed training job.
    - `spark`: A Spark-based distributed job or interactive cluster.
    - `dask`: A Dask-based distributed job or interactive cluster.
    - `ray`: A Ray-based distributed job or interactive cluster.
    - `custom`: A user-defined distributed job type with a custom adaptor.
    """

    python = "python"
    torch = "torch"
    deepspeed = "deepspeed"
    fairscale = "fairscale"
    horovod = "horovod"
    spark = "spark"
    dask = "dask"
    ray = "ray"
    custom = "custom"

    @classmethod
    def from_value(cls, value: str | Enum) -> "DistJobType":
        str_val = str(value.value if hasattr(value, "value") else value).upper()
        for i, enum_val in enumerate(cls):
            # noinspection PyUnresolvedReferences
            if str(enum_val.value).upper() == str_val:
                return cls(enum_val)

        valid_types = "\n".join(["- " + DistJobType(job).value for job in DistJobType])
        raise ValueError(f"{value} is not a valid job_type. Please use one of the following: \n{valid_types}")


class DistJobExecutorState(str, Enum):
    pending = "pending"
    ready = "ready"
    running = "running"
    completed = "completed"
    failed = "failed"
    killed = "killed"

    @classmethod
    def from_value(cls, value: str | Enum) -> "DistJobExecutorState":
        str_val = str(value.value if hasattr(value, "value") else value).upper()
        for i, enum_val in enumerate(cls):
            # noinspection PyUnresolvedReferences
            if str(enum_val.value).upper() == str_val:
                return cls(enum_val)

        raise ValueError(f"{value} is not a valid {cls}")


class DistJobExecutor(BaseModel):
    rank: int
    instance_id: str
    state: DistJobExecutorState | None = None
    used_ram: int | None = None
    peak_ram: int | None = None
    total_ram: int | None = None
    gpus: int | None = None
    used_vram: int | None = None
    peak_vram: int | None = None
    reserved_vram: int | None = None
    total_vram: int | None = None


class DistJobConfig(BaseModel):
    """
    Configuration for distributed jobs in Practicus AI.

    A distributed job involves multiple worker nodes cooperating to run a large-scale task, such as Spark, Dask, or
    Torch-based training jobs. This configuration defines how the cluster is formed, how many workers, memory, and CPU
    resources to allocate, as well as additional parameters like job directories, Python files, and termination
    conditions.

    **Usage Example:**
    ```python
    dist_conf = DistJobConfig(
        job_type=DistJobType.deepspeed,
        job_dir="/path/to/job_dir",
        worker_count=10,
        py_file="job.py"
    )
    ```
    """

    job_type: DistJobType
    """Specifies the type of distributed job (e.g., Spark, Dask, Torch, Python)."""

    job_dir: str | None = None
    """Directory containing job code and related files. For non-auto-distributed Spark and Dask jobs, and for all other 
    job types, this must be provided."""

    auto_distributed: bool | None = None
    """If True and `job_type` is Spark, the cluster is managed automatically (auto-scaling, etc.). Currently only supported 
    for Spark."""

    worker_count: int | None = Field(default=None, exclude=True)
    """(alias) Sets `initial_count` and `max_count` to the same value, resulting in a fixed cluster size. 
    Use `worker_count` if you are not auto-scaling."""

    initial_count: int | None = None
    """Set the initial number of workers. If not using `worker_count`, you must specify both `initial_count` and 
    `max_count`."""

    max_count: int | None = None
    """Set the maximum number of workers. If not using `worker_count`, must be set along with `initial_count`."""

    coordinator_port: int | None = None
    """The coordinator (master) port. If left empty, a suitable default is used based on `job_type`."""

    additional_ports: list[int] | None = None
    """List of extra ports for worker communication. Leave empty to use defaults. Most job types do not need these."""

    custom_adaptor: str | None = None
    """Specifies a custom Python class (adaptor) extending job handling logic. Must refer to a class accessible at runtime."""

    terminate_on_completion: bool | None = None
    """If True, terminates all workers after job completion. Set to False to keep the cluster alive for further 
    exploration, experiments, or debugging."""

    capture_script_output: bool | None = None
    """If True, captures and logs stdout/stderr of job scripts (e.g. .py, .sh). Disable if already logging to avoid duplicates."""

    service_mesh_sidecar: bool | None = None
    """By default disabled for performance. If True, enables service mesh sidecars for encrypted traffic between workers."""

    job_start_timeout_seconds: int | None = None
    """Time in seconds to wait for the cluster to fully start before timing out."""

    retries: int | None = None
    """Number of retries if the job fails, useful for transient failures."""

    sleep_between_retries: int | None = None
    """Seconds to wait between retries."""

    py_file: str | None = None
    """The Python file to run. If empty, defaults may apply (e.g. `job.py` or `train.py`)."""

    py_venv_name: str | None = None
    """The name of a Python virtual environment (under ~/.venv/) to use. Leave empty for the default venv."""

    log_in_run_dir: bool | None = None
    """If True, places logs and artifacts in the run directory. Leave empty for defaults."""

    measure_utilization: bool | None = None
    """If True, measures system and GPU utilization periodically."""

    measure_utilization_interval: int | None = None
    """Interval in seconds for measuring system and GPU usage if `measure_utilization` is True."""

    coordinator_is_worker: bool | None = None
    """If True, coordinator also acts as a worker. Default True if unset. If False, coordinator doesn't run tasks, freeing resources."""

    processes: int | None = None
    """Number of processes/executors per worker node. For Spark, this is the executor count per node; for Dask, the worker count."""

    threads: int | None = None
    """Number of threads per executor/process. In Spark, corresponds to executor cores; in Dask, `--nthreads` per worker."""

    memory_gb: int | None = None
    """Memory limit per executor/process in GB. For Spark, maps to executor/driver memory; for Dask, `--memory-limit`."""

    executors: list[DistJobExecutor] | None = None
    """(Read-only) A list of executor definitions, set by the system after cluster creation."""

    def __init__(self, **data):
        super().__init__(**data)
        if self.worker_count is not None:
            self.initial_count = self.worker_count
        if (
            not self.job_dir
            and not self.py_file
            and self.job_type in [DistJobType.spark, DistJobType.dask, DistJobType.ray]
            and not self.auto_distributed
        ):
            # Assign a system-managed job directory for certain interactive scenarios
            self.job_dir = CoreDef.AUTO_CREATED_DIST_JOB_DIR

    def __setattr__(self, name, value):
        if name == "worker_count":
            super().__setattr__("initial_count", value)
        super().__setattr__(name, value)

    @model_validator(mode="before")
    def validate_model(cls, values):
        auto_distributed = values.get("auto_distributed", False)
        job_type = DistJobType.from_value(values["job_type"])

        if auto_distributed and job_type != DistJobType.spark:
            raise ValueError("auto_distributed is currently only supported for Spark jobs.")

        needs_job_dir = False
        if job_type not in [DistJobType.spark, DistJobType.dask, DistJobType.ray]:
            needs_job_dir = True
        else:
            py_file = values.get("py_file", None)
            if py_file:
                needs_job_dir = True

        if needs_job_dir and (not values.get("job_dir")):
            raise ValueError("job_dir must be provided for this job configuration.")

        if "worker_count" not in values and "initial_count" not in values:
            raise ValueError("Number of workers not known. Set worker_count or initial_count and max_count.")

        if job_type in [DistJobType.dask, DistJobType.spark, DistJobType.ray]:
            py_file = values.get("py_file", None)
            terminate_on_completion = values.get("terminate_on_completion", None)
            if terminate_on_completion is True and not py_file:
                raise ValueError(
                    f"For {job_type.value} jobs, py_file must be provided if terminate_on_completion=True. "
                    "Otherwise, the cluster starts with no job to run and terminates instantly."
                )

        return values

    model_config = ConfigDict(validate_assignment=True)


class GitConfig(BaseModel):
    """
    Configuration details for interacting with a Git repository.
    """

    remote_url: str
    """The URL of the remote Git repository."""

    secret_name: str
    """Name of the secret (credentials/token) to authenticate with the Git repository."""

    save_secret: bool | None = None
    """Whether to persist the secret after retrieval (default: None, persists)."""

    username: str | None = None
    """Optional username for repository authentication (default: None)."""

    local_path: str | None = None
    """Local path for cloning or checking out the repository (default: None, uses ~/my/projects or ~/projects if no ~/my folder is present)."""

    branch: str | None = None
    """Git branch to check out. If None, the default branch is used (default: None)."""

    sparse_checkout_folders: list[str] | None = None
    """List of folders for sparse checkout. If None, all files and folders are checked out (default: None)."""

    fetch_depth: int | None = None
    """Shallow clone depth. If None, fetches the full commit history (default: None)."""


class ImageConfig(BaseModel):
    """
    ImageConfig is used within the Practicus AI platform to configure how
    container images are built, pulled, and managed. This configuration
    can be used to:

    - Provide registry credentials (username/password or use an existing
      Kubernetes secret).
    - Control Kubernetes pull policies.
    - Enable/disable container-building capabilities.
    - Specify builder configuration (capacity, insecure registries, custom builder URL).

    For example, you might want to create an `ImageConfig` to build or pull
    images from a private registry. You can set a username/password pair, or
    refer to an existing `repo_secret_name` in your Kubernetes environment.
    If you enable a builder (`builder=True`), you can fine-tune how much of
    the Worker capacity is used for building images (`builder_capacity`) and
    define insecure registries or custom builder URLs.
    """

    repo_username: str | None = None
    """Username for the container registry. Leave blank if not needed or if using repo_secret_name."""

    repo_password: str | None = None
    """Password or token for the container registry. Leave blank if not needed or if using repo_secret_name."""

    repo_secret_name: str | None = None
    """
    Kubernetes secret name for the container registry.
    If this is set, you must not set `repo_username` or `repo_password`.
    """

    pull_policy: str | None = None
    """
    Kubernetes pull policy for the container. Valid values:
      - Always
      - IfNotPresent
      - Never
    Leave empty to use the default setting.
    """

    builder: bool | None = None
    """
    If True, enables container-building functionality for custom images.
    Must be set to True in order to configure builder-specific fields.
    """

    builder_capacity: int | None = None
    """
    Defines the percentage (1–99) of Worker capacity allocated for building images.
    Can only be set if `builder=True`.
    """

    custom_builder_url: str | None = None
    """
    Optional custom image builder URL that extends or inherits from:
      - ghcr.io/practicusai/practicus-builder
      - or ../practicus-builder-privileged
    Can only be set if `builder=True`.
    """

    @field_validator("pull_policy")
    def validate_pull_policy(cls, value) -> str | None:
        valid_values = ["Always", "IfNotPresent", "Never"]
        if value and value not in valid_values:
            raise ValueError(f"Invalid pull_policy: {value}. Please leave empty or use one of: {valid_values}")
        return value

    @field_validator("builder_capacity")
    def validate_builder_capacity(cls, value) -> int | None:
        if value is not None and (value < 1 or value > 99):
            raise ValueError("Invalid builder_capacity. Must be between 1 and 99 (inclusive), or left empty.")
        return value

    @model_validator(mode="before")
    def validate_model(cls, values):
        """
        Cross-field validation:
        - `builder_capacity`, and `custom_builder_url`
          can only be set if `builder=True`.
        - If `repo_secret_name` is set, neither `repo_username` nor `repo_password`
          can be specified.
        """
        is_builder_enabled = values.get("builder") is True

        if not is_builder_enabled:
            for field_name in [
                "builder_capacity",
                "custom_builder_url",
            ]:
                if field_name in values and values[field_name] is not None:
                    raise ValueError(f"{field_name} can only be set if builder=True.")

        if "repo_secret_name" in values and values["repo_secret_name"] is not None:
            if any(field in values and values[field] is not None for field in ["repo_username", "repo_password"]):
                raise ValueError("If repo_secret_name is set, repo_username or repo_password cannot be set.")

        return values


class WorkerConfig(BaseModel):
    """
    Defines a worker configuration for launching Practicus AI Workers.

    **Usage Example:**

    ```python
    worker_config = WorkerConfig(
        worker_image="practicus",
        worker_size="Small",
    )
    ```
    """

    worker_image: str | None = None
    """
    The container image to be used for this worker.

    If you provide a simple image name like `practicus-gpu-torch`, it will be expanded to a full image name
    (e.g. `ghcr.io/practicusai/practicus-gpu-torch`) with a default version. You can also specify a fully qualified
    image such as `my-container-repo/my-container:some-version`.

    **Note:** Custom container images must be based on a Practicus AI-compatible base image.
    """

    worker_size: str | None = None
    """
    The worker size indicating the CPU, RAM, and GPU resources allocated to the worker.

    **Example:** "Small", "Medium", "Large".
    """

    service_type: str | None = None
    """
    The type of service this worker represents, typically "cloud_worker" or "workspace".
    If omitted, defaults to "cloud_worker".
    """

    network_protocol: str | None = None
    """
    The network protocol to use for this worker. Valid values are "http" or "https".
    If omitted, the worker will choose a suitable default.
    """

    distributed_config: DistJobConfig | None = Field(default=None, exclude=True)
    """
    Configuration for distributed jobs (e.g., Spark, Dask, Torch). 

    If provided, it defines the parameters and ports for running a distributed cluster.
    """

    image_config: ImageConfig | None = Field(default=None, exclude=True)
    """
    Configuration for using or building custom container images. Set this to an `ImageConfig` instance when you need 
    to provide registry credentials or enable image-building capabilities.  
    """

    startup_script: str | None = Field(default=None, exclude=True)
    """
    An optional startup script (shell commands) to be run when the worker starts. 
    This should be a small script and should complete around ~5 minutes to avoid time-outs.
    For scripts that need to run longer (e.g. for complex installations) please create a custom container image. 
    """

    log_level: str | None = Field(default=None, exclude=True)
    """
    The log level for the worker process itself. Examples: "DEBUG", "INFO", "WARNING", "ERROR".
    If omitted, defaults to a region-level or system default.
    """

    modules_log_level: str | None = Field(default=None, exclude=True)
    """
    A module-specific log level configuration, if you want certain modules to log at different levels.
    """

    bypass_ssl_verification: bool | None = Field(default=None, exclude=True)
    """
    Set this to "True" if you need to bypass SSL certificate verification. 
    Generally not recommended unless working with trusted but self-signed certs.
    """

    interactive: bool | None = Field(default=None, exclude=True)
    """
    Indicates if the worker should be run in an interactive mode, e.g. allowing shell access or interactive sessions.
    """

    service_url: str | None = None
    """
    An optional service URL. For special use-cases where the worker might need to connect to a particular endpoint 
    (e.g., a custom model host), you can specify it here.
    """

    email: str | None = None
    """
    An optional user email associated with this worker's configuration, if needed for authentication or logging.
    """

    refresh_token: str | None = None
    """
    An optional refresh token for authentication against certain services.

    If provided, the worker might use it to obtain a fresh access token automatically.
    """

    env_variables: dict | None = Field(default=None, exclude=True)
    """OS environment variables to pass to the worker."""

    personal_secrets: list[str] | None = Field(default=None, exclude=True)
    """List of personal secrets to pull from the vault."""

    shared_secrets: list[str] | None = Field(default=None, exclude=True)
    """Shared secrets saved by the admin in the vault."""

    git_configs: list["GitConfig"] | None = Field(default=None, exclude=True)
    """List of GitConfig objects for auto-syncing (clone or pull) repositories."""

    # 'e30=' -> base64 for '{}' - do not remove this, or field_serializer will not work for model_dump(exclude_none=True)
    additional_params: str | None = "e30="  # ** Do not make None **
    """(Internal and advanced use only) Read-only field. Additional params is used to base 64 decode/encode certain fields.
    **Do not set it manually** since the value of additional_params will be overwritten each time model_dump is called.
    """

    # Field Validators
    @field_validator("service_type")
    def validate_service_type(cls, value) -> str | None:
        valid_service_types = ["cloud_worker", "workspace"]
        if value and value not in valid_service_types:
            raise ValueError(f"Invalid service_type. Please leave empty or use one of: {valid_service_types}")
        return value

    @field_validator("network_protocol")
    def validate_network_protocol(cls, value) -> str | None:
        valid_network_protocols = ["http", "https"]
        if value and value not in valid_network_protocols:
            raise ValueError(f"Invalid network_protocol. Please leave empty or use one of: {valid_network_protocols}")
        return value

    @model_validator(mode="before")
    def validate_model(cls, values):
        # Future model-level validations can be added here.
        return values

    model_config = ConfigDict(validate_assignment=True)

    @model_validator(mode="before")
    @classmethod
    def _custom_model_validator(cls, data: Any) -> Any:
        """Decode additional_params during model initialization"""
        if not isinstance(data, dict):
            return data

        if "additional_params" not in data or not data["additional_params"]:
            return data

        try:
            # Decode base64 and parse JSON
            decoded_bytes = base64.b64decode(data["additional_params"])
            additional_params = json.loads(decoded_bytes.decode("utf-8"))

            # Handle complex fields
            if "distributed_conf_dict" in additional_params:
                data["distributed_config"] = additional_params["distributed_conf_dict"]

            if "image_conf_dict" in additional_params:
                data["image_config"] = additional_params["image_conf_dict"]

            if "git_configs" in additional_params:
                if not isinstance(additional_params["git_configs"], list):
                    raise ValueError("git_configs in additional_params is not a list")
                data["git_configs"] = additional_params["git_configs"]

            # Handle startup script
            if "startup_script_b64" in additional_params:
                data["startup_script"] = base64.b64decode(additional_params["startup_script_b64"]).decode("utf-8")

            # Map other fields
            field_mappings = {
                "PRT_LOG_LEVEL": "log_level",
                "PRT_MODULES_LOG_LEVEL": "modules_log_level",
                "bypass_ssl_verification": "bypass_ssl_verification",
                "PRT_INTERACTIVE": "interactive",
                "env_variables": "env_variables",
                "personal_secrets": "personal_secrets",
                "shared_secrets": "shared_secrets",
            }

            for src, dest in field_mappings.items():
                if src in additional_params:
                    data[dest] = additional_params[src]

            # Legacy support
            if "image_pull_policy" in additional_params:
                if "image_config" not in data:
                    data["image_config"] = {}
                data["image_config"]["pull_policy"] = additional_params["image_pull_policy"]

        except (ValueError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid additional_params format: {e}")

        return data

    @field_serializer("additional_params")
    def _serialize_additional_params(self, v: Optional[str], _info) -> Optional[str]:
        """Serialize excluded fields into additional_params during model_dump"""

        # Collect excluded fields into a dictionary
        additional_params_dict = {}
        additional_params_str: str | None = None

        # Serialize complex objects
        if self.distributed_config:
            additional_params_dict["distributed_conf_dict"] = self.distributed_config.model_dump(
                mode="json", exclude_none=True
            )

        if self.image_config:
            additional_params_dict["image_conf_dict"] = self.image_config.model_dump(exclude_none=True)

        if self.git_configs:
            additional_params_dict["git_configs"] = [gc.model_dump(exclude_none=True) for gc in self.git_configs]

        # Handle startup script with base64 encoding
        if self.startup_script is not None:
            additional_params_dict["startup_script_b64"] = base64.b64encode(
                self.startup_script.strip().encode("utf-8")
            ).decode("utf-8")

        # Map simple fields
        field_mappings = {
            "log_level": "PRT_LOG_LEVEL",
            "modules_log_level": "PRT_MODULES_LOG_LEVEL",
            "bypass_ssl_verification": "bypass_ssl_verification",
            "interactive": "PRT_INTERACTIVE",
            "env_variables": "env_variables",
            "personal_secrets": "personal_secrets",
            "shared_secrets": "shared_secrets",
        }

        for src, dest in field_mappings.items():
            value = getattr(self, src)
            if value is not None:
                additional_params_dict[dest] = value

        additional_params_str = base64.b64encode(json.dumps(additional_params_dict).encode("utf-8")).decode("utf-8")

        return additional_params_str  # If empty, returns "e30=" base64 for {}


class UploadS3Conf(BaseModel):
    """
    Configuration for uploading files to an S3-compatible storage.

    This class defines the parameters needed to upload files from a local source to a specified S3 bucket and prefix.
    It can also handle cutting part of the source path to simplify the uploaded key structure.

    **Usage Example:**
    ```python
    s3_conf = UploadS3Conf(
        bucket="my-bucket",
        prefix="data/backups",
        folder_path="local_data/",
        aws_access_key_id="AKIA...",
        aws_secret_access_key="secret...",
    )
    ```
    """

    bucket: str | None = None
    """
    The name of the S3 bucket to upload files to.

    **Example:** `"my-bucket"`
    """

    prefix: str | None = None
    """
    The prefix (folder/key path) inside the bucket where files will be placed.

    **Example:** `"data/backups"`

    If no prefix is provided, files are uploaded to the bucket's root.
    """

    folder_path: str | None = None
    """
    The local folder path containing the files to upload.

    **Example:** `"local_data/"`
    """

    source_path_to_cut: str | None = None
    """
    A portion of the source file path to remove when constructing the object key in S3.

    For example, if `source_path_to_cut` is `"/Users/username/abc"` and your file is at 
    `"/Users/username/abc/subfolder/file.csv"`, the uploaded S3 key becomes `"subfolder/file.csv"` 
    instead of `"Users/username/abc/subfolder/file.csv"`.
    """

    aws_access_key_id: str | None = None
    """
    AWS Access Key ID for authentication.

    If not provided, credentials may be sourced from the environment or a shared credentials file.
    """

    aws_secret_access_key: str | None = None
    """
    AWS Secret Access Key for authentication.

    Must be provided if `aws_access_key_id` is specified and no other credentials sources are used.
    """

    aws_session_token: str | None = None
    """
    An optional session token (STS token) used for temporary AWS credentials.

    Typically required if using temporary credentials from AWS STS.
    """

    endpoint_url: str | None = None
    """
    A custom endpoint URL for S3-compatible storage services (e.g., MinIO, Ceph).

    If provided, the SDK uses this endpoint instead of the standard AWS S3 endpoint.
    """


class MQConfig(BaseModel):
    """
    MQConfig is a unified configuration model for both RabbitMQ publishers and consumers (subscribers).
    It encapsulates all necessary parameters for connecting to a RabbitMQ broker and configuring
    message publishing and consumption (subscription). Adjust these parameters to fine-tune your publishers
    and consumers (subscribers).

    In production, ensure that the topology (exchanges, queues, bindings) is already configured.
    Alternatively, if you have configure privileges, call `mq.apply_topology(...)` to create
    the necessary artifacts, or `mq.export_topology(...)` to export artifacts and let an admin
    create the topology resources.
    """

    conn_str: str
    """AMQP URL (e.g. "amqp://user:pass@host/vhost")."""

    exchange: str | None = None
    """Exchange name.
    - If omitted, publishers use the channel's default exchange.
    """

    exchange_type: str | None = None
    """Exchange type ("direct", "fanout", "topic", "headers"). Defaults to "direct" if omitted.
    - Ignored when publishing directly to a queue.
    """

    routing_key: str | None = None
    """Routing key for publishing.
    - For direct-to-queue publishing, defaults to the queue name if not provided.
    - Otherwise defaults to an empty string.
    """

    queue: str | None = None
    """Queue name.
    - Required for consumers (subscribers).
    - For publishers, required if `exchange` is None (i.e., for direct-to-queue publishing).
    """

    # Use an integer for TTL (in milliseconds)
    queue_ttl: int | None = None
    """
    Consumers (Subscribers) only:
    - Message TTL in milliseconds (e.g. 60000).
    - If omitted, no TTL is set.
    """

    max_retries: int | None = 5
    """Maximum number of times a message is retried (based on x-death).
    - Defaults to 5.
    """

    dead_letter_exchange: str | None = None
    """Dead-letter exchange name."""

    dead_letter_routing_key: str | None = None
    """Routing key for dead-lettering. Defaults to an empty string.
    """

    headers: dict | None = None
    """
    For headers exchanges:
    - Attached to the message when publishing and used as binding arguments when consuming (subscribing).
    """

    verify_delivery: bool = True
    """
    If True, sets the broker's `mandatory` flag during publishing.
    - In principle, unroutable messages would be returned by the broker.
    - However, the current code does NOT attach a return-listener callback, so it may
      not fully handle the “unroutable” scenario. General publish failures are retried.
    """

    prefetch_count: int | None = None
    """Consumers (Subscribers) only:
    - Configures channel prefetch (QoS) if set.
    """

    @property
    def user_name(self) -> str:
        """Returns the user name extracted from conn_str."""
        from urllib.parse import urlparse

        parsed = urlparse(self.conn_str)
        return parsed.username or ""

    @property
    def password(self) -> str:
        """Returns the password extracted from conn_str."""
        from urllib.parse import urlparse

        parsed = urlparse(self.conn_str)
        return parsed.password or ""

    @property
    def host(self) -> str:
        """Returns the host extracted from conn_str."""
        from urllib.parse import urlparse

        parsed = urlparse(self.conn_str)
        return parsed.hostname or ""

    @property
    def vhost(self) -> str:
        """
        Returns the virtual host (vhost) extracted from conn_str.
        The vhost is taken from the path component (excluding the leading '/').
        """
        from urllib.parse import urlparse

        parsed = urlparse(self.conn_str)
        # If the path is "/" or empty, return empty string
        return parsed.path[1:] if parsed.path and len(parsed.path) > 1 else ""


class Notification(BaseModel):
    """
    Represents a notification to be sent via the Practicus AI SDK.
    """

    recipients: list[str] | str | None = None
    """
    List of recipient email addresses. Can be a single string or a list of strings.
    If none, sends notification to requester.
    """

    title: str | None = None
    """Title of the notification."""

    body: str | None = None
    """Main content of the notification (HTML or plain text)."""

    preheader: str | None = None
    """
    Preview text for email clients. Defaults to the first 100 characters of the body if not provided.
    """

    level: str | None = None
    """Log level. Options: "debug", "info", "warning", "error"."""

    category: str | None = None
    """Category of the notification."""

    urgency: str | None = None
    """Urgency level. Options: "low", "normal", "high", "critical"."""

    send_plain_text: bool | None = None
    """Whether to send the notification as plain text."""

    ignore_template: bool | None = None
    """
    If True, indicates that the body contains the complete HTML and no further templating is applied.
    """

    additional_params: dict | None = None
    """Additional custom parameters for the notification."""


class PrtLangMessage(BaseModel):
    content: str
    """The text message content to send to language model."""
    role: str | None = None
    """Role can be human, system etc. Leave None for human."""


class PrtLangRequest(BaseModel):
    messages: list[PrtLangMessage]
    """List of messages to send to the language model."""
    lang_model: str | None = None
    """Model to use as defined by the model endpoint E.g. llama-3-70b-v2"""
    streaming: bool = False
    """If model should stream results. Note: model developer must enable this"""
    temperature: float = 0.5
    """Controls randomness in generating"""
    max_tokens: int = 4094
    """Limit the length of generated text output"""
    lang_model_kwargs: dict = {}
    """Keyword arguments to pass to the model. Some are: http_proxy, https_proxy. Can be custom."""


class PrtLangResponse(BaseModel):
    content: str
    """The text response from language model."""
    lang_model: str | None = None
    """If the request does not define a model to use, model developer can choose a default model. E.g. llama-3-70b-v2"""
    input_tokens: int = 0
    """Input tokens consumed by the language model."""
    output_tokens: int = 0
    """Output tokens consumed by the language model."""
    total_tokens: int = 0
    """Total tokens consumed by the language model."""
    additional_kwargs: dict = {}
    """Additional metadata that the language model orAPI developer needs to return."""


class PrtEmbeddingsRequest(BaseModel):
    input: str | list[str]
    """Input text to embed, encoded as a string or array of strings. Please verify token size requirements. 
    E.g. for OpenAI each input must not exceed 8192 tokens."""
    model: str | None = None
    """Optional. ID of the model to use. You can ignore and use a single model while serving."""
    user: str | None = None
    """Optional. A unique identifier representing your end-user, which can help to monitor and detect abuse."""


class PrtEmbeddingObject(BaseModel):
    object: str = "embedding"
    """The object type, which is always 'embedding'."""
    embedding: list[float]
    """The embedding vector, which is a list of floats."""
    index: int
    """The index of the embedding in the list of embeddings."""


class PrtEmbeddingUsage(BaseModel):
    prompt_tokens: int
    """The number of tokens used by the prompt."""
    total_tokens: int
    """The total number of tokens used by the request."""


class PrtEmbeddingsResponse(BaseModel):
    object: str = "list"
    """The object type, which is always 'list'."""
    data: list[PrtEmbeddingObject]
    """The list of embeddings generated by the model."""
    model: str = "default"
    """The model used for embedding."""
    usage: PrtEmbeddingUsage
    """Usage statistics for the request."""


class ChatMessage(BaseModel):
    """
    Represents one message in a conversation.
    role must be one of: "system", "user", or "assistant".
    """

    role: Literal["system", "user", "assistant"] = "user"
    content: str
    name: str | None = None


class ChatCompletionRequest(BaseModel):
    """
    Pydantic model that reflects the structure of OpenAI's ChatCompletion request.
    """

    model: str = "gpt-3.5-turbo"
    messages: list[ChatMessage]
    temperature: float | None = None
    top_p: float | None = None
    n: int | None = None
    stream: bool | None = None
    stop: str | list[str] | None = None
    max_tokens: int | None = None
    presence_penalty: float | None = None
    frequency_penalty: float | None = None
    logit_bias: dict[str, float] | None = None
    user: str | None = None


class ChatCompletionResponseUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatCompletionResponseChoiceMessage(BaseModel):
    """
    For the response, OpenAI typically returns role="assistant".
    But we'll allow "system" or "assistant" to align with the known schema.
    """

    role: Literal["system", "assistant"] = "assistant"
    content: str


class ChatCompletionResponseChoice(BaseModel):
    index: int = 0
    message: ChatCompletionResponseChoiceMessage
    finish_reason: str | None = "stop"


class ChatCompletionResponse(BaseModel):
    """
    Pydantic model that reflects the structure of OpenAI's ChatCompletion response.
    Default values let you create a minimal test object.
    """

    id: str = "chatcmpl-0000"
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time()))
    model: str = "gpt-3.5-turbo"
    usage: ChatCompletionResponseUsage = Field(default=ChatCompletionResponseUsage())
    choices: list[ChatCompletionResponseChoice]


class APIExecutionTarget(str, Enum):
    """Defines where the primary work initiated by the API call to the Practicus AI App is performed."""

    DirectExecution = "DirectExecution"
    """Executes standard application logic directly, without involving AI agents, humans, or external automation."""

    AIAgent = "AIAgent"
    """Execution delegated to a specialized AI agent."""

    HumanWorker = "HumanWorker"
    """Execution delegated to a human worker (Human-in-the-Loop)."""

    RPABot = "RPABot"
    """Execution delegated to a Robotic Process Automation bot."""

    RemoteService = "RemoteService"
    """Execution involves calling another distinct internal or external service/API."""

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


# Explicitly re-assigning __doc__ since triple string docs for Enums are not automatically attached
APIExecutionTarget.DirectExecution.__doc__ = (
    "Executes standard application logic directly, without involving AI agents, humans, or external automation."
)
APIExecutionTarget.AIAgent.__doc__ = "Execution delegated to a specialized AI agent."
APIExecutionTarget.HumanWorker.__doc__ = "Execution delegated to a human worker (Human-in-the-Loop)."
APIExecutionTarget.RPABot.__doc__ = "Execution delegated to a Robotic Process Automation bot."
APIExecutionTarget.RemoteService.__doc__ = (
    "Execution involves calling another distinct internal or external service/API."
)


class APIScope(str, Enum):
    """Defines the access scope of the Practicus AI App API endpoint."""

    AppOnly = "AppOnly"
    """Accesses resources limited to this Practicus AI App."""

    TeamWide = "TeamWide"
    """Accesses resources across systems managed by this app's development team."""

    CompanyWide = "CompanyWide"
    """Accesses internal resources across different teams and systems within the company."""

    PartnerExternal = "PartnerExternal"
    """Accesses resources hosted externally by verified third-party partners."""

    Public = "Public"
    """Accesses resources publicly available on the internet."""

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


# Explicitly re-assigning __doc__ since triple string docs for Enums are not automatically attached
APIScope.AppOnly.__doc__ = "Accesses resources limited to this Practicus AI App."
APIScope.TeamWide.__doc__ = "Accesses resources across systems managed by this app's development team."
APIScope.CompanyWide.__doc__ = "Accesses internal resources across different teams and systems within the company."
APIScope.PartnerExternal.__doc__ = "Accesses resources hosted externally by verified third-party partners."
APIScope.Public.__doc__ = "Accesses resources publicly available on the internet."


class APIRiskProfile(str, Enum):
    """Represents the assessed potential risk associated with the Practicus AI App API endpoint."""

    Low = "Low"
    """Low risk if misused or if it fails. Minimal to no compliance, security, financial, or legal concerns."""

    Medium = "Medium"
    """Moderate risk if misused or if it fails. Potential compliance, security, financial, or legal concerns."""

    High = "High"
    """High risk if misused or if it fails. Significant compliance, security, financial, or legal concerns."""

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


# Explicitly re-assigning __doc__ since triple string docs for Enums are not automatically attached
APIRiskProfile.Low.__doc__ = (
    "Low risk if misused or if it fails. Minimal to no compliance, security, financial, or legal concerns."
)
APIRiskProfile.Medium.__doc__ = (
    "Moderate risk if misused or if it fails. Potential compliance, security, financial, or legal concerns."
)
APIRiskProfile.High.__doc__ = (
    "High risk if misused or if it fails. Significant compliance, security, financial, or legal concerns."
)


class APISpec(BaseModel):
    """
    Defines the characteristics and behavior of a Practicus AI App API endpoint,
    focusing on its execution pattern, operational properties, and context.
    """

    execution_target: APIExecutionTarget | None = None
    """Specifies where the primary work initiated by the API call is performed."""

    read_only: bool | None = None
    """Indicates if the endpoint only reads data (True, Informational) or if it modifies data/state (False, Operational)."""

    interactive: bool | None = None
    """Defines if API endpoint is automatically discovered byt interactive AI Assistants through protocols such as MCP."""

    scope: APIScope | None = None
    """Defines the intended audience or network reach of the API endpoint."""

    risk_profile: APIRiskProfile | None = None
    """Assesses the potential risk associated with the API endpoint's usage or failure."""

    human_gated: bool | None = None
    """Indicates if an otherwise operational task will go through human review or approval before final execution."""

    deterministic: bool | None = None
    """Indicates if the endpoint's logic is Deterministic (consistent output for identical inputs), or Non-deterministic (output may vary even for identical inputs)."""

    idempotent: bool | None = None
    """Indicates if calling the endpoint multiple times with the same input has the same net effect as calling it once. Only relevant for non-read-only endpoints."""

    stateful: bool | None = None
    """Indicates if the endpoint maintains state across multiple calls from the same client (True) or if each call is independent (False)."""

    asynchronous: bool | None = None
    """Indicates if the endpoint completes its work immediately and returns the result (False, Sync) or if it acknowledges the request and completes the work later (True, Async)."""

    maturity_level: int | None = None
    """Represents the intrinsic stability and readiness of the API. Default Categories are:
    1: POC, 2: Experimental, 3: Beta, 4: Stable, 5: Critical/Foundational.
    """

    disable_authentication: bool | None = None
    """(Use with Caution) If True, disables standard API authentication, making the endpoint publicly accessible or accessible without tokens. Defaults to False (authentication enabled) if None."""

    sensitive_data: bool | None = None
    """Defines if the API endpoint can return sensitive data such as PII."""

    custom_attributes: dict[str, str | int | float | bool] | None = None
    """Allows defining arbitrary key-value pairs for custom attributes, tagging, or extensions specific to this endpoint.

    Provide a dictionary where keys are strings (e.g., 'my-tag') and values should be JSON-serializable 
    (e.g., string, number, boolean). These pairs are exposed as OpenAPI specification 
    extensions, automatically prefixed with 'x-prt-'. 

    Example: 
      Input:  {'my-tag': 'tag-value', 'experimental': True}
      OpenAPI Output: 'x-prt-my-tag': 'tag-value', 'x-prt-experimental': True

    This metadata is also typically displayed in generated API documentation views like ReDoc.
    """

    @field_validator("custom_attributes")
    def validate_custom_attributes(cls, value: dict[str, Any] | None) -> dict[str, Any] | None:
        if value:
            for custom_attr_key in value:
                custom_attr_key = str(custom_attr_key)
                if custom_attr_key.startswith("x-prt"):
                    raise ValueError(
                        f"Custom Attribute key '{custom_attr_key}' starts with 'x-prt'. "
                        f"The prefix 'x-prt-' is automatically added in run-time, "
                        f"so please remove yours to prevent 'x-prt-x-prt-..'"
                    )

        return value

    model_config = ConfigDict(validate_assignment=True)


class GatewayModel(BaseModel):
    """
    Configuration for a single model endpoint within the gateway. Each model can
    represent a concrete LLM endpoint or a virtual router that delegates to other models.
    """

    name: str
    """The user-facing name for the model (e.g., 'practicus/medium'). This is the name users will specify in their API calls."""

    model: str | None = None
    """The actual model identifier for LiteLLM (e.g., 'openai/gpt-4o', 'hosted_vllm/my-deployment'). This should be set for concrete models."""

    api_key: str | None = None
    """
    Static API Key for the model. You can use `api_key_os_env` to get the token from an OS environment variable.
    For Practicus AI hosted models, you can leave api_key blank if there is an active user (see below), and a dynamic session token is generated with the active user credentials.
    Note: for dynamic tokens to work, an admin must first enable `user impersonation` for a Practicus AI modelhost deployment, so that a user account is appointed as the `active user`.
    """

    api_key_os_env: str | None = None
    """The OS environment variable from which to read the API Key (e.g., 'OPENAI_API_KEY')."""

    api_base: str | None = None
    """The API base to use for OpenAI compatible LLM servers such as Practicus AI LLM hosting (with or without vLLM)"""

    pre_guards: list[Callable[..., Coroutine[Any, Any, dict[str, Any]]] | str] | None = None
    """
    A list of async functions (or their name) to use as the pre guard. 
    The async functions can inspect or modify the request payload
    before it is sent to the LLM. It must return the (potentially modified) data dictionary.
    """

    post_guards: list[Callable[..., Coroutine[Any, Any, Any]] | str] | None = None
    """
    A list of async functions (or their name) to use as the post guard. 
    The async functions can inspect or modify the response object
    before it is sent to the client. To make changes, it must not return the response, but modify it directly.
    """

    pre_call: Callable[..., Coroutine[Any, Any, dict[str, Any]]] | str | None = None
    """
    A general-purpose async function (or its name) to run before the LLM call, after any routing has occurred.
    """

    post_call_success: Callable[..., Coroutine[Any, Any, None]] | str | None = None
    """An async function (or its name) to run after a successful LLM call, for additional logging, metrics, or other side effects."""

    post_call_failure: Callable[..., Coroutine[Any, Any, None]] | str | None = None
    """An async function (or its name) to run after a failed LLM call, for additional error logging and cleanup."""

    router: Callable[..., Coroutine[Any, Any, Union["GatewayModel", str]]] | str | None = None
    """A dynamic routing function (or its name) that determines the actual model to use at runtime. If this is set, 'model' should be None."""

    max_tokens: int | None = None
    """Maximum total number of tokens (input + output) allowed for a single request. If not set, defaults to the engine’s maximum."""

    max_input_tokens: int | None = None
    """Maximum number of input tokens accepted for a request. If not set, uses the model’s default or unlimited."""

    max_output_tokens: int | None = None
    """Maximum number of output tokens that can be generated in a single response. If not set, uses the model’s default."""

    input_cost_per_token: float | None = None
    """Cost per input token, typically in USD but can be other currency or a virtual credit. Used for tracking and estimating prompt costs. Leave unset to ignore."""

    output_cost_per_token: float | None = None
    """Cost per output token, typically in USD but can be other currency or a virtual credit. Used for tracking and estimating completion costs. Leave unset to ignore."""

    mode: Literal["embedding", "chat", "completion"] | None = None
    """
    Type of model operation. 
        - "embedding": For embedding/vectorization requests.
        - "chat": For conversational models supporting multi-turn input.
        - "completion": For standard prompt-to-text completion. 
    If not set, defaults to the model’s primary mode.
    """

    @field_serializer("pre_call", "post_call_success", "post_call_failure", "router")
    def serialize_callable(self, value: Callable[..., Any] | str | None) -> str | None:
        """Serializes a callable to its name for YAML/JSON output."""
        if callable(value):
            return value.__name__
        return value

    @field_serializer("pre_guards", "post_guards")
    def serialize_callable_list(
        self, value: list[Callable[..., Coroutine[Any, Any, Any]] | str] | None
    ) -> list[str] | None:
        """Serializes a callables list to its name for YAML/JSON output."""
        if not value:
            return None
        final_list: list[str] = []
        for item in value:
            if callable(item):
                final_list.append(item.__name__)
            else:
                final_list.append(item)
        return final_list

    @model_validator(mode="after")
    def validate_model(self) -> "GatewayModel":
        """Validate model."""
        if self.model and self.router:
            raise ValueError(
                f"Model '{self.name}' cannot have both a 'model' and a 'router' defined. A router model is virtual and must delegate to a concrete model."
            )
        if not self.model and not self.router:
            raise ValueError(f"Model '{self.name}' must have either a 'model' or a 'router' defined.")
        return self


class GatewayGuardrail(BaseModel):
    """
    Defines guardrail hooks at the Gateway level, applying to all models.
    To apply a guardrail to a model only, you can add the guard method directly to the GatewayModel configuration.
    """

    name: str
    """
    The name of the guardrail. If the guardrail is not default_on, clients must request to use the guardrail(s) 
    with their names by adding to the chat completion `extra_body.guardrails` list. E.g.

    ```python
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "What year was Alice born?"}],
            extra_body={
                "guardrails": ["my-pre-guard", "my-post-guard"],
            },
        )
    ```
    """

    mode: Literal["pre_call", "post_call"]
    """Whether to call the guard method before or after LLM executes."""

    guard: Callable[..., Coroutine[Any, Any, Any]] | str
    """
    An async function (or its name) to use as the guard. 

    If mode is 'pre_call', the async function can inspect or modify the request payload
    before it is sent to the LLM. It must return the (potentially modified) data dictionary.
    
    If mode is 'post_call', the async function can inspect or modify the response object
    before it is sent to the client. To make changes, it must not return the response, but modify it directly.
    """

    default_on: bool = False
    """
    Whether the guard is active by default, for ALL MODELS. Use with caution. 
    If a guardrail needs to always run for a particular model only (but not all models) 
    you can apply the guardrail directly to the GatewayModel.pre_guards/post_guards fields.
    """

    @field_serializer("guard")
    def serialize_callable(self, value: Callable[..., Any] | str | None) -> str | None:
        """Serializes a callable to its name for YAML/JSON output."""
        if callable(value):
            return value.__name__
        return value


class GatewayConfig(BaseModel):
    """
    The main configuration schema for the LLM Gateway, acting as the root object.
    """

    models: list[GatewayModel] | None = None
    """A list of all model configurations available in the gateway."""

    guardrails: list[GatewayGuardrail] | None = None
    """
    A list of guardrail configurations to make available to the entire gateway, and all models.
    If a guardrail is default_on (use with caution), it wil lbe enforced to all models.
    If a guardrail is not default_on, clients must request to use them in each chat call. 
    See guardrail documentation to learn more.
    """

    custom_conf: str | None = None
    """A path to a custom LiteLLM YAML file or a raw YAML string to use as a base configuration."""

    database_url: str | None = None
    """
    Enables logging usage, spend and similar information to a PostgreSQL database. 
    Use a connection string in the following format: 
    postgresql://user:password@db_address:db_port/db_name
    IMPORTANT: The database must be migrated before first use by setting `USE_PRISMA_MIGRATE=True` OS Env variable
    on a modelhost deployment. You can use Practicus AI management console, modelhost deployment, Extra configuration section.
    """

    module: str | None = None
    """The absolute file path to the Python module containing user-defined hook functions (e.g., '/app/src/my_hooks.py')."""

    strict: bool = False
    """
    If strict=False (default), gateway configuration errors do not stop the chat flow. 
    For uses cases with strict regulatory requirements, please make strict=True.
    """

    @model_validator(mode="after")
    def validate_model(self) -> "GatewayConfig":
        """Validate model."""
        if not self.models and not self.guardrails and not self.custom_conf:
            raise ValueError(
                "GatewayConfig does not define models, guardrails or a custom_conf, and therefore is useless."
            )
        return self


class SQLTable(BaseModel):
    """Represents metadata for a database table, including its columns."""

    name: str
    """The name of the table found in the SQL query."""
    columns: list[str]
    """A list of column names accessed or referenced within this table in the SQL query."""


class SQLMeta(BaseModel):
    """Represents the parsed metadata of a SQL query."""

    limit: int | None = None
    """The LIMIT clause value from the SQL query, if present."""
    tables: list[SQLTable]
    """A list of tables and their accessed columns found within the SQL query."""


class TableColumnMeta(BaseModel):
    """Represents a table column from a metadata service such as Open Metadata, with only essentials."""

    name: str
    """The name of the column."""
    tags: list[str] = []
    """A list of fully qualified names (FQN's) of the tags applied to the column."""

    @field_validator("tags", mode="before")
    @classmethod
    def extract_tag_fqns(cls, v):
        """
        Normalizes the tags field by extracting the `tagFQN` value from each tag object.

        Args:
            v: The raw value provided for `tags`. It is expected to be a list of dicts.

        Returns:
            A list of tag FQN strings. Returns an empty list if the input is invalid.
        """
        if not isinstance(v, list):
            return []
        return [tag.get("tagFQN") for tag in v if tag.get("tagFQN")]

    def is_pii_sensitive(self) -> bool:
        """
        Returns True if the column is marked as PII-sensitive.

        A column is considered PII-sensitive if it contains the tag "PII.Sensitive".
        """
        return "PII.Sensitive" in self.tags


class TableMeta(BaseModel):
    """Represents a table from a metadata service such as Open Metadata, with only essentials."""

    name: str
    """The name of the table."""
    fully_qualified_name: str = Field(..., alias="fullyQualifiedName")
    """The unique fully qualified name (FQN) of the table, including its database, schema, etc."""
    columns: list[TableColumnMeta]
    """A list of the table's columns, each represented by TableColumnMeta."""
    tags: list[str] = []
    """A list of fully qualified names (FQN's) of the tags applied to the table."""
    tier: int | None = None
    """The importance tier of the table, usually from 1 to 5 where 1 is more critical."""
    certification: str | None = None
    """The certification status or level of the table such as Bronze, Silver, Gold, if any."""

    def has_pii(self) -> bool:
        """
        Returns True if the table or any of its columns is tagged as PII (Personally Identifiable Information).
        """
        if "PII.Sensitive" in self.tags:
            return True
        return any(col.is_pii_sensitive() for col in self.columns)

    def get_pii_columns(self) -> list[str]:
        """
        Returns the names of all columns in the table that are tagged as PII.
        """
        return [col.name for col in self.columns if col.is_pii_sensitive()]

    def find_pii_columns(self, columns: list[str]) -> list[str]:
        """
        Filters the input list of column names to return only those that are PII-tagged.

        Args:
            columns: A list of column names to check.

        Returns:
            A list of column names from the input that are marked as PII.
        """
        result: list[str] = []
        pii_columns = self.get_pii_columns()
        for column in columns:
            if column in pii_columns:
                result.append(column)
        return result

    def get_columns_with_tag(self, tag: str) -> list[str]:
        """
        Returns the names of all columns that have the given tag.

        Args:
            tag: The fully qualified name of the tag to match.

        Returns:
            A list of column names with the specified tag.
        """
        return [col.name for col in self.columns if tag in col.tags]

    def find_columns_with_tag(self, columns: list[str], tag: str) -> list[str]:
        """
        Filters the input list of column names to return only those that have the specified tag.

        Args:
            columns: A list of column names to filter.
            tag: The tag to search for.

        Returns:
            A list of column names from the input that have the given tag.
        """
        result: list[str] = []
        columns_with_tag = self.get_columns_with_tag(tag)
        for column in columns:
            if column in columns_with_tag:
                result.append(column)
        return result

    @field_validator("certification", mode="before")
    @classmethod
    def extract_certification(cls, v: Any) -> str | None:
        if v and isinstance(v, dict) and "tagLabel" in v:
            tag_fqn = v["tagLabel"].get("tagFQN", "")  # type: ignore
            # Parse "Certification.Silver" into "Silver"
            if "." in tag_fqn:
                return tag_fqn.split(".")[-1]  # type: ignore
            return tag_fqn  # type: ignore
        return None

    @model_validator(mode="before")
    @classmethod
    def preprocess_data(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # 1. Process 'tags' first (extract tagFQN)
            raw_tags = data.get("tags")  # type: ignore
            processed_tags: list[str] = []
            if isinstance(raw_tags, list):
                for tag_item in raw_tags:  # type: ignore
                    # Assuming tag_item can be a dict with 'tagFQN' or a string directly
                    if isinstance(tag_item, dict) and "tagFQN" in tag_item and tag_item["tagFQN"]:
                        processed_tags.append(tag_item["tagFQN"])  # type: ignore
            data["tags"] = processed_tags  # Update the data dictionary with processed tags

            # 2. Process 'tier' based on the now-processed 'tags'
            current_tier = data.get("tier")  # type: ignore
            if current_tier is None:  # Only attempt to extract if tier is not explicitly provided
                for tag_fqn in processed_tags:  # Use the already processed tags
                    if tag_fqn.startswith("Tier.Tier"):
                        try:
                            tier_value = int(tag_fqn.replace("Tier.Tier", ""))
                            data["tier"] = tier_value
                            break  # Found the tier, no need to check further
                        except (ValueError, IndexError):
                            continue  # Ignore malformed tier tags
        return data


class UserMeta(BaseModel):
    """Represents a user from a metadata service such as Open Metadata, with only essentials."""

    name: str
    """The unique name of the user."""
    email: str
    """The email address of the user."""
    teams: list[str] = []
    """A list of fully qualified names (FQN's) of the teams the user belongs to."""
    roles: list[str] = []
    """A list of fully qualified names (FQN's) of the roles assigned to the user."""
    personas: list[str] = []
    """A list of fully qualified names (FQN's) of the personas associated with the user."""
    defaultPersona: str | None = None
    """The fully qualified name (FQN) of the user's default persona, if set."""
    domains: list[str] = []
    """A list of fully qualified names (FQN's) of the domains the user is associated with."""

    @field_validator("teams", "personas", "defaultPersona", "domains", mode="before")
    @classmethod
    def extract_fqns_from_entities(cls, v, info: Any):
        # This validator correctly handles combining roles and parsing all entity lists.
        if info.field_name == "defaultPersona":
            return v.get("fullyQualifiedName")
        else:
            # For 'teams', 'personas', 'domains', v is the raw list from JSON
            entity_list = v

        if not isinstance(entity_list, list):
            return []
        return [ref.get("fullyQualifiedName") for ref in entity_list if ref.get("fullyQualifiedName")]

    @model_validator(mode="before")
    @classmethod
    def preprocess_data(cls, data: Any) -> Any:
        if isinstance(data, dict):
            roles: list[str] = []
            direct_roles = data.get("roles")
            if direct_roles:
                roles = [ref.get("fullyQualifiedName") for ref in direct_roles if ref.get("fullyQualifiedName")]
            inherited_roles = data.get("inheritedRoles")
            if inherited_roles:
                roles += [ref.get("fullyQualifiedName") for ref in inherited_roles if ref.get("fullyQualifiedName")]

            data["roles"] = roles

        return data


class TrinoPolicyTable(BaseModel):
    """Represents a table resource with optional column information."""

    model_config = ConfigDict(extra="allow")

    catalogName: str
    """The name of the catalog containing the table."""
    schemaName: str
    """The name of the schema containing the table."""
    tableName: str
    """The name of the table."""
    columns: list[str] | None = None
    """An optional list of column names involved in the operation."""

    @computed_field
    @property
    def full_name(self) -> str:
        """Alias that returns catalogName.schemaName.tableName"""
        return f"{self.catalogName}.{self.schemaName}.{self.tableName}"

    def __str__(self) -> str:
        return self.full_name


class TrinoPolicyColumn(BaseModel):
    """Represents a fully-qualified column, used for column-level security."""

    model_config = ConfigDict(extra="allow")

    # This field will be populated by the validator in the parent 'Action' class.
    index: int | None = None
    """Only used for column masking requests. The zero-based index of this item from the original request list."""
    catalogName: str
    """The name of the catalog containing the column."""
    schemaName: str
    """The name of the schema containing the column."""
    tableName: str
    """The name of the table containing the column."""
    columnName: str
    """The name of the column."""
    columnType: str
    """The Trino data type of the column (e.g., 'bigint', 'varchar(100)')."""

    @computed_field
    @property
    def table_full_name(self) -> str:
        """Alias that returns catalogName.schemaName.tableName"""
        return f"{self.catalogName}.{self.schemaName}.{self.tableName}"

    def __str__(self) -> str:
        return f"{self.catalogName}.{self.schemaName}.{self.tableName}.{self.columnName}"


class TrinoPolicyResource(BaseModel):
    """A container for a single resource."""

    model_config = ConfigDict(extra="allow")

    table: TrinoPolicyTable | None = None
    """A table resource, present for table-level operations."""
    user: dict[str, Any] | None = None
    catalog: dict[str, Any] | None = None


class TrinoPolicyFilterResource(BaseModel):
    """An item within the 'filterResources' list for batch operations."""

    model_config = ConfigDict(extra="allow")

    column: TrinoPolicyColumn | None = None
    """A column resource, present for column-masking operations."""


class TrinoPolicyIdentity(BaseModel):
    """Represents the identity of the user performing the action."""

    model_config = ConfigDict(extra="allow")

    user: str
    """The username of the authenticated user."""
    groups: list[str] = []
    """A list of groups the user belongs to. Note: this is usually an empty list and groups are fetched from another metadata system."""


class TrinoPolicyContext(BaseModel):
    """The context in which the action is being performed."""

    model_config = ConfigDict(extra="allow")

    identity: TrinoPolicyIdentity
    """The identity of the user and their groups."""


class TrinoPolicyAction(BaseModel):
    """Represents the action being performed."""

    model_config = ConfigDict(extra="allow")

    operation: str
    resource: TrinoPolicyResource | None = None
    filterResources: list[TrinoPolicyFilterResource] | None = None

    @model_validator(mode="after")
    def set_filter_resource_indices(self) -> "TrinoPolicyAction":
        """
        A post-validation hook that injects the list index into each
        item in 'filterResources'.
        """
        if self.filterResources:
            for i, item in enumerate(self.filterResources):
                # Pydantic allows mutable assignment within a validator.
                assert item.column, f"Filter resource column field is None for item indexed at {i}"
                item.column.index = i
        return self


class TrinoPolicyRequest(BaseModel):
    """The core authorization request from Trino."""

    model_config = ConfigDict(extra="allow")

    context: TrinoPolicyContext
    """Identity and session metadata (user, impersonation, etc.)."""
    action: TrinoPolicyAction
    """The requested action, such as selecting, masking, or filtering data."""

    @computed_field
    @property
    def user(self) -> str:
        """The user that is making the request. If impersonation is active, this will be the impersonated end user."""
        return self.context.identity.user

    @computed_field
    @property
    def operation(self) -> str:
        """The type of operation being evaluated (e.g. SelectFromColumns, GetRowFilters)."""
        return self.action.operation

    def get_table_to_select(self) -> TrinoPolicyTable:
        """Returns the table being selected from (used for 'SelectFromColumns' only)."""
        if self.action.operation != "SelectFromColumns":
            raise ValueError(
                f"Cannot get table to select since trino policy request operation is '{self.action.operation}' "
                "instead of 'SelectFromColumns'. Please make sure you are calling get_table_to_select() inside a Trino validate handler."
            )
        assert self.action.resource, "Resource for 'GetRowFilters' is None"
        assert self.action.resource.table, "Resource table for 'GetRowFilters' is None"
        return self.action.resource.table

    def get_table_to_filter(self) -> TrinoPolicyTable:
        """Returns the table being filtered (used for 'GetRowFilters' only)."""
        if self.action.operation != "GetRowFilters":
            raise ValueError(
                f"Cannot get table to filter since trino policy request operation is '{self.action.operation}' "
                "instead of 'GetRowFilters'. Please make sure you are calling get_table_to_filter() inside a Trino row filter handler."
            )
        assert self.action.resource, "Resource for 'GetRowFilters' is None"
        assert self.action.resource.table, "Resource table for 'GetRowFilters' is None"
        return self.action.resource.table

    def get_columns_to_mask(self) -> list[TrinoPolicyColumn]:
        """Returns the list of columns to be masked (used for 'GetColumnMask' only)."""
        if self.action.operation != "GetColumnMask":
            raise ValueError(
                f"Cannot get columns to mask since trino policy request operation is '{self.action.operation}' "
                "instead of 'GetColumnMask'. Please make sure you are calling get_columns_to_mask() inside a Trino column masking handler."
            )
        assert self.action.filterResources, "filterResources for 'GetColumnMask' is None"
        columns: list[TrinoPolicyColumn] = []
        for resource in self.action.filterResources:
            assert resource.column, "Column inside filterResources for 'GetColumnMask' is None"
            columns.append(resource.column)

        return columns

    @model_validator(mode="before")
    @classmethod
    def unwrap_input_layer(cls, data: Any) -> Any:
        """
        Intercepts the raw data before validation to unwrap the 'input' key.
        """
        if isinstance(data, dict) and "input" in data:
            return data["input"]  # type: ignore
        return data  # type: ignore


class TrinoColumnMaskRule(BaseModel):
    """
    A single column mask rule to be applied in Trino query responses.

    This rule defines how a specific column's value should be masked (e.g., redacted or obfuscated)
    when a user does not have full access permissions. It supports both static and dynamic expressions.

    The masking behavior is defined using Trino SQL expressions, which may require explicit casting
    depending on the target column type (e.g., `CAST('****-1234' AS VARCHAR(9))`).

    Used as part of Practicus AI SDK's Trino integration for column-level security.
    """

    column: TrinoPolicyColumn = Field(exclude=True)
    """
    The target column that the masking rule applies to.

    This field is excluded from serialization as it is typically used internally
    for evaluation or lookup purposes. It contains metadata about the column such
    as its name, type, catalog, schema, and table.
    """

    expression: str = Field(exclude=True)
    """
    The Trino SQL expression to return in place of the actual column value.

    This can be a:
      - **Static replacement**: e.g., `'****'` for redaction
      - **Dynamic transformation**: e.g., `CONCAT('****-', SUBSTRING(card_number, -4))`
    
    **Important**:
    - The expression must be enclosed in single quotes when appropriate.
    - If the expression produces a shorter or differently typed value than the original column,
      it may require explicit casting to avoid Trino inferring overly broad types (e.g., 
      `CAST('****-1234' AS VARCHAR(9))` instead of returning a plain string).
    - This is critical for fields like `VARCHAR(20)` credit card numbers to prevent
      unexpected type mismatches or memory overhead from inferred `VARCHAR(2^31)` types.

    **Examples**:
    - `'****'`
    - `CAST(CONCAT('****-', SUBSTRING(card_number, -4)) AS VARCHAR(9))`
    - `'REDACTED'::VARCHAR`
    """

    @computed_field
    @property
    def index(self) -> int:
        """The zero-based index of the column from the original request list."""
        assert self.column.index, (
            f"Column index is required for a column masking response, but not set for column: {self.column}"
        )
        return self.column.index

    @computed_field
    @property
    def viewExpression(self) -> dict[str, str]:
        """Creates the nested 'viewExpression' dictionary for the JSON output."""
        return {"expression": self.expression}


class TrinoColumnMask(BaseModel):
    """The final response object for a 'GetColumnMask' operation."""

    result: list[TrinoColumnMaskRule]
    """List of column masking rules"""


class TrinoRowFilter(BaseModel):
    """
    Represents the row-level security response for a Trino 'GetRowFilters' policy operation.

    The `expressions` field contains one or more SQL-style filter expressions (as strings),
    which will be combined using logical AND (`... AND ...`) and injected directly into
    the `WHERE` clause of the final Trino query.

    This class converts those expressions into the JSON structure expected by Trino.

    Example:
        If `expressions = ["city = 'NY'", "age >= 18"]`, the resulting query will effectively become:

            SELECT * FROM some_table
            WHERE city = 'NY' AND age >= 18

    These filters are enforced transparently by Trino after policy approval and cannot be bypassed by users.
    """

    expressions: list[str] = Field(exclude=True)
    """
    A list of SQL-compatible expressions (as strings) to apply as row-level filters.
    E.g. ["city = 'NY'", "age >= 18"]

    These are inserted directly into the Trino `WHERE` clause using logical AND.
    This field is excluded from the serialized output to Trino, as only the structured result is returned.
    """

    @computed_field
    @property
    def result(self) -> list[dict[str, str]]:
        """
        Converts the raw expression strings into the Trino-compatible format:
        a list of {"expression": "<sql>"} dictionaries.

        Trino will apply all expressions using `AND` logic.
        """
        return [{"expression": expr} for expr in self.expressions]
