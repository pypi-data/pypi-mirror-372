def all_subsequences(arr):
    ans = []
    n = len(arr)

    def subseq(i, l):
        if i == n:
            ans.append(l.copy())
            return
        l.append(arr[i])
        subseq(i+1, l)
        l.pop()
        subseq(i+1, l)

    subseq(0, [])
    return ans
