def find_key_by_value(input_string, dictionary):
    for key, values in dictionary.items():
        if input_string in values:
            return key
    return input_string  # 如果没有找到匹配的值，返回输入的字符串本身


# 示例字典
example_dict = {"text": ["text1", "text2"]}

# 测试函数
result1 = find_key_by_value("text1", example_dict)
print(result1)  # 输出: text

result2 = find_key_by_value("text3", example_dict)
print(result2)  # 输出: text3
