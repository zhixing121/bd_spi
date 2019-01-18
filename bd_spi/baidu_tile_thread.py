import os
import re
import threading
import time
from queue import Queue

import requests
from row_col_lng_lat_prj import get_row_col_num
from merge_tiles import MergeJpg

PIX_SIZE = 256
LAYER_URL = {
    'gaosu': "http://api0.map.bdimg.com/customimage/tile?&x={}&y={}&z={}&udt=20181205&scale=1&ak={}&styles=t%3Aland%7Ce%3Ag%7Cv%3Aoff%7Cc%3A%23f5f5f5ff%2Ct%3Awater%7Ce%3Ag%7Cv%3Aoff%7Cc%3A%23bedbf9ff%2Ct%3Agreen%7Ce%3Ag%7Cv%3Aoff%7Cc%3A%23d0edccff%2Ct%3Abuilding%7Ce%3Ag%7Cv%3Aoff%2Ct%3Abuilding%7Ce%3Ag.f%7Cc%3A%23ffffffb3%2Ct%3Abuilding%7Ce%3Ag.s%7Cc%3A%23dadadab3%2Ct%3Asubwaystation%7Ce%3Ag%7Cv%3Aoff%7Cc%3A%23b15454B2%2Ct%3Aeducation%7Ce%3Ag%7Cv%3Aoff%7Cc%3A%23e4f1f1ff%2Ct%3Amedical%7Ce%3Ag%7Cv%3Aoff%7Cc%3A%23f0dedeff%2Ct%3Ascenicspots%7Ce%3Ag%7Cv%3Aoff%7Cc%3A%23e2efe5ff%2Ct%3Ahighway%7Ce%3Ag%7Cv%3Aon%7Cw%3A4%2Ct%3Ahighway%7Ce%3Ag.f%7Cc%3A%23f7c54dff%2Ct%3Ahighway%7Ce%3Ag.s%7Cc%3A%23fed669ff%2Ct%3Ahighway%7Ce%3Al%7Cv%3Aon%2Ct%3Ahighway%7Ce%3Al.t.f%7Cc%3A%238f5a33ff%2Ct%3Ahighway%7Ce%3Al.t.s%7Cc%3A%23ffffffff%2Ct%3Ahighway%7Ce%3Al.i%7Cv%3Aon%2Ct%3Aarterial%7Ce%3Ag%7Cv%3Aoff%7Cw%3A2%2Ct%3Aarterial%7Ce%3Ag.f%7Cc%3A%23d8d8d8ff%2Ct%3Aarterial%7Ce%3Ag.s%7Cc%3A%23ffeebbff%2Ct%3Aarterial%7Ce%3Al%7Cv%3Aoff%2Ct%3Aarterial%7Ce%3Al.t.f%7Cc%3A%23525355ff%2Ct%3Aarterial%7Ce%3Al.t.s%7Cc%3A%23ffffffff%2Ct%3Alocal%7Ce%3Ag%7Cv%3Aoff%7Cw%3A1%2Ct%3Alocal%7Ce%3Ag.f%7Cc%3A%23d8d8d8ff%2Ct%3Alocal%7Ce%3Ag.s%7Cc%3A%23ffffffff%2Ct%3Alocal%7Ce%3Al%7Cv%3Aoff%2Ct%3Alocal%7Ce%3Al.t.f%7Cc%3A%23979c9aff%2Ct%3Alocal%7Ce%3Al.t.s%7Cc%3A%23ffffffff%2Ct%3Arailway%7Ce%3Ag%7Cv%3Aoff%7Cw%3A1%2Ct%3Arailway%7Ce%3Ag.f%7Cc%3A%23949494ff%2Ct%3Arailway%7Ce%3Ag.s%7Cc%3A%23ffffffff%2Ct%3Asubway%7Ce%3Ag%7Cv%3Aoff%7Cw%3A1%2Ct%3Asubway%7Ce%3Ag.f%7Cc%3A%23d8d8d8ff%2Ct%3Asubway%7Ce%3Ag.s%7Cc%3A%23ffffffff%2Ct%3Asubway%7Ce%3Al%7Cv%3Aoff%2Ct%3Asubway%7Ce%3Al.t.f%7Cc%3A%23979c9aff%2Ct%3Asubway%7Ce%3Al.t.s%7Cc%3A%23ffffffff%2Ct%3Acontinent%7Ce%3Al%7Cv%3Aon%2Ct%3Acontinent%7Ce%3Al.i%7Cv%3Aon%2Ct%3Acontinent%7Ce%3Al.t.f%7Cc%3A%23333333ff%2Ct%3Acontinent%7Ce%3Al.t.s%7Cc%3A%23ffffffff%2Ct%3Acity%7Ce%3Al.i%7Cv%3Aon%2Ct%3Acity%7Ce%3Al%7Cv%3Aon%2Ct%3Acity%7Ce%3Al.t.f%7Cc%3A%23454d50ff%2Ct%3Acity%7Ce%3Al.t.s%7Cc%3A%23ffffffff%2Ct%3Atown%7Ce%3Al.i%7Cv%3Aon%2Ct%3Atown%7Ce%3Al%7Cv%3Aon%2Ct%3Atown%7Ce%3Al.t.f%7Cc%3A%23454d50ff%2Ct%3Atown%7Ce%3Al.t.s%7Cc%3A%23ffffffff%2Ct%3Abackground%7Ce%3Ag%7Cv%3Aon%7Cc%3A%23000000ff%2Ct%3Apoi%7Ce%3Al%7Cv%3Aoff%2Ct%3Apoi%7Ce%3Al.i%7Cv%3Aoff%2Ct%3Alabel%7Ce%3Al%7Cv%3Aoff%2Ct%3Alabel%7Ce%3Al.i%7Cv%3Aoff%2Ct%3Aroad%7Ce%3Al%7Cv%3Aon%2Ct%3Aroad%7Ce%3Ag%7Cv%3Aon%2Ct%3Amanmade%7Ce%3Ag%7Cv%3Aoff%2Ct%3Aestate%7Ce%3Ag%7Cv%3Aoff%2Ct%3Atransportation%7Ce%3Ag%7Cv%3Aoff%2Ct%3Ashopping%7Ce%3Ag%7Cv%3Aoff%2Ct%3Aentertainment%7Ce%3Ag%7Cv%3Aoff%2Ct%3Aairportlabel%7Ce%3Al%7Cv%3Aoff%2Ct%3Aairportlabel%7Ce%3Al.i%7Cv%3Aoff",
    'jianzhu': "http://api0.map.bdimg.com/customimage/tile?&x={}&y={}&z={}&udt=20181205&scale=1&ak={}&styles=t%3Abackground%7Ce%3Ag%7Cv%3Aon%7Cc%3A%23000000ff%2Ct%3Aroad%7Ce%3Ag%7Cv%3Aoff%2Ct%3Aroad%7Ce%3Al%7Cv%3Aoff%2Ct%3Apoi%7Ce%3Al%7Cv%3Aoff%2Ct%3Apoi%7Ce%3Al.i%7Cv%3Aoff%2Ct%3Alabel%7Ce%3Al%7Cv%3Aoff%2Ct%3Alabel%7Ce%3Al.i%7Cv%3Aoff%2Ct%3Alocal%7Ce%3Ag%7Cv%3Aoff%2Ct%3Alocal%7Ce%3Ag.f%7Cc%3A%23000000ff%2Ct%3Alocal%7Ce%3Ag.s%7Cc%3A%23000000ff%2Ct%3Afourlevelway%7Ce%3Ag.f%7Cc%3A%23000000ff%2Ct%3Afourlevelway%7Ce%3Ag.s%7Cc%3A%23000000ff%2Ct%3Afourlevelway%7Ce%3Al%7Cv%3Aoff%2Ct%3Afourlevelway%7Ce%3Al.t.f%7Cc%3A%23000000ff%2Ct%3Afourlevelway%7Ce%3Al.t.s%7Cc%3A%23000000ff%2Ct%3Afourlevelway%7Ce%3Ag%7Cv%3Aoff%2Ct%3Atertiaryway%7Ce%3Ag.f%7Cc%3A%23000000ff%2Ct%3Atertiaryway%7Ce%3Ag.s%7Cc%3A%23000000ff%2Ct%3Atertiaryway%7Ce%3Ag%7Cv%3Aoff%2Ct%3Atertiaryway%7Ce%3Al.t.s%7Cc%3A%23000000ff%2Ct%3Atertiaryway%7Ce%3Al.t.f%7Cc%3A%23000000ff%2Ct%3Avacationway%7Ce%3Ag.f%7Cc%3A%23000000ff%2Ct%3Avacationway%7Ce%3Ag.s%7Cc%3A%23000000ff%2Ct%3Arailway%7Ce%3Ag.f%7Cc%3A%23000000ff%2Ct%3Arailway%7Ce%3Ag.s%7Cc%3A%23000000ff%2Ct%3Asubway%7Ce%3Ag.f%7Cc%3A%2300000000%2Ct%3Asubway%7Ce%3Ag.s%7Cc%3A%2300000000%2Ct%3Ahighwaysign%7Ce%3Al.t.f%7Cc%3A%23000000ff%2Ct%3Ahighwaysign%7Ce%3Al.t.s%7Cc%3A%23000000ff%2Ct%3Ahighwaysign%7Ce%3Al.i%7Cv%3Aoff%2Ct%3Ahighwaysign%7Ce%3Al%7Cv%3Aoff%2Ct%3Anationalwaysign%7Ce%3Al%7Cv%3Aoff%2Ct%3Anationalwaysign%7Ce%3Al.i%7Cv%3Aoff%2Ct%3Aprovincialwaysign%7Ce%3Al%7Cv%3Aoff%2Ct%3Aprovincialwaysign%7Ce%3Al.i%7Cv%3Aoff%2Ct%3Atertiarywaysign%7Ce%3Al%7Cv%3Aoff%2Ct%3Atertiarywaysign%7Ce%3Al.i%7Cv%3Aoff%2Ct%3Asubwaylabel%7Ce%3Al%7Cv%3Aoff%2Ct%3Asubwaylabel%7Ce%3Al.i%7Cv%3Aoff%2Ct%3Auniversityway%7Ce%3Ag.f%7Cc%3A%23000000ff%2Ct%3Auniversityway%7Ce%3Ag.s%7Cc%3A%23000000ff%2Ct%3Auniversityway%7Ce%3Ag%7Cv%3Aoff%2Ct%3Ascenicspotsway%7Ce%3Ag.f%7Cc%3A%23000000ff%2Ct%3Ascenicspotsway%7Ce%3Ag.s%7Cc%3A%23000000ff%2Ct%3Ascenicspotsway%7Ce%3Ag%7Cv%3Aoff%2Ct%3Aarterial%7Ce%3Ag.f%7Cc%3A%23000000ff%2Ct%3Aarterial%7Ce%3Ag.s%7Cc%3A%23000000ff%2Ct%3Aarterial%7Ce%3Al%7Cv%3Aoff%2Ct%3Aarterial%7Ce%3Al.t.f%7Cc%3A%23000000ff%2Ct%3Aarterial%7Ce%3Al.t.s%7Cc%3A%23000000ff%2Ct%3Aarterial%7Ce%3Ag%7Cv%3Aoff%2Ct%3Acityhighway%7Ce%3Ag.f%7Cc%3A%23000000ff%2Ct%3Acityhighway%7Ce%3Ag.s%7Cc%3A%23000000ff%2Ct%3Acityhighway%7Ce%3Al%7Cv%3Aoff%2Ct%3Acityhighway%7Ce%3Ag%7Cv%3Aoff%2Ct%3Aprovincialway%7Ce%3Ag.f%7Cc%3A%23000000ff%2Ct%3Aprovincialway%7Ce%3Ag.s%7Cc%3A%23000000ff%2Ct%3Aprovincialway%7Ce%3Al%7Cv%3Aoff%2Ct%3Aprovincialway%7Ce%3Ag%7Cv%3Aoff%2Ct%3Anationalway%7Ce%3Ag.f%7Cc%3A%23000000ff%2Ct%3Anationalway%7Ce%3Ag.s%7Cc%3A%23000000ff%2Ct%3Anationalway%7Ce%3Al%7Cv%3Aoff%2Ct%3Anationalway%7Ce%3Ag%7Cv%3Aoff%2Ct%3Ahighway%7Ce%3Ag.f%7Cc%3A%23000000ff%2Ct%3Ahighway%7Ce%3Ag.s%7Cc%3A%23000000ff%2Ct%3Ahighway%7Ce%3Ag%7Cv%3Aoff%2Ct%3Ahighway%7Ce%3Al%7Cv%3Aoff%2Ct%3Ahighway%7Ce%3Al.t.f%7Cc%3A%23ffffffff%2Ct%3Ahighway%7Ce%3Al.t.s%7Cc%3A%23ffffffff%2Ct%3Aland%7Ce%3Ag%7Cv%3Aon%7Cc%3A%23000000ff%2Ct%3Atertiaryway%7Ce%3Al%7Cv%3Aoff%2Ct%3Arailway%7Ce%3Ag%7Cv%3Aoff%2Ct%3Awater%7Ce%3Ag%7Cv%3Aoff%7Cc%3A%23000000ff%2Ct%3Awater%7Ce%3Al%7Cv%3Aoff%2Ct%3Abuilding%7Ce%3Ag.f%7Cc%3A%23ffffffff%2Ct%3Abuilding%7Ce%3Ag.s%7Cc%3A%23ffffffff%2Ct%3Asubwaystation%7Ce%3Ag%7Cv%3Aoff%7Cc%3A%23000000ff%2Ct%3Aeducation%7Ce%3Ag%7Cv%3Aoff%7Cc%3A%23000000ff%2Ct%3Amedical%7Ce%3Ag%7Cv%3Aoff%7Cc%3A%23000000ff%2Ct%3Ascenicspots%7Ce%3Ag%7Cv%3Aoff%7Cc%3A%23000000ff%2Ct%3Atransportation%7Ce%3Ag%7Cv%3Aoff%7Cc%3A%23000000ff",
}


