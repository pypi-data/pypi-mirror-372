# encoding: utf-8

import sys
import traceback

from apimeter import exceptions, logger, parser


class ResponseFieldProxy(object):
    """响应字段代理，支持点号访问语法，复用现有的extract_field逻辑"""
    
    def __init__(self, resp_obj, field_name):
        self._resp_obj = resp_obj
        self._field_name = field_name
        self._cached_value = None
        self._cached = False
    
    def __getattr__(self, name):
        # 构建完整的字段路径，如 content.token
        full_field = f"{self._field_name}.{name}"
        try:
            # 复用现有的extract_field逻辑
            value = self._resp_obj.extract_field(full_field)
            # 如果返回的是字典，则创建新的代理对象以支持进一步的点号访问
            if isinstance(value, dict):
                return ResponseFieldProxy(self._resp_obj, full_field)
            return value
        except (exceptions.ExtractFailure, exceptions.ParamsError):
            raise AttributeError(f"'{self._field_name}' object has no attribute '{name}'")
    
    def __getitem__(self, key):
        # 支持字典式访问，如 headers["Content-Type"]
        full_field = f"{self._field_name}.{key}"
        try:
            return self._resp_obj.extract_field(full_field)
        except (exceptions.ExtractFailure, exceptions.ParamsError):
            raise KeyError(key)
    
    def __contains__(self, key):
        # 支持 in 操作符
        try:
            full_field = f"{self._field_name}.{key}"
            self._resp_obj.extract_field(full_field)
            return True
        except (exceptions.ExtractFailure, exceptions.ParamsError):
            return False
    
    def __str__(self):
        if not self._cached:
            try:
                self._cached_value = self._resp_obj.extract_field(self._field_name)
                self._cached = True
            except (exceptions.ExtractFailure, exceptions.ParamsError):
                self._cached_value = f"<{self._field_name}>"
        return str(self._cached_value)
    
    def __repr__(self):
        return f"ResponseFieldProxy({self._field_name})"
    
    def __len__(self):
        # 支持len()函数
        try:
            value = self._resp_obj.extract_field(self._field_name)
            return len(value)
        except (exceptions.ExtractFailure, exceptions.ParamsError):
            raise TypeError(f"object of type '{self._field_name}' has no len()")


