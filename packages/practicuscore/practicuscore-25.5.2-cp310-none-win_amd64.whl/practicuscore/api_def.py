from enum import Enum  # pylint:disable=wildcard-import,unused-wildcard-import
from typing import Optional, Any
from datetime import datetime

from pydantic import BaseModel

from practicuscore.api_base import (
    PrtBaseModel,
    PRTRequest,
    PRTResponse,
    PRTDataRequest,
    PRTEng,
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
    TrinoConnConf,
    DremioConnConf,
    HanaConnConf,
    TeradataConnConf,
    Db2ConnConf,
    DynamoDBConnConf,
    CockroachDBConnConf,
    ClouderaConnConf,
    CustomDBConnConf,
)


class CreateProcessRequest(PRTRequest):
    pass


class CreateProcessResponse(PRTResponse):
    process_id: int = -1
    os_pid: int = -1


class StartExtSvcRequest(PRTRequest):
    svc_name: str = ""
    port: int | None = None
    dark_mode: bool = True
    auto_start_after_failure: bool = False
    singleton_service_per_node: bool = True
    options: dict | None = None


class StartExtSvcResponse(PRTResponse):
    port: int = -1
    options: dict | None = None


class RestartNodeSvcRequest(PRTRequest):
    restart_reason_to_log: str | None = None


class KillProcessRequest(PRTRequest):
    process_id: int = -1
    process_uuid: str | None = None


class KillProcessesRequest(PRTRequest):
    process_id_list: list[int] | None = None


class PingRequest(PRTRequest):
    pass


class HeartBeatRequest(PRTRequest):
    payload: dict | None = None


class HeartBeatResponse(PRTResponse):
    payload: dict | None = None


class CloneLogsRequest(PRTRequest):
    pass


class LoadRequest(PRTDataRequest):
    pass
    # response is csv, no class needed


class ExportDataRequest(PRTDataRequest):
    # conn_conf in base class is a mandatory field and is the destination of save
    source_conn_conf: (
        dict
        | ConnConf
        | WorkerFileConnConf
        | SqLiteConnConf
        | S3ConnConf
        | MYSQLConnConf
        | PostgreSQLConnConf
        | RedshiftConnConf
        | SnowflakeConnConf
        | MSSQLConnConf
        | OracleConnConf
        | HiveConnConf
        | AthenaConnConf
        | TrinoConnConf
        | DremioConnConf
        | HanaConnConf
        | TeradataConnConf
        | Db2ConnConf
        | DynamoDBConnConf
        | CockroachDBConnConf
        | ClouderaConnConf
        | CustomDBConnConf
        | None
    ) = None

    step_dict_list: list[dict] | None = None
    # response is op_result


class GetDFRequest(PRTRequest):
    # You can use one of: sampling_method + sample_size_app or from_row -> to_row
    sampling_method: str | None = None
    sample_size_app: int | None = None
    from_row: int | None = None
    to_row: int | None = None


class WSStateKeys:
    DF_FULL_TYPE_NAME = "DF_FULL_TYPE_NAME"
    DF_LOADED_ROWS_COUNT = "DF_LOADED_ROWS_COUNT"


class GetWSStateRequest(PRTRequest):
    wait_for_free_sec: float = 600.0
    generic_attributes_keys: list[str] | None = None


class GetWSStateResponse(PRTResponse):
    busy: bool = False
    step_dict_list: list[dict] | None = None
    async_op_issues_json_list: list[str] | None = None
    generic_attributes_dict: dict | None = None


class RunStepsRequest(PRTRequest):
    # used to run for "Node only" steps. Using dict, since Step is not a Pydantic model
    step_dict_list: list[dict] | None = None
    reset_steps: bool = False


class GetObjectStorageMetaRequest(PRTDataRequest):
    prefix: str | None = None
    max_size: int | None = None
    starting_token: str | None = None
    element_uuid: str | None = None


class StorageMetaChildrenLoadStatus(str, Enum):
    NOT_LOADED = "NOT_LOADED"
    LOADED = "LOADED"
    WONT_LOAD = "WONT_LOAD"


