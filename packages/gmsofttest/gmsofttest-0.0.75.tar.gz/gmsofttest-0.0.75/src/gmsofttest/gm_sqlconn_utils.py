"""
Name : gm_sqlconn_utils.py
Author  : 写上自己的名字
Contact : 邮箱地址
Time    : 2021/3/22 15:52
Desc: 操作MYSQL数据库
"""
import os

import pymysql
import argparse

# 数据库连接信息
user = "root"
password = "mysql"
# ip地址
env20 = "192.168.2.20"
env15 = "192.168.2.15"
env2 = "192.168.2.2"

# show环境端口
show_xcj_sql_port = 31004
show_zcj_sql_port = 31404
show_inner_sql_port = 31604
show_analysis_sql_port = 31406

# test1环境和端口
test1_zcj_sql_port = 32404
test1_xcj_sql_port = 32004
test1_inner_sql_port = 32604
test1_syh_sql_port = 32904
test1_analysis_sql_port = 32406

# test2环境端口
test2_jydn_sql_port = 34704
test2_jydw_sql_port = 34804

# 使用15服务器的sql容器
test2_zcj_sql_port = 34404
test2_xcj_sql_port = 34004
test2_inner_sql_port = 34604

# test3环境和端口
test3_zcj_sql_port = 32004
test3_xcj_sql_port = 31004
test3_inner_sql_port = 24357
test3_syh_sql_port = 31904
test3_analysis_sql_port = 31406

# 达梦数据库



