#keyUtils.py
#A part of NonVisual Desktop Access (NVDA)
#Copyright (C) 2006-2007 NVDA Contributors <http://www.nvda-project.org/>
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

import time
import globalVars
import winUser
import queueHandler
import wx
import vkCodes

def key(name):
	"""Converts a string representation of a keyPress in to a set of modifiers and a key (which is NVDA's internal key representation).
@param name: keyPress name to convert
@type name: string
@returns: the internal key representation 
"""
	name=name.lower()
	l = name.split("+")
	for num in range(len(l)):
		t=l[num]
		if len(t)>1:
			t="%s%s"%(t[0],t[1:])
		elif len(t)==1:
			t=t[0]
		l[num]=t
	if len(l) >= 2:
		s=set()
		for m in l[0:-1]:
			s.add(m)
		modifiers = frozenset(s)
	else:
		modifiers = None
	return (modifiers, l[-1])

def keyName(keyPress):
	"""Converts an internal key press to a printable name
@param keyPress: a keyPress
@type keyPress: key
"""
	keyName=""
	for k in list(keyPress[0] if isinstance(keyPress[0],frozenset) else [])+[keyPress[1]]:
		keyName+="+%s"%k
	return keyName[1:]

def sendKey(keyPress):
	"""Sends a key press through to the operating system.
@param keyPress: the key to send
@type keyPress: NVDA internal key
"""
	globalVars.log.info("%s"%keyName(keyPress))
	keyList=[]
	#Process modifier keys
	if keyPress[0] is not None:
		for modifier in keyPress[0]:
			if (modifier=="alt") and (winUser.getKeyState(winUser.VK_MENU)&32768):
				continue
			elif (modifier=="control") and (winUser.getKeyState(winUser.VK_CONTROL)&32768):
				continue
			elif (modifier=="shift") and (winUser.getKeyState(winUser.VK_SHIFT)&32768):
				continue
			elif (modifier=="win") and ((winUser.getKeyState(winUser.VK_LWIN)&32768) or (winUser.getKeyState(winUser.VK_RWIN)&32768)):
				continue
			elif (modifier=="insert") and insertDown:
				continue
			if modifier[0:8]=="extended":
				extended=1
				modifier=modifier[8:]
			else:
				extended=0
			if modifier=="alt":
				modifier="MENU"
			if modifier=="win":
				modifier="LWIN"
			keyID=vkCodes.byName[modifier.upper()]
			keyList.append((keyID,extended))
	#Process normal key
	if keyPress[1] is not None:
		k=keyPress[1]
		if k[0:8]=="extended":
			extended=1
			k=k[8:]
		else:
			extended=0
		k=k.upper()
		if len(k)==1:
			keyID=ord(k)
		else:
			keyID=vkCodes.byName[k.upper()]
		keyList.append((keyID,extended))
	if (keyList is None) or (len(keyList)==0):
		return
	#Send key up for any keys that are already down
	for k in filter(lambda x: winUser.getKeyState(x[0])&32768,keyList):
		winUser.keybd_event(k[0],0,k[1]+2,0)
	#Send key down events for these keys
	for k in keyList:
		winUser.keybd_event(k[0],0,k[1],0)
	#Send key up events for the keys in reverse order
	keyList.reverse()
	for k in keyList:
		winUser.keybd_event(k[0],0,k[1]+2,0)
	if not isKeyWaiting():
		time.sleep(0.01)
		wx.Yield()

def isKeyWaiting():
	"""Determines whether a script key is waiting to be handled.
	@returns: C{True} if a script key is waiting to be handled, C{False} otherwise.
	@rtype: boolean
"""
	return queueHandler.isPendingItems(queueHandler.interactiveQueue)
