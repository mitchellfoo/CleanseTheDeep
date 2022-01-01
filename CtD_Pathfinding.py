#################################################
# CtD_Pathfinding.py:
#
# File containing objects and functions related
# enemy pathfinding via A*
#
# Your name: Mitchell Foo
# Your andrew id: mfoo
#################################################

# Referenced A* algorithm from:
# https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2

class Node(object):
	def __init__(self, parent, cell):
		self.parent = parent
		self.cell = cell
		self.g = 0
		self.h = 0
		self.f = 0

	def __repr__(self):
		return f"Node at: {self.cell}"

	def __eq__(self, other):
		return (self.cell == other.cell)

def manhattanDistance(x1, y1, x2, y2):
	return abs((x1-x2) + (y1-y2))

def backtrackNode(node):
	retPath = []
	while node is not None:
		retPath.append(node)
		node = node.parent
	return retPath[::-1]

def getAdjacentCells(row, col):
	dirList = [(0,-1), (0,1), (-1, 0), (1,0)]
	retList = []
	for aR, aC in dirList:
		aR += row
		aC += col
		retList.append((aR, aC))
	return retList

def getNodeChildren(levelMap, node):
	retChildren = []
	nRow, nCol = node.cell
	for aRow, aCol in getAdjacentCells(nRow, nCol):
		cellVal = levelMap[aRow][aCol]
		if cellVal == 0 or cellVal == 'P':
			aNode = Node(node, (aRow, aCol))
			retChildren.append(aNode)
	return retChildren

def aStar(levelMap, start, end):
	openNodes = []
	closedNodes = []

	startNode = Node(None, start)
	endNode = Node(None, end)

	openNodes.append(startNode)

	while openNodes:
		# Get current node
		currentNode = openNodes[0]
		openNodes.remove(currentNode)
		closedNodes.append(currentNode)

		# Check goal
		if currentNode == endNode:
			return backtrackNode(currentNode)

		# Get children
		adjacentNodes = getNodeChildren(levelMap, currentNode)
		
		for child in adjacentNodes:
			if child in closedNodes:
				continue

			childRow, childCol = child.cell
			currRow, currCol = currentNode.cell
			endRow, endCol = endNode.cell

			child.g = currentNode.g + manhattanDistance(childCol, childRow, currCol, currCol)
			child.h = manhattanDistance(childCol, childRow, endCol, endRow)
			child.f = child.g + child.h

			for oldChild in openNodes:
				if child == oldChild:
					if child.g > oldChild.g:
						continue

			openNodes.append(child)

def directShotPos(path, end):
	revPath = path[::-1]
	endRow, endCol = end
	row = None
	val = None
	count = 1

	for node in revPath[1:]:
		currRow, currCol = node.cell
		if val is None:
			if currRow == endRow:
				val = currRow
				row = True
				count += 1
			elif currCol == endCol:
				val = currCol
				row = False
				count += 1
			else:
				return count
		elif row:
			if currRow == endRow:
				count += 1
			else:
				return count
		else:
			if currCol == endCol:
				count += 1
			else:
				return count