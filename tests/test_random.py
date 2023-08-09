import random


def test_random():
    nums = []
    for i in range(100000):

        num = random.randint(1024, 65535)
        if num not in nums:
            nums.append(num)
            # print("第{}次，num={}".format(i, num))
        else:
            print(f"\n\n第{i}次，重复了， num={num}")
            break