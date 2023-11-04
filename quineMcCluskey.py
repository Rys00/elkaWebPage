import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--vars", help="Number of variables in function")
parser.add_argument("--ones", help="List of function's ones (split with ';')")
parser.add_argument(
    "--summary",
    help="Whether to only print summary or full step-by-slep solution (0 for step-by-step, 1 for summary)",
    default="0"
)
parser.add_argument(
    "--mergeLevel",
    help="How many functions ones were inputted",
    default="1"
)
parser.add_argument(
    "--wildcards", help="List of function's wildcards (split with ';')", default=""
)
parser.add_argument(
    "--html",
    help="Whether or not output in html format (0 for standard, 1 for html)",
    default="0",
)

args = parser.parse_args()

howManyVars = int(args.vars)
mergeLevel = int(args.mergeLevel)

def validateData(char):
    try:
        i = int(char)
        return True
    except:
        return False

ones = []
onesRaw = [int(i) for i in filter(validateData, args.ones.split(";"))]
for one in onesRaw:
    if one not in ones and onesRaw.count(one) == mergeLevel:
        ones.append(one)
#ones = [0, 1, 4, 5, 6, 10, 11, 12, 14, 16, 17, 18, 19, 20, 21, 22, 25, 26, 27, 28, 29, 30, 31]

wildcards = []
wildcardsRaw = [int(i) for i in filter(validateData, args.wildcards.split(";"))] if args.wildcards != "" else []
for wildcard in wildcardsRaw:
    if wildcard not in wildcards and wildcardsRaw.count(wildcard) == mergeLevel:
        wildcards.append(wildcard)

html = bool(int(args.html))
summary = bool(int(args.summary))


