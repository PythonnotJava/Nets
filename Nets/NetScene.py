from typing import *

import matplotlib.pyplot as plt

from Nets.BaseMixin import TextStyleMixin, CommonStyleMixin, DefaultTextStyle, DefaultLineStyle, DefaultNodeStyle
from Nets.BaseVar import NodeVar, LineVar, TextVar, Offset

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

    # 12. 从某点出发到各点的路径图，返回线；也可以相当于某点出发偏移
    def addPtoPs(
            self,
            pos : Offset,
            points : Iterable[Offset],
            arrow=False,
            isBind=False,
            style : CommonStyleMixin = DefaultLineStyle
    ) -> List[LineVar]:
        return [LineVar(pos, p, self.ax, arrow, style) for p in points] if isBind \
            else [LineVar(pos, pos + p, self.ax, arrow, style) for p in points]

    # 13. 从某点出发到各点的路径图，……，同时返回节点
    def addPtoPsWithNode(
            self,
            pos: Offset,
            points: Iterable[Offset],
            arrow=False,
            isBind=False,
            linestyle: CommonStyleMixin = DefaultLineStyle,
            nodestyle : CommonStyleMixin = DefaultNodeStyle
    ) -> Tuple[List[LineVar], List[NodeVar]]:
        ls = []
        ns = []
        if isBind:
            for p in points:
                ls.append(LineVar(pos, p, self.ax, arrow, linestyle))
                ns.append(NodeVar(p, self.ax, nodestyle))
            return ls, ns
        for p in points:
            off = p + pos
            ls.append(LineVar(pos, off, self.ax, arrow, linestyle))
            ns.append(NodeVar(off, self.ax, nodestyle))
        return ls, ns

    # 14. 从某点出发到各点的路径图，……，同时返回节点，以及文本，文本为空就显示距离
    def addPtoPsWithNodeAndText(
            self,
            pos: Offset,
            points: Iterable[Offset],
            text : Optional[str] = None,
            arrow=False,
            isBind=False,
            bias : Optional[float] = None,
            linestyle: CommonStyleMixin = DefaultLineStyle,
            nodestyle : CommonStyleMixin = DefaultNodeStyle,
            textstyle : TextStyleMixin = DefaultTextStyle,
            visible : int = 0
    ) -> Tuple[List[LineVar], List[NodeVar], List[TextVar]]:
        ls, ns = self.addPtoPsWithNode(pos, points, arrow, isBind, linestyle, nodestyle)
        return (ls, ns, [TextVar.parallel(line, text, self.ax, bias, textstyle) for line in ls]
        if text else [TextVar.length(line, self.ax, bias, textstyle, visible) for line in ls])