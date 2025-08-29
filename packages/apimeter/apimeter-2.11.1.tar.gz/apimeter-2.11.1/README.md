# ApiMeter

*ApiMeter* is a simple & elegant, yet powerful HTTP(S) API testing framework, base on HttpRunner v2.5.9. Enjoy! ✨ 🚀 ✨


## Document

1. ApiMeter 用户使用文档：[https://zhuifengshen.github.io/APIMeter/](https://zhuifengshen.github.io/APIMeter/)
2. ApiMeter PYPI发布版本：[https://pypi.org/project/apimeter](https://pypi.org/project/apimeter)


## Usage
```python
pip install apimeter  # 安装，安装后可用内置命令：apimeter、hrun、apilocust
apimeter /path/to/api  # 完整生成报告
apimeter /path/to/api --skip-success  # 报告忽略成功用例数
```


## 支持新特性
1. 自定义函数的参数支持引用全局变量
```yaml
- eq: 
    - ${validate_token_v2(content)}
    - true
```    

2. 自定义函数的参数支持引用全局变量的链式取值
```yaml
- eq: 
    - ${validate_token(content.token)}
    - true
```    

3. 自定义函数的参数支持引用自定义变量链式取值
```yaml
- eq: 
    - ${validate_token($resp.token)}
    - true
```    

4. 自定义函数支持列表参数解析
```yaml
sign: ${get_sign_v2([$device_sn, $os_platform, $app_version])}
```

5. 自定义函数支持字典对象参数解析
```
sign: "${get_sign_v3({device_sn: $device_sn, os_platform: $os_platform, app_version: $app_version})}"
``` 

6. 自定义函数支持复杂嵌套对象参数解析
```yaml
- eq:
    - "${check_nested_list_fields_not_empty(content, {list_path: productList, nested_list_field: sku, check_fields: [id, amount, origin_amount, currency, account_number, duration]})}"
    - True
```    

7. 自定义函数支持链式参数｜通配符参数｜正则表达式参数解析
```yaml
- eq:
    - ${check(content, data.product.purchasePlan.*.sku.*.id, data.product.purchasePlan.*.sku.*.amount, data.product.purchasePlan.*.sku.*.origin_amount, data.product.purchasePlan.*.sku.*.currency, data.product.purchasePlan.*.sku.*.account_number, data.product.purchasePlan.*.sku.*.duration)}
    - True
- eq:
    - ${check(content, '_url ~= ^https?://[^\s/$.?#].[^\s]*$', 'default_currency =* [USD, CNY]', 'default_sku @= dict', 'sku @= list', 'product @= dict')} # 一次性校验所有字段
    - True    
```

8. 内置全局变量支持转义

全局变量可以在用例中直接使用、作为函数参数入参，同时支持链式取值，引用时无需添加前缀：$。另外支持全局变量转义功能，使用反斜杠'\'将全局变量名作为字面量字符串使用。

    - content / body / text / json
    - status_code
    - cookies
    - elapsed
    - headers
    - encoding
    - ok
    - reason
    - url
```yaml
# 使用示例
status_code
content
content.person.name.first_name
body
body.token
headers
"headers.content-type"
cookies
elapsed.total_seconds

# 特殊情况：当数据字段与全局变量同名时，支持使用反斜杠'\'转义全局变量，将其作为字面量字符串处理
- eq:
    - ${check_data_not_null(content.data.linesCollectList.data,2,lines,\content)}
    - True
# 这里 \content 会被解析为字符串 "content"，而不是全局变量 content 的值
# 支持转义所有全局变量：\content, \body, \text, \json, \status_code, \headers, \cookies, \encoding, \ok, \reason, \url
```

9. 支持自定义脚本校验方式，支持任意python脚本（基于assert校验理念，异常即失败，符合开发直觉）
```yaml
teststeps:
- name: 示例
  request:
    url: /api/example
    method: GET
  script:
    - assert status_code == 200
    # 使用assert语句，支持变量引用和链式取值
    - assert content.success is 
    # 使用自定义函数，异常即失败，否则为通过
    - ${custom_validation_function($token)}
    # 使用 YAML 的 | 语法编写多行脚本
    - |
        if status_code == 200:
            assert content.success is True
        elif status_code == 400:
            assert content.error_code is not None
        else:
            assert False, f"Unexpected status code: {status_code}"
    # 循环校验
    - |
        for item in content.items:
            assert item.get("id") is not None
            assert item.get("name") is not None
```

10. HTML测试报告支持内容智能折叠和JSON数据树形展示，提升大数据量场景下测试报告的可读性和查看体验
  - 当内容超过10行时自动进行折叠显示
  - 支持JSON数据、Python对象数据树形结构展示
  - 提供彩色语法高亮和节点级别的展开/折叠交互
  - 应用于所有关键数据字段
    - Request body（请求体）
    - Response body（响应体）
    - Request headers（请求头）
    - Response headers（响应头）
    - Validator expect value（校验器期望值）
    - Validator actual value（校验器实际值）
    - Script（自定义脚本）
    - Output（脚本执行结果）
  

## Validate核心用法

### 1、校验器支持两种格式
```yaml
- {"check": check_item, "comparator": comparator_name, "expect": expect_value}  # 一般格式
- comparator_name: [check_item, expect_value]  # 简化格式
```

### 2、支持自定义校验器
对于自定义的校验函数，需要遵循三个规则：
- (1)自定义校验函数需放置到debugtalk.py中;
- (2)参数有两个：第一个为原始数据，第二个为原始数据经过运算后得到的预期结果值;
- (3)在校验函数中通过assert将实际运算结果与预期结果值进行比较;
```yaml
# 用例
- test:
    name: get token
    request:
        url: http://127.0.0.1:5000/api/get-token
        method: GET
    validate:
        - {"check": "status_code", "comparator": "eq", "expect": 200}
        - {"check": "status_code", "comparator": "sum_status_code", "expect": 2}

# 自定义校验器
def sum_status_code(status_code, expect_sum):
    """ sum status code digits
        e.g. 400 => 4, 201 => 3
    """
    sum_value = 0
    for digit in str(status_code):
        sum_value += int(digit)
    assert sum_value == expect_sum
```

### 3、支持在校验器中引用变量
在结果校验器validate中，check和expect均可实现实现变量的引用；而引用的变量，可以来自四种类型：
- （1）当前teststep中定义的variables，例如expect_status_code
- （2）当前teststep中提取（extract）的结果变量，例如token
- （3）当前测试用例集testset中，先前teststep中提取（extract）的结果变量
- （4）当前测试用例集testset中，全局配置config中定义的变量
```yaml
- test:
    name: get token
    request:
      url: http://127.0.0.1:5000/api/get_token
      method: GET
    variables:
      - expect_status_code: 200
      - token_len: 16
    extract:
      - token: content.token
    validate:
      - {"check": "status_code", "comparator": "eq", “expect": "$expect_status_code"}
      - {"check": "content.token", "comparator": "len_eq", "expect": "$token_len"}
      - {"check": "$token", "comparator": "len_eq", "expect": "$token_len"}
```
基于引用变量的特效，可实现更灵活的自定义函数校验器
```yaml
- test:
    name: get token
    request:
        url: http://127.0.0.1:5000/api/get-token
        method: GET
    validate:
        - {"check": "status_code", "comparator": "eq", "expect": 200}
        - {"check": "${sum_status_code(status_code)}", "comparator": "eq", "expect": 2}

# 自定义函数
def sum_status_code(status_code):
    """ sum status code digits
        e.g. 400 => 4, 201 => 3
    """
    sum_value = 0
    for digit in str(status_code):
        sum_value += int(digit)
    return sum_value
```

### 4、支持正则表达式提取结果校验内容
假设接口的响应结果内容为LB123abcRB789，那么要提取出abc部分进行校验：
```yaml
- test:
    name: get token
    request:
        url: http://127.0.0.1:5000/api/get-token
        method: GET
    validate:
        - {"check": "LB123(.*)RB789", "comparator": "eq", "expect": "abc"}
```


### 5、内置校验器
| Comparator       | Description                    | A(check), B(expect)          | Examples                                     |
|------------------|--------------------------------|------------------------------|----------------------------------------------|
| eq               | value is equal                 | A == B                       | 9 eq 9                                       |
| lt               | less than                      | A < B                        | 7 lt 8                                       |
| le               | less than or equals            | A <= B                       | 7 le 8, 8 le 8                               |
| gt               | greater than                   | A > B                        | 8 gt 7                                       |
| ge               | greater than or equals         | A >= B                       | 8 ge 7, 8 ge 8                               |
| ne               | not equals                     | A != B                       | 6 ne 9                                       |
| str_eq           | string equals                  | str(A) == str(B)             | 123 str_eq '123'                             |
| len_eq, count_eq | length or count equals         | len(A) == B                  | 'abc' len_eq 3, [1,2] len_eq 2               |
| len_gt, count_gt | length greater than            | len(A) > B                   | 'abc' len_gt 2, [1,2,3] len_gt 2             |
| len_ge, count_ge | length greater than or equals  | len(A) >= B                  | 'abc' len_ge 3, [1,2,3] len_ge 3             |
| len_lt, count_lt | length less than               | len(A) < B                   | 'abc' len_lt 4, [1,2,3] len_lt 4             |
| len_le, count_le | length less than or equals     | len(A) <= B                  | 'abc' len_le 3, [1,2,3] len_le 3             |
| contains         | contains                       | [1, 2] contains 1            | 'abc' contains 'a', [1,2,3] len_lt 4         |
| contained_by     | contained by                   | A in B                       | 'a' contained_by 'abc', 1 contained_by [1,2] |
| type_match       | A is instance of B             | isinstance(A, B)             | 123 type_match 'int'                         |
| regex_match      | regex matches                  | re.match(B, A)               | 'abcdef' regex 'a|w+d'                       |
| startswith       | starts with                    | A.startswith(B) is True      | 'abc' startswith 'ab'                        |
| endswith         | ends with                      | A.endswith(B) is True        | 'abc' endswith 'bc'                          |


## 用例 SKIP 机制

1. 无条件跳过：skip: skip this test unconditionally
2. 自定义函数返回True：skipIf: ${skip_test_in_production_env()}
3. 自定义函数返回False：skipUnless: ${skip_test_in_production_env()}

```yaml
# 支持API层
name: subscriptionList_查询
skip: 用例参数变量待适配
base_url: ${get_config(youcloud,graphql_url)}
variables:
  user: ${get_config(youcloud,v0_user)}
  pwd: ${get_config(youcloud,v0_pwd)}
  sessionId: ${get_login(youcloud,$user,$pwd,youcloud_token)}
request:
  method: POST
  url: /graphql
  headers:
    Content-Type: application/json; charset=utf-8
    Accept-Language: zh
    x-operation-name: subscriptionList
  cookies:
    sessionId: $sessionId
  json:
    operationName: subscriptionList
    query: query subscriptionList{ subscriptionList { brand { app_id, name } } }
    variables: {}
validate:
- eq:
  - status_code
  - 200


# 支持用例层
config:
  name: subscriptionList 查询测试
teststeps:
- name: 执行 subscriptionList 查询
  skipIf: ${skip_test_in_production_env()}
  api: api/youcloud/query_subscriptionList_api.yml
  extract:
  - data: content.data
  validate:
  - eq:
    - status_code
    - 200
```


## 常见注意事项
```yaml
# 日志输出需要指定绝对路径或相对路径，不能指定单独一个文件名（文件可以未创建）
hrun --log-level debug --log-file ./test.log   api/youcloud/query_product_api.yml

# 自定义函数使用了字典参数，需要使用双引号包围，避免YAML解析器会将其误认为是字典定义。例如：
sign: "${get_sign_v3({device_sn: $device_sn, os_platform: $os_platform, app_version: $app_version})}"

# 两种转义方式
1. $ 符号转义
$$
2. 全局变量转义
\global_variable，例如：\content

# 一键打包发布，更多内容参考 scripts
make release-patch  MESSAGE="支持自动化打包发布，发布版本v2.8.4" # 自动累积小版本
make quick-release VERSION=2.85 MESSAGE="完善使用说明文档，发布版本v2.8.5" # 跳过单元测试
```


## Development
```python
# 本地开发与运行
poetry install  # 拉取代码后安装依赖
poetry run python -m apimeter /path/to/api  # 完整生成报告
poetry run python -m apimeter /path/to/api --skip-success  # 报告忽略成功用例数据
python -m apimeter -h # 查看使用指南


# 测试运行
python -m unittest discover # 运行所有单元测试
python -m unittest tests/test_context.py # 运行指定测试文件
python -m unittest tests.test_api.TestHttpRunner.test_validate_response_content # 运行单个测试用例

python -m tests.api_server 或 PYTHONPATH=. python tests/api_server.py # 启动测试示例服务器
python -m apimeter tests/demo/demo.yml
python -m apimeter tests/testcases --log-level debug --save-tests # 测试示例，同时设置日志与生成中间处理文件


# 打包编译与发布
git tag v1.0.0 或 git tag -a v1.0.0 -m "发布正式版本 v1.0.0" # 打标签（轻量或附注）
git push v1.0.0 或 git push --tags # 推送标签(单个或所有)
poetry build  # 打包
poetry publish  # 发布，根据提示输入pypi账号密码
pip install -i https://pypi.Python.org/simple/ apimeter  # 指定安装源，因为刚发布其他平台未及时同步


# 文档编译与部署 
## 1. 本地构建
pip install mkdocs-material==3.3.0
mkdocs build
mkdocs serve

## 2. Gitlab CI 自动化构建
添加.gitlab-ci.yml配置文件，apimeter仓库设置-部署-Pages/完善功能文档，更新mkdocs.yml配置

## 3. Github Action 自动化构建
添加.github/workflows/docs.yml配置文件，apimeter参考设置-pages-Source选择：Deploy from a branch-分支选择：gh-pages（注意避坑：Source不要选择Github Actions、另外添加disable_nojekyll: false不使用默认Jekyll主题）


# 逐行代码运行时内存分析
poetry shell
pip install memory-profiler
# 1. 导入方式
python -m apimeter ~/Project/ATDD/tmp/demo_api/ --skip-success
# 2. 装饰器方式
python -m memory_profiler apimeter ~/Project/ATDD/tmp/demo_api --skip-success --log-level error
# 3. 命令方式
mprof run apimeter /path/to/api
mprof plot  # 生成内存趋势图，安装依赖pip install matplotlib
# 参考链接：https://www.cnblogs.com/rgcLOVEyaya/p/RGC_LOVE_YAYA_603days_1.html
```


## 附录
- HttpRunner: https://github.com/httprunner/
- Requests: http://docs.python-requests.org/en/master/
- unittest: https://docs.python.org/3/library/unittest.html
- Locust: http://locust.io/
- har2case: https://github.com/httprunner/har2case
- HAR: http://httparchive.org/
- Swagger: https://swagger.io/