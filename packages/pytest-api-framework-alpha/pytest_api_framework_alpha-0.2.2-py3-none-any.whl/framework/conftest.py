import os
import re
import sys
import copy
import threading
import importlib
import traceback
from pathlib import Path
from itertools import chain
from urllib.parse import urljoin
from collections import OrderedDict
from datetime import datetime, timedelta
from itertools import groupby

import dill
import retry
import allure
import pytest
from box import Box

from framework.exit_code import ExitCode
from framework.db.mysql_db import MysqlDB
from framework.db.redis_db import RedisDB
from framework.utils.log_util import logger
from framework.render_data import RenderData
from framework.utils.yaml_util import YamlUtil
from framework.allure_report import generate_report
from framework.global_attribute import CONTEXT, CONFIG, _FRAMEWORK_CONTEXT
from framework.utils.common import snake_to_pascal, get_apps, convert_numbers_to_decimal
from config.settings import DATA_DIR, CASES_DIR

all_app = get_apps()
module = importlib.import_module("test_case.conftest")


def find_data_path_by_case(app, case_file_name):
    """
    基于case文件名称查找与之对应的yml文件路径
    :param app:
    :param case_file_name:
    :return:
    """
    for file_path in Path(os.path.join(DATA_DIR, app)).rglob(f"{case_file_name}.y*"):
        if file_path:
            return file_path


def __init_allure(params):
    """设置allure中case的 title, description, level"""
    case_level_map = {
        "p0": allure.severity_level.BLOCKER,
        "p1": allure.severity_level.CRITICAL,
        "p2": allure.severity_level.NORMAL,
        "p3": allure.severity_level.MINOR,
        "p4": allure.severity_level.TRIVIAL,
    }
    allure.dynamic.title(params.get("title"))
    allure.dynamic.description(params.get("describe"))
    allure.dynamic.severity(case_level_map.get(params.get("level")))
    allure.dynamic.feature(params.get("module"))
    allure.dynamic.story(params.get("describe"))


def pytest_configure(config):
    """
    初始化时被调用，可以用于设置全局状态或配置
    :param config:
    :return:
    """

    for app in all_app:
        # 将所有app对应环境的基础测试数据加到全局
        CONTEXT.set_from_yaml(f"config/{app}/context.yaml", CONTEXT.env, app)
        # 将所有app对应环境的中间件配置加到全局
        CONFIG.set_from_yaml(f"config/{app}/config.yaml", CONTEXT.env, app)

    CONTEXT.set(key="all_app", value=all_app)
    sys.path.append(CASES_DIR)


def pytest_addoption(parser):
    parser.addini(name="ignore_error_and_continue", help="是否忽略失败case,继续执行")


