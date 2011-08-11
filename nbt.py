import struct
import gzip

class NBTNode:
	def __init__(self):
		self.name = None
		self.type = None
		self.count = False
		self.value = None
		self.parent = None
		
	def __repr__(self):
		nbParents = 0
		cur = self
		while cur.parent:
			nbParents += 1
			cur = cur.parent
		
		if self.parent and (self.parent.type == NBTParser.TAG_List):
			nbParents -= 1

		off = ""
		for i in range(nbParents):
			off += "  "
		
		_name = ""
		if self.name:
			_name = self.name
		s = off+"("+str(self.type)+")"+_name+" {\n"
		if self.count:
			for v in self.value:
				s += off+repr(v)
		else:
			s += off+"  "+str(self.value)
		s +="\n"+off+"}\n"
		
		return s

	def findByName(self, needle, l):
		
		if self.count:
			for n in self.value:
				n.findByName(needle, l)
		
		if self.name == needle:
			l.append(self)


class NBTParser:
	# constant
	TAG_End = 0x0
	TAG_Byte = 0x1
	TAG_Short = 0x2
	TAG_Int = 0x3
	TAG_Long = 0x4
	TAG_Float = 0x5
	TAG_Double = 0x6
	TAG_Byte_Array = 0x7
	TAG_String = 0x8
	TAG_List = 0x9
	TAG_Compound = 0xA
	
	# translation
	trans = {
		TAG_Byte: ">b",
		TAG_Short: ">h",
		TAG_Int: ">i",
		TAG_Long: ">q",
		TAG_Float: ">f",
		TAG_Double: ">d",
	}
	
	# length
	lgt = {
		TAG_Byte: 1,
		TAG_Short: 2,
		TAG_Int: 4,
		TAG_Long: 8,
		TAG_Float: 4,
		TAG_Double: 8,
	}
	
	# named contexts
	namedContext = [
		TAG_Compound
	]
	
	# members
	fd = None
	root = None
	context_stack = []
	tree = []
	linear_data = []

	def __init__(self, filename):		
		self.fd = gzip.open(filename)
	
	def parse(self):
		_type = self.readType()
		
		if _type != self.TAG_Compound:
			print "Error : Start Byte should be a TAG_Compound"
			return -1
		
		self.root = NBTNode()
		self.root.name = self.readName()
		self.context_stack.append(self.root)
		self.processCompound(self.root)
		
		
	def processCompound(self, context):
		context.type = self.TAG_Compound
		context.value = []
		context.count = True
		#processing
		_type = self.readType()
		while _type != self.TAG_End:
			_name = self.readName()
			node = NBTNode()
			node.name = _name
			node.type = _type
			node.parent = context
			#print "Will process type: "+str(node.type)
			#print "   name: "+node.name
			p = self.processPayload(node)
			#print "   value: "+str(p.value)
			context.value.append(p)
			_type = self.readType()
				
	def processList(self, context):
		context.value = []
		t = self.readType()
		
		n = self.readValue(self.TAG_Int)
		#print "list of "+str(t)+ "(x"+str(n)+")"
		context.count = True
		for i in range(n):
			node = NBTNode()
			node.type = t
			node.parent = context
			p = self.processPayload(node)
			context.value.append(p)
			
			
	def processPayload(self, context):
		
		t = context.type
		if t == self.TAG_Compound:
			self.processCompound(context)
		elif t == self.TAG_List:
			self.processList(context)
		elif t == self.TAG_Byte_Array:
			context.value = self.readString()
			context.count = False
		elif t == self.TAG_String:
			context.value = self.readString()
			context.count = False
		else:
			context.count = False
			context.value = self.readValue(t)

		return context
		
	def readName(self):
		res = self.readString()
		if res :
			return res
		else:
			return "_Unnamed_"
		
	def readString(self):
		l = self.readValue(self.TAG_Short)
		if l > 0:
			return self.fd.read(l)
		return None
		

	def readType(self):
		return ord(self.fd.read(1))


	def readValue(self, tagType):
		if tagType in self.trans:
			frmt = self.trans[tagType]
			s = self.fd.read(self.lgt[tagType])
			return struct.unpack(frmt, s)[0]
			
		return None
