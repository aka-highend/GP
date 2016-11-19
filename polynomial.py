from random import random, randint, choice
from copy import deepcopy
from PIL import Image, ImageDraw

class polynomial:
  def __init__(self, function, childcount, name):
    self.function = function
    self.childcount = childcount
    self.name = name

class variable:
  def __init__(self, var, value=0):
    self.var = var
    self.value = value
    self.name = str(var)
    self.type = "variable"  

  def evaluate(self):
    return self.varvalue

  def setvar(self, value):
    self.value = value

  def display(self, indent=0):
    print '%s%s' % (' '*indent, self.var)

class const:
  def __init__(self, value):
    self.value = value
    self.name = str(value)
    self.type = "constant"   

  def evaluate(self):
    return self.value

  def display(self, indent=0):
    print '%s%d' % (' '*indent, self.value) 

class node:
  def __init__(self, type, children, funwrap, var=None, const=None):
    self.type = type
    self.children = children
    self.funwrap = funwrap
    self.variable = var
    self.const = const
    self.depth = self.refreshdepth()
    self.value = 0
    self.fitness = 0

  def eval(self):
    if self.type == "variable":
      return self.variable.value
    elif self.type == "constant":
      return self.const.value
    else:
      for c in self.children:
        result = [c.eval() for c in self.children]
      return self.funwrap.function(result)  

  def getfitness(self, checkdata):#checkdata like {"x":1,"result":3"}
    diff = 0
    #set variable value
    for data in checkdata:
      self.setvariablevalue(data)
      diff += abs(self.eval() - data["result"])
    self.fitness = diff      

  def setvariablevalue(self, value):
    if self.type == "variable":
      if value.has_key(self.variable.var):
        self.variable.setvar(value[self.variable.var])
      else:
        print "There is no value for variable:", self.variable.var
        return
    if self.type == "constant":
      pass
    if self.children:#function node
      for child in self.children:
        child.setvariablevalue(value)            

  def refreshdepth(self):
    if self.type == "constant" or self.type == "variable":
      return 0
    else:
      depth = []
      for c in self.children:
        depth.append(c.refreshdepth())
      return max(depth) + 1

  def __cmp__(self, other):
        return cmp(self.fitness, other.fitness)  

  def display(self, indent=0):
    if self.type == "function":
      print ('  '*indent) + self.funwrap.name
    elif self.type == "variable":
      print ('  '*indent) + self.variable.name
    elif self.type == "constant":
      print ('  '*indent) + self.const.name
    if self.children:
      for c in self.children:
        c.display(indent + 1)
  ##for draw node
  def getwidth(self):
    if self.type == "variable" or self.type == "constant":
      return 1
    else:
      result = 0
      for i in range(0, len(self.children)):
        result += self.children[i].getwidth()
      return result
  def drawnode(self, draw, x, y):
    if self.type == "function":
      allwidth = 0
      for c in self.children:
        allwidth += c.getwidth()*100
      left = x - allwidth / 2
      #draw the function name
      draw.text((x - 10, y - 10), self.funwrap.name, (0, 0, 0))
      #draw the children
      for c in self.children:
        wide = c.getwidth()*100
        draw.line((x, y, left + wide / 2, y + 100), fill=(255, 0, 0))
        c.drawnode(draw, left + wide / 2, y + 100)
        left = left + wide
    elif self.type == "variable":
      draw.text((x - 5 , y), self.variable.name, (0, 0, 0))
    elif self.type == "constant":
      draw.text((x - 5 , y), self.const.name, (0, 0, 0))

  def drawtree(self, jpeg="tree.png"):
    w = self.getwidth()*100
    h = self.depth * 100 + 120

    img = Image.new('RGB', (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    self.drawnode(draw, w / 2, 20)
    img.save(jpeg, 'PNG')

class enviroment:
  def __init__(self, funwraplist, variablelist, constantlist, checkdata, \
               minimaxtype="min", population=None, size=10, maxdepth=10, \
               maxgen=100, crossrate=0.9, mutationrate=0.1, newbirthrate=0.6):
    self.funwraplist = funwraplist
    self.variablelist = variablelist
    self.constantlist = constantlist
    self.checkdata = checkdata
    self.minimaxtype = minimaxtype
    self.maxdepth = maxdepth
    self.population = population or self._makepopulation(size)
    self.size = size
    self.maxgen = maxgen
    self.crossrate = crossrate
    self.mutationrate = mutationrate
    self.newbirthrate = newbirthrate

    self.besttree = self.population[0]
    for i in range(0, self.size):
      self.population[i].depth=self.population[i].refreshdepth()
      self.population[i].getfitness(checkdata)
      if self.minimaxtype == "min":
        if self.population[i].fitness < self.besttree.fitness:
          self.besttree = self.population[i]
      elif self.minimaxtype == "max":
        if self.population[i].fitness > self.besttree.fitness:
          self.besttree = self.population[i]    

  def _makepopulation(self, popsize):
    return [self._maketree(0) for i in range(0, popsize)]     

  def _maketree(self, startdepth):
    if startdepth == 0:
      #make a new tree
      nodepattern = 0#function
    elif startdepth == self.maxdepth:
      nodepattern = 1#variable or constant
    else:
      nodepattern = randint(0, 1)
    if nodepattern == 0:
      childlist = []
      selectedfun = randint(0, len(self.funwraplist) - 1)
      for i in range(0, self.funwraplist[selectedfun].childcount):
        child = self._maketree(startdepth + 1)
        childlist.append(child)
      return node("function", childlist, self.funwraplist[selectedfun])
    else:
      if randint(0, 1) == 0:#variable
        selectedvariable = randint(0, len(self.variablelist) - 1)
        return node("variable", None, None, \
               variable(self.variablelist[selectedvariable]), None)
      else:
        selectedconstant = randint(0, len(self.constantlist) - 1)
        return node("constant", None, None, None,\
               const(self.constantlist[selectedconstant]))

  def mutate(self, tree, probchange=0.1, startdepth=0):
    if random() < probchange:
      return self._maketree(startdepth)
    else:
      result = deepcopy(tree)
      if result.type == "function":
        result.children = [self.mutate(c, probchange, startdepth + 1) \
                           for c in tree.children]
    return result

  def crossover(self, tree1, tree2, probswap=0.8, top=1):
    if random() < probswap and not top:
      return deepcopy(tree2)
    else:
      result = deepcopy(tree1)
      if tree1.type == "function" and tree2.type == "function":
        result.children = [self.crossover(c, choice(tree2.children), \
                           probswap, 0) for c in tree1.children]
    return result

  def envolve(self, maxgen=100, crossrate=0.9, mutationrate=0.1):
    for i in range(0, maxgen):
      print "generation no.", i
      child = []
      for j in range(0, int(self.size * self.newbirthrate / 2)):
        parent1, p1 = self.roulettewheelsel()
        parent2, p2 = self.roulettewheelsel()
        newchild = self.crossover(parent1, parent2)
        child.append(newchild)#generate new tree
        parent, p3 = self.roulettewheelsel()
        newchild = self.mutate(parent, mutationrate)
        child.append(newchild)
      #refresh all tree's fitness
      for j in range(0, int(self.size * self.newbirthrate)):
        replacedtree, replacedindex = self.roulettewheelsel(reverse=True)
        #replace bad tree with child
        self.population[replacedindex] = child[j]

      for k in range(0, self.size):
        self.population[k].getfitness(self.checkdata)
        self.population[k].depth=self.population[k].refreshdepth()
        if self.minimaxtype == "min":
          if self.population[k].fitness < self.besttree.fitness:
            self.besttree = self.population[k]
        elif self.minimaxtype == "max":
          if self.population[k].fitness > self.besttree.fitness:
            self.besttree = self.population[k]
      print "best tree's fitness..",self.besttree.fitness
    self.besttree.display()
    self.besttree.drawtree()  

  def gettoptree(self, choosebest=0.9, reverse=False):
    if self.minimaxtype == "min":
      self.population.sort()
    elif self.minimaxtype == "max":
      self.population.sort(reverse=True)  

    if reverse == False:
      if random() < choosebest:
        i = randint(0, self.size * self.newbirthrate)
        return self.population[i], i
      else:
        i = randint(self.size * self.newbirthrate, self.size - 1)
        return self.population[i], i
    else:
      if random() < choosebest:
        i = self.size - randint(0, self.size * self.newbirthrate) - 1
        return self.population[i], i
      else:
        i = self.size - randint(self.size * self.newbirthrate,\
            self.size - 1)
        return self.population[i], i

  def roulettewheelsel(self, reverse=False):
    if reverse == False:
      allfitness = 0
      for i in range(0, self.size):
        allfitness += self.population[i].fitness
      randomnum = random()*(self.size - 1)
      check = 0
      for i in range(0, self.size):
        check += (1.0 - self.population[i].fitness / allfitness)
        if check >= randomnum:
          return self.population[i], i
    if reverse == True:
      allfitness = 0
      for i in range(0, self.size):
        allfitness += self.population[i].fitness
      randomnum = random()
      check = 0
      for i in range(0, self.size):
        check += self.population[i].fitness * 1.0 / allfitness
        if check >= randomnum:
          return self.population[i], i

  def listpopulation(self):
    for i in range(0, self.size):
      self.population[i].display()   

#############################################################

def add(ValuesList):
    sumtotal = 0
    for val in ValuesList:
      sumtotal = sumtotal + val
    return sumtotal

def sub(ValuesList):
    return ValuesList[0] - ValuesList[1]

def mul(ValuesList):
    return ValuesList[0] * ValuesList[1]

def div(ValuesList):
    if ValuesList[1] == 0:
        return 1
    return ValuesList[0] / ValuesList[1]

addwrapper = polynomial(add, 2, "Add")
subwrapper = polynomial(sub, 2, "Sub")
mulwrapper = polynomial(mul, 2, "Mul")
divwrapper = polynomial(div, 2, "Div")

def examplefun(x, y):
  return x * x + x + 2 * y + 1
def constructcheckdata(count=10):
  checkdata = []
  for i in range(0, count):
    dic = {}
    x = randint(0, 10)
    y = randint(0, 10)
    dic['x'] = x
    dic['y'] = y
    dic['result'] = examplefun(x, y)
    checkdata.append(dic)
  return checkdata

if __name__ == "__main__":
  checkdata = constructcheckdata()
  print checkdata
  env = enviroment([addwrapper, subwrapper, mulwrapper], ["x", "y"],
                  [-3, -2, -1, 1, 2, 3], checkdata)
  env.envolve()