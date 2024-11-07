from typing import Optional, overload, Union, Tuple, List, Iterable, Dict
from copy import copy as tempCopy

import matplotlib.pyplot as plt

from Nets.BaseMixin import TextStyleMixin, CommonStyleMixin, DefaultTextStyle, DefaultLineStyle, DefaultNodeStyle
from Nets.BaseVar import NodeVar, LineVar, TextVar, Offset

# 传入半轴长度figsize控制画布
class NetScene:
    def __init__(self, show_origin=True, *, figsize : float, titledict : Optional[dict] = None, cfg=True):
        self.figure, self.ax = plt.subplots(figsize=(figsize, figsize))
        if cfg:
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
    def addNode(self, pos: Offset, style: CommonStyleMixin = tempCopy(DefaultNodeStyle)) -> NodeVar: ...
    # - 相对于节点偏移
    @overload
    def addNode(self, pos: Offset, style: CommonStyleMixin = tempCopy(DefaultNodeStyle), *, node: Optional[NodeVar] = None) -> NodeVar: ...
    def addNode(self, pos: Offset, style: CommonStyleMixin = tempCopy(DefaultNodeStyle), *,
                node: Optional[NodeVar] = None) -> NodeVar:
        """
        - def addNode(self, pos: Offset, style: CommonStyleMixin = tempCopy(DefaultNodeStyle)) -> NodeVar
        - def addNode(self, pos: Offset, style: CommonStyleMixin = tempCopy(DefaultNodeStyle), *, node: Optional[NodeVar] = None) -> NodeVar
        """
        return NodeVar.offset(node, pos, self.ax, style) if node else NodeVar(pos, self.ax, style)

    # 2. 添加一根线，可以带有箭头。当isBind为True的时候，to位置节点是相对于start位置节点偏移的
    def addLine(self, start: Union[Offset, NodeVar], to: Union[Offset, NodeVar], style: CommonStyleMixin = tempCopy(DefaultLineStyle), arrow=False,
                isBind=False) -> LineVar:
        if isinstance(start, NodeVar):
            start = start.pos
            to = to.pos
        if isBind:
            to = start + to
        return LineVar(start, to, self.ax, arrow, style)

    # 3. 连接两点
    def addConnect(self, node1: NodeVar, node2: NodeVar, style: CommonStyleMixin = tempCopy(DefaultLineStyle),
                   arrow=False) -> LineVar:
        return LineVar.bind(node1, node2, self.ax, arrow, style)

    # 4. 添加两个点和一条线
    def addLineBindNodes(
            self,
            start: Offset,
            to: Offset,
            arrow=False,
            linestyle: CommonStyleMixin = tempCopy(DefaultLineStyle),
            nodestyle: CommonStyleMixin = tempCopy(DefaultNodeStyle),
            isBind: bool = False
    ) -> Tuple[NodeVar, NodeVar, LineVar]:
        node1 = NodeVar(start, self.ax, nodestyle)
        if isBind:
            to = start + to
        node2 = NodeVar(to, self.ax, nodestyle)
        return node1, node2, LineVar(start, to, self.ax, arrow, linestyle)

    # 5. 添加文本，特地把rotation单独拿出来了
    def addText(self, pos: Offset, text: str, style: TextStyleMixin = tempCopy(DefaultTextStyle), *,
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
            linestyle: CommonStyleMixin = tempCopy(DefaultLineStyle),
            nodestyle: CommonStyleMixin = tempCopy(DefaultNodeStyle),
            textstyle: TextStyleMixin = tempCopy(DefaultTextStyle)
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
            style: TextStyleMixin = tempCopy(DefaultTextStyle),
            visible: int = 0,
            parallel=True
    ) -> TextVar:
        return TextVar.parallel(line, text, self.ax, bias, style) if text else TextVar.length(line, self.ax, bias, style, visible, parallel)

    # 8. 依次连接生成路径列表，但是不绘制点，点数必须不小于2个，可以带有箭头；另外长度不小于三个的时候，closure可以控制是否闭合
    def drawPath(
            self,
            points: List[Offset],
            arrow=False,
            closure=False,
            style: CommonStyleMixin = tempCopy(DefaultLineStyle)
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
            nodestyle: CommonStyleMixin = tempCopy(DefaultNodeStyle),
            linestyle: CommonStyleMixin = tempCopy(DefaultLineStyle)
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

    # 10. 依次连接绘制路径，而且绘制点和路径长度；可以用parallel控制文本始终与直线平行
    def drawPathWithNodeAndText(
            self,
            points: List[Offset],
            arrow=False,
            closure=False,
            visible: int = 0,
            bias: float | None = None,
            parallel=True,
            nodestyle: CommonStyleMixin = tempCopy(DefaultNodeStyle),
            linestyle: CommonStyleMixin = tempCopy(DefaultLineStyle),
            textstyle: TextStyleMixin = tempCopy(DefaultTextStyle)
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
            ts.append(TextVar.length(line, self.ax, bias, textstyle, visible, parallel))
        ns.append(NodeVar(points[-1], self.ax, nodestyle))
        if closure and length >= 3:
            ls.append(LineVar.bind(ns[-1], ns[0], self.ax, arrow, linestyle))
            ts.append(TextVar.length(ls[-1], self.ax, bias, textstyle, visible, parallel))
        return ns, ls, ts

    # 11. 节点旁边指定文本
    def addTextNearNode(
            self,
            node : NodeVar,
            text : str,
            theta: int = 0,
            bias: Optional[float] = None,
            style : TextStyleMixin = tempCopy(DefaultTextStyle)
    ) -> TextVar:
        return TextVar.bind(node, text, self.ax, theta, bias, style)

    # 12. 从某点出发到各点的路径图，返回线；也可以相当于某点出发偏移
    def addPtoPs(
            self,
            pos : Offset,
            points : Iterable[Offset],
            arrow=False,
            isBind=False,
            style : CommonStyleMixin = tempCopy(DefaultLineStyle)
    ) -> List[LineVar]:
        return [LineVar(pos, p, self.ax, arrow, style) for p in points] if isBind \
            else [LineVar(pos, pos + p, self.ax, arrow, style) for p in points]

    # 13. 从某点出发到各点的路径图，……，同时返回节点(不包含起点)
    def addPtoPsWithNode(
            self,
            pos: Offset,
            points: Iterable[Offset],
            arrow=False,
            isBind=False,
            linestyle: CommonStyleMixin = tempCopy(DefaultLineStyle),
            nodestyle : CommonStyleMixin = tempCopy(DefaultNodeStyle)
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

    # 14. 从某点出发到各点的路径图，……，同时返回节点(不包含起点)，以及文本，文本为空就显示距离
    def addPtoPsWithNodeAndText(
            self,
            pos: Offset,
            points: Iterable[Offset],
            text : Optional[str] = None,
            arrow=False,
            isBind=False,
            bias : Optional[float] = None,
            linestyle: CommonStyleMixin = tempCopy(DefaultLineStyle),
            nodestyle : CommonStyleMixin = tempCopy(DefaultNodeStyle),
            textstyle : TextStyleMixin = tempCopy(DefaultTextStyle),
            visible : int = 0,
            parallel=True
    ) -> Tuple[List[LineVar], List[NodeVar], List[TextVar]]:
        ls, ns = self.addPtoPsWithNode(pos, points, arrow, isBind, linestyle, nodestyle)
        return (ls, ns, [TextVar.parallel(line, text, self.ax, bias, textstyle) for line in ls]
        if text else [TextVar.length(line, self.ax, bias, textstyle, visible, parallel) for line in ls])

    # 15. 相对于节点偏移的距离和夹角
    def addBindNode(self, node : NodeVar, length : float, theta : float, style : CommonStyleMixin = tempCopy(DefaultNodeStyle)) -> NodeVar:
        return NodeVar.bind(node, length, theta, self.ax, style)

    # 16. 保存图片
    def save(self, fileName : str, format : str = 'png', **kwargs) -> None:
        self.figure.savefig(f"{fileName}.{format}", **kwargs)

    # 17. 根据偏移的距离和夹角绘制所有图元，下一个的节点是相对于上一个节点的
    # 在选择闭合的同时，如果为了避免精确计算闭合线长度而不是自己期待的长度，可以使用closureText传入指定文本替换
    # 如果起点传入的是节点类型，不会被重新创建，而是直接添加到列表第一个
    def addBindsToAll(
            self,
            pos : Union[Offset, NodeVar],
            distances_thetas : Dict[float, float],
            arrow=False,
            closure=False,
            closureText : Optional[str] = None,
            bias : Optional[float] = None,
            linestyle: CommonStyleMixin = tempCopy(DefaultLineStyle),
            nodestyle : CommonStyleMixin = tempCopy(DefaultNodeStyle),
            textstyle : TextStyleMixin = tempCopy(DefaultTextStyle),
            visible : int = 0,
            parallel=False,
    ) -> Tuple[List[NodeVar], List[LineVar], List[TextVar]]:
        ls = []
        ns = []
        ts = []
        if isinstance(pos, Offset):
            last = NodeVar(pos, self.ax, nodestyle)
        else:
            last = pos
        ns.append(last)
        for distance, theta in distances_thetas.items():
            node = NodeVar.bind(last, distance, theta, self.ax, nodestyle)
            ns.append(node)
            line = LineVar.bind(last, node, self.ax, arrow, linestyle)
            ls.append(line)
            ts.append(TextVar.length(line, self.ax, bias, textstyle, visible, parallel))
            last = node
        if closure:
            ls.append(LineVar.bind(last, ns[0], self.ax, arrow, linestyle))
            if parallel:
                textstyle.rotation = ls[-1].theta
            if bias is None:
                bias = (linestyle.size + textstyle.size) * 0.05
            ts.append(TextVar(
                ls[-1].middle + bias,
                closureText if closureText else str(ls[-1].length),
                self.ax,
                textstyle
            ))
        return ns, ls, ts

    # 18. 批量生成节点旁边的文本图元
    def addNodeSigns(
            self,
            texts : Iterable[str],
            nodes : Iterable[NodeVar],
            bias : Optional[float] = None,
            style : TextStyleMixin = tempCopy(DefaultTextStyle),
    ) -> List[TextVar]:
        texts = list(texts)
        ts = []
        for index, node in enumerate(nodes):
            ts.append(TextVar.bind(node, texts[index], self.ax, 0, bias, style))
        return ts

    # 19. 复杂的情况解决方案：如果要生成一个路径，路径包含的点可能已经创建，又怕使用closureText以及大致的偏移角度（不一定准确）导致不精确
    # 第一个必须是node，因为如果是偏移位置，不一定具有准确性，node仍会被添加到节点列表
    # mixins是一个列表，其每个元素是一个List[Optional[NodeVar], Optional[Union[float, str]], Optional[float]]类型有且必须有三个值
    # 第一个值表示节点或者空值，节点不会被创建和操作，只起到访问作用，但是仍然被添加；空值情况使用长度与角偏移创建
    # 第二个值传入字符串，一般在有误差时自己指定长度，否则传入确切长度，二者都表示当前点相对于上一个的偏移；空值的时候忽略创建直线，也代表已有，同时第三值失效
    # 第三个值表示偏移角度
# 总结一下传入情况，从某个节点A开始，要和下一个节点B连接，你传入类似[B, 'len', None]；B和下一个位置Offc相连，传入[None, len, 45]
    def addMixedBindsToALl(
            self,
            node: NodeVar,
            mixins : List,
            arrow=False,
            closure=False,
            closureText: Optional[str] = None,
            bias: Optional[float] = None,
            linestyle: CommonStyleMixin = tempCopy(DefaultLineStyle),
            nodestyle: CommonStyleMixin = tempCopy(DefaultNodeStyle),
            textstyle: TextStyleMixin = tempCopy(DefaultTextStyle),
            visible: int = 0,
            parallel=False,
    ) -> Tuple[List[NodeVar], List[LineVar], List[TextVar]]:
        ns = [node]
        ts = []
        ls = []
        last = node
        for mixin in mixins:
            maybe_node, distance, theta = mixin
            if maybe_node is None:
                maybe_node = NodeVar.bind_like(last, str(distance), theta, self.ax, nodestyle)
            ns.append(maybe_node)
            if distance:
                line = LineVar(last.pos, maybe_node.pos, self.ax, arrow, linestyle)
                ls.append(line)
                text = TextVar.bindOffset(
                    line.middle,
                    f'{float(distance):.{visible}f}',
                    self.ax,
                    textstyle.rotation if not parallel else line.theta,
                    bias,
                    textstyle,
                    linestyle.size
                )
                ts.append(text)
            last = maybe_node
        if closure:
            line = LineVar.bind(last, node, self.ax, arrow, linestyle)
            ls.append(line)
            ts.append(TextVar.bindOffset(
                line.middle,
                closureText, self.ax, textstyle.rotation if not parallel else line.theta, bias, textstyle, linestyle.size
            ))
        return ns, ls, ts

__all__ = ['NetScene']