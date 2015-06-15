__author__ = 'Stefanos'
import numpy
from IPython import embed
import  xml.etree.cElementTree as ET

VERBOSE = True  
#these are the same for all users
folderName = 'data/'
momdpOutFolderName = 'data/'
policyFileName = 'TableCarryingTask.policy'
statesFileName = 'obsState.dat'
startStateTheta = 100
goal1StateTheta = 0
goal2StateTheta = 180
NUMOFSTATES = 42
NUMOFROBOTACTIONS = 2
NUMOFHUMANACTIONS = 2
NUMOFUNOBSSTATES = 5
STR_ACTIONS = ['ROTATE_CLOCKWISE', 'ROTATE_COUNTER_CLOCKWISE']
R = numpy.zeros([NUMOFSTATES,NUMOFROBOTACTIONS, NUMOFHUMANACTIONS, NUMOFSTATES])
T = numpy.zeros([NUMOFUNOBSSTATES, NUMOFSTATES, NUMOFROBOTACTIONS, NUMOFSTATES])
NUMOFALPHAVECTORS = 99
A = numpy.zeros([NUMOFALPHAVECTORS, NUMOFUNOBSSTATES + 2])
startStateIndx = NUMOFSTATES-2 #assume that the state before last is the starting one

#uninitiated globals for globalsInit()
stateNames = None

def globalsInit():
  global stateNames, R, T, A
  print "Loading state names from file"
  with open(folderName+statesFileName, 'r') as stateNamesFile:
    stateNames = numpy.asarray([ line.split(' ') for line in stateNamesFile])[0]

  print "Loading reachability matrix from file"
  for ra in range(0,NUMOFROBOTACTIONS):
    for ha in range(0,NUMOFHUMANACTIONS):
      with open(folderName + 'R' + str(ra+1)+str(ha+1)+'.dat', 'r') as reachFile:
        reachMtx = numpy.asarray([map(float, line.split('\t')) for line in reachFile])
        for ss in range(0, NUMOFSTATES):
          for nss in range(0,NUMOFSTATES):
            R[ss][ra][ha][nss] = reachMtx[ss][nss]
  print "Loading Transition Matrix from file"
  for yIndx in range(0,NUMOFUNOBSSTATES):
      for ra in range(0, NUMOFROBOTACTIONS):
        with open(folderName + 'T' + str(yIndx+1)+str(ra+1)+'.dat', 'r') as transFile:
          transMtx = numpy.asarray([map(float, line.split('\t')) for line in transFile])
          for ss in range(0, NUMOFSTATES):
            for nss in range(0, NUMOFSTATES):
              T[yIndx][ss][ra][nss] = transMtx[ss][nss]
  print "Loading XML policy file"
  tree = ET.parse(momdpOutFolderName + policyFileName)
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
    A[counter][0] = float(obsValue)
    A[counter][1] = float(action)
    for vv in range(0,NUMOFUNOBSSTATES):
      A[counter][2+vv] = float(values[vv])
    counter = counter + 1

class Data:

  def __init__(self, id):
    ##############The following variables are different per user########################
    self.bel_t = numpy.ones([5,1])*0.2
    self.currState = startStateIndx
    self.id = id  #this is a user id

  def stateUpdateFromHumanAction(self,humanAction):
    global stateNames
    robotAction = self.getRobotActionFromPolicy(self.currState, self.bel_t)
    nextState = self.getNextStateFromHumanRobotAction(self.currState,robotAction, humanAction)
    new_bel_t = self.getNewBeliefFromHumanAction(self.currState,robotAction,nextState, self.bel_t)
    self.bel_t = new_bel_t
    self.currState = nextState
    currTableTheta = self.getTableThetaFromState(self.currState)

    resultState = stateNames[self.currState]
    resultBelief = self.bel_t
    resultHAction = STR_ACTIONS[humanAction]
    resultRAction = STR_ACTIONS[robotAction]

    return (currTableTheta, resultState, resultBelief, resultHAction, resultRAction)

  def getRobotActionFromPolicy(self, ss, bel_t):
    action = -1
    maxVal = -1
    for aa in range(0, NUMOFALPHAVECTORS):
      if(A[aa][0] == ss):
        val = numpy.dot(A[aa][2:NUMOFUNOBSSTATES+2],bel_t)
        if(val > maxVal):
          maxVal = val
          action = int(A[aa][1])
    if VERBOSE:
      print "Value function is: " + str(maxVal)
      #print "Robot action is: " + self.STR_ACTIONS[action]
    return action

  def getTableThetaFromState(self, ss):
    thetaIndx = int(ss/4)
    if(thetaIndx>=0) and (thetaIndx<=18):
     return thetaIndx*20
    else:
     return startStateTheta

  def getNextStateFromHumanRobotAction(self, ss, ra, ha):
    nextStateMtx = R[ss][ra][ha][:]
    return nextStateMtx.argmax()

  def getNewBeliefFromHumanAction(self, ss, ra, nss, bel_t):
    bel_tp1 = numpy.zeros([NUMOFUNOBSSTATES,1])
    SumBeliefs = 0
    for yy in range(0, NUMOFUNOBSSTATES):
      bel_tp1[yy] = T[yy][ss][ra][nss]*bel_t[yy]
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
  print("IN:id={},action={}".format(id,humanAction))
  #retrieve/create the class instance
  if idInitiated(id,d):
    x = d[id] #dictionary
    print("Returning user: ID={}".format(id))
  else:
    x = Data(id)
    d[id] = x
    print("New class instance created: id={}".format(id))
  currTableTheta, resultState, resultBelief, resultHAction, resultRAction = \
    x.stateUpdateFromHumanAction(humanAction)
  print("OUT:theta={}".format(currTableTheta))
  return (currTableTheta, resultState, resultBelief, resultHAction, resultRAction)