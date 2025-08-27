from base64 import b64decode

import pymysql
from common.constants.database_config import HOST_DICT, PASSWD_DICT
from common.util.encrypt_util import decrypt_aes


def get_connection_by_schema(key, schema, env='test'):
    passwd = decrypt_aes(key, b64decode(PASSWD_DICT[env])).decode()
    return pymysql.connect(host=HOST_DICT[env], port=4000, user="root", passwd=passwd,
                           db=schema, charset="utf8")


def get_mpi_connection(key, env='test'):
    """
    获取ncpcs_mpi库的连接
    :return: 数据库连接
    """
    passwd = decrypt_aes(key, b64decode(PASSWD_DICT[env])).decode()
    return pymysql.connect(host=HOST_DICT[env], port=4000, user="root", passwd=passwd,
                           db="ncpcs_mpi", charset="utf8")


def get_sibling_connection(key, env='test'):
    """
    获取ncpcs_sibling库的连接
    :return: 数据库连接
    """
    passwd = decrypt_aes(key, b64decode(PASSWD_DICT[env])).decode()
    return pymysql.connect(host=HOST_DICT[env], port=4000, user="root", passwd=passwd,
                           db="ncpcs_sibling", charset="utf8")


def get_nlp_connection(key, env='test'):
    """
    获取ncpcs_nlp库的连接
    :return: 数据库连接
    """
    passwd = decrypt_aes(key, b64decode(PASSWD_DICT[env])).decode()
    return pymysql.connect(host=HOST_DICT[env], port=4000, user="root", passwd=passwd,
                           db="ncpcs_nlp", charset="utf8")


def get_corpus_connection(key, env='test'):
    """
    获取nlp_corpus库的连接
    :return: 数据库连接
    """
    passwd = decrypt_aes(key, b64decode(PASSWD_DICT[env])).decode()
    return pymysql.connect(host=HOST_DICT[env], port=4000, user="root", passwd=passwd,
                           db="nlp_corpus", charset="utf8")


def get_tumor_connection(key, env='test'):
    """
    获取ncpcs_tumour库的连接
    :return: 数据库连接
    """
    passwd = decrypt_aes(key, b64decode(PASSWD_DICT[env])).decode()
    return pymysql.connect(host=HOST_DICT[env], port=4000, user="root", passwd=passwd,
                           db="ncpcs_tumor", charset="utf8")


def get_meiyin_db_connection(password):
    """
    获取meiyin db库的连接
    :return: 数据库连接
    """
    return pymysql.connect(host="172.31.11.153", port=3306, user="root", passwd=password,
                           db="ncpcs", charset="utf8")