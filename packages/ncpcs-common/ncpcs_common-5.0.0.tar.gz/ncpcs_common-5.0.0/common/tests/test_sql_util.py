from common.util.sql_util import get_insert_columns_and_values, transfer_database_name_to_hump, \
    transfer_hump_to_database_name, generate_select_sql, generate_insert_sql, generate_batch_insert_sql, \
    generate_common_query_sql, generate_create_table_sql


class TestSqlUtil:
    def test_transfer_database_name_to_hump(self):
        assert transfer_database_name_to_hump("nc_add_time") == 'ncAddTime'
        assert transfer_database_name_to_hump("nc_admission_record") == 'ncAdmissionRecord'

    def test_transfer_hump_to_database_name(self):
        assert transfer_hump_to_database_name("ncAddTime") == 'nc_add_time'
        assert transfer_hump_to_database_name("ncAdmissionRecord") == 'nc_admission_record'

    def test_generate_select_sql(self):
        print(generate_select_sql('ncpcs_nlp', 'nc_entity'))

    def test_generate_insert_sql(self):
        print(generate_insert_sql('ncpcs_nlp', 'nc_human_reasoning_archive'))

    def test_generate_batch_insert_sql(self):
        print(generate_batch_insert_sql('ncpcs_nlp', 'nc_entity'))

    def test_generate_common_query_sql(self):
        print(generate_common_query_sql('ncpcs_tool', 'nc_report_medical_info'))

    def test_get_insert_columns_and_values(self):
        columns, values = get_insert_columns_and_values({
            "a": "深爱",
            "b": ['1', '2', '3'],
            "c": 5
        })
        assert columns == 'a,b,c'
        print(values)
        assert values == "'深爱','1,2,3',5"

    def test_generate_create_table_sql(self):
        # 测试数据
        table_name = "example_table"
        columns = {
            "id": "INT AUTO_INCREMENT PRIMARY KEY",
            "nc_add_account": "VARCHAR(50) COMMENT '添加者'",
            "nc_upd_account": "VARCHAR(50) COMMENT '添加者'",
            "nc_add_time": "VARCHAR(18) COMMENT '添加时间'",
            "nc_upd_time": "VARCHAR(18) COMMENT '更新时间'",
            "nc_medical_institution_code": "VARCHAR(30) COMMENT '组织机构代码'",
            "nc_medical_record_no": "VARCHAR(50) COMMENT '病案号'",
            "nc_discharge_time": "DATETIME COMMENT '出院时间'"
        }

        # 生成CREATE TABLE语句
        create_table_sql = generate_create_table_sql(table_name, columns)
        print(create_table_sql)