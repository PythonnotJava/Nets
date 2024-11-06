# 我想基于matplotlib做一个网络图的库，考虑有以下几种类节点类、线类、文本类，这三种都有以下属性
from typing import *
from dataclasses import dataclass
from math import sqrt, cos, sin, degrees, atan2, radians
import matplotlib.pyplot as plt
from matplotlib.axes import Axes

# 共同的样式配置
@dataclass
class CommonStyleMixin(object):
    """
    各个属性分别从节点类、线类、文本类展开说明
    1. style
        - 可取圆形、矩形、三角形 | o、s、^
        - 可取实线、虚线、点线、点划线 | -、--、:、—.
        - 可取正常字体、斜体 | normal、italic
    2. size
        - 表示点的大小
        - 表示线粗
        - 表示字体大小
    3. color
        均表示颜色
    """
    style: str
    size: int
    color: str

    @classmethod
    def to(cls, which: Literal["node", "line", "text"], **kwargs) -> Self:
        if which == 'node':
            return cls(style=kwargs.get('style', 'o'), size=kwargs.get('size', 5), color=kwargs.get('color', '#000000'))
        elif which == 'line':
            return cls(style=kwargs.get('style', '-'), size=kwargs.get('size', 2), color=kwargs.get('color', '#000000'))
        else:
            return cls(style=kwargs.get('style', 'normal'), size=kwargs.get('size', 16),
                       color=kwargs.get('color', '#000000'))

    def __str__(self):
        return f"style : {self.style}\nsize : {self.size}\ncolor : {self.color}"


# 文本的额外配置
class TextStyleMixin(CommonStyleMixin):
    """
    family表示字体类型，默认是微软雅黑
    rotation表示文本角度，默认是水平，即0°，但在两个指定点时，会自动替换为达到平行线需要的角度
    """
    family: str = 'Microsoft YaHei'
    rotation: int = 0

    @classmethod
    def to(cls, **kwargs) -> Self:
        instance = super().to('text', **kwargs)
        instance.family = kwargs.get('family', 'Microsoft YaHei')
        instance.rotation = kwargs.get('rotation', 0)
        return instance

    def __str__(self):
        return f"{super().__str__()}\nfamily : {self.family}\nrotation : {self.rotation}"


"""默认样式配置"""
DefaultNodeStyle = CommonStyleMixin.to('node')
DefaultLineStyle = CommonStyleMixin.to('line')
DefaultTextStyle = TextStyleMixin.to()
DefaultMixinStyle = {
    'Node': DefaultNodeStyle,
    'Line': DefaultLineStyle,
    'Text': DefaultTextStyle
}

