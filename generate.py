from warnings import resetwarnings
import numpy as np
from itertools import combinations_with_replacement, combinations
from tqdm import tqdm
from collections import defaultdict
from tabulate import tabulate

DEBUG = 0

# GENERATION PARAMS
HAND_SIZE = 2
MAX_MARGIN = 3
C_MIN_VAL = 1
C_MAX_VAL = 10

# RANKING

# we need to add +1 to MAX_VAL as we want an open range
interval = ''.join([str(x) for x in range(C_MIN_VAL, C_MAX_VAL + 1)])


# Test every possible hands
data = defaultdict(lambda: defaultdict(list))
taboo = defaultdict(dict)
stats = defaultdict(int)
for hand in tqdm(combinations_with_replacement(interval, HAND_SIZE * 2 - 1)):
    if DEBUG:
        print('\n[hand', hand, ']')

    for margin in range(1, MAX_MARGIN + 1):
        losses = []
        wins = []
        valid = True

        # test every hand permutations
        for perm in combinations(hand, len(hand)):
            stats['Num combinations'] += 1
            # divide
            p1 = hand[:HAND_SIZE]
            p2 = hand[HAND_SIZE:]

            # sum
            p1_val = sum([int(x) for x in p1])
            p2_val = sum([int(x) for x in p2])
            if DEBUG:
                print('|-P1', p1, 'sum', p1_val)
                print('|-P2', p2, 'sum', p2_val)

            # conditions
            diff = p1_val - p2_val
            loss = diff - margin
            win = diff + margin

            # invalid bounds
            if loss < C_MIN_VAL:
                stats['Invalid loss'] += 1
                if DEBUG:
                    print('|-Invalid loss val:', p1, p2, loss)
                valid = 0

            if win > C_MAX_VAL:
                stats['Invalid win'] += 1
                if DEBUG:
                    print('|-Invalid win val:', p1, p2, win)
                valid = 0

            if win + p2_val > 21:
                stats['Over'] += 1
                if DEBUG:
                    print('|-Over val:', p1, p2, win, p2_val, win + p2_val)
                valid = 0

            losses.append(loss)
            wins.append(win)

        # record valid combination
        if valid:
            maxv = min(losses)
            minv = max(wins)
            c = '%s/%s' % (maxv, minv)
            hstr = " ".join(hand)
            if hstr not in taboo[c]:
                data[c][margin].append(hstr)
                stats['Valid hand'] += 1
            else:
                stats['Duplicate hand']
            if DEBUG:
                print(c, data[c])
        else:
            stats['Invalid hand'] += 1

    if DEBUG and len(stats['Valid hand']) > DEBUG:
        break

# Ranking
results = []
for c, d in data.items():

    res = {
        'c': c,
        "total_hands": 0,
        "score": 0,
        "breakdown": defaultdict(int),
        "hands": []
    }

    # comput aggregte
    for margin, hands in d.items():

        for hand in hands:
            vals = hand.split(' ')
            distinct = len(set(vals))

            txt = "%s" % distinct
            not_consecutive = 0
            if distinct == HAND_SIZE + 1:
                if int(vals[0]) != int(vals[1]) - 1:

                    if int(vals[1]) != int(vals[2]) - 1:
                        txt += '++'
                        not_consecutive = 2
                    else:
                        txt += '+'
                        not_consecutive = 1

            res['total_hands'] += 1
            res['score'] += distinct * 2 + not_consecutive * 3
            res['breakdown'][distinct] += 1
            res['hands'].append([hand, margin, txt])

    res['hands'] = sorted(res['hands'], key=lambda i: i[2], reverse=True)
    results.append(res)

# write results
fname = 'results/%s_%s_%s_%s.md' % (C_MIN_VAL, C_MAX_VAL,
                                    HAND_SIZE, MAX_MARGIN)
out = open(fname, 'w+')

# header
out.write('\n# Search result\n\n')

out.write("Found %d candidates for the following parameters:\n\n" % len(results))  # noqa

out.write("- Hand size: %d\n" % HAND_SIZE)
out.write("- Max margin: %d\n" % MAX_MARGIN)
out.write("- Min card value: %d\n" % C_MIN_VAL)
out.write("- Max card value: %d\n" % C_MAX_VAL)


# details
for res in sorted(results, key=lambda i: i['score'], reverse=True):
    out.write("\n## %s\n\n" % res['c'])

    out.write("- score: **%d**\n" % res['score'])
    out.write("- total_hands: **%d**\n\n" % (len(res['hands'])))

    # breakdown
    rows = [[k, v] for k, v in res['breakdown'].items()]
    rows = sorted(rows, key=lambda i: i[0], reverse=True)
    out.write(tabulate(rows, headers=['distinct', 'hands'], tablefmt='github'))
    out.write('\n\n')

    # details
    out.write(tabulate(res['hands'], headers=['hand', 'margin', 'distinct'], tablefmt='github'))
    out.write('\n')

# stats
out.write("\n## Statistics\n\n")
out.write(tabulate([[k, v] for k, v in stats.items()], tablefmt='github'))
out.write('\n\n')

# # cards
# for h, res in data.items():
#     out.write("\n## %s\n\n" % h)

#     out.write("- score: **%d**\n" % res['score'])
#     out.write("- hands: **%d**\n" % (len(res['hands'])))

#     out.write("\n### Outcomes Odds\n")
#     rows = [['win', res['win']['min'], res['win']['avg'], res['win']['max']],
#             [
#                 'loss', res['loss']['min'], res['loss']['avg'],
#                 res['loss']['max']
#             ]]
#     s = "\n%s\n" % tabulate(rows,
#                             headers=['', 'min', 'average', 'max'],
#                             tablefmt='github')
#     out.write(s)

#     out.write('\n## Hands\n')

#     out.write(str(res['hands']))

