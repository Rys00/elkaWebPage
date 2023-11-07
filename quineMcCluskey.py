import argparse
import re
from copy import deepcopy


def chooseSmallestSetOfFunctions(ones, functions):
    currentSmallestSet = [9999, []]

    def chooseSmallestSet(onesToCover, testedSet, functionsToScan):
        if not onesToCover:
            if len(testedSet) < currentSmallestSet[0]:
                currentSmallestSet[0] = len(testedSet)
                currentSmallestSet[1] = [testedSet]
            elif len(testedSet) == currentSmallestSet[0]:
                currentSmallestSet[1].append(testedSet)
            return
        if len(testedSet) == currentSmallestSet[0]:
            return
        for i, func in enumerate(functionsToScan):
            newOnes = [o for o in onesToCover if o not in func[0]]
            newSet = testedSet.copy()
            newSet.append(func)
            chooseSmallestSet(newOnes, newSet, functionsToScan[i + 1 :])

    chooseSmallestSet(ones, [], functions)
    return currentSmallestSet[1]


def sortFunctions(functions):
    byWeight = {}
    for func in functions:
        weight = len(func[0])
        if weight not in byWeight:
            byWeight[weight] = []
        byWeight[weight].append(func)
    byWeight = sorted(byWeight.items())[::-1]
    toReturn = []
    for element in byWeight:
        toReturn.extend(element[1])
    return toReturn


