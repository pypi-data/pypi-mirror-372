def check_value(input_value):
    """
    检查输入值是否为异常类型：
    - 如果是Exception子类则抛出该异常
    - 否则打印该值
    """
    if isinstance(input_value, type) and issubclass(input_value, Exception):
        raise input_value()
    elif isinstance(input_value, Exception):
        raise input_value
    else:
        print(f"输入值: {input_value}")


# 测试用例
check_value(123)  # 输出: 输入值: 123
check_value("hello")  # 输出: 输入值: hello
try:
    check_value(ValueError)  # 会抛出ValueError
except ValueError:
    print("捕获到ValueError")
try:
    check_value(TypeError("类型错误"))  # 会抛出TypeError
except TypeError as e:
    print(f"捕获到TypeError: {e}")
