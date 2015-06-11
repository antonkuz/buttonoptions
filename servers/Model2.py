__author__ = 'Stefanos'
import numpy
from IPython import embed
import  xml.etree.cElementTree as ET

VERBOSE = True

class Data:
  folderName = 'data/'
  momdpOutFolderName = 'data/'
  policyFileName = 'TableCarryingTask.policy'
  statesFileName = 'obsState.dat'

  def __init__(self, id):

    #loading data, these are the same for all users
    self.startStateTheta = 100
    self.goal1StateTheta = 0
    self.goal2StateTheta = 180
    self.NUMOFSTATES = 77
    self.NUMOFROBOTACTIONS = 2
    self.NUMOFHUMANACTIONS = 2
    self.NUMOFUNOBSSTATES = 5
    self.STR_ACTIONS = ['ROTATE_CLOCKWISE', 'ROTATE_COUNTER_CLOCKWISE']
    self.R = numpy.zeros([self.NUMOFSTATES,self.NUMOFROBOTACTIONS, self.NUMOFHUMANACTIONS, self.NUMOFSTATES])
    self.T = numpy.zeros([self.NUMOFUNOBSSTATES, self.NUMOFSTATES, self.NUMOFROBOTACTIONS, self.NUMOFSTATES])
    self.NUMOFALPHAVECTORS = 337
    self.A = numpy.zeros([self.NUMOFALPHAVECTORS, self.NUMOFUNOBSSTATES + 2])
    self.startStateIndx = self.NUMOFSTATES-1 #assume that the last state is the starting one
    ##############The following variables are different per user########################
    self.bel_t = numpy.ones([5,1])*0.2
    self.currState = self.startStateIndx
    self.id = id  #this is a user id

    print "Loading state names from file"
    with open(self.folderName+self.statesFileName, 'r') as stateNamesFile:
      self.stateNames = numpy.asarray([ line.split(' ') for line in stateNamesFile])[0]

    print "Loading reachability matrix from file"
    for ra in range(0,self.NUMOFROBOTACTIONS):
      for ha in range(0,self.NUMOFHUMANACTIONS):
        with open(self.folderName + 'R' + str(ra+1)+str(ha+1)+'.dat', 'r') as reachFile:
          reachMtx= numpy.asarray([map(float, line.split('\t')) for line in reachFile])
          for ss in range(0, self.NUMOFSTATES):
            for nss in range(0,self.NUMOFSTATES):
              self.R[ss][ra][ha][nss] = reachMtx[ss][nss]
    print "Loading Transition Matrix from file"
    for yIndx in range(0,self.NUMOFUNOBSSTATES):
        for ra in range(0, self.NUMOFROBOTACTIONS):
          with open(self.folderName + 'T' + str(yIndx+1)+str(ra+1)+'.dat', 'r') as transFile:
            transMtx = numpy.asarray([map(float, line.split('\t')) for line in transFile])
            for ss in range(0, self.NUMOFSTATES):
              for nss in range(0, self.NUMOFSTATES):
                self.T[yIndx][ss][ra][nss] = transMtx[ss][nss]
    print "Loading XML policy file"
    tree = ET.parse(self.momdpOutFolderName + self.policyFileName)
    root = tree.getroot()
    numVectors = len(root.getchildren()[0].getchildren())
    print numVectors
    print root.iter('Vector')
    counter = 0
    for vector in root.iter('Vector'):
      obsValue  = vector.get('obsValue')
      action = vector.get('action')
      values = vector.text.split(' ')

      # vector format: obsValue, action, values
      self.A[counter][0] = float(obsValue)
      self.A[counter][1] = float(action)
      for vv in range(0,self.NUMOFUNOBSSTATES):
        self.A[counter][2+vv] = float(values[vv])
      counter = counter + 1

  def stateUpdateFromHumanAction(self,humanAction):
    robotAction = self.getRobotActionFromPolicy(self.currState, self.bel_t)
    nextState = self.getNextStateFromHumanRobotAction(self.currState,robotAction, humanAction)
    new_bel_t = self.getNewBeliefFromHumanAction(self.currState,robotAction,nextState, self.bel_t)
    self.bel_t = new_bel_t
    self.currState = nextState
    currTableTheta = self.getTableThetaFromState(self.currState)

    resultState = self.stateNames[self.currState]
    resultBelief = self.bel_t
    resultHAction = self.STR_ACTIONS[humanAction]
    resultRAction = self.STR_ACTIONS[robotAction]

    return (currTableTheta, resultState, resultBelief, resultHAction, resultRAction)

  def getRobotActionFromPolicy(self, ss, bel_t):
    action = -1
    maxVal = -1
    for aa in range(0, self.NUMOFALPHAVECTORS):
      if(self.A[aa][0] == ss):
        val = numpy.dot(self.A[aa][2:self.NUMOFUNOBSSTATES+2],bel_t)
        if(val > maxVal):
          maxVal = val
          action = int(self.A[aa][1])
    if VERBOSE:
      print "Value function is: " + str(maxVal)
      #print "Robot action is: " + self.STR_ACTIONS[action]
    return action

  def getTableThetaFromState(self, ss):
    thetaIndx = int(ss/4)
    if(thetaIndx>=0) and (thetaIndx<=18):
     return thetaIndx*10
    else:
     return self.startStateTheta

  def getNextStateFromHumanRobotAction(self, ss, ra, ha):
    nextStateMtx = self.R[ss][ra][ha][:]
    return nextStateMtx.argmax()

  def getNewBeliefFromHumanAction(self, ss, ra, nss, bel_t):
    bel_tp1 = numpy.zeros([self.NUMOFUNOBSSTATES,1])
    SumBeliefs = 0
    for yy in range(0, self.NUMOFUNOBSSTATES):
      bel_tp1[yy] = self.T[yy][ss][ra][nss]*bel_t[yy]
      SumBeliefs = SumBeliefs + bel_tp1[yy]
    bel_tp1 = bel_tp1 / SumBeliefs
    return bel_tp1

def idInitiated(id,d):
  if id in d:
    return True
  else:
    return False

#the server will call this function passing the id and the button pressed
#we'll store the class instances in a dictionary with IDs as keys
#idInitiated helper function checks if id is in the dictionary
def getMove(d,id,humanAction):
  #print("IN:id={},action={}".format(id,humanAction))
  #retrieve/create the class instance
  if idInitiated(id,d):
    x = d[id] #dictionary
  else:
    x = Data(id)
    d[id] = x
  currTableTheta, resultState, resultBelief, resultHAction, resultRAction = \
    x.stateUpdateFromHumanAction(humanAction)
  #print("OUT:theta={}".format(currTableTheta))
  if currTableTheta==x.goal1StateTheta or currTableTheta==x.goal2StateTheta:
    return (42,42,42,42,42) #server knows this is game over
  else:
    return (currTableTheta, resultState, resultBelief, resultHAction, resultRAction)

# x = Data(1)
# currTableTheta = x.startStateTheta
# while (currTableTheta!=x.goal1StateTheta) and (currTableTheta!=x.goal2StateTheta):
#   print "The table rotation angle is: " + str(currTableTheta) + " degrees. "
#   try:
#       humanAction = input('Enter human action [0 for ROTATE_CLOCKWISE, 1 for ROTATE_COUNTER_CLOCKWISE]: ')
#   except Exception as e:
#      print 'Exception: wrong input. '
#      continue
#   currTableTheta = x.stateUpdateFromHumanAction(humanAction)

# print 'Goal state reached. '