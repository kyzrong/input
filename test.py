#coding:utf-8
#import keyboard
import pynput
import time,threading
import sys,string,os
sys.path.append('.')
from strayIcon import *
#from operator import itemgetter, attrgetter #排序
'''
空格如果有内容，直接输出第一个。
第五码是数字，则输出对应的内容。
"`",进行选词，选择格式：[1:格式2:桥式]

2020-08-20 10.17.21
优化了wordDict的索引，可以索引两个字母。搜索速度可以达到小0.001秒。
添加了pynput库，添加此库，可以在win7-32位下运行的兼容性。
重写了srf类的判断逻辑。同时添加超时清空输入。

2020-08-28 09.01.09
对wordDict添加try，

2020-10-13 10.45.18
取消字符后面输入数字直接选择的功能。
索引数量加至4个字符。
'''
#print(keyboard.all_modifiers)
#{'alt', 'ctrl', 'right shift', 'right alt', 'right windows', 'left shift', 'right ctrl', 'alt gr', 'windows', 'left ctrl', 'shift', 'left windows', 'left alt'}
#print(keyboard.is_modifier('ifconfig'))
#print(keyboard.key_to_scan_codes('1'))

#返回对应的热键扫描码。
#print(keyboard.parse_hotkey("alt+shift+a, alt+b, c"))

# def myPrint(c):
	# print('#device:',c.device) #未知。
	# print('#event_type:',c.event_type) #up or down
	# print('#is_keypad:',c.is_keypad) #False，未知。
	# print('#modifiers:',c.modifiers) #None 未知。
	# print('#name:',c.name) #真实的输入。
	# print('#scan_code:',c.scan_code) #扫描码。
	# print('#time',c.time) #当前时间。
	# print('#############################')ifconfigifconfigsloeooeifisdfasdfasdfadsfasdfasdfad

#keyboard.hook(myPrint)

