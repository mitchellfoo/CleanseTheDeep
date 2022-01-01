#################################################
# CtD_Game.py:
#
# File containing app definition and functions
# related to game interactions of objects - run
# the game with this file
#
# Your name: Mitchell Foo
# Your andrew id: mfoo
#################################################

from CtD_Classes import *
from CtD_Customizers_UI import *

### App

def appStarted(app):
	# Game Customizations
	runGameCustomizers(app)
	playerModifiers(app)
	enemyModifiers(app) 

	## Controls
	app.keysDown = set()
	app.validMove = {'a', 'd', 'w', 's'}

	## Flags
	app.title = True
	app.guide = False
	app.playing = False
	app.goalReached = False
	app.gameOver = False
	
	app.chosenMods = False
	app.goalScored = False
	app.firstClick = True
	app.shotEnabled = False
	app.viewBounds = False

	# Draw Factors
	colorDictionary(app)
	app.scale = 100

	# Game Objects
	## Agents
	newPlayer(app)
	newEnemyList(app)

	## Map
	newMap(app)
	populateMap(app)

	app.crosshair = Crosshair(app.scale, 0, 0, app.crosshairSize)

	# Game Factors
	app.playerMoveVector = 0,0
	app.playerRotation = 0
	app.shotMod = []

def mousePressed(app, event):
	x, y = event.x, event.y

	# Button Events
	if app.title:
		if app.guideHover:
			changeState(app, 'guide')
		elif app.startHover:
			changeState(app, 'playing')
	elif app.guide:
		if app.homeHover:
			changeState(app, 'title')
	elif app.gameOver:
		if app.homeHover:
			restartGame(app)

	# Shooting
	if app.playerAmmo > 0 and app.playing and not app.firstClick and app.shotEnabled:
		app.player.fireShots(app, x, y)
		app.playerAmmo -= 1
	elif app.playing:
		app.firstClick = False

def mouseMoved(app, event):
	mouseX, mouseY = event.x, event.y

	# Title Screen
	if app.title:
		app.guideHover = checkHover(app.guideCoords, mouseX, mouseY)
		app.startHover = checkHover(app.startCoords, mouseX, mouseY)
	elif app.guide:
		app.guideHover = False
		app.homeHover = checkHover(app.homeCoords, mouseX, mouseY)
	elif app.gameOver:
		app.homeHover = checkHover(app.startCoords, mouseX, mouseY)

	# Update crosshair
	app.crosshair.setPos(mouseX, mouseY)

	# Rotate player towards mouse
	mouseX -= app.width//2
	mouseY -= app.height//2
	
	mod = 1
	if event.x < app.width//2:
		mod *= -1

	app.playerRotation = mod * angle2Vectors(mouseX, mouseY)

def keyPressed(app, event):
	key = event.key.lower()
	if key in app.validMove and app.playing:
		app.keysDown.add(key)
	elif app.playing:
		if key == 'r':
			app.player.addAmmo(10)
			app.playerAmmo += 10

	elif app.title:
		mod = None
		if key == '1':
			mod = 'big'
		elif key == '2':
			mod = 'bounce'
		elif key == '3':
			mod = 'tri'
		elif key == '4':
			mod = 'fast'
		elif key == '5':
			mod = 'spread'
		elif key == 'b':
			app.viewBounds = not app.viewBounds
			colorDictionary(app)

		if mod is not None:
			if mod in app.shotMod:
				app.shotMod.remove(mod)
			else:
				app.shotMod.append(mod)

def keyReleased(app, event):
	key = event.key.lower()
	if key in app.keysDown:
		app.keysDown.remove(key)

def timerFired(app):
	# Update Player Cell
	checkPlayerMoved(app)

	# Spawn Enemies
	if app.playing:
		spawnZombies(app)
		spawnSnipers(app)

	# Move Player
	mX, mY = getMoveVector(app)
	speed = app.playerSpeed
	app.player.move(mX*speed, mY*speed)

	# Check Player Collisions
	checkPlayerCollision(app, mX, mY)

	# Move Enemies
	moveEnemies(app)

	# Move Bullets
	moveBullets(app, app.player.shotsFired, app.player)
	for sniper in app.snipers:
		moveBullets(app, sniper.shotsFired, sniper)

	# Check Object Lives
	## Check Player Health
	checkPlayerHealth(app)
	app.playerHealth = app.player.health

	## Check Enemy Health
	app.player.updateDamageCounter()
	checkEnemyHealth(app, app.zombies, app.zombieScore)
	checkEnemyHealth(app, app.snipers, app.sniperScore)

	## Check D Wall Health
	checkDWallHealth(app)

	## Check Dropped Item
	checkItemDrops(app)
	checkItemText(app)

	# Win State Delay
	checkWinState(app)

