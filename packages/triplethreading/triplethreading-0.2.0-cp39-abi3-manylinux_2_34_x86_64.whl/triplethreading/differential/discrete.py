def diff(t, x):

    v = []

    #Check the length of array
    if(len(x) != len(t)):
        print("Arrays have different lengths")
        return

    for i in range((len(t) - 1)):
        if (t[i+1] - t[i]) != 0:
            v.append ((x[i+1] - x[i]) / (t[i+1] - t[i]))

    return v