class srf:
	def __init__(self):
		self.w = wordDict()
		#self.kb = theKeyboard()
		self.kb = thePynput()
		self.kb.hotKey('right shift',self.changeSwitchFlag)
		
		self.inputString = ''
		self.wordList = None #返回字典返回的结果。
		self.switchFlag = False #输入开关
		self.digitMode = False
		
		self.menu = (('黑莓', None, changeChinese),)
		self.icon = iconCN = icon('on.ico','off.ico','blackberry',self.menu)
		self.icon.show()

		#这里缺失一个字符，就是1左边的那边，用来提示选择。
		self.enMark = ['!','-@','-#','-$','-%','-^','-&','-*','(',')','-_','-+','-{','-}','-|',':','"','-<','->','?','--','-=','-[','-]','\\',';','\'',',','.','-/']
		self.cnMark = ['！','@','#','￥','%','……','&','*','（','）','——','+','{','}','|','：','”','《','》','？','-','=','【','】','、','；','‘','，','。','/']
		self.initChoiseMode()
		threading.Thread(target=self.getChar,args=()).start()
		threading.Thread(target=self.timeoutClean,args=()).start() #超时清除。
		self.changeSwitchFlag()
		print('End of srf __init__.')
		
	def initChoiseMode(self):
		self.choiseMode = False #选择模式开关，
		self.choiseString = '' #类型为list，list内为string，显示给用户信息。
		self.choiseList = '' #类型为list，list为内list，用户最终选择。
		self.choisePage = 0 #当前选择页面。
		self.curChoiseLen = 0 #当前输出长度，输出时，更新此值，用于翻页时退格。
		
	def getChar(self):
		while True:
			curChat = self.kb.getOne()
			if curChat == '':
				time.sleep(0.01)
				continue
				
			if self.switchFlag == False: #非输入模式
				continue
			
			#print('#:',curChat)

			if curChat in [None,'Tab','shift','left shift','right shift',\
						   'alt','left alt','right alt',\
						   'ctrl', 'left ctrl', 'right ctrl',\
						   'windows','left windows', 'right windows',\
						   'enter','delete','insert','home','end'
						   ]:
				#print('#modifiers:',c.name)
				self.cleanInput()
				continue

			if self.choiseMode == True:
				# print('===in choise mode===')
				if curChat not in '-=' and self.ifMark(curChat):
					self.disPrintChoise()
					self.output(1)
					self.printMark(curChat)
					self.initChoiseMode()
					self.cleanInput()
					continue

				if curChat.isdigit():
					self.kb.backspace(1)
					self.disPrintChoise()
					self.output(int(curChat))
					self.initChoiseMode()
					continue

				if curChat in '-=':
					time.sleep(0.04)
					self.kb.backspace(1)
					if len(self.choiseList) <= 1:
						self.kb.printInfo('-Ns-')
						continue

					if curChat == '-' and self.choisePage == 0:
						self.choisePage = len(self.choiseList) - 1 #第一页再前，转成最后一个。
					elif curChat == '-' and self.choisePage > 0:
						self.choisePage = self.choisePage -1
					elif curChat == '=' and self.choisePage == len(self.choiseList) - 1:  #最后一个再加，转成第一页
						self.choisePage = 0
					elif curChat == '=' and self.choisePage < len(self.choiseList):
						self.choisePage = self.choisePage + 1

					print('==================')
					self.disPrintChoise()
					self.printChoise()
					continue

				if curChat == 'space':
					# if len(self.inputString) == 0:
					# 	continue
					self.kb.backspace(1)
					self.disPrintChoise()
					self.output(1)
					self.initChoiseMode()
					continue

				if curChat == 'backspace':
					self.kb.backspace(self.curChoiseLen - 1) #这里backspace已经删除了一个。
					self.kb.write(self.inputString)
					self.initChoiseMode()
					continue

				#这里跟space效果是一样的，都是自动选择第一个。
				if curChat == '`':
					self.kb.backspace(1)
					self.disPrintChoise()
					self.output(1)
					self.initChoiseMode()
					continue

				#这里跟space效果是一样的，都是自动选择第一个。
				if self.lowLetter(curChat):
					self.kb.backspace(1)
					self.disPrintChoise()
					self.output(1)
					self.initChoiseMode()
					continue

			#==================================================
			elif self.choiseMode == False:
				# print('===notin choise mode===')
				if curChat in '-=':
					self.digitMode = True
					self.cleanInput()
					continue

				if self.ifMark(curChat):
					self.printMark(curChat)
					self.cleanInput()
					continue

				self.digitMode = False

				if curChat == 'space':
					if len(self.inputString) == 0:
						continue

					if self.myCmd() == True:
						self.cleanInput()
						continue

					curSelect = 1
					plus = 0
					print('inputString:',self.inputString)
					if self.inputString[-1].isdigit():
						curSelect = int(self.inputString[-1])
						self.inputString = self.inputString[0:-1]
						plus = 1

					self.getChoise(True)
					# print('#choiseList:',self.choiseList)

					if self.choiseMode == False:
						self.cleanInput()
						continue

					# 第一页有多少个选择。
					choiseListLen = len(self.choiseList[0])

					# 在选择范围内，则输出对应的选择项。
					# 否则，退回输入项，不作任何操作，保留选择模式。
					print('curSelect:',curSelect)
					print('choiseListLen:',choiseListLen)
					if curSelect != 0 and curSelect <= choiseListLen:
						self.kb.backspace(1) #退回空格
						self.kb.backspace(len(self.inputString) + plus) #数字加已经输入的
						self.output(curSelect)
						self.cleanInput()
						self.initChoiseMode()
					else:
						self.kb.backspace(1)

					continue

				if curChat == 'backspace':
					self.inputString = self.inputString[0:-1]
					continue

				if curChat == '`':
					if len(self.inputString) == 0:
						continue

					self.kb.backspace(1)
					self.initChoiseMode()
					self.getChoise()

					if self.choiseMode == False:
						self.kb.printInfo('-NC-')
						self.initChoiseMode()
						continue

					self.kb.backspace(len(self.inputString))
					self.printChoise()
					continue

				if self.lowLetter(curChat):
					self.inputString = self.inputString + curChat
					print('#inputString:', self.inputString)
					self.digitMode = True #添加这个，如果之前输入不是中文，则后续输出字符为英文字符。
					continue

				if curChat.isdigit():
					self.digitMode = True
					#print('#<into digit mode.>')
					self.cleanInput()
					continue
	
	def myCmd(self):
		if self.inputString == 'time':
			self.kb.backspace(1)
			self.kb.backspace(len(self.inputString))
			self.kb.write(time.strftime("%Y-%m-%d %H.%M.%S", time.localtime()))
			return True
			
		if self.inputString == 'exitsrf':
			self.kb.backspace(1)
			self.kb.backspace(len(self.inputString))
			time.sleep(4)
			os._exit(1)
			return True
		return False
	
	def cleanInput(self):
		self.inputString = ''
		print('<clean input.>')
	
	#curSelect以1开始，处理时要减1
	def output(self,curSelect):
		if curSelect - 1 > len(self.choiseList[self.choisePage]) : #如果选择不在范围内。
			return None
		self.kb.write(self.choiseList[self.choisePage][curSelect-1])
		#print('#>:',self.choiseList[self.choisePage][curSelect-1])
		self.cleanInput()
		return True
	
	#获取选择。
	def getChoise(self,oneFlag=False):
		print('inGetChoise:',self.inputString)
		self.choiseList,self.choiseString = self.w.getChoise(self.inputString,oneFlag)
		if len(self.choiseList) == 0:
			self.choiseMode = False
		else:
			self.choiseMode = True

	#打印选择
	def printChoise(self):
		self.printPage()
		#self.write(self.choiseString[self.choisePage])
		#self.curChoiseLen = len(self.choiseString[self.choisePage])

	def printPage(self):
		self.kb.write(self.choiseString[self.choisePage])
		self.curChoiseLen = len(self.choiseString[self.choisePage])
		#print('curChoiseLen:',self.curChoiseLen)
		#print('choisePage',self.choisePage)
	
	#退回打印选择。
	def disPrintChoise(self):
		self.kb.backspace(self.curChoiseLen)
		self.curChoiseLen = 0
	
	def lowLetter(self,c):
		try:
			if c in 'abcdefghijklmnopqrstuvwxyz':
				return True
			return False
		except Exception as e:
			return False
	
	def ifMark(self,c):
		return c in self.enMark
	
	def printMark(self,c):
		if self.digitMode == True: #数字后面直接英文符号。
			#print('#lenOf:',len(self.inputString))
			return None
			
		for i in range(len(self.enMark)):
			if c == self.enMark[i]:
				time.sleep(0.1) #这里要进行延时，否则backspace应该会发送失败。不知道为什么。
				self.kb.backspace(1)
				self.kb.write(self.cnMark[i])
				# if c in ['(','[','<','\'','"']: #输出成对的符号。
				# 	self.kb.write(self.cnMark[i+1])
				return True
		return False
					
	# def addAbbreviation(self):
		# for i in range(len(self.enMark)):
			# print('#',self.enMark[i],self.cnMark[i])
			# self.k.add_abbreviation(self.enMark[i],self.cnMark[i])
	
	def changeSwitchFlag(self):
		"""更改图标"""
		print('----change switchFlag----')
		if self.switchFlag == True:
			self.switchFlag = False
			print('-Off-')
			self.icon.toOff()
			#self.kb.printInfo('<')
		else:
			self.switchFlag = True
			self.icon.toOn()
			print('-On-')
			#self.kb.printInfo('L')
		self.cleanInput()

	def timeoutClean(self):
		while True:
			time.sleep(14)
			if len(self.inputString) == 0:
				continue

			tmpString = self.inputString
			time.sleep(14)
			if tmpString == self.inputString:
				self.cleanInput()

