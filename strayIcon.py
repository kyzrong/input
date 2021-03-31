#coding:utf-8
from infi.systray import SysTrayIcon
import threading
import time

#pip install infi.systray
#https://github.com/Infinidat/infi.systray

# menu_options = (('Say Hello', "hello.ico", hello),
                # ('Do nothing', None, do_nothing),
                # ('A sub-menu', "submenu.ico", (('Say Hello to Simon', "simon.ico", simon),
                                               # ('Do nothing', None, do_nothing),
                                              # ))
               # )
			   

def changeChinese(sysTrayIcon):
    print("change to chinese.")
def changeEnglish(sysTrayIcon):
    print("change to english.")
def bye(sysTrayIcon):
    print('Bye, then.')

class icon:
	def __init__(self,imageIco,imageIco2,hoverText,menuOptions,quitOption=None):
		"""2021-03-30 21.22.53添加两个图标，使用update进行切换"""
		self.hoverText = hoverText
		self.imageIco = imageIco 
		self.imageIco2 = imageIco2
		self.menuOptions = menuOptions
		if quitOption == None:
			self.quitOption = self.bye
		else:
			self.quitOption = self.quitOption
			
		self.sysTrayIcon = SysTrayIcon(self.imageIco, hoverText, menuOptions, on_quit=self.quitOption, default_menu_index=0)
			
	def bye(self,sysTrayIcon):
		#print('bye.')
		pass
		
	def update(self,iconFile):
		self.sysTrayIcon.update(icon=iconFile)
	
	def toOn(self):
		self.update(self.imageIco)
	
	def toOff(self):
		self.update(self.imageIco2)
	
	def show(self):
		threading.Thread(target=self.sysTrayIcon.start,args=()).start()
		
	def shutdown(self):
		self.sysTrayIcon.shutdown()
		

menuToCN = (('Chinese', None, changeChinese),)
menuToEN = (('English', None, changeEnglish),)
				
# menu_options = (('Chinese', None, changeChinese),
				# ('English', None, changeEnglish),)
# sysTrayIcon = SysTrayIcon("on.ico", hover_text, menu_options, on_quit=bye, default_menu_index=0)
#sysTrayIcon.start()
# threading.Thread(target=sysTrayIcon.start,args=()).start()

# iconCN = icon('on.ico','blackberry',menuToEN)
# iconEN = icon('off.ico','blackberry',menuToCN)

def changeTo(into = 'CN'):
	if into == 'CN':
		iconEN.shutdown()
		iconCN.show()
	else:
		iconCN.shutdown()
		iconEN.show()
	
if __name__ == '__main__':
	while True:
		iconCN = icon('on.ico','blackberry',menuToEN)
		iconCN.show()
		print('#1')
		time.sleep(4)
		iconCN.update('off.ico')
		print('#2')
		time.sleep(4)
		changeTo('CN')
		time.sleep(4)
		changeTo('EN')
		time.sleep(4)