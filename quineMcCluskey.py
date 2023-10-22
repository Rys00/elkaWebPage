import sys

#Dla tych co chcą użyć

#Tu wpisz ile zmiennych ma twoja funkcja
ileZmiennych = int(sys.argv[1])
#Tu wpisz wszystkie jedynki funkcji
jedynki = [int(i) for i in sys.argv[2].split(";")]
#print(ileZmiennych, jedynki)

# I tyle! Uruchom skrypt. Wyniki wraz z krokami zostaną zapisane w pliku groups.txt



class QuineMcCluskey(object):

    def __init__(self, n: int, ones: [int]) -> None:
        self.n = n
        self.ones = ones
        self.binStringMask = "{:0>"+str(self.n)+"}"
        self.groups = []
        self.results = []
        self.createGroups()

        msg = ""
        msg += f"Attempting to minimize function of {self.n} variables \nwith ones at positions: {self.ones}\n\n"
        msg += self.printGroups(self.groups, "Printing initial groups:")
        result = self.merge()
        i = 1
        while result == True:
            msg += self.printGroups(self.groups, f"Printing groups after merge nr {i}")
            result = self.merge()
            i += 1
        self.results = self.results[::-1]
        msg += self.printGroups([self.results], "Possible functions:")
        analyzed = self.analyzeResults()
        msg += self.printGroups([analyzed[0]], f"Required functions (are covering {analyzed[1]}):")
        if len(self.results) > 0: msg += self.printGroups([self.results], f"Functions to choose from (need to cover {analyzed[2]}):")
        
        msg.replace("\n", "<br/>")
        msg.replace(" ", "&nbsp")

        print(msg)

    def analyzeResults(self):
        onesUsed = {}
        toRemoveId = []
        required = []

        #resetting all to 0
        for i in self.ones: onesUsed[i] = 0

        #counting how many functions cover specific one
        for elem in self.results:
            for one in elem[0]: onesUsed[one] += 1

        #identify functions which are required
        for i, elem in enumerate(self.results):
            for one in elem[0]:
                if onesUsed[one] == 1:
                    required.append(elem)
                    toRemoveId.append(i)
                    break

        #remove them from possible functions (they now have their separate list)
        for i in toRemoveId[::-1]: self.results.pop(i)
        #reset list
        toRemoveId = []

        #resetting all to 0
        for i in self.ones: onesUsed[i] = 0

        #set 1 for all covered by required functions
        for elem in required:
            for one in elem[0]: onesUsed[one] = 1

        #identify redundant functions
        for i, elem in enumerate(self.results):
            useful = False
            for one in elem[0]:
                if onesUsed[one] == 0:
                    useful = True
            if not useful: toRemoveId.append(i)
        
        #remove them from possible functions
        for i in toRemoveId[::-1]: self.results.pop(i)

        #calculate uncovered ones
        covered = []
        left = []
        for one in onesUsed.keys():
            if onesUsed[one] == 0: left.append(one)
            else: covered.append(one)

        #hide unrelevant ones in left functions
        for i, elem in enumerate(self.results):
            self.results[i] = ([(i if (i in elem[0]) else " ") for i in left], elem[1])
        
        return required, covered, left

    def printGroups(self, groups, label: str = "Printing groups:"):
        #styles
        maxNumberSize = len(str(2**self.n)) + 1
        maxGroupSize = len(groups[0][0][0]) * (maxNumberSize+1) + 2
        tabSize = 6
        maxGroupNumber = len(str(len(groups)))
        maskSize = self.n * 2
        multiplierSize = maxGroupNumber+1
        maxLabelSize = len(" group nr  ") + maxGroupNumber
        padding = (tabSize*3 + maxGroupSize + maskSize + multiplierSize - maxLabelSize) // 2

        msg = ""
        msg += f"\n{label}\n"
        for i, group in enumerate(groups):
            nr = ("{:<"+str(maxGroupNumber)+"}").format(str(i))
            msg += "-"*padding + f" group nr {nr} " + "-"*padding+"\n"
            for elem in group:
                msg += " "*(tabSize//2) + ("{:<"+str(multiplierSize)+"}").format(f"{len(elem[0])}x") #8x
                groupInfo = " ".join(("{:<"+str(maxNumberSize)+"}").format(str(e)+",") for e in elem[0])
                msg += (" "*tabSize + "{:<"+str(maxGroupSize)+"}").format(f"({groupInfo})")
                msg += " "*tabSize + " ".join(list(elem[1]))
                msg += "\n"
        msg += "\n"
        return msg

    def toBinString(self, n: int) -> (str, int):
        b = ""
        ones = 0
        while n != 0:
            mod = n%2
            n //= 2
            ones += 1 if mod == 1 else 0
            b = str(mod)+b
        return self.binStringMask.format(b), ones
    
    def createGroups(self):
        self.groups = [[] for i in range(self.n+1)]
        for one in self.ones:
            data = self.toBinString(one)
            self.groups[data[1]].append([[one], data[0], False])
        toRemove = []
        for i, group in enumerate(self.groups):
            if len(group) == 0: toRemove.append(i)
        for i in toRemove[::-1]:
            self.groups.pop(i)
    
    def comparePair(self, s1: str, s2: str) -> int:
        diff = 0
        idx = 0
        for i, c in enumerate(s1):
            if c == "-" and s2[i] != "-": return -1
            if c != s2[i]:
                diff += 1
                if diff > 1: return -1
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
                if idx == -1: continue
                p1[2] = True
                p2[2] = True
                mask = p1[1][:idx]+"-"+p1[1][idx+1:]
                elems = self.mergeSort(p1[0], p2[0], lvl)
                new = [elems, mask, False]
                if not new in merged: merged.append(new)
        return merged
    
    def merge(self) -> bool:
        newGroups = []
        created = 0
        for i in range(len(self.groups)-1):
            merged = self.mergeGroups(i, i+1)
            if len(merged) == 0: continue
            newGroups.append(merged)
            created += 1

        for group in self.groups:
            for elem in group:
                if elem[2] == False: self.results.append((elem[0], elem[1]))

        if created == 0: return False
        self.groups = newGroups
        return True

    


if __name__ == "__main__":
    QuineMcCluskey(ileZmiennych, jedynki)
    #QuineMcCluskey(3, [3,4,5,6,7])
    #QuineMcCluskey(5, [0, 1, 4, 5, 6, 10, 11, 12, 14, 16, 17, 18, 19, 20, 21, 22, 25, 26, 27, 28, 29, 30, 31])
    #QuineMcCluskey(6, [0, 1, 4, 5, 6, 10, 11, 12, 14, 16, 17, 18, 19, 20, 21, 22, 25, 26, 27, 28, 29, 30, 31, 40, 41, 44, 45, 46, 47, 48, 56, 57, 58, 59, 60, 61, 62, 63])