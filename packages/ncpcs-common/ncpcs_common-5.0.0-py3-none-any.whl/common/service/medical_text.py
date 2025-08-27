import hashlib
import random
import re
from collections import Counter
from common.constants.level_dict import COLUMN_DICT, NAME_MAP
from common.entity.document import Document, DEFAULT_DOCUMENT_AVG_LEN
from common.entity.relation_key import RelationKey
from common.util.database_connection_util import get_corpus_connection
from common.util.date_util import current_time
from common.util.sql_util import store_by_batch
from common.util.string_util import cut_by_time

ORDER_TABLE_DICT = {
    "nc_admission_record": {
        "pageUuid": "",
        "orderSql": "",
        "tableUuid": "703000000"
    },
    "nc_discharge_record": {
        "pageUuid": "",
        "orderSql": "",
        "tableUuid": "707000000"
    },
    "nc_daily_disease_course": {
        "pageUuid": "706010000",
        "orderSql": " order by nc_disease_course_no ASC,sort_time ASC, nc_course_time ASC, nc_rid",
        "tableUuid": "706000000"
    },
    "nc_pathology_info": {
        "pageUuid": "711010000",
        "orderSql": " order by nc_pathology_no ASC,sort_time ASC, nc_report_time ASC, nc_rid",
        "tableUuid": "711000000"
    },
    "nc_imageology_exam": {
        "pageUuid": "713010000",
        "orderSql": " order by nc_exam_order ASC,nc_report_no ASC,sort_time ASC, nc_rid",
        "tableUuid": "713000000"
    },
    "nc_fist_disease_course": {
        "pageUuid": "705010000",
        "orderSql": " order by nc_disease_course_no ASC,sort_time ASC, nc_rid",
        "tableUuid": "705000000"
    },
    "nc_24hours_admission_discharge_info": {
        "pageUuid": "",
        "orderSql": "",
        "tableUuid": "708000000"
    },
    "nc_readmission_record": {
        "pageUuid": "",
        "orderSql": "",
        "tableUuid": "709000000"
    },
    "nc_death_record": {
        "pageUuid": "",
        "orderSql": "",
        "tableUuid": "712000000"
    }
}

GET_TEXT_SQL_FORMAT = "select {} from {} where nc_medical_institution_code = '{}' and nc_medical_record_no = '{}' and " \
                      "nc_discharge_time = '{}' and nc_hedge = 0 and nc_data_status != 99"

DATASET_ID_SCREEN_SQL_FORMAT = " and dataset_id = '{}'"


def do_nothing(val, admission_time, avg_len):
    return [(0, len(val), None)]


def generate_dataset_screen_sql(dataset_id, sql):
    if dataset_id:
        return sql + DATASET_ID_SCREEN_SQL_FORMAT.format(dataset_id)
    return sql


def extract_medical_record_text(cursor, medical_institution_code, medical_record_no, discharge_time, admission_time=None,
                        column_dict=COLUMN_DICT, avg_len=DEFAULT_DOCUMENT_AVG_LEN, dataset_id=None):
    if not admission_time:
        admission_time = discharge_time
    relation_key = RelationKey(medical_institution_code, medical_record_no, discharge_time, admission_time)
    return extract_medical_text(cursor, relation_key, column_dict, avg_len, do_nothing, dataset_id)


