from common.constants.level_dict import ICCC3_CODE_NAME_DICT

from pypinyin import lazy_pinyin

from common.util.string_util import remove_special_symbols, remove_bracket


def handle_iccc3_name(name):
    name = remove_special_symbols(name)
    name = remove_bracket(name)
    return name


ICCC3_NAME_TO_CODE_DICT = {}
for code, name_list in ICCC3_CODE_NAME_DICT.items():
    for name in name_list:
        ICCC3_NAME_TO_CODE_DICT[handle_iccc3_name(name)] = code


def convert_iccc3_name_to_iccc3_code(iccc3_name):
    iccc3_name = handle_iccc3_name(iccc3_name)
    return ICCC3_NAME_TO_CODE_DICT.get(iccc3_name, None)


def convert_iccc3_name_to_iccc3_code_best(iccc3_name):
    iccc3_code = convert_iccc3_name_to_iccc3_code(iccc3_name)
    if iccc3_code:
        return iccc3_code

    iccc3_name = handle_iccc3_name(iccc3_name)
    for name, code in ICCC3_NAME_TO_CODE_DICT.items():
        if len(iccc3_name) < len(name):
            continue
        match = True
        for i, ch in enumerate(name):
            if ch != iccc3_name[i] and lazy_pinyin(ch) != lazy_pinyin(iccc3_name[i]):
                match = False
                break
        if match:
            return code

    return None


def get_large_group(iccc3_code):
    bound = iccc3_code.find(".")
    if bound == -1:
        bound = len(iccc3_code)
    return iccc3_code[: bound]


def extract_iccc3_name_large_group(iccc3_name):
    iccc3_code = convert_iccc3_name_to_iccc3_code_best(iccc3_name)
    if iccc3_code:
        return get_large_group(iccc3_code)
    return None

