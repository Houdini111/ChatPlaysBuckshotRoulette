import sys

topLeft = [int(sys.argv[1]), int(sys.argv[2])]
size = [int(sys.argv[3]), int(sys.argv[4])]

left = topLeft[0]
right = left + size[0]
top = 1440 - topLeft[1]
bottom = 1440 - top + size[1]

leftP = round(left/2560, 3)
rightP = round(right/2560, 3)
topP = round(top/1440, 3)
bottomP = round(bottom/1440, 3)

print(f"ITEM_ZONE_1 = Zone({leftP}, {rightP}, {topP}, {bottomP}) #{left} - {right} on 2560  and  {top} - {bottom} on 1440")

