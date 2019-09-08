from random import randint

import sys

import time


class Calculable:
    # 计算节点抽象类，
    # 事实上可以将这个抽象类及其派生类看作一个二叉树的简单实现：
    # Calculable是所有node类型的基类，
    # Number是leaf node,
    # Calculation是parent node
    def __init__(self):
        self.answer = None  # 计算节点的结果
        self.parameter_1 = None  # 参与计算的入参1
        self.parameter_2 = None  # 参与计算的入参2
        self.equation = []  # 计算节点的算式
        self.op = None  # 计算的操作符： OP = 1:   加法，OP = 2:   减法，OP = 3:   乘法，OP = 4:   除法

    def Answer(self):  # 获得计算节点的结果
        return self.answer

    def Equation(self):  # 获得计算节点的算式
        return self.equation

    def Calculate(self):  # 计算该节点
        pass

    def isNumber(self):  # 是否为整型节点，返回false，
        return False


class Number(Calculable):  # 计算节点派生类：整型数字
    def __init__(self, value):
        Calculable.__init__(self)
        self.answer = value
        self.equation.append(value)
        self.Calculate()

    def isNumber(self):  # 是否为整型节点，返回true
        return True


OP_PLUS = 1  # OP = 1:   加法
OP_MINUS = 2  # OP = 2:   减法
OP_MULTIPLE = 3  # OP = 3:   乘法
OP_DIVISION = 4  # OP = 4:   除法

kOperatorSymbolMap = {}
kOperatorSymbolMap[OP_PLUS] = '+'
kOperatorSymbolMap[OP_MINUS] = '-'
kOperatorSymbolMap[OP_MULTIPLE] = '✕'
kOperatorSymbolMap[OP_DIVISION] = '÷'


def plus(para1, para2):
    return para1 + para2


def multiple(para1, para2):
    return para1 * para2


kOperatorMethodMap = {}
kOperatorMethodMap[OP_PLUS] = plus
kOperatorMethodMap[OP_MINUS] = plus  # 减法的逆运算为加法
kOperatorMethodMap[OP_MULTIPLE] = multiple
kOperatorMethodMap[OP_DIVISION] = multiple  # 除法的逆运算为乘法


