
import sys
from PIL import Image, ImageDraw
#pip install pillow
from datetime import datetime
from math import acos as acos, cos as cos
from math import exp as exp
import matplotlib.pyplot  as plt
import datetime
import pandas
import xlrd


def addpoint (x, y, timepoint):
    if timepoint >= starttime and (timepoint <= stoptime or stoptime < 0):
        if (x - central_x) ** 2 + (y - central_y) ** 2 <= r_central_zone ** 2:  
            patch_central.append((x, y, timepoint))


# ____________________________________________________________________________________________________________

xmax = 0  
ymax = 0
xmin = 0
ymin = 0




colorA = (255, 0, 0) 
#dcolorA = 20 

colorB = (0, 0, 127) 
dcolorB = (0, 0, 2)  
colorBase = (0, 0, 0) 
bgcolor = (50, 255, 50)
linecolor=(0,255,0)

settingsstr="\
10\n\
40\n\
,\n\
0 -1\n\
200\n\
Line #1: point radius, mm (positive integer; you could put several ones separated by space, and all would be done) \n\
Line #2: numebr of intersection colors (integer from1 to 254) \n\
Line #3: decimal pointer (. or ,)\n\
Line #4: start and stop time from analizing track part. If stop time <0, the track analizing to the ena point\n\
Line #5: central zone radius, mm (positive integer)"

try:
    filesettings = open("settings.txt", "r")
except:
    filesettings = open("settings.txt", "w")
    filesettings.write(settingsstr)
    filesettings.close()
    filesettings = open("settings.txt", "r")
    print("Could not read settings, use standart ones")

r_list=list()
part_list=list()
try:
    strng=filesettings.readline()
    for substr in strng.split(" "):
        r_list.append(int(substr))
    colorlvls=int(filesettings.readline())
    decimalseparator=filesettings.readline()[0]

    strng = filesettings.readline()
    starttime=int(strng.split(" ")[0])
    stoptime=int(strng.split(" ")[1])

    strng = filesettings.readline()
    r_central_zone=int(strng.split(" ")[0])

except:
    filesettings.close()
    filesettings = open("settings.txt", "w")
    filesettings.write(settingsstr)
    filesettings.close()
    r_list=[10]
    colorlvls=40
    decimalseparator=","
    starttime=0
    stoptime=-1
    r_central_zone=0
    print("wrong settings file, changed to standard one")

for r in r_list:
    if r<1:
        filesettings.close()
        filesettings = open("settings.txt", "w")
        filesettings.write(settingsstr)
        filesettings.close()
        r_list=[10]
        colorlvls=40
        decimalseparator=","
        starttime = 0
        stoptime = -1
        r_central_zone = 0
        print("Wrong r: "+str(r)+" in settings.txt, using standard one")


if (colorlvls<1 or colorlvls>254 or (decimalseparator != "." and decimalseparator != ",")):
    filesettings.close()
    filesettings = open("settings.txt", "w")
    filesettings.write(settingsstr)
    filesettings.close()
    r_list=[10]
    colorlvls=40
    decimalseparator=","
    starttime=0
    stoptime=-1
    r_central_zone=0
    print("wrong settings file, changed to standard one")

filesettings.close()

colorstep=int(255/colorlvls)