class QuineMcCluskey(object):
    def __init__(self, n: int, ones, wildcards=[], html=False, summaryOnly=False) -> None:
        self.n = n
        self.ones = ones
        self.wildcards = wildcards

        msg = ""
        msg += f"Attempting to minimize function of {self.n} variables \n"
        msg += f"With ones at positions: {self.ones}\n"
        msg += f"And wildcards at positions: {self.wildcards}\n\n"

        if html:
            msg += f"<a*s*href=\"karnaughMap.html?amount={self.n}&direction=horizontal&ones={';'.join([str(o) for o in self.ones])}&wildcards={';'.join([str(w) for w in self.wildcards])}\">Karnaugh map for this function</a>\n"
        
        if not self.ones:
            msg += f"\nNo data given!\n"
            if html:
                msg = msg.replace("\n", "<br/>")
                msg = msg.replace(" ", "&nbsp")
                msg = msg.replace("*s*", " ")
            print(msg)
            return
        
        self.binStringMask = "{:0>" + str(self.n) + "}"
        self.groups = []
        self.results = []
        self.createGroups()

        
        if not summaryOnly:
            msg += self.printGroups(self.groups, "Printing initial groups:")
        result = self.merge()
        i = 1
        while result:
            if not summaryOnly:
                msg += self.printGroups(self.groups, f"Printing groups after merge nr {i}")
            result = self.merge()
            i += 1
        self.results = self.results[::-1]
        if not summaryOnly:
            msg += self.printGroups([self.results], "Possible functions:")

        self.currentSmallestSet = [9999, []]
        analyzed = self.analyzeResults()

        if not summaryOnly:
            msg += self.printGroups(
                [analyzed[0]], f"Required functions (are covering {analyzed[1]}):"
            )
            if len(analyzed[3]) > 0:
                msg += self.printGroups(
                    [analyzed[3]],
                    f"Functions to choose from (need to cover {analyzed[2]}):",
                )
            if len(analyzed[4]) > 0:
                msg += self.printGroups(
                    [analyzed[4]],
                    f"Automatically chosen functions (from above):",
                )

        msg += self.printGroups(
            [analyzed[5]], f"Final proposed set (covers all ones):"
        )

        if html:
            msg = msg.replace("\n", "<br/>")
            msg = msg.replace(" ", "&nbsp")
            msg = msg.replace("*s*", " ")

        print(msg)

    def analyzeResults(self):
        onesUsed = {}
        toRemoveId = []
        required = []

        # resetting all to 0
        for i in self.ones:
            onesUsed[i] = 0

        # counting how many functions cover specific one
        for elem in self.results:
            for one in elem[0]:
                if one in onesUsed:
                    onesUsed[one] += 1

        # identify functions which are required
        for i, elem in enumerate(self.results):
            for one in elem[0]:
                if one in onesUsed and onesUsed[one] == 1:
                    required.append(elem)
                    toRemoveId.append(i)
                    break

        # remove them from possible functions (they now have their separate list)
        for i in toRemoveId[::-1]:
            self.results.pop(i)
        # reset list
        toRemoveId = []

        # resetting all to 0
        for i in self.ones:
            onesUsed[i] = 0

        # set 1 for all covered by required functions
        for elem in required:
            for one in elem[0]:
                if one in onesUsed:
                    onesUsed[one] = 1

        # identify redundant functions
        for i, elem in enumerate(self.results):
            useful = False
            for one in elem[0]:
                if one in onesUsed and onesUsed[one] == 0:
                    useful = True
            if not useful:
                toRemoveId.append(i)

        # remove them from possible functions
        for i in toRemoveId[::-1]:
            self.results.pop(i)

        # calculate uncovered ones
        onesFromRequired = []
        onesFromChosen = []
        for one in onesUsed.keys():
            if one in onesUsed and onesUsed[one] == 0:
                onesFromChosen.append(one)
            else:
                onesFromRequired.append(one)

        # hide unrelevant ones in left functions
        toChoose = []
        
        for elem in self.results:
            toChoose.append(([(i if (i in elem[0]) else " ") for i in onesFromChosen], elem[1]))
        
        #try to find optimal set of chooseable functions
        candidates = []
        for elem in self.results:
            neededOnes = [o for o in elem[0] if o in onesFromChosen]
            candidates.append((neededOnes, elem[1], elem[0]))
        
        self.chooseSmallestSet(onesFromChosen, [], candidates)

        chosen = [(e[2], e[1]) for e in self.currentSmallestSet[1]]
        
        final = required+chosen

        return required, onesFromRequired, onesFromChosen, toChoose, chosen, final
    
    def chooseSmallestSet(self, onesToCover, testedSet, functionsToScan):
        if len(testedSet) == self.currentSmallestSet[0]:
            return
        if not onesToCover:
            if len(testedSet) < self.currentSmallestSet[0]:
                self.currentSmallestSet[0] = len(testedSet)
                self.currentSmallestSet[1] = testedSet
            return
        for i, func in enumerate(functionsToScan):
            newOnes = [o for o in onesToCover if o not in func[0]]
            newSet = testedSet.copy()
            newSet.append(func)
            self.chooseSmallestSet(newOnes, newSet, functionsToScan[i+1:])

    def printGroups(self, groups, label: str = "Printing groups:"):
        # styles
        maxNumberSize = len(str(2**self.n)) + 1
        maxGroupSize = len(groups[0][0][0]) * (maxNumberSize + 1) + 2
        tabSize = 6
        maxGroupNumber = len(str(len(groups)))
        maskSize = self.n * 2
        multiplierSize = maxGroupNumber + 1
        maxLabelSize = len(" group nr  ") + maxGroupNumber
        padding = (
            tabSize * 3 + maxGroupSize + maskSize + multiplierSize - maxLabelSize
        ) // 2

        msg = ""
        msg += f"\n{label}\n"
        for i, group in enumerate(groups):
            nr = ("{:<" + str(maxGroupNumber) + "}").format(str(i))
            msg += "-" * padding + f" group nr {nr} " + "-" * padding + "\n"
            for elem in group:
                msg += " " * (tabSize // 2) + (
                    "{:<" + str(multiplierSize) + "}"
                ).format(
                    f"{len(elem[0])}x"
                )  # 8x
                groupInfo = " ".join(
                    ("{:<" + str(maxNumberSize) + "}").format(str(e) + ",")
                    for e in elem[0]
                )
                msg += (" " * tabSize + "{:<" + str(maxGroupSize) + "}").format(
                    f"({groupInfo})"
                )
                msg += " " * tabSize + " ".join(list(elem[1]))
                msg += "\n"
        msg += "\n"
        return msg

    def toBinString(self, n: int) -> (str, int):
        b = ""
        ones = 0
        while n != 0:
            mod = n % 2
            n //= 2
            ones += 1 if mod == 1 else 0
            b = str(mod) + b
        return self.binStringMask.format(b), ones

    def createGroups(self):
        self.groups = [[] for i in range(self.n + 1)]
        for one in self.ones + self.wildcards:
            data = self.toBinString(one)
            self.groups[data[1]].append([[one], data[0], False])
        toRemove = []
        for i, group in enumerate(self.groups):
            if len(group) == 0:
                toRemove.append(i)
        for i in toRemove[::-1]:
            self.groups.pop(i)

    def comparePair(self, s1: str, s2: str) -> int:
        diff = 0
        idx = 0
        for i, c in enumerate(s1):
            if c == "-" and s2[i] != "-":
                return -1
            if c != s2[i]:
                diff += 1
                if diff > 1:
                    return -1
                idx = i
        return idx

    def mergeSort(self, t1, t2, lvl: int):
        result = []
        i2 = 0
        for i1 in range(lvl):
            while t2[i2] < t1[i1]:
                result.append(t2[i2])
                i2 += 1
                if i2 == lvl:
                    result.extend(t1[i1:])
                    return result
            result.append(t1[i1])
        result.extend(t2[i2:])
        return result

    def mergeGroups(self, i1: int, i2: int):
        lvl = len(self.groups[i1][0][0])
        merged = []
        for p1 in self.groups[i1]:
            for p2 in self.groups[i2]:
                idx = self.comparePair(p1[1], p2[1])
                if idx == -1:
                    continue
                p1[2] = True
                p2[2] = True
                mask = p1[1][:idx] + "-" + p1[1][idx + 1 :]
                elems = self.mergeSort(p1[0], p2[0], lvl)
                new = [elems, mask, False]
                if not new in merged:
                    merged.append(new)
        return merged

    def merge(self) -> bool:
        newGroups = []
        created = 0
        for i in range(len(self.groups) - 1):
            merged = self.mergeGroups(i, i + 1)
            if len(merged) == 0:
                continue
            newGroups.append(merged)
            created += 1

        for group in self.groups:
            for elem in group:
                if elem[2] == False:
                    self.results.append((elem[0], elem[1]))

        if created == 0:
            return False
        self.groups = newGroups
        return True


if __name__ == "__main__":
    QuineMcCluskey(howManyVars, ones, wildcards, html, summary)