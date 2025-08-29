"""
Name : gm_format_params.py
Author  : 写上自己的名字
Contact : 邮箱地址
Time    : 2024-03-20 13:29
Desc:
"""


def format_url(url_template, params):
	"""
	格式化URL，替换其中的命名占位符。

	参数:
	url_template (str): 包含命名占位符的URL模板，例如'{itemNo}/{packageNo}'。
	params (dict): 包含占位符及其对应值的字典，例如{'itemNo': '12345', 'packageNo': '67890'}。

	返回:
	str: 格式化后的URL。
	"""
	return url_template.format(**params)


if __name__ == '__main__':
	params = {
		'itemNo': 'CQS23C00001',
		'packageNo': '1',
		# 可以添加更多参数，例如 'anotherParam': 'value'
	}
	print(format_url('https://www.gpwbeta.com/gwebsite/inner/query/bid-guarantee/{itemNo}/{packageNo}', params))