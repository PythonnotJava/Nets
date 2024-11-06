from dataclasses import dataclass
from copy import copy as tempCopy
from typing import Optional, Self, Iterable, List, overload, Union, Literal
from math import sqrt, cos, sin, degrees, atan2, radians

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from Nets.BaseMixin import CommonStyleMixin, TextStyleMixin, DefaultNodeStyle, DefaultTextStyle, DefaultLineStyle, StyleAnalyze

# 位置偏移类，默认是相当于原点，传入x和y轴的坐标
@dataclass
class Offset(object):
    x: float
    y: float

    @overload
    def __add__(self, other: Self) -> Self: ...
    @overload
    def __add__(self, other : float) -> Self: ...
    def __add__(self, other : Union[Self, float]) -> Self:
        return Offset(self.x + other.x, other.y + self.y) if isinstance(other, Offset) else Offset(self.x + other, other + self.y)

    @overload
    def __sub__(self, other: Self) -> Self: ...
    @overload
    def __sub__(self, other: float) -> Self: ...
    def __sub__(self, other : Union[Self, float]) -> Self:
        return Offset(self.x - other.x, self.y - other.y) if isinstance(other, Offset) else Offset(self.x - other, self.y - other)

# 节点类
class NodeVar(object):
    # 相对于原点的偏移的向量构造方式
    def __init__(self, pos: Offset, ax: Axes, style: CommonStyleMixin = tempCopy(DefaultNodeStyle)):
        StyleAnalyze('node', style)
        self._instance : Line2D = ax.plot(pos.x, pos.y, marker=style.style, color=style.color, markersize=style.size)[0]
        self.style = style
        self.pos = pos

    # 相对于某点偏移，计算方式为向量求和
    @classmethod
    def offset(cls, node: Self, direction: Offset, ax: Axes, style: CommonStyleMixin = tempCopy(DefaultNodeStyle)) -> Self:
        return cls(node.pos + direction, ax, style)

    def X(self) -> float: return self.pos.x

    def Y(self) -> float: return self.pos.y

    # 重写设置点的样式
    def setStyle(
            self,
            style : Optional[Literal['o', '^', 'v', '>', '<', 's', '*', 'p', 'P', 'h', 'H', 'D', 'd', 'X', '+', 'x', '|', '_']] = None,
            size : Optional[int] = None,
            color : Optional[str] = None
    ) -> Self:
        if color:
            self._instance.set_color(color)
        if style:
            self._instance.set_marker(style)
        if size:
            self._instance.set_markersize(size)
        return self

    # 绑定一个相对点的长度夹角构造方式
    @classmethod
    def bind(cls, node: Self, length: float, theta: float, ax: Axes,
             style: CommonStyleMixin = tempCopy(DefaultNodeStyle)) -> Self:
        theta = radians(theta)
        pos = Offset(x=node.X() + length * cos(theta), y=node.Y() + length * sin(theta))
        return cls(pos=pos, ax=ax, style=style)

    # 与目标点的距离
    def measure(self, node: Self) -> float: return sqrt((self.X() - node.X()) ** 2 + (self.Y() - node.Y()) ** 2)
    # 到某线段所在直线的垂距
    def vertical_distance(self, line : 'LineVar') -> float:
        return abs(-line.K * self.X() + self.Y() - line.B) * abs(cos(radians(line.theta)))

# 线类
class LineVar(object):
    # 相当于原点的两个点，两种实现，另一个是基于节点
    def __init__(self, start: Offset, to: Offset, ax: Axes, arrow=False, style: CommonStyleMixin = tempCopy(DefaultLineStyle)):
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
    def bind(cls, node1: NodeVar, node2: NodeVar, ax: Axes, arrow=False, style: CommonStyleMixin = tempCopy(DefaultLineStyle)):
        return cls(node1.pos, node2.pos, ax, arrow, style)

    # 相对于原点的夹角，返回度数值
    @property
    def theta(self) -> float: return degrees(atan2(self.to.y - self.start.y, self.to.x - self.start.x)) % 360
    # 获取斜率与截距
    @property
    def K(self) -> float: return (self.start.y - self.to.y) / (self.start.x - self.to.x)
    @property
    def B(self) -> float: return self.start.y - self.start.x * self.K
    # 长度
    @property
    def length(self): return sqrt((self.start.x - self.to.x) ** 2 + (self.start.y - self.to.y) ** 2)
    # 中点位置
    @property
    def middle(self) -> Offset: return Offset(self.start.x / 2 + self.to.x / 2, self.start.y / 2 + self.to.y / 2)
    # 中点
    def middleNode(self, ax : Axes, style : CommonStyleMixin = tempCopy(DefaultNodeStyle)) -> NodeVar: return NodeVar(self.middle, ax, style)
