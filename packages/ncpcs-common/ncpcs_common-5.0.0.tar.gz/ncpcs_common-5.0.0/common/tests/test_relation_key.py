from common.entity.relation_key import RelationKey
from common.util.date_util import current_time


class TestRelationKey:
    def test_relation_key(self):
        relation_key = RelationKey('test', 'sd', current_time())
        print(relation_key)