# THIS IS A GENERATED FILE, DO NOT MODIFY MANUALLY
from typing import Callable

from .dll import lib


# hyper_error_category_t
HYPER_ERROR_CATEGORY_GENERIC: int = lib.HYPER_ERROR_CATEGORY_GENERIC
HYPER_ERROR_CATEGORY_SYSTEM: int = lib.HYPER_ERROR_CATEGORY_SYSTEM
HYPER_ERROR_CATEGORY_PROCESS_EXIT_CODE: int = lib.HYPER_ERROR_CATEGORY_PROCESS_EXIT_CODE
HYPER_ERROR_CATEGORY_SQLSTATE: int = lib.HYPER_ERROR_CATEGORY_SQLSTATE

# hyper_error_severity_t
HYPER_SEVERITY_ERROR: int = lib.HYPER_SEVERITY_ERROR
HYPER_SEVERITY_FATAL: int = lib.HYPER_SEVERITY_FATAL
HYPER_SEVERITY_PANIC: int = lib.HYPER_SEVERITY_PANIC

# hyper_error_source_t
HYPER_ERROR_SOURCE_USER: int = lib.HYPER_ERROR_SOURCE_USER
HYPER_ERROR_SOURCE_SYSTEM: int = lib.HYPER_ERROR_SOURCE_SYSTEM

# hyper_error_field_key
HYPER_ERROR_FIELD_ERROR_CATEGORY: int = lib.HYPER_ERROR_FIELD_ERROR_CATEGORY
HYPER_ERROR_FIELD_ERROR_CODE: int = lib.HYPER_ERROR_FIELD_ERROR_CODE
HYPER_ERROR_FIELD_MESSAGE: int = lib.HYPER_ERROR_FIELD_MESSAGE
HYPER_ERROR_FIELD_HINT_MESSAGE: int = lib.HYPER_ERROR_FIELD_HINT_MESSAGE
HYPER_ERROR_FIELD_SEVERITY: int = lib.HYPER_ERROR_FIELD_SEVERITY
HYPER_ERROR_FIELD_SQL_STATE: int = lib.HYPER_ERROR_FIELD_SQL_STATE
HYPER_ERROR_FIELD_CAUSE: int = lib.HYPER_ERROR_FIELD_CAUSE
HYPER_ERROR_FIELD_CONTEXT_ID: int = lib.HYPER_ERROR_FIELD_CONTEXT_ID
HYPER_ERROR_FIELD_DETAIL: int = lib.HYPER_ERROR_FIELD_DETAIL
HYPER_ERROR_FIELD_SOURCE: int = lib.HYPER_ERROR_FIELD_SOURCE
HYPER_ERROR_GRPC_STATUS: int = lib.HYPER_ERROR_GRPC_STATUS

# hyper_telemetry_t
HYPER_DISABLE_TELEMETRY: int = lib.HYPER_DISABLE_TELEMETRY
HYPER_ENABLE_TELEMETRY: int = lib.HYPER_ENABLE_TELEMETRY

# hyper_create_mode_t
HYPER_DO_NOT_CREATE: int = lib.HYPER_DO_NOT_CREATE
HYPER_CREATE: int = lib.HYPER_CREATE
HYPER_CREATE_IF_NOT_EXISTS: int = lib.HYPER_CREATE_IF_NOT_EXISTS
HYPER_CREATE_AND_REPLACE: int = lib.HYPER_CREATE_AND_REPLACE

# hyper_connection_status_t
HYPER_CONNECTION_OK: int = lib.HYPER_CONNECTION_OK
HYPER_CONNECTION_BAD: int = lib.HYPER_CONNECTION_BAD

