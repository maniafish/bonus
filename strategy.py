# coding: utf-8

import math
import sys


class SmallStg(object):
    """ 重复执行压大小定投, 每轮下注大小small(1, 小; 0, 大), 每轮固定收益因子factor, 定投轮次count
    收益曲线呈指数
    """
    def __init__(self, principal, count):
        self.small = 1
        self.count = count
        self.principal = principal
        self.current_multi = 0
        self.set_bet_multi()
        self.factor = 1
        self.factor_list = []

    def set_bet_multi(self):
        """ 设定每轮定投倍率 """
        self.bet_multi = []
        sum_multi = 0
        for i in range(0, self.count):
            index = i + 1
            bet = math.ceil(sum_multi + index * math.pow(1.5, index))
            self.bet_multi.append(bet)
            sum_multi += bet

    def set_factor(self):
        """ 设定收益因子 """
        if not self.principal:
            print "no principal"
            sys.exit(1)

        # 达到本金上限后，额外计算round_remain轮定投sum
        round_remain = 100
        factor = self.factor
        set_factor_flag = True
        while True:
            if round_remain <= 0:
                print "factor: {0}, sum_bet: {1}".format(
                    self.factor, self.factor_list[self.factor_index])
                return

            sum_bet = self.round_bonus(factor)
            self.factor_list.append(sum_bet)
            if sum_bet > self.principal / 2:
                if set_factor_flag:
                    self.factor = factor - 1
                    # 当前factor 对应factor_list的游标
                    self.factor_index = len(self.factor_list) - 2
                    if self.factor < 1:
                        print "invalid principal: {0}".format(self.principal)
                        sys.exit(1)

                    set_factor_flag = False

                round_remain -= 1

            factor += 1

    def adjust_factor_list(self):
        """ sum_bet列表后移 """
        l = len(self.factor_list)
        # 取后100个元素
        self.factor_list = self.factor_list[l-100:l]
        self.factor_index = 99
        factor = self.factor
        # 增加100个元素
        for i in range(0, 100):
            self.factor_list.append(self.round_bonus(factor))
            factor += 1

    def set_factor_lower(self):
        """ 收益因子降档 """
        while self.factor_list[self.factor_index] > self.principal / 2:
            if self.factor_index - 1 < 0:
                break

            self.factor_index -= 1
            self.factor -= 1

        print "set factor lower to {0}, sum_bet: {1}".format(
            self.factor, self.factor_list[self.factor_index])

    def set_factor_higher(self):
        """ 收益因子升档 """
        while self.factor_list[self.factor_index + 1] < self.principal / 2:
            self.factor_index += 1
            self.factor += 1

            if self.factor_index + 1 >= len(self.factor_list):
                # 可下注额超过sum_bet list的上限
                self.adjust_factor_list()

        print "set factor higher to {0}, sum_bet: {1}".format(
            self.factor, self.factor_list[self.factor_index])

    def do_bet(self, i, round_map):
        """ 执行一轮定投策略 """
        bet = self.bet_multi[self.current_multi] * self.factor
        self.principal -= bet
        if round_map[i]["single"] == round_map[i].get("pre_single", "--") or round_map[i]["small"] == round_map[i].get("pre_small", "--"):
            self.principal += bet * 1.96
            # 中了则重新定投
            self.current_multi = 0
        else:
            # 没中则执行下一定投倍率
            self.current_multi = (self.current_multi + 1) % self.count

        print "{0}: actual {1}{2}, pre {3}{4}, bet {5}, principal {6}".format(
            i, round_map[i]["single"], round_map[i]["small"],
            round_map[i].get("pre_single", "--"), round_map[i].get("pre_small", "--"),
            bet, self.principal)
        if self.principal < 0:
            print "do strategy failed"
            sys.exit(0)

    def reset_factor(self):
        """ 重设当日收益因子 """
        self.current_multi = 0
        if self.factor_index + 1 >= len(self.factor_list):
            # 可下注额超过sum_bet list的上限
            self.adjust_factor_list()

        if self.factor_list[self.factor_index] > self.principal / 2:
            # sum_bet > 本金; 降低factor
            self.set_factor_lower()
        elif self.factor_list[self.factor_index + 1] < self.principal:
            # 本金达到下个级别的可下注额
            self.set_factor_higher()

    def do(self, round_map):
        """ 执行定投策略 """
        # 设定当前收益因子
        self.set_factor()
        temp_date = 0
        temp_principal = self.principal
        bet_round = 0
        for i in sorted(round_map.keys()):
            if not round_map[i].get("multi", None):
                continue

            date = i / 1000
            if temp_date != date:
                # 新的一天
                bet_round = 0
                temp_date = date
                temp_principal = self.principal
                self.reset_factor()

            # 当日止盈策略(高于30%收益不下注)
            if self.principal >= temp_principal * 1.3:
                print "bonus of {0} = {1} > {2} stop bet today, bet_round = {3}".format(
                    date, self.principal - temp_principal, temp_principal * 0.3, bet_round)
                continue

            # 当日止损策略(低于30%亏损不下注)
            if self.principal <= temp_principal * 0.7:
                print "loss of {0} = {1} > {2} stop bet today, bet_round = {3}".format(
                    date, temp_principal - self.principal, temp_principal * 0.3, bet_round)
                continue

            bet_round += 1
            self.do_bet(i, round_map)

    def round_bonus(self, factor):
        """ 模拟一组完整定投的收益 """
        sum_bet = 0
        bet = 0
        for i, m in enumerate(self.bet_multi):
            if i >= self.count:
                break

            bet = m * factor
            sum_bet += bet
            print "round {0}: bet {1}, sum {2}, bonus: {3}".format(
                i+1, bet, sum_bet, 1.96*bet-sum_bet)

        return sum_bet


