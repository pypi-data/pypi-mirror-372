import requests
from requests.exceptions import RequestException
import time
from typing import Dict, Any, Optional, Union

class APICaller:
    """API调用工具类，封装了接口调用的通用逻辑"""

    def __init__(self, base_url: str = "http://localhost:25800", retries: int = 3,
                 click_timeout: float = 1, read_timeout: float = 2):
        """
        初始化API调用器

        Args:
            base_url: API基础URL
            retries: 请求失败时的重试次数
            click_timeout: 点击接口超时时间(秒)
            read_timeout: 读取接口超时时间(秒)
        """
        self.base_url = base_url
        self.retries = retries
        self.click_timeout = click_timeout
        self.read_timeout = read_timeout
        self.session = requests.Session()  # 使用Session对象保持连接

    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None,
                      timeout: float = 1) -> Optional[Dict[str, Any]]:
        """
        发送HTTP请求并处理响应

        Args:
            url: 请求URL
            params: 请求参数
            timeout: 超时时间(秒)

        Returns:
            解析后的JSON响应或None

        Raises:
            RequestException: 请求异常
        """
        for attempt in range(self.retries):
            try:
                self._log_request(url, params, attempt)
                response = self.session.get(url, params=params, timeout=timeout)
                response.raise_for_status()  # 检查HTTP状态码
                return response.json()
            except RequestException as e:
                self._log_error(e, attempt)
                if attempt < self.retries - 1:
                    wait_time = (attempt + 1) * 0.5  # 指数退避策略
                    print(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    raise

    def _log_request(self, url: str, params: Optional[Dict[str, Any]], attempt: int) -> None:
        """记录请求信息"""
        print(f"尝试请求 {url} (参数: {params}) - 尝试 {attempt + 1}/{self.retries}")

    def _log_error(self, error: Exception, attempt: int) -> None:
        """记录错误信息"""
        print(f"请求失败: {str(error)}")

    def _call_web_inject_api(self,
                             action: str,
                             element_selector: Optional[Any] = None,
                             val: Optional[Any] = None,
                             days: Optional[Any] = None,
                             val1: Optional[Any] = None,
                             x:Optional[Any] = None,
                             y: Optional[Any] = None,
                             keytab: Optional[Any] = None,
                             keys:Optional[Any] = None,
                             scroll_amount:Optional[Any] = None,
                             play_file: Optional[Any] = None,
                             times: Optional[Any] = None


        ) -> Dict[str, Any]:
        """
        调用webInjectTake API的通用方法

        Args:
            action: 操作类型
            element_selector: 元素选择器
            val: 可选的值参数

        Returns:
            API响应
        """
        print(f"===== 开始调用{self._get_action_name(action)}接口 =====")
        url = f"{self.base_url}/webInjectTake"
        params = {
            "action": action,
            "element": element_selector
        }
        if val is not None:
            params["val"] = val
        if days is not None:
            params["days"] = days
        if val1 is not None:
            params["val1"] = val1
        if x is not None:
            params["x"] = x
        if y is not None:
            params["y"] = y
        if keytab is not None:
            params["keytab"] = keytab
        if keys is not None:
            params["keys"] = keys
        if scroll_amount is not None:
            params["scroll_amount"] = scroll_amount,
        if play_file is not None:
            params["play_file"] = play_file
        if times is not None:
            params["times"] = times
        try:
            result = self._make_request(url, params, self.click_timeout)
            self._log_success(result, action)
            return result
        except Exception as e:
            self._log_failure(e, action)
            raise

    def _get_action_name(self, action: str) -> str:
        """获取操作名称的中文描述"""
        action_names = {
            "click": "点击",
            "url": "打开URL",
            "alert": "弹窗",
            "val": "设置值/获取值",
            "text": "设置文本/获取文本",
            "css": "设置CSS样式",
            "html": "设置HTML内容",
            "prop": "设置/获取属性",
            "attr": "设置/获取特性",
            "focus": "聚焦元素",
            "show": "显示元素",
            "hide": "隐藏元素",
            "remove": "移除元素",
            "offset": "获取元素位置",
            "cookie": "操作Cookie",
            "count":"获取元素数量",
            "move":"鼠标移动",
            "left_click":"鼠标左键单击",
            "right_click":"鼠标右键单击",
            "combo":"组合按键",
            "tab":"按键",
            "up":"滚轮上",
            "down":"滚轮下",
            "playback":"回放"
        }
        return action_names.get(action, action)

    def _log_success(self, result: Dict[str, Any], action: str) -> None:
        """记录成功响应"""
        print(f"{self._get_action_name(action)}接口成功响应：{result}")

    def _log_failure(self, error: Exception, action: str) -> None:
        """记录失败响应"""
        print(f"{self._get_action_name(action)}接口调用失败：{str(error)}")


    def call_playback_api(self,play_file:str,times:int)-> Dict[str, Any]:
        return self._call_web_inject_api("playback",play_file,times)
    def call_move_api(self, x:int=0,y:int=0) -> Dict[str, Any]:
        return self._call_web_inject_api("move",x=x,y=y)

    def call_left_click_api(self) -> Dict[str, Any]:
        return self._call_web_inject_api("left_click")

    def call_right_click_api(self) -> Dict[str, Any]:
        return self._call_web_inject_api("right_click")

    def call_combo_api(self,keys:str="") -> Dict[str, Any]:
        return self._call_web_inject_api("combo",keys=keys)

    def call_tab_api(self,keytab:str="") -> Dict[str, Any]:
        return self._call_web_inject_api("tab",keytab=keytab)

    def call_up_api(self,scroll_amount:str="") -> Dict[str, Any]:
        return self._call_web_inject_api("up",scroll_amount=scroll_amount)

    def call_down_api(self,scroll_amount:str="") -> Dict[str, Any]:
        return self._call_web_inject_api("down",scroll_amount=scroll_amount)

    def call_click_api(self, element_selector: str = "#su") -> Dict[str, Any]:
        """调用点击API"""
        return self._call_web_inject_api("click", element_selector)

    def call_openUrl_api(self, url: str = "") -> Dict[str, Any]:
        """调用打开URL API"""
        return self._call_web_inject_api("url", url)

    def call_alert_api(self, message: str = "1") -> Dict[str, Any]:
        """调用弹窗API"""
        return self._call_web_inject_api("alert", message)

    def call_val_api(self, element_selector: str = "", val: Any = "") -> Dict[str, Any]:
        """调用设置值/获取值API"""
        return self._call_web_inject_api("val", element_selector, val)

    def call_text_api(self, element_selector: str = "", val: Any = "") -> Dict[str, Any]:
        """调用设置文本/获取文本API"""
        return self._call_web_inject_api("text", element_selector, val)

    def call_css_api(self, element_selector: str = "", val: Any = "",val1: Any = "") -> Dict[str, Any]:
        """调用设置CSS样式API"""
        return self._call_web_inject_api("css", element_selector, val,val1=val1)

    def call_html_api(self, element_selector: str = "", val: Any = "") -> Dict[str, Any]:
        """调用设置HTML内容API"""
        return self._call_web_inject_api("html", element_selector, val)

    def call_prop_api(self, element_selector: str = "", val: Any = "",val1: Any = "") -> Dict[str, Any]:
        """调用设置/获取属性API"""
        return self._call_web_inject_api("prop", element_selector, val,val1=val1)

    def call_attr_api(self, element_selector: str = "", val: Any = "",val1: Any = "") -> Dict[str, Any]:
        """调用设置/获取特性API"""
        return self._call_web_inject_api("attr", element_selector, val,val1=val1)

    def call_focus_api(self, element_selector: str = "#su") -> Dict[str, Any]:
        """调用聚焦元素API"""
        return self._call_web_inject_api("focus", element_selector)

    def call_show_api(self, element_selector: str = "#su") -> Dict[str, Any]:
        """调用显示元素API"""
        return self._call_web_inject_api("show", element_selector)

    def call_offset_api(self, element_selector: str = "#su") -> Dict[str, Any]:
        """调用获取元素位置API"""
        return self._call_web_inject_api("offset", element_selector)

    def call_hide_api(self, element_selector: str = "#su") -> Dict[str, Any]:
        """调用隐藏元素API"""
        return self._call_web_inject_api("hide", element_selector)

    def call_remove_api(self, element_selector: str = "#su") -> Dict[str, Any]:
        """调用移除元素API"""
        return self._call_web_inject_api("remove", element_selector)

    def call_cookie_api(self, element_selector: str = "#su", val: Any = "", days: Any = "") -> Dict[str, Any]:
        """调用操作Cookie API"""
        return self._call_web_inject_api("cookie", element_selector, val, days=days)
    def call_count_api(self, element_selector: str = "#su") -> Dict[str, Any]:
        """调用显示元素API"""
        return self._call_web_inject_api("count", element_selector)

    def call_read_api(self) -> Dict[str, Any]:
        """
        调用read数据读取接口

        Returns:
            读取接口的响应数据
        """
        print("\n===== 开始调用读取接口 =====")
        read_url = f"{self.base_url}/read"

        try:
            read_result = self._make_request(read_url, timeout=self.read_timeout)
            print(f"读取接口成功响应：{read_result}")
            return read_result
        except Exception as e:
            print(f"读取接口调用失败：{str(e)}")
            raise

    def _call_apis_sequence(self, action_method: callable, *args, **kwargs) -> Dict[str, Any]:
        """
        通用的API序列调用方法

        Args:
            action_method: 要调用的操作方法
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            包含操作结果和读取结果的字典
        """
        try:
            action_result = action_method(*args, **kwargs)
            read_result = self.call_read_api()

            return {
                "action_result": action_result,
                "read_result": read_result,
                "status": "success"
            }
        except Exception as e:
            return {
                "action_result": None,
                "read_result": None,
                "status": "failed",
                "error": str(e)
            }

    def call_apis_playback(self, play_file: str, times: int) -> Dict[str, Any]:
        return self._call_apis_sequence(self.call_playback_api, play_file, times)

    def call_apis_count(self, element_selector: str = "#su") -> Dict[str, Any]:
        return self._call_apis_sequence(self.call_count_api, element_selector)

    def call_apis_move(self, x:int=0,y:int=0) -> Dict[str, Any]:
        return self._call_apis_sequence(self.call_move_api,x=x,y=y)

    def call_apis_left_click(self) -> Dict[str, Any]:
        return self._call_apis_sequence(self.call_left_click_api)

    def call_apis_right_click(self) -> Dict[str, Any]:
        return self._call_apis_sequence(self.call_right_click_api)

    def call_apis_combo(self,keys:str="") -> Dict[str, Any]:
        return self._call_apis_sequence(self.call_combo_api,keys=keys)

    def call_apis_tab(self,keytab:str="") -> Dict[str, Any]:
        return self._call_apis_sequence(self.call_tab_api,keytab=keytab)

    def call_apis_up(self,scroll_amount:str="") -> Dict[str, Any]:
        return self._call_apis_sequence(self.call_up_api,scroll_amount=scroll_amount)

    def call_apis_down(self,scroll_amount:str="") -> Dict[str, Any]:
        return self._call_apis_sequence(self.call_down_api,scroll_amount=scroll_amount)


    def call_apis_click(self, element_selector: str = "#su") -> Dict[str, Any]:
        """调用点击API并随后调用读取API"""
        return self._call_apis_sequence(self.call_click_api, element_selector)

    def call_apis_alert(self, message: str = "1") -> Dict[str, Any]:
        """调用弹窗API并随后调用读取API"""
        return self._call_apis_sequence(self.call_alert_api, message)

    def call_apis_openUrl(self, url: str = "https://www.baidu.com") -> Dict[str, Any]:
        """调用打开URL API并随后调用读取API"""
        return self._call_apis_sequence(self.call_openUrl_api, url)

    def call_apis_val(self, element_selector: str = "", val: Any = "") -> Dict[str, Any]:
        """调用设置值/获取值API并随后调用读取API"""
        return self._call_apis_sequence(self.call_val_api, element_selector, val)

    def call_apis_text(self, element_selector: str = "", val: Any = "") -> Dict[str, Any]:
        """调用设置文本/获取文本API并随后调用读取API"""
        return self._call_apis_sequence(self.call_text_api, element_selector, val)

    def call_apis_css(self, element_selector: str = "", val: Any = "",val1: Any = "") -> Dict[str, Any]:
        """调用设置CSS样式API并随后调用读取API"""
        return self._call_apis_sequence(self.call_css_api, element_selector, val,val1=val1)

    def call_apis_html(self, element_selector: str = "", val: Any = "") -> Dict[str, Any]:
        """调用设置HTML内容API并随后调用读取API"""
        return self._call_apis_sequence(self.call_html_api, element_selector, val)

    def call_apis_prop(self, element_selector: str = "", val: Any = "",val1: Any = "") -> Dict[str, Any]:
        """调用设置/获取属性API并随后调用读取API"""
        return self._call_apis_sequence(self.call_prop_api, element_selector, val,val1=val1)

    def call_apis_attr(self, element_selector: str = "", val: Any = "", val1: Any = "") -> Dict[str, Any]:
        """调用设置/获取特性API并随后调用读取API"""
        return self._call_apis_sequence(self.call_attr_api, element_selector, val,val1=val1)

    def call_apis_focus(self, element_selector: str = "#su") -> Dict[str, Any]:
        """调用聚焦元素API并随后调用读取API"""
        return self._call_apis_sequence(self.call_focus_api, element_selector)

    def call_apis_show(self, element_selector: str = "#su") -> Dict[str, Any]:
        """调用显示元素API并随后调用读取API"""
        return self._call_apis_sequence(self.call_show_api, element_selector)

    def call_apis_hide(self, element_selector: str = "#su") -> Dict[str, Any]:
        """调用隐藏元素API并随后调用读取API"""
        return self._call_apis_sequence(self.call_hide_api, element_selector)

    def call_apis_remove(self, element_selector: str = "#su") -> Dict[str, Any]:
        """调用移除元素API并随后调用读取API"""
        return self._call_apis_sequence(self.call_remove_api, element_selector)

    def call_apis_cookie(self, keys: str = "#su", val: Any = "", days: Any = "") -> Dict[str, Any]:
        """调用操作Cookie API并随后调用读取API"""
        return self._call_apis_sequence(self.call_cookie_api, keys, val, days=days)