def redrawAll(app, canvas):
	# Draw Board
	pX, pY = app.player.getPos()
	app.map.drawChecker(app, canvas, pX, pY)

	# Draw Bullets
	drawBullets(app, canvas)

	# Draw Player
	app.player.draw(app, canvas, app.width, app.height, app.playerRotation)
	app.player.drawBounds(app, canvas)

	# Draw Enemies
	drawZombies(app, canvas)
	drawSnipers(app, canvas)

	# Draw UI
	fill = 'peach puff'
	canvas.create_text(app.width//10, app.height//9,
                       text=f'Score: {app.playerScore}', font='Courier 12 bold', fill=fill)
	canvas.create_text(app.width//10, app.height//9 + 25,
                       text=f'Health: {app.playerHealth}', font='Courier 12 bold', fill=fill)
	canvas.create_text(app.width//10, app.height//9 + 50,
                       text=f'Ammo: {app.playerAmmo}', font='Courier 12 bold', fill=fill)
	canvas.create_text(app.width//10, app.height//9 + 75,
                       text=f'Depth: {app.playerDepth}', font='Courier 12 bold', fill=fill)

	# Draw Text
	app.map.drawText(app, canvas, pX, pY)

	# Check State 
	drawCurrState(app, canvas)

	# Draw Crosshair
	app.crosshair.draw(app, canvas)

def runGame():
    runApp(width=600, height=600)

### Helper Functions

# Game State and Levels
def restartGame(app, end=True):
	runGameCustomizers(app)
	changeState(app, 'title')
	app.firstClick = True
	app.shotEnabled = False
	app.chosenMods = False

	newPlayer(app)
	newEnemyList(app)

	app.goalScored = False

	if end:
		app.shotMod = []
		newMap(app)
		populateMap(app)
		playerModifiers(app)
		enemyModifiers(app)

def checkWinState(app):
	if app.goalReached:
		app.winDelay -= 1
		if not app.chosenMods:
			app.chosenMods = True
			chooseModifiers(app)
		if not app.winDelay:
			nextLevel(app)

def nextLevel(app):
	# Carry-Over Stats
	currHealth = app.playerHealth
	currAmmo = app.playerAmmo
	currScore = app.playerScore
	currDepth = app.playerDepth + 1

	# Restart Game
	restartGame(app, False)

	# Apply Carried Stats
	app.playerHealth = currHealth
	app.playerAmmo = currAmmo
	app.playerScore = currScore
	app.playerDepth = currDepth

	# Modifiers
	applyModifiers(app)
	updateMapSize(app)
	newMap(app)
	populateMap(app)
	addGunMod(app)

	# Update Player
	app.player.updateCarriedStats(app)

	# Start Playing
	changeState(app, 'playing')

	app.firstClick = False

def chooseModifiers(app):
	# Item Mod
	item = random.choice(['health', 'ammo', 'score'])
	if item == 'health':
		app.healthUpMod += 1
	elif item == 'ammo':
		app.ammoUpMod += 5
	elif item == 'score':
		app.scoreUpMod += 100

	# Player Mod
	player = random.choice(['speed', 'ammo', 'health'])
	if player == 'speed':
		app.playerSpeedMod += 2
	elif player == 'ammo':
		app.playerAmmoMod += 5
	elif player == 'health':
		app.playerHealthMod += 2

	# Zombie Mod
	zombie = random.choice(['speed', 'health', 'count'])
	if zombie == 'speed':
		app.zombieSpeedMod += 2
	elif zombie == 'health':
		app.zombieHealthMod += 1
	elif zombie == 'count':
		app.zombieCountMod += 1

	# Sniper Mod
	sniper = random.choice(['speed', 'health', 'count'])
	if sniper == 'speed':
		app.sniperSpeedMod += 3
	elif sniper == 'health':
		app.sniperHealthMod += 1
	elif sniper == 'count':
		app.sniperCountMod += 1

	app.currMods = [item, player, zombie, sniper]

def updateMapSize(app):
	mapIncrease = app.playerDepth // app.mapIncreaseInterval
	app.mapSize += mapIncrease * 2

def applyModifiers(app):
	# Item
	app.healthUpValue += app.healthUpMod
	app.ammoUpValue += app.ammoUpMod
	app.scoreUpValue += app.scoreUpMod

	# Player
	app.playerSpeed += app.playerSpeedMod
	app.playerAmmo += app.playerAmmoMod
	app.playerHealth += app.playerHealthMod

	# Zombie
	app.zombieSpeed += app.zombieSpeedMod
	app.zombieCount += app.zombieCountMod
	app.zombieHealth += app.zombieHealthMod

	# Sniper
	app.sniperSpeed += app.sniperSpeedMod
	app.sniperCount += app.sniperCountMod
	app.sniperHealth += app.sniperHealthMod

