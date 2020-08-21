# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 19:47:21 2020

@author: SnowmanZhang

stay hungry,stay foolish
"""

import time



def GenGeneralBlockList(filepath):
    '''SOUTH模式，1.12，48色，其中XY皆正，从左下角开始计算 '''
    BlockList = [[0 for i in range(129)] for j in range(129)]
    with open(filepath,"r") as f:
        con = f.readlines()
    for u in con:
        if "~ ~ ~" in u:
            u = u.replace("~ ~ ~","~ ~0 ~")  #两个波浪号的是y,一个波浪号是x
        if "fill" in u:
            """进入区块填充模式"""
            s = u[u.find("fill")+4:u.find("minecraft:")]
            X1 = int(s.split("~ ~")[1].split("~")[1])
            Y1 = int(s.split("~ ~")[1].split("~")[0]) + 1 #注意这是1*2地图！！
            X2 = int(s.split("~ ~")[2].split("~")[1]) 
            Y2 = int(s.split("~ ~")[2].split("~")[0]) + 1
            name = u[u.find("minecraft:")+10:-1]
            #print(u,Y1,Y2)
            for i in range(min(X1,X2),max(X1,X2) + 1):
                for j in range(min(Y1,Y2),max(Y1,Y2) + 1):
                    BlockList[i][j] = name
        elif "setblock" in u:
            """进入方块放置模式"""
            s = u[:u.find("minecraft:")]
            X = int(s.split("~")[3])
            Y = int(s.split("~")[2]) + 1
            name = u[u.find("minecraft:")+10:-1]
            #print(X,Y)
            BlockList[X][Y] = name
    return BlockList

def TranslateMcfunction(filepath,startX,startY):
    '''该程序用于返回一个简陋的方块放置清单，即什么坐标放什么方块，startX startY均按左下角计算
    
    '''
    cmdlist = []
    colorarray = ['白色','橙色','品红','浅蓝','黄色','黄绿色','粉色','灰色',
                  '浅灰','青色','紫色','蓝色','棕色','绿色','红色','黑色'] 
    itemdict = {'concrete_powder':"粉末",'concrete':"混凝土",'stained_hardened_clay':"陶瓦"}
    with open(filepath,"r") as f:
        con = f.readlines()
    for u in con:
        nameraw = u[u.find("minecraft:")+10:-1]
        if " " not in nameraw:
            nameraw += " 0"
        color = " " + colorarray[int(nameraw.split(" ")[1])]
        name = color + itemdict[nameraw.split(" ")[0]] + nameraw.split(" ")[1]
        
        if "~ ~ ~" in u:
            u = u.replace("~ ~ ~","~ ~0 ~")  #两个波浪号的是y,一个波浪号是x
        if "fill" in u:
            """进入区块填充模式"""
            s = u[u.find("fill")+4:u.find("minecraft:")]
            X1 = int(s.split("~ ~")[1].split("~")[1])
            Y1 = int(s.split("~ ~")[1].split("~")[0]) + 1 #注意这是1*2地图！！
            X2 = int(s.split("~ ~")[2].split("~")[1]) 
            Y2 = int(s.split("~ ~")[2].split("~")[0]) + 1      
            cmdlist.append(f"从{X1 + startX},{-Y1 + startY} 到 {X2 + startX},{-Y2 + startY}，填充方块{name}")
        elif "setblock" in u:
            """进入方块放置模式"""
            s = u[:u.find("minecraft:")]
            X = int(s.split("~")[3])
            Y = int(s.split("~")[2]) + 1
            cmdlist.append(f"{X+startX},{-Y+startY}填充方块{name}")
    return cmdlist

def CheckRec(X1,Y1,X2,Y2,blockid):
    '''查看当前的矩形外环是否为单色'''
    if X1 <= 0 or X2 > 128 or Y1 <= 0 or Y2 > 128:
        return False
    for i in range(X1,X2+1):
        for j in range(Y1,Y2+1):
            if BlockList[i][j] != blockid:
                return False
    return True
    

def GetBlockName(X,Y):
    nameraw = BlockList[X][Y]  #给出方块名称
    colorarray = ['白色','橙色','品红','浅蓝','黄色','黄绿色','粉色','灰色',
                  '浅灰','青色','紫色','蓝色','棕色','绿色','红色','黑色'] 
    itemdict = {'concrete_powder':"粉末",'concrete':"混凝土",'stained_hardened_clay':"陶瓦"}
    if " " not in nameraw:
        nameraw += " 0"
    color = " " + colorarray[int(nameraw.split(" ")[1])]
    name = color + itemdict[nameraw.split(" ")[0]] + nameraw.split(" ")[1]
    return name

def GetRectangle(X,Y):
    '''给定传输坐标，求最大矩形'''
    global startX
    global startY
    X = X - startX
    Y = startY - Y  #因为Y本身小于startY,此时的XY才与blocklist对应
    X1 = X
    X2 = X
    Y1 = Y
    Y2 = Y
    up = True
    down = True
    left = True
    right = True
    blockid = BlockList[X][Y]
    while (up or down or left or right):
        #print(up,down,left,right)
        if up:
            if CheckRec(X1,Y2+1,X2,Y2+1,blockid):
                Y2 += 1
            else:
                up = False
        if down:
            if CheckRec(X1,Y1-1,X2,Y1-1,blockid):
                Y1 -= 1
            else:
                down = False
        if left:
            if CheckRec(X1-1,Y1,X1-1,Y2,blockid):
                X1 -= 1
            else:
                left = False
        if right:
            if CheckRec(X2+1,Y1,X2+1,Y2,blockid):
                X2 += 1
            else:
                right = False
    #print("test")
    name = GetBlockName(X,Y)
    return X1+startX,X2+startX,startY - Y1,startY - Y2,name,(Y2 - Y1 + 1)*(X2 - X1 + 1)


def itemseq(name):
    #函数返回该名称（如白色混凝土0）对应的项目序号
    colorarray = ['白色','橙色','品红','浅蓝','黄色','黄绿色','粉色','灰色',
                  '浅灰','青色','紫色','蓝色','棕色','绿色','红色','黑色']
    itemlist = ['粉末','混凝土','陶瓦']
    NUM = 0
    for color in colorarray:
        if color in name:
            NUM = colorarray.index(color) * 3
            break
    for item in itemlist:
        if item in name:
            NUM += itemlist.index(item)
    return NUM

def PrintRecBlockSpecial(X,Y,filepath):
    #该函数给出以上一个第一坐标点currentX,currentY和当前坐标点X.Y构成的矩形中
    #1. 九项物品的耗材清单（按使用数量多少排列）
    #2. 输出压缩编码（10个一组，标注起始坐标）
    global currentX
    global currentY
    Xmin = min(X,currentX) - startX
    Ymin = startY - max(Y,currentY)
    Xmax = max(X,currentX) - startX
    Ymax = startY - min(Y,currentY)
    itemdict = {}
    for x in range(Xmin,Xmax+1):
        for y in range(Ymin,Ymax+1):
            name = GetBlockName(x,y)
            if name in itemdict:
                itemdict[name] += 1
            else:
                itemdict[name] = 1
    itemlist = sorted(itemdict.items(), key=lambda d:d[1], reverse = True)
    ItemNumDict = {}
    s = "本次矩形清单列表为\n"
    sweety = "方块取用清单为\n"
    sweetylist = []
    n = 1
    for u in itemlist:
        s += u[0] + "  " + str(u[1]) + "\n"
        ItemNumDict[u[0]] = n
        n += 1
        sweetyunit = [u[0],itemseq(u[0]),int(u[1]/64) + 1]
        sweetylist.append(sweetyunit)
    l = sorted(sweetylist,key=lambda d:d[1],reverse = False)
    bakList = []
    for u in l:
        sweety += u[0] + "  " + str(u[2]) + "组\n" 
    for x in range(Xmin,Xmax+1):  #输出五个数字一单元的编码
        n = 1
        for y in range(Ymin,Ymax+1):
            name = GetBlockName(x,y)
            if n%10 == 1:
                s += str(x + startX) + "," + str(startY - y) + ": "
            if ItemNumDict[name] > 9:
                bakList.append((x,y))  #给出备用list清单
                s += "0"
            else:
                s += str(ItemNumDict[name])
            if n%5 == 0:
                s += " "
            if n%10 == 0:
                s += "\n"
            n += 1
        s += "\n\n"
    bakS = "本次清单二次方块列表为：\n"
    bakname = ""
    for u in bakList:
        name = GetBlockName(u[0],u[1])
        bakS += f"{u[0]+startX},{startY - u[1]}: {ItemNumDict[name] - 9} \n"
    try:
        with open(filepath,"w",encoding='utf8') as f:
            f.write(f"方块清单从{currentX},{currentY}到{X},{Y}，顺序自左向右，自下向上\n")
            f.write(sweety)
            f.write(s)
            f.write(bakS)
    except Exception as e:
        print(e)
    currentX = X
    currentY = Y
    
def PrintRecBlockNormal(X,Y,filepath):
    #该函数给出以上一个第一坐标点currentX,currentY和当前坐标点X.Y构成的矩形中
    #从左到右，从下到上的方块顺序
    global currentX
    global currentY
    Xmin = min(X,currentX) - startX
    Ymin = startY - max(Y,currentY)
    Xmax = max(X,currentX) - startX
    Ymax = startY - min(Y,currentY)
    s = ""
    for x in range(Xmin,Xmax+1):
        n = 1
        for y in range(Ymin,Ymax+1):
            name = GetBlockName(x,y)
            s += str(n) + " " + name+'\n'
            n += 1
    with open(filepath,"w",encoding='utf8') as f:
        f.write(f"方块清单从{currentX},{currentY}到{X},{Y}，顺序自左向右，自下向上\n")
        f.write(s)
    currentX = X
    currentY = Y


def Detect(log_file_path,filepath):
    '''不断监听文件，如果存在更新的坐标内容，就传入处理函数'''
    global currentX
    global currentY
    global startX
    global startY
    try:
        with open(log_file_path,"r",errors='ignore') as f:
            con = f.readlines()
        for i in range(len(con)-1,0,-1):
            if "第一个 选取点" in con[i]:
                X = con[i][con[i].find("X:")+2:con[i].find("Y")]
                Y = con[i][con[i].find("Z")+2:]
                #print(X,Y)
                if currentX != int(X) or currentY != int(Y):
                    print("发现第一个选取点,且与当前坐标不同")
                    #print(X,Y)
                    currentX = int(X)
                    currentY = int(Y)
                    X1,X2,Y1,Y2,name,size = GetRectangle(int(X),int(Y))
                    print(X1,X2,Y1,Y2,name,size)
                    with open(filepath,"w",encoding='utf8') as f:
                        print("同步中")
                        f.write(f"当前坐标为{currentX},{currentY}.方块从{X1},{Y1}到{X2},{Y2} \n即自左{currentX-X1}下{Y1-currentY}到右{X2-currentX}上{currentY-Y2} \n全部铺 {name} 面积为{size} \n")
                return 0
            elif "第二个 选取点" in con[i]:
                if currentX == 0:
                    return 0
                X = con[i][con[i].find("X:")+2:con[i].find("Y")]
                Y = con[i][con[i].find("Z")+2:]
                print(f"捕捉到第二个选取点 进行判断，当前current坐标为{currentX},{currentY},X与Y分别是{X},{Y}")
                if currentX != int(X) or currentY != int(Y):
                    PrintRecBlockSpecial(int(X),int(Y),filepath)   #开启矩形计算的复杂模式
                    #print(currentX,currentY)
                return 0
    except Exception as e:
        pass

def main(mcfunc_file_path,log_file_path,output_file_path,f_startX,f_startY):
    global currentX
    global currentY
    global startX
    global startY
    startX = f_startX - 1
    startY = f_startY + 1
    currentX = 0
    currentY = 0
    BlockList = GenGeneralBlockList(mcfunc_file_path)
    while True:
        Detect(log_file_path,output_file_path)
        time.sleep(1)

if __name__ == "__main__":
    '''
    使用限制：
    1. 本程序用于生成构图复杂的像素画清单
    2. 本程序目前只接受16色的混凝土粉末、混凝土、陶瓦，一共48种方块，其余方块放入会报错
    3. 本程序只支持128*128大小及以下的像素画，暂不接受更大规格的像素画，更大规格像素画请切分后载入
    4. 本程序仅在服务器中有小木棍圈地插件的情况下使用
    
    使用步骤：
    1. 使用https://minecraftart.netlify.app/editor 网站，生成自己需要的像素画（需要遵循以上三项限制）
    2. 选择`Convert to Commands`，在下方的配置项中，`spawn toward`选择为`South`,`Convert method`选择为`.mcfunction file`，下载该文件
    3. 将该文件路径作为main函数的第一个参数，第二个参数是游戏所产生的日志文件，第三个参数是将要生成的指令文件路径。第4、5个参数分别是像素画最西南角的那个格子的X、Z值
    4. 运行程序后，切回到游戏中，在像素画区域的某点使用小木棍左键单击一个方块，这个圈地信息会被日志文件记录下来，在确认指令文件更新了这个消息后（一般5-10秒），使用木棍右键单击另一个方块，此时构成了一个矩形，程序会给出这个矩形内的方块清单信息。

    结果分析：
    1. 指令文件分为三个部分，第一部分会给出本像素画需要的所有物品的清单，遵循`物品名:需要的数量`这个模式，第二部分是一次指令行，例如
        28302,43634: 11132 2
        表示的是，方块从坐标28302，43634开始向北铺，这6个方块的物品栏编号分别为11132 2
        第三部分是如果这次的矩形超过了9种颜色方块，第一次指令行的相关位置会显示为0，这些超出的方块会在第二次指令中以 X,Y: 编号 的形式给出，例如
        28302,43635: 3
        表示的是该坐标下放置一个清单中的第12格方块（前9种方块在第一次指令行时已经铺完，第12种方块序号也就变成了3）
    2. 事实上，在实际使用中，物品栏编号也就是游戏中的9格物品栏，例如编号1的方块放在最左边的物品栏位上，这样的话，铺起来只需要来回滚动鼠标滚轮，就能快速换方块了
    3. 请不要一次性圈太大的地方，这样会使得颜色过于丰富，第二次指令行的内容过多，铺方块的效率降低.
    '''
    main(r"pixel/鹡鸰.mcfunction","NetEase/today.log",r"tmpupload/指令.txt",28292,43681)
        

