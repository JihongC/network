import random
import datetime
import time
from multiprocessing import Process, Pipe, Manager

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


def test_part_1(test_top, num_of_flow, max_flow_size):
    test_top.generate_flows(num_of_flow, max_flow_size)
    start_time = datetime.datetime.now()
    route_flow_in_top(test_top)
    end_time = datetime.datetime.now()
    result = {'route succeed': len(test_top.flows) - len(test_top.flows_cant_be_routed),
              'route failed': len(test_top.flows_cant_be_routed), 'route time': end_time - start_time}
    test_top.flows_cant_be_routed.clear()
    for flow in test_top.flows:
        flow.disconnect_flow()


def _helper_part_2(slice, num_of_slice, manager):
    start_time = datetime.datetime.now()
    route_flow_in_top(slice)
    end_time = datetime.datetime.now()
    manager['slice' + str(num_of_slice) + ' route time'] = (end_time - start_time).total_seconds()
    manager['slice' + str(num_of_slice) + ' route success'] = len(slice.flows) - len(slice.flows_cant_be_routed)
    manager['slice' + str(num_of_slice) + ' route failure'] = len(slice.flows_cant_be_routed)


def test_part_2(test_top, test_slices):
    flow_clustering(test_top)
    trans_flow(test_top, test_slices)
    jobs = []
    result = Manager().dict()
    for i in test_slices:
        p = Process(target=_helper_part_2, args=(test_slices[i], i, result,))
        jobs.append(p)
        p.start()
    for proc in jobs:
        proc.join()
    return result


def _helper_op_send_band_request(slice, paths, demand):
    operation_send = ['band_request', paths, demand]
    return operation_send


def _helper_op_send_band_permission(slice, op_request_recv):
    assert op_request_recv[0] == 'band_request'
    paths = []
    band = op_request_recv[2]
    for (a, b) in op_request_recv[1]:
        if slice.graph[a][b]['bandwidth'] > 2: # 此处需要修改 每次实验 2*最大flow
            slice.graph[a][b]['bandwidth'] -= band
            paths.append(tuple([a, b]))
    operation_send = ['band_permission', paths, band]
    return operation_send


def _helper_op_recv_band_request(operation):
    assert operation[0] == 'band_request'
    return operation


def _helper_op_recv_band_permission(slice, op_permission_recv):
    assert op_permission_recv[0] == 'band_permission'
    band = op_permission_recv[2]
    for (a, b) in op_permission_recv[1]:
        slice.graph[a][b]['bandwidth'] += band


def _helper_test_part_3(slice, num_of_slice, pipe1, pipe2, manager):
    start_time = datetime.datetime.now()
    for flow in tqdm(slice.flows):
        pipe1_request_ops = []
        pipe2_request_ops = []
        while pipe1.poll():
            operation = pipe1.recv()
            if operation[0] == 'band_permission':
                _helper_op_recv_band_permission(slice, operation)
            else:
                pipe1_request_ops.append(operation)
        while pipe2.poll():
            operation = pipe2.recv()
            if operation[0] == 'band_permission':
                _helper_op_recv_band_permission(slice, operation)
            else:
                pipe2_request_ops.append(operation)
        assert flow._belong_toploggy == slice.graph
        flow.route_flow(weight='delay')
        if flow.route_state:
            pipe1.send(['band_request', flow._sp_paths[0], flow.demand])
            pipe2.send(['band_request', flow._sp_paths[0], flow.demand])
        else:
            slice.flows_cant_be_routed.append(flow)
        for op in pipe1_request_ops:
            pipe1.send(_helper_op_send_band_permission(slice, op))
        for op in pipe2_request_ops:
            pipe2.send(_helper_op_send_band_permission(slice, op))
    end_time = datetime.datetime.now()
    manager['slice' + str(num_of_slice) + ' route success'] = len(slice.flows) - len(slice.flows_cant_be_routed)
    manager['slice' + str(num_of_slice) + ' route failed'] = len(slice.flows_cant_be_routed)
    manager['slice' + str(num_of_slice) + ' route time'] = (end_time-start_time).total_seconds()


def test_part_3(test_top, test_slices):
    result = Manager().dict()
    pipe12_1, pipe12_2 = Pipe()
    pipe13_1, pipe13_3 = Pipe()
    pipe23_2, pipe23_3 = Pipe()
    p1 = Process(target=_helper_test_part_3, args=(test_slices[0], 0, pipe12_1, pipe13_1, result))
    p2 = Process(target=_helper_test_part_3, args=(test_slices[1], 1, pipe12_2, pipe23_2, result))
    p3 = Process(target=_helper_test_part_3, args=(test_slices[2], 2, pipe13_3, pipe23_3, result))
    p1.start()
    p2.start()
    p3.start()
    p1.join()
    p2.join()
    p3.join()
    return result

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
