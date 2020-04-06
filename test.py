import random

from tqdm import tqdm
from slice import Slice

from flow_clustering import flow_clustering, trans_flow


def route_flow_in_top(top):
    for flow in tqdm(top.flows, desc='Routing'):
        flow.route_flow(weight='delay')
    for flow in top.flows:
        if not flow.route_state:
            top.flows_cant_be_routed.append(flow)
            # top.flows.remove(flow)


def gen_slices(net_top, num_slice=3):
    Slice.set_num_slice(num_slice)
    slices = {}
    for i in tqdm(range(num_slice), desc='Generating ' + str(num_slice) + ' slices'):
        slices[i] = Slice(net_top)
    return slices


class Test:
    def __init__(self, main_top, slices, num_of_flow, max_flow_size, num_of_epoh):
        self.main_top = main_top
        self.slices = slices
        self.num_flow = num_of_flow
        self.max_flow_size = max_flow_size
        self.num_epoh = num_of_epoh

    def _part_1(self):
        res = {}
        self.main_top.generate_flows(self.num_flow, max_flow_size=self.max_flow_size)
        route_flow_in_top(self.main_top)
        res['route succeed'] = len(self.main_top.flows) - len(self.main_top.flows_cant_be_routed)
        res['route failed'] = len(self.main_top.flows_cant_be_routed)
        # self.main_top.flows = self.main_top.flows + self.main_top.flows_cant_be_routed
        self.main_top.flows_cant_be_routed.clear()
        for flow in self.main_top.flows:
            flow.disconnect_flow()
        return res

    def _part_2(self):
        res = {}
        flow_clustering(self.main_top)
        trans_flow(self.main_top, self.slices)
        self.main_top.flows.clear()
        for i, _ in enumerate(self.slices):
            res['slice' + str(i)] = {}
            temp = res['slice' + str(i)]
            route_flow_in_top(self.slices[i])
            temp['route succeed'] = len(self.slices[i].flows) - len(self.slices[i].flows_cant_be_routed)
            temp['route failed'] = len(self.slices[i].flows_cant_be_routed)
        for i, _ in enumerate(self.slices):
            for flow_r in self.slices[i].flows:
                flow_r.disconnect_flow()
                flow_r.set_top(self.main_top)
                self.main_top.flows.append(flow_r)
            self.slices[i].flows.clear()
            # for flow_c_r in self.slices[i].flows_cant_be_routed:
            #     flow_r.set_top(self.main_top)
            #     self.main_top.flows.append(flow_r)
            self.slices[i].flows_cant_be_routed.clear()
        return res

    def _part_3(self):
        random.shuffle(self.main_top.flows)
        slices = self.slices
        for flow in tqdm(self.main_top.flows, desc='part3'):
            assert flow.route_state is False
            flow.set_top(slices[flow.classification])
            slices[flow.classification].flows.append(flow)
            flow.route_flow(weight='delay')
            if flow.route_state:
                path = flow._sp_paths[0]
                for (a, b) in path:
                    self._scheduling_bandwidth(a, b, flow.demand, flow.classification)
            else:
                slices[flow.classification].flows_cant_be_routed.append(flow)
        res = {}
        for i, _ in enumerate(self.slices):
            res['slice' + str(i)] = {}
            temp = res['slice' + str(i)]
            temp['route succeed'] = len(self.slices[i].flows) - len(self.slices[i].flows_cant_be_routed)
            temp['route failed'] = len(self.slices[i].flows_cant_be_routed)
        return res

    def _scheduling_bandwidth(self, a, b, flow_demand, slice_num):
        differ_slice_num = [(1, 2), (0, 2), (0, 1)]  # 只适用三个切片，多了需要改，有空改成通用
        for i in differ_slice_num[slice_num]:
            if self.slices[i].graph[a][b]['bandwidth'] > (2 * self.max_flow_size):
                self.slices[slice_num].graph[a][b]['bandwidth'] += flow_demand
                self.slices[i].graph[a][b]['bandwidth'] -= flow_demand

    def _gen_flow_data(self):
        flow_data = {}
        for flow in self.main_top.flows:
            flow_data['flow' + str(flow.num_of_the_flow)] = {}
            temp = flow_data['flow' + str(flow.num_of_the_flow)]
            temp['class'] = flow.classification
            temp['source'] = flow.source
            temp['destination'] = flow.destination
            temp['demand'] = flow.demand
        return flow_data

    def run(self):
        self.data = {'part 1': self._part_1(), 'part 2': self._part_2(), 'flow data': self._gen_flow_data(),
                     'part 3': self._part_3()}

    def data(self):
        return self.data
