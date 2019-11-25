# coding: utf-8

import sys
import re
import traceback
from datetime import datetime
import strategy

stg_map = {
    "1": "SmallStg",
    "2": "SmallFixStg",
    "3": "YfStg",
    "4": "SmallOneThirdStg",
    "5": "YfHalfStg",
    "6": "EightBeginStg",
}

count = 6


class Round(object):
    """ 轮次信息处理类 """
    def __init__(self):
        self.round_map = {}

    def parse(self):
        """ 处理文件 """
        for fileline in open("simulate_input.txt"):
            filename = fileline.strip()
            i = 0
            for line in open(filename):
                try:
                    keys = re.split('\t| *', line.rstrip())
                    if i % 2 == 0:
                        # 暂存当前轮次，供下一行使用
                        tmp = int(keys[0])
                        if len(keys) != 3:
                            raise Exception("invalid round keys: {0}".format(keys))

                        self.round_map[tmp] = {
                            "time": datetime.strptime(
                                "{0} {1}".format(keys[1], keys[2]),
                                "%Y-%m-%d %H:%M:%S"),
                        }
                    else:
                        # 完善当前轮次信息
                        self.round_map[tmp]["point"] = keys[0]
                        self.round_map[tmp]["single"] = keys[1]
                        self.round_map[tmp]["small"] = keys[2]
                        if len(keys) > 3:
                            self.round_map[tmp]["pre_single"] = keys[3]
                            self.round_map[tmp]["pre_small"] = keys[4]
                            self.round_map[tmp]["multi"] = keys[5]

                except Exception:
                    print "Invalid line {0}: {1}".format(i+1, line)
                    print traceback.format_exc()

                finally:
                    i += 1

    def show(self, key):
        """ 顺序展示 """
        for i in sorted(self.round_map.keys()):
            if not key:
                print "{0}: {1}".format(i, self.round_map[i])
            else:
                print "{0}: {1}".format(i, self.round_map[i].get(key, None))

    def set_strategy(self, stg):
        """ 定投策略设定 """
        self.stg = stg

    def do_strategy(self):
        """ 定投策略执行 """
        self.stg.do(self.round_map)


def help():
    print "Usage: python simulate.py [option] [args] [strategy]"
    print "仿真处理的文件名在simulate_input.txt中"
    print "Options:"
    print "bonus: 模拟一组完整定投收益; `bonus 1 2`表示执行SmallStg, 收益因子为2"
    print "show: 展示当前走势。small: 大小; single: 单双; 不输入<args>则为全部输出"
    print "do: 执行相应定投策略; `do 1 324`表示执行SmallStg, 本金为324"
    print "strategy: 表示当前策略，策略映射表如下:"
    print "\t1: SmallStg, 重复指数收益小定投"
    print "\t2: SmallFixStg, 重复固定收益小定投"
    sys.exit(1)


def main():
    if len(sys.argv) < 2:
        help()

    if sys.argv[1] == 'bonus':
        stg_class = getattr(strategy, stg_map[sys.argv[2]])
        stg = stg_class(None, count)
        print stg_map[sys.argv[2]]
        stg.round_bonus(int(sys.argv[3]))
        sys.exit(0)

    # 处理文件
    r = Round()
    r.parse()

    if sys.argv[1] == 'show':
        if len(sys.argv) == 2:
            r.show('')
            sys.exit(0)
        else:
            r.show(sys.argv[2])
            sys.exit(0)
    elif sys.argv[1] == 'do':
        stg_class = getattr(strategy, stg_map[sys.argv[2]])
        stg = stg_class(int(sys.argv[3]), count)
        print stg_map[sys.argv[2]]
        r.set_strategy(stg)
        r.do_strategy()
    else:
        help()


if __name__ == "__main__":
    main()