class theKeyboard:
	def __init__(self):
		self.bufferChat = []
		self.k = keyboard
		self.hook()
		threading.Thread(target=self.wait,args=()).start()
		print('End of theKeyboard __init__.')
	
	def getChar(self,c):		
		if c.event_type != 'down':
			return None
		#print('#:',c.name)
		self.bufferChat.append(c.name)
	
	#这里不应该有cleanInput的方法的，这里是原始的输入。
	#应该由srf类清空自己所缓存的内容。
	# def cleanInput(self):
		# print('<clean input.>')
		# del self.bufferChat[:]
	
	def onRelease(self):
		pass
	
	def getOne(self):
		if len(self.bufferChat) != 0:
			return self.bufferChat.pop(0)
		return ''
	
	def write(self,cn):
		self.stopBuffer = True
		self.k.write(cn)
		self.stopBuffer = False
		
	def backspace(self,n):
		for i in range(n):
			self.k.send('backspace')
		
	def hook(self):
		try:
			self.k.hook(self.getChar)
		except Exception as e:
			print('#error in theKeyboard hook:',e)
	
	def wait(self):
		self.k.wait()
		
	def hotKey(self,theHotKey,theFun):
		self.k.add_hotkey(theHotKey,theFun)
	
	def testHotKey(self):
		print('active hot key.')
		
	def printInfo(self,info):
		self.write(info)
		time.sleep(0.4)
		self.backspace(len(info))

