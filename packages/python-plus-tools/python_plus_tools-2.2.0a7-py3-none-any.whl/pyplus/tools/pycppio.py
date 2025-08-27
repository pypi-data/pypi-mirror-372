class _OStream:
    def __lshift__(self, value):
        print(value, end="")
        return self


class _IStream:
    def __init__(self):
        self.inputs = []

    def __rshift__(self, value: object):
        self.inputs.append(input())
        return self

    def clear_inputs(self):
        self.inputs.clear()
        return self

    def get_inputs(self):
        return self.inputs


cout = _OStream()
cin = _IStream()

endl = "\n"

if __name__ == "__main__":
    name = None
    age = None
    cout << "Enter your name: "
    cin >> name
    cout << "Enter your age: "
    cin >> age
    name = cin.inputs[0]
    age = cin.inputs[1]
    cout << "Name: " << name << endl << "Age: " << age << endl
    cin.clear_inputs()
