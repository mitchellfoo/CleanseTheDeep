#################################################
# CtD_Customizers_UI.py:
#
# File containing definitions for all key
# gameplay customizers and functions related to
# game UI
#
# Your name: Mitchell Foo
# Your andrew id: mfoo
#################################################

from cmu_112_graphics import *

### Game Customizers

def runGameCustomizers(app):
	playerCustomize(app)
	zombieCustomize(app)
	sniperCustomize(app)
	mapCustomize(app)
	itemCustomize(app)
	UICustomize(app)

def playerCustomize(app):
	app.playerHealth = 9
	app.playerSize = 30
	app.playerAmmo = 30
	app.playerSpeed = 10
	app.playerScore = 0
	app.playerDepth = 1
	app.playerDamagedInterval = 15
	app.gunModInterval = 5

def zombieCustomize(app):
	app.zombieHealth = 3
	app.zombieSize = 15
	app.zombieSpeed = 7
	app.zombieCount = 4
	app.zombieScore = 50
	app.zombieAttackRange = 5
	app.zombieAttackInterval = 5

def sniperCustomize(app):
	app.sniperHealth = 1
	app.sniperSize = 12
	app.sniperSpeed = 5
	app.sniperCount = 1
	app.sniperScore = 100
	app.sniperAttackInterval = 25

def mapCustomize(app):
	app.mapSize = 9
	app.wallCount = app.mapSize//3
	app.dWallCount = app.mapSize//2
	app.dWallHealth = 4
	app.levelScore = 1000
	app.minGoalDist = app.mapSize // 1.6
	app.minSpawnDist = app.mapSize // 1.8
	app.mapIncreaseInterval = 5

def itemCustomize(app):
	# Bullet
	app.bulletSize = 3
	app.bulletHealth = 1
	app.bulletSpeed = 25
	app.bulletSpacing = 1.5
	app.bulletSpread = 30

	# Drops
	app.healthSize = 10
	app.healthUpValue = 1

	app.ammoSize = 10
	app.ammoUpValue = 5

	app.scoreSize = 15
	app.scoreUpValue = 300

	app.textSize = 12
	app.textTimer = 20

	## [Health, Ammo, Points, None]
	itemRates = [30, 30, 20, 20]
	## Code referenced from: https://stackoverflow.com/questions/14992521/python-weighted-random
	app.itemDrops = ['H']*itemRates[0] + ['A']*itemRates[1] + ['P']*itemRates[2] + ['N']*itemRates[3]