# hyper_type_tag_t
HYPER_UNSUPPORTED: int = lib.HYPER_UNSUPPORTED
HYPER_BOOL: int = lib.HYPER_BOOL
HYPER_BIG_INT: int = lib.HYPER_BIG_INT
HYPER_SMALL_INT: int = lib.HYPER_SMALL_INT
HYPER_INT: int = lib.HYPER_INT
HYPER_NUMERIC: int = lib.HYPER_NUMERIC
HYPER_FLOAT: int = lib.HYPER_FLOAT
HYPER_DOUBLE: int = lib.HYPER_DOUBLE
HYPER_OID: int = lib.HYPER_OID
HYPER_BYTE_A: int = lib.HYPER_BYTE_A
HYPER_TEXT: int = lib.HYPER_TEXT
HYPER_VARCHAR: int = lib.HYPER_VARCHAR
HYPER_CHAR: int = lib.HYPER_CHAR
HYPER_JSON: int = lib.HYPER_JSON
HYPER_DATE: int = lib.HYPER_DATE
HYPER_INTERVAL: int = lib.HYPER_INTERVAL
HYPER_TIME: int = lib.HYPER_TIME
HYPER_TIMESTAMP: int = lib.HYPER_TIMESTAMP
HYPER_TIMESTAMP_TZ: int = lib.HYPER_TIMESTAMP_TZ
HYPER_TABGEOGRAPHY: int = lib.HYPER_TABGEOGRAPHY
# Deprecated alias for `HYPER_TABGEOGRAPHY`. Will be removed as part of W-17701666.
HYPER_GEOGRAPHY: int = lib.HYPER_GEOGRAPHY

# hyper_table_persistence_t
HYPER_PERMANENT: int = lib.HYPER_PERMANENT
HYPER_TEMPORARY: int = lib.HYPER_TEMPORARY

# hyper_rowset_result_format_t
HYPER_ROWSET_RESULT_FORMAT_TEXT: int = lib.HYPER_ROWSET_RESULT_FORMAT_TEXT
HYPER_ROWSET_RESULT_FORMAT_HYPER_BINARY: int = lib.HYPER_ROWSET_RESULT_FORMAT_HYPER_BINARY

# hyper_rowset_type_t
HYPER_ROWSET_EMPTY_QUERY: int = lib.HYPER_ROWSET_EMPTY_QUERY
HYPER_ROWSET_COMMAND: int = lib.HYPER_ROWSET_COMMAND
HYPER_ROWSET_QUERY_RESULT: int = lib.HYPER_ROWSET_QUERY_RESULT
HYPER_ROWSET_COPY_IN: int = lib.HYPER_ROWSET_COPY_IN
HYPER_ROWSET_COPY_OUT: int = lib.HYPER_ROWSET_COPY_OUT

# hyper_log_level_t
HYPER_LOG_LEVEL_TRACE: int = lib.HYPER_LOG_LEVEL_TRACE
HYPER_LOG_LEVEL_INFO: int = lib.HYPER_LOG_LEVEL_INFO
HYPER_LOG_LEVEL_WARNING: int = lib.HYPER_LOG_LEVEL_WARNING
HYPER_LOG_LEVEL_ERROR: int = lib.HYPER_LOG_LEVEL_ERROR
HYPER_LOG_LEVEL_FATAL: int = lib.HYPER_LOG_LEVEL_FATAL

# anonymous enum
HYPER_OID_BOOL: int = lib.HYPER_OID_BOOL
HYPER_OID_BIG_INT: int = lib.HYPER_OID_BIG_INT
HYPER_OID_SMALL_INT: int = lib.HYPER_OID_SMALL_INT
HYPER_OID_INT: int = lib.HYPER_OID_INT
HYPER_OID_NUMERIC: int = lib.HYPER_OID_NUMERIC
HYPER_OID_FLOAT: int = lib.HYPER_OID_FLOAT
HYPER_OID_DOUBLE: int = lib.HYPER_OID_DOUBLE
HYPER_OID_OID: int = lib.HYPER_OID_OID
HYPER_OID_BYTE_A: int = lib.HYPER_OID_BYTE_A
HYPER_OID_TEXT: int = lib.HYPER_OID_TEXT
HYPER_OID_VARCHAR: int = lib.HYPER_OID_VARCHAR
HYPER_OID_CHAR: int = lib.HYPER_OID_CHAR
HYPER_OID_CHAR1: int = lib.HYPER_OID_CHAR1
HYPER_OID_JSON: int = lib.HYPER_OID_JSON
HYPER_OID_DATE: int = lib.HYPER_OID_DATE
HYPER_OID_INTERVAL: int = lib.HYPER_OID_INTERVAL
HYPER_OID_TIME: int = lib.HYPER_OID_TIME
HYPER_OID_TIMESTAMP: int = lib.HYPER_OID_TIMESTAMP
HYPER_OID_TIMESTAMP_TZ: int = lib.HYPER_OID_TIMESTAMP_TZ
HYPER_OID_TABGEOGRAPHY: int = lib.HYPER_OID_TABGEOGRAPHY
# Deprecated alias for `HYPER_OID_TABGEOGRAPHY`. Will be removed as part of W-17701666.
HYPER_OID_GEOGRAPHY: int = lib.HYPER_OID_GEOGRAPHY

