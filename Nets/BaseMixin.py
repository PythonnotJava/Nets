# 我想基于matplotlib做一个网络图的库，考虑有以下几种类节点类、线类、文本类，这三种都有以下属性
from typing import Literal, Self
from dataclasses import dataclass

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

__all__ = ['CommonStyleMixin', 'TextStyleMixin', 'DefaultLineStyle', 'DefaultMixinStyle', 'DefaultNodeStyle', 'DefaultTextStyle', 'StyleAnalyze']
