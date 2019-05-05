"""
常用python工具集 类clojure的实现.
为了获得箭头宏以及流程控制宏
这种模式下写代码最好的选择
1. 所有的入参和出参都是一个dict
2. 采用dict表示一个对象, 采用[dicts] 表示集合对象,
arrow 仿clojure箭头宏
arrow_first 参数在第一位的箭头宏
chain 针对对象的链式调用


"""
# import functools


class Variable():
    def __init__(self, funcs: list):
        self.funcs = funcs

    @property
    def value(self):
        """
        启动求值的时候, 才会进行惰性求值的操作.
        """
        # 当vector中的参数为vecor的时候, 进行求值,
        if isinstance(self.funcs[0], self.__class__):
            func = self.funcs[0].value
        else:
            func = self.funcs[0]
        funcs = [func] + self.funcs[1:]
        return arrow_first(funcs)


def chain(chain_list: list):
    """
    实际上有arrow就不需要这个了. 
    本函数主要的目的还是针对链式调用做的.
    面向对象的链式调用, 用法是 第一位是对象,
    后面都是调用该对象的方法.
    用于搭配带链式调用的方法来使用 蕾晒
    class obj():
        def chain_sample(self):
            self.sample = 33
            return self
    只有方法的返回值是它自身的时候,才能这样调用, 这也是个顺序调用方法
    主要是为了降低程序复杂度 简单理解.
    """
    obj = chain_list[0]
    if len(chain_list[1:0]) == 0:
        return None

    for func in chain_list[1:0]:
        obj = getattr(obj, func)(obj)
    return obj


def con_first(funcs: list, arg):
    func = funcs[0]
    # 如果参数里面有Variable对象 则在运算的时候进行求值, (惰性参数求值,)
    m = map(lambda x: x.value if isinstance(x, Variable) else x, funcs[1:])
    m = [x for x in m]
    return func(arg, *m)


def arrow_first(arrows: list):
    """
    箭头宏函数, 用于进行流程化工作这里的所有参数都在第一个位置. 
    """
    target = arrows[0]
    for func in arrows[1:]:
        # 如果遇到的函数是列表, 则第一个是需要运算的函数,
        # 剩下的是后面位置的参数,
        # 上流程的结果放在第一位的参数
        if isinstance(func, list):
            target = con_first(func, target)
        elif isinstance(func, Variable):
            # 如果是Variable对象, 则把上环节的参数塞进variab,然后再运算.
            if isinstance(func.funcs[0], str):
                # 假如中间环节的variable的第一个是字符串
                # 将该字符串替换为上环节的结果
                func.funcs[0] = target
            else:
                # 如果第一个variable是函数, 则将上环节结果塞进funcs去执行.
                func.funcs = [target] + func.funcs
            target = func.value
        else:
            target = func(target)
    return target


def con(funcs: list, arg):
    func = funcs[0]
    # 如果参数里面有Variable对象 则在运算的时候进行求值, (惰性参数求值,)
    m = map(lambda x: x.value if isinstance(x, Variable) else x, funcs[1:])
    m = [x for x in m]
    return func(*m, arg)


def arrow(arrows: list):
    """
    箭头宏函数, 用于进行流程化工作. 
    """
    target = arrows[0]
    for func in arrows[1:]:
        if isinstance(func, list):
            target = con(func, target)
        else:
            target = func(target)
    return target


def statements_func(input_, func, statement):
    res = None
    if statement:
        res = func(input)
    return res


def conds(input_, condstuple: tuple):
    """
    列表式的条件判断示例
    """
    res = None
    for state, func in condstuple:
        if state:
            res = func(input_)
            input_ = res
        else:
            pass
    if res is None:
        print('there is somethin not process')
    return res


def test_embed():
    f = Variable

    def m(x, y):
        return x + y

    def n(x, y):
        return x * y

    res = f([1, [m, 1]])
    nn = f([[n, 2]])

    resut = f([
        res,
        nn,
    ])
    return resut