def addGunMod(app):
	if app.playerDepth % app.gunModInterval == 0:
		app.player.modShot(app)

def changeState(app, state):
	app.title = False
	app.guide = False
	app.playing = False
	app.goalReached = False
	app.gameOver = False

	if state == 'title':
		app.title = True
	elif state == 'guide':
		app.guide = True
	elif state == 'playing':
		app.playing = True
	elif state == 'goal':
		app.goalReached = True
	elif state == 'gameover':
		app.gameOver = True

def drawCurrState(app, canvas):
	if app.title:
		drawTitleScreen(app, canvas)
	elif app.gameOver:
		drawLoseScreen(app, canvas)
	elif app.goalReached:
		drawWinScreen(app, canvas)
	elif app.guide:
		drawGuideScreen(app, canvas)

# Map Functions
def newMap(app):
	pRow, pCol = app.player.getCell(app)
	playerX, playerY = app.player.getPos()

	start = Start(app.scale, pCol, pRow, app.scale)
	goal = createGoal(app, playerX, playerY)
	app.map = Map(app.scale, app.mapSize, start, goal)
	app.map.addItem('P', pRow, pCol)
	
	gRow, gCol = app.map.goal.getRowCol()
	app.map.addItem('G', gRow, gCol)

def createGoal(app, playerX, playerY):
	dist = -1
	scale = app.scale
	minDist = app.minGoalDist*scale
	while dist < minDist:
		row, col = randomColRow(app)
		dist = dist2Points(col*scale, row*scale, playerX, playerY)
		minDist -= 20

	return Goal(app.scale, col, row, app.scale)

def randomStart(app):
	scale = app.scale
	size = app.mapSize
	row = random.randint(1, size-2)
	col = random.randint(1, size-2)

	return row, col

def randomColRow(app):
	size = app.mapSize
	row = random.randint(1, size-2)
	col = random.randint(1, size-2)
	return row, col

def populateMap(app):
	app.map.populateWalls(app.wallCount, app.dWallCount)
	for row in range(app.mapSize):
		for col in range(app.mapSize):
			if app.map.levelMap[row][col] == 'W':
				app.map.addWall(row, col)
			elif app.map.levelMap[row][col] == 'D':
				app.map.addDWall(row, col, app.dWallHealth)

# Control Functions
def getMoveVector(app):
	vX, vY = 0,0

	if 'd' in app.keysDown:
		vX += 1
	if 'a' in app.keysDown:
		vX -= 1
	if 'w' in app.keysDown:
		vY -= 1
	if 's' in app.keysDown:
		vY += 1

	return vX, vY

# Player Functions
def newPlayer(app):
	pRow, pCol = randomStart(app)
	app.playerCell = (pRow, pCol)
	playerX, playerY = pCol*app.scale - app.scale//2, pRow*app.scale - app.scale//2
	app.player = Player(app.scale, playerX, playerY, app.playerSize,
						app.playerHealth, app.playerAmmo, app.playerDamagedInterval)

def checkPlayerHealth(app):
	if not app.player.checkAlive():
		newEnemyList(app)
		changeState(app, 'gameover')

def checkPlayerCollision(app, mX, mY):
	collision, collisionType = app.player.checkCollisions(app)
	if collision:
		if collisionType == 'G':
			newEnemyList(app)
			changeState(app, 'goal')
			if not app.goalScored:
				app.goalScored = True
				app.playerScore += app.levelScore
		elif collisionType == 'W' or collisionType == 'D':
			app.player.move(-mX*app.playerSpeed, -mY*app.playerSpeed)

def checkPlayerMoved(app):
	row, col = app.player.getCell(app)

	if app.playerCell != (row,col):
		app.playerCell = (row, col)
		updateEnemyPath(app)
		app.shotEnabled = True
		return True

	return False

# Bullet Functions
def drawBullets(app, canvas):
	x, y = app.player.getPos()
	for bullet in app.player.shotsFired:
		bullet.draw(app, canvas, x, y)
		bullet.drawBounds(app, canvas)

	for sniper in app.snipers:
		for sniperBullet in sniper.shotsFired:
			sniperBullet.draw(app, canvas, x, y)
			sniperBullet.drawBounds(app, canvas)

def moveBullets(app, shots, shooter):
	delBullets = []

	# Move each bullet, and check collision
	for bullet in range(len(shots)):
		shots[bullet].move()
		if checkBulletCollision(app, shots[bullet]):
			shots[bullet].takeDamage()
			if shots[bullet].checkAlive():
				shots[bullet].bounce()
			else:
				delBullets.append(bullet)

	# Delete collided bulletsb
	for b in delBullets[::-1]:
		shooter.delBullet(b)