class OperateMysql(object):
    """快速连接gmsoft内部测试数据库"""

    def __init__(self, env=None, host=None):

        # 账号密码初始化
        self.user = user
        self.password = password
        self.host = host or os.getenv('host')
        self.env = env or os.getenv('env')

        # 数据库连接地址初始化, 端口初始化
        if (self.env == 'test2' and self.host == 'jydn') or (self.env == 'test2' and self.host == 'jydw'):
            # test2特殊处理,军医大内和军医大外使用ip应该是192.168.2.20
            self.env = env20
            self.jydn_port = test2_jydn_sql_port
            self.jydw_port = test2_jydw_sql_port
            try:
                self.jydn_conn = pymysql.connect(host=self.env, user=self.user,
                                                 password=self.password, port=self.jydn_port, charset='utf8mb4')
                self.jydw_conn = pymysql.connect(host=self.env, user=self.user,
                                                 password=self.password, port=self.jydw_port, charset='utf8mb4')
            except TimeoutError as e:
                print('连接超时：{}'.format(e))

            print("已创建jydn数据库连接,链接信息{}:{}".format(self.host, self.jydn_port))
            print("已创建jydw数据库连接,链接信息{}:{}".format(self.host, self.jydw_port))
        elif self.env == 'test2':
            # test2特殊处理，ip应该是192.168.2.15
            self.env = env15
            self.zcj_port = test2_zcj_sql_port
            self.xcj_port = test2_xcj_sql_port
            self.inner_port = test2_inner_sql_port
            try:
                self.zcj_conn = pymysql.connect(host=self.env, user=self.user,
                                                password=self.password, port=self.zcj_port, charset='utf8mb4')
                self.xcj_conn = pymysql.connect(host=self.env, user=self.user,
                                                password=self.password, port=self.xcj_port, charset='utf8mb4')
                self.inner_conn = pymysql.connect(host=self.env, user=self.user,
                                                  password=self.password, port=self.inner_port, charset='utf8mb4')
            except TimeoutError as e:
                print('连接超时：{}'.format(e))
        elif self.env == 'show' and self.host == 'zcj':
            self.env = env20
            self.zcj_port = show_zcj_sql_port
            self.zcj_conn = pymysql.connect(host=self.env, user=self.user, password=self.password, port=self.zcj_port, charset='utf8mb4')
        elif self.env == 'show' and self.host == 'xcj':
            self.env = env20
            self.xcj_port = show_xcj_sql_port
            self.xcj_conn = pymysql.connect(host=self.env, user=self.user, password=self.password, port=self.xcj_port, charset='utf8mb4')
        elif self.env == 'show' and self.host == 'analysis':
            self.env = env20
            self.analysis_port = show_analysis_sql_port
            self.analysis_conn = pymysql.connect(host=self.env, user=self.user, password=self.password, port=self.analysis_port, charset='utf8mb4')
        elif self.env == 'test1' and self.host == 'zcj':
            self.env = env20
            self.zcj_port = test1_zcj_sql_port
            self.zcj_conn = pymysql.connect(host=self.env, user=self.user, password=self.password, port=self.zcj_port, charset='utf8mb4')
        elif self.env == 'test1' and self.host == 'xcj':
            self.env = env20
            self.xcj_port = test1_xcj_sql_port
            self.xcj_conn = pymysql.connect(host=self.env, user=self.user, password=self.password, port=self.xcj_port, charset='utf8mb4')
        elif self.env == 'test1' and self.host == 'analysis':
            self.env = env20
            self.analysis_port = test1_analysis_sql_port
            self.analysis_conn = pymysql.connect(host=self.env, user=self.user, password=self.password, port=self.analysis_port, charset='utf8mb4')
        elif self.env == 'test3' and self.host == 'zcj':
            self.env = env2
            self.zcj_port = test3_zcj_sql_port
            self.zcj_conn = pymysql.connect(host=self.env, user=self.user, password=self.password, port=self.zcj_port, charset='utf8mb4')
        elif self.env == 'test3' and self.host == 'xcj':
            self.env = env2
            self.xcj_port = test3_xcj_sql_port
            self.xcj_conn = pymysql.connect(host=self.env, user=self.user, password=self.password, port=self.xcj_port, charset='utf8mb4')
        elif self.env == 'test3' and self.host == 'analysis':
            self.env = env2
            self.analysis_port = test3_analysis_sql_port
            self.analysis_conn = pymysql.connect(host=self.env, user=self.user, password=self.password, port=self.analysis_port, charset='utf8mb4')
        elif self.env == 'test3' and self.host == 'glxt':
            self.env = env2
            self.glxt_port = test3_inner_sql_port
            self.glxt_conn = pymysql.connect(host=self.env, user=self.user, password=self.password, port=self.analysis_port, charset='utf8mb4')
        elif self.env == 'test3' and self.host == 'syh':
            self.env = env2
            self.syh_port = test3_syh_sql_port
            self.syh_conn = pymysql.connect(host=self.env, user=self.user, password=self.password, port=self.analysis_port, charset='utf8mb4')

        else:
            print("未获取到env或host参数")



    def select_first_data(self, sql):
        """
        查询第一条数据
        """
        try:
            # 执行 sql 语句
            if self.host == 'zcj':
                with self.zcj_conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    cursor.execute(sql)
                    first_data = cursor.fetchone()
                    return first_data
            elif self.host == 'xcj':
                with self.xcj_conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    cursor.execute(sql)
                    first_data = cursor.fetchone()
                    return first_data
            elif self.host == 'analysis':
                with self.analysis_conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    cursor.execute(sql)
                    first_data = cursor.fetchone()
                    return first_data
            elif self.host == 'glxt':
                with self.glxt_conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    cursor.execute(sql)
                    first_data = cursor.fetchone()
                    return first_data
            elif self.host == 'syh':
                with self.syh_conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    cursor.execute(sql)
                    first_data = cursor.fetchone()
                    return first_data
        finally:
            if hasattr(self, 'xcj_conn'):
                self.xcj_conn.close()
            if hasattr(self, 'zcj_conn'):
                self.zcj_conn.close()
            if hasattr(self, 'analysis_conn'):
                self.analysis_conn.close()
            if hasattr(self, 'glxt_conn'):
                self.glxt_conn.close()
            if hasattr(self, 'syh_conn'):
                self.syh_conn.close()

    def select_all_data(self, sql):
        """
        查询所有数据
        :param sql:
        :return:
        """
        try:
            # 执行 sql 语句
            if self.host == 'zcj':
                with self.zcj_conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    cursor.execute(sql)
                    data = cursor.fetchall()
                    return data
            elif self.host == 'xcj':
                with self.xcj_conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    cursor.execute(sql)
                    data = cursor.fetchall()
                    return data
            elif self.host == 'analysis':
                with self.analysis_conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    cursor.execute(sql)
                    data = cursor.fetchall()
                    return data
            elif self.host == 'glxt':
                with self.glxt_conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    cursor.execute(sql)
                    data = cursor.fetchall()
                    return data
            elif self.host == 'syh':
                with self.syh_conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    cursor.execute(sql)
                    data = cursor.fetchall()
                    return data
        finally:
            if hasattr(self, 'xcj_conn'):
                self.xcj_conn.close()
            if hasattr(self, 'zcj_conn'):
                self.zcj_conn.close()
            if hasattr(self, 'analysis_conn'):
                self.analysis_conn.close()
            if hasattr(self, 'glxt_conn'):
                self.glxt_conn.close()
            if hasattr(self, 'syh_conn'):
                self.syh_conn.close()

    def delete_data(self, sql):
        """
        查询所有数据
        :param host:  zcj、xcj
        :param sql: SQL查询
        :return:
        """
        try:
            conn = getattr(self, self.host + '_conn')
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:  # 参数化获取
                sql_list = sql.split(';')
                for exe_sql in sql_list:  # 支持多条执行，以;分隔SQL
                    if exe_sql:  # 去掉列表数据为空的项
                        exe_sql = exe_sql.strip() + ';'
                        cursor.execute(exe_sql)
                        conn.commit()
            # if self.host == 'zcj':
            #     with self.zcj_conn.cursor(pymysql.cursors.DictCursor) as zcj_cursor:
            #         sql_list = sql.split(';')
            #         for exe_sql in sql_list:  # 支持多条执行，以;分隔SQL
            #             if exe_sql:  # 去掉列表数据为空的项
            #                 exe_sql = exe_sql.strip() + ';'
            #                 zcj_cursor.execute(exe_sql)
            #                 self.zcj_conn.commit()
            # elif self.host == 'xcj':
            #     with self.xcj_conn.cursor(pymysql.cursors.DictCursor) as xcj_cursor:
            #         sql_list = sql.split(';')
            #         for exe_sql in sql_list:
            #             if exe_sql:
            #                 exe_sql = exe_sql.strip() + ';'
            #                 xcj_cursor.execute(exe_sql)
            #                 self.xcj_conn.commit()
            # elif self.host == 'analysis':
            #     with self.analysis_conn.cursor(pymysql.cursors.DictCursor) as analysis_cursor:
            #         sql_list = sql.split(';')
            #         for exe_sql in sql_list:
            #             if exe_sql:
            #                 exe_sql = exe_sql.strip() + ';'
            #                 analysis_cursor.execute(exe_sql)
            #                 self.analysis_conn.commit()
            #         print(f"删除条数：{analysis_cursor.rowcount}")
        except TypeError as e1:
            print(f"SQL执行时类型错误！请检查: {e1}")
            # 根据host的值来决定调用哪个连接的rollback方法
            if self.host == 'zcj':
                self.zcj_conn.rollback()
            elif self.host == 'xcj':
                self.xcj_conn.rollback()
            elif self.host == 'analysis':
                self.analysis_conn.rollback()
            elif self.host == 'glxt':
                self.glxt_conn.rollback()
            elif self.host == 'syh':
                self.syh_conn.rollback()
        except Exception as e:
            # 捕获所有其他异常，并回滚相应的连接
            print(f"执行SQL时发生错误：{e}")
            if self.host == 'zcj':
                self.zcj_conn.rollback()
            elif self.host == 'xcj':
                self.xcj_conn.rollback()
            elif self.host == 'analysis':
                self.analysis_conn.rollback()
            elif self.host == 'glxt':
                self.glxt_conn.rollback()
            elif self.host == 'syh':
                self.syh_conn.rollback()
        finally:
            if hasattr(self, 'xcj_conn'):
                self.xcj_conn.close()
            if hasattr(self, 'zcj_conn'):
                self.zcj_conn.close()
            if hasattr(self, 'analysis_conn'):
                self.analysis_conn.close()
            if hasattr(self, 'glxt_conn'):
                self.glxt_conn.close()
            if hasattr(self, 'syh_conn'):
                self.syh_conn.close()

    def conn_close(self):
        # 关闭数据库连接
        try:
            if hasattr(self, 'xcj_conn'):
                self.xcj_conn.close()
            if hasattr(self, 'zcj_conn'):
                self.zcj_conn.close()
            if hasattr(self, 'jydn_conn'):
                self.jydn_conn.close()
            if hasattr(self, 'jydw_conn'):
                self.jydw_conn.close()
            if hasattr(self, 'syh_conn'):
                self.syh_conn.close()
            if hasattr(self, 'inner_conn'):
                self.inner_conn.close()
            if hasattr(self, 'xcj_cursor'):
                self.xcj_cursor.close()
            if hasattr(self, 'zcj_cursor'):
                self.zcj_cursor.close()
            if hasattr(self, 'jydn_cursor'):
                self.jydn_cursor.close()
            if hasattr(self, 'jydw_cursor'):
                self.jydw_cursor.close()
            if hasattr(self, 'syh_cursor'):
                self.syh_cursor.close()
            if hasattr(self, 'inner_cursor'):
                self.inner_cursor.close()
            if hasattr(self, 'analysis_cursor'):
                self.analysis_cursor.close()
        except AttributeError as e:
            print("数据库连接已关闭!!!")