def extract_medical_record_text_by_entity_uuid(cursor, entity_uuid, nlp_db='ncpcs'):
    cursor.execute("select dataset_id, nc_key, nc_table_name, nc_column_name, nc_page from {}.nc_entity where nc_uuid = '{}'".format(nlp_db, entity_uuid))
    result = cursor.fetchone()
    if not result:
        return "Error: 实体【{}】不存在".format(entity_uuid)
    dataset_id, relation_key, table_name, column_name, page = result[0], result[1], result[2], result[3], result[4]
    relation_key_arr = relation_key.split("|")
    medical_institution_code, medical_record_no, discharge_time = relation_key_arr[0], relation_key_arr[1], relation_key_arr[2]
    discharge_time = discharge_time[:4] + '-' + discharge_time[4:6] + '-' + discharge_time[6:8] + " " + discharge_time[8:10] + ":" + discharge_time[10:12] + ":" + discharge_time[12:14]
    get_text_sql = GET_TEXT_SQL_FORMAT.format(column_name, table_name, medical_institution_code, medical_record_no, discharge_time)
    get_text_sql = generate_dataset_screen_sql(dataset_id, get_text_sql)
    table_uuid, page_uuid, get_text_sql = generate_order_sql(get_text_sql)
    get_text_sql = generate_limit_sql(get_text_sql, page-1)
    cursor.execute(get_text_sql)
    result = cursor.fetchone()
    if not result:
        return "Error: 实体【{}】上下文不存在".format(entity_uuid)

    content = result[0]
    document = Document(dataset_id, '', medical_institution_code,
                        medical_record_no, discharge_time, '', table_name,
                        column_name, table_uuid, page, page_uuid, 0,
                        len(content), content, '', None, '')
    return document


def extract_medical_record_text_cut_by_time(cursor, medical_institution_code, medical_record_no, discharge_time, admission_time=None,
                        column_dict=COLUMN_DICT, avg_len=DEFAULT_DOCUMENT_AVG_LEN, dataset_id=None):
    return extract_document_by(cursor, medical_institution_code, medical_record_no, discharge_time, admission_time, column_dict, avg_len, dataset_id)


def extract_document_by(cursor, medical_institution_code, medical_record_no, discharge_time, admission_time=None,
                        column_dict=COLUMN_DICT, avg_len=DEFAULT_DOCUMENT_AVG_LEN, dataset_id=None):
    if not admission_time:
        admission_time = discharge_time
    relation_key = RelationKey(medical_institution_code, medical_record_no, discharge_time, admission_time)
    return extract_medical_text(cursor, relation_key, column_dict, avg_len, cut_by_time, dataset_id)


def extract_document_list_by(dataset_id, medical_institution_code, medical_record_no, discharge_time, admission_time=None,
                           column_dict=COLUMN_DICT, avg_len=None, env="prod_test"):
    conn = get_corpus_connection(b'my pleasure lord', env)
    cursor = conn.cursor()
    if not admission_time:
        admission_time = discharge_time
    relation_key = RelationKey(medical_institution_code, medical_record_no, discharge_time, admission_time)
    return extract_medical_text(cursor, relation_key, column_dict, avg_len, dataset_id)


def extract_medical_text(cursor, relation_key, column_dict=COLUMN_DICT, avg_len=DEFAULT_DOCUMENT_AVG_LEN, cut_func=do_nothing,
                         dataset_id=None):
    document_list = []
    for table_name, column_list in column_dict.items():
        get_text_sql = GET_TEXT_SQL_FORMAT.format(','.join(column_list), table_name,
                                                  relation_key.medical_institution_code,
                                                  relation_key.medical_record_no, relation_key.discharge_time)
        get_text_sql = generate_dataset_screen_sql(dataset_id, get_text_sql)
        table_uuid, page_uuid, get_text_sql = generate_order_sql(get_text_sql)
        cursor.execute(get_text_sql)
        page = 1
        for ele in cursor.fetchall():
            for i, val in enumerate(ele):
                if not val:
                    continue
                column_name = column_list[i]
                content_list = cut_func(val, admission_time=relation_key.admission_time, avg_len=avg_len)
                for start_index, end_index, timeline in content_list:
                    content = val[start_index:end_index]
                    document = Document(dataset_id, '', relation_key.medical_institution_code,
                                        relation_key.medical_record_no,
                                        relation_key.discharge_time, relation_key.admission_time, table_name,
                                        column_name, table_uuid, page, page_uuid, start_index,
                                        start_index + len(content),
                                        content, '', timeline, '')
                    document_list.append(document)

            page += 1
    calculate_document_list(document_list)
    return document_list


