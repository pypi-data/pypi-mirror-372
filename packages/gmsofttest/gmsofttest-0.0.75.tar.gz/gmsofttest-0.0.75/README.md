# Gmtestplugin

    大家软件Python插件定制私有库开发项目

## change logs
```
v0.0.75
	gm_oauth_utils.py增加获取公告访问码方法get_license_key(domain: str, refresh_key: str, is_print=None) -> str
```



```
v0.0.73-74
	增加gm_oauth_utils.py，获取第三方登录auth
```





```
v0.0.72
	支撑test3环境数据库连接和登录
```



```
v0.0.71
    修复gm_login_into_utils.py类bug
```

```
v0.0.70
    gm_login_into_utils.py类增加getattr(LoginDomain, login_domain).value
```

```
v0.0.69
    增加翻译工具类，调用的是阿里云api
    pip install alibabacloud_alimt20181012 alibabacloud_credentials alibabacloud_tea_openapi alibabacloud_tea_util
```

```
v0.0.68
    增加gmsoft_login_into函数
```


```
v0.0.61
    增加locust_login函数，支撑locust登录
```
```
v0.0.60
    修复二次验证bug
```
```
v0.0.59
    处理多次验证时未兼容问题
```
```
v0.0.57 
    处理多次验证时未兼容问题
```
```
v0.0.56 
    处理多次验证时未兼容问题
```
V0.0.55
    2024-08-06 gm_login2_utils工具類增加login方法
v0.0.54
```
    2024-07-04  增加gm_exec_python_def.py方法，可通过调用此方法执行python相关函数

```

v0.0.53



v0.0.52 

```
    randomdata_utils中getStr支撑最大长度5000

```

v0.0.51 

```
    打包gm_sucreditcode_utils.py



```

V0.0.49

    适配已有的DMSql的引入，DMSql类直接返回pass
V0.0.48

    2.19的unix服务器有问题，取消import pyodbc

V0.0.46

    增加文件上传

v0.0.45
    增加gm_format_parmas工具，支撑批量替换URL中{}参数
v0.0.44
    OperateMysql()类的delete_data()函数支持多条SQL语句

V0.0.42
    OperateMysql()类支撑通过Pytest环境变量调用

V0.0.39
    1：修复登录行采家的登录问题
    2：修复触发二次手机登录时未处理逻辑的问题

V0.0.19
   sql工具类增加达梦数据库ODBC（test1）

V0.0.16
   1、增加登录封装gm_login2_utils.py
   2、优化second_verify.py

V0.0.15 
   增加二次验证读取identities的值

V0.0.14
    gm_assert_utils工具增加按列表分别取列表中的值并进行验证gm_assert_list_anyone_in

v0.0.13
  gm_assert_utils工具增加字典类型验证 gm_assert_dict_iseuqal

V0.0.12
  gm_assert_utils工具增加 gm_assert_lists_isinclude和gm_assert_lists_iseuqals验证

V0.0.11
  增加analysis库
v0.0.10
  优化部分内容
v0.0.9
  demo演示

v0.0.8
 修改gm_prase_response的调用名称为gm_extract_json
 增加gm_sucreditcode_utils，用于生成企业社会信用代码

v0.0.6 
 修改gm_request_utils的请求参数verfiy的默认值,由NONE调整成False

v0.0.5

 增加gm_assert_utils：assert验证封装

 增加gm_excel_utils: excel工具类封装

 增加gm_stock_enum: 增加采购数据枚举类

 增加gm_yaml_process_utils: 增加yaml工具类

 增加gm_request_utils：增加requests请求封装类	

v0.0.4
  增加gm_prase_response.py: 解析request请求返回值
  增加gm_timestamp.py： 生成测试的时间戳

v0.0.3 
  优化目录结构
  china_address.py 
  getrandomdata.py -- 生成随机数据
  mysqlconn.py -- 数据库连接池
v0.0.2 
  try something

v0.0.1 
  mydemo-package 实验项目