# Build each row of the columnData array for a basic Report table
def makeReportColumnData(cols, colHeaders):
    columnData = []
    firstTrue = True
    i = 0
    for name in cols:
        toAdd = {"id": name, "numeric" : "false", "disablePadding" : firstTrue, "label" : colHeaders[i]}
        columnData.append(toAdd)
        firstTrue = False
        i += 1
    return columnData