def write_document_list_to_db(conn, document_list, table_name='nc_document'):
    cur_time = current_time()
    store_list = []
    for document in document_list:
        base_time, base_time_convert = '', ''
        base_time_type = None
        if document.timeline:
            base_time = document.timeline.base_time
            base_time_convert = document.timeline.base_time_convert
            base_time_type = document.timeline.base_time_type
        store_list.append({
            'dataset_id': document.dataset_id,
            'nc_uuid': document.uuid,
            'nc_add_account': '机器自动识别',
            'nc_upd_account': '机器自动识别',
            'nc_add_time': cur_time,
            'nc_upd_time': cur_time,
            'nc_global_id': document.global_id,
            'nc_key': document.package_relation_key(),
            'nc_medical_institution_code': document.medical_institution_code,
            'nc_medical_record_no': document.medical_record_no,
            'nc_discharge_time': document.discharge_time,
            'nc_admission_time': document.admission_time,
            'nc_table_name': document.table_name,
            'nc_column_name': document.column_name,
            'nc_source': '{}-{}'.format(NAME_MAP.get(document.table_name), NAME_MAP.get(document.column_name)),
            'nc_content': document.content,
            'nc_md5_sum': document.md5_sum,
            'nc_start_index': document.start_index,
            'nc_end_index': document.end_index,
            'nc_page': document.page,
            'nc_page_uuid': document.page_uuid,
            'nc_table_uuid': document.table_uuid,
            'nc_base_time': base_time,
            'nc_base_time_standard': base_time_convert,
            'nc_base_time_type': base_time_type,
        })
    store_by_batch(table_name, store_list, conn)


def get_document_by(cursor, document_uuid, dataset_id=None):
    document_list = get_document_list_by(cursor, [document_uuid], dataset_id)
    if document_list:
        return document_list[0]
    return None


def get_document_list_by(cursor, document_uuid_list, dataset_id=None):
    query_sql = ','.join(["'{}'".format(uuid) for uuid in document_uuid_list])
    get_document_list_sql = "select dataset_id, nc_uuid, nc_medical_institution_code, nc_medical_record_no," \
                            "nc_discharge_time, nc_admission_time, nc_table_name, nc_column_name, nc_table_uuid," \
                            "nc_page, nc_page_uuid, nc_start_index, nc_end_index, nc_content, nc_md5_sum, nc_global_id"\
                            " from nc_document where nc_uuid in ({})".format(query_sql)
    get_document_list_sql = generate_dataset_screen_sql(dataset_id, get_document_list_sql)
    cursor.execute(get_document_list_sql)
    document_list = []
    for ele in cursor.fetchall():
        document = Document(ele[0], ele[1], ele[2], ele[3], ele[4], ele[5], ele[6], ele[7], ele[8], ele[9], ele[10],
                            ele[11], ele[12], ele[13], ele[14])
        document.global_id = ele[14]
        document_list.append(document)

    return document_list


def give_global_id(cursor, document_list, source_table_name='nc_mpi_relation', dataset_id=None):
    sql = 'select nc_medical_institution_code, nc_medical_record_no, nc_discharge_time, nc_global_id from {} where 1=1'\
        .format(source_table_name)
    sql = generate_dataset_screen_sql(dataset_id, sql)
    cursor.execute(sql)
    relation_key_dict = {}
    for ele in cursor:
        relation_key = ele[0] + "|" + ele[1] + "|"
        if type(ele[2]) == str:
            relation_key += ele[2].replace("-", "").replace(" ", "").replace(":", "")
        else:
            relation_key += ele[2].strftime('%Y%m%d%H%M%S')
        relation_key_dict[relation_key] = ele[3]

    for document in document_list:
        relation_key = document.package_relation_key()
        if relation_key in relation_key_dict:
            document.global_id = relation_key_dict[relation_key]


