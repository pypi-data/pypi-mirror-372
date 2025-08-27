from common.util.phone_util import clean


class TestPhoneUtil:
    def test_clean(self):
        assert clean("+  17710651612") == '17710651612'
        assert clean("+  177106516124") is None


