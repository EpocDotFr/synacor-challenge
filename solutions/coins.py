# This script solves the so called "coins challenge" found in the text adventure game. It's brute-forcing, but it works.
import itertools


def run():
    coins = {
        2: 'red', # 2 dots
        9: 'blue', # 9 dots
        5: 'shiny', # pentagon
        7: 'concave', # 7 dots
        3: 'corroded', # triange
    }

    for combination in itertools.permutations(coins.keys(), len(coins)):
        a, b, c, d, e = combination

        if a + b * pow(c, 2) + pow(d, 3) - e == 399:
            print('Correct combination is: {}'.format(
                ', '.join([coins[v] for v in combination])
            ))

            break


if __name__ == '__main__':
    run()