class ObjectStorageMeta(PrtBaseModel):
    key: str | None = None
    name: str | None = None
    prefix: str | None = None
    is_folder: bool | None = None
    size: int | None = None
    last_modified: datetime | None = None
    level: int = 0
    children: list["ObjectStorageMeta"] | None = None
    children_loaded: StorageMetaChildrenLoadStatus = StorageMetaChildrenLoadStatus.NOT_LOADED

    @property
    def is_file(self) -> bool:
        return not self.is_folder


class GetObjectStorageMetaResponse(PRTResponse):
    meta_list: list[ObjectStorageMeta] | None = None


class ConnSelectionStats(PrtBaseModel):
    # statistics about a selected key or keys
    size_per_row: int | None = None
    sample_size_in_bytes: int | None = None
    sample_rows: int | None = None
    total_size_in_bytes: int | None = None
    total_rows: int | None = None


class PreviewRequest(PRTDataRequest):
    pass


class PreviewResponse(PRTResponse):
    selection_stats: ConnSelectionStats | None = None
    csv_str: str | None = None
    preview_text: str | None = None


class TestConnectionRequest(PRTDataRequest):
    pass


class GetFileStatusRequest(PRTRequest):
    node_path_list: list[str] | None = None
    recursive: bool = False


class FileStatus(PrtBaseModel):
    file_path: str
    file_size: int
    file_epoch: float


class GetFileStatusResponse(PRTResponse):
    file_status_list: list[FileStatus] | None = None


class UploadFilesRequest(PRTRequest):
    # opens a multipart app to Worker communication channel. files/file parts are communicated chunk by chunk
    pass


class UploadFilesToCloudRequest(PRTRequest):
    conn_conf: S3ConnConf | None = None


class UploadWorkerFilesRequest(PRTRequest):
    conn_conf: S3ConnConf | None = None
    source_path_list: list[str] | None = None
    target_dir_path: str | None = None
    source_path_to_cut: str | None = None


class DownloadFilesRequest(PRTRequest):
    node_path_list: list[str] | None = None
    recursive: bool = False


class CopyFilesRequest(PRTRequest):
    source_path_list: list[str] | None = None
    target_dir_path: str | None = None
    source_path_to_cut: str | None = None


class ProfileWSRequest(PRTRequest):
    profile_uuid: str | None = None
    title: str | None = None
    compare_to_original: bool | None = None


class ProfileWSResponse(PRTResponse):
    started_profiling: bool | None = None


class ViewLogsRequest(PRTRequest):
    log_size_mb: int = 1


class ViewLogsResponse(PRTResponse):
    practicus_log: str | None = None


class TestGenericRequest(PRTRequest):
    some_str: str | None = None


class TestGenericResponse(PRTResponse):
    some_result: str | None = None


class RunScriptRequest(PRTRequest):
    script_path: str | None = None
    run_as_sudo: bool = False
    timeout_secs: int = 120
    wait_for_end: bool = True


class RunScriptResponse(PRTResponse):
    std_out: str = ""
    std_err: str = ""


class FlushLogsRequest(PRTRequest):
    pass


class XLImportRequest(PRTRequest):
    file_name: str = ""


class XLImportResponse(PRTResponse):
    dp_content: str = ""
    dp_err_warning: str = ""


class TestCodeRequest(PRTRequest):
    sampling_method: str | None = None
    sample_size: int | None = None
    code_block_encoded: str | None = None
    is_sql: bool | None = None
    sql_table_name: str | None = None
    snippet_path: str | None = None
    snippet_params: dict | None = None


class TestCodeResponse(PRTResponse):
    test_result_csv_b: str | None = None


class GenerateCodeRequest(PRTRequest):
    worksheets_dict: dict | None = None
    template: str | None = None
    app_user_name: str | None = None
    export_name: str | None = None
    dag_flow: str | None = None
    schedule_start_date_ts: float | None = None
    schedule_interval: str | None = None
    save_cloud_credentials: bool = False
    params: dict | None = None  # Worker + auth details (if requested by user)


class GenerateCodeResponse(PRTResponse):
    generated_file_paths: list[str] | None = None


class CreateFolderRequest(PRTDataRequest):
    full_path: str | None = None


class ModelAPIHeaderMeta(PrtBaseModel):
    # x-prt-... Http headers of a model api
    model_id: int | None = None
    model_version: str | None = None
    model_deployment_key: str | None = None
    pod_name: str | None = None
    model_prefix: str | None = None
    model_name: str | None = None
    traffic_weight: int | None = None
    auth_detail: str | None = None
    extra_config: str | None = None