def checkBulletCollision(app, bullet):
	possibleCollisions = {'W', 'D', 'Z', 'S', 'P'}
	collision, collisionType = bullet.checkCollisions(app)
	if collision:
		if collisionType in possibleCollisions:
			return True

# Item Functions
def checkDWallHealth(app):
	delList = []
	dWalls = app.map.dWalls
	for i in range(len(dWalls)):
		if not dWalls[i].checkAlive():
			delList.append(i)

	for j in delList[::-1]:
		app.map.delDWall(j)

def checkItemDrops(app):
	delList = []
	drops = app.map.itemDrops
	for i in range(len(drops)):
		if drops[i].dropUsed():
			delList.append(i)

	for j in delList[::-1]:
		itemDropText(app, drops[j])
		app.map.delDrop(j)

def checkItemText(app):
	delList = []
	itemText = app.map.text
	for i in range(len(itemText)):
		itemText[i].updateText()
		if not itemText[i].checkAlive():
			delList.append(i)

	for j in delList[::-1]:
		app.map.delPickUpText(j)


def itemDropText(app, item):
	iX, iY = item.getPos()
	name, value = item.getNameValue(app)
	text = PickUpText(app.scale, iX, iY, app.textSize,
					  name, value, app.textTimer)
	app.map.addPickUpText(text)



# Enemy Functions
def newEnemyList(app):
	app.zombies = []
	app.snipers = []

def randSpeed(midSpeed):
	return random.randint(midSpeed-1,midSpeed+1)

def spawnZombies(app):
	while len(app.zombies) < app.zombieCount:
		dist = -1
		scale = app.scale
		pX, pY = app.player.getPos()
		minDist = app.minSpawnDist*scale
		while dist < minDist:
			cell = True
			while cell:
				row, col = randomColRow(app)
				cell = app.map.levelMap[row][col]
			dist = dist2Points(col*scale, row*scale, pX, pY)
			minDist -= 50
		app.zombies.append(Zombie(scale, col*scale-scale/2, row*scale-scale/2,
								  app.zombieSize, app.zombieHealth,
								  randSpeed(app.zombieSpeed), app.zombieAttackInterval))

def spawnSnipers(app):
	while len(app.snipers) < app.sniperCount:
		dist = -1
		scale = app.scale
		pX, pY = app.player.getPos()
		minDist = app.minSpawnDist*scale
		while dist < minDist:
			cell = True
			while cell:
				row, col = randomColRow(app)
				cell = app.map.levelMap[row][col]
			dist = dist2Points(col*scale, row*scale, pX, pY)
			minDist -= 50
		app.snipers.append(Sniper(scale, col*scale-scale/2, row*scale-scale/2,
								  app.sniperSize, app.sniperHealth,
								  randSpeed(app.sniperSpeed), app.sniperAttackInterval))

def drawZombies(app, canvas):
	x, y = app.player.getPos()
	for zombie in app.zombies:
		zombie.draw(app, canvas, x, y)
		zombie.drawBounds(app, canvas)

def drawSnipers(app, canvas):
	x, y = app.player.getPos()
	for sniper in app.snipers:
		sniper.draw(app, canvas, x, y)
		sniper.drawBounds(app, canvas)

def checkEnemyHealth(app, enemyList, score):
	delList = []
	for i in range(len(enemyList)):
		enemyList[i].checkDamaged()
		if not enemyList[i].checkAlive():
			delList.append(i)

	for j in delList[::-1]:
		enemyItemDrop(app, enemyList[j])
		enemySlayMark(app, enemyList[j])
		enemyList.pop(j)
		app.playerScore += score

def enemySlayMark(app, enemy):
	eX, eY = enemy.getPos()
	app.map.addMark(SlayMarker(app.scale, eX, eY,
							   app.slayMarkSize, app.slayMark))

def enemyItemDrop(app, enemy):
	eX, eY = enemy.getPos()
	drop = random.choice(app.itemDrops)

	if drop == 'H':
		item = HealthUp(app.scale, eX, eY, app.healthSize)
	elif drop == 'A':
		item = AmmoUp(app.scale, eX, eY, app.ammoSize)
	elif drop == 'P':
		item = ScoreUp(app.scale, eX, eY, app.scoreSize)
	elif drop == 'N':
		return None

	app.map.addDrop(item)

def moveEnemies(app):
	for zombie in app.zombies:
		zombie.chase(app.player)
		zombie.edgeStop(app.mapSize)

	for sniper in app.snipers:
		sniper.chase(app)
		sniper.edgeStop(app.mapSize)

def updateEnemyPath(app):
	for zombie in app.zombies:
		zombie.setPath(app.map.levelMap, app.playerCell)

	for sniper in app.snipers:
		sniper.setPath(app.map.levelMap, app.playerCell)

### Main

def main():
    runGame()

if __name__ == '__main__':
    main()