fileHandle = open ( 'output.txt',"r" )
lineList = fileHandle.readlines()
fileHandle.close()


result = lineList[-1]

fileHandle = open ( 'result.txt',"r" )
lineList = fileHandle.readlines()
fileHandle.close()

upper_wins = int(lineList[0].split(',')[1])
draws = int(lineList[1].split(',')[1])
lower_wins = int(lineList[2].split(',')[1])

print(result)
if "* winner: upper" in result:
    upper_wins += 1
elif "* winner: lower" in result:
    lower_wins += 1
elif "draw" in result:
    draws += 1
else:
    print("ERROR")

f = open ( 'result.txt',"w" )
f.write("upper_wins," + str(upper_wins)+"\n")
f.write("draws," + str(draws)+"\n")
f.write("lower_wins," + str(lower_wins)+"\n")
f.close()

