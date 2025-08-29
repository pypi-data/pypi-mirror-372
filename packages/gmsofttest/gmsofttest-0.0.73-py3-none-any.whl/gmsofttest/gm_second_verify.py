"""
Name : gm_second_verify.py
Author  : 写上自己的名字
Contact : 邮箱地址
Time    : 2023-11-15 20:25
Desc:
"""

import json
def second_verify(resp, login_org):
	"""第一次验证不通过时获取返回值，并传入待登录的单位名称，返回EMPLOEE"""
	try:
		identities = json.loads(resp.text).get('identities')
		identities_id = [x['id'] for x in identities if x['name'] == str(login_org)][0]
		return identities_id
	except IndexError as e:
		print(f"二次验证未获取到单位名称,请传入单位名称。当前单位名称：{login_org}")



