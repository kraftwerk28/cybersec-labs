#!/usr/bin/env python
from utils import plot_ioc

lines = [
    'c3437dbc7c1255d3a21d444d86ebf2e9234c22bd',
    'ef81042e1e86acb765718ea37393a1292452bbcc',
    'a3c1509bd8df6d72992b312e4f6b7f4ce7fd3f3d',
    '3f95edc0399d06d4b84e7811dd79272c69c8ed3a',
    '5d519dc941b90db6e4c1de9ecda3d6c1a3217d18',
    '4f8278c89ad16da05fec4fdfc61fe44798b92720',
    '422962ba8ed1df2564b3d568b0c3808c4bb5d9e2',
    'de986a93db399554210777239b937b4b8fecc001',
    '1ef50edc9f644f7fe379d61418546a4497354298',
    'fd80598eb62148b61e75200c0a5efede36395445',
    'de68c179fe674d5b0f405154240b3fae9f0c2422',
    '2886fd6babd9c984c23628614709c15631206ad5',
    'a6f1723d68ddb143f08d65807bede824bdad67af',
    'e291da3f08936b73d735c3ff923e90982a89d1e6',
]


def line2ints(line):
    s = []
    while line:
        ch = line[:2]
        s.append(int(ch, 16))
        line = line[2:]
    return s


if __name__ == '__main__':
    alphabet = [chr(x) for x in range(256)]
    ints = line2ints(''.join(lines))
    # print(ints)
    # plot_ioc([chr(i) for i in ints], alphabet)