class theKeyboardLinux:
	def __init__(self):
		self.bufferChat = []
		self.sendBuffer = 0 #自身发送后，缓存。
		self.k = keyboard
		self.stopBuffer = 0 #在输出时，linux下，这个库会自己捉自己发出去的包。所以这个在自己发包时，停止记录输入。
		self.hook()
		threading.Thread(target=self.wait,args=()).start()
		print('End of theKeyboard __init__.')
	
	def getChar(self,c):
		if c.event_type != 'down':
			return None
		
		print('#:',c.name,self.bufferChat)
		
		if self.sendBuffer != 0:
			self.sendBuffer = self.sendBuffer - 1
			print('------:',self.sendBuffer)
			return None
					
		# if self.stopBuffer != 0:
			# self.stopBuffer = self.stopBuffer - 1
			# print('stopBuffer-1:',self.stopBuffer)
			# return None
			
		#print('#:',c.name)
		self.bufferChat.append(c.name)
	
	#这里不应该有cleanInput的方法的，这里是原始的输入。
	#应该由srf类清空自己所缓存的内容。
	# def cleanInput(self):
		# print('<clean input.>')
		# del self.bufferChat[:]
	
	def onRelease(self):
		pass
	
	def getOne(self):
		if len(self.bufferChat) != 0:
			return self.bufferChat.pop(0)
		return ''
	
	def write(self,cn):
		self.k.write(cn)
		#if cn not in ['ctrl','shift']:
		self.sendBuffer = self.sendBuffer + 1
		print('++++++:',cn,self.sendBuffer)
		
	def backspace(self,n):
		for i in range(n):
			self.k.send('backspace')
		
	def hook(self):
		try:
			self.h = self.k.hook(self.getChar)
		except Exception as e:
			print('#error in theKeyboard hook:',e)
			
	def unHook(self):
		try:
			self.k.unhook(self.h)
		except Exception as e:
			print('#error in keyboard linux unhook:',e)
	
	def wait(self):
		self.k.wait()
		
	def hotKey(self,theHotKey,theFun):
		self.k.add_hotkey(theHotKey,theFun)
	
	def testHotKey(self):
		print('active hot key.')
		
	def printInfo(self,info):
		self.write(info)
		time.sleep(0.4)
		self.backspace(len(info))

class thePynput:
	def __init__(self):
		self.bufferChat = []
		self.theHotKey = '' #hot key,手动判断
		self.theFun = None #手动执行回调函数
		self.stopBuffer = False #在输出时，这个库会自己捉自己发出去的包。所以这个在自己发包时，停止记录输入。
		self.k = pynput.keyboard.Controller()
		threading.Thread(target=self.hook,args=()).start()
		print('End of thePynput __init__.')
	
	def getChar(self,c):
		if self.stopBuffer == True:
			return None

		try:
			curChat = str(c.char)
		except AttributeError:
			curChat = str(c).split('.')[1]
		
		#特殊字符处理，处理成与keyboard库所描述的一样。
		if len(curChat) != 1 and curChat.find('_') != -1:
			keyName = curChat.split('_')[0]
			lr = curChat.split('_')[1]
			if lr == 'r':
				curChat = 'right '+keyName
			elif lr == 'l':
				curChat = 'left '+keyName
		
		#手动执行热键。
		if curChat == self.theHotKey:
			self.startHkThread()
			return None
		
		self.bufferChat.append(curChat)
		print('>:',curChat)
		#print('>>:',self.bufferChat)
	
	#这个方法没用。
	def onRelease(self,c):
		pass

	#获一个键盘输入字符。
	def getOne(self):
		if len(self.bufferChat) != 0:
			return self.bufferChat.pop(0)
		return ''
	
	def write(self,cn):
		"""写文字，在写之前，要停止捕捉，否则会捕捉到自己的输出。"""
		self.stopBuffer = True
		self.k.type(cn)
		self.stopBuffer = False
	
	def backspace(self,n):
		for i in range(n):
			self.write([pynput.keyboard.Key.backspace])
		
	def hook(self):
		"""键盘捕捉"""
		with pynput.keyboard.Listener(on_press=self.getChar,on_release=self.onRelease) as self.listener:
			self.listener.join()
			print('End of the listener join.')
	
	def hotKey(self,theHotKey,theFun):
		self.theHotKey = theHotKey
		self.theFun = theFun
		# self.hk = pynput.keyboard.GlobalHotKeys({theHotKey:theFun})
		# self.hk.start()
		# return None
	
		# self.h = threading.Thread(target=self.hkThread,args=(theHotKey,theFun))
		# self.h.start()
		# print('here')
	
	def startHkThread(self):
		self.hkThread = threading.Thread(target=self.theFun,args=())
		self.hkThread.start()

	def testHotKey(self):
		print('active hot key.')
	
	def printInfo(self,info):
		self.write(info)
		time.sleep(0.4)
		self.backspace(len(info))