class QuineMcCluskey(object):
    def __init__(
        self,
        varsAmount: int,
        ones,
        wildcards=[],
        excluded=[],
        html=False,
        summaryOnly=False,
    ) -> None:
        self.varsAmount = varsAmount
        self.excluded = []
        for one in excluded:
            if one not in self.excluded and one in ones:
                self.excluded.append(one)
        self.wildcards = wildcards + [
            one for one in self.excluded if one not in wildcards
        ]
        self.ones = [one for one in ones if one not in excluded]
        self.html = html

        msg = ""
        msg += f"Attempting to minimize function of {self.varsAmount} variables \n"
        msg += f"With ones at positions: {self.ones}\n"
        msg += f"And wildcards at positions: {self.wildcards}\n\n"

        if html:
            link = self.generateLinkForKarnaughMap(
                self.varsAmount, self.ones, self.wildcards
            )
            msg += f'<a href="{link}">Karnaugh map for this function</a>\n'

        if not self.ones:
            msg += "\nNo ones specified, can't minimize!\n"
            if html:
                msg = msg.replace("\n", "<br/>")

            self.result = {
                "message": msg,
                "functionsOptions": [[]],
                "coveredOptions": [[]],
            }
            return

        self.binStringMask = "{:0>" + str(self.varsAmount) + "}"
        self.groups = []
        self.results = []
        self.createGroups()

        if not summaryOnly:
            msg += self.printGroups(self.groups, "Printing initial groups:")
        result = self.merge()
        i = 1
        while result:
            if not summaryOnly:
                msg += self.printGroups(
                    self.groups, f"Printing groups after merge nr {i}"
                )
            result = self.merge()
            i += 1
        self.results = self.results[::-1]
        if not summaryOnly:
            msg += self.printGroups([self.results], "Possible functions:")

        analyzed = self.analyzeResults()

        if not summaryOnly:
            if len(analyzed["requiredFunctions"]) > 0:
                msg += self.printGroups(
                    [analyzed["requiredFunctions"]],
                    f"Required functions (are covering {analyzed['onesFromRequired']}):",
                )
            if len(analyzed["functionsToChoose"]) > 0:
                msg += self.printGroups(
                    [analyzed["functionsToChoose"]],
                    f"Functions to choose from (need to cover {analyzed['onesFromChosen']}):",
                )
            for i, chosenOption in enumerate(analyzed["chosenOptions"]):
                msg += self.printGroups(
                    [chosenOption],
                    f"Automatically chosen functions (from above) - option {i+1}:",
                )

        for i, finalOption in enumerate(analyzed["finalOptions"]):
            msg += self.printGroups(
                [finalOption],
                f"Final proposed set - option {i+1} (covers {analyzed['coveredOptions'][i]}):",
            )
            msg += "APN notation: "
            if html:
                msg += "<span style='color:gold'>"
            msg += " + ".join(self.codeToVars(elem[1], html) for elem in finalOption)
            if html:
                copyButton = self.generateCopyButton(finalOption)
                msg += f"</span>{copyButton}\n"

        if html:
            msg = msg.replace("\n", "<br/>")

        self.result = {
            "message": msg,
            "functionsOptions": analyzed["finalOptions"],
            "coveredOptions": analyzed["coveredOptions"],
        }

    def generateCopyButton(self, functions):
        return f"<button onclick='copy(this)' value='{' + '.join(self.codeToVars(elem[1], False) for elem in functions)}'>Copy APN</button>"

    def generateLinkForKarnaughMap(self, varsAmount, ones, wildcards):
        return f"karnaughMap.html?amount={varsAmount}&direction=horizontal&ones={';'.join([str(o) for o in ones])}&wildcards={';'.join([str(w) for w in wildcards])}"

    def codeToVars(self, binCode, html):
        toReturn = []
        for i, c in enumerate(binCode):
            if c == "-":
                continue
            var = f"x{self.varsAmount - i - 1}"
            neg = (
                ("<span style='text-decoration:overline'>" if html else "~")
                if c == "0"
                else ""
            )
            end = ("</span>" if html else "") if c == "0" else ""
            toReturn.append(neg + var + end)
        return "(" + (" " if html else "*").join(toReturn) + ")"

    def analyzeResults(self):
        onesUsed = {}
        toRemoveId = []
        requiredFunctions = []

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
                    requiredFunctions.append(elem)
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
        for elem in requiredFunctions:
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
        functionsToChoose = []

        for elem in self.results:
            functionsToChoose.append(
                ([(i if (i in elem[0]) else " ") for i in onesFromChosen], elem[1])
            )

        # try to find optimal set of chooseable functions
        candidates = []
        for elem in self.results:
            neededOnes = [o for o in elem[0] if o in onesFromChosen]
            candidates.append((neededOnes, elem[1], elem[0]))
        smallestSet = chooseSmallestSetOfFunctions(onesFromChosen, candidates)

        chosenOptions = [[(e[2], e[1]) for e in ss] for ss in smallestSet]

        # final answer
        finalOptions = [requiredFunctions + option for option in chosenOptions]

        coveredOptions = [[] for i in finalOptions]
        for option in range(len(finalOptions)):
            for elem in finalOptions[option]:
                for one in elem[0]:
                    if one not in coveredOptions[option]:
                        coveredOptions[option].append(one)
            coveredOptions[option].sort()

        return {
            "requiredFunctions": requiredFunctions,
            "onesFromRequired": onesFromRequired,
            "onesFromChosen": onesFromChosen,
            "functionsToChoose": functionsToChoose,
            "chosenOptions": chosenOptions,
            "finalOptions": finalOptions,
            "coveredOptions": coveredOptions,
        }

    def printGroups(self, groups, label: str = "Printing groups:"):
        # styles
        if not groups[0]:
            return ""
        maxNumberSize = len(str(2**self.varsAmount)) + 1
        maxGroupSize = len(groups[0][0][0]) * (maxNumberSize + 1) + 2
        tabSize = 6
        maxGroupNumber = len(str(len(groups)))
        maskSize = self.varsAmount * 2
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
        if self.html:
            msg = msg.replace(" ", "&nbsp")
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
        self.groups = [[] for i in range(self.varsAmount + 1)]
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
                if new not in merged:
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
                if elem[2] is False:
                    self.results.append((elem[0], elem[1]))

        if created == 0:
            return False
        self.groups = newGroups
        return True


