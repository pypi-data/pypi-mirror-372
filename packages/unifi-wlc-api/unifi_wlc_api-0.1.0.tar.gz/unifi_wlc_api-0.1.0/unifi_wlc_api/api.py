import time
import urllib.parse
from typing import Dict, List, Union, Optional, Any, TypeVar

import requests

T = TypeVar('T')


class UnifiApi:
    """
    Python API client for Ubiquiti UniFi Controller

    Based on the PHP UniFi API Client
    """

    def __init__(self, controller_url: str, username: str, password: str, site: str = 'default',
                 version: str = '5.12.35', ssl_verify: bool = False):
        """
        初始化UniFi API客户端

        Args:
            controller_url: UniFi控制器URL (例如: 'https://unifi.example.com:8443')
            username: UniFi控制器用户名
            password: UniFi控制器密码
            site: UniFi站点名称，默认为'default'
            version: UniFi控制器版本，默认为'5.12.35'
            ssl_verify: 是否验证SSL证书，默认为True
        """
        self.controller_url = controller_url.rstrip('/')
        self.username = username
        self.password = password
        self.site = site
        self.version = version
        self.ssl_verify = ssl_verify
        self.is_unifi_os = False
        self.cookies = {}
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.session = requests.Session()
        self.session.verify = ssl_verify

    def login(self) -> bool:
        """
        登录到UniFi控制器

        Returns:
            bool: 登录成功返回True，否则返回False
        """

        # 根据是否为UniFi OS设备选择登录路径
        login_url = f"{self.controller_url}/api/login"
        payload = {"username": self.username, "password": self.password}

        try:
            response = self.session.post(login_url, json=payload, headers=self.headers)
            if response.status_code == 200:
                self.cookies = self.session.cookies.get_dict()
                return True
            return False
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False

    def logout(self) -> bool:
        """
        从UniFi控制器注销

        Returns:
            bool: 注销成功返回True，否则返回False
        """
        logout_url = f"{self.controller_url}/api/logout" if not self.is_unifi_os else f"{self.controller_url}/api/auth/logout"
        try:
            response = self.session.post(logout_url, headers=self.headers)
            return response.status_code == 200
        except Exception as e:
            print(f"Logout failed: {str(e)}")
            return False

    def _fetch_results(self, endpoint: str, payload: Optional[Dict] = None, method: str = 'POST') -> Any:
        """
        向UniFi控制器发送请求并获取结果

        Args:
            endpoint: API端点
            payload: 请求负载
            method: HTTP方法，默认为'POST'

        Returns:
            Any: API响应数据
        """
        url = f"{self.controller_url}{endpoint}"

        try:
            if method.upper() == 'GET':
                response = self.session.get(url, headers=self.headers)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=payload, headers=self.headers)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=self.headers)
            else:  # POST
                response = self.session.post(url, json=payload, headers=self.headers)

            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    return data['data']
                return data
            else:
                print(f"API request failed with status code {response.status_code}")
                return False
        except Exception as e:
            print(f"API request failed: {str(e)}")
            return False

    def _fetch_results_boolean(self, endpoint: str, payload: Optional[Dict] = None, method: str = 'POST') -> bool:
        """
        向UniFi控制器发送请求并获取布尔结果

        Args:
            endpoint: API端点
            payload: 请求负载
            method: HTTP方法，默认为'POST'

        Returns:
            bool: 请求成功返回True，否则返回False
        """
        result = self._fetch_results(endpoint, payload, method)
        return result is not False

    # 客户端设备相关方法

    def list_clients(self, mac: Optional[str] = None) -> Union[List[Dict], Dict, bool]:
        """
        获取在线客户端设备

        Args:
            mac: 可选，客户端MAC地址

        Returns:
            Union[List[Dict], Dict, bool]: 客户端设备列表或单个客户端设备信息
        """
        if mac:
            mac = mac.lower().strip()
        return self._fetch_results(f"/api/s/{self.site}/stat/sta/{mac or ''}", method='GET')

    def list_active_clients(self, include_traffic_usage: bool = True, include_unifi_devices: bool = True) -> Union[
        List[Dict], bool]:
        """
        获取活跃的客户端设备

        Args:
            include_traffic_usage: 是否包含流量使用情况
            include_unifi_devices: 是否包含UniFi设备

        Returns:
            Union[List[Dict], bool]: 活跃客户端设备列表
        """
        query = urllib.parse.urlencode({
            'include_traffic_usage': include_traffic_usage,
            'include_unifi_devices': include_unifi_devices
        })
        return self._fetch_results(f"/v2/api/site/{self.site}/clients/active?{query}", method='GET')

    def list_clients_history(self, only_non_blocked: bool = True, include_unifi_devices: bool = True,
                             within_hours: int = 0) -> Union[List[Dict], bool]:
        """
        获取客户端设备历史记录（离线客户端设备）

        Args:
            only_non_blocked: 是否只包含未被阻止的客户端设备
            include_unifi_devices: 是否包含UniFi设备
            within_hours: 设备离线的小时数（0表示无限制）

        Returns:
            Union[List[Dict], bool]: 离线客户端设备列表
        """
        query = urllib.parse.urlencode({
            'only_non_blocked': only_non_blocked,
            'include_unifi_devices': include_unifi_devices,
            'within_hours': within_hours
        })
        return self._fetch_results(f"/v2/api/site/{self.site}/clients/history?{query}", method='GET')

    def stat_client(self, mac: str) -> Union[Dict, bool]:
        """
        获取单个客户端设备的详细信息

        Args:
            mac: 客户端设备MAC地址

        Returns:
            Union[Dict, bool]: 客户端设备信息
        """
        return self._fetch_results(f"/api/s/{self.site}/stat/user/{mac.lower().strip()}", method='GET')

    def set_client_name(self, client_id: str, name: str) -> Union[Dict, bool]:
        """
        更新客户端设备名称

        Args:
            client_id: 客户端设备ID
            name: 新的客户端设备名称

        Returns:
            Union[Dict, bool]: 更新后的客户端设备信息
        """
        if not name:
            return False

        payload = {
            '_id': client_id,
            'name': name
        }
        return self._fetch_results(f"/api/s/{self.site}/rest/user/{client_id.strip()}", payload, method='PUT')

    def set_sta_name(self, user_id: str, name: str = '') -> bool:
        """
        添加/修改/删除客户端设备名称

        Args:
            user_id: 客户端设备ID
            name: 名称，为空时删除现有名称

        Returns:
            bool: 操作成功返回True，否则返回False
        """
        payload = {'name': name}
        return self._fetch_results_boolean(f"/api/s/{self.site}/upd/user/{user_id.strip()}", payload)

    def set_sta_note(self, user_id: str, note: str = '') -> bool:
        """
        添加/修改/删除客户端设备备注

        Args:
            user_id: 客户端设备ID
            note: 备注，为空时删除现有备注

        Returns:
            bool: 操作成功返回True，否则返回False
        """
        payload = {'note': note}
        return self._fetch_results_boolean(f"/api/s/{self.site}/upd/user/{user_id.strip()}", payload)

    def block_sta(self, mac: str) -> bool:
        """
        阻止客户端设备

        Args:
            mac: 客户端设备MAC地址

        Returns:
            bool: 操作成功返回True，否则返回False
        """
        payload = {'cmd': 'block-sta', 'mac': mac.lower()}
        return self._fetch_results_boolean(f"/api/s/{self.site}/cmd/stamgr", payload)

    def unblock_sta(self, mac: str) -> bool:
        """
        解除阻止客户端设备

        Args:
            mac: 客户端设备MAC地址

        Returns:
            bool: 操作成功返回True，否则返回False
        """
        payload = {'cmd': 'unblock-sta', 'mac': mac.lower()}
        return self._fetch_results_boolean(f"/api/s/{self.site}/cmd/stamgr", payload)

    def reconnect_sta(self, mac: str) -> bool:
        """
        重新连接客户端设备

        Args:
            mac: 客户端设备MAC地址

        Returns:
            bool: 操作成功返回True，否则返回False
        """
        payload = {'cmd': 'kick-sta', 'mac': mac.lower()}
        return self._fetch_results_boolean(f"/api/s/{self.site}/cmd/stamgr", payload)

    def authorize_guest(self, mac: str, minutes: int, up: Optional[int] = None,
                        down: Optional[int] = None, megabytes: Optional[int] = None,
                        ap_mac: Optional[str] = None) -> bool:
        """
        授权访客设备

        Args:
            mac: 客户端设备MAC地址
            minutes: 授权时长（分钟）
            up: 上传速率限制
            down: 下载速率限制
            megabytes: 流量限制（MB）
            ap_mac: 接入点MAC地址

        Returns:
            bool: 操作成功返回True，否则返回False
        """
        payload = {'cmd': 'authorize-guest', 'mac': mac.lower(), 'minutes': minutes}

        if up is not None:
            payload['up'] = up

        if down is not None:
            payload['down'] = down

        if megabytes is not None:
            payload['bytes'] = megabytes

        if ap_mac is not None:
            # 验证MAC地址格式
            if self._is_valid_mac(ap_mac):
                payload['ap_mac'] = ap_mac.lower()

        return self._fetch_results_boolean(f"/api/s/{self.site}/cmd/stamgr", payload)

    def unauthorize_guest(self, mac: str) -> bool:
        """
        取消授权访客设备

        Args:
            mac: 客户端设备MAC地址

        Returns:
            bool: 操作成功返回True，否则返回False
        """
        payload = {'cmd': 'unauthorize-guest', 'mac': mac.lower()}
        return self._fetch_results_boolean(f"/api/s/{self.site}/cmd/stamgr", payload)

    # 设备管理相关方法

    def list_devices(self, macs: Union[str, List[str]] = []) -> Union[List[Dict], bool]:
        """
        获取UniFi设备列表

        Args:
            macs: 可选，设备MAC地址或MAC地址列表

        Returns:
            Union[List[Dict], bool]: UniFi设备列表
        """
        if isinstance(macs, str):
            macs = [macs]
        payload = {'macs': [mac.lower() for mac in macs]}
        return self._fetch_results(f"/api/s/{self.site}/stat/device", payload)

    def list_devices_basic(self) -> Union[List[Dict], bool]:
        """
        获取UniFi设备基本信息列表

        Returns:
            Union[List[Dict], bool]: UniFi设备基本信息列表
        """
        return self._fetch_results(f"/api/s/{self.site}/stat/device-basic", method='GET')

    def adopt_device(self, macs: Union[str, List[str]]) -> bool:
        """
        将设备添加到当前站点

        Args:
            macs: 设备MAC地址或MAC地址列表

        Returns:
            bool: 操作成功返回True，否则返回False
        """
        if isinstance(macs, str):
            macs = [macs]
        payload = {
            'macs': [mac.lower() for mac in macs],
            'cmd': 'adopt'
        }
        return self._fetch_results_boolean(f"/api/s/{self.site}/cmd/devmgr", payload)

    def restart_device(self, macs: Union[str, List[str]], reboot_type: str = 'soft') -> bool:
        """
        重启设备

        Args:
            macs: 设备MAC地址或MAC地址列表
            reboot_type: 重启类型，'soft'或'hard'

        Returns:
            bool: 操作成功返回True，否则返回False
        """
        if isinstance(macs, str):
            macs = [macs]

        payload = {
            'cmd': 'restart',
            'macs': [mac.lower() for mac in macs]
        }

        if reboot_type and reboot_type.lower() in ['soft', 'hard']:
            payload['reboot_type'] = reboot_type.lower()

        return self._fetch_results_boolean(f"/api/s/{self.site}/cmd/devmgr", payload)

    def force_provision(self, mac: Union[str, List[str]]) -> bool:
        """
        强制配置设备

        Args:
            mac: 设备MAC地址或MAC地址列表

        Returns:
            bool: 操作成功返回True，否则返回False
        """
        if isinstance(mac, str):
            mac = [mac]

        payload = {
            'cmd': 'force-provision',
            'macs': [m.lower() for m in mac]
        }

        return self._fetch_results_boolean(f"/api/s/{self.site}/cmd/devmgr/", payload)

    def power_cycle_switch_port(self, mac: str, port_idx: int) -> bool:
        """
        对交换机端口进行断电重启

        Args:
            mac: 交换机MAC地址
            port_idx: 端口索引

        Returns:
            bool: 操作成功返回True，否则返回False
        """
        payload = {'mac': mac.lower(), 'port_idx': port_idx, 'cmd': 'power-cycle'}
        return self._fetch_results_boolean(f"/api/s/{self.site}/cmd/devmgr", payload)

    def spectrum_scan(self, mac: str) -> bool:
        """
        触发AP进行RF扫描

        Args:
            mac: AP的MAC地址

        Returns:
            bool: 操作成功返回True，否则返回False
        """
        payload = {'cmd': 'spectrum-scan', 'mac': mac.lower()}
        return self._fetch_results_boolean(f"/api/s/{self.site}/cmd/devmgr", payload)

    def spectrum_scan_state(self, mac: str) -> Union[Dict, bool]:
        """
        检查AP的RF扫描状态

        Args:
            mac: AP的MAC地址

        Returns:
            Union[Dict, bool]: RF扫描状态信息
        """
        return self._fetch_results(f"/api/s/{self.site}/stat/spectrum-scan/{mac.lower().strip()}", method='GET')

    def set_device_settings_base(self, device_id: str, payload: Dict) -> bool:
        """
        更新设备基本设置

        Args:
            device_id: 设备ID
            payload: 设备配置

        Returns:
            bool: 操作成功返回True，否则返回False
        """
        return self._fetch_results_boolean(f"/api/s/{self.site}/rest/device/{device_id.strip()}", payload, method='PUT')

    # 站点管理相关方法

    def list_sites(self) -> Union[List[Dict], bool]:
        """
        获取站点列表

        Returns:
            Union[List[Dict], bool]: 站点列表
        """
        return self._fetch_results("/api/self/sites", method='GET')

    def stat_sites(self) -> Union[List[Dict], bool]:
        """
        获取站点统计信息

        Returns:
            Union[List[Dict], bool]: 站点统计信息
        """
        return self._fetch_results("/api/stat/sites", method='GET')

    def create_site(self, description: str) -> Union[Dict, bool]:
        """
        创建站点

        Args:
            description: 站点描述

        Returns:
            Union[Dict, bool]: 新站点信息
        """
        payload = {'desc': description, 'cmd': 'add-site'}
        return self._fetch_results(f"/api/s/{self.site}/cmd/sitemgr", payload)

    def delete_site(self, site_id: str) -> bool:
        """
        删除站点

        Args:
            site_id: 站点ID

        Returns:
            bool: 操作成功返回True，否则返回False
        """
        payload = {'site': site_id, 'cmd': 'delete-site'}
        return self._fetch_results_boolean(f"/api/s/{self.site}/cmd/sitemgr", payload)

    def set_site_name(self, site_name: str) -> bool:
        """
        修改当前站点名称

        Args:
            site_name: 新站点名称

        Returns:
            bool: 操作成功返回True，否则返回False
        """
        payload = {'desc': site_name, 'cmd': 'update-site'}
        return self._fetch_results_boolean(f"/api/s/{self.site}/cmd/sitemgr", payload)

    # 统计数据相关方法

    def stat_5minutes_site(self, start: Optional[int] = None, end: Optional[int] = None,
                           attribs: Optional[List[str]] = None) -> Union[List[Dict], bool]:
        """
        获取站点5分钟统计数据

        Args:
            start: 开始时间戳（毫秒）
            end: 结束时间戳（毫秒）
            attribs: 要获取的属性列表

        Returns:
            Union[List[Dict], bool]: 站点5分钟统计数据
        """
        end = end if end is not None else int(time.time() * 1000)
        start = start if start is not None else end - (12 * 3600 * 1000)
        default_attribs = ['bytes', 'wan-tx_bytes', 'wan-rx_bytes', 'wlan_bytes', 'num_sta', 'lan-num_sta',
                           'wlan-num_sta', 'time']
        attribs = attribs if attribs is not None else default_attribs
        if 'time' not in attribs:
            attribs = ['time'] + attribs

        payload = {'attrs': attribs, 'start': start, 'end': end}
        return self._fetch_results(f"/api/s/{self.site}/stat/report/5minutes.site", payload)

    def stat_hourly_site(self, start: Optional[int] = None, end: Optional[int] = None,
                         attribs: Optional[List[str]] = None) -> Union[List[Dict], bool]:
        """
        获取站点每小时统计数据

        Args:
            start: 开始时间戳（毫秒）
            end: 结束时间戳（毫秒）
            attribs: 要获取的属性列表

        Returns:
            Union[List[Dict], bool]: 站点每小时统计数据
        """
        end = end if end is not None else int(time.time() * 1000)
        start = start if start is not None else end - (7 * 24 * 3600 * 1000)
        default_attribs = ['bytes', 'wan-tx_bytes', 'wan-rx_bytes', 'wlan_bytes', 'num_sta', 'lan-num_sta',
                           'wlan-num_sta', 'time']
        attribs = attribs if attribs is not None else default_attribs
        if 'time' not in attribs:
            attribs = ['time'] + attribs

        payload = {'attrs': attribs, 'start': start, 'end': end}
        return self._fetch_results(f"/api/s/{self.site}/stat/report/hourly.site", payload)

    def stat_daily_site(self, start: Optional[int] = None, end: Optional[int] = None,
                        attribs: Optional[List[str]] = None) -> Union[List[Dict], bool]:
        """
        获取站点每日统计数据

        Args:
            start: 开始时间戳（毫秒）
            end: 结束时间戳（毫秒）
            attribs: 要获取的属性列表

        Returns:
            Union[List[Dict], bool]: 站点每日统计数据
        """
        end = end if end is not None else int(time.time() * 1000)
        start = start if start is not None else end - (7 * 24 * 3600 * 1000)
        default_attribs = ['bytes', 'wan-tx_bytes', 'wan-rx_bytes', 'wlan_bytes', 'num_sta', 'lan-num_sta',
                           'wlan-num_sta', 'time']
        attribs = attribs if attribs is not None else default_attribs
        if 'time' not in attribs:
            attribs = ['time'] + attribs

        payload = {'attrs': attribs, 'start': start, 'end': end}
        return self._fetch_results(f"/api/s/{self.site}/stat/report/daily.site", payload)

    def stat_5minutes_user(self, mac: Optional[str] = None, start: Optional[int] = None,
                           end: Optional[int] = None, attribs: Optional[List[str]] = None) -> Union[List[Dict], bool]:
        """
        获取用户5分钟统计数据

        Args:
            mac: 客户端MAC地址
            start: 开始时间戳（毫秒）
            end: 结束时间戳（毫秒）
            attribs: 要获取的属性列表

        Returns:
            Union[List[Dict], bool]: 用户5分钟统计数据
        """
        end = end if end is not None else int(time.time() * 1000)
        start = start if start is not None else end - (12 * 3600 * 1000)
        default_attribs = ['time', 'rx_bytes', 'tx_bytes']
        attribs = attribs if attribs is not None else default_attribs
        if 'time' not in attribs:
            attribs = ['time'] + attribs

        payload = {'attrs': attribs, 'start': start, 'end': end}
        if mac:
            payload['mac'] = mac.lower()

        return self._fetch_results(f"/api/s/{self.site}/stat/report/5minutes.user", payload)

    def stat_hourly_user(self, mac: Optional[str] = None, start: Optional[int] = None,
                         end: Optional[int] = None, attribs: Optional[List[str]] = None) -> Union[List[Dict], bool]:
        """
        获取用户每小时统计数据

        Args:
            mac: 客户端MAC地址
            start: 开始时间戳（毫秒）
            end: 结束时间戳（毫秒）
            attribs: 要获取的属性列表

        Returns:
            Union[List[Dict], bool]: 用户每小时统计数据
        """
        end = end if end is not None else int(time.time() * 1000)
        start = start if start is not None else end - (7 * 24 * 3600 * 1000)
        default_attribs = ['time', 'rx_bytes', 'tx_bytes']
        attribs = attribs if attribs is not None else default_attribs
        if 'time' not in attribs:
            attribs = ['time'] + attribs

        payload = {'attrs': attribs, 'start': start, 'end': end}
        if mac:
            payload['mac'] = mac.lower()

        return self._fetch_results(f"/api/s/{self.site}/stat/report/hourly.user", payload)

    def stat_daily_user(self, mac: Optional[str] = None, start: Optional[int] = None,
                        end: Optional[int] = None, attribs: Optional[List[str]] = None) -> Union[List[Dict], bool]:
        """
        获取用户每日统计数据

        Args:
            mac: 客户端MAC地址
            start: 开始时间戳（毫秒）
            end: 结束时间戳（毫秒）
            attribs: 要获取的属性列表

        Returns:
            Union[List[Dict], bool]: 用户每日统计数据
        """
        end = end if end is not None else int(time.time() * 1000)
        start = start if start is not None else end - (7 * 24 * 3600 * 1000)
        default_attribs = ['time', 'rx_bytes', 'tx_bytes']
        attribs = attribs if attribs is not None else default_attribs
        if 'time' not in attribs:
            attribs = ['time'] + attribs

        payload = {'attrs': attribs, 'start': start, 'end': end}
        if mac:
            payload['mac'] = mac.lower()

        return self._fetch_results(f"/api/s/{self.site}/stat/report/daily.user", payload)

    def stat_monthly_user(self, mac: Optional[str] = None, start: Optional[int] = None,
                          end: Optional[int] = None, attribs: Optional[List[str]] = None) -> Union[List[Dict], bool]:
        """
        获取用户每月统计数据

        Args:
            mac: 客户端MAC地址
            start: 开始时间戳（毫秒）
            end: 结束时间戳（毫秒）
            attribs: 要获取的属性列表

        Returns:
            Union[List[Dict], bool]: 用户每月统计数据
        """
        end = end if end is not None else int(time.time() * 1000)
        start = start if start is not None else end - (13 * 7 * 24 * 3600 * 1000)
        default_attribs = ['time', 'rx_bytes', 'tx_bytes']
        attribs = attribs if attribs is not None else default_attribs
        if 'time' not in attribs:
            attribs = ['time'] + attribs

        payload = {'attrs': attribs, 'start': start, 'end': end}
        if mac:
            payload['mac'] = mac.lower()

        return self._fetch_results(f"/api/s/{self.site}/stat/report/monthly.user", payload)

    def stat_allusers(self, historyhours: int = 8760) -> Union[List[Dict], bool]:
        """
        获取在给定时间范围内连接到站点的客户端设备

        Args:
            historyhours: 回溯的小时数（默认为8760小时或1年）

        Returns:
            Union[List[Dict], bool]: 客户端设备列表
        """
        payload = {'type': 'all', 'conn': 'all', 'within': historyhours}
        return self._fetch_results(f"/api/s/{self.site}/stat/alluser", payload)

    def list_guests(self, within: int = 8760) -> Union[List[Dict], bool]:
        """
        获取访客设备

        Args:
            within: 回溯的小时数（默认为8760小时或1年）

        Returns:
            Union[List[Dict], bool]: 访客设备列表
        """
        payload = {'within': within}
        return self._fetch_results(f"/api/s/{self.site}/stat/guest", payload)

    # 网络配置相关方法

    def list_networkconf(self, network_id: str = '') -> Union[List[Dict], Dict, bool]:
        """
        获取网络配置

        Args:
            network_id: 可选，网络ID

        Returns:
            Union[List[Dict], Dict, bool]: 网络配置列表或单个网络配置
        """
        return self._fetch_results(f"/api/s/{self.site}/rest/networkconf/{network_id.strip()}", method='GET')

    def create_network(self, payload: Dict) -> Union[Dict, bool]:
        """
        创建网络

        Args:
            payload: 网络配置

        Returns:
            Union[Dict, bool]: 新网络信息
        """
        return self._fetch_results(f"/api/s/{self.site}/rest/networkconf", payload)

    def set_networksettings_base(self, network_id: str, payload: Dict) -> bool:
        """
        更新网络设置

        Args:
            network_id: 网络ID
            payload: 网络配置

        Returns:
            bool: 操作成功返回True，否则返回False
        """
        return self._fetch_results_boolean(f"/api/s/{self.site}/rest/networkconf/{network_id.strip()}", payload,
                                           method='PUT')

    def delete_network(self, network_id: str) -> bool:
        """
        删除网络

        Args:
            network_id: 网络ID

        Returns:
            bool: 操作成功返回True，否则返回False
        """
        return self._fetch_results_boolean(f"/api/s/{self.site}/rest/networkconf/{network_id.strip()}", method='DELETE')

    # WLAN配置相关方法

    def list_wlanconf(self, wlan_id: str = '') -> Union[List[Dict], Dict, bool]:
        """
        获取WLAN配置

        Args:
            wlan_id: 可选，WLAN ID

        Returns:
            Union[List[Dict], Dict, bool]: WLAN配置列表或单个WLAN配置
        """
        return self._fetch_results(f"/api/s/{self.site}/rest/wlanconf/{wlan_id.strip()}", method='GET')

    def create_wlan(self, name: str, x_passphrase: str, usergroup_id: str, wlangroup_id: str,
                    enabled: bool = True, hide_ssid: bool = False, is_guest: bool = False,
                    security: str = 'open', wpa_mode: str = 'wpa2', wpa_enc: str = 'ccmp',
                    vlan_enabled: Optional[bool] = None, vlan_id: Optional[str] = None,
                    uapsd_enabled: bool = False, schedule_enabled: bool = False,
                    schedule: List = [], ap_group_ids: Optional[List] = None,
                    payload: Dict = {}) -> bool:
        """
        创建WLAN

        Args:
            name: SSID
            x_passphrase: 预共享密钥
            usergroup_id: 用户组ID
            wlangroup_id: WLAN组ID
            enabled: 是否启用WLAN
            hide_ssid: 是否隐藏SSID
            is_guest: 是否为访客WLAN
            security: 安全类型（open, wep, wpapsk, wpaeap）
            wpa_mode: WPA模式（wpa, wpa2, ...）
            wpa_enc: 加密方式（auto, ccmp）
            vlan_enabled: 是否启用VLAN
            vlan_id: VLAN ID
            uapsd_enabled: 是否启用UAPSD
            schedule_enabled: 是否启用WLAN计划
            schedule: 计划规则
            ap_group_ids: AP组ID列表
            payload: 附加参数

        Returns:
            bool: 操作成功返回True，否则返回False
        """
        merged_payload = {
            'name': name.strip(),
            'usergroup_id': usergroup_id.strip(),
            'wlangroup_id': wlangroup_id.strip(),
            'enabled': enabled,
            'hide_ssid': hide_ssid,
            'is_guest': is_guest,
            'security': security.strip(),
            'wpa_mode': wpa_mode.strip(),
            'wpa_enc': wpa_enc.strip(),
            'uapsd_enabled': uapsd_enabled,
            'schedule_enabled': schedule_enabled,
            'schedule': schedule
        }

        if vlan_id:
            merged_payload['networkconf_id'] = vlan_id

        if x_passphrase and security != 'open':
            merged_payload['x_passphrase'] = x_passphrase.strip()

        if ap_group_ids:
            merged_payload['ap_group_ids'] = ap_group_ids

        # 合并附加参数
        merged_payload.update(payload)

        return self._fetch_results_boolean(f"/api/s/{self.site}/add/wlanconf", merged_payload)

    # 标签相关方法

    def list_tags(self) -> Union[List[Dict], bool]:
        """
        获取标签列表

        Returns:
            Union[List[Dict], bool]: 标签列表
        """
        return self._fetch_results(f"/api/s/{self.site}/rest/tag", method='GET')

    def create_tag(self, name: str, macs: Optional[List[str]] = None) -> bool:
        """
        创建标签

        Args:
            name: 标签名称
            macs: 可选，要标记的设备MAC地址列表

        Returns:
            bool: 操作成功返回True，否则返回False
        """
        payload = {'name': name}

        if macs:
            payload['member_table'] = macs

        return self._fetch_results_boolean(f"/api/s/{self.site}/rest/tag", payload)

    def set_tagged_devices(self, macs: List[str], tag_id: str) -> bool:
        """
        设置标记的设备

        Args:
            macs: 要标记的设备MAC地址列表
            tag_id: 标签ID

        Returns:
            bool: 操作成功返回True，否则返回False
        """
        payload = {'member_table': macs}
        return self._fetch_results_boolean(f"/api/s/{self.site}/rest/tag/{tag_id}", payload, method='PUT')

    def get_tag(self, tag_id: str) -> Union[Dict, bool]:
        """
        获取标签

        Args:
            tag_id: 标签ID

        Returns:
            Union[Dict, bool]: 标签信息
        """
        return self._fetch_results(f"/api/s/{self.site}/rest/tag/{tag_id}", method='GET')

    def delete_tag(self, tag_id: str) -> bool:
        """
        删除标签

        Args:
            tag_id: 标签ID

        Returns:
            bool: 操作成功返回True，否则返回False
        """
        return self._fetch_results_boolean(f"/api/s/{self.site}/rest/tag/{tag_id}", method='DELETE')

    # 事件和警报相关方法

    def list_events(self, historyhours: int = 720, start: int = 0, limit: int = 3000) -> Union[List[Dict], bool]:
        """
        获取事件列表

        Args:
            historyhours: 回溯的小时数
            start: 起始索引
            limit: 返回的最大事件数

        Returns:
            Union[List[Dict], bool]: 事件列表
        """
        payload = {
            '_sort': '-time',
            'within': historyhours,
            'type': None,
            '_start': start,
            '_limit': limit
        }
        return self._fetch_results(f"/api/s/{self.site}/stat/event", payload)

    def list_alarms(self, payload: Dict = {}) -> Union[List[Dict], bool]:
        """
        获取警报列表

        Args:
            payload: 可选，过滤条件

        Returns:
            Union[List[Dict], bool]: 警报列表
        """
        return self._fetch_results(f"/api/s/{self.site}/list/alarm", payload)

    def count_alarms(self, archived: Optional[bool] = None) -> Union[Dict, bool]:
        """
        统计警报数量

        Args:
            archived: 可选，是否包括已归档的警报

        Returns:
            Union[Dict, bool]: 警报数量
        """
        path_suffix = '?archived=false' if archived is False else ''
        return self._fetch_results(f"/api/s/{self.site}/cnt/alarm{path_suffix}", method='GET')

    def archive_alarm(self, alarm_id: str = '') -> bool:
        """
        归档警报

        Args:
            alarm_id: 可选，警报ID，为空时归档所有警报

        Returns:
            bool: 操作成功返回True，否则返回False
        """
        payload = {'cmd': 'archive-all-alarms'}

        if alarm_id:
            payload = {'_id': alarm_id, 'cmd': 'archive-alarm'}

        return self._fetch_results_boolean(f"/api/s/{self.site}/cmd/evtmgr", payload)

    # 固件相关方法

    def list_firmware(self, type: str = 'available') -> Union[List[Dict], bool]:
        """
        获取固件版本

        Args:
            type: 固件类型，'available'或'cached'

        Returns:
            Union[List[Dict], bool]: 固件版本列表
        """
        if type not in ['available', 'cached']:
            return False

        payload = {'cmd': f'list-{type}'}
        return self._fetch_results(f"/api/s/{self.site}/cmd/firmware", payload)

    def start_rolling_upgrade(self, payload: List[str] = ['uap', 'usw', 'ugw', 'uxg']) -> bool:
        """
        开始滚动升级

        Args:
            payload: 要升级的设备类型列表

        Returns:
            bool: 操作成功返回True，否则返回False
        """
        return self._fetch_results_boolean(f"/api/s/{self.site}/cmd/devmgr/set-rollupgrade", payload)

    def cancel_rolling_upgrade(self) -> bool:
        """
        取消滚动升级

        Returns:
            bool: 操作成功返回True，否则返回False
        """
        payload = {'cmd': 'unset-rollupgrade'}
        return self._fetch_results_boolean(f"/api/s/{self.site}/cmd/devmgr", payload)

    # 系统日志相关方法

    def get_system_log(self, class_name: str = 'device-alert', start: Optional[int] = None,
                       end: Optional[int] = None, page_number: int = 0, page_size: int = 100,
                       custom_payload: Dict = {}) -> Union[Dict, bool]:
        """
        获取系统日志

        Args:
            class_name: 日志类别
            start: 开始时间戳（毫秒）
            end: 结束时间戳（毫秒）
            page_number: 页码
            page_size: 每页条数
            custom_payload: 自定义参数

        Returns:
            Union[Dict, bool]: 系统日志
        """
        end = end if end is not None else int(time.time() * 1000)
        start = start if start is not None else end - (7 * 24 * 3600 * 1000)

        payload = {
            'pageNumber': page_number,
            'pageSize': page_size,
            'timestampFrom': start,
            'timestampTo': end
        }

        if class_name == 'next-ai-alert':
            payload['nextAiCategory'] = ['CLIENT', 'DEVICE', 'INTERNET', 'VPN']
        elif class_name == 'admin-activity':
            payload['activity_keys'] = ['ACCESSED_NETWORK_WEB', 'ACCESSED_NETWORK_IOS', 'ACCESSED_NETWORK_ANDROID']
            payload['change_keys'] = ['CLIENT', 'DEVICE', 'HOTSPOT', 'INTERNET', 'NETWORK', 'PROFILE', 'ROUTING',
                                      'SECURITY', 'SYSTEM', 'VPN', 'WIFI']
        elif class_name == 'update-alert':
            payload['systemLogDeviceTypes'] = ['GATEWAYS', 'SWITCHES', 'ACCESS_POINT', 'SMART_POWER',
                                               'BUILDING_TO_BUILDING_BRIDGES', 'UNIFI_LTE']

        # 合并自定义参数
        payload.update(custom_payload)

        return self._fetch_results(f"/api/s/{self.site}/stat/logs", payload)

    # 流氓AP相关方法

    def list_rogueaps(self, within: int = 1) -> Union[List[Dict], bool]:
        """
        获取流氓/邻近接入点

        Args:
            within: 回溯的小时数（默认为24小时）

        Returns:
            Union[List[Dict], bool]: 流氓/邻近接入点对象列表
        """
        payload = {'within': within}
        return self._fetch_results(f"/api/s/{self.site}/stat/rogueap", payload, "POST")

    def list_known_rogueaps(self) -> Union[List[Dict], bool]:
        """
        获取已知的流氓接入点

        Returns:
            Union[List[Dict], bool]: 已知的流氓接入点对象列表
        """
        return self._fetch_results(f"/api/s/{self.site}/rest/rogueknown", method='GET')

    # 辅助方法

    def _is_valid_mac(self, mac: str) -> bool:
        """
        验证MAC地址格式

        Args:
            mac: MAC地址

        Returns:
            bool: 格式正确返回True，否则返回False
        """
        import re
        pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
        return bool(re.match(pattern, mac))

