import pkuseg

from common.util.string_util import any_match, any_match_bool, extract_digit, find_all, \
    remove_special_symbols, has_chinese, is_chinese, split_text, handle_short_sentence, locate_two_word, \
    clean_string, CHINESE_MATCH


class TestStringUtil:
    def test_any_match(self):
        result = any_match("快乐池塘栽种了梦想就变成海洋", ["快乐", "梦想", "海洋", "人生", "纱布"])
        assert result == ["快乐", "梦想", "海洋"]

    def test_any_match_bool(self):
        result = any_match_bool("快乐池塘栽种了梦想就变成海洋", ["快乐", "人生", "纱布"])
        assert result is True

    def test_extract_digit(self):
        result = extract_digit("快乐1池塘栽5种了梦想就9变成海洋")
        assert result == "159"

    def test_find_all(self):
        positions = find_all("快了1池塘栽5种了梦想就9变成海洋", '了')
        assert positions == [1, 8]

    def test_remove_special_symbols(self):
        result = remove_special_symbols("快乐池塘\n\r\b栽\t种了梦想就变成海\n洋")
        assert result == "快乐池塘栽种了梦想就变成海洋"

    def test_has_chinese(self):
        result = has_chinese("dis当ogiosdg")
        assert result is True
        result = has_chinese("disogiosdg")
        assert result is False

    def test_is_chinese(self):
        result = is_chinese("好")
        assert result is True
        result = is_chinese("1")
        assert result is False
        result = is_chinese("a")
        assert result is False
        result = is_chinese("+")
        assert result is False

    def test_handle_short_sentence(self):
        result = handle_short_sentence([(0, 10), (11, 14), (15, 30), (31, 39)])
        assert result == [(0, 14), (15, 30), (31, 39)]

    def test_locate_two_word(self):
        assert locate_two_word("神经母细胞瘤神经的镂空设计符合4期神经母细胞瘤收到反馈就是刘佳分4期是快乐的感觉", "神经母细胞瘤", "4期") == (0, 15)
        assert locate_two_word("神经母细胞瘤神经的镂空设计符合4期神经母细胞瘤收到反馈就是刘佳分4期是快乐的感觉", "神经母细胞瘤", "4期", keep_order=False) == (17, 15)

    def test_clean_string(self):
        assert clean_string("=458*双方今后的健康+", left_match_list=[CHINESE_MATCH], right_match_list=[CHINESE_MATCH]) == "双方今后的健康"