class Calculation(Calculable):  # 计算节点派生类：算式结果
    def __init__(self, parameter_1, parameter_2, op):
        Calculable.__init__(self)  # 从父类完成一部分初始化
        if isinstance(
                parameter_1, int
        ):  # 1.isinstance()释义：来判断一个对象是否是一个已知的类型。 2.它用来判断parameter_1参数是否整形，是则用number里的数
            self.parameter_1 = Number(parameter_1)
        elif isinstance(parameter_1, Calculation):  # 否则用参数
            self.parameter_1 = parameter_1
        self.parameter_2 = parameter_2
        self.op = op
        self.Calculate()  # 如果此class里有一个calculate，执行它，如果没有，执行它父类的

    # 关于算式的格式化输出：
    # parameter_1将作为算式的第二部分输出，
    # 符号"+"不会打乱基本运算顺序关系，所以不需要加括号
    # 符号"-"可能会导致括号内"+"和"-"运算变逆运算，比如 "3 -（5 + 2）"与 "3 - 5 + 2"，所以需要括号，
    # 但如果后续的运算为"✕"和"÷"，则运算顺序和符号不受影响，所以不需要括号
    # 符号"✕"可能会导致括号内"+"和"-"运算顺序变化，比如 "3 ✕ （5 + 2）"与 3 ✕ 5 + 2"，所以需要括号，
    # 但如果后续的运算为"✕"和"÷"，则运算顺序和符号不受影响，所以不需要括号
    # 符号"÷"既可能会导致括号内"+"和"-"运算顺序变化，比如 "3 ÷ （5 + 2）"与 3 ÷ 5 + 2"
    # 又可能导致括号内"✕"和"÷"运算变逆运算，比如"3 ÷ （4 ÷ 2）"与 3 ÷ 4 ÷ 2"，无论后续运算是什么都需要括号
    # 如果当前算式的parameter_1是一个数字而非嵌套算式，无需括号

    def NeedBrackets(self):  # 格式化输出，判断是否需要输出括号：
        # 不是加法、入参1不是整型数字、是减法但后续运算有更高优先级、是乘法但后续运算有不低于乘法的优先级，需要输出括号
        return not (self.parameter_1.isNumber() or self.op == OP_PLUS or
                    (self.op == OP_MINUS and self.parameter_1.op > self.op) or
                    (self.op == OP_MULTIPLE
                     and self.parameter_1.op >= self.op))

    def GenerateEquation(self):  # 生成格式化算式
        self.equation = [self.parameter_2, kOperatorSymbolMap[self.op]
                         ]  # 输出第一位和运算符：使用kOperatorSymbolMap中op对应的运算符
        if self.NeedBrackets():  # 是否需要括号
            self.equation.append('(')  # 需要括号，输出
        self.equation.extend(self.parameter_1.Equation())  # 输出第二位
        if self.NeedBrackets():  # 是否需要括号结束
            self.equation.append(')')  # 需要括号结束，输出
        return

    def Calculate(self):

        if self.op == OP_PLUS or self.op == OP_MULTIPLE:  # 加法和乘法直接运算
            self.answer = kOperatorMethodMap[self.op](
                self.parameter_1.answer, self.parameter_2
            )  # 调用kOperatorMethodMap中op对应的函数，直接赋值给self.answer
        elif self.op == OP_MINUS or self.op == OP_DIVISION:  # 减法和除法使用逆运算，避免出现负数和不可整除情况
            answer = kOperatorMethodMap[self.op](
                self.parameter_1.answer,
                self.parameter_2)  # 调用kOperatorMethodMap中op对应的函数，赋值给临时变量answer
            self.answer = self.parameter_2  # 为了后续格式化输出的一致性，交换self.answer和self.parameter_2的内容
            self.parameter_2 = answer
        # 计算完毕。
        self.GenerateEquation()  # 调用算式格式化
        return self.equation


    # 新问题：
    # 如果三个数字和两个运算关系符号都是随机产生的话，有可能造成算式中出现最大是9位的数字！
    # 所以需要在产生数字和运算关系的时候控制一下。
    # 基本原则是：
    # 算式中任何2个数乘法的乘数和被乘数最大为3位数乘2位数，也就是两个数的位数之和不大于5；
    # 算式中任何2个数除法的除数最大为4位数，被除数最大为2位数；因为使用了逆运算来实现除法，所以两个数字的位数都不大于2；
    # 算式中任何2个数加法的加数和被加数最大为4位数；
    # 算式中任何2个数减法的减数和被减数最大为4位数；
    # 三个数运算的原则就应该是：
    # 如果2个运算关系都是加减法，那么3个数都不需要做额外位数限制；
    # 如果2个运算关系都是乘法，那么三个数的位数之和不大于5；
    # 如果2个运算关系都是除法，那么三个数的位数都不大于2；
    # 如果第二个运算关系是加减法，那么第三个数不需要做位数限制；如果第一个运算关系是乘法，那么第一二两个数的位数之和不大于4；如果第一个运算
    # 关系是除法，那么第一二个数字位数都不大于2；
    # 如果第二个运算关系是除法，那么第三个数字位数不大于2；如果第一个运算关系是乘法，那么第一二两个数字都只能是个位数字；如果第一个运算关系
    # 是加法，那么第一二两个数字的和的位数不大于2；如果第一个运算关系是减法，那么第二个数字的位数不大于2，第一个数字不需要更多限制；
    # 如果第二个运算关系是乘法，如果第一个运算关系是加法，那么第一二两个数的和的位数不大于3，第三个数字与这个和的位数之和不大于5；如果第一
    # 个运算关系是减法，那么第一个数字没有额外限制，第二三两个数字位数之和不大于5；如果第一个运算关系是除法，第一二两个数字位数不大于2，第
    # 三个数字位数没有额外限制；