for r in r_list:

    S0=0.0 
    for rx in range(-r, r):
        for ry in range(-r, r):
            if rx * rx + ry * ry < r * r:
                S0 += 1

    try:
        filelog = open("log.csv", "r")
    except:
        filelog = open("log.csv", "w")
        filelog.write("File;Radius(mm);Track area(normalized to cickle area);Linearized track area(normalized to cickle area);areas ratio (linearized to standard ); track lenght(mm);")
        filelog.write("\r\n")
        filelog.close()


    # ____________________________________________________________________________________________________________
    patch_central=[] # Центральная зона, если задана

    nameA = sys.argv[1]

    try:
        namexls=nameA.split(".")[0] + ".xls"
        xls=pandas.read_excel(namexls) 

        corner_nw_x=int(xls["Unnamed: 1"][14])
        corner_nw_y=int(xls["Unnamed: 2"][14])
        corner_ne_x=int(xls["Unnamed: 1"][15])
        corner_ne_y=int(xls["Unnamed: 2"][15])
        corner_sw_x=int(xls["Unnamed: 1"][16])
        corner_sw_y=int(xls["Unnamed: 2"][16])
        corner_se_x=int(xls["Unnamed: 1"][17])
        corner_se_y=int(xls["Unnamed: 2"][17])
        central_y = int(xls["Unnamed: 1"][24]) 
        central_x = int(xls["Unnamed: 2"][24]) 

        xmin=min(corner_nw_x, corner_sw_x)
        xmax=max(corner_ne_x, corner_se_x)
        ymin=min(corner_nw_y, corner_ne_y)
        ymax=max(corner_sw_y, corner_se_y)

        central_x+=xmin
        central_y+=ymin

    except:
        print ("Could not open file: "+ namexls )
        exit(1)


    if nameA.split(".")[1]=="xls":
        xls = pandas.read_excel(nameA)  
        for column in range (1, 1000): 
            if xls["Unnamed: " + str(column)][1] == "POSITIONS":
                break

        try:
            for row in range(4, 1000000):
                timepoint = xls["Unnamed: "+str(column)][row]
                x = (xls["Unnamed: "+str(column+2)][row])
                y = (xls["Unnamed: "+str(column+3)][row])
                addpoint(x, y, timepoint)
        except:
            print ("XLS successfully read:", nameA)


    else:
        print ("Unknown file type:", nameA)
        exit (3)




    counted = 0
    img = Image.new('RGB', (xmax - xmin + 2 * r, ymax - ymin + 2 * r), colorBase)

    pathA=patch_central
    for i in range(0, len(pathA)):
        for rx in range(-r, r):
            for ry in range(-r, r):
                if rx * rx + ry * ry < r * r:
                    currentcolor = img.getpixel((pathA[i][0] + rx - xmin + r, pathA[i][1] + ry - ymin + r))
                    if currentcolor == colorBase:
                        img.putpixel((int(pathA[i][0] + rx - xmin + r), int(pathA[i][1] + ry - ymin + r)), colorA)
                    else:
                        tmp=list(currentcolor)
                        colorlvl=int(tmp[2]/colorstep)
                        if (colorlvl+1)<colorlvls: tmp[2]+=colorstep
                        else: tmp[2]=255
                        currentcolor=tuple(tmp)
                        img.putpixel((int(pathA[i][0] + rx - xmin + r), int(pathA[i][1] + ry - ymin + r)), currentcolor)


    allcolor = 0
    coloronce = 0
    colorstepcount=[0]*colorlvls
    for i in range(0, xmax - xmin + 2 * r):
        for j in range(0, ymax - ymin + 2 * r):
            currentcolor = img.getpixel((i, j))
            if currentcolor != colorBase:
                allcolor += 1
                if currentcolor == colorA:
                    coloronce += 1
                else:
                    if currentcolor[2]==255:
                        colorstepcount[-1]+=1
                    else:
                        colorstepcount[int(currentcolor[2]/colorstep)-1]+=1

    draw = ImageDraw.Draw(img)
    draw.circle((central_x-xmin+r, central_y-ymin+r), r_central_zone, fill=None, outline=linecolor)
    draw.line((corner_nw_x-xmin+r,corner_nw_y-ymin+r, corner_ne_x-xmin+r,corner_ne_y-ymin+r, corner_se_x-xmin+r,corner_se_y-ymin+r, corner_sw_x-xmin+r,corner_sw_y-ymin+r, corner_nw_x-xmin+r,corner_nw_y-ymin+r),fill=linecolor) 
    img.save(nameA.split(".")[0] + "_" + str(r) + ".png", "png")


    # ____________________________________________________________________________________________________________

    linelenght = 0
    linelenght_float = 0
    for i in range(1, len(pathA)):
        linelenght += int(((pathA[i][0]-pathA[i-1][0])**2 + (pathA[i][1]-pathA[i-1][1])**2 )**0.5)+1
        linelenght_float += ((pathA[i][0]-pathA[i-1][0])**2 + (pathA[i][1]-pathA[i-1][1])**2 )**0.5

    img = Image.new('RGB', (linelenght + 2 * r+5,  2 * r), colorBase)

    currX=r+1
    for i in range(0, len(pathA)):
        for rx in range(-r, r):
            for ry in range(-r, r):
                if rx * rx + ry * ry < r * r:
                    currentcolor = img.getpixel((currX + rx, ry + r))
                    if currentcolor == colorBase:
                        img.putpixel((currX + rx, ry + r), colorA)
                    else:
                        tmp=list(currentcolor)
                        colorlvl=int(tmp[2]/colorstep)
                        if (colorlvl+1)<colorlvls: tmp[2]+=colorstep
                        else: tmp[2]=255
                        currentcolor=tuple(tmp)
                        img.putpixel((currX +rx, ry + r), currentcolor)
        if i<len(pathA)-1: currX+=int(((pathA[i+1][0]-pathA[i][0])**2 + (pathA[i+1][1]-pathA[i][1])**2 )**0.5)+1



    allcolorline = 0
    coloronceline = 0
    colorstepcountline=[0]*colorlvls
    for i in range(0, linelenght + 2 * r+5):
        for j in range(0, 2 * r):
            currentcolor = img.getpixel((i, j))
            if currentcolor != colorBase:
                allcolorline += 1
                if currentcolor == colorA:
                    coloronceline += 1
                else:
                    if currentcolor[2]==255:
                        colorstepcountline[-1]+=1
                    else:
                        colorstepcountline[int(currentcolor[2]/colorstep)-1]+=1


    img.save(nameA.split(".")[0] + "_" + str(r) + "_line.png", "png")


    decimalseparatordefault=str(0.0)[1]

    filelog = open("log.csv", "a")
    if allcolor:

        filelog.write(nameA + "; " + str(r)+"; " + str(allcolor/S0).replace(decimalseparatordefault,decimalseparator) + "; " + str(allcolorline/S0).replace(decimalseparatordefault,decimalseparator) + "; "  + str(allcolorline/allcolor).replace(decimalseparatordefault,decimalseparator) +"; "+str(linelenght_float).replace(decimalseparatordefault,decimalseparator)+"; ")
        filelog.write("\n")
        part_list.append(allcolorline / allcolor)
        print(str(datetime.datetime.today()).split(".")[0], ":", r, " - OK.")
    else:
        filelog.write(nameA + "; " + "; No points;\n")
        print(str(datetime.datetime.today()).split(".")[0], ":", r, " - no points.")
    filelog.close()

