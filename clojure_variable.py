# 标准的录入状况

from collections import OrderedDict

sample = [
    "fdsafsd",
    ["dfsd", "dfasd", "sdfs"],
    ["dfasdf", "dsfas", "dsfasd"],
    ["sdfsda"],
]


def con_first(funcs: list, arg):
    func = funcs[0]
    # 如果参数里面有Variable对象 则在运算的时候进行求值, (惰性参数求值,)
    return func(arg, *funcs[1:])


def arrow_first(arrows: list):
    """
    严格的箭头宏函数, 第一个为待处理内容
    剩下的是处理函数
    如果剩下的函数里面有参数 则从列表第二项开始
    上流程的结果会插入函数执行过程的第一个参数
    """
    target = arrows[0]
    for func in arrows[1:]:
        if isinstance(func, list):
            # 如果是列表则传递参数dd
            target = con_first(func, target)
        elif callable(func):
            # 如果是可执行的
            target = func(target)
        else:
            # 不是列表不可执行啥也不干
            target = target
    return target


class Variable():
    def __init__(self, funcs: list):
        self.funcs = funcs
        self.statuslist = self.get_func_list(funcs)

    @property
    def value(self):
        # 首先获取所有的计算列表
        target = arrow_first([
            self.funcs,
            self.get_func_list,
            self.apply_func_list,
        ])
        return target

    @classmethod
    def get_func_map(cls, arrow_list: list):
        res = OrderedDict()
        for i, action_list in enumerate(arrow_list):
            if isinstance(action_list, list):
                for ii, action in enumerate(action_list):
                    if isinstance(action, list):
                        raise RuntimeError('超过三重的列表嵌套是不允许的')
                    res[(i, ii)] = action
            else:
                res[(i, 0)] = action
        # 清除掉空列表
        res = {k: v for k, v in res.items() if len(v) != 0}
        # 清除掉只有字符串的列表
        res = {k: v for k, v in res.items() if not isinstance(v, str)}
        return res

    @classmethod
    def get_func_list(self, arrow_list: list):
        res = []
        for i, li in enumerate(arrow_list):
            if isinstance(li, list):
                for ii, action in enumerate(li):
                    if isinstance(action, list):
                        raise RuntimeError('超过三重的列表嵌套是不允许的')
                    res.append([i, ii, action])
            else:
                res.append([i, 0, li])
        # 清除掉空列表
        # 清除掉只有字符串的列表
        # 作为代价本系统不允许只有字符串做起始输入
        res = [x for x in res if not isinstance(x[2], str)]
        return res

    @classmethod
    def apply_func_map(cls, func_map: OrderedDict):
        for k, action in func_map.items():
            if k == (0, 0):
                target = action
            else:
                target = action(target)
        return target

    @classmethod
    def apply_func_list(cls, func_list: list):
        target = func_list[0][2]
        # if isinstance(target, Variable):
        #     # 如果是一个Variable实例 则求值
        #     target = target.value
        target = cls.actbyinstance_con(target)

        for i, j, action in func_list[1:]:
            target = cls.actbyinstance_car(action, target)
            # if isinstance(action, Variable):
            #     # 如果是一个Variable实例 则把第一个放入
            #     target = action.variable_in_car(target, action)
            # else:
            #     target = action(target)
        return target

    def iscompleted(self):
        if isinstance(self.funcs[0], str):
            return False
        else:
            return True

    @classmethod
    def variable_in_car(cls, action, target):
        """
        当Variable 在运算列表的最后时, 如何处理
        """
        #funcs = [[-1, -1, target]] + action.funcs
        func_list = [[-1, -1, target]] + cls.get_func_list(action.funcs)
        target = action.apply_func_list(func_list)
        return target

    @classmethod
    def variable_in_con(cls, target):
        """
        当Variable在整个运算列表第一个时的效果
        """
        return target.value

    @classmethod
    def tuple_func(cls, tuplef: tuple, target):
        """
        如果是tuple 则说明这是一个带参数函数,
        将上一环节的数据塞进第一个参数里,
        target 为上一环节的输入
        tuple为函数列表
        """
        func = tuplef[0]
        arg = tuplef[1:]

        return func(target, *arg)

    @classmethod
    def actbyinstance_car(cls, action, target):
        """
        target 上一步结果
        action 本回合动作
        return : 本回合结果
        """
        if isinstance(action, Variable):
            # 如果是一个Variable实例 则把第一个放入
            return action.variable_in_car(action, target)
        elif isinstance(action, tuple):
            return cls.tuple_func(action, target)
        else:
            return action(target)

    @classmethod
    def actbyinstance_con(cls, action):
        if isinstance(action, Variable):
            # 如果是一个Variable实例 则求值
            return action.value
        else:
            return action


def test():
    def m(x):
        return x + 1

    def n(x):
        return x - 1

    mm = Variable([
        5,
        m,
        n,
    ])

    nm = Variable([
        m,
        n,
    ])

    yo = Variable([
        mm,
        nm,
        m,
        n,
    ])

    print(yo.value)
