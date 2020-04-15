import numpy as np
from sklearn.cluster import KMeans
from slice import Slice


def _helper_gen_ring_num(node_class, igp_num, ring_num, num_core, num_converge, num_access, conv_num=3):
    node_classes = ('Metro Core', 'Backbone Convergence', 'Ordinary Convergence', 'Access Convergence', 'Access')
    if node_class == node_classes[0] or node_class == node_classes[1]:
        return igp_num
    elif node_class == node_classes[2] or node_class == node_classes[3]:
        return ring_num + (num_core + (igp_num - 1) * num_converge)
    else:
        return ring_num + (num_core + num_core * num_converge + (igp_num - 1) * num_converge * num_access + (
                num_converge - 1) * num_access)


def flow_clustering(net_top):
    # num_core = net_top._num_core
    # num_converge = net_top._num_converge
    # num_access = net_top._num_access
    node = net_top.graph.nodes
    data = np.empty([len(net_top.flows), 4])
    for i, flow in enumerate(net_top.flows):
        data[i, 0] = flow.source
        data[i, 1] = flow.destination
        data[i, 2] = _helper_gen_ring_num(node[flow.source]['node class'], node[flow.source]['IGP_num'],
                                          node[flow.source]['ring_num'], net_top._num_core, net_top._num_converge,
                                          net_top._num_access)
        data[i, 3] = _helper_gen_ring_num(node[flow.destination]['node class'], node[flow.destination]['IGP_num'],
                                          node[flow.destination]['ring_num'], net_top._num_core, net_top._num_converge,
                                          net_top._num_access)
    kmeans_flow = KMeans(3).fit(data)
    for i, flow in enumerate(net_top.flows):
        flow.classification = int(kmeans_flow.labels_[i])


def random_classification(net_top, slices):
    count = 0
    num_of_flow = len(net_top.flows)
    slice_num = 0
    for x in net_top.flows:
        count += 1
        if count == 333:
            slice_num = 1
        if count == 666:
            slice_num = 2
        x.set_top(slices[slice_num])
        slices[slice_num].flows.append(x)
        # net_top.flows.remove(x)


def trans_flow(net_top, slice):
    """
    将分类后的流从主拓扑类的flows属性中转移到对应的切片的flows中
    """
    for flow in net_top.flows:
        flow.set_top(slice[flow.classification])
        slice[flow.classification].flows.append(flow)
        # net_top.flows.remove(flow)