# 文本类
"""
设计规定：
1. 我们传入的一切角度都是自然直观的度数，不是弧度，范围是0 ~ 360
2. 在进行一个文本布置的时候，bias控制文本偏移目标距离、其内置属性rotation控制文本相当于目标位置的角度
注：文本布置最大的bug在于如果初始画布不是n*n尺寸，会导致直线不与文本平行的问题;
另外，即使初始平行，任意缩放尺寸也会造成平行丢失，办法就是重写resize画布事件.
除了使用画布纵横比约束（在图元少的情况，显示效果很差），我不写更多，其他作为备注
"""
class TextVar(object):
    # 从某点开始布置文本
    def __init__(self, pos: Offset, text: str, ax: Axes, style: TextStyleMixin = tempCopy(DefaultTextStyle)):
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
                 style: TextStyleMixin = tempCopy(DefaultTextStyle)) -> Self:
        gap: float = bias if bias else (line.style.size + style.size) * 0.05
        theta = line.theta
        X = (line.start.x + line.to.x) / 2
        Y = (line.start.y + line.to.y) / 2 + gap
        pos = Offset(X, Y)
        style.rotation = theta
        return cls(pos, text, ax, style)

    # 显示两点之间的距离(distance) | 显示直线长度(length)。这两个方法都是主动平行于所在直线的，可以设置不平行
    @classmethod
    def distance(cls,
                 node1: NodeVar,
                 node2: NodeVar,
                 ax: Axes,
                 bias: Optional[float] = None,
                 style: TextStyleMixin = tempCopy(DefaultTextStyle),
                 visible: int = 0,
                 parallel=False
     ) -> Self:
        gap: float = bias if bias else (node1.style.size + style.size) * 0.05
        theta = degrees(atan2(node2.Y() - node1.Y(), node2.X() - node1.X()))
        X = (node1.X() + node2.X()) / 2
        Y = (node2.Y() + node1.Y()) / 2 + gap
        pos = Offset(X, Y)
        if parallel:
            style.rotation = theta
        text = f'{node1.measure(node2):.{visible}f}'
        return cls(pos, text, ax, style)

    @classmethod
    def length(cls,
               line: LineVar,
               ax: Axes,
               bias: Optional[float] = None,
               style: TextStyleMixin = tempCopy(DefaultTextStyle),
               visible: int = 0,
               parallel=False
    ) -> Self:
        gap: float = bias if bias else (line.style.size + style.size) * 0.05
        theta = line.theta
        node1 = line.start
        node2 = line.to
        X = (node1.x + node2.x) / 2
        Y = (node2.y + node1.y) / 2 + gap
        pos = Offset(X, Y)
        if parallel:
            style.rotation = theta
        text = f'{line.length:.{visible}f}'
        return cls(pos, text, ax, style)

    # 在节点旁边添加文本
    # theta是文本相当于目标位置的夹角
    @classmethod
    def bind(
            cls,
            node : NodeVar,
            text : str,
            ax: Axes,
            theta : int = 0,
            bias: Optional[float] = None,
            style : TextStyleMixin = tempCopy(DefaultTextStyle)
    ) -> Self:
        # print(style.rotation)
        gap: float = bias if bias else (node.style.size + style.size) * 0.05
        t = radians(theta)
        return cls(node.pos + Offset(gap * cos(t), gap * sin(t)), text, ax, style)

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