def calculate_document_list(document_list):
    # 创建md5对象
    md5_hash = hashlib.md5()
    for document in document_list:
        # 使用正则表达式替换掉所有非中文、非英文、非数字字符
        cleaned_string = re.sub(r'[^\u4e00-\u9fffA-Za-z0-9]', '', document.content)
        if cleaned_string:
            md5_hash.update(cleaned_string.encode('utf-8'))
            document.md5_sum = md5_hash.hexdigest()
        key = document.medical_institution_code + document.medical_record_no + document.discharge_time + document.table_name + document.column_name + document.md5_sum
        md5_hash.update(key.encode('utf-8'))
        document.uuid = md5_hash.hexdigest()


def extract_all_relation_key(cursor, dataset_id=None):
    get_all_relation_key_sql = "select distinct nc_medical_institution_code, nc_medical_record_no, nc_discharge_time, " \
                               "nc_admission_time from nc_medical_record_first_page where nc_hedge = 0 and " \
                               "nc_data_status != 99"
    get_all_relation_key_sql = generate_dataset_screen_sql(dataset_id, get_all_relation_key_sql)
    get_all_relation_key_sql += " order by nc_rid"
    cursor.execute(get_all_relation_key_sql)
    relation_key_list = []
    for ele in cursor.fetchall():
        relation_key_list.append(
            RelationKey(ele[0], ele[1], ele[2].strftime('%Y-%m-%d %H:%M:%S'), ele[3].strftime('%Y-%m-%d %H:%M:%S')))

    return relation_key_list


def extract_relation_key_list_by_global_id(cursor, global_id, dataset_id=None):
    get_relation_key_list_by_global_id_sql = "select nc_medical_institution_code, nc_medical_record_no, " \
                                             "nc_discharge_time, nc_admission_time from nc_mpi_relation where " \
                                             "nc_global_id = '{}'".format(global_id)
    get_relation_key_list_by_global_id_sql = generate_dataset_screen_sql(dataset_id,
                                                                         get_relation_key_list_by_global_id_sql)
    get_relation_key_list_by_global_id_sql += " order by nc_admission_time"
    cursor.execute(get_relation_key_list_by_global_id_sql)
    relation_key_list = []
    for ele in cursor.fetchall():
        relation_key_list.append(
            RelationKey(ele[0], ele[1], ele[2].strftime('%Y-%m-%d %H:%M:%S'), ele[3].strftime('%Y-%m-%d %H:%M:%S')))
    return relation_key_list


def generate_order_sql(sql):
    for table_name, order_info in ORDER_TABLE_DICT.items():
        if sql.count(table_name):
            return order_info['tableUuid'], order_info['pageUuid'], sql + order_info['orderSql']
    return '', '', sql


def generate_limit_sql(sql, page):
    return sql + " limit {}, 1".format(page)


def sentence_count(sentence_list):
    count_dict = Counter(sentence_list)
    for sentence, count in sorted(count_dict.items(), key=lambda t: t[1], reverse=True):
        print(sentence, count)


def random_pick_relation_key(relation_key_dict, num_to_pick):
    selected_relation_key_list = []
    avg_to_pick = num_to_pick // len(relation_key_dict.keys())
    left_relation_key_list = []
    for _, relation_key_list in relation_key_dict.items():
        if len(relation_key_list) <= avg_to_pick:
            selected_relation_key_list.extend(relation_key_list)
        else:
            random_list = random.sample(relation_key_list, avg_to_pick)
            random_set = set(random_list)
            selected_relation_key_list.extend(random_list)
            left_relation_key_list.extend([relation_key for relation_key in relation_key_list
                                           if relation_key not in random_set])
    selected_relation_key_list.extend(
        random.sample(left_relation_key_list, num_to_pick - len(selected_relation_key_list)))
    return selected_relation_key_list