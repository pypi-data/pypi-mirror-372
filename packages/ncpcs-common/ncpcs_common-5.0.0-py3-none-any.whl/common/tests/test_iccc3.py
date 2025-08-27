from common.service.iccc3 import convert_iccc3_name_to_iccc3_code, convert_iccc3_name_to_iccc3_code_best, \
    get_large_group, extract_iccc3_name_large_group


class TestIccc3Util:
    def test_convert_iccc3_name_to_iccc3_code(self):
        result = convert_iccc3_name_to_iccc3_code("结肠癌")
        assert result == 'Ⅺ.f2'
        result = convert_iccc3_name_to_iccc3_code("恶形黑色素瘤")
        assert result != 'Ⅺ.d'

    def test_convert_iccc3_name_to_iccc3_code_best(self):
        result = convert_iccc3_name_to_iccc3_code_best("恶形黑色素瘤")
        assert result == 'Ⅺ.d'

        result = convert_iccc3_name_to_iccc3_code_best("前体细胞白雪病")
        assert result == 'Ⅰ.a1'

    def test_get_large_group(self):
        result = get_large_group("Ⅰ.a1")
        assert result == 'Ⅰ'

    def test_extract_iccc3_name_large_group(self):
        result = extract_iccc3_name_large_group("前体细胞白雪病")
        assert result == 'Ⅰ'