def pytest_generate_tests(metafunc):
    """
    生成（多个）对测试函数的参数化调用
    :param metafunc:
    :return:
    """
    # 获取当前待执行用例的文件名
    module_name = metafunc.module.__name__.split('.')[-1]
    func_file_path = metafunc.module.__file__
    # 获取当前待执行用例的函数名
    func_name = metafunc.function.__name__

    # 获取测试用例所属app
    belong_app = Path(func_file_path).relative_to(CASES_DIR).parts[0]
    # 获取当前用例对应的测试数据路径
    data_path = find_data_path_by_case(belong_app, module_name)

    if not data_path:
        logger.error(f"测试数据文件: {func_file_path} 不存在")
        traceback.print_exc()
        pytest.exit(ExitCode.CASE_YAML_NOT_EXIST)
    test_data = YamlUtil(data_path).load_yml()
    # 测试用例公共数据
    case_common = test_data.get("case_common")
    if case_common.get("ignore"):
        return

    # UPDATE: 为了支持Setup和Teardown的分组
    if func_name in ["test_setup", "test_teardown"]:
        return

    # 测试用例数据
    case_data = test_data.get(func_name) or dict()
    if not case_data:
        case_data["_scenario"] = {"data": {}}
        case_data["_belong_app"] = belong_app
        metafunc.parametrize("data", [case_data, ], ids=[f'{case_data.get("title", "")}#'], scope="function")
        return
    if case_data.get("request") is None:
        case_data["request"] = dict()
    if case_data.get("request").get("headers") is None:
        case_data["request"]["headers"] = dict()

    # 合并测试数据
    case_data.setdefault("module", case_common.get("module"))
    case_data.setdefault("describe", case_common.get("describe"))
    case_data["_belong_app"] = belong_app

    domain = CONTEXT.get(key="domain", app=belong_app)
    domain = domain if domain.startswith("http") else f"https://{domain}"
    url = case_data.get("request").get("url")
    method = case_data.get("request").get("method")
    if not url:
        # UPDATE: 有的步骤不需要请求接口 比如 只校验数据库， 去掉下面的校验
        if not case_common.get("url"):
            logger.warning(f"{func_file_path} request中缺少必填字段: url", case_data)
            # pytest.exit(ExitCode.YAML_MISSING_FIELDS)
    else:
        if url.strip().startswith("${"):
            case_data["request"]["url"] = url
        else:
            case_data["request"]["url"] = urljoin(domain, url)

    if not method:
        # UPDATE: 有的步骤不需要请求接口 比如 只校验数据库， 去掉下面的校验
        if not case_common.get("method"):
            logger.warning(f"{func_file_path} request中缺少必填字段: method", case_data)
            # pytest.exit(ExitCode.YAML_MISSING_FIELDS)

    for key in ["title", "level"]:
        if key not in case_data:
            logger.warning(f"{func_file_path} 缺少必填字段: {key}", case_data)
            # pytest.exit(ExitCode.YAML_MISSING_FIELDS)

    if case_data.get("mark"):
        metafunc.function.marks = [case_data.get("mark"), case_data.get("level")]
    else:
        metafunc.function.marks = [case_data.get("level")]

    scenarios = case_common.get("scenarios")
    case_data_list = list()
    if scenarios:
        ids = list()
        for index, item in enumerate(scenarios):
            if item.get("scenario").get("ignore"):
                continue
            if func_name in item.get("scenario").get("exclude", list()):
                continue
            _mark = CONTEXT.get("mark")
            if _mark and item.get("scenario").get("flag") != _mark:
                continue
            deep_copied_case_data = copy.deepcopy(case_data)
            scenario = item.get("scenario")
            try:
                # 剔除标记disable的字段
                deep_copied_case_data = disable_field(scenario.get("data"), deep_copied_case_data)
                deep_copied_case_data["_scenario"] = item.get("scenario")
                case_data_list.append(deep_copied_case_data)
                ids.append(case_data.get("title") + f"#{index + 1}")
            except KeyError as e:
                logger.error(f"scenario参数化格式不正确:{e}")
                traceback.print_exc()
                pytest.exit(ExitCode.PARAMETRIZE_ATTRIBUTE_NOT_EXIT)
        metafunc.parametrize("data", case_data_list, ids=ids, scope="function")
    else:
        if not case_common.get("ignore"):
            case_data["_scenario"] = {"data": {}}
            case_data_list = [case_data]
        # 进行参数化生成用例
        metafunc.parametrize("data", case_data_list, ids=[f'{case_data.get("title")}#1'], scope="function")


def pytest_collection_modifyitems(items):
    # 重新排序
    new_items = sort(items)
    # Demo: new_items = [items[0],items[2],items[1],items[3]]
    items[:] = new_items

    for item in items:
        try:
            marks = item.function.marks
            for mark in marks:
                if isinstance(mark, list):
                    for _ in mark:
                        item.add_marker(_)
                else:
                    item.add_marker(mark)
        except Exception:
            pass


def disable_field(scenario, data):
    def _clean(obj):
        if isinstance(obj, dict):
            keys_to_delete = []
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    _clean(v)
                elif isinstance(v, str):
                    for ak, av in scenario.items():
                        if av == "disable" and v == f"${{{ak}}}":
                            keys_to_delete.append(k)
                            break
            # 统一删除，避免边遍历边删
            for k in keys_to_delete:
                del obj[k]

        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    _clean(item)

    _clean(data)
    return data


# UPDATE 将用例 按类名进行分组的核心方法
def filtered_groupby(iterable, key_func):
    """生成器：过滤key_func返回None的元素，并按key_func分组"""
    current_key = None
    current_group = []

    for item in iterable:
        key = key_func(item)
        if key is None:
            continue  # 跳过key为None的元素

        # 处理分组逻辑（类似groupby）
        if key != current_key:
            if current_group:
                yield current_key, current_group
            current_key = key
            current_group = [item]
        else:
            current_group.append(item)

    # 输出最后一组
    if current_group:
        yield current_key, current_group


