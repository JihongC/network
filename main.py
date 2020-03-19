import argparse
import os

import json

from net_toploggy import NetTop
from test import gen_slices, Test


def get_parser():
    parser = argparse.ArgumentParser(description='Test flow route in slices!')
    parser.add_argument('-n', '--num_of_tests', help='Set the experiment number!', type=int)
    return parser


if __name__ == '__main__':
    parser = get_parser()
    args = vars(parser.parse_args())

    flow_samples = (x for x in range(100, 800, 100))
    for x in flow_samples:
        net = NetTop()
        slices = gen_slices(net)
        test = Test(net, slices, x, 1, 1)
        test.run()
        data = test.data
        data_json = json.dumps(data)
        work_dir = os.getcwd() + '/data/test'+str(args['num_of_tests'])
        file = str(x)+'_flows.json'
        if not os.path.exists(work_dir):
            os.makedirs(work_dir)
        with open(work_dir + '/' + file, 'w') as json_file:
            json_file.write(data_json)
    exit()
