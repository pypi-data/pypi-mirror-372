"""
Name : gm_demo_project.py
Author  : 写上自己的名字
Contact : 邮箱地址
Time    : 2023-11-15 10:13
Desc:
"""

def gm_verify_true(mylist):
	my_result = all(mylist)
	return my_result

def gm_verify_any(mylist):
	my_result = any(mylist)
	return my_result


if __name__ == '__main__':
	print(gm_verify_true([False, '2']))
	print(gm_verify_any([False, '2']))


