import networkx as nx


class Flow:
    def __init__(self, num_of_the_flow, s, d, demand, top):
        self.num_of_the_flow = num_of_the_flow
        self.classification = 0
        self._sp_nodes = []
        self._sp_paths = []
        self._num_paths = 0
        self.source = s
        self.destination = d
        self.demand = demand
        self._belong_toploggy = top
        self.route_state = False
        # self._max_hop =

    # def _add_tunnels(self, tunnel):
    #     self._sp_nodes.append(tunnel)
    #     self._num_paths += 1

    def route_flow(self, weight='weight'):
        toploggy = self._belong_toploggy
        self._sp_nodes.clear()
        self._num_paths = 0
        try:
            temp_sp = nx.shortest_path(toploggy, self.source, self.destination, weight=weight)
        except nx.NetworkXNoPath:
            # print('没有最短路径')
            self._num_paths = 0
            self.route_state = False
            return
        unable_trans = self._reduce_band_in_top(toploggy, temp_sp)
        temp_band = []
        while len(unable_trans) > 0:
            #         print('recompute SP')
            for a, b, attrs in unable_trans:
                temp_band.append(tuple([a, b, toploggy[a][b]]))
                toploggy.remove_edge(a, b)
            try:
                temp_sp = nx.shortest_path(toploggy, self.source, self.destination, weight=weight)
            except nx.NetworkXNoPath:
                # print('没有最短路径')
                self._num_paths = 0
                self.route_state = False
                for a, b, attrs in temp_band:
                    toploggy.add_edge(a, b)
                    for k, v in attrs.items():
                        toploggy[a][b][k] = v
                return
            unable_trans = self._reduce_band_in_top(toploggy, temp_sp)
        for a, b, attrs in temp_band:
            toploggy.add_edge(a, b)
            for k, v in attrs.items():
                toploggy[a][b][k] = v
        self._sp_nodes.append(temp_sp)
        self._num_paths += 1
        self.route_state = True
        self._gen_path()

    def disconnect_flow(self):
        if not self.route_state:
            return
        self.route_state = False
        for path in self._sp_paths:
            for (a, b) in path:
                self._belong_toploggy[a][b]['bandwidth'] += self.demand
        self._num_paths = 0
        self._sp_nodes.clear()
        self._sp_paths.clear()

    def set_top(self, top):
        self._belong_toploggy = top.graph

    def _gen_path(self):
        for path in self._sp_nodes:
            self._sp_paths.append(list(zip(path[:-1], path[1:])))

    def _reduce_band_in_top(self, toploggy, tunnels):  # 返回最短路径中容量不够的链接
        paths = list(zip(tunnels[:-1:], tunnels[1:]))
        unable_to_trans = []
        sign = True
        for a, b in paths:
            if toploggy[a][b]['bandwidth'] < self.demand:
                sign = False
                unable_to_trans.append(tuple([a, b, toploggy[a][b]]))
        if not sign:
            return unable_to_trans
        for a, b in paths:
            toploggy[a][b]['bandwidth'] -= self.demand
        return unable_to_trans