def generateParameters(op1, op2):
    # OP = 1:   加法
    # OP = 2:   减法
    # OP = 3:   乘法
    # OP = 4:   除法
    if op2 < OP_MULTIPLE:  # 第二个运算关系是加减法
        param3 = randint(1, 999)  # 随机产生参与运算数3，1-3位整型
        if op1 == OP_MULTIPLE:  # 第二个运算关系是乘法, 第一二两个数的位数之和不大于4
            param1 = randint(1, 999)  # 随机产生参与运算数1，1-3位整型
            if param1 < 10:  # 第一个数是个位数，第二个数位数不大于3
                param2 = randint(1, 999)  # 随机产生参与运算数2，1-3位整型
            elif param1 < 100:  # 第一个数是两位数，第二个数位数不大于2
                param2 = randint(1, 99)  # 随机产生参与运算数2，1-2位整型
            else:
                param2 = randint(1, 9)  # 随机产生参与运算数2，1位整型
        elif op1 == OP_DIVISION:  # 第一个运算关系是除法,第一二个数字位数都不大于2
            param1 = randint(1, 99)  # 随机产生参与运算数1，1-2位整型
            param2 = randint(1, 99)  # 随机产生参与运算数2，1-2位整型
        else:  # 第一个运算关系是加减法,第一二个数字位数没有额外限制
            param1 = randint(1, 999)  # 随机产生参与运算数1，1-3位整型
            param2 = randint(1, 999)  # 随机产生参与运算数2，1-3位整型
    elif op2 == OP_MULTIPLE:  # 第二个运算关系是乘法
        if op1 == OP_MULTIPLE:  # 第一个运算关系是乘法，三个数的位数之和不大于5
            param1 = randint(1, 999)  # 随机产生参与运算数1，1-3位整型
            if param1 < 10:  # 第一个数是个位数，第二三两个数位数之和不大于4
                param2 = randint(1, 999)  # 随机产生参与运算数2，1-2位整型
                if param2 < 10:  # 第二个数是个位数，第三个数位数不大于3
                    param3 = randint(1, 999)  # 随机产生参与运算数3，1-3位整型
                elif param2 < 100:  # 第二个数是两位数，第三个数位数不大于2
                    param3 = randint(1, 99)  # 随机产生参与运算数3，1-2位整型
                else:  # 第二个数是三位数，第三个数位数只能是个位数
                    param3 = randint(1, 9)  # 随机产生参与运算数3，1位整型
            elif param1 < 100:  # 第一个数是两位数，第一二两个数位数位数之和不大于3
                param2 = randint(1, 99)  # 随机产生参与运算数2，1-2位整型
                if param2 < 10:  # 第二个数是个位数，第三个数位数不大于2
                    param3 = randint(1, 99)  # 随机产生参与运算数3，1-2位整型
                else:  # 第二个数是两位数，第三个数位数只能是个位数
                    param3 = randint(1, 9)  # 随机产生参与运算数3，1位整型
            else:  # 第一个数是三位数，第二三两个数位数之和不大于2
                param2 = randint(1, 9)  # 随机产生参与运算数2，1位整型
                param3 = randint(1, 9)  # 随机产生参与运算数3，1位整型
        elif op1 == OP_PLUS:  # 第一个运算关系是加法，第一二两个数的和的位数不大于3，第三个数字与这个和的位数之和不大于5
            param1 = randint(1, 999)  # 随机产生参与运算数1，1-3位整型
            param2 = randint(1, 999 - param1)  # 第一二两个数的和的位数不大于3
            if param1 + param2 < 100:  # 第一二两个数的和位数不大于2，第三个数字没有额外限制
                param3 = randint(1, 999)  # 随机产生参与运算数3，1-3位整型
            else:  # 第一二两个数的和是3位数，第三个数字位数不大于2
                param3 = randint(1, 99)  # 随机产生参与运算数3，1-2位整型
        elif op1 == OP_MINUS:  # 第一个运算关系是减法，第一个数字没有额外限制，第二三两个数字位数之和不大于5
            param1 = randint(1, 999)  # 随机产生参与运算数1，1-3位整型
            param2 = randint(1, 999)  # 随机产生参与运算数2，1-3位整型
            if param2 < 100:  # 第一个数的位数不大于2，第三个数字没有额外限制
                param3 = randint(1, 999)  # 随机产生参与运算数3，1-3位整型
            else:  # 第一个数是三位数，第三个数字位数不大于2
                param3 = randint(1, 99)  # 随机产生参与运算数3，1-2位整型
        else:  # 第一个运算关系是除法，第一二两个数字位数不大于2，第三个数字位数没有额外限制
            param1 = randint(1, 99)  # 随机产生参与运算数1，1-2位整型
            param2 = randint(1, 99)  # 随机产生参与运算数2，1-2位整型
            param3 = randint(1, 999)  # 随机产生参与运算数3，1-3位整型
    else:  # 第二个运算关系是除法,第三个数字位数不大于2
        param3 = randint(1, 99)  # 随机产生参与运算数3，1-2位整型
        if op1 == OP_MULTIPLE:  # 第一个运算关系是乘法，第一二两个数字都只能是个位数字
            param1 = randint(1, 9)  # 随机产生参与运算数1，1位整型
            param2 = randint(1, 9)  # 随机产生参与运算数2，1位整型
        elif op1 == OP_PLUS:  # 第一个运算关系是加法，第一二两个数字的和的位数不大于2
            param1 = randint(1, 99)  # 随机产生参与运算数1，1-2位整型
            param2 = randint(1, 99 - param1)  # 随机产生参与运算数1，1-2位整型
        elif op1 == OP_MINUS:  # 第一个运算关系是减法，第二个数字的位数不大于2，第一个数字不需要更多限制
            param1 = randint(1, 999)  # 随机产生参与运算数1，1-3位整型
            param2 = randint(1, 99)  # 随机产生参与运算数2，1-2位整型
        else:  # 第一个运算关系是除法，第一二两个数的位数都不大于2
            param1 = randint(1, 99)  # 随机产生参与运算数1，1-2位整型
            param2 = randint(1, 99)  # 随机产生参与运算数2，1-2位整型
    return param1, param2, param3


