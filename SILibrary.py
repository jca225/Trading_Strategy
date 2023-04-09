  
#finds high points in prices
def hip_method(list1):
        list2 = [None] * len(list1)
        for i in range(len(list1)):
            if i == len(list1) - 1:
                continue
            if (list1[i] > list1[i-1] and list1[i] > list1[i+1]):
                list2[i] = list1[i]
                for j in range(1, (len(list1) - i)):
                    if i+j == len(list1) - 1:
                        continue
                    if (list1[i + j] > list1[i + j - 1] and list1[i + j] > list1[i + j + 1]):
                        #n = 0
                        break
                    else:
                        #n+=1
                        #print(n)
                        list2[i+j] = list1[i]
        return list2

#finds low points in prices
def lop_method(list1):
        list2 = [None] * len(list1)
        for i in range(len(list1)):
            if i == len(list1) - 1:
                continue
            if (list1[i] < list1[i - 1] and list1[i] < list1[i + 1]):
                list2[i] = list1[i]
                for j in range(1, (len(list1) - i)):  # 7,4
                    if i + j == len(list1) - 1:
                        continue
                    if (list1[i + j] < list1[i + j - 1] and list1[i + j] < list1[i + j + 1]):
                        # n = 0
                        break
                    else:
                        # n+=1
                        # print(n)
                        list2[i + j] = list1[i]
        return list2

# finds high swing point with respect to ASI (Accumulative Swing  Index)
def hsp_asi(df, list1):
        list2 = [None] * len(list1)

        for i in range(len(list1)):
            if i == len(list1) - 1:
                continue
            if (list1[i] > list1[i-1] and list1[i] > list1[i+1]):
                list2[i] = list1[i]
                for j in range(1, (len(list1) - i)):  #7,4
                    if i+j == len(list1) - 1:
                        continue
                    if (list1[i + j] > list1[i + j - 1] and list1[i + j] > list1[i + j + 1]):
                        #n = 0
                        break
                    else:
                        #n+=1
                        #print(n)
                        list2[i+j] = list1[i]
        return list2

 # finds high point with respect to swing index system
def hip_asi(df, list1, hsp):
        list2 = [None] * len(list1)
        for i in range(len(list1)):
            if i == len(list1) - 1:
                continue
            if (list1[i] > list1[i-1] and list1[i] > list1[i+1]):
                list2[i] = list1[i]
                for j in range(1, (len(list1) - i)):  #7,4
                    if i+j == len(list1) - 1:
                        continue
                    if (list1[i + j] > list1[i + j - 1] and list1[i + j] > list1[i + j + 1]):
                        #n = 0
                        break
                    else:
                        #n+=1
                        #print(n)
                        list2[i+j] = list1[i]
            if hsp[i] != hsp[i-1] and list1[i] == list1[i-1]:
                    if list1[i+1] != list1[i]:
                        list2[i] = list1[i+1]

        return list2

# finds low swing point with respect to ASI (Accumulative Swing Index)
def lsp_asi(df, list1):
        list2 = [None] * len(list1)
        for i in range(len(list1)):
            if i == len(list1) - 1:
                continue
            if (list1[i] < list1[i-1] and list1[i] < list1[i+1]):
                list2[i] = list1[i]
                for j in range(1, (len(list1) - i)):  #7,4
                    if i+j == len(list1) - 1:
                        continue
                    if (list1[i + j] < list1[i + j - 1] and list1[i + j] < list1[i + j + 1]):
                        #n = 0
                        break
                    else:
                        #n+=1
                        #print(n)
                        list2[i+j] = list1[i]
        return list2

# finds low point with respect to swing index system
def lop_asi(df, list1, lsp):
        list2 = [None] * len(list1)
        for i in range(len(list1)):
            if i == len(list1) - 1:
                continue
            if (list1[i] < list1[i - 1] and list1[i] < list1[i + 1]):
                list2[i] = list1[i]
                for j in range(1, (len(list1) - i)):  # 7,4
                    if i + j == len(list1) - 1:
                        continue
                    if (list1[i + j] < list1[i + j - 1] and list1[i + j] < list1[i + j + 1]):
                        # n = 0
                        break
                    else:
                        # n+=1
                        # print(n)
                        list2[i + j] = list1[i]
            if lsp[i] != lsp[i - 1] and list1[i] == list1[i - 1]:
                if list1[i + 1] != list1[i]:
                    list2[i] = list1[i + 1]
        return list2

# finds whether two data sets have crossed
def cross(over, under):
        if len(over) == len(under):
            for i in range(len(over)):
                if over[i-1] < under[i-1] and over[i] > under[i]:
                    return True
                else:
                    return False
        else:
            return 'Value error: Lengths of list are not identical.'
