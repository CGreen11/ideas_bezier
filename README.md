# ideas_bezier
粘性曲线与官方贝塞尔曲线对比

1、在寻找趣味项目时，基于https://github.com/Molly6943/pythonGames 的singlePicMove.py、mutiplPicMove.py修改eventsGames.py想要结合成有意思操作动画
，通过鼠标选中或使用上一个与其他球或四个边界碰撞，鼠标按下到抬起的矢量决定选中球的速度。
2、在Molly6943/pythonGames的项目中还有绘制矩形的arts.py，以及https://blog.csdn.net/klxh2009/article/details/78314060 中介绍了android实现的粘性动画
，利用bezier曲线实现拖拽的粘性动画并增加鼠标抬起后的振荡效果以及替换相关位置图片，实现过程中发现pygame.gfxdraw提供了bezier曲线的绘制
，但是没有使用抗锯齿，且暂时没有发现pygame如何填充封闭曲线的方法（应该是有提供但没找到）
，最后还是通过bezier二阶方程式获取左边曲线上的所有点，并对称轴画横线并填补横线间的多边形达到显式填充曲线的效果
最后，upoload file一直失败，只好通过create new 创建复制代码，而我想上传一些比如效果图不知道该怎么弄。