# 样式分析
def StyleAnalyze(which: Literal["node", "line", "text"], style) -> None:
    if which == 'node':
        if style.style is None:
            style.style = 'o'
        if style.size is None:
            style.size = 5
        if style.color is None:
            style.color = '#000000'
    elif which == 'line':
        if style.style is None:
            style.style = '-'
        if style.size is None:
            style.size = 2
        if style.color is None:
            style.color = '#000000'
    else:
        if style.style is None:
            style.style = 'normal'
        if style.size is None:
            style.size = 16
        if style.color is None:
            style.color = '#000000'
        if style.family is None:
            style.family = 'Microsoft YaHei'
        if style.rotation is None:
            style.rotation = 0

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
    @classmethod
    def bind(cls, node: Self, length: float, theta: float, ax: Axes,
             style: CommonStyleMixin = DefaultNodeStyle) -> Self:
        theta = radians(theta)
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
设计规定：
1. 我们传入的一切角度都是自然直观的度数，不是弧度，范围是0 ~ 360
2. 在进行一个文本布置的时候，bias控制文本偏移目标距离、其内置属性rotation控制文本相当于目标位置的角度
注：文本布置最大的bug在于如果初始画布不是n*n尺寸，会导致直线不与文本平行的问题;
另外，即使初始平行，任意缩放尺寸也会造成平行丢失，办法就是重写resize画布事件.
我不写，只声明
"""
class TextVar(object):
    # 从某点开始布置文本
    def __init__(self, pos: Offset, text: str, ax: Axes, style: TextStyleMixin = DefaultTextStyle):
        StyleAnalyze('text', style)
        # Bug Here：当使用默认的时候，应该是0°的文本方向，但是自动会变，特地修正
        if style == DefaultTextStyle:
            style.rotation = 0
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
    @classmethod
    def distance(cls,
                 node1: NodeVar,
                 node2: NodeVar,
                 ax: Axes,
                 bias: Optional[float] = None,
                 style: TextStyleMixin = DefaultTextStyle,
                 visible: int = 0
                 ) -> Self:
        gap: float = bias if bias else (node1.style.size + style.size) * 0.05
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
            style : TextStyleMixin = DefaultTextStyle
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

# 传入半轴长度figsize控制画布
class NetScene:
    def __init__(self, show_origin=True, *, figsize: float, titledict : Optional[dict] = None):
        self.figure, self.ax = plt.subplots(figsize=(figsize, figsize))
        self.ax.set_aspect('equal', adjustable='box')  # 保持纵横比
        self.ax.set_facecolor('white')
        self.ax.axis('off')
        # 特地提供一个原点设置
        self.Origin: Optional[NodeVar] = None
        if titledict:
            self.ax.set_title(**titledict)
        if show_origin:
            self.Origin = NodeVar(Offset(0, 0), self.ax, CommonStyleMixin(color='red', size=10, style='o'))

    @staticmethod
    def show() -> None:
        plt.show()

    # 1. 添加一个节点
    # - 相对于原点添加
    @overload
    def addNode(self, pos: Offset, style: CommonStyleMixin = DefaultNodeStyle) -> NodeVar: ...
    # - 相对于节点偏移
    @overload
    def addNode(self, pos: Offset, style: CommonStyleMixin = DefaultNodeStyle, *, node: Optional[NodeVar] = None) -> NodeVar: ...

    def addNode(self, pos: Offset, style: CommonStyleMixin = DefaultNodeStyle, *,
                node: Optional[NodeVar] = None) -> NodeVar:
        """
        - def addNode(self, pos: Offset, style: CommonStyleMixin = DefaultNodeStyle) -> NodeVar
        - def addNode(self, pos: Offset, style: CommonStyleMixin = DefaultNodeStyle, *, node: Optional[NodeVar] = None) -> NodeVar
        """
        return NodeVar.offset(node, pos, self.ax, style) if node else NodeVar(pos, self.ax, style)

    # 2. 添加一根线，可以带有箭头。当isBind为True的时候，to位置节点是相对于start位置节点偏移的
    def addLine(self, start: Offset, to: Offset, style: CommonStyleMixin = DefaultLineStyle, arrow=False,
                isBind=False) -> LineVar:
        if isBind:
            to = start + to
        return LineVar(start, to, self.ax, arrow, style)

    # 3. 连接两点
    def addConnect(self, node1: NodeVar, node2: NodeVar, style: CommonStyleMixin = DefaultLineStyle,
                   arrow=False) -> LineVar:
        return LineVar.bind(node1, node2, self.ax, arrow, style)

    # 4. 添加两个点和一条线
    def addLineBindNodes(
            self,
            start: Offset,
            to: Offset,
            arrow=False,
            linestyle: CommonStyleMixin = DefaultLineStyle,
            nodestyle: CommonStyleMixin = DefaultNodeStyle,
            isBind: bool = False
    ) -> Tuple[NodeVar, NodeVar, LineVar]:
        node1 = NodeVar(start, self.ax, nodestyle)
        if isBind:
            to = start + to
        node2 = NodeVar(to, self.ax, nodestyle)
        return node1, node2, LineVar(start, to, self.ax, arrow, linestyle)

    # 5. 添加文本，特地把rotation单独拿出来了
    def addText(self, pos: Offset, text: str, style: TextStyleMixin = DefaultTextStyle, *,
                rotation: Optional[int] = None) -> TextVar:
        if rotation:
            style.rotation = rotation
        return TextVar(pos, text, self.ax, style)

    # 6. 连接两个点并且展示文本，如果文本不指定就展示两点之间距离，点的类型可以是Offset，也可以是NodeVar
    def addTextByConnectNodes(
            self,
            node1: Union[Offset, NodeVar],
            node2: Union[Offset, NodeVar],
            text: Optional[str] = None,
            arrow: bool = False,
            bias: Optional[float] = None,
            linestyle: CommonStyleMixin = DefaultLineStyle,
            nodestyle: CommonStyleMixin = DefaultNodeStyle,
            textstyle: TextStyleMixin = DefaultTextStyle
    ) -> Tuple[NodeVar, NodeVar, LineVar, TextVar]:
        if isinstance(node1, Offset):
            node1 = NodeVar(node1, self.ax, nodestyle)
            node2 = NodeVar(node2, self.ax, nodestyle)
        line = LineVar.bind(node1, node2, self.ax, arrow, linestyle)
        return node1, node2, line, TextVar.parallel(line, text if text else str(round(node1.measure(node2), 0)),
                                                    self.ax, bias, textstyle)

    # 7. 附着于线上的文本
    def addAttachText(
            self,
            line: LineVar,
            text: Optional[str] = None,
            bias: Optional[float] = None,
            style: TextStyleMixin = DefaultTextStyle,
            visible: int = 0
    ) -> TextVar:
        return TextVar.parallel(line, text, self.ax, bias, style) if text else TextVar.length(line, self.ax, bias,
                                                                                              style, visible)

    # 8. 依次连接生成路径列表，但是不绘制点，点数必须不小于2个，可以带有箭头；另外长度不小于三个的时候，closure可以控制是否闭合
    def drawPath(
            self,
            points: List[Offset],
            arrow=False,
            closure=False,
            style: CommonStyleMixin = DefaultLineStyle
    ) -> List[LineVar]:
        length = len(points)
        assert length >= 2
        paths = []
        for i in range(length - 1):
            paths.append(LineVar(points[i], points[i + 1], self.ax, arrow, style))
        if closure and length >= 3:
            paths.append(LineVar(points[-1], points[0], self.ax, arrow, style))
        return paths

    # 9. 依次连接绘制路径，而且绘制点
    def drawPathWithNode(
            self,
            points: List[Offset],
            arrow=False,
            closure=False,
            nodestyle: CommonStyleMixin = DefaultNodeStyle,
            linestyle: CommonStyleMixin = DefaultLineStyle
    ) -> Tuple[List[NodeVar], List[LineVar]]:
        length = len(points)
        assert length >= 2
        ns = []
        ls = []
        length = len(points)
        assert length >= 2
        for i in range(length - 1):
            pos = points[i]
            ns.append(NodeVar(pos, self.ax, nodestyle))
            ls.append(LineVar(pos, points[i + 1], self.ax, arrow, linestyle))
        ns.append(NodeVar(points[-1], self.ax, nodestyle))
        if closure and length >= 3:
            ls.append(LineVar.bind(ns[-1], ns[0], self.ax, arrow, linestyle))
        return ns, ls

    # 10. 依次连接绘制路径，而且绘制点和路径长度
    def drawPathWithNodeAndText(
            self,
            points: List[Offset],
            arrow=False,
            closure=False,
            visible: int = 0,
            bias: float | None = None,
            nodestyle: CommonStyleMixin = DefaultNodeStyle,
            linestyle: CommonStyleMixin = DefaultLineStyle,
            textstyle: TextStyleMixin = DefaultTextStyle
    ) -> Tuple[List[NodeVar], List[LineVar], List[TextVar]]:
        length = len(points)
        assert length >= 2
        ns = []
        ls = []
        ts = []
        length = len(points)
        assert length >= 2
        for i in range(length - 1):
            pos = points[i]
            ns.append(NodeVar(pos, self.ax, nodestyle))
            line = LineVar(pos, points[i + 1], self.ax, arrow, linestyle)
            ls.append(line)
            ts.append(TextVar.length(line, self.ax, bias, textstyle, visible))
        ns.append(NodeVar(points[-1], self.ax, nodestyle))
        if closure and length >= 3:
            ls.append(LineVar.bind(ns[-1], ns[0], self.ax, arrow, linestyle))
            ts.append(TextVar.length(ls[-1], self.ax, bias, textstyle, visible))
        return ns, ls, ts

    # 11. 节点旁边指定文本
    def addTextNearNode(
            self,
            node : NodeVar,
            text : str,
            theta: int = 0,
            bias: Optional[float] = None,
            style : TextStyleMixin = DefaultTextStyle
    ) -> TextVar:
        return TextVar.bind(node, text, self.ax, theta, bias, style)

    # 12. 解析一个邻接矩阵路径无向图，规定0和
    def tranToUndirectedPath(self, ): pass
