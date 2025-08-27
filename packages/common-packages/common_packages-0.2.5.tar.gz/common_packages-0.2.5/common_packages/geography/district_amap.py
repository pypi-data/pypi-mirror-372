import requests


class ChinaDistrictAmap:
    """获取中国的行政区域
    使用 高德地图 获取中国的行政区域信息

    city_code: 城市编码。只有市级行政区有citycode。
        - 县/区、城镇/街道 没有自己的citycode,使用所在市的citycode
        - 省级行政区没有citycode
    adcode: 行政区域编码。
        - 省、市、区/县 的adcode是唯一的
        - 城镇/街道 使用所在区/县的adcode
    """

    def __init__(self, key: str):
        self.key = key
        self.base_url = "https://restapi.amap.com/v3/config/district"
        self.country = "中华人民共和国"

    def _send_request(self, url: str) -> dict:
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("请求高德地图API失败")
        res = response.json()

        # 1. 校验响应状态
        status = res["status"]
        assert status == "1", f"请求高德地图API失败，status: {status}"
        info = res.get("info")
        assert info == "OK", f"请求高德地图API失败，info: {info}"
        infocode = res.get("infocode")
        assert infocode == "10000", f"请求高德地图API失败，infocode: {infocode}"
        # count = res["count"]

        # 2. 校验响应结构
        districts = res["districts"]
        assert len(districts) == 1

        # 3. 将实际有效的内容进行提取返回
        response_data_info = districts[0]
        return response_data_info

    def get_privince(self) -> list[dict]:
        """获取省份

        "citycode": [],
        "adcode": "410000",
        "name": "河南省",
        "center": "113.753094,34.767052",
        "level": "province",
        "districts": []
        """
        url = f"{self.base_url}?key={self.key}&keywords={self.country}"

        china_info = self._send_request(url)

        # 获取国家信息，判断是否是中国
        china_adcode = china_info["adcode"]
        china_name = china_info["name"]
        level = china_info["level"]
        assert china_adcode == "100000"
        assert china_name == self.country
        assert level == "country"

        privinces: list[dict] = china_info["districts"]

        return privinces

    def get_city(self, privince_name: str, privince_adcode: str) -> list[dict]:
        """获取指定省份的所有城市
        privince_name: 省份名称
        privince_adcode: 省份行政区域编码

        "citycode": "0379", # 城市编码
        "adcode": "410300", # 行政区域编码
        "name": "洛阳市",
        "center": "112.453895,34.619702",
        "level": "city",
        "districts": []
        """
        url = f"{self.base_url}?key={self.key}&keywords={privince_name}"
        privince_info = self._send_request(url)

        # chekc
        privince_adcode_res = privince_info["adcode"]
        privince_name_res = privince_info["name"]
        level = privince_info["level"]
        assert level == "province"
        assert privince_name_res == privince_name
        assert privince_adcode_res == privince_adcode

        city_info: list[dict] = privince_info["districts"]
        return city_info

    def get_district(
        self, city_name: str, city_code: str, city_adcode: str
    ) -> list[dict]:
        """获取指定城市的所有区/县
        city_name: 城市名称
        city_code: 城市编码
        city_adcode: 城市行政区域编码

        返回结果:
        "citycode": "0379",
        "adcode": "410323",
        "name": "新安县",
        "center": "112.13246,34.728909",
        "level": "district",
        "districts": []
        """
        url = f"{self.base_url}?key={self.key}&keywords={city_name}"
        city_info = self._send_request(url)

        # check
        city_name_res = city_info["name"]
        city_code_res = city_info["citycode"]
        city_adcode_res = city_info["adcode"]
        level = city_info["level"]
        assert level == "city"
        assert city_name_res == city_name
        assert city_code_res == city_code
        assert city_adcode_res == city_adcode

        district_info: list[dict] = city_info["districts"]
        return district_info
