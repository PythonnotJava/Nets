from dataclasses import dataclass
from typing import Optional, Self, Iterable, List, overload
from math import sqrt, cos, sin, degrees, atan2

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from Nets.BaseMixin import CommonStyleMixin, TextStyleMixin, DefaultNodeStyle, DefaultTextStyle, DefaultLineStyle, StyleAnalyze

# 位置偏移类，默认是相当于原点，传入x和y轴的坐标
@dataclass
class Offset(object):
    x: float
    y: float

    def __add__(self, other: Self) -> Self: return Offset(self.x + other.x, other.y + self.y)

    def __sub__(self, other: Self) -> Self: return Offset(self.x - other.x, self.y - other.y)

# 节点类
class NodeVar(object):
    # 相对于原点的偏移的向量构造方式
    def __init__(self, pos: Offset, ax: Axes, style: CommonStyleMixin = DefaultNodeStyle):
        StyleAnalyze('node', style)
        ax.plot(pos.x, pos.y, marker=style.style, color=style.color, markersize=style.size)
        self.style = style
        self.pos = pos

    # 相对于某点偏移，计算方式为向量求和
    @classmethod
    def offset(cls, node: Self, direction: Offset, ax: Axes, style: CommonStyleMixin = DefaultNodeStyle) -> Self:
        return cls(node.pos + direction, ax, style)

    def X(self) -> float: return self.pos.x

    def Y(self) -> float: return self.pos.y

    # 绑定一个相对点的长度夹角构造方式
    # 规定：theta是度数值，不是弧度，且范围是0 ~ 360
    @classmethod
    def bind(cls, node: Self, length: float, theta: float, ax: Axes,
             style: CommonStyleMixin = DefaultNodeStyle) -> Self:
        pos = Offset(x=node.X() + length * cos(theta), y=node.Y() + length * sin(theta))
        return cls(pos=pos, ax=ax, style=style)

    # 与目标点的距离
    def measure(self, node: Self) -> float: return sqrt((self.X() - node.X()) ** 2 + (self.Y() - node.Y()) ** 2)

# 线类
class LineVar(object):
    # 相当于原点的两个点，两种实现，另一个是基于节点
    def __init__(self, start: Offset, to: Offset, ax: Axes, arrow=False, style: CommonStyleMixin = DefaultLineStyle):
        StyleAnalyze('line', style)
        if arrow:
            ax.annotate('', xy=(to.x, to.y), xytext=(start.x, start.y),
                        arrowprops=dict(arrowstyle='->', color=style.color, lw=style.size, ls=style.style))
        else:
            plt.plot((start.x, to.x), (start.y, to.y), color=style.color, lw=style.size, ls=style.style)

        self.style = style
        self.start = start
        self.to = to

    @classmethod
    def bind(cls, node1: NodeVar, node2: NodeVar, ax: Axes, arrow=False, style: CommonStyleMixin = DefaultLineStyle):
        return cls(node1.pos, node2.pos, ax, arrow, style)

    # 相对于原点的夹角，返回度数值
    @property
    def theta(self) -> float:
        return degrees(atan2(self.to.y - self.start.y, self.to.x - self.start.x)) % 360

    # 获取斜率
    @property
    def K(self) -> float:
        return (self.start.y - self.to.y) / (self.start.x - self.to.x)

    # 长度
    @property
    def length(self):
        return sqrt((self.start.x - self.to.x) ** 2 + (self.start.y - self.to.y) ** 2)

# 文本类
"""
文本布置最大的bug在于如果初始画布不是n*n尺寸，会导致直线不与文本平行的问题;
另外，即使初始平行，任意缩放尺寸也会造成平行丢失，办法就是重写resize画布事件.
我不写，只声明
"""
class TextVar(object):
    # 从某点开始布置文本
    def __init__(self, pos: Offset, text: str, ax: Axes, style: TextStyleMixin = DefaultTextStyle):
        StyleAnalyze('text', style)
        self.pos = pos
        self.text = text
        self.style = style
        ax.text(pos.x, pos.y, text, fontdict=dict(
            fontname=style.family,
            fontsize=style.size,
            style=style.style
        ), ha='center', va='center', c=style.color, rotation=style.rotation)

    # 在线的一侧偏置平行标注，注意此时，如果采用默认角度，会被纠正
    # 可以通过bias设置平行间距，如果不设置，偏移间距为（线粗+字体）* 0.05
    @classmethod
    def parallel(cls, line: LineVar, text: str, ax: Axes, bias: Optional[float] = None,
                 style: TextStyleMixin = DefaultTextStyle) -> Self:
        gap: float = bias if bias else (line.style.size + style.size) * 0.05
        theta = line.theta
        X = (line.start.x + line.to.x) / 2
        Y = (line.start.y + line.to.y) / 2 + gap
        pos = Offset(X, Y)
        style.rotation = theta
        return cls(pos, text, ax, style)

    # 显示两点之间的距离(distance) | 显示直线长度(length)。这两个方法都是主动平行于所在直线的
    # 偏移不指定就取第一个（点大小 + 字体大小）* 0.025
    @classmethod
    def distance(cls,
                 node1: NodeVar,
                 node2: NodeVar,
                 ax: Axes,
                 bias: Optional[float] = None,
                 style: TextStyleMixin = DefaultTextStyle,
                 visible: int = 0
                 ) -> Self:
        gap: float = bias if bias else (node1.style.size + style.size) * 0.025
        theta = degrees(atan2(node2.Y() - node1.Y(), node2.X() - node1.X()))
        X = (node1.X() + node2.X()) / 2
        Y = (node2.Y() + node1.Y()) / 2 + gap
        pos = Offset(X, Y)
        style.rotation = theta
        text = f'{node1.measure(node2):.{visible}f}'
        return cls(pos, text, ax, style)

    @classmethod
    def length(cls,
               line: LineVar,
               ax: Axes,
               bias: Optional[float] = None,
               style: TextStyleMixin = DefaultTextStyle,
               visible: int = 0
               ) -> Self:
        gap: float = bias if bias else (line.style.size + style.size) * 0.05
        theta = line.theta
        node1 = line.start
        node2 = line.to
        X = (node1.x + node2.x) / 2
        Y = (node2.y + node1.y) / 2 + gap
        pos = Offset(X, Y)
        style.rotation = theta
        text = f'{line.length:.{visible}f}'
        return cls(pos, text, ax, style)

# 将相对于原点的位置列表转为Offset | 另一个版本是相对于是上一个进行偏移，第一个相对于原点
@overload
def transToOffset(points : Iterable) -> List[Offset]: ...
@overload
def transToOffset(points : Iterable, isBind : bool = False) -> List[Offset]: ...
def transToOffset(points : Iterable, isBind : Optional[bool] = False) -> List[Offset]:
    if not isBind:
        return [Offset(p[0], p[1]) for p in points]
    else:
        last = Offset(0, 0)
        ls = []
        for p in points:
            last = last + Offset(p[0], p[1])
            ls.append(last)
        return ls

__all__ = ['NodeVar', 'LineVar', 'TextVar', 'Offset', 'transToOffset']