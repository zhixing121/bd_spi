# bd_spi
bd_tile_spider

-----------

### 功能：
* 1 下载矩形范围内地图切片并合并，相应生成jpg以及jgw文件
* 2 坐标转换（bd_4326_火星）
* 3 坐标转bd切片坐标
* 4 目前只能下道路与建筑  道路是混合的 更多类型请添加bd个性化地图的不同样式的url 最好进行格式化 具体不再赘述

### 准备
* 1 需要自己申请: bd地图 浏览器端key
* 2 地图范围 左下角坐标以及右上角坐标（bd坐标拾取系统获取）
* 3 其他看代码

##### 注意
* 1 地图有时候下载切片没有请求到（代码不够完善所致），用problem.jpg代替，可手动下载切片替换，具体方法不在此赘述
* 2 需要连外网才能用
* 3 想做的并没有全部完成，还有很多功能没做，有时间了再更新
* 4 跪求大佬批评指正，感谢提供好的思路，我想要数据来搞搞事情

##### 还没实现的功能
* 1 搞搞gd
* 2 尝试搞搞矢量
------
> 声明：数据有偏移，需要自己纠正，纠正数据如涉及保密信息或者数据本身涉密，禁止违法传播，具体请参考《地图审核管理规定》。代码公开数据不公开，如侵权或者损害了您的利益，请第一时间通知作者，给予删除！最终解释权归作者所有
