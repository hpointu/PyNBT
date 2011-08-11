import sys
import gzip
from nbt import *

class Item:
	def __init__(self):
		self.item_id = 0
		self.damage = 0
		self.count = 0
		self.slot = -1

	def __repr__(self):
		return "[" + str(self.slot) + "] \t" + str(self.item_id)+ " \t x " +str(self.count)

class ItemCollection:
	def __init__(self):
		self.items = []

	def addItem(self, item):
		self.items.append(item)

	def __repr__(self):
		s = []
		for i in self.items:
			s.append(repr(i))
		return "\n".join(s)

class Inventory:
	def __init__(self):
		self.items = ItemCollection()

	def addItem(self, item):
		self.items.addItem(item)

	def __repr__(self):
		result = ""
		result += "Items:\n"
		result += repr(self.items)
		return result
	
class InventoryParser:
	def __init__(self, data):
		self.data = data
		self.inventory = Inventory()
		
	def parse(self):
		for line in self.data.value:
			self.parseInventory(line.value)

	def parseInventory(self, i):
		_item = self.parseItem(i)
		#print _item
		self.inventory.addItem(_item)


	def parseItem(self, i):
		item = Item()
		
		for _data in i:
			if _data.name == "id":
				item.item_id = _data.value
			elif _data.name == "Damage":
				item.damage = _data.value
			elif _data.name == "Count":
				item.count = _data.value
			elif _data.name == "Slot":
				item.slot = _data.value
		return item

def main(arg):

	nb = NBTParser(arg)
	nb.parse()	
	l = nb.root.findByName('Inventory')
	

	if len(l)>0:
		inventoryParser = InventoryParser(l[0])
		inventoryParser.parse()
		print repr(inventoryParser.inventory)
	
	return 0

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "Usage : "+sys.argv[0]+" file.dat"
		sys.exit(0)
	sys.exit(main(sys.argv[1]))