class ModelConfig(PrtBaseModel):
    state: str | None = None
    percent_complete: int | None = None
    model_name: str | None = None
    model_desc: str | None = None
    target: str | None = None
    re_sample_size: int | None = None
    model_dir: str | None = None
    short_model_name: str | None = None
    version_name: str | None = None
    problem_type: str | None = None
    limit_to_models: str | None = None
    use_gpu: bool | None = None
    explain: bool | None = None
    sensitive_features: str | None = None
    user_name: str | None = None
    node_name: str | None = None
    node_instance_id: str | None = None
    setup_params: dict | None = None
    tune_params: dict | None = None
    model_signature_json: str | None = None
    # Feature selection
    feature_selection_percent: int | None = None
    features_ignored: list[str] | None = None
    # Time Series
    time_feature: str | None = None
    time_frequency: str | None = None
    # Clustering
    num_clusters: int | None = None
    # Engines etc. versions
    py_version: str | None = None
    auto_ml_engine: str | None = None
    auto_ml_version: str | None = None
    # Experiment logging
    log_exp_name: str | None = None
    log_experiment_service_key: str | None = None
    log_experiment_service_name: str | None = None
    log_exp_id: str | None = None
    log_exp_full_parent_run_id: str | None = None
    log_exp_full_final_run_id: str | None = None
    final_model: str | None = None
    score: float | None = None
    errors: str | None = None
    summary: str | None = None

    @property
    def input_columns(self) -> list[str]:
        input_cols = []
        try:
            if self.model_signature_json is not None:
                import json

                signature_json = json.loads(self.model_signature_json)
                if "inputs" in signature_json:
                    inputs_dict_list = json.loads(signature_json["inputs"])
                    for input_dict in inputs_dict_list:
                        input_cols.append(input_dict["name"])
        except:
            from practicuscore.log_manager import get_logger, Log

            logger = get_logger(Log.CORE)
            logger.error(
                f"Unable to extract input columns from model_signature_json: {self.model_signature_json}.",
                exc_info=True,
            )
        finally:
            return input_cols

    def save(self, json_path: str):
        with open(json_path, "wt") as f:
            f.write(self.model_dump_json(exclude_none=True))

    def __str__(self):
        return self.model_dump_json(indent=4, exclude_none=True)

    @staticmethod
    def load(model_conf: str | dict) -> Optional["ModelConfig"]:
        """
        Model configuration Json or dictionary
        :param model_conf:
        :return:
        """
        if isinstance(model_conf, str):
            import json

            model_conf = json.loads(model_conf)

        if isinstance(model_conf, dict):
            return ModelConfig.model_validate(model_conf)

        return None


class CreateModelRequest(PRTRequest):
    model_conf: ModelConfig | None = None
    status_check: bool = False
    last_reported_log_byte: int = 0


class CreateModelResponse(PRTResponse):
    model_conf: ModelConfig | None = None
    current_log: str | None = None
    last_reported_log_byte: int = 0


class RegisterModelRequest(PRTRequest):
    model_dir: str | None = None


class ModelSearchResult(PrtBaseModel):
    model_name: str | None = None
    latest_v: int | None = None
    latest_v_timestamp: int | None = None
    latest_staging_v: int | None = None
    latest_staging_timestamp: int | None = None
    latest_prod_v: int | None = None
    latest_prod_timestamp: int | None = None


class ModelSearchResults(PrtBaseModel):
    results: list[ModelSearchResult] | None = None


class SearchModelsRequest(PRTRequest):
    filter_string_b64: str | None = None
    max_results: int = 100


class SearchModelsResponse(PRTResponse):
    model_search_results: ModelSearchResults | None = None


class GetModelMetaRequest(PRTRequest):
    model_uri: str | None = None
    model_json_path: str | None = None


class GetModelMetaResponse(PRTResponse):
    model_conf_json: str | None = None
    prepare_ws_b64: str | None = None


class GetSystemStatRequest(PRTRequest):
    pass


class GetSystemStatResponse(PRTResponse):
    system_stat: dict | None = None
    node_version: str | None = None


class DeleteKeysRequest(PRTDataRequest):
    keys: list[str] | None = None
    delete_sub_keys: bool = False


