from tqdm import tqdm

from net_toploggy import NetTop
from slice import Slice
import flow_clustering


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
    for i in tqdm(range(num_slice),desc='Generating ' + str(num_slice) + ' slices'):
        slices[i] = Slice(net_top)
    return slices


if __name__ == '__main__':
    net = NetTop()
    slices = gen_slices(net)
    net.generate_flows(800)
    flow_clustering.flow_clustering(net)
    flow_clustering.trans_flow(net, slices)
    # random_classification(net, slices)
    # route_flow_in_top(net)
    # route_flow_in_top(slices[0])
    # route_flow_in_top(slices[1])
    # route_flow_in_top(slices[2])
    flow_cant = len(slices[0].flows_cant_be_routed) \
                + len(slices[1].flows_cant_be_routed) + len(slices[2].flows_cant_be_routed)
    print(str(flow_cant) + ' flows cant be routed in slices')
    print(str(len(net.flows_cant_be_routed)) + ' flows cant be routed in main top')
    exit()