def UICustomize(app):
	app._root.config(cursor="none")
	app.timerDelay = 30
	app.winDelay = 200
	app.crosshairSize = 15
	app.currMods = []
	
	# Slay Marker
	app.slayMark = 'X'
	app.slayMarkSize = 25

	# Global Colors
	app.splashColor = 'peach puff'
	app.buttonColor = 'white'
	app.hoverColor = 'pink'

	# Button Bools
	app.guideHover = False
	app.startHover = False
	app.homeHover = False

	# Button Location
	guideWidth = 80
	guideHeight = 20
	app.guideCoords = [app.width//2-guideWidth, app.height//2.5-guideHeight,
				   app.width//2+guideWidth, app.height//2.5+guideHeight]

	startWidth = 120
	startHeight = 30
	app.startCoords = [app.width//2-startWidth, app.height//2-startHeight,
				   app.width//2+startWidth, app.height//2+startHeight]

	app.homeCoords = [app.width//2-guideWidth, app.height//1.2-guideHeight,
				   app.width//2+guideWidth, app.height//1.2+guideHeight]

def colorDictionary(app):
	if app.viewBounds:
		app.colors = {
			"player": "blue",
			"playerDamaged": "pink",
			"zombie": "purple",
			"zombieDamaged": "coral",
			"sniper": "magenta",
			"sniperDamaged": "dark orange",
			"bullet": "black",
			"sniperBullet": "magenta",
			"healthUp": "lawn green",
			"ammoUp": "indian red",
			"scoreUp": "gold",
			"crosshair": "orange",
			"goal": "yellow",
			"start": "cyan",
			"wall": "brown",
			"dWall": "red",
			"slayMark": "grey",
			"background": "navy",
			"board1": "green",
			"board2": "lime green",
		}
	else:
		app.colors = {
			"player": "sandy brown",
			"playerDamaged": "red2",
			"zombie": "green yellow",
			"zombieDamaged": "maroon",
			"sniper": "khaki",
			"sniperDamaged": "pale violet red",
			"bullet": "gainsboro",
			"sniperBullet": "purple",
			"healthUp": "lawn green",
			"ammoUp": "hot pink",
			"scoreUp": "gold",
			"crosshair": "orange",
			"goal": "yellow",
			"start": "cyan",
			"wall": "saddle brown",
			"dWall": "royal blue",
			"slayMark": "red",
			"background": "black",
			"board1": "slate gray",
			"board2": "light slate gray",
		}

def playerModifiers(app):
	app.healthUpMod = 0
	app.ammoUpMod = 0
	app.scoreUpMod = 0

	app.playerSpeedMod = 0
	app.playerAmmoMod = 0
	app.playerHealthMod = 0

def enemyModifiers(app):
	app.zombieSpeedMod = 0
	app.zombieHealthMod = 0
	app.zombieCountMod = 0

	app.sniperHealthMod = 0
	app.sniperCountMod = 0
	app.sniperSpeedMod = 0

### UI
def drawBacksplash(app, canvas, color):
	canvas.create_rectangle(0, 0, app.width, app.height,
							fill=color, outline="")

def drawTitleScreen(app, canvas):
	drawBacksplash(app, canvas, app.splashColor)
	
	# Title
	canvas.create_text(app.width//2, app.height//4,
                	   text='CLEANSE THE DEEP', font='Terminal 32 bold')
	# Guide Button
	guideColor = app.buttonColor
	if app.guideHover:
		guideColor = app.hoverColor

	canvas.create_rectangle(app.guideCoords, fill=guideColor, outline ="")
	canvas.create_text(app.width//2, app.height//2.5,
					   text='Game Guide', font= 'Courier 12')

	# Start Button
	startColor = app.buttonColor
	if app.startHover:
		startColor = app.hoverColor

	canvas.create_rectangle(app.startCoords, fill=startColor, outline ="")
	canvas.create_text(app.width//2, app.height//2,
					   text='ENTER THE DEEP', font= 'Courier 18')

	# Shot Mods
	allMods = getGunMods(app)
	canvas.create_text(app.width//2, app.height//2 + app.height//4,
					   text=allMods, font= 'Courier 12', fill='red')

	# View Bounds?
	if app.viewBounds:
		canvas.create_text(app.width//2, app.height - app.height//8,
					   text='Developer View', font= 'Courier 8', fill='red')

def drawGuideScreen(app, canvas):
	drawBacksplash(app, canvas, 'green')

	# Title
	canvas.create_text(app.width//2, app.height//4,
                   	   text='GAME GUIDE', font='Terminal 32 bold')
	
	# Body Text
	instructions = ("WASD is for player directional movement\n\n" + 
					"Point with cursor and left-click to fire bullets\n\n" +
					"Dark blue walls are indestructible whereas lighter blue walls are destructible by bullets\n\n" +
					"Reach the highlighted goal to descend into the next level\n\n" +
					"Red pickups increase ammo, green increases health, yellow your score\n\n" +
					"Gameplay changes over the rounds...\n\n")

	canvas.create_text(app.width//2, app.height//2+app.height//12,
                   	   text=instructions, font='Courier 10', fill='white', width = app.width//1.5)

	# Home Button
	homeColor = app.buttonColor
	if app.homeHover:
		homeColor = app.hoverColor

	canvas.create_rectangle(app.homeCoords, fill=homeColor, outline ="")
	canvas.create_text(app.width//2, app.height//1.2,
					   text='Home Screen', font= 'Courier 12')

def drawLoseScreen(app, canvas):
	drawBacksplash(app, canvas, 'brown')

	canvas.create_text(app.width//2, app.height//4,
                   	   text='GAME OVER', font='Terminal 32 bold')
	canvas.create_text(app.width//2, app.height//3+15,
                   	   text=f'Final Score: {app.playerScore}', font='Terminal 14 bold')
	canvas.create_text(app.width//2, app.height//3+35,
                   	   text=f'Depth Reached: {app.playerDepth}', font='Terminal 14 bold')

	# Game Modifiers
	drawModifiers(app, canvas)

	# Home Button
	homeColor = app.buttonColor
	if app.homeHover:
		homeColor = app.hoverColor

	canvas.create_rectangle(app.startCoords, fill=homeColor, outline ="")
	canvas.create_text(app.width//2, app.height//2,
					   text='HOME SCREEN', font= 'Courier 18')

def drawWinScreen(app, canvas):
	drawBacksplash(app, canvas, 'yellow')

	canvas.create_text(app.width//2, app.height//4,
                   	   text='GOAL REACHED', font='Terminal 32 bold')
	canvas.create_text(app.width//2, app.height//3+35,
                   	   text=f'Descending to level: {app.playerDepth+1}', font='Terminal 14 bold')
	
	dots = '.'*(app.winDelay//20)
	canvas.create_text(app.width//2, app.height//2-20,
                   	   text=dots, font='Terminal 32 bold')

	# Current Game Modifiers
	mods = app.currMods
	mapIncrease = (app.playerDepth+1) // app.mapIncreaseInterval

	appliedMods = f"{mods[0]} drop leveled up, player {mods[1]} leveled up\n\n"
	appliedMods += f"zombie {mods[2]} leveled up, sniper {mods[3]} leveled up\n\n"
	appliedMods += f"map size level: {mapIncrease + 1}"
	
	canvas.create_text(app.width//2, app.height//2 + app.height//8,
					   text=appliedMods, font='Terminal 14', fill='purple')

	if getGunMods(app):
		guns = 'Gun Mods:' + getGunMods(app)
	else:
		guns = ""
	canvas.create_text(app.width//2, app.height//2 + app.height//8+70,
					   text=guns, font='Courier 10', fill='red')

	drawModifiers(app, canvas)

def getGunMods(app):
	allMods = ""
	for mod in app.shotMod:
		allMods += "   " + mod + "   "
	return allMods

def drawModifiers(app, canvas):
	tX = app.width//5
	tY = app.height//2 + app.height//2.8
	width = app.width//6
	font = 'Courier 8'

	itemText = f"Health Up Level: {app.healthUpMod}\n"
	itemText += f"Ammo Up Level: {app.ammoUpMod//5}\n"
	itemText += f"Score Up Level: {app.scoreUpMod//100}"

	playerText = f"Health Regen Level: {app.playerHealthMod//2}\n"
	playerText += f"Ammo Regen Level: {app.playerAmmoMod//5}\n"
	playerText += f"Player Speed Level: {app.playerSpeedMod//2}"

	zombieText = f"Zombie Health Level: {app.zombieHealthMod}\n"
	zombieText += f"Zombie Speed Level: {app.zombieSpeedMod//2}\n"
	zombieText += f"Zombie Count Level: {app.zombieCountMod}"
	
	sniperText = f"Sniper Health Level: {app.sniperHealthMod}\n"
	sniperText += f"Sniper Speed Level: {app.sniperSpeedMod//3}\n"
	sniperText += f"Sniper Count Level: {app.sniperCountMod}"

	canvas.create_text(tX, tY, text=itemText, font=font, width=width)
	canvas.create_text(tX*2, tY, text=playerText, font=font, width=width)
	canvas.create_text(tX*3, tY, text=zombieText, font=font, width=width)
	canvas.create_text(tX*4, tY, text=sniperText, font=font, width=width)

### Button Controls

def checkHover(coordinates, mouseX, mouseY):
	if mouseX > coordinates[0] and mouseX < coordinates[2]:
		if mouseY > coordinates[1] and mouseY < coordinates[3]:
			return True
	return False