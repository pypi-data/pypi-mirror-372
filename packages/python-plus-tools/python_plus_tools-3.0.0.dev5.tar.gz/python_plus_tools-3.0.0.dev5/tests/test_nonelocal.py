def a():
    a = 0

    def b():
        nonlocal a
        a += 1
        return a

    return b


f = a()
g = a()

print(f())
print(f())
print(f())
print(f())

print(g())
print(g())
