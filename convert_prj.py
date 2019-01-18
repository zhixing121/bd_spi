import json
import requests
import math
import time

key = "tsNfn92Z2YiZRpwRcLQL7yxm7XhQRaCC"  # 这里填写你的百度开放平台的key

x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 扁率
 
 
def geocode(address):
    """
    利用百度geocoding服务解析地址获取位置坐标
    :param address:需要解析的地址
    :return:
    """

    geocoding_url = "http://api.map.baidu.com/geocoder/v2/?address={}&output=json&ak={}".format(address,key)
    res = requests.get(geocoding_url)
    if res.status_code == 200:
        res_json = res.json()
        status = res_json.get('status')
        if status == 0:
            result = res_json.get('result')
            lng = result.get('location').get('lng')
            lat = result.get('location').get('lat')
            return [lng, lat]
        else:
            return None
    else:
        return None
 
 
def gcj02_to_bd09(lng, lat):
    """
    火星坐标系(GCJ-02)转百度坐标系(BD-09)
    谷歌、高德——>百度
    :param lng:火星坐标经度
    :param lat:火星坐标纬度
    :return:
    """
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return [bd_lng, bd_lat]
 
 
def bd09_to_gcj02(bd_lon, bd_lat):
    """
    百度坐标系(BD-09)转火星坐标系(GCJ-02)
    百度——>谷歌、高德
    :param bd_lat:百度坐标纬度
    :param bd_lon:百度坐标经度
    :return:转换后的坐标列表形式
    """
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return [gg_lng, gg_lat]
 
 
def wgs84_to_gcj02(lng, lat):
    """
    WGS84转GCJ02(火星坐标系)
    :param lng:WGS84坐标系的经度
    :param lat:WGS84坐标系的纬度
    :return:
    """
    if out_of_china(lng, lat):  # 判断是否在国内
        return lng, lat
    dlat = transform_lat(lng - 105.0, lat - 35.0)
    dlng = transform_lng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [mglng, mglat]
 
 
def gcj02_to_wgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    if out_of_china(lng, lat):
        return lng, lat
    dlat = transform_lat(lng - 105.0, lat - 35.0)
    dlng = transform_lng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]
 
 
def bd09_to_gcj02_to_wgs84(lng, lat):
    gcj_lng_lat = bd09_to_gcj02(lng,lat)    
    gcj_lng = gcj_lng_lat[0]
    gcj_lat = gcj_lng_lat[1]
    wgs_lng_lat = gcj02_to_wgs84(gcj_lng,gcj_lat)
    wgs_lng = wgs_lng_lat[0]
    wgs_lat = wgs_lng_lat[1]
    return [wgs_lng,wgs_lat]

def transform_lat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
        0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret
 
 
def transform_lng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
        0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret
 
 
def out_of_china(lng, lat):
    """
    判断是否在国内，不在国内不做偏移
    :param lng:
    :param lat:
    :return:
    """
    if lng < 72.004 or lng > 137.8347:
        return True
    if lat < 0.8293 or lat > 55.8271:
        return True
    return False
 
 
if __name__ == '__main__':

    #  result = geocode()
#     bd_lng = result[0]
#     bd_lat = result[1]
    
#     result1 = gcj02_to_bd09(bd_lng, bd_lat)
#     result2 = bd09_to_gcj02(bd_lng, bd_lat)
#     result3 = wgs84_to_gcj02(bd_lng, bd_lat)
#     result4 = gcj02_to_wgs84(bd_lng, bd_lat)
#     result5 = bd09_to_gcj02_to_wgs84(bd_lng, bd_lat)
#     print(result1, result2, result3, result4, result5)
#     print(dd," ",result," ", result5)
#     sub_name = ["南宁市规划管理局","青秀分局","兴宁分局","江南分局","青秀山分局","西乡塘分局","邕宁分局","良庆分局","高新技术产业开发区分局","经济技术开发区分局","相思湖新区分局","五象分局"]
#     address = ["南宁市东葛路125号","南宁市茶花园路31-1号7楼","南宁市厢竹大道63号兴宁区政府附楼2楼","南宁市星光大道37-1号","南宁市青山路19号青秀山管委会办公楼230室","南宁市明秀东路238号(原地委大院检察院一楼)","南宁市仙葫大道185号","南宁市大沙田东风北路银沙大道交叉路口","南宁市滨河路1号火炬大厦17楼","南宁市星光大道230号经济技术开发区管委会2号楼","南宁市大学东路81号相思湖新区管委会","南宁市良庆区云英路8号五象总部大厦"]
#     for name,addr in zip(sub_name,address):
#         # time.sleep(1)
#         result = geocode(addr)
#         bd_lng = result[0]
#         bd_lat = result[1]
#         result5 = bd09_to_gcj02_to_wgs84(bd_lng, bd_lat)
#         print(name,result, result5)
    left_result = bd09_to_gcj02_to_wgs84(108.134474,22.680925)
    right_result = bd09_to_gcj02_to_wgs84(108.59843,22.969258)

    print(left_result)
    print(right_result)