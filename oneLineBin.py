def toBin(n, size):
    return "".join([str(n // (2**i) % 2) for i in range(size)][::-1])


for i in range(10):
    print(toBin(i))
