from Nets.NetScene import NetScene
from Nets.BaseVar import Offset
from Nets.BaseMixin import CommonStyleMixin

netS = NetScene(show_origin=True, figsize=6, titledict=dict(label='This is title!'))
node1 = netS.addNode(Offset(5, 6), CommonStyleMixin(size=12, color='red', style='^'))
netS.addNode(Offset(2, 6), node=node1)
netS.addLine(node1.pos, netS.Origin.pos, arrow=True)
netS.addLineBindNodes(Offset(3, 5), Offset(2, 2), True, isBind=True)
netS.addText(Offset(10, 10), "Hello World", rotation=45)
netS.addTextByConnectNodes(Offset(-3.5, -3.5), Offset(-6, -7.2),
                           nodestyle=CommonStyleMixin(style='s', color='blue', size=10))
line1 = netS.addLine(Offset(-4, -5.5), Offset(-4.5, -6), isBind=True,
                     style=CommonStyleMixin(style='--', color='grey', size=2))
netS.addAttachText(line1, bias=-1, visible=0)
netS.drawPathWithNodeAndText([Offset(-2, 2), Offset(-3, 3), Offset(-3, 6), Offset(0, 7), Offset(-0.5, 5.5)],
                             True, True, linestyle=CommonStyleMixin(color='cyan', size=2, style='-'))
netS.drawPath([Offset(-13, -12), Offset(-13, -16), Offset(-17, -16)], closure=True)

netS.show()