def question(order, count):
    '''
    :param order:
    :param count:
    :return: 如输入结果不正确，返回否；如果输入结果正确，返回是；
    unit test 用例如下：
    >>> test1=Calculation(1,2,OP_PLUS)
    >>> test1.Answer()
    3
    >>> test1.Equation()
    [2, '+', 1]

    >>> test2=Calculation(3,2,OP_MINUS)
    >>> test2.Answer()
    2
    >>> test2.Equation()
    [5, '-', 3]

    >>> test3=Calculation(4,5,OP_MULTIPLE)
    >>> test3.Answer()
    20
    >>> test3.Equation()
    [5, '✕', 4]

    >>> test4=Calculation(7,3,OP_DIVISION)
    >>> test4.Answer()
    3
    >>> test4.Equation()
    [21, '÷', 7]

    >>> test5=Calculation(Calculation(7,3,OP_PLUS),2,OP_PLUS)
    >>> test5.Answer()
    12
    >>> test5.Equation()
    [2, '+', 3, '+', 7]

    >>> test6=Calculation(Calculation(7,3,OP_PLUS),2,OP_MINUS)
    >>> test6.Answer()
    2
    >>> test6.Equation()
    [12, '-', '(', 3, '+', 7, ')']

    >>> test7=Calculation(Calculation(7,3,OP_PLUS),2,OP_MULTIPLE)
    >>> test7.Answer()
    20
    >>> test7.Equation()
    [2, '✕', '(', 3, '+', 7, ')']

    >>> test8=Calculation(Calculation(7,3,OP_PLUS),2,OP_DIVISION)
    >>> test8.Answer()
    2
    >>> test8.Equation()
    [20, '÷', '(', 3, '+', 7, ')']

    >>> test9=Calculation(Calculation(7,3,OP_MINUS),2,OP_PLUS)
    >>> test9.Answer()
    5
    >>> test9.Equation()
    [2, '+', 10, '-', 7]

    >>> test10=Calculation(Calculation(7,3,OP_MINUS),2,OP_MINUS)
    >>> test10.Answer()
    2
    >>> test10.Equation()
    [5, '-', '(', 10, '-', 7, ')']

    >>> test11=Calculation(Calculation(7,3,OP_MINUS),2,OP_MULTIPLE)
    >>> test11.Answer()
    6
    >>> test11.Equation()
    [2, '✕', '(', 10, '-', 7, ')']

    >>> test12=Calculation(Calculation(7,3,OP_MINUS),2,OP_DIVISION)
    >>> test12.Answer()
    2
    >>> test12.Equation()
    [6, '÷', '(', 10, '-', 7, ')']

    >>> test13=Calculation(Calculation(7,3,OP_MULTIPLE),2,OP_PLUS)
    >>> test13.Answer()
    23
    >>> test13.Equation()
    [2, '+', 3, '✕', 7]

    >>> test14=Calculation(Calculation(7,3,OP_MULTIPLE),2,OP_MINUS)
    >>> test14.Answer()
    2
    >>> test14.Equation()
    [23, '-', 3, '✕', 7]

    >>> test15=Calculation(Calculation(7,3,OP_MULTIPLE),2,OP_MULTIPLE)
    >>> test15.Answer()
    42
    >>> test15.Equation()
    [2, '✕', 3, '✕', 7]

    >>> test16=Calculation(Calculation(7,3,OP_MULTIPLE),2,OP_DIVISION)
    >>> test16.Answer()
    2
    >>> test16.Equation()
    [42, '÷', '(', 3, '✕', 7, ')']

    >>> test17=Calculation(Calculation(7,3,OP_DIVISION),2,OP_PLUS)
    >>> test17.Answer()
    5
    >>> test17.Equation()
    [2, '+', 21, '÷', 7]

    >>> test18=Calculation(Calculation(7,3,OP_DIVISION),2,OP_MINUS)
    >>> test18.Answer()
    2
    >>> test18.Equation()
    [5, '-', 21, '÷', 7]

    >>> test19=Calculation(Calculation(7,3,OP_DIVISION),2,OP_MULTIPLE)
    >>> test19.Answer()
    6
    >>> test19.Equation()
    [2, '✕', 21, '÷', 7]

    >>> test20=Calculation(Calculation(7,3,OP_DIVISION),2,OP_DIVISION)
    >>> test20.Answer()
    2
    >>> test20.Equation()
    [6, '÷', '(', 21, '÷', 7, ')']

    '''

    # OP = 1:   加法
    # OP = 2:   减法
    # OP = 3:   乘法
    # OP = 4:   除法
    op1 = randint(1, 4)  # 随机产生运算符号1，整型 1-4
    op2 = randint(1, 4)  # 随机产生运算符号2，整型 1-4

    # param1 = randint(1, 999)  # 随机产生参与运算数1，1-3位整型
    # param2 = randint(1, 999)  # 随机产生参与运算数2，1-3位整型
    # param3 = randint(1, 999)  # 随机产生参与运算数3，1-3位整型
    # param4 = randint(1, 999)
    # op3 = randint(1, 4)

    param1, param2, param3 = generateParameters(op1, op2)

    # print(param1, param2, param3, param4)
    # print(param1, param2, param3)
    # math = Calculation(Calculation(Calculation(param1, param2, op1), param3, op2), param4, op3)
    math = Calculation(Calculation(param1, param2, op1), param3, op2)
    print("Question [" + str(order) + "/" + str(count) + "]: ", "".join(
        str(i) for i in math.Equation()), '=')  # 输出题目算式到终端
    custom_input = input("Your answer please: ")  # 等待使用者输入结果
    if custom_input == str(math.Answer()):  # 如果输入结果正确，返回是
        print("Congratulations, Your answer: %s is correct." %
              custom_input)  # 提示结果正确
        return True
    else:  # 如果输入结果不正确，返回否
        print("Sorry, the answer %s you given is not correct, it should be %d."
              % (custom_input, math.Answer()))  # 提示结果错误
        return False