#字典，格式
'''
[
['a',['工']],
['staa',['格式','桥式']]
]

如果查询结果有多个选择项。
则返回格式如下：
[[4个中文选择项],
[4个中文选择项],
[4个中文选择项]]

[4个中文选择项字符串,4个中文选择项字符串,4个中文选择项字符串]

返回上述两个项后，则srf类进行处理。
'''
class wordDict:
	def __init__(self):
		self.fileName = ['myWord.txt','wubi86.txt','pinyin.txt']
		self.fileChangeTime = []
		self.enWord = [] #英文
		self.cnWord = [] #中文
		self.sedList = {} #索引
		self.initChangeTime() #文件修改时间
		self.readFile()
		threading.Thread(target=self.checkModify,args=()).start()
	
	#更新文件修改时间
	def initChangeTime(self):
		del self.fileChangeTime[:]
		for file in self.fileName:
			self.fileChangeTime.append(os.path.getmtime(file))
	
	#检测文件是否有修改过。
	def checkModify(self):
		while True:
			time.sleep(30)
			for i in range(len(self.fileName)):
				if os.path.getmtime(self.fileName[i]) != self.fileChangeTime[i]:
					print('file:',self.fileName[i],'have modify.Begin to reload.')
					self.readFile()
					self.initChangeTime()
					
	#简单的索引，索引前两个字母
	def initSed(self):
		self.sedList.clear()
		print('===开始简单索引===')
		startTime = time.time()
		for i in range(len(self.enWord)):
			for j in range(1,5): #索引4个字符
				if self.enWord[i][0:j] not in self.sedList.keys():
					self.sedList[self.enWord[i][0:j]] = i
			# if self.enWord[i][0] not in self.sedList.keys():
			# 	self.sedList[self.enWord[i][0]] = i
			# if self.enWord[i][0:2] not in self.sedList.keys():
			# 	self.sedList[self.enWord[i][0:2]] = i

		print('===简单索引完成===(耗时：',time.time()-startTime,')')
		# for key in self.sedList.keys():
		# 	print('#',key,self.sedList[key])
		# 	if key == 'ru':
		# 		print(self.cnWord[149048:149158])
		print('===索引长度：',len(self.sedList),'===')
		
	#获取开始的位置
	def getStartSed(self,en):
		try:
			return self.sedList[en[0:4]]
		except Exception as e:
			return len(self.enWord)
	
	#读文件数据到内存，然后进行排序。
	def readFile(self):
		tempResult = []
		del self.enWord[:]
		del self.cnWord[:]
		for oneFile in self.fileName:
			print('===开始加载：',oneFile,'===')
			startTime = time.time()
			f = open(oneFile,'r',encoding='utf-8')
			for line in f.readlines():
				line = line.replace('\r\n','')
				line = line.replace('\n','')
				en = line.split('=')[0]
				cn = line.split('=')[1]
				tempResult.append([en,cn])
			f.close()
		print('===读txt文件完成===(耗时：',time.time()-startTime,')')
		print('===开始排序===')
		 #以英文进行排序
		for line in sorted(tempResult,key=lambda s:s[0]):
			self.enWord.append(line[0])
			self.cnWord.append(line[1])
		print('===排序完成===')
		print('===总条目数：',len(self.enWord),'===')
		self.initSed()
		# for line in self.word[0:1]:
			# print(line)

	#查找中文，默认查找全部。只返回第一个。返回类型始终为list
	def getWord(self,en,oneFlag=False):
		resultList = self.getMatchList(en,oneFlag)
		if resultList == []:
			return []
		else:
			allResult = []
			tmp = []
			for oneList in resultList: 
				for i in oneList:
					tmp.append(self.cnWord[i])
				allResult.append(tmp)
				tmp = []
				
			# print('==in getWord===')
			# for line in allResult:
				# print(line)
			return allResult

		# for line in self.word:
		# 	if line[0] == en:
		# 		return line[1]
		# return ''
	
	#选择字符串，返回两个值，第一个是list内为list，第二个是list内为string
	def getChoise(self,en,oneFlag=False):
		choiseList = self.getWord(en,oneFlag)
		if choiseList == []:
			return [],[]
		
		result = []
		tmp = ''
		#print('###choiseList####')
		for line in choiseList:
			print(line)
		
		for line in choiseList:
			tmp = ''
			for i in range(len(line)):
				tmp = tmp + str(i+1) + line[i]
			result.append(tmp)
		return choiseList,result
				
		# for i in range(len(choiseList)):
			# tmp = tmp + str(i+1) + choiseList[i] #这里不能带冒号，否则会提示大写。
		# return '[' + tmp + ']'
		
	#选择选择的具体内容
	# def getIndex(self,en,index=1):
		# choiseList = self.getWord(en)
		# if choiseList != [] and len(choiseList) >= index:
			# return choiseList[index-1]
		# return ''

	#添加词组。如果没有，则直接添加，如果有，则失败。手动添加。
	#直接添加到文件头。
	# def addWord(self,theString):
		# en = theString.split('=')[0]
		# cn = theString.split('=')[1]
		# for one in self.word:
			# if one[0] == en and one[1] == cn:
				# return False
		# self.enWord.insert(0,en)
		# self.cnWord.insert(0,cn)
		# return self.saveToFile(theString)
		
	#将最新的内容保存在文件头。	
	# def saveToFile(self,theString):
		# try:
			# with open(self.fileName[0],'r+',encoding='utf-8') as f:
				# content = f.read()
				# f.seek(0,0)
				# f.write(theString)
				# f.write('\n')
				# f.write(content)
			# return True
		# except Exception as e:
			# print('Error in saveToFile:',e)
			# return False

	#多个选择时。
	#[[4个选择项],
	#[4个选择项]
	#]
	def getMatchList(self,en,oneFlag=False):
		result = [] #返回结果
		tmp = [] #四个为一组。
		findFlag = None #由于是sorted过的，搜索结果的序号是连续的，搜索到开始，再到匹配不成功，即表示搜索完成。
		startSed = self.getStartSed(en)
		for value,index in zip(self.enWord[startSed:],range(startSed,len(self.enWord))):
			if value.find(en) == 0 and len(value) - len(en) <= 2:
				#print('Find it.',index)
				findFlag = True
				tmp.append(index)
				if len(tmp) >= 4:
					result.append(tmp)
					if oneFlag == True:
						return result
					tmp = []
				if len(result) >= 10: #最多返回10页内容。
					return result
			elif findFlag == True:
				break
		if len(tmp) != 0:
			result.append(tmp)
		#print('getMatchList:',result)
		return result

