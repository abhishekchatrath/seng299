from Parser import Parser



def test():
	temp = Parser()
	
	tempString = temp.assemble(100, "CoolGroup", "CoolKid", "12:54:16", "Fuck This")
	
	temp.breakdown(tempString)
	
test()

