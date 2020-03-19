from net_toploggy import NetTop
from test import gen_slices, Test


if __name__ == '__main__':
    net = NetTop()
    slices = gen_slices(net)
    test = Test(net, slices, 4000, 1, 1)
    test.run()
    exit()