def supplyService():
    response = []
    for i in range(0, 5):
        # OP = 1:   加法
        # OP = 2:   减法
        # OP = 3:   乘法
        # OP = 4:   除法
        op1 = randint(1, 4)  # 随机产生运算符号1，整型 1-4
        op2 = randint(1, 4)  # 随机产生运算符号2，整型 1-4

        # param1 = randint(1, 999)  # 随机产生参与运算数1，1-3位整型
        # param2 = randint(1, 999)  # 随机产生参与运算数2，1-3位整型
        # param3 = randint(1, 999)  # 随机产生参与运算数3，1-3位整型
        # param4 = randint(1, 999)
        # op3 = randint(1, 4)

        param1, param2, param3 = generateParameters(op1, op2)
        math = Calculation(Calculation(param1, param2, op1), param3, op2)
        response.append(math)
    return response


def main(argv):
    count = 5  # 习题总数，默认值=5
    if int(argv[1]) != 0:  # 如果有给出运行参数，且符合有效范围，赋值给习题总数
        count = int(argv[1])
    start = time.time()
    correction_count = 0  # 正确习题总数
    for math in supplyService():
        print(math.Equation())
        print(math.Answer())

    for i in range(0, count):
        if question(i + 1, count):
            correction_count += 1  # question()方法返回是，意味着此习题回答正确，将正确习题总数+1
    print("Totally %d questions with accuracy ratio: %s" %
          (count, "{:.2%}".format(correction_count / count)))  # 输出题目总数和正确率
    print("Totally %s used." % (time.strftime(
        "%H hours, %M minutes, %S seconds",
        time.gmtime(time.time() - start))))  # 输出所有习题完成时长


if __name__ == "__main__":

    # 单元测试执行方法：python math2-for-race.py
    # 普通运行方法：python math2-for-race.py ${四则运算题目个数}
    if len(sys.argv) > 1:
        main(sys.argv)
    else:
        import doctest

        doctest.testmod()
