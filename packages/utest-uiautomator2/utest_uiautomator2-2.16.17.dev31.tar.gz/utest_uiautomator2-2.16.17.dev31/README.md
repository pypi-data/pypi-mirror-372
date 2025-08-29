基于uiautomator2 2.16.14定制化版本

###### 修改记录

    1、修改部分xpath写法无法正确识别的问题
    例：xpath = （//*[@class='android.widget.HorizontalScrollView'])[last()]
    原代码中对传入的xpath做了特殊处理，对于'('开头的xpath，被转移成其他结构的xpath。并且源码中将所有xml所有节点的class属性清除掉了
    修改后解决了以上问题
    2. 初始化 atx-agent 时，增加初始化 utest-agent，以便复用其中的视频流能力

###### 打包方式

注：utest-agent 二进制文件，需要事先放置于 uiautomator2/assets/ 目录下

    python setup.py bdist_wheel
    python setup.py sdist