import datetime
from multiprocessing import Process, Manager, Queue

from tqdm import tqdm

from test import route_flow_in_top
from flow_clustering import flow_clustering, trans_flow


def test_part_1(test_top, num_of_flow, max_flow_size):
    test_top.generate_flows(num_of_flow, max_flow_size)
    start_time = datetime.datetime.now()
    route_flow_in_top(test_top)
    end_time = datetime.datetime.now()
    result = {'route succeed': len(test_top.flows) - len(test_top.flows_cant_be_routed),
              'route failed': len(test_top.flows_cant_be_routed), 'route time': (end_time - start_time).total_seconds()}
    test_top.flows_cant_be_routed.clear()
    for flow in test_top.flows:
        flow.disconnect_flow()
    return result


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
    result_return = {}
    with Manager() as manager:
        result = manager.dict()
        for i in test_slices:
            p = Process(target=_helper_part_2, args=(test_slices[i], i, result,))
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()
        result_return = dict(result)
    return result_return


def _helper_op_send_band_request(slice, paths, demand):
    operation_send = ['band_request', paths, demand]
    return operation_send


def _helper_op_send_band_permission(slice, op_request_recv):
    assert op_request_recv[0] == 'band_request'
    paths = []
    band = op_request_recv[2]
    for (a, b) in op_request_recv[1]:
        if slice.graph[a][b]['bandwidth'] > 2:  # 此处需要修改 每次实验 2*最大flow
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


def _helper_test_part_3(slice, num_of_slice, queue_get, queue_out1, queue_out2, manager):
    start_time = datetime.datetime.now()
    for flow in tqdm(slice.flows):
        op_request_recv = []
        while not queue_get.empty():
            operation = queue_get.get()
            if operation[0] == 'band_permission':
                _helper_op_recv_band_permission(slice, operation)
            else:
                op_request_recv.append(operation)
        assert flow._belong_toploggy == slice.graph
        flow.route_flow(weight='delay')
        if flow.route_state:
            queue_out1.put(['band_request', flow._sp_paths[0], flow.demand, num_of_slice])
            queue_out2.put(['band_request', flow._sp_paths[0], flow.demand, num_of_slice])
        else:
            slice.flows_cant_be_routed.append(flow)
        out_slice_num = [x for x in range(3) if x != num_of_slice]
        for op in op_request_recv:
            assert op[0] == 'band_request'
            if op[3] == out_slice_num[0]:
                queue_out1.put(_helper_op_send_band_permission(slice, op))
            else:
                queue_out2.put(_helper_op_send_band_permission(slice, op))
    end_time = datetime.datetime.now()
    manager['slice' + str(num_of_slice) + ' route success'] = len(slice.flows) - len(slice.flows_cant_be_routed)
    manager['slice' + str(num_of_slice) + ' route failed'] = len(slice.flows_cant_be_routed)
    manager['slice' + str(num_of_slice) + ' route time'] = (end_time - start_time).total_seconds()


def test_part_3(test_top, test_slices):
    queue1 = Queue()
    queue2 = Queue()
    queue3 = Queue()
    result_return = {}
    with Manager() as manager:
        result = manager.dict()
        p1 = Process(target=_helper_test_part_3, args=(test_slices[0], 0, queue1, queue2, queue3, result,))
        p2 = Process(target=_helper_test_part_3, args=(test_slices[1], 1, queue2, queue1, queue3, result,))
        p3 = Process(target=_helper_test_part_3, args=(test_slices[2], 2, queue3, queue1, queue2, result,))
        p1.start()
        p2.start()
        p3.start()
        p1.join()
        p2.join()
        p3.join()
        result_return = dict(result)
    return result_return