hyper_error_create: Callable = lib.hyper_error_create
hyper_error_destroy: Callable = lib.hyper_error_destroy
hyper_error_get_field: Callable = lib.hyper_error_get_field
hyper_error_set_field: Callable = lib.hyper_error_set_field
hyper_parameters_destroy: Callable = lib.hyper_parameters_destroy
hyper_parameters_copy: Callable = lib.hyper_parameters_copy
hyper_parameters_set: Callable = lib.hyper_parameters_set
hyper_create_instance_parameters: Callable = lib.hyper_create_instance_parameters
hyper_instance_create: Callable = lib.hyper_instance_create
hyper_instance_shutdown: Callable = lib.hyper_instance_shutdown
hyper_instance_close: Callable = lib.hyper_instance_close
hyper_instance_get_endpoint_descriptor: Callable = lib.hyper_instance_get_endpoint_descriptor
hyper_instance_get_pid: Callable = lib.hyper_instance_get_pid
hyper_instance_get_exit_code: Callable = lib.hyper_instance_get_exit_code
hyper_create_connection_parameters: Callable = lib.hyper_create_connection_parameters
hyper_connect: Callable = lib.hyper_connect
hyper_disconnect: Callable = lib.hyper_disconnect
hyper_cancel: Callable = lib.hyper_cancel
hyper_connection_status: Callable = lib.hyper_connection_status
hyper_connection_trace: Callable = lib.hyper_connection_trace
hyper_connection_is_ready: Callable = lib.hyper_connection_is_ready
hyper_connection_is_alive: Callable = lib.hyper_connection_is_alive
hyper_connection_parameter_status: Callable = lib.hyper_connection_parameter_status
hyper_create_database: Callable = lib.hyper_create_database
hyper_drop_database: Callable = lib.hyper_drop_database
hyper_detach_all_databases: Callable = lib.hyper_detach_all_databases
hyper_detach_database: Callable = lib.hyper_detach_database
hyper_attach_database: Callable = lib.hyper_attach_database
hyper_create_schema: Callable = lib.hyper_create_schema
hyper_is_valid_type_tag: Callable = lib.hyper_is_valid_type_tag
hyper_create_table_definition: Callable = lib.hyper_create_table_definition
hyper_get_table_definition: Callable = lib.hyper_get_table_definition
hyper_destroy_table_definition: Callable = lib.hyper_destroy_table_definition
hyper_copy_table_definition: Callable = lib.hyper_copy_table_definition
hyper_table_definition_database_name: Callable = lib.hyper_table_definition_database_name
hyper_table_definition_schema_name: Callable = lib.hyper_table_definition_schema_name
hyper_table_definition_table_name: Callable = lib.hyper_table_definition_table_name
hyper_table_definition_table_persistence: Callable = lib.hyper_table_definition_table_persistence
hyper_table_definition_column_count: Callable = lib.hyper_table_definition_column_count
hyper_table_definition_column_type_tag: Callable = lib.hyper_table_definition_column_type_tag
hyper_table_definition_column_type_oid: Callable = lib.hyper_table_definition_column_type_oid
hyper_table_definition_column_type_modifier: Callable = lib.hyper_table_definition_column_type_modifier
hyper_get_max_length_from_modifier: Callable = lib.hyper_get_max_length_from_modifier
hyper_get_precision_from_modifier: Callable = lib.hyper_get_precision_from_modifier
hyper_get_scale_from_modifier: Callable = lib.hyper_get_scale_from_modifier
hyper_encode_numeric_modifier: Callable = lib.hyper_encode_numeric_modifier
hyper_encode_string_modifier: Callable = lib.hyper_encode_string_modifier
hyper_table_definition_column_index: Callable = lib.hyper_table_definition_column_index
hyper_table_definition_column_name: Callable = lib.hyper_table_definition_column_name
hyper_table_definition_column_is_nullable: Callable = lib.hyper_table_definition_column_is_nullable
hyper_table_definition_column_collation: Callable = lib.hyper_table_definition_column_collation
hyper_table_definition_add_column: Callable = lib.hyper_table_definition_add_column
hyper_create_table: Callable = lib.hyper_create_table
hyper_set_chunked_mode: Callable = lib.hyper_set_chunked_mode
hyper_set_chunk_size: Callable = lib.hyper_set_chunk_size
hyper_set_prefetch_threshold: Callable = lib.hyper_set_prefetch_threshold
hyper_execute_query: Callable = lib.hyper_execute_query
hyper_execute_query_params: Callable = lib.hyper_execute_query_params
hyper_execute_command: Callable = lib.hyper_execute_command
hyper_execute_command_with_stdin_from_file: Callable = lib.hyper_execute_command_with_stdin_from_file
hyper_execute_command_with_stdout_to_file: Callable = lib.hyper_execute_command_with_stdout_to_file
hyper_set_connection_setting: Callable = lib.hyper_set_connection_setting
hyper_string_list_destroy: Callable = lib.hyper_string_list_destroy
hyper_string_list_size: Callable = lib.hyper_string_list_size
hyper_string_list_at: Callable = lib.hyper_string_list_at
hyper_get_schema_names: Callable = lib.hyper_get_schema_names
hyper_get_table_names: Callable = lib.hyper_get_table_names
hyper_has_table: Callable = lib.hyper_has_table
hyper_quote_sql_identifier: Callable = lib.hyper_quote_sql_identifier
hyper_quote_sql_literal: Callable = lib.hyper_quote_sql_literal
hyper_prepare: Callable = lib.hyper_prepare
hyper_execute_prepared: Callable = lib.hyper_execute_prepared
hyper_close_rowset: Callable = lib.hyper_close_rowset
hyper_rowset_get_type: Callable = lib.hyper_rowset_get_type
hyper_rowset_get_table_definition: Callable = lib.hyper_rowset_get_table_definition
hyper_rowset_get_affected_row_count: Callable = lib.hyper_rowset_get_affected_row_count
hyper_rowset_get_next_chunk: Callable = lib.hyper_rowset_get_next_chunk
hyper_rowset_chunk_row_count: Callable = lib.hyper_rowset_chunk_row_count
hyper_rowset_chunk_field_value: Callable = lib.hyper_rowset_chunk_field_value
hyper_rowset_chunk_field_is_null: Callable = lib.hyper_rowset_chunk_field_is_null
hyper_rowset_chunk_field_values: Callable = lib.hyper_rowset_chunk_field_values
hyper_rowset_has_copy_data: Callable = lib.hyper_rowset_has_copy_data
hyper_rowset_get_copy_data: Callable = lib.hyper_rowset_get_copy_data
hyper_rowset_free_copy_data: Callable = lib.hyper_rowset_free_copy_data
hyper_destroy_rowset_chunk: Callable = lib.hyper_destroy_rowset_chunk
hyper_create_data_chunk: Callable = lib.hyper_create_data_chunk
hyper_resize_data_chunk: Callable = lib.hyper_resize_data_chunk
hyper_get_chunk_data: Callable = lib.hyper_get_chunk_data
hyper_get_chunk_header_size: Callable = lib.hyper_get_chunk_header_size
hyper_get_chunk_data_size: Callable = lib.hyper_get_chunk_data_size
hyper_destroy_data_chunk: Callable = lib.hyper_destroy_data_chunk
hyper_create_inserter: Callable = lib.hyper_create_inserter
hyper_init_bulk_insert: Callable = lib.hyper_init_bulk_insert
hyper_insert_computed_expressions: Callable = lib.hyper_insert_computed_expressions
hyper_inserter_insert_chunk: Callable = lib.hyper_inserter_insert_chunk
hyper_close_inserter: Callable = lib.hyper_close_inserter
hyper_write_null: Callable = lib.hyper_write_null
hyper_write_header: Callable = lib.hyper_write_header
hyper_write_int8: Callable = lib.hyper_write_int8
hyper_write_int8_not_null: Callable = lib.hyper_write_int8_not_null
hyper_write_int16: Callable = lib.hyper_write_int16
hyper_write_int16_not_null: Callable = lib.hyper_write_int16_not_null
hyper_write_int32: Callable = lib.hyper_write_int32
hyper_write_int32_not_null: Callable = lib.hyper_write_int32_not_null
hyper_write_int64: Callable = lib.hyper_write_int64
hyper_write_int64_not_null: Callable = lib.hyper_write_int64_not_null
hyper_write_data128: Callable = lib.hyper_write_data128
hyper_write_data128_not_null: Callable = lib.hyper_write_data128_not_null
hyper_write_varbinary: Callable = lib.hyper_write_varbinary
hyper_write_varbinary_not_null: Callable = lib.hyper_write_varbinary_not_null
hyper_read_int8: Callable = lib.hyper_read_int8
hyper_read_int16: Callable = lib.hyper_read_int16
hyper_read_int32: Callable = lib.hyper_read_int32
hyper_read_int64: Callable = lib.hyper_read_int64
hyper_read_data128: Callable = lib.hyper_read_data128
hyper_read_varbinary: Callable = lib.hyper_read_varbinary
hyper_create_inserter_buffer: Callable = lib.hyper_create_inserter_buffer
hyper_inserter_buffer_flush: Callable = lib.hyper_inserter_buffer_flush
hyper_inserter_buffer_destroy: Callable = lib.hyper_inserter_buffer_destroy
hyper_inserter_buffer_add_null: Callable = lib.hyper_inserter_buffer_add_null
hyper_inserter_buffer_add_bool: Callable = lib.hyper_inserter_buffer_add_bool
hyper_inserter_buffer_add_int16: Callable = lib.hyper_inserter_buffer_add_int16
hyper_inserter_buffer_add_int32: Callable = lib.hyper_inserter_buffer_add_int32
hyper_inserter_buffer_add_int64: Callable = lib.hyper_inserter_buffer_add_int64
hyper_inserter_buffer_add_float: Callable = lib.hyper_inserter_buffer_add_float
hyper_inserter_buffer_add_double: Callable = lib.hyper_inserter_buffer_add_double
hyper_inserter_buffer_add_binary: Callable = lib.hyper_inserter_buffer_add_binary
hyper_inserter_buffer_add_date: Callable = lib.hyper_inserter_buffer_add_date
hyper_inserter_buffer_add_raw: Callable = lib.hyper_inserter_buffer_add_raw
hyper_decode_date: Callable = lib.hyper_decode_date
hyper_encode_date: Callable = lib.hyper_encode_date
hyper_date_to_string: Callable = lib.hyper_date_to_string
hyper_decode_time: Callable = lib.hyper_decode_time
hyper_encode_time: Callable = lib.hyper_encode_time
hyper_time_to_string: Callable = lib.hyper_time_to_string
hyper_decode_interval: Callable = lib.hyper_decode_interval
hyper_encode_interval: Callable = lib.hyper_encode_interval
hyper_numeric_from_string: Callable = lib.hyper_numeric_from_string
hyper_big_numeric_from_string: Callable = lib.hyper_big_numeric_from_string
hyper_numeric_to_string: Callable = lib.hyper_numeric_to_string
hyper_big_numeric_to_string: Callable = lib.hyper_big_numeric_to_string
hyper_numeric_change_scale: Callable = lib.hyper_numeric_change_scale
hyper_big_numeric_change_scale: Callable = lib.hyper_big_numeric_change_scale
hyper_numeric_round_to_int64: Callable = lib.hyper_numeric_round_to_int64
hyper_big_numeric_round_to_int64: Callable = lib.hyper_big_numeric_round_to_int64
hyper_numeric_from_float: Callable = lib.hyper_numeric_from_float
hyper_big_numeric_from_float: Callable = lib.hyper_big_numeric_from_float
hyper_numeric_to_float: Callable = lib.hyper_numeric_to_float
hyper_big_numeric_to_float: Callable = lib.hyper_big_numeric_to_float
hyper_numeric_from_double: Callable = lib.hyper_numeric_from_double
hyper_big_numeric_from_double: Callable = lib.hyper_big_numeric_from_double
hyper_numeric_to_double: Callable = lib.hyper_numeric_to_double
hyper_big_numeric_to_double: Callable = lib.hyper_big_numeric_to_double
hyper_copy_data: Callable = lib.hyper_copy_data
hyper_copy_end: Callable = lib.hyper_copy_end
hyper_log_set_log_function: Callable = lib.hyper_log_set_log_function
hyper_log_set_log_level: Callable = lib.hyper_log_set_log_level
hyper_default_log_function: Callable = lib.hyper_default_log_function
hyper_log_event: Callable = lib.hyper_log_event
