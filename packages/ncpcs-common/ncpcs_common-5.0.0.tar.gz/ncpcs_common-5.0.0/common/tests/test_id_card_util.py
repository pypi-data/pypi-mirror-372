from common.util.id_card_util import validate


class TestIdCardUtil:
    def test_validate(self):
        assert validate("111111111111111") == False
        assert validate("111111111111111111") == False
        assert validate("350301199609270718") == True