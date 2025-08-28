def greeting():
   return "Hello, I'm your first library!"


def add(a, b):
    '''
    :param a: цифра a
    :param b: цифра b
    :return a+b: сумма цифр a и b
    '''
    return a + b

def bubble():
    a = '''def bubble(lst):
    n = len(lst)
    for i in range(n):
        for j in range(n - i - 1):
            if lst[j]>lst[j+1]:
                lst[j], lst[j+1] = lst[j+1], lst[j]
    return lst'''
    return print('AXAXAXAXAXAXAXAXXAXA')

def cocktail():
    '''def cocktail(lst):
    n = len(lst)
    start = 0
    end = n - 1
    swapped = True
    while swapped:
        swapped = False
        for i in range(start, end):
            if lst[i]>lst[i+1]:
                lst[i],lst[i+1] = lst[i+1],lst[i]
                swapped = True
        if not swapped:
            break
        swapped = False
        end = end - 1
        for i in range(end-1,start-1,-1):
            if lst[i]>lst[i+1]:
                lst[i],lst[i+1] = lst[i+1],lst[i]
                swapped = True
        start = start + 1
    return lst'''
    return print('AXAXAXAXAXAXAXAXXAXA')


def comb():
    '''def comb(lst):
    gap = len(lst)
    swapped = True
    while gap > 1 or swapped:
        gap = max(1, int(gap/1.25))
        swapped = False
        for i in range(len(lst)-gap):
            j = i + gap
            if lst[i]>lst[j]:
                lst[i],lst[j] = lst[j],lst[i]
                swapped = True
    return lst'''
    return print('AXAXAXAXAXAXAXAXXAXA')


def selection():
    '''def selection(lst):
    n = len(lst)
    for i in range(n):
        min_idx = i
        for j in range(i+1,n):
            if lst[j]<lst[min_idx]:
                min_idx = j
        lst[i],lst[min_idx]=lst[min_idx],lst[i]
    return lst'''
    return print('AXAXAXAXAXAXAXAXXAXA')

def quick():
    '''def quick(lst):
    quick_help(lst,0,len(lst)-1)
    return lst

def quick_help(lst, first, last):
    if first<last:
        split = partition(lst,first,last)
        quick_help(lst,first,split-1)
        quick_help(lst,split+1,last)

def partition(lst,first,last):
    pivot = lst[first]
    left = first + 1
    right = last
    done = False

    while not done:
        while left <= right and lst[left] <= pivot:
            left += 1
        while lst[right] >= pivot and right >= left:
            right -= 1

        if right<left:
            done = True
        else:
            lst[left],lst[right] = lst[right],lst[left]

    lst[first],lst[right]=lst[right],lst[first]

    return right'''
    return print('AXAXAXAXAXAXAXAAXAXAXA')


def shall():
    '''def shell(lst):
    gap = len(lst)//2
    while gap > 0:
        for i in range(gap,len(lst)):
            temp = lst[i]
            j = i
            while j >= gap and lst[j - gap] > temp:
                lst[j] = lst[j-gap]
                j -= gap
            lst[j] = temp
        gap //= 2
    return lst'''
    return print('maximka')

def merge():
    '''def sort(left,right):
    ans = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i]<=right[j]:
            ans.append(left[i])
            i += 1
        else:
            ans.append(right[j])
            j += 1

    ans += left[i:]
    ans += right[j:]

    return ans

def merge(lst):
    if len(lst)<=1:
        return lst

    mid = len(lst)//2
    left = merge(lst[:mid])
    right = merge(lst[mid:])

    return sort(left,right)'''
    return print('alooooooooo')


def insertion():
    '''def insertion(lst):
    for i in range(1,len(lst)):
        key = lst[i]
        j = i - 1
        while j >= 0 and lst[j] > key:
            lst[j+1] = lst[j]
            j -= 1
        lst[j+1] = key
    return lst'''
    return print('чел это рофлс')

# dehadb.ke
def all():
    '''insertion
    merge
    shall
    quick
    selection
    bubble
    cocktail
    comb'''
    return print('гаврилен')