class ListBucketsRequest(PRTDataRequest):
    pass


class ListBucketsResponse(PRTResponse):
    buckets: list[str] | None = None


class ReplicateNodeRequest(PRTRequest):
    source_node_name: str | None = None
    source_node_dns: str | None = None
    source_node_pem_data: str | None = None
    timeout_secs: int = 30 * 60  # 30 minutes


class UploadModelFilesRequest(PRTRequest):
    model_dir: str | None = None
    region_url: str | None = None
    deployment_key: str | None = None
    token: str | None = None
    prefix: str | None = None
    model_id: int | None = None
    model_name: str | None = None
    version: str | None = None


class UploadModelFilesResponse(PRTResponse):
    model_url: str | None = None


class DeployWorkflowRequest(PRTRequest):
    workflow_service_key: str | None = None
    destination_dir_path: str | None = None
    files_dir_path: str | None = None


class CreatePlotRequest(PRTRequest):
    dark_mode: bool = False


class CreatePlotResponse(PRTResponse):
    plot_token: str | None = None


class UpdateWsNameRequest(PRTRequest):
    ws_name: str | None = None


class RunTaskRequest(PRTRequest):
    task_uuid: str | None = None
    task_file_path: str | None = None
    capture_task_output: bool = True
    python_venv_name: str | None = None


class CheckTaskStateRequest(PRTRequest):
    task_uuid: str | None = None
    log_size_mb: int = 10
    view_practicus_log: bool = False
    last_reported_log_byte: int = 0


class TaskState(str, Enum):
    UNKNOWN = "UNKNOWN"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"

    @classmethod
    def from_value(cls, value: str | Enum) -> "TaskState":
        str_val = str(value.value if hasattr(value, "value") else value).upper()
        for i, enum_val in enumerate(cls):
            # noinspection PyUnresolvedReferences
            if str(enum_val.value).upper() == str_val:
                return cls(enum_val)

        raise ValueError(f"{value} is not a valid {cls}")


class CheckTaskStateResponse(PRTResponse):
    task_state: TaskState = TaskState.UNKNOWN
    practicus_log: str | None = None
    last_reported_log_byte: int = 0


class GetActiveProcessListRequest(PRTRequest):
    # Searches for active processes (worksheets) from 1 if start_process is empty, else searches from start
    start_process: int | None = None


class GetActiveProcessListResponse(PRTResponse):
    process_list: list[int] | None = None


class AssistantCodeRequest(PRTRequest):
    assistant_config_key: str
    user_query: str
    code_language: str  # Currently python or sql
    sql_table_name: str | None = None
    model_name: str | None = None  # If None, uses default in config


class AssistantCodeResponse(PRTResponse):
    generated_code: str | None = None


class GetAssistantListRequest(PRTRequest):
    pass


class GetAssistantListResponse(PRTResponse):
    assistant_config_list: list[dict[str, Any]] | None = None


class GetAssistantModelsRequest(PRTRequest):
    assistant_name: str


class GetAssistantModelsResponse(PRTResponse):
    model_list: list[str]


class SnippetParamJS(BaseModel):
    # This class is used to convert SnippetParam to JSON
    name: str | None = None
    optional: bool | None = None
    param_type: str | None = None
    is_list: bool | None = None
    default_value: Any | None = None
    enum_values: list[dict] | None = None
    docs: str | None = None
    name_for_users: str | None = None
    is_column: bool | None = None
    actual_column_type: str | None = None
    user_friendly_column_name: str | None = None


class SnippetMetaJS(BaseModel):
    # This class is used to convert SnippetMeta to JSON
    snippet_path: str | None = None
    primary_function_name: str | None = None
    system_snippet: bool | None = None
    category: str | None = None
    short_desc: str | None = None
    long_desc: str | None = None
    params: list[SnippetParamJS] | None = None
    worker_required: bool | None = None
    supported_engines: list[PRTEng] | None = None
    has_errors: bool | None = None
    code_block: str | None = None
    file_name: str | None = None
    name_for_users: str | None = None


class ReadSnippetsRequest(PRTRequest):
    read_system_snippets: bool = True
    user_snippets_path_list: list[str] | None = None


class ReadSnippetsResponse(PRTResponse):
    snippets: list[SnippetMetaJS] | None = None
