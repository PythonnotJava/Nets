from Nets.NetScene import NetScene
from Nets.BaseVar import Offset, NodeVar, TextVar
from Nets.BaseMixin import CommonStyleMixin, TextStyleMixin

netS = NetScene(show_origin=True, titledict=dict(label='Nets Example'), figsize=6)
ns1, _, _ = netS.addBindsToAll(
    Offset(0, 0),
    distances_thetas={
        4 : 60,
        3.7 : 280,
        3.4 : 225
    },
    closure=True,
    closureText='3.5',
    bias=0,
    parallel=True
)

A, B, C, D = ns1
ns2, _, _ = netS.addBindsToAll(
    A,
    distances_thetas={
        6.2 : 145,
        7.2 : 220,
        7 : 335
    },
    parallel=True,
    closure=True,
    closureText='3.5',
    bias=0
)

netS.save('example')
netS.show()


