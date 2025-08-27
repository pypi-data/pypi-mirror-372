import re


def clean_phone(phone):
    if not phone:
        return None
    pattern = r"\d{11,}"
    match = re.search(pattern, phone)
    phone = None
    if match and len(match.group()) == 11:
        phone = match.group()
    return phone
