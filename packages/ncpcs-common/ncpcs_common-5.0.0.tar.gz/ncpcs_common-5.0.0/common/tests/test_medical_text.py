import collections
import uuid

from common.service.medical_text import extract_all_relation_key, extract_medical_text, sentence_count, \
    random_pick_relation_key, extract_document_by, extract_medical_record_text_by_entity_uuid
from common.util.csv_util import write_csv
from common.util.database_connection_util import get_connection_by_schema
from common.util.date_util import current_time
from common.util.sql_util import store_by_batch
from common.util.string_util import cut_by_time


class TestSqlUtil:
    def test_extract_all_relation_key(self):
        pass
        # conn = get_tumour_stage_connection(b'')
        # cursor = conn.cursor()
        # relation_key_list = extract_all_relation_key(cursor)
        # for relation_key in relation_key_list:
        #     print(relation_key)

    def test_extract_medical_text(self):
        corpus_conn = get_connection_by_schema(b'my pleasure lord', 'nlp_corpus')
        cursor = corpus_conn.cursor()

        # doc_list = extract_document_by(cursor, '1011001', '854966', '2019-03-15 15:24:00', dataset_id='Dataset20240914rms001')
        doc = extract_medical_record_text_by_entity_uuid(cursor, "6402a865abebe9a2ee635eb1", 'ncpcs_nlp')

        print(doc.content)

    def test_sentence_count(self):
        sentence_list = ["测试", "测试", "四大皆空", "第三方i哦", "第三方i哦", "第三方i哦"]
        sentence_count(sentence_list)

    def test_random_pick_relation_key(self):
        conn = get_connection_by_schema(b'')
        cursor = conn.cursor()
        all_relation_key_list = extract_all_relation_key(cursor)
        relation_key_dict = collections.defaultdict(list)
        for relation_key in all_relation_key_list:
            relation_key_dict[relation_key.medical_institution_code].append(relation_key)
        assert len(random_pick_relation_key(relation_key_dict, 500)) == 500
        assert len(random_pick_relation_key(relation_key_dict, 37)) == 37

