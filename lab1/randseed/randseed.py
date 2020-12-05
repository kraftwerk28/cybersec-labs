import random
MAXINT = 2 ** 32

if __name__ == '__main__':
    random.seed(a=0)
    for _ in range(10):
        print(random.randint(0, MAXINT) % 1000)