class CombinedMinimization(object):
    def __init__(
        self,
        varsAmount: int,
        ones,
        wildcards=[],
        combined=False,
        html=False,
        summaryOnly=False,
        finalOnly=False,
    ) -> None:
        self.varsAmount = varsAmount
        self.ones = ones
        self.wildcards = wildcards
        self.funcAmount = len(self.ones)

        self.subsets = {}
        self.subsetsId = {}

        # calculating APN for all function separately
        msg = ""
        for i in range(self.funcAmount):
            result = QuineMcCluskey(
                self.varsAmount, self.ones[i], self.wildcards[i], [], html, summaryOnly
            )
            if not finalOnly or not combined:
                msg += f"<br/><h2>Results for separated function nr {i+1}:</h2><br/>"
                msg += result.result["message"]
            self.subsets[i] = []
            self.subsets[0].append(
                {
                    "regex": f".*{i}.*",
                    "ones": self.ones[i],
                    "wildcards": self.wildcards[i],
                    "name": f"{i+1}",
                    "functionsOptions": result.result["functionsOptions"],
                    "coveredOptions": result.result["coveredOptions"],
                }
            )

        if not combined:
            print(msg)
            return

        # ! python quineMcCluskey.py --vars 4 --ones "2;3;6;7;14;15|2;3;4;5;12;13;14;15|2;3;4;5;9;11;14;15" --summary 1 --html 0 --combined 1
        # creating all possible subsets of set of all functions
        self.createAllSubsets([i for i in range(self.funcAmount)])

        # calculating APN for merge of all functions
        result = QuineMcCluskey(
            self.varsAmount,
            self.subsets[self.funcAmount - 1][0]["ones"],
            self.subsets[self.funcAmount - 1][0]["wildcards"],
            [],
            html,
            summaryOnly,
        )
        self.subsets[self.funcAmount - 1][0]["functionsOptions"] = result.result[
            "functionsOptions"
        ]
        self.subsets[self.funcAmount - 1][0]["coveredOptions"] = result.result[
            "coveredOptions"
        ]
        if not finalOnly:
            msg += f"<br/><h2>Results for merged functions nr {self.subsets[self.funcAmount-1][0]['name']}:</h2><br/>"
            msg += result.result["message"]

        # calculating APN for all merges of functions from remaining subsets
        for lvl in range(self.funcAmount - 2, -1, -1):
            for ss in self.subsets[lvl]:
                toExclude = []
                for lvlHi in range(lvl + 1, self.funcAmount):
                    for ps in self.subsets[lvlHi]:
                        if re.search(ss["regex"], ps["regex"]):
                            toExclude.extend(ps["ones"])

                if not finalOnly:
                    if lvl == 0:
                        msg += f"<br/><h2>Results for function nr {ss['name']} excluding all merges:</h2><br/>"
                    else:
                        msg += f"<br/><h2>Results for merged functions nr {ss['name']} excluding higher merges:</h2><br/>"

                result = QuineMcCluskey(
                    self.varsAmount,
                    ss["ones"],
                    ss["wildcards"],
                    toExclude,
                    html,
                    summaryOnly,
                )
                ss["functionsOptions"] = result.result["functionsOptions"]
                ss["coveredOptions"] = result.result["coveredOptions"]
                if not finalOnly:
                    msg += result.result["message"]

        # calculating optimal set of functions for each function
        self.currSmallestUqFuncSet = {
            "size": 9999,
            "setOptions": [],
            "uniqueFunctionsOptions": [],
        }
        self.counter = 0
        self.counter2 = 0
        self.counter3 = []
        self.chooseSmallestFunctionCombination(self.subsets.copy())
        print(self.currSmallestUqFuncSet["id"], self.counter, self.counter3)
        for setOption in self.currSmallestUqFuncSet["setOptions"]:
            for ss in setOption[0]:
                for i in range(len(ss["functionsOptions"])):
                    ss["functionsOptions"][i] = sortFunctions(ss["functionsOptions"][i])
        for i in range(len(self.currSmallestUqFuncSet["uniqueFunctionsOptions"])):
            self.currSmallestUqFuncSet["uniqueFunctionsOptions"][i] = sortFunctions(
                self.currSmallestUqFuncSet["uniqueFunctionsOptions"][i]
            )
        self.subsets = self.currSmallestUqFuncSet["setOptions"]
        uniqueFunctions = self.currSmallestUqFuncSet["uniqueFunctionsOptions"]

        # calculating final results for each function
        msgr = f"<h2>Found {len(self.subsets)} equally good final propositions:</h2>"
        if len(self.subsets) > 1:
            msgr += "<button onclick='showAllResults(this)'>Show all results</button>"
        for i in range(len(self.subsets)):
            if i == 1:
                msgr += "<div id='allResults' style='display:none'>"
            msgr += f"<br/><h1>Final proposition nr {i+1}:</h1><br/><div style='padding-left: 15px; margin-left: 15px; border-left: 1px solid white'>"
            for ss in self.subsets[i][0]:
                msgr += f"<br/><h2>Proposition for function nr {ss['name']}:</h2><br/>"
                if html:
                    link = result.generateLinkForKarnaughMap(
                        self.varsAmount, ss["ones"], ss["wildcards"]
                    )
                    msgr += f'<a href="{link}">Karnaugh map for this function</a>\n'
                msgr += result.printGroups(
                    [ss["functionsOptions"][0]], "Proposed functions:"
                )
                msgr += "APN notation: "
                if html:
                    msgr += "<span style='color:gold'>"
                msgr += " + ".join(
                    result.codeToVars(elem[1], html)
                    for elem in ss["functionsOptions"][0]
                )
                if html:
                    copyButton = result.generateCopyButton(ss["functionsOptions"][0])
                    msgr += f"</span>{copyButton}\n"

            # ...and printing all used functions
            ones = []
            for func in uniqueFunctions[i]:
                for one in func[0]:
                    if one not in ones:
                        ones.append(one)

            msgr += f"<br/><h2>List of all {len(uniqueFunctions[i])} used functions:</h2><br/>"
            if html:
                link = result.generateLinkForKarnaughMap(self.varsAmount, ones, [])
                msgr += f'<a href="{link}">Karnaugh map if this was a function</a>\n'
            msgr += result.printGroups([uniqueFunctions[i]], "Functions:")
            msgr += "APN notation: "
            if html:
                msgr += "<span style='color:gold'>"
            msgr += " + ".join(
                result.codeToVars(elem[1], html) for elem in uniqueFunctions[i]
            )
            if html:
                copyButton = result.generateCopyButton(uniqueFunctions[i])
                msgr += f"</span>{copyButton}\n</div>"

        if len(self.subsets) > 1:
            msgr += "</div>"
        msg = msgr + msg
        if html:
            msg = msg.replace("\n", "<br/>")

        print(msg)

    def chooseSmallestFunctionCombination(self, fromSet, spacer=""):
        self.counter += 1
        # executing for each combination
        for lvl in range(self.funcAmount):
            for i, ps in enumerate(fromSet[lvl]):
                for j in range(1, len(ps["functionsOptions"])):
                    newVariant = deepcopy(fromSet)
                    newVariant[lvl][i]["functionsOptions"] = [
                        newVariant[lvl][i]["functionsOptions"][j]
                    ]
                    newVariant[lvl][i]["coveredOptions"] = [
                        newVariant[lvl][i]["coveredOptions"][j]
                    ]
                    self.chooseSmallestFunctionCombination(newVariant, spacer + "    ")
                ps["functionsOptions"] = [ps["functionsOptions"][0]]
                ps["coveredOptions"] = [ps["coveredOptions"][0]]

        # appending all promising functions
        for ss in fromSet[0]:
            for lvl in range(1, self.funcAmount):
                for ps in fromSet[lvl]:
                    if re.search(ss["regex"], ps["regex"]):
                        ss["functionsOptions"][i].extend(ps["functionsOptions"][0])

        # selecting the best functions set
        for ss in fromSet[0]:
            ss["functionsOptions"] = chooseSmallestSetOfFunctions(
                ss["ones"], ss["functionsOptions"][0]
            )

        self.counter2 = 0
        self.chooseBestSetCombination(fromSet)
        self.counter3.append(self.counter2)

    def chooseBestSetCombination(self, fromSet):
        self.counter2 += 1
        # execution for each option
        for i, ss in enumerate(fromSet[0]):
            for j in range(1, len(ss["functionsOptions"])):
                newVariant = deepcopy(fromSet)
                newVariant[0][i]["functionsOptions"] = [
                    newVariant[0][i]["functionsOptions"][j]
                ]
                self.chooseBestSetCombination(newVariant)
            ss["functionsOptions"] = [ss["functionsOptions"][0]]

        # calculating unique functions
        uniqueFunctions = {}
        for ss in fromSet[0]:
            for func in ss["functionsOptions"][0]:
                if func[1] not in uniqueFunctions:
                    uniqueFunctions[func[1]] = func[0]
        uniqueFunctions = [(uniqueFunctions[func], func) for func in uniqueFunctions]
        # ! print(len(uniqueFunctions))
        if len(uniqueFunctions) < self.currSmallestUqFuncSet["size"]:
            self.currSmallestUqFuncSet["size"] = len(uniqueFunctions)
            self.currSmallestUqFuncSet["setOptions"] = [deepcopy(fromSet)]
            self.currSmallestUqFuncSet["uniqueFunctionsOptions"] = [uniqueFunctions]
            self.currSmallestUqFuncSet[
                "id"
            ] = f"{self.counter}-{self.counter2} ({len(uniqueFunctions)})"
        elif len(uniqueFunctions) == self.currSmallestUqFuncSet["size"]:
            self.currSmallestUqFuncSet["setOptions"].append(deepcopy(fromSet))
            self.currSmallestUqFuncSet["uniqueFunctionsOptions"].append(uniqueFunctions)

    def createAllSubsets(self, parentSet):
        parentSetId = ";".join([str(i) for i in parentSet])
        if parentSetId in self.subsetsId:
            return

        self.subsetsId[parentSetId] = 1
        funcAmount = len(parentSet)
        subsetId = []
        subsetName = ""
        onesRaw = []
        wildcardsRaw = []
        for i in range(funcAmount - 1, -1, -1):
            if funcAmount > 2:
                # current set minus i element
                self.createAllSubsets(parentSet[:i] + parentSet[i + 1 :])

            if i == funcAmount - 1:
                subsetName = f"{parentSet[i]+1}" + subsetName
            elif i == funcAmount - 2:
                subsetName = f"{parentSet[i]+1} and " + subsetName
            else:
                subsetName = f"{parentSet[i]+1}, " + subsetName

            subsetId.append(parentSet[i])
            onesRaw.extend(self.ones[parentSet[i]])
            wildcardsRaw.extend(self.wildcards[parentSet[i]])

        ones = []
        wildcards = []
        pom = {}
        for i in range(len(onesRaw)):
            if onesRaw[i] not in pom:
                pom[onesRaw[i]] = 0

            pom[onesRaw[i]] += 1
            if pom[onesRaw[i]] == funcAmount:
                ones.append(onesRaw[i])

        pom = {}
        for i in range(len(wildcardsRaw)):
            if wildcardsRaw[i] not in pom:
                pom[wildcardsRaw[i]] = 0

            pom[onesRaw[i]] += 1
            if pom[wildcardsRaw[i]] == funcAmount:
                wildcards.append(wildcardsRaw[i])

        ones.sort()
        wildcards.sort()

        self.subsets[funcAmount - 1].append(
            {
                "regex": f".*{'.*'.join([str(i) for i in subsetId[::-1]])}.*",
                "ones": ones,
                "wildcards": wildcards,
                "name": subsetName,
                "functions": [],
            }
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--vars", help="Number of variables in function")
    parser.add_argument("--ones", help="List of function's ones (split with ';')")
    parser.add_argument(
        "--summary",
        help="Whether to only print summary or full step-by-slep solution (0 for step-by-step, 1 for summary)",
        default="0",
    )
    parser.add_argument(
        "--combined",
        help="Whether or not to make combined minimization (0 for normal, 1 for combined)",
        default="0",
    )
    parser.add_argument(
        "--finalOnly",
        help="Whether to show only the final functions (0 for all, 1 for only final)",
        default="0",
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
    combined = bool(int(args.combined))
    finalOnly = bool(int(args.finalOnly))
    amount = 1
    if args.ones:
        amount = args.ones.count("|") + 1

    def validateData(char):
        try:
            int(char)
            return True
        except Exception:
            return False

    wildcards = []
    wildcardsRawest = args.wildcards.split("|")
    for i in range(len(wildcardsRawest), amount + 1):
        wildcardsRawest.append("")
    for fi in range(amount):
        wildcards.append([])
        wildcardsRaw = (
            [int(i) for i in filter(validateData, wildcardsRawest[fi].split(";"))]
            if wildcardsRawest[fi] != ""
            else []
        )
        for one in wildcardsRaw:
            if one not in wildcards[fi]:
                wildcards[fi].append(one)

    ones = []
    onesRawest = args.ones.split("|")
    for i in range(len(onesRawest), amount + 1):
        onesRawest.append("")
    for fi in range(amount):
        ones.append([])
        onesRaw = (
            [int(i) for i in filter(validateData, onesRawest[fi].split(";"))]
            if onesRawest[fi] != ""
            else []
        )
        for one in onesRaw:
            if one not in ones[fi]:
                ones[fi].append(one)
    # ones = 0;1;4;5;6;10;11;12;14;16;17;18;19;20;21;22;25;26;27;28;29;30;31

    html = bool(int(args.html))
    summary = bool(int(args.summary))
    CombinedMinimization(
        howManyVars, ones, wildcards, combined, html, summary, finalOnly
    )
