from common.constants.database_config import STORE_BATCH_COUNT
from common.util.database_connection_util import get_connection_by_schema

COMMON_WHERE_FORMAT = '''
<sql id="Common_Where">
    <where>
        {}    
    </where>
</sql>
'''
INSERT_SQL_FORMAT = "insert into {}({}) values({})"
SELECT_SQL_FORMAT = "select {} from {}"
BATCH_INSERT_SQL_FORMAT = '''
<insert id="batchInsert">
    <if test="list.size() > 0">
        insert into {}({}) 
        values
        <foreach collection="list" item="item" separator=",">
            ({})
        </foreach>
        ;
    </if>
</insert>
'''


def update_by_batch(table_name, relation_key_list, conn):
    if not relation_key_list:
        return
    cursor = conn.cursor()
    size = len(relation_key_list)
    i = 0
    print(update_by_batch.__name__, "执行{}任务开始, 总计{}条待修改数据".format(table_name, size))
    while i < size:
        endI = min(i + STORE_BATCH_COUNT, size)
        print(update_by_batch.__name__, "startIndex: {}, endIndex: {}".format(i, endI))
        cursor.execute("update {} set nc_valid_flag = 1 where nc_key in ({})".format(
                        table_name, ','.join(["'{}'".format(nc_key) for nc_key in relation_key_list[i: endI]])))
        conn.commit()
        i += STORE_BATCH_COUNT
    cursor.close()
    print(update_by_batch.__name__, "执行{}任务结束".format(table_name))

def store_by_batch(table_name, data_list, conn):
    if not data_list:
        return
    size = len(data_list)
    i = 0
    cursor = conn.cursor()
    print(store_by_batch.__name__, "执行{}任务开始, 总计{}条待存储数据".format(table_name, size))
    while i < size:
        endI = min(i + STORE_BATCH_COUNT, size)
        print(store_by_batch.__name__, "startIndex: {}, endIndex: {}".format(i, endI))
        _batch_store_func(table_name, data_list[i: endI], cursor)
        conn.commit()
        i += STORE_BATCH_COUNT
    cursor.close()
    print(store_by_batch.__name__, "执行{}任务结束".format(table_name))


def transfer_database_name_to_hump(column_name):
    i = 0
    ans = ''
    while i < len(column_name):
        ch = column_name[i]
        if ch == '_' and i + 1 < len(column_name):
            ans = ans + column_name[i + 1].upper()
            i += 2
        else:
            ans += ch
            i += 1
    return ans


def transfer_hump_to_database_name(string):
    # schoolAddress -> school_address
    result = ""
    for ch in string:
        if ch.isupper():
            result = result + '_' + ch.lower()
        else:
            result += ch
    return result


def generate_select_sql(schema, table_name):
    col_name_list, _ = _get_col_list(schema, table_name)
    select_sql = SELECT_SQL_FORMAT.format(", ".join(col_name_list), table_name)
    return select_sql


def generate_insert_sql(schema, table_name):
    col_name_list, item_name_list = _get_col_list(schema, table_name)
    item_name_str = ", ".join(item_name_list)
    item_name_str = item_name_str.replace("[", "{")
    item_name_str = item_name_str.replace("]", "}")
    insert_sql = INSERT_SQL_FORMAT.format(table_name, ", ".join(col_name_list), item_name_str)
    return insert_sql


def generate_batch_insert_sql(schema, table_name):
    col_name_list, item_name_list = _get_col_list(schema, table_name)
    item_name_str = ",\n\t\t\t".join(item_name_list)
    item_name_str = item_name_str.replace("[", "{")
    item_name_str = item_name_str.replace("]", "}")
    batch_insert_sql = BATCH_INSERT_SQL_FORMAT.format(table_name, ",\n\t\t\t".join(col_name_list), item_name_str)
    return batch_insert_sql


def generate_common_query_sql(schema, table_name):
    OTHER_IF_SQL_FORMAT = '''
        <if test="param.{} != null">
            and {} = #[param.{}]
        </if>'''

    STR_IF_SQL_FORMAT = '''
        <if test="param.{} != null and param.{} != ''">
            and {} = #[param.{}]
        </if>'''
    CHECK_COL_SQL_FORMAT = "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{}' AND TABLE_SCHEMA = '{}'"
    conn = get_connection_by_schema(schema)
    cursor = conn.cursor()
    cursor.execute(CHECK_COL_SQL_FORMAT.format(table_name, schema))
    if_sql = ""
    for ele in cursor.fetchall():
        hump_name = transfer_database_name_to_hump(ele[0])
        if ele[1].find("char") != -1 or ele[1].find("text") != -1:
            if_sql = if_sql + STR_IF_SQL_FORMAT.format(hump_name, hump_name, ele[0], hump_name)
        if ele[1].find("int") != -1:
            if_sql = if_sql + OTHER_IF_SQL_FORMAT.format(hump_name, ele[0], hump_name)
        if ele[1].find("datetime") != -1:
            if_sql = if_sql + OTHER_IF_SQL_FORMAT.format(hump_name, ele[0], hump_name)

    if_sql = if_sql.replace("[", "{")
    if_sql = if_sql.replace("]", "}")
    common_where_sql = COMMON_WHERE_FORMAT.format(if_sql)
    return common_where_sql


def generate_create_table_sql(table_name, columns, charset='utf8mb4', collate='utf8mb4_unicode_ci'):
    """
    生成创建表的SQL语句

    参数:
    table_name (str): 表名
    columns (dict): 包含列名和数据类型的字典，例如 {'column1': 'INT', 'column2': 'VARCHAR(255)'}
    charset (str): 字符编码，默认为utf8
    collate (str): 校对规则，默认为utf8_general_ci

    返回:
    str: CREATE TABLE语句
    """
    sql = f"CREATE TABLE IF NOT EXISTS {table_name} ("
    for column_name, column_type in columns.items():
        sql += f"{column_name} {column_type}, "
    sql = sql[:-2]  # 移除最后的逗号和空格
    sql += f") CHARACTER SET {charset} COLLATE {collate};"
    return sql


def _get_insert_columns(columns):
    return ','.join(columns)


def _get_insert_values(values):
    """
    根据values获取insert data
    :param values:
    :return:
    """
    ans = []
    for value in values:
        if hasattr(value, '__iter__') and type(value) != str:
            ans.append(','.join([v for v in value if v and isinstance(v, str)]))
        else:
            ans.append(value)
    return tuple(ans)


def get_insert_columns_and_values(data):
    return _get_insert_columns(data.keys()), _get_insert_values(data.values())


def _get_col_list(schema, table_name):
    conn = get_connection_by_schema(b'my pleasure lord', schema)
    cursor = conn.cursor()
    CHECK_COL_SQL_FORMAT = "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{}' AND TABLE_SCHEMA = '{}'"
    ITEM_FORMAT = "#[item.{}]"
    cursor.execute(CHECK_COL_SQL_FORMAT.format(table_name, schema))
    col_name_list = []
    item_name_list = []
    for ele in cursor.fetchall():
        col_name_list.append(ele[0])
        item_name_list.append(ITEM_FORMAT.format(transfer_database_name_to_hump(ele[0])))
    return col_name_list, item_name_list


def _batch_store_func(table_name, data_list, cursor):
    insertSqlFormat = 'insert into {}({}) values{}'
    columns = ','.join(data_list[0].keys())
    value_format = '({})'.format(','.join(["%s"] * len(data_list[0])))
    value_list = []
    for data in data_list:
        value_list.append(_get_insert_values(data.values()))
    insertSql = insertSqlFormat.format(table_name, columns, value_format)
    cursor.executemany(insertSql, value_list)