# UPDATE：按类的全路径 进行用例分组 同一个类的test方法分到一组
def __get_group_key__(item):
    return '::'.join(item.nodeid.split('::')[:2])


# UPDATE：改变pytest的原始排序规则
def sort(case_items):
    # 按测试类全路径分类,同一个类文件的用例归集到一起
    # 使用 groupby 函数进行分组
    item_group_list = [list(group) for _, group in filtered_groupby(case_items, __get_group_key__)]

    all_item_list = []
    clase_id = None
    for items in item_group_list:
        # 未被test_setup/test_teardown 标记的test方法
        non_custom_scope_items = [item for item in items if
                                  'test_setup' != item.originalname and 'test_teardown' != item.originalname]
        item_list = []
        # 用例的组数
        case_suite_num = 0
        # 生成每个组当前的索引
        ori_name_temp = None
        ori_name_list = []

        for item in non_custom_scope_items:
            clase_id = item.cls.__name__
            original_name = item.originalname

            if ori_name_temp is None or ori_name_temp == original_name:
                ori_name_temp = original_name
                case_suite_num += 1
                ori_name_list.append([original_name, item])
            else:
                break

        # 根据组数 创建各组的数组 并插入第一个case
        case_dict = dict()
        try:
            for i in range(case_suite_num):
                item = ori_name_list[i][1]
                id = item.callspec.id

                first_part = id.split('#', 1)[-1]
                index = first_part.split(']')[0]
                case_dict[index] = [item]
        except:
            pass

        new_start_index = case_suite_num
        # 以new_start_index为起点 重新遍历items
        try:
            for i in range(new_start_index, len(non_custom_scope_items)):
                item = non_custom_scope_items[i]
                id = item.callspec.id
                first_part = id.split('#', 1)[-1]
                index = first_part.split(']')[0]
                case_dict.get(index).append(item)
        except:
            pass

        index = 0
        for id in case_dict:
            index += 1
            case_item_list = case_dict.get(id)
            for item in case_item_list:
                allure_suite_mark = f'{clase_id}#{index}'
                setattr(item, 'allure_suite_mark', allure_suite_mark)
            item_list += case_item_list

        all_item_list += item_list

    return all_item_list


def pytest_collection_finish(session):
    """获取最终排序后的 items 列表"""
    # 过滤掉item名称是test_setup或test_teardown的
    session.items = [item for item in session.items if item.name not in ["test_setup", "test_teardown"]]

    # 1. 筛选出带井号 名称带'#' 的item，并记录原始索引
    hash_items_with_index = [(index, item) for index, item in enumerate(session.items) if "#" in item.name]

    # 2. 按照 'cls' 对带井号的元素进行分组
    grouped_by_cls = {}
    for index, item in hash_items_with_index:
        cls = item.cls.__module__ + item.parent.name
        if cls not in grouped_by_cls:
            grouped_by_cls[cls] = []
        grouped_by_cls[cls].append((index, item))  # 记录索引和元素

    # 3. 对每个 cls 分组内的带井号的元素进行排序
    for cls, group in grouped_by_cls.items():
        group_values = [x[1] for x in group]
        # 获取item#号后面的数字
        pattern = r"#(\d+)]"
        grouped_data = OrderedDict()
        # 按照#号后面的数字进行排序并分组
        for item in group_values:
            index = re.search(pattern, item.name).group(1)
            grouped_data.setdefault(index, []).append(item)
        # 标记每个分组的第一个和最后一个
        for group2 in grouped_data.values():
            group2[0].funcargs["first"] = True
            group2[-1].funcargs["last"] = True

        group_values = list(chain.from_iterable(grouped_data.values()))

        # 4. 将排序后的items放回原列表
        for (original_index, _), val in zip(group, group_values):
            session.items[original_index] = val  # 将反转后的元素替换回原位置


def pytest_runtestloop(session):
    _FRAMEWORK_CONTEXT.set(key="_http", value=login())


@pytest.hookimpl
def pytest_runtest_setup(item):
    allure.dynamic.sub_suite(item.allure_suite_mark)
    if item.funcargs.get("first"):
        test_object = item.instance
        test_object.context = CONTEXT
        test_object.config = CONFIG
        test_object.http = _FRAMEWORK_CONTEXT.get(key="_http")
        data = item.callspec.params.get("data")
        test_object.data = Box(data)
        test_object.scenario = Box(convert_numbers_to_decimal(data.get("_scenario").get("data")))
        test_object.belong_app = data.get("_belong_app")
        test_before_scenario = getattr(test_object, "test_setup", None)
        if test_before_scenario:
            try:
                test_before_scenario()
                item.funcargs["setup_success"] = True
            except Exception as e:
                item.funcargs["setup_success"] = False
                traceback.print_exc()
                logger.error(f"{item.location[0]} test_before_scenario方法执行异常:{e}")


def pytest_runtest_call(item):
    """
    模版渲染，运行用例
    :param item:
    :return:
    """
    func_name = item.originalname
    ignore_error_and_continue = item.config.getini("ignore_error_and_continue")
    if ignore_error_and_continue == "false":
        # setup方法执行失败，则主动标记用例执行失败，不会执行用例
        if item.funcargs.get("setup_success") is False:
            pytest.skip("test_before_scenario execute error")
        # 判断上一个用例是否执行失败，如果上一个用例执行失败，则主动标记用例执行失败，不会执行用例（解决场景性用例，有一个失败则后续用例判为失败）
        index = item.session.items.index(item)
        current_cls_name = item.parent.name
        # 向前遍历，找到属于同一个类的用例
        pattern = r"#(\d+)]"
        current_turn = re.search(pattern, item.name)
        if current_turn:
            for prev_item in reversed(item.session.items[:index]):  # 只遍历当前 item 之前的
                if prev_item.parent.name == current_cls_name and re.search(pattern, prev_item.name).group(
                        1) == current_turn.group(1):  # 确保是同一个类
                    status = getattr(prev_item, "status", None)  # 访问 status 属性
                    skip_reason = getattr(prev_item, "skip_reason", None)  # 访问 skip_reason 属性
                    if status == "skipped" and skip_reason.strip() in [
                        "the previous method execution skipped",
                        "the previous method execution failed",
                        "test_before_scenario execute error"]:
                        pytest.skip("the previous method execution skipped")
                    elif status == "failed":
                        pytest.skip("the previous method execution failed")

    # 获取原始测试数据
    origin_data = item.funcargs.get("data")
    __init_allure(origin_data)
    logger.info(f"执行用例: {item.nodeid}")
    # # 对原始请求数据进行渲染替换
    # rendered_data = RenderData(origin_data).render()
    # 函数式测试用例添加参数data, belong_app
    http = item.funcargs.get("http")
    item.funcargs["data"] = item.instance.data = Box(origin_data)
    item.funcargs["scenario"] = item.instance.scenario = Box(
        convert_numbers_to_decimal(origin_data.get("_scenario").get("data")))
    _belong_app = origin_data.get("_belong_app")
    item.funcargs["belong_app"] = item.instance.belong_app = _belong_app
    item.funcargs["config"] = item.instance.config = CONFIG
    item.funcargs["context"] = item.instance.context = CONTEXT
    # 类式测试用例添加参数http，data, belong_app
    item.instance.http = http

    # # 获取测试函数体内容
    # func_source = re.sub(r'(?<!["\'])#.*', '', dill.source.getsource(item.function))
    # # 校验测试用例中是否有断言
    # if "assert" not in func_source:
    #     logger.error(f"测试方法:{item.originalname}缺少断言")
    #     pytest.exit(ExitCode.MISSING_ASSERTIONS)

    # 判断token是否过期，过期则重新登录
    expire_time = _FRAMEWORK_CONTEXT.get(app=_belong_app, key="expire_time")
    if expire_time:
        _http = _FRAMEWORK_CONTEXT.get("_http")
        if datetime.now() >= expire_time:
            # 重新登录
            setattr(_http, _belong_app, getattr(module, f"{snake_to_pascal(_belong_app)}Login")(_belong_app))
            # 更新记录的过期时间
            token_expiry = CONTEXT.get(_belong_app).get("token_expiry")
            expire_time = datetime.now() + timedelta(seconds=token_expiry)
            _FRAMEWORK_CONTEXT.set(app=_belong_app, key="expire_time", value=expire_time)