#==========快速查找list的内容（精确查找）=====================
# def findIndex(varList,varSearch,start,end):
	# try:
		# curIndex = varList.index(varSearch,start,end)
		# return curIndex
	# except Exception as e:
		# return False

# def listFind(varList,varSearch,start=0,end=-1):
	# theIndex  = findIndex(varList,varSearch,start,end)
	# if theIndex == False:
		# return ''
	# else:
		# return str(theIndex)+':'+listFind(varList,varSearch,theIndex+1,end)

# def listIndex(varList,varSearch):
	# result = listFind(varList,varSearch)
	# if result == '':
		# return []
	# else:
		# intResult = []
		# for one in result[0:-1].split(':'):
			# intResult.append(int(one))
		# return intResult

def main():
	srf()
	print('End of main.')
	while True:
		time.sleep(1)
	
def testKb():
	kb = theKeyboardLinux()
	#kb = thePynput()
	#kb.hotKey('right shift',kb.testHotKey)
	# kb.hotKey('e',kb.testHotKey)
	while True:
		curChat = kb.getOne()
		if curChat != '':
			print(curChat)
			#print('bufferChat:',kb.bufferChat)
			kb.write('测试')
			continue
		#
		time.sleep(1)
		
def testWord():
	w = wordDict()
	time.sleep(1)
	for i in range(10):
		startTime = time.time()
		print(w.getChoise('ruv'))
		print('End:',time.time() - startTime)
		time.sleep(0.1)

if __name__ == '__main__':
	#testKb()
	#testWord()
	main()
	print('End of process.')
	#srf()

	