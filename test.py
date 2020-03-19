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
            top.flows.remove(flow)


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
        res['route succeed'] = len(self.main_top.flows)
        res['route failed'] = len(self.main_top.flows_cant_be_routed)
        self.main_top.flows = self.main_top.flows + self.main_top.flows_cant_be_routed
        self.main_top.flows_cant_be_routed.clear()
        for flow in self.main_top.flows:
            flow.disconnect_flow()
        return res

    def _part_2(self):
        res = {}
        flow_clustering(self.main_top)
        trans_flow(self.main_top, self.slices)
        for i, _ in enumerate(self.slices):
            res['slice'+str(i)] = {}
            temp = res['slice'+str(i)]
            route_flow_in_top(self.slices[i])
            temp['route succeed'] = len(self.slices[i].flows)
            temp['route failed'] = len(self.slices[i].flows_cant_be_routed)
        for i, _ in enumerate(self.slices):
            for flow_r in self.slices[i].flows:
                flow_r.disconnect_flow()
                flow_r.set_top(self.main_top)
                self.main_top.flows.append(flow_r)
            self.slices[i].flows.clear()
            for flow_c_r in self.slices[i].flows_cant_be_routed:
                flow_r.set_top(self.main_top)
                self.main_top.flows.append(flow_r)
            self.slices[i].flows_cant_be_routed.clear
        return res

    def _part_3(self):
        random.shuffle(self.main_top.flows)
        slices = self.slices
        for flow in self.main_top.flows:
            assert flow.route_state is False
            flow.set_top(slices[flow.classification])
            slices[flow.classification].flows.append(flow)

    def run(self):
        print(self._part_1())
        print(self._part_2())


