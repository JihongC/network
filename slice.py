import copy


class Slice:
    _num_slice = 3

    def __init__(self, net_top):
        self.graph = copy.deepcopy(net_top.graph)
        self.set_band()
        self.flows = []
        self.flows_cant_be_routed = []

    @classmethod
    def set_num_slice(cls, n=3):
        cls._num_slice = n

    def set_band(self):
        """
        初始化均匀分配切片带宽
        """
        for a, b in self.graph.edges:
            self.graph[a][b]['bandwidth'] /= Slice._num_slice