class DownloadTiles():
    """
    多线程爬取bd地图切片
    1，输入级别与左下角右上角范围坐标
    2，根据坐标自动计算切片行列号（实现）
    3，根据行列号爬取切片（赋予切片位置信息未实现）
    4，保存切片文件
    5, 检查切片是否能用，不能则重新爬取或替换为无数据
    5，拼接切片文件（实现）
    6，配准图片（手动，未实现）
    7,输入坐标超出拼接内存范围则自动分组(未实现)
    """
    leftRowCol = None
    rightRowCol = None
    min_x = None
    min_y = None
    max_x = None
    max_y = None

    def __init__(self, z, ak, save_path, left_bottom_xy, right_top_xy, url_num, url_temp):
        self.z = z
        self.ak = ak
        self.save_path = save_path
        self.left_bottom_xy = left_bottom_xy
        self.right_top_xy = right_top_xy
        self.url_num = url_num
        self.url_temp = url_temp
        self.row_col_t = Queue()
        self.url_q = Queue()

    def get_row_col_n(self):
        DownloadTiles.min_x = float(self.left_bottom_xy.split(",")[0].strip())
        DownloadTiles.min_y = float(self.left_bottom_xy.split(",")[1].strip())
        DownloadTiles.max_x = float(self.right_top_xy.split(",")[0].strip())
        DownloadTiles.max_y = float(self.right_top_xy.split(",")[1].strip())
        if "," or "，" in self.left_bottom_xy:
            left_row_col = get_row_col_num(
                DownloadTiles.min_x, DownloadTiles.min_y, self.z)
            DownloadTiles.leftRowCol = left_row_col
        if "," or "，" in self.right_top_xy:
            right_row_col = get_row_col_num(
                DownloadTiles.max_x, DownloadTiles.max_y, self.z)
            DownloadTiles.rightRowCol = right_row_col
        return(left_row_col, right_row_col)

    def set_row_col_q(self):
        left_row_col, right_row_col = self.get_row_col_n()
        # for x in range(94067, 94451):  # 自左向右爬取
        #     for y in range(20120, 20387):
        for x in range(left_row_col[0], right_row_col[0]):  # 自左向右爬取 50*80
            for y in range(left_row_col[1], right_row_col[1]):
                self.row_col_t.put([x, y])

    def get_url(self):
        '''
        获取url
        '''
        while True:
            xy = self.row_col_t.get()
            self.url_q.put(self.url_temp.format(xy[0], xy[1], self.z, self.ak))
            self.row_col_t.task_done()

    def get_row_col(self):
        '''
        下载切片
        '''
        while True:
            url = self.url_q.get()
            self.get_img(url)
            self.url_q.task_done()

    def get_img(self, url):
        '''
        下载图片
        '''
        x = re.findall(r'&x=(\d+)', url)[0]
        y = re.findall(r'&y=(\d+)', url)[0]
        try:
            while True:
                try:
                    img = requests.get(url)
                except Exception :
                    continue
                if str(img.status_code) == "200":
                    if re.findall('页面不存在',img.text):
                        continue
                    break
                else:
                    continue
            img_name = str(x) + "_" + str(y) + "_" + str(self.z) + ".jpg"
            img_path = os.path.join(self.save_path, img_name)
            print(img_name)
            with open(img_path, 'wb') as ff:
                ff.write(img.content)
            ff.close()
        except Exception as e:
            print(e)
        return (img_name, img.status_code)

    def run(self):
        """
        多线程运行
        """
        threading_list = []
        set_rl = threading.Thread(target=self.set_row_col_q)
        threading_list.append(set_rl)
        for i in range(20):
            rl_t = threading.Thread(target=self.get_row_col)
            threading_list.append(rl_t)
        for i in range(20):
            url_t = threading.Thread(target=self.get_url)
            threading_list.append(url_t)
        for t in threading_list:
            t.setDaemon(True)
            t.start()
            # t.join()

        for q in [self.row_col_t, self.url_q]:
            q.join()

        print("主线程结束")