def pytest_runtest_teardown(item):
    if item.funcargs.get("last") and getattr(item, "status", None) not in ["skipped", "failed"]:
        test_object = item.instance
        test_after_scenario = getattr(test_object, "test_teardown", None)
        if test_after_scenario:
            try:
                test_after_scenario()
            except Exception as e:
                pytest.fail(f"the test_after_scenario method execution error: {e}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """拦截 pytest 生成测试报告，移除特定用例的统计"""
    outcome = yield
    report = outcome.get_result()
    # 将测试结果存储到 item 对象的自定义属性 `_test_status`
    if report.when == "call":  # 只记录测试执行阶段的状态，不包括 setup/teardown
        longrepr = report.longrepr
        if longrepr:
            try:
                if ":" in longrepr[2]:
                    key, reason = longrepr[2].split(":")
                else:
                    key, reason = longrepr[2], ""
                if key == "Skipped":
                    item.skip_reason = reason
            except:
                pass
        item.status = report.outcome  # 'passed', 'failed', or 'skipped'


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """在 pytest 结束后修改统计数据或添加自定义报告"""
    stats = terminalreporter.stats
    # 统计各种测试结果
    passed = len(stats.get("passed", []))
    failed = len(stats.get("failed", []))
    skipped = len(stats.get("skipped", []))
    total = passed + failed + skipped
    try:
        pass_rate = round(passed / (total - skipped) * 100, 2)
    except ZeroDivisionError:
        pass_rate = 0
    # 打印自定义统计信息
    terminalreporter.write("\n============ 执行结果统计 ============\n", blue=True, bold=True)
    terminalreporter.write(f"执行用例总数: {passed + failed}\n", bold=True)
    terminalreporter.write(f"通过用例数: {passed}\n", green=True, bold=True)
    terminalreporter.write(f"失败用例数: {failed}\n", red=True, bold=True)
    terminalreporter.write(f"跳过用例数: {skipped}\n", yellow=True, bold=True)
    terminalreporter.write(f"用例通过率: {pass_rate}%\n", green=True, bold=True)
    terminalreporter.write("====================================\n", blue=True, bold=True)
    # 生成allure测试报告
    generate_report()


def pytest_exception_interact(node, call, report):
    """
    用例执行抛出异常时，将异常记录到日志
    :param node:
    :param call:
    :param report:
    :return:
    """
    if call.excinfo.type is AssertionError:
        logger.error(f"{node.nodeid} failed: {call.excinfo.value}\n")


@pytest.fixture(autouse=True)
def response():
    response = None
    yield response


@pytest.fixture(autouse=True)
def data():
    data: dict = dict()
    yield data


@pytest.fixture(autouse=True)
def belong_app():
    app = None
    yield app


@pytest.fixture(autouse=True)
def config():
    config = None
    yield config


@pytest.fixture(autouse=True)
def context():
    context = None
    yield context


@retry.retry(tries=3, delay=1)
@pytest.fixture(scope="function", autouse=True)
def http():
    yield _FRAMEWORK_CONTEXT.get("_http")


class Http(object):
    ...


def login():
    def inner_login(app):
        setattr(Http, app, getattr(module, f"{snake_to_pascal(app)}Login")(app))
        token_expiry = CONTEXT.get(app).get("token_expiry")
        if token_expiry:
            expire_time = datetime.now() + timedelta(seconds=token_expiry)
            _FRAMEWORK_CONTEXT.set(app=app, key="expire_time", value=expire_time)
        mysqls = CONFIG.get(app=app, key="mysql")
        mysqls_obj = {item: MysqlDB(**mysqls.get(item)) for item in mysqls.keys()}
        _FRAMEWORK_CONTEXT.set(app=app, key="mysql", value=mysqls_obj)

    try:
        logger.info("登录账号".center(80, "*"))
        threads = []
        for app in all_app:
            t = threading.Thread(target=inner_login, args=(app,))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        logger.info("登录完成".center(80, "*"))
        return Http
    except Exception as e:
        logger.error(f"登录{app}异常:{e}")
        traceback.print_exc()
        pytest.exit(ExitCode.LOGIN_ERROR)
        return None
