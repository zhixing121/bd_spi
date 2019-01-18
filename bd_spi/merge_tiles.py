import os

from PIL import Image

# from baidu_tile_thread import
UNIT_SIZE = 256
problem_jpg = r"F:\bd_spi\problem.jpg"


class MergeJpg():
    """
    根据切片的名称对切片进行拼接，从左下角开始向上拼接，拼接完一列返回第二列的最下面继续上一步

    (0,0)—— —— → x
      | ■■
      | ■■
      | ■■↑
      | ■■■
      ↓y
    """

    def __init__(self, min_x, min_y, max_x, max_y, min_pix_x, min_pix_y, max_pix_x, max_pix_y, z, tile_path):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
        self.min_pix_x = min_pix_x 
        self.min_pix_y = min_pix_y 
        self.max_pix_x = max_pix_x 
        self.max_pix_y = max_pix_y
        self.z = z
        self.tile_path = tile_path

    def merge_left_bottom(self):
        TARGET_HEIGHT = (int(self.max_pix_y) - int(self.min_pix_y)) * UNIT_SIZE
        TARGET_WIDTH = (int(self.max_pix_x) - int(self.min_pix_x)) * UNIT_SIZE
        print(TARGET_HEIGHT, TARGET_WIDTH)
        target = Image.new('RGB', (TARGET_WIDTH, TARGET_HEIGHT))
        print(target)
        # 左下角图片的左上角坐标
        left_top_x = 0
        left_top_y = TARGET_HEIGHT - UNIT_SIZE
        right_bottom_x = UNIT_SIZE
        right_bottom_y = TARGET_HEIGHT
        # 有问题图片
        replace_img = img = Image.open(problem_jpg)
        # y是由下而上行号增加，x是自左向右列号增加，拼图从左下角开始 94 x列号 20 y行号
        for x in range(self.min_pix_x, self.max_pix_x):  # 自左向右爬取 50*80
            for y in range(self.min_pix_y, self.max_pix_y):
                img_name = str(x)+"_"+str(y)+"_"+str(self.z)+".jpg"
                try:
                    img = Image.open(os.path.join(self.tile_path, img_name))
                except Exception as e:
                    img = replace_img
                target.paste(img, (left_top_x, left_top_y,
                                   right_bottom_x, right_bottom_y))
                # 竖向拼接 由下而上
                left_top_y -= UNIT_SIZE
                right_bottom_y -= UNIT_SIZE
            # 横向拼接 自左向右
            left_top_x += UNIT_SIZE
            right_bottom_x += UNIT_SIZE
            left_top_y = TARGET_HEIGHT - UNIT_SIZE
            right_bottom_y = TARGET_HEIGHT
        quality_value = 100
        target.save(os.path.join(self.tile_path, "merge.jpg"),
                    quality=quality_value)

    def run(self):
        self.merge_left_bottom()


    def get_jgw(self,PIX_SIZE, out_file_path):
        """
        生成arcmap能够识别的jgw坐标文件
        A=X方向上的象素分辨率
        D=旋转系统
        B=旋转系统
        E=Y方向上的象素分辨素
        C=栅格地图左上角象素中心X坐标
        F=栅格地图左上角象素中心Y坐标
        其中：A=（maxX – minX）/numX；D、B一般默认为0；E=（minY – maxY）/numY；C=minX；F=maxY
        """
        A = (self.max_x-self.min_x)/((self.max_pix_x-self.min_pix_x)*PIX_SIZE)
        D = 0
        B = 0
        E = (self.min_y-self.max_y)/((self.max_pix_y-self.min_pix_y)*PIX_SIZE)
        C = self.min_x
        F = self.max_y
        resulr_list = [A, D, B, E, C, F]
        with open(out_file_path, 'w+') as ff:
            for i in resulr_list:
                ff.write(str(i))
                ff.write("\n")
        ff.close()


if __name__ == '__main__':

    tile_path = "F:/baiduTraffic/tiles18"

    min_x = 47021
    min_y = 10065
    max_x = 47222
    max_y = 10200
    z = 18

    # mer_j = MergeJpg(min_x, min_y, max_x, max_y, z, tile_path)
    # mer_j.run()