class Validator(object):
    """Validate tests

    Attributes:
        validation_results (dict): store validation results,
            including validate_extractor and validate_script.

    """

    def __init__(self, session_context, resp_obj):
        """initialize a Validator for each teststep (API request)

        Args:
            session_context: HttpRunner session context
            resp_obj: ResponseObject instance
        """
        self.session_context = session_context
        self.resp_obj = resp_obj
        self.validation_results = {}

    def __eval_validator_check(self, check_item):
        """evaluate check item in validator.

        Args:
            check_item: check_item should only be the following 5 formats:
                1, variable reference, e.g. $token
                2, function reference, e.g. ${is_status_code_200($status_code)}
                3, dict or list, maybe containing variable/function reference, e.g. {"var": "$abc"}
                4, string joined by delimiter. e.g. "status_code", "headers.content-type"
                5, regex string, e.g. "LB[\d]*(.*)RB[\d]*"

        """
        try:
            if isinstance(check_item, (dict, list)) or isinstance(
                check_item, parser.LazyString
            ):
                # format 1/2/3
                check_value = self.session_context.eval_content(check_item)
            else:
                # format 4/5
                check_value = self.resp_obj.extract_field(check_item)

            return check_value
        except (exceptions.ParamsError, exceptions.ExtractFailure) as ex:
            # 对于关键异常（如字段不存在、参数错误等），继续抛出以保持原有行为
            # 这些异常通常表示测试用例配置错误，应该导致测试失败或错误
            logger.log_error("Validator get check value failed for '{}': {}".format(check_item, str(ex)))
            raise
        except (exceptions.VariableNotFound, exceptions.FunctionNotFound) as ex:
            # 对于资源找不到的异常，也应该抛出，因为这通常是配置问题
            logger.log_error("Validator get check value failed for '{}': {}".format(check_item, str(ex)))
            raise
        except Exception as ex:
            # 对于其他类型的异常（如一些运行时异常），将异常信息作为check_value返回，避免中断其他校验点
            error_msg = "{}: {}".format(type(ex).__name__, str(ex)) if str(ex) else "{}".format(type(ex).__name__)
            logger.log_error("Validator get check value failed for '{}': {}".format(check_item, error_msg))
            return error_msg

    def __eval_validator_expect(self, expect_item):
        """evaluate expect item in validator.

        Args:
            expect_item: expect_item should only be in 2 types:
                1, variable reference, e.g. $expect_status_code
                2, actual value, e.g. 200

        """
        try:
            expect_value = self.session_context.eval_content(expect_item)
            return expect_value
        except (exceptions.ParamsError, exceptions.ExtractFailure) as ex:
            # 对于关键异常，继续抛出
            logger.log_error("Validator get expect value failed for '{}': {}".format(expect_item, str(ex)))
            raise
        except (exceptions.VariableNotFound, exceptions.FunctionNotFound) as ex:
            # 对于资源找不到的异常，也应该抛出
            logger.log_error("Validator get expect value failed for '{}': {}".format(expect_item, str(ex)))
            raise
        except Exception as ex:
            # 对于其他异常，将异常信息作为expect_value返回
            error_msg = "{}: {}".format(type(ex).__name__, str(ex)) if str(ex) else "{}".format(type(ex).__name__)
            logger.log_error("Validator get expect value failed for '{}': {}".format(expect_item, error_msg))
            return error_msg

    def validate_script(self, script):
        """make validation with python script:
        1. assert 语句
        2. 自定义函数
        """
        # 准备变量环境
        variables = {
            "response": self.resp_obj,
            "status_code": self.resp_obj.status_code,
            "url": self.resp_obj.url,
            "ok": self.resp_obj.ok,
            "encoding": self.resp_obj.encoding,
            "reason": self.resp_obj.reason,
        }
        
        # 使用ResponseFieldProxy复用现有的extract_field逻辑，避免代码重复
        try:
            variables.update({
                "content": ResponseFieldProxy(self.resp_obj, "content"),
                "body": ResponseFieldProxy(self.resp_obj, "body"),
                "text": ResponseFieldProxy(self.resp_obj, "text"),
                "json": ResponseFieldProxy(self.resp_obj, "json"),
                "headers": ResponseFieldProxy(self.resp_obj, "headers"),
                "cookies": ResponseFieldProxy(self.resp_obj, "cookies"),
                "elapsed": ResponseFieldProxy(self.resp_obj, "elapsed"),
            })
        except Exception as e:
            # 如果获取响应字段失败，记录警告但继续执行
            logger.log_warning("Failed to add response field variables: {}".format(e))
        
        variables.update(self.session_context.test_variables_mapping)
        variables.update(globals())

        # 逐条执行脚本
        script_results = []
        overall_success = True
        
        for script_line in script:
            script_dict = {
                "script": script_line,
                "check_result": "pass",
                "output": "success",
            }
            
            try:
                # 解析脚本内容（支持assert语句和自定义函数）
                parsed_script_line = self.session_context.eval_content(script_line)
                logger.log_debug(f"parsed_script_line: {parsed_script_line}")
                if parser.function_regex_compile.match(str(script_line)):
                    # 如果是自定义函数，直接赋值输出
                    logger.log_debug("自定义函数: {}".format(script_line))
                    script_dict["output"] = str(parsed_script_line)
                else:
                    # 否则当做python脚本执行（包括assert语句等）
                    logger.log_debug("python脚本: {}".format(script_line))
                    exec(parsed_script_line, variables.copy())
                logger.log_debug("validate_script: {} ==> pass".format(script_line))
            except SyntaxError as ex:
                err_msg = "SyntaxError: {} (Line: {})".format(ex.msg, ex.lineno)
                overall_success = False
                script_dict["check_result"] = "fail"
                script_dict["output"] = err_msg
                
                validate_msg = "validate_script: {} ==> fail\n{}".format(script_line, err_msg)
                logger.log_error(validate_msg)
                
            except Exception as ex:
                err_msg = "{}: {}".format(type(ex).__name__, str(ex)) if str(ex) else "{}".format(type(ex).__name__)
                overall_success = False
                script_dict["check_result"] = "fail"
                script_dict["output"] = err_msg
                
                validate_msg = "validate_script: {} ==> fail\n{}".format(script_line, err_msg)
                logger.log_error(validate_msg)
            
            script_results.append(script_dict)
        
        # 返回结果，兼容原有格式但增加详细信息
        result = {
            # 修复TypeError: sequence item 2: expected str instance, LazyString found
            "validate_script": "<br/>".join([str(line) for line in script]),
            "check_result": "pass" if overall_success else "fail", 
            "output": "success" if overall_success else "script validation failed",
            "details": script_results  # 新增详细结果
        }
        
        return result

    def validate(self, validators):
        """make validation with comparators"""
        self.validation_results = {}
        if not validators:
            return

        logger.log_debug("start to validate.")

        validate_pass = True
        failures = []

        for validator in validators:

            if isinstance(validator, dict) and validator.get("type") == "python_script":
                # script = self.session_context.eval_content(validator["script"])
                result = self.validate_script(validator["script"])
                if result["check_result"] == "fail":
                    validate_pass = False
                    failures.append(result["output"])

                self.validation_results["validate_script"] = result
                continue

            if "validate_extractor" not in self.validation_results:
                self.validation_results["validate_extractor"] = []

            # validator should be LazyFunction object
            if not isinstance(validator, parser.LazyFunction):
                raise exceptions.ValidationFailure(
                    "validator should be parsed first: {}".format(validators)
                )

            # evaluate validator args with context variable mapping.
            validator_args = validator.get_args()
            check_item, expect_item = validator_args
            check_value = self.__eval_validator_check(check_item)
            expect_value = self.__eval_validator_expect(expect_item)
            validator.update_args([check_value, expect_value])

            comparator = validator.func_name
            validator_dict = {
                "comparator": comparator,
                "check": check_item,
                "check_value": check_value,
                "expect": expect_item,
                "expect_value": expect_value,
            }
            validate_msg = "\nvalidate: {} {} {}({})".format(
                check_item, comparator, expect_value, type(expect_value).__name__
            )

            try:
                validator.to_value(self.session_context.test_variables_mapping)
                validator_dict["check_result"] = "pass"
                validate_msg += "\t==> pass"
                logger.log_debug(validate_msg)
            except (AssertionError, TypeError):
                validate_pass = False
                validator_dict["check_result"] = "fail"
                validate_msg += "\t==> fail"
                validate_msg += "\n{}({}) {} {}({})".format(
                    check_value,
                    type(check_value).__name__,
                    comparator,
                    expect_value,
                    type(expect_value).__name__,
                )
                logger.log_error(validate_msg)
                failures.append(validate_msg)

            self.validation_results["validate_extractor"].append(validator_dict)

            # restore validator args, in case of running multiple times
            validator.update_args(validator_args)

        if not validate_pass:
            failures_string = "\n".join([failure for failure in failures])
            raise exceptions.ValidationFailure(failures_string)
