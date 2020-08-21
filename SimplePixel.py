# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 16:47:17 2020

@author: SnowmanZhang

stay hungry,stay foolish
"""
def GenGeneralBlockList(filepath):
	'''SOUTH模式，1.12，48色，其中XY皆正，从左下角开始计算 '''
	BlockList = [[0 for i in range(129)] for j in range(129)]
	with open(filepath,"r") as f:
		con = f.readlines()
	colorarray = ['白色','橙色','品红','浅蓝','黄色','黄绿色','粉色','灰色',
				  '浅灰','青色','紫色','蓝色','棕色','绿色','红色','黑色'] 
	itemdict = {'concrete_powder':"粉末",'concrete':"混凝土",'stained_hardened_clay':"陶瓦"}
	for u in con:
		if "~ ~ ~" in u:
			u = u.replace("~ ~ ~","~ ~0 ~")  #两个波浪号的是y,一个波浪号是x
		nameraw = u[u.find("minecraft:")+10:-1]
		if " " not in nameraw:
			nameraw += " 0"
		color = " " + colorarray[int(nameraw.split(" ")[1])]
		name = color + itemdict[nameraw.split(" ")[0]] + nameraw.split(" ")[1]
		if "fill" in u:
			"""进入区块填充模式"""
			s = u[u.find("fill")+4:u.find("minecraft:")]
			X1 = int(s.split("~ ~")[1].split("~")[1])
			Y1 = int(s.split("~ ~")[1].split("~")[0]) + 1 
			X2 = int(s.split("~ ~")[2].split("~")[1]) 
			Y2 = int(s.split("~ ~")[2].split("~")[0]) + 1
			#print(u,Y1,Y2)
			for i in range(min(X1,X2),max(X1,X2) + 1):
				for j in range(min(Y1,Y2),max(Y1,Y2) + 1):
					BlockList[i][j] = name
		elif "setblock" in u:
			"""进入方块放置模式"""
			s = u[:u.find("minecraft:")]
			X = int(s.split("~")[3])
			Y = int(s.split("~")[2]) + 1
			BlockList[X][Y] = name
	return BlockList


def FindStartPoint(BlockList,x = None,starty = 1,endy = 128):
	'''找到最左侧最下侧的点'''
	if x is None:
		'''全局查找'''
		for x in range(1,128):
			for y in range(1,128):
				if BlockList[x][y] != " 白色粉末0":
					#print(x,y)
					return x,y
		return 129,0
	else:
		'''局部查找'''
		for y in range(starty,endy+1):
			if BlockList[x + 1][y] != " 白色粉末0":
				y = y - 1
				while BlockList[x + 1][y] != " 白色粉末0":
					y = y - 1
				return x + 1,y + 1
		return None,None


def ReturnItemdict(BlockList):
	'''返回物品列表（小于18种）'''
	itemdict = {}
	for x in range(1,128):
		for y in range(1,128):
			if BlockList[x][y] not in itemdict:
				itemdict[BlockList[x][y]] = 1
			else:
				itemdict[BlockList[x][y]] += 1
	itemlist = sorted(itemdict.items(), key=lambda d:d[1], reverse = True)
	return itemdict,{u[0]:itemlist.index(u) for u in itemlist}
		


def ExecuteSinglePath(BlockList,itemdict,ItemNumDict):
	'''给定一个起始的坐标，输出单次路径清单'''
	global startX
	global startY
	x,y = FindStartPoint(BlockList)
	lastY = y
	s = "清单列表如下：\n"
	for u in itemdict:
		s += u + ":" + str(itemdict[u]) + ":" + str(ItemNumDict[u])  + "\n"

	while BlockList[x][y] != " 白色粉末0":
		ss = f"\n**{x + startX},{startY - y}({lastY - y})**"
		lastY = y
		n = 1
		tmps = ""
		while BlockList[x][y] != " 白色粉末0":
			tmps += str(itemdict[BlockList[x][y]])
			if n%5 == 0:
				tmps += " "
			n += 1
			BlockList[x][y] = " 白色粉末0"
			y += 1
		ss += f"本轮到 **{startY - y + 1}** 结束。\n" #一列结束后换行
		s += ss + tmps
		x,y = FindStartPoint(BlockList,x,lastY,y-1)
		if x is None:
			x,y = FindStartPoint(BlockList)
		if x > 128:
			return s
	return s


def main(mcfunc_file_path,output_file_path,f_startX,f_startY):
	global startX
	global startY
	startX = f_startX - 1
	startY = f_startY + 1
	currentX = 0
	currentY = 0
	BlockList = GenGeneralBlockList(mcfunc_file_path)
	ItemNumDict,itemdict = ReturnItemdict(BlockList)
	s = ExecuteSinglePath(BlockList,itemdict,ItemNumDict)
	with open(output_file_path,"w",encoding="utf8") as f:
		f.write(s)

if __name__ == "__main__":
	'''
	使用限制：
	1. 本程序用于生成构图简单的像素画清单（物品一共不超过9种，如果多了程序不会报错，但是体验不佳）
	2. 本程序目前只接受16色的混凝土粉末、混凝土、陶瓦，一共48种方块，其余方块放入会报错
	3. 本程序只支持128*128大小的像素画，暂不接受其余规格的像素画
	
	使用步骤：
	1. 使用https://minecraftart.netlify.app/editor 网站，生成自己需要的像素画（需要遵循以上三项限制）
	2. 选择`Convert to Commands`，在下方的配置项中，`spawn toward`选择为`South`,`Convert method`选择为`.mcfunction file`，下载该文件
	3. 将该文件路径作为main函数的第一个参数，第二个参数是要生成的指令文件。第3、4个参数分别是像素画最西南角的那个格子的X、Z值

	结果分析：
	1. 指令文件分为两个部分，第一部分会给出本像素画需要的所有物品的清单，遵循`物品名:物品栏编号:需要的数量`这个模式，第二部分是指令行，例如
			**885,8029(3)**本轮到 **8019** 结束。
			53821 11111 7
		表示的是，方块从坐标885，8029开始（较上一指令行的起始Y值大了3）向北铺，一直铺到885,8019结束，这11个方块的物品栏编号分别为53821 11111 7
	2. 事实上，在实际使用中，物品栏编号也就是游戏中的9格物品栏，例如编号1的方块放在最左边的物品栏位上，这样的话，铺起来只需要来回滚动鼠标滚轮，就能快速换方块了
	'''
	global startX
	global startY
	main(r"pixel/b.mcfunction","指示.txt",f_startX = -217920,f_startY = -217921)