class DMSql(object):

    pass

    # def __init__(self):
    #     CONN_STR = (
    #         r'DRIVER={DM8 ODBC DRIVER};'
    #         r'SERVER=192.168.2.32:34994;'  # 服务器地址
    #         r'DATABASE=DJC_EXPERT;'  # 数据库名
    #         r'UID=djc_expert;'  # 用户名
    #         r'PWD=111111111;'  # 密码
    #     )
    #     self.conn = pyodbc.connect(CONN_STR)
    #     self.cursor = self.conn.cursor()
    #
    # def __enter__(self):
    #     return self
    #
    # def __exit__(self, exc_type, exc_val, exc_tb):
    #     self.conn.close()
    #     print('关闭达梦数据库连接！！！')
    #
    # def query(self, sql: str, params=None):
    #     try:
    #         self.cursor.execute(sql, params)
    #         result = self.cursor.fetchall()
    #         return result
    #     except Exception as e:
    #         print(f"An error occurred:{e}")
    #         return []
    #
    # def delete(self, sql):
    #     try:
    #         self.cursor.execute(sql)
    #         self.cursor.commit()
    #         # result = self.cursor.fetchone()
    #         # return result
    #     except Exception as e:
    #         print(f"An error occurred:{e}")
    #         return []
    #
    # def update(self, sql):
    #     try:
    #         self.cursor.execute(sql)
    #         self.cursor.commit()
    #         # result = self.cursor.fetchone()
    #         # return result
    #     except Exception as e:
    #         print(f"An error occurred:{e}")
    #         return []
    #
    # def count(self, sql):
    #     try:
    #         self.cursor.execute(sql)
    #         result = self.cursor.fetchall()
    #         if len(result) == 1 and len(result[0]) == 1:
    #         # 如果结果集只有一个元素，返回那个元素
    #             return result[0][0]
    #     except Exception as e:
    #         print(f"An error occurred:{e}")
    #         return []


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Operate MySQL for gmsoft internal testing')
    parser.add_argument('--env', type=str, help='测试环境的标识')
    parser.add_argument('--host', type=str, help='数据库主机地址')
    args = parser.parse_args()

    om = OperateMysql(env=args.env, host=args.host)
    sql = """
    delete  from zcj_finance.zcj_guarantee_apply where id = 1315787791032147968"""
    print(om.delete_data(sql))