class SmallFixStg(SmallStg):
    """ 重复执行压大小定投, 每轮下注大小small(1, 小; 0, 大), 每轮固定收益因子factor, 定投轮次count
    收益曲线成线性
    """
    def set_bet_multi(self):
        """ 设定每轮定投倍率 """
        self.bet_multi = [1]
        sum_multi = 1
        for i in range(1, self.count):
            index = i + 1
            bet = (sum_multi + index)/0.96
            self.bet_multi.append(bet)
            sum_multi += bet


class YfStg(SmallStg):
    """ 盈丰网络定投策略 """
    def set_bet_multi(self):
        self.bet_multi = [1, 3, 8, 24, 72, 216]


class SmallOneThirdStg(SmallFixStg):
    """ 总轮次1/3定投策略 """
    def __init__(self, principal, count):
        super(SmallOneThirdStg, self).__init__(principal, count)
        self.count = count/3

    def round_bonus(self, factor):
        """ 模拟一组完整定投的收益 """
        sum_bet = 0
        bet = 0
        for i, m in enumerate(self.bet_multi):
            if i >= self.count:
                break

            bet = m * factor
            sum_bet += bet
            print "round {0}: bet {1}, sum {2}, bonus: {3}".format(
                i+1, bet, sum_bet, 1.96*bet-sum_bet)

        return 3 * sum_bet


class YfHalfStg(YfStg):
    """ 盈丰网络1/2定投策略 """
    def __init__(self, principal, count):
        super(YfHalfStg, self).__init__(principal, count)
        self.count = count/2


class EightBeginStg(SmallStg):
    """ 从pre的multi为8开始进行1倍定投 """
    def __init__(self, principal, count):
        super(EightBeginStg, self).__init__(principal, count)
        self.count -= 2

    def do(self, round_map):
        """ 执行定投策略 """
        # 设定当前收益因子
        self.set_factor()
        temp_date = 0
        temp_principal = self.principal
        bet_round = 0
        for i in sorted(round_map.keys()):
            if not round_map[i].get("multi", None):
                continue

            date = i / 1000
            if temp_date != date:
                # 新的一天
                bet_round = 0
                temp_date = date
                temp_principal = self.principal

            # 当日止盈策略(高于30%收益不下注)
            if self.principal >= temp_principal * 1.3:
                print "bonus of {0} = {1} > {2} stop bet today, bet_round = {3}".format(
                    date, self.principal - temp_principal, temp_principal * 0.3, bet_round)
                continue

            bet_round += 1
            if int(round_map[i]["multi"]) >= 8:
                self.do_bet(i, round_map)
