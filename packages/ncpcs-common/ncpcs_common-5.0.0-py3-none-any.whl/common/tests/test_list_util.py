from common.util.list_util import get_string_list_total_length


class TestListUtil:
    def test_get_string_list_total_length(self):
        l = get_string_list_total_length(['深爱着的', '人', '不会犯错'])
        assert l == 9
