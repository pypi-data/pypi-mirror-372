# THIS IS A GENERATED FILE, DO NOT EDIT
# noinspection PyPep8
LIB_H = R"""
typedef struct hyper_error_t hyper_error_t;
typedef enum {
HYPER_ERROR_CATEGORY_GENERIC = 0,
HYPER_ERROR_CATEGORY_SYSTEM = 1,
HYPER_ERROR_CATEGORY_PROCESS_EXIT_CODE = 3,
HYPER_ERROR_CATEGORY_SQLSTATE = 4
} hyper_error_category_t;
typedef enum {
HYPER_SEVERITY_ERROR,
HYPER_SEVERITY_FATAL,
HYPER_SEVERITY_PANIC
} hyper_error_severity_t;
typedef enum {
HYPER_ERROR_SOURCE_USER,
HYPER_ERROR_SOURCE_SYSTEM
} hyper_error_source_t;
typedef enum {
HYPER_ERROR_FIELD_ERROR_CATEGORY = 0,
HYPER_ERROR_FIELD_ERROR_CODE = 1,
HYPER_ERROR_FIELD_MESSAGE = 2,
HYPER_ERROR_FIELD_HINT_MESSAGE = 3,
HYPER_ERROR_FIELD_SEVERITY = 4,
HYPER_ERROR_FIELD_SQL_STATE = 5,
HYPER_ERROR_FIELD_CAUSE = 6,
HYPER_ERROR_FIELD_CONTEXT_ID = 7,
HYPER_ERROR_FIELD_DETAIL = 8,
HYPER_ERROR_FIELD_SOURCE = 9,
HYPER_ERROR_GRPC_STATUS = 10
} hyper_error_field_key;
hyper_error_t* hyper_error_create(uint32_t contextId);
void hyper_error_destroy(hyper_error_t* error);
struct hyper_error_field_value {
int discriminator;
union {
int integer;
const char* string;
void* pointer;
uint32_t uinteger;
} value;
};
;
;
typedef struct hyper_parameters_t hyper_parameters_t;
void hyper_parameters_destroy(hyper_parameters_t* parameters);
hyper_parameters_t* hyper_parameters_copy(const hyper_parameters_t* parameters);
hyper_error_t* hyper_parameters_set(hyper_parameters_t* parameters, const char* key, const char* value);
typedef struct hyper_instance_t hyper_instance_t;
typedef enum {
HYPER_DISABLE_TELEMETRY = 0,
HYPER_ENABLE_TELEMETRY = 1
} hyper_telemetry_t;
hyper_error_t* hyper_create_instance_parameters(hyper_parameters_t** parameters, bool use_defaults);
hyper_error_t* hyper_instance_create(
const char* hyper_path, hyper_telemetry_t telemetry, const hyper_parameters_t* parameters, hyper_instance_t** instance);
hyper_error_t* hyper_instance_shutdown(hyper_instance_t* instance, int timeoutMs);
void hyper_instance_close(hyper_instance_t* instance);
const char* hyper_instance_get_endpoint_descriptor(const hyper_instance_t* instance);
int64_t hyper_instance_get_pid(const hyper_instance_t* instance);
bool hyper_instance_get_exit_code(hyper_instance_t* instance, int* exit_code);
typedef struct hyper_connection_t hyper_connection_t;
typedef struct {
uint32_t major;
uint32_t minor;
} hyper_service_version_t;
hyper_error_t* hyper_create_connection_parameters(const hyper_instance_t* instance, hyper_parameters_t** parameters);
typedef enum {
HYPER_DO_NOT_CREATE = 0,
HYPER_CREATE,
HYPER_CREATE_IF_NOT_EXISTS,
HYPER_CREATE_AND_REPLACE
} hyper_create_mode_t;
hyper_error_t* hyper_connect(const hyper_parameters_t* parameters, hyper_connection_t** connection, hyper_create_mode_t mode);
void hyper_disconnect(hyper_connection_t* connection);
hyper_error_t* hyper_cancel(hyper_connection_t* connection);
typedef enum {
HYPER_CONNECTION_OK,
HYPER_CONNECTION_BAD
} hyper_connection_status_t;
hyper_connection_status_t hyper_connection_status(hyper_connection_t* connection);
void hyper_connection_trace(hyper_connection_t* connection, void* debugDestination);
bool hyper_connection_is_ready(hyper_connection_t* connection);
bool hyper_connection_is_alive(hyper_connection_t* connection);
const char* hyper_connection_parameter_status(const hyper_connection_t* connection, const char* parameter_name);
typedef void (*hyper_notice_receiver_t)(void* context, hyper_error_t* notice);
typedef void (*hyper_rowset_async_callback_t)(void* context, bool is_last_empty_chunk);
void hyper_set_notice_receiver(hyper_connection_t* connection, hyper_notice_receiver_t receiver, void* context);
void hyper_set_rowset_async_callback(hyper_connection_t* connection, hyper_rowset_async_callback_t callback, void* context);
hyper_error_t* hyper_create_database(hyper_connection_t* connection, const char* path, bool failIfExists);
hyper_error_t* hyper_drop_database(hyper_connection_t* connection, const char* path, bool failIfNotExists);
hyper_error_t* hyper_detach_all_databases(hyper_connection_t* connection);
hyper_error_t* hyper_detach_database(hyper_connection_t* connection, const char* alias);
hyper_error_t* hyper_attach_database(hyper_connection_t* connection, const char* path, const char* alias);
hyper_error_t* hyper_create_schema(hyper_connection_t* connection, const char* databaseName, const char* schemaName, bool failIfExists);
typedef struct hyper_table_definition_t hyper_table_definition_t;
typedef enum {
HYPER_UNSUPPORTED = 0,
HYPER_BOOL = 1,
HYPER_BIG_INT = 2,
HYPER_SMALL_INT = 3,
HYPER_INT = 4,
HYPER_NUMERIC = 5,
HYPER_DOUBLE = 6,
HYPER_OID = 7,
HYPER_BYTE_A = 8,
HYPER_TEXT = 9,
HYPER_VARCHAR = 10,
HYPER_CHAR = 11,
HYPER_JSON = 12,
HYPER_DATE = 13,
HYPER_INTERVAL = 14,
HYPER_TIME = 15,
HYPER_TIMESTAMP = 16,
HYPER_TIMESTAMP_TZ = 17,
HYPER_TABGEOGRAPHY = 18,
HYPER_GEOGRAPHY = 18,
HYPER_FLOAT = 19,
} hyper_type_tag_t;
bool hyper_is_valid_type_tag(hyper_type_tag_t tag);
typedef uint32_t hyper_field_index_t;
typedef uint32_t hyper_row_index_t;
typedef uint32_t hyper_type_modifier_t;
typedef enum {
HYPER_PERMANENT = 0,
HYPER_TEMPORARY = 1
} hyper_table_persistence_t;
hyper_table_definition_t* hyper_create_table_definition(
const char* database_name, const char* schema_name, const char* table_name, hyper_table_persistence_t persistence, bool stream);
hyper_error_t* hyper_get_table_definition(
hyper_connection_t* connection, const char* database_name, const char* schema_name, const char* table_name, hyper_table_definition_t** table_definition);
void hyper_destroy_table_definition(hyper_table_definition_t* table_definition);
hyper_error_t* hyper_copy_table_definition(const hyper_table_definition_t* table_definition, hyper_table_definition_t** copy);
const char* hyper_table_definition_database_name(const hyper_table_definition_t* table_definition);
const char* hyper_table_definition_schema_name(const hyper_table_definition_t* table_definition);
const char* hyper_table_definition_table_name(const hyper_table_definition_t* table_definition);
hyper_table_persistence_t hyper_table_definition_table_persistence(const hyper_table_definition_t* table_definition);
size_t hyper_table_definition_column_count(const hyper_table_definition_t* table_definition);
hyper_type_tag_t hyper_table_definition_column_type_tag(const hyper_table_definition_t* table_definition, hyper_field_index_t column_index);
uint32_t hyper_table_definition_column_type_oid(const hyper_table_definition_t* table_definition, hyper_field_index_t column_index);
hyper_type_modifier_t hyper_table_definition_column_type_modifier(const hyper_table_definition_t* table_definition, hyper_field_index_t column_index);
uint32_t hyper_get_max_length_from_modifier(hyper_type_modifier_t modifier);
uint32_t hyper_get_precision_from_modifier(hyper_type_modifier_t modifier);
uint32_t hyper_get_scale_from_modifier(hyper_type_modifier_t modifier);
hyper_type_modifier_t hyper_encode_numeric_modifier(uint32_t precision, uint32_t scale);
hyper_type_modifier_t hyper_encode_string_modifier(uint32_t max_length);
hyper_field_index_t hyper_table_definition_column_index(const hyper_table_definition_t* table_definition, const char* column_name);
const char* hyper_table_definition_column_name(const hyper_table_definition_t* table_definition, hyper_field_index_t column_index);
bool hyper_table_definition_column_is_nullable(const hyper_table_definition_t* table_definition, hyper_field_index_t column_index);
const char* hyper_table_definition_column_collation(const hyper_table_definition_t* table_definition, hyper_field_index_t column_index);
hyper_error_t* hyper_table_definition_add_column(
hyper_table_definition_t* table_definition,
const char* column_name,
hyper_type_tag_t type_tag,
hyper_type_modifier_t modifier,
const char* collation,
bool nullable);
hyper_error_t* hyper_create_table(
hyper_connection_t* connection, const hyper_table_definition_t* table_definition, bool failIfExists);
typedef struct hyper_rowset_t hyper_rowset_t;
typedef struct hyper_rowset_chunk_t hyper_rowset_chunk_t;
typedef struct
{
const uint8_t* value;
size_t size;
} hyper_value_t;
typedef enum {
HYPER_ROWSET_RESULT_FORMAT_TEXT = 0,
HYPER_ROWSET_RESULT_FORMAT_HYPER_BINARY = 2
} hyper_rowset_result_format_t;
void hyper_set_chunked_mode(hyper_connection_t* connection, bool chunked_mode);
size_t hyper_set_chunk_size(hyper_connection_t* connection, size_t chunk_size);
void hyper_set_prefetch_threshold(hyper_connection_t* connection, size_t prefetch_threshold);
hyper_error_t* hyper_execute_query(hyper_connection_t* connection, const char* query, hyper_rowset_t** rowset);
hyper_error_t* hyper_execute_query_params(
hyper_connection_t* connection, const char* query, hyper_rowset_result_format_t result_format, hyper_rowset_t** rowset);
hyper_error_t* hyper_execute_command(hyper_connection_t* connection, const char* query, int* affected_row_count);
hyper_error_t* hyper_execute_command_with_stdin_from_file(hyper_connection_t* connection, const char* query, const char* path);
hyper_error_t* hyper_execute_command_with_stdout_to_file(hyper_connection_t* connection, const char* query, const char* path);
hyper_error_t* hyper_set_connection_setting(hyper_connection_t* connection, const char* key, const char* value);
typedef struct hyper_string_list_t hyper_string_list_t;
void hyper_string_list_destroy(hyper_string_list_t* string_list);
size_t hyper_string_list_size(hyper_string_list_t* string_list);
const char* hyper_string_list_at(hyper_string_list_t* string_list, int index);
hyper_error_t* hyper_get_schema_names(hyper_connection_t* connection, const char* database, hyper_string_list_t** schema_names);
hyper_error_t* hyper_get_table_names(
hyper_connection_t* connection, const char* database, const char* schema, hyper_string_list_t** table_names);
hyper_error_t* hyper_has_table(
hyper_connection_t* connection, const char* database, const char* schema, const char* table, bool* exists);
size_t hyper_quote_sql_identifier(char* target, size_t space, const char* value, size_t length);
size_t hyper_quote_sql_literal(char* target, size_t space, const char* value, size_t length);
hyper_error_t* hyper_prepare(hyper_connection_t* connection, const char* statement_name, const char* query);
hyper_error_t* hyper_execute_prepared(
hyper_connection_t* connection, const char* statement_name, hyper_rowset_result_format_t result_format, hyper_rowset_t** rowset);
void hyper_close_rowset(hyper_rowset_t* rowset);
typedef enum {
HYPER_ROWSET_EMPTY_QUERY,
HYPER_ROWSET_COMMAND,
HYPER_ROWSET_QUERY_RESULT,
HYPER_ROWSET_COPY_IN,
HYPER_ROWSET_COPY_OUT,
} hyper_rowset_type_t;
hyper_rowset_type_t hyper_rowset_get_type(hyper_rowset_t* rowset);
const hyper_table_definition_t* hyper_rowset_get_table_definition(const hyper_rowset_t* rowset);
int64_t hyper_rowset_get_affected_row_count(const hyper_rowset_t* rowset);
hyper_error_t* hyper_rowset_get_next_chunk(hyper_rowset_t* rowset, hyper_rowset_chunk_t** rowset_chunk);
size_t hyper_rowset_chunk_row_count(const hyper_rowset_chunk_t* rowset_chunk);
hyper_value_t hyper_rowset_chunk_field_value(const hyper_rowset_chunk_t* rowset_chunk, hyper_row_index_t row_index, hyper_field_index_t field_index);
bool hyper_rowset_chunk_field_is_null(const hyper_rowset_chunk_t* rowset_chunk, hyper_field_index_t row_index, hyper_field_index_t field_index);
void hyper_rowset_chunk_field_values(hyper_rowset_chunk_t* rowset_chunk, size_t* col_count, size_t* row_count, const uint8_t* const* values[], const size_t* sizes[]);
bool hyper_rowset_has_copy_data(const hyper_rowset_t* rowset);
hyper_error_t* hyper_rowset_get_copy_data(hyper_rowset_t* rowset, char** buffer, size_t* length);
void hyper_rowset_free_copy_data(char* buffer);
void hyper_destroy_rowset_chunk(const hyper_rowset_chunk_t* rowset_chunk);
typedef struct hyper_data_chunk_t hyper_data_chunk_t;
hyper_data_chunk_t* hyper_create_data_chunk();
hyper_error_t* hyper_resize_data_chunk(hyper_data_chunk_t* data_chunk, size_t size);
uint8_t* hyper_get_chunk_data(const hyper_data_chunk_t* data_chunk);
size_t hyper_get_chunk_header_size(const hyper_data_chunk_t* data_chunk);
size_t hyper_get_chunk_data_size(const hyper_data_chunk_t* data_chunk);
void hyper_destroy_data_chunk(hyper_data_chunk_t* data_chunk);
typedef struct hyper_inserter_t hyper_inserter_t;
hyper_error_t* hyper_create_inserter(
hyper_connection_t* connection, const hyper_table_definition_t* table_definition, hyper_inserter_t** inserter);
hyper_error_t* hyper_init_bulk_insert(hyper_inserter_t* inserter, const hyper_table_definition_t* table_definition, const char* select_list);
hyper_error_t* hyper_insert_computed_expressions(hyper_inserter_t* inserter, const char* select_list);
hyper_error_t* hyper_inserter_insert_chunk(hyper_inserter_t* inserter, const uint8_t* data_chunk, size_t bytes);
hyper_error_t* hyper_close_inserter(hyper_inserter_t* inserter, bool insert_data);
typedef struct
{
uint64_t data[2];
} hyper_data128_t;
size_t hyper_write_null(uint8_t* target, size_t space);
size_t hyper_write_header(uint8_t* target, size_t space);
size_t hyper_write_int8(uint8_t* target, size_t space, int8_t value);
size_t hyper_write_int8_not_null(uint8_t* target, size_t space, int8_t value);
size_t hyper_write_int16(uint8_t* target, size_t space, int16_t value);
size_t hyper_write_int16_not_null(uint8_t* target, size_t space, int16_t value);
size_t hyper_write_int32(uint8_t* target, size_t space, int32_t value);
size_t hyper_write_int32_not_null(uint8_t* target, size_t space, int32_t value);
size_t hyper_write_int64(uint8_t* target, size_t space, int64_t value);
size_t hyper_write_int64_not_null(uint8_t* target, size_t space, int64_t value);
size_t hyper_write_data128(uint8_t* target, size_t space, hyper_data128_t value);
size_t hyper_write_data128_not_null(uint8_t* target, size_t space, hyper_data128_t value);
size_t hyper_write_varbinary(uint8_t* target, size_t space, const uint8_t* value, size_t length);
size_t hyper_write_varbinary_not_null(uint8_t* target, size_t space, const uint8_t* value, size_t length);
int8_t hyper_read_int8(const uint8_t* source);
int16_t hyper_read_int16(const uint8_t* source);
int32_t hyper_read_int32(const uint8_t* source);
int64_t hyper_read_int64(const uint8_t* source);
hyper_data128_t hyper_read_data128(const uint8_t* source);
const uint8_t* hyper_read_varbinary(const uint8_t* source);
typedef struct hyper_inserter_buffer_t hyper_inserter_buffer_t;
hyper_error_t* hyper_create_inserter_buffer(
hyper_inserter_t* inserter, const hyper_table_definition_t* table_definition, const char* select_list, hyper_inserter_buffer_t** buffer);
hyper_error_t* hyper_inserter_buffer_flush(hyper_inserter_buffer_t* buffer);
void hyper_inserter_buffer_destroy(hyper_inserter_buffer_t* buffer);
hyper_error_t* hyper_inserter_buffer_add_null(hyper_inserter_buffer_t* buffer);
hyper_error_t* hyper_inserter_buffer_add_bool(hyper_inserter_buffer_t* buffer, bool value);
hyper_error_t* hyper_inserter_buffer_add_int16(hyper_inserter_buffer_t* buffer, int16_t value);
hyper_error_t* hyper_inserter_buffer_add_int32(hyper_inserter_buffer_t* buffer, int32_t value);
hyper_error_t* hyper_inserter_buffer_add_int64(hyper_inserter_buffer_t* buffer, int64_t value);
hyper_error_t* hyper_inserter_buffer_add_float(hyper_inserter_buffer_t* buffer, float value);
hyper_error_t* hyper_inserter_buffer_add_double(hyper_inserter_buffer_t* buffer, double value);
hyper_error_t* hyper_inserter_buffer_add_binary(hyper_inserter_buffer_t* buffer, const uint8_t* value, size_t size);
hyper_error_t* hyper_inserter_buffer_add_date(hyper_inserter_buffer_t* buffer, int32_t year, int16_t month, int16_t day);
hyper_error_t* hyper_inserter_buffer_add_raw(hyper_inserter_buffer_t* buffer, const uint8_t* value, size_t size);
typedef uint32_t hyper_date_t;
typedef struct
{
int32_t year;
int16_t month;
int16_t day;
} hyper_date_components_t;
typedef uint64_t hyper_time_t;
typedef struct
{
int8_t hour;
int8_t minute;
int8_t second;
int32_t microsecond;
} hyper_time_components_t;
typedef uint64_t hyper_timestamp_t;
typedef hyper_data128_t hyper_interval_t;
typedef struct
{
int32_t years;
int32_t months;
int32_t days;
int32_t hours;
int32_t minutes;
int32_t seconds;
int32_t microseconds;
} hyper_interval_components_t;
hyper_date_components_t hyper_decode_date(hyper_date_t date);
hyper_date_t hyper_encode_date(hyper_date_components_t components);
size_t hyper_date_to_string(char* target, size_t space, hyper_date_t value);
hyper_time_components_t hyper_decode_time(hyper_time_t time);
hyper_time_t hyper_encode_time(hyper_time_components_t components);
size_t hyper_time_to_string(char* target, size_t space, hyper_time_t value);
hyper_interval_components_t hyper_decode_interval(hyper_interval_t interval);
hyper_interval_t hyper_encode_interval(hyper_interval_components_t components);
hyper_error_t* hyper_numeric_from_string(const char** iter, const char* limit, uint32_t precision, uint32_t scale, int64_t* result);
hyper_error_t* hyper_big_numeric_from_string(const char** iter, const char* limit, uint32_t precision, uint32_t scale, hyper_data128_t* result);
char* hyper_numeric_to_string(char* target, size_t space, int64_t value, uint32_t scale);
char* hyper_big_numeric_to_string(char* target, size_t space, hyper_data128_t value, uint32_t scale);
hyper_error_t* hyper_numeric_change_scale(int64_t value, uint32_t scale, uint32_t new_scale, int64_t* result);
hyper_error_t* hyper_big_numeric_change_scale(hyper_data128_t value, uint32_t scale, uint32_t new_scale, hyper_data128_t* result);
int64_t hyper_numeric_round_to_int64(int64_t value, uint32_t scale);
hyper_error_t* hyper_big_numeric_round_to_int64(hyper_data128_t value, uint32_t scale, int64_t* result);
hyper_error_t* hyper_numeric_from_float(float value, uint32_t scale, int64_t* result);
hyper_error_t* hyper_big_numeric_from_float(float value, uint32_t scale, hyper_data128_t* result);
float hyper_numeric_to_float(int64_t value, uint32_t scale);
float hyper_big_numeric_to_float(hyper_data128_t value, uint32_t scale);
hyper_error_t* hyper_numeric_from_double(double value, uint32_t scale, int64_t* result);
hyper_error_t* hyper_big_numeric_from_double(double value, uint32_t scale, hyper_data128_t* result);
double hyper_numeric_to_double(int64_t value, uint32_t scale);
double hyper_big_numeric_to_double(hyper_data128_t value, uint32_t scale);
hyper_error_t* hyper_copy_data(hyper_connection_t* connection, const uint8_t* buffer, size_t size);
hyper_error_t* hyper_copy_end(hyper_connection_t* connection);
typedef enum {
HYPER_LOG_LEVEL_TRACE = 0,
HYPER_LOG_LEVEL_INFO,
HYPER_LOG_LEVEL_WARNING,
HYPER_LOG_LEVEL_ERROR,
HYPER_LOG_LEVEL_FATAL
} hyper_log_level_t;
typedef void (*hyper_log_function_t)(hyper_log_level_t log_level, const char* topic, const char* json_value, void* context);
hyper_log_function_t hyper_log_set_log_function(hyper_log_function_t log_function, void* context);
hyper_log_level_t hyper_log_set_log_level(hyper_log_level_t log_level);
void hyper_default_log_function(hyper_log_level_t log_level, const char* topic, const char* json_value, void* context);
void hyper_log_event(hyper_log_level_t log_level, const char* topic, const char* json_value);
enum {
HYPER_OID_BOOL = 16,
HYPER_OID_BIG_INT = 20,
HYPER_OID_SMALL_INT = 21,
HYPER_OID_INT = 23,
HYPER_OID_NUMERIC = 1700,
HYPER_OID_FLOAT = 700,
HYPER_OID_DOUBLE = 701,
HYPER_OID_OID = 26,
HYPER_OID_BYTE_A = 17,
HYPER_OID_TEXT = 25,
HYPER_OID_VARCHAR = 1043,
HYPER_OID_CHAR = 1042,
HYPER_OID_CHAR1 = 18,
HYPER_OID_JSON = 114,
HYPER_OID_DATE = 1082,
HYPER_OID_INTERVAL = 1186,
HYPER_OID_TIME = 1083,
HYPER_OID_TIMESTAMP = 1114,
HYPER_OID_TIMESTAMP_TZ = 1184,
HYPER_OID_TABGEOGRAPHY = 5003,
HYPER_OID_GEOGRAPHY = 5003,
};
"""