if __name__ == '__main__':
    # 输入区
    while True:
        z = input("请输入级别(1-19)：")
        if z == '':
            z=18
            print("输入默认18")
            break
        if int(z) > 19 or int(z) == 0:
            print("请输入1-19")
            continue
        z = int(z)
        break
    while True:
        ak = input("请输入你的浏览器端key()：")
        if ak == '' or ak == None:
            print("ak不能为空！")
            continue
        break
    
    save_path = input("请输入存储路径,比如(F:/bd_spi/jz)：")
    if os.path.exists(save_path) == False:
        os.mkdir(save_path)
    while True:
        left_bottom_xy = input("请输入左下角坐标，用逗号隔开(108.36413,22.810891)：")
        if re.findall(r"[^0-9.,\s]", left_bottom_xy):
            print("含有非法字符：")
            continue
        # if left_bottom_xy == '1':
        #     print("输入默认值")
        #     left_bottom_xy = "108.134474,22.680925"
        break
    while True:
        right_top_xy = input("请输入右上角坐标，用逗号隔开(108.36921,22.81341)：")
        if re.findall(r"[^0-9.,\s]", left_bottom_xy):
            print("含有非法字符：")
            continue
        # if right_top_xy == '1':
        #     print("输入默认值")
        #     right_top_xy = "108.59843,22.969258"
        break

    while True:
        url_num = input("请选择类型，输入数字即可。1：高速；2：建筑；")
        url_temp = None
        if url_num == '1':
            url_temp = LAYER_URL["gaosu"]
            break
        elif url_num == '2':
            url_temp = LAYER_URL["jianzhu"]
            break
        elif url_num == "q":
            exit()
        else:
            print("输入不合法，请重新输入")
            continue

    # 运行区
    rl_t = DownloadTiles(z, ak, save_path, left_bottom_xy,
                         right_top_xy, url_num, url_temp)
    st = time.time()
    rl_t.run()
    rl_t.get_row_col_n()
    et = time.time()
    t = et - st
    print("切片下载完毕，用时：{}时{}分{}秒".format(int(t/60/60), int(t/60), int(t % 60)))
    print("爬取切片范围：左下角{} 右上角{}".format(rl_t.leftRowCol, rl_t.rightRowCol))
    print("正在合并切片。。。。。。")
    mj = MergeJpg(DownloadTiles.min_x,
                  DownloadTiles.min_y,
                  DownloadTiles.max_x,
                  DownloadTiles.max_y,
                  DownloadTiles.leftRowCol[0],
                  DownloadTiles.leftRowCol[1], 
                  DownloadTiles.rightRowCol[0], 
                  DownloadTiles.rightRowCol[1], 
                  rl_t.z, rl_t.save_path)
    mj.merge_left_bottom()
    jgw_path = os.path.join(rl_t.save_path,"merge.jgw")
    mj.get_jgw(PIX_SIZE,jgw_path)
    print("合并完成！")
