import argparse
import json
import os

from concurrent_test import test_part_1, test_part_2, test_part_3_cycle, test_part_4, test_part_5, test_part_6
from net_toploggy import NetTop
from test import gen_slices, route_flow_in_top
from flow_clustering import random_classification


def get_parser():
    parser = argparse.ArgumentParser(description='Test flow route in slices!')
    parser.add_argument('-n', '--num_of_tests', help='Set the experiment number!', type=int)
    return parser


# def parallel_average_test(num_of_test):
#     flow_samples = (x for x in range(100, 300, 100))
#     for flow_num in flow_samples:
#         net = NetTop()
#         slices = gen_slices(net)
#         data = {'part1': test_part_1(net, flow_num, 1), 'part2': test_part_2(net, slices),
#                 'part3': test_part_3(net, slices)}
#         data_json = json.dumps(data)
#         work_dir = os.getcwd() + '/data/test' + str(num_of_test)
#         file = str(flow_num) + '_flows.json'
#         if not os.path.exists(work_dir):
#             os.makedirs(work_dir)
#         with open(work_dir + '/' + file, 'w') as json_file:
#             json_file.write(data_json)
#     return str(num_of_test) + 'compelete!'


if __name__ == '__main__':
    parser = get_parser()
    args = vars(parser.parse_args())

    flow_samples = (x for x in range(500, 10000, 200))

    # with ProcessPoolExecutor(4) as executor:
    #     jobs = []
    #     for i in range(4):
    #         jobs.append(executor.submit(parallel_average_test, i))

    # for x in flow_samples:
    #     net = NetTop()
    #     slices = gen_slices(net)
    #     test = Test(net, slices, x, 1, 1)
    #     test.run()
    #     data = test.data
    #     data_json = json.dumps(data)
    #     work_dir = os.getcwd() + '/data/test'+str(args['num_of_tests'])
    #     file = str(x)+'_flows.json'
    #     if not os.path.exists(work_dir):
    #         os.makedirs(work_dir)
    #     with open(work_dir + '/' + file, 'w') as json_file:
    #         json_file.write(data_json)

    for flow_num in flow_samples:
        net = NetTop()
        slices = gen_slices(net)
        net.generate_flows(150)
        random_classification(net, slices)
        route_flow_in_top(net)
        net.flows.clear()
        net.flows_cant_be_routed.clear()
        for i, s in slices.items():
            for flow in s.flows:
                flow.route_flow(weight='delay')
        for i, s in slices.items():
            s.flows.clear()
            s.flows_cant_be_routed.clear()
        data = {'part1': test_part_1(net, flow_num, 1), 'part2': test_part_2(net, slices),
                'part3': test_part_3_cycle(net, slices), 'part4': test_part_4(net, slices),
                'part5': test_part_5(net, slices), 'part6': test_part_6(net, slices)}
        data_json = json.dumps(data)
        work_dir = os.getcwd() + '/data/test' + str(args['num_of_tests'])
        file = str(flow_num) + '_flows.json'
        if not os.path.exists(work_dir):
            os.makedirs(work_dir)
        with open(work_dir + '/' + file, 'w') as json_file:
            json_file.write(data_json)
    exit()
