#################################################
# CtD_Classes.py:
#
# File containing all the class definitions of
# game objects including game math functions
#
# Your name: Mitchell Foo
# Your andrew id: mfoo
#################################################

import math
import copy
import random
import numpy as np

from cmu_112_graphics import *
from CtD_Pathfinding import *

### Helper Functions
def dist2Points(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def rotatePoint(ox, oy, px, py, r):
	# Referenced code from:
	# https://stackoverflow.com/questions/34372480/rotate-point-about-another-point-in-degrees-python
    qx = ox + math.cos(r) * (px - ox) - math.sin(r) * (py - oy)
    qy = oy + math.sin(r) * (px - ox) + math.cos(r) * (py - oy)
    return qx, qy

def rotateVertices(v, w, h, r):
	retV = []
	for point in v:
		ox, oy = point
		rPoint = rotatePoint(w, h, ox, oy, r)
		retV.append(rPoint)
	return retV

def angle2Vectors(mouseX, mouseY):
	# Referenced code from:
	# https://www.kite.com/python/answers/how-to-get-the-angle-between-two-vectors-in-python
	playerX, playerY = 0, -1

	v1 = [playerX, playerY]
	v2 = [mouseX, mouseY]
	v1 /= np.linalg.norm(v1)
	v2 /= np.linalg.norm(v2)

	dp = np.dot(v1, v2)
	angle = np.arccos(dp)

	return angle

def vector2Points(mouseX, mouseY, playerX, playerY, norm=True):
	vX = mouseX - playerX
	vY = mouseY - playerY
	
	v = [vX, vY]
	if norm:
		v /= np.linalg.norm(v)

	return v[0],v[1]

def checkCollision(x1, y1, r1, x2, y2, r2):
	# Referenced code from:
	# https://developer.mozilla.org/en-US/docs/Games/Techniques/2D_collision_detection
	x1 -= r1
	x2 -= r2
	y1 -= r1
	y2 -= r2
	r1 *= 2
	r2 *= 2

	if (x1 < x2 + r2 and
		x1 + r1 > x2 and
		y1 < y2 + r2 and
		y1 + r1 > y2):
		return True
	return False

### Classes

class Agent(object):
	def __init__(self, scale, aX, aY, aR, health):
		self.scale = scale
		self.aX = aX
		self.aY = aY
		self.aR = aR
		self.health = health

	def getPos(self):
		return self.aX, self.aY

	def getBounds(self, app):
		mX, mY = app.player.getPos()

		x = self.aX - mX + self.scale*3
		y = self.aY - mY + self.scale*3
		r = self.aR

		return x, y, r

	def drawBounds(self, app, canvas):
		if app.viewBounds:
			x,y,r = self.getBounds(app)
			canvas.create_rectangle(x-r,y-r,x+r,y+r, fill="", outline='red', width=2)

	def getCell(self):
		row = int(self.aY//self.scale + 1)
		col = int(self.aX//self.scale + 1)
		return (row, col)

	def getSize(self):
		return self.aR

	def move(self, mX, mY):
		self.aX += mX
		self.aY += mY

	def takeDamage(self):
		self.health -= 1

	def checkAlive(self):
		return self.health

	def handleObjectCollision(self, app, items):
		for i in items:
			aR = self.aR * 1.2
			aX, aY, aR = self.getBounds(app)
			wX, wY, wR = i.getBounds(app)
			if checkCollision(aX, aY, aR, wX, wY, wR):
				if type(i) == DestructibleWall and type(self) == Bullet:
					i.takeDamage()
				elif type(i) == Zombie and type(self) == Bullet:
					i.takeDamage()
					i.setDamaged()
				elif type(i) == Sniper and type(self) == Bullet:
					i.takeDamage()
					i.setDamaged()
				elif type(i) == Player and type(self) == SniperBullet:
					i.takeDamage()
				elif type(i) == HealthUp and type(self) == Player:
					i.healUpPlayer(app)
				elif type(i) == AmmoUp and type(self) == Player:
					i.ammoUpPlayer(app)
				elif type(i) == ScoreUp and type(self) == Player:
					i.scoreUpPlayer(app)

				return True
		return False

	def checkCollisions(self, app):
		if self.handleObjectCollision(app, [app.map.goal]):
			return True, 'G'
		elif self.handleObjectCollision(app, app.map.walls):
			return True, 'W'
		elif self.handleObjectCollision(app, app.map.dWalls):
			return True, 'D'
		elif self.handleObjectCollision(app, app.map.itemDrops):
			return True, 'I'
		elif self.handleObjectCollision(app, app.zombies):
			return True, 'Z'
		elif self.handleObjectCollision(app, app.snipers):
			return True, 'S'
		elif self.handleObjectCollision(app, [app.player]):
			return True, 'P'

		return False, None

class Player(Agent):
	def __init__(self, scale, aX, aY, aR, health, ammo, damageInterval):
		super().__init__(scale, aX, aY, aR, health)
		self.ammo = ammo
		self.shotsFired = []
		self.damaged = False
		self.damageCounter = 500
		self.damageInterval = damageInterval

	def updateCarriedStats(self, app):
		self.health = app.playerHealth
		self.ammo = app.playerAmmo

	def getCell(self, app):
		row = int(self.aY//self.scale + 1)
		col = int(self.aX//self.scale + 1)

		if row <= 0:
			row += 1
		elif row >= app.mapSize-1:
			row -=1

		if col <= 0:
			col += 1
		elif col >= app.mapSize-1:
			col -=1
		
		return (row, col)

	def fireShots(self, app, x, y):
		if 'big' in app.shotMod:
			bulletSize = app.bulletSize*2
		else:
			bulletSize = app.bulletSize

		if 'bounce' in app.shotMod:
			bulletHealth = app.bulletHealth + 1
		else:
			bulletHealth = app.bulletHealth

		if 'tri' in app.shotMod:
			times = 3
		else:
			times = 1

		if 'fast' in app.shotMod:
			bulletSpeed = app.bulletSpeed*1.5
		else:
			bulletSpeed = app.bulletSpeed

		for i in range(times):
			space = 1
			self.shoot(app.width//2, app.height//2,
						 	 bulletSize, bulletHealth, bulletSpeed,
						 	 app.bulletSpacing+i*space, x, y)
			if 'spread' in app.shotMod:
				spread = app.bulletSpread
				self.shoot(app.width//2, app.height//2,
						 	 bulletSize, bulletHealth, bulletSpeed,
						 	 app.bulletSpacing+i*space, x-spread, y-spread)
				self.shoot(app.width//2, app.height//2,
						 	 bulletSize, bulletHealth, bulletSpeed,
						 	 app.bulletSpacing+i*space, x+spread, y+spread)

	def shoot(self, x, y, bR, bH, v, d, mouseX, mouseY):
		mX, mY = vector2Points(mouseX, mouseY, x, y)
		sX, sY = self.aX+mX*v*d, self.aY+mY*v*d

		newBullet = Bullet(self.scale, sX, sY, bR, bH, v, mX, mY)
		self.shotsFired.append(newBullet)

	def delBullet(self, i):
		self.shotsFired.pop(i)

	def modShot(self, app):
		mods = ['tri', 'bounce', 'spread', 'big', 'fast']
		selMods = []
		for i in mods:
			if i not in app.shotMod:
				selMods.append(i)
		mod = random.choice(selMods)
		app.shotMod.append(mod)

	def takeDamage(self):
		if not self.damaged:
			self.damaged = True
			self.damageCounter = 0
			self.health -= 1

	def updateDamageCounter(self):
		self.damageCounter += 1
		if self.damageCounter > self.damageInterval:
			self.damaged = False

	def addHealth(self, amount=1):
		self.health += amount

	def addAmmo(self, amount=1):
		self.ammo += amount

	def draw(self, app, canvas, w, h, r):
		triSize = self.aR//2
		x, y = w//2, h//2
		vertices = [(x, y-self.aR), (x-triSize, y+triSize), (x+triSize, y+triSize)]
		rVertices = rotateVertices(vertices, x, y, r)

		points = []
		for v in rVertices:
			points.append(v[0])
			points.append(v[1])

		color = app.colors['player']
		if self.damaged:
			color = app.colors['playerDamaged']

		canvas.create_polygon(points, fill=color, outline="")

class Zombie(Agent):
	def __init__(self, scale, aX, aY, aR, health, speed, attackInterval):
		super().__init__(scale, aX, aY, aR, health)
		self.speed = speed
		self.path = None
		self.mX = 0
		self.mY = 0
		self.attackInterval = attackInterval
		self.attackCounter = 500
		self.damaged = False
		self.damagedCounter = 10

	def setDamaged(self):
		self.damaged = True
		self.damagedCounter = 10

	def checkDamaged(self):
		self.damagedCounter -= 1
		if not self.damagedCounter:
			self.damaged = False

	def edgeStop(self, mapSize):
		row, col = self.getCell()
		if row == 0:
			self.aY+self.scale//2
			self.mY = 0
		elif row == mapSize:
			self.aY-self.scale//2
			self.mY = 0
		if col == 0:
			self.aX+self.scale//2
			self.mX = 0
		elif col == mapSize:
			self.aX-self.scale//2

	def setPath(self, levelMap, playerCell):
		nodePath = aStar(levelMap, self.getCell(), playerCell)
		if nodePath is not None:
			newPath = []
			for node in nodePath:
				newPath.append(node.cell)
			self.path = newPath
		else:
			self.path = None

	def chase(self, player):
		self.attackCounter += 1
		if self.path is not None:
			if self.getCell() == self.path[0]:
				if len(self.path) > 1:
					self.path.pop(0)

					zRow, zCol = self.getCell()
					pRow, pCol = self.path[0]

					self.mX = pCol - zCol
					self.mY = pRow - zRow
				else:
					pX, pY = player.getPos()
					self.mX, self.mY = 0, 0
					dist = dist2Points(pX, pY, self.aX, self.aY)
					if dist < self.scale*2 and dist > self.scale//3:
						self.mX, self.mY = vector2Points(pX, pY, self.aX, self.aY)
					else:
						if self.attackCounter > self.attackInterval:
							self.attackCounter = 0
							self.attack(player)
		else:
			pX, pY = player.getPos()
			dist = dist2Points(pX, pY, self.aX, self.aY)
			if dist > self.scale*3:
				self.mX, self.mY = 0, 0				
		
		self.move(self.mX * self.speed, self.mY * self.speed)

	def attack(self, player):
		player.takeDamage()

	def draw(self, app, canvas, mX, mY):
		color = app.colors['zombie']
		if self.damaged:
			color = app.colors['zombieDamaged']

		x = self.aX - mX + self.scale*3
		y = self.aY - mY + self.scale*3
		r = self.aR
		canvas.create_oval(x+r, y+r, x-r, y-r, fill=color, outline="")

class Sniper(Zombie):
	def __init__(self, scale, aX, aY, aR, health, speed, attackInterval):
		super().__init__(scale, aX, aY, aR, health, speed, attackInterval)
		self.shotsFired = []

	def setPath(self, levelMap, playerCell):
		nodePath = aStar(levelMap, self.getCell(), playerCell)
		if nodePath is not None:
			newEnd = directShotPos(nodePath, playerCell)
			nodePath = nodePath[:newEnd]
			newPath = []
			for node in nodePath:
				newPath.append(node.cell)
			self.path = newPath
		else:
			self.path = None

	def chase(self, app):
		self.attackCounter += 1
		if self.path is not None:
			if self.getCell() == self.path[0]:
				if len(self.path) > 1:
					self.path.pop(0)

					zRow, zCol = self.getCell()
					pRow, pCol = self.path[0]

					self.mX = pCol - zCol
					self.mY = pRow - zRow
				else:
					self.mX, self.mY = 0, 0
					if self.attackCounter > self.attackInterval:
						pX, pY = app.player.getPos()
						self.attackCounter = 0
						self.attack(app.bulletSize, app.bulletHealth, app.bulletSpeed,
							app.bulletSpacing, pX, pY)
		else:
			pX, pY = app.player.getPos()
			dist = dist2Points(pX, pY, self.aX, self.aY)
			if dist > self.scale*3:
				self.mX, self.mY = 0, 0
		
		self.move(self.mX * self.speed, self.mY * self.speed)

	def attack(self, bR, bH, v, d, playerX, playerY):
		mX, mY = vector2Points(playerX, playerY, self.aX, self.aY)
		sX, sY = self.aX+mX*v*d, self.aY+mY*v*d

		newBullet = SniperBullet(self.scale, sX, sY, bR, bH, v, mX, mY)
		self.shotsFired.append(newBullet)

	def delBullet(self, i):
		self.shotsFired.pop(i)

	def draw(self, app, canvas, mX, mY):
		color = app.colors['sniper']
		if self.damaged:
			color = app.colors['sniperDamaged']

		x = self.aX - mX + self.scale*3
		y = self.aY - mY + self.scale*3
		r = self.aR
		canvas.create_oval(x+r, y+r, x-r, y-r, fill=color, outline="")

class Bullet(Agent):
	def __init__(self, scale, aX, aY, aR, health, velocity, mX, mY):
		super().__init__(scale, aX, aY, aR, health)
		self.velocity = velocity
		self.mX = mX
		self.mY = mY

	def move(self):
		self.aX += self.mX * self.velocity
		self.aY += self.mY * self.velocity

	def bounce(self):
		self.mY *= random.choice([1,-1])
		self.mX *= random.choice([1,-1])

	def draw(self, app, canvas, pX, pY):
		color = app.colors['bullet']
		x, y = self.aX - pX + self.scale*3, self.aY - pY + self.scale*3
		r = self.aR
		canvas.create_oval(x+r, y+r, x-r, y-r, fill=color, outline="")

class SniperBullet(Bullet):
	def draw(self, app, canvas, pX, pY):
		color = app.colors['sniperBullet']
		x, y = self.aX - pX + self.scale*3, self.aY - pY + self.scale*3
		r = self.aR
		canvas.create_oval(x+r, y+r, x-r, y-r, fill=color, outline="")

class Item(object):
	def __init__(self, scale, iX, iY, iR):
		self.scale = scale
		self.iX = iX
		self.iY = iY
		self.iR = iR

	def getRowCol(self):
		return self.iY, self.iX

	def getBounds(self, app):
		mX, mY = app.player.getPos()
		scale = self.scale
		x = (self.iX+2) * scale + scale//2 - mX
		y = (self.iY+2) * scale + scale//2 - mY
		r = self.iR//2
		return x, y, r

	def drawBounds(self, app, canvas):
		if app.viewBounds:
			x,y,r = self.getBounds(app)
			canvas.create_rectangle(x-r,y-r,x+r,y+r, fill="", outline='red', width=2)

class ItemDrop(Item):
	def __init__(self, scale, iX, iY, iR):
		super().__init__(scale, iX, iY, iR)
		self.pickedUp = False
		self.color = ""

	def getPos(self):
		return self.iX, self.iY

	def getBounds(self, app):
		mX, mY = app.player.getPos()

		x = self.iX - mX + self.scale*3
		y = self.iY - mY + self.scale*3
		r = self.iR

		return x, y, r

	def dropUsed(self):
		return self.pickedUp

	def draw(self, app, canvas, mX, mY):
		x, y, xR, yR = (self.iX-mX+self.scale, self.iY-mY+self.scale,
						self.iR//2, self.iR)
		vertices = [x-xR, y, x, y-yR, x+xR, y, x, y+yR]
		canvas.create_polygon(vertices, fill=app.colors[self.color], outline='')

class HealthUp(ItemDrop):
	def __init__(self, scale, iX, iY, iR):
		super().__init__(scale, iX, iY, iR)
		self.color = 'healthUp'

	def healUpPlayer(self, app):
		app.player.addHealth(app.healthUpValue)
		app.playerHealth += app.healthUpValue
		self.pickedUp = True

	def getNameValue(self, app):
		return 'Health', app.healthUpValue

class AmmoUp(ItemDrop):
	def __init__(self, scale, iX, iY, iR):
		super().__init__(scale, iX, iY, iR)
		self.color = 'ammoUp'

	def ammoUpPlayer(self, app):
		app.player.addAmmo(app.ammoUpValue)
		app.playerAmmo += app.ammoUpValue
		self.pickedUp = True

	def getNameValue(self, app):
		return 'Ammo', app.ammoUpValue

class ScoreUp(ItemDrop):
	def __init__(self, scale, iX, iY, iR):
		super().__init__(scale, iX, iY, iR)
		self.color = 'scoreUp'

	def scoreUpPlayer(self, app):
		app.playerScore += app.scoreUpValue
		self.pickedUp = True

	def getNameValue(self, app):
		return 'Score', app.scoreUpValue

class Crosshair(Item):
	def setPos(self, x, y):
		self.iX, self.iY = x, y

	def draw(self, app, canvas):
		x, y = self.iX, self.iY
		r = self.iR
		color = app.colors['crosshair']
		canvas.create_line(x+r, y, x-r, y, fill=color)
		canvas.create_line(x, y+r, x, y-r, fill=color)
		r //= 3
		canvas.create_oval(x+r, y+r, x-r, y-r, outline=color)

class Goal(Item):
	def draw(self, app, canvas, mX, mY):
		x = self.iX
		y = self.iY
		scale = self.scale

		color = app.colors['goal']
		canvas.create_rectangle(x*scale-mX, y*scale-mY,
								x*scale+scale-mX, y*scale+scale-mY,
								fill=color, outline="")
class Start(Item):
	def draw(self, app, canvas, mX, mY):
		x = self.iX
		y = self.iY
		scale = self.scale

		color = app.colors['start']
		canvas.create_rectangle(x*scale-mX, y*scale-mY,
								x*scale+scale-mX, y*scale+scale-mY,
								fill=color, outline="")

class Wall(Item):
	def draw(self, app, canvas, mX, mY):
		x = self.iX
		y = self.iY
		scale = self.scale

		color = app.colors['wall']
		canvas.create_rectangle(x*scale-mX, y*scale-mY,
								x*scale+scale-mX, y*scale+scale-mY,
								fill=color, outline="")

class DestructibleWall(Item):
	def __init__(self, scale, iX, iY, iR, health):
		super().__init__(scale, iX, iY, iR)
		self.health = random.randint(1,health)
		self.colors = ['', 'RoyalBlue1', 'RoyalBlue2', 'RoyalBlue3', 'RoyalBlue4']

	def takeDamage(self):
		self.health -= 1

	def checkAlive(self):
		return self.health

	def draw(self, app, canvas, mX, mY):
		x = self.iX
		y = self.iY
		scale = self.scale

		if self.health < 0:
			self.health = 0
		color = self.colors[self.health]
		if app.viewBounds:
			color = app.colors['dWall']

		canvas.create_rectangle(x*scale-mX, y*scale-mY,
								x*scale+scale-mX, y*scale+scale-mY,
								fill=color, outline="")

class SlayMarker(Item):
	def __init__(self, scale, iX, iY, iR, marker):
		super().__init__(scale, iX, iY, iR)
		self.marker = marker

	def draw(self, app, canvas, mX, mY):
		x, y = self.iX-mX+self.scale, self.iY-mY+self.scale
		canvas.create_text(x, y, text=self.marker, font=f'Helvetica {self.iR}',
						   fill=app.colors['slayMark'])

class PickUpText(Item):
	def __init__(self, scale, iX, iY, iR, itemType, value, timer):
		super().__init__(scale, iX, iY, iR)
		self.itemType = itemType
		self.value = value
		self.timer = timer
		self.upValue = 3

	def updateText(self):
		self.timer -= 1
		self.iY -= self.upValue

	def checkAlive(self):
		return self.timer

	def draw(self, app, canvas, mX, mY):
		x, y = self.iX-mX+self.scale, self.iY-mY+self.scale
		text = f'{self.itemType} +{self.value}'
		canvas.create_text(x, y, text=text, font=f'Courier {self.iR}',
						   fill=app.colors['goal'])

class Map(object):
	def __init__(self, scale, size, start, goal):
		self.scale = scale
		self.size = size
		self.walls = []
		self.dWalls = []
		self.itemDrops = []
		self.text = []
		self.slayed = []
		self.start = start
		self.goal = goal
		self.levelMap = self.createMap()

	def __repr__(self):
		retString = ""
		for row in self.levelMap:
			strRow = copy.copy(row)
			for i in range(len(strRow)):
				strRow[i] = str(strRow[i])
			retString += str(strRow) + "\n"
		return retString

	def createMap(self):
		retM = []
		size = self.size
		for i in range(size):
			addL = []
			for j in range(size):
				if i == 0 or i == size-1 or j == 0 or j == size-1:
					addL.append('W')
				else:
					addL.append(0)
			retM.append(addL)
		return retM

	def mapRandomWalls(self, wallType, count):
		size = self.size
		while count > 0:
			for row in range(size):
				for col in range(size):
					if self.levelMap[row][col] == 0:
						make = random.randint(1, size-2)
						if make == 2:
							count -= 1
							self.levelMap[row][col] = wallType

	def validAdjacent(self, row, col):
		size = self.size
		l, d, r, u = True, True, True, True
		dirList = [(0,-1), (0,1), (-1, 0), (1,0), (-1,-1), (-1,1), (1,-1), (1,1)]

		if col < 2:
			dirList.remove((0,-1))
			l = False
		elif col > size-3:
			dirList.remove((0,1))
			r = False
		if row < 2:
			dirList.remove((-1,0))
			u = False
		elif row > size-3:
			dirList.remove((1, 0))
			d = False

		if not l or not u:
			dirList.remove((-1,-1))
		if not l or not d:
			dirList.remove((1,-1))
		if not r or not u:
			dirList.remove((-1,1))
		if not r or not d:
			dirList.remove((1,1))

		return dirList

	def makeClearing(self):
		size = self.size
		for row in range(size):
			for col in range(size):
				cell = self.levelMap[row][col]
				if cell == 'P' or cell == 'G':
					for cell in self.validAdjacent(row, col):
						self.levelMap[row + cell[0]][col + cell[1]] = 0

	def populateWalls(self, wallCount, dWallCount):
		validMap = False
		while not validMap:
			self.mapRandomWalls('W', wallCount)
			self.mapRandomWalls('D', dWallCount)
			self.makeClearing()

			solution = aStar(self.levelMap, self.goal.getRowCol(), self.start.getRowCol())
			if solution is not None:
				validMap = True

	def addItem(self, item, row, col):
		self.levelMap[row][col] = item

	def addDrop(self, drop):
		self.itemDrops.append(drop)

	def delDrop(self, i):
		self.itemDrops.pop(i)

	def addWall(self, row, col):
		wall = Wall(self.scale, col, row, self.scale)
		self.walls.append(wall)

	def addDWall(self, row, col, health):
		dWall = DestructibleWall(self.scale, col, row, self.scale, health)
		self.dWalls.append(dWall)

	def delDWall(self, i):
		self.dWalls.pop(i)

	def addPickUpText(self, text):
		self.text.append(text)

	def delPickUpText(self, i):
		self.text.pop(i)

	def drawText(self, app, canvas, mX, mY):
		mX -= app.scale*2
		mY -= app.scale*2

		for t in self.text:
			t.draw(app, canvas, mX, mY)

	def addMark(self, mark):
		self.slayed.append(mark)

	def drawChecker(self, app, canvas, mX, mY):
		size = self.size
		scale = self.scale

		mX -= scale*2
		mY -= scale*2

		# Background
		canvas.create_rectangle(app.width-app.width*3, app.height-app.height*3,
								app.width+app.width*3, app.height+app.height*3,
								fill=app.colors['background'])

		# Draw Board
		black = True
		for row in range(size):
			for col in range(size):
				color = app.colors['board1']
				if not black:
					black = True
					color = app.colors['board2']
				else:
					black = False
				canvas.create_rectangle(col*scale-mX, row*scale-mY,
										col*scale+scale-mX, row*scale+scale-mY,
										fill=color, outline="")

		# Draw Start and Goal
		self.start.draw(app, canvas, mX, mY)
		self.goal.draw(app, canvas, mX, mY)

		# Draw Slay Marker
		for mark in self.slayed:
			mark.draw(app, canvas, mX, mY)

		# Draw Walls
		for wall in self.walls:
			wall.draw(app, canvas, mX, mY)
			wall.drawBounds(app, canvas)
		for dWall in self.dWalls:
			dWall.draw(app, canvas, mX, mY)
			dWall.drawBounds(app, canvas)

		# Draw Drops
		for drop in self.itemDrops:
			drop.draw(app, canvas, mX, mY)
			drop.drawBounds(app, canvas)
