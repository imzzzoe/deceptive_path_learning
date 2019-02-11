# qlearningAgents.py
# ------------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from game import *
from learningAgents import ReinforcementAgent
from featureExtractors import *

import random,util,math

class QLearningAgent(ReinforcementAgent):
  """
    Q-Learning Agent

    Functions you should fill in:
      - getQValue
      - getAction
      - getValue
      - getPolicy
      - update

    Instance variables you have access to
      - self.epsilon (exploration prob)
      - self.alpha (learning rate)
      - self.discount (discount rate)

    Functions you should use
      - self.getLegalActions(state)
        which returns legal actions
        for a state
  """
  def __init__(self, **args):
    "You can initialize Q-values here..."
    ReinforcementAgent.__init__(self, **args)

    # Q table
    self.qValues = util.Counter()
    print "ALPHA", self.alpha
    print "DISCOUNT", self.discount
    print "EXPLORATION", self.epsilon

  def getQValue(self, state, action):
    """
      Returns Q(state,action)
      Should return 0.0 if we never seen
      a state or (state,action) tuple
    """
    "*** YOUR CODE HERE ***"
    return self.qValues[(state, action)]


  def getValue(self, state):
    """
      Returns max_action Q(state,action)
      where the max is over legal actions.  Note that if
      there are no legal actions, which is the case at the
      terminal state, you should return a value of 0.0.
    """
    possibleStateQValues = util.Counter()
    for action in self.getLegalActions(state):
    	possibleStateQValues[action] = self.getQValue(state, action)
    return possibleStateQValues[possibleStateQValues.argMax()]

  def getObserverValue(self, state):
    possibleStateQValues = util.Counter()
    for action in state.getFood().asList():
      possibleStateQValues[action] = self.getObserverQValue(state, action)
    return possibleStateQValues[possibleStateQValues.argMax()]

  def getPolicy(self, state):
    """
      Compute the best action to take in a state.  Note that if there
      are no legal actions, which is the case at the terminal state,
      you should return None.
    """
    possibleStateQValues = util.Counter()
    possibleActions = self.getLegalActions(state)
    choosedAction = None
    if len(possibleActions) == 0:
    	return choosedAction

    for action in possibleActions:
      possibleStateQValues[action] = self.getQValue(state, action)
    # if state.getPacmanPosition() == (1, 1) or state.getPacmanPosition() == (2, 1):
      # print "Q values for each action in (%s,%s)" % (state.getPacmanPosition()[0], state.getPacmanPosition()[1])
      # print possibleStateQValues

    if possibleStateQValues.totalCount() == 0:
      choosedAction = random.choice(possibleActions)
    else:
      choosedAction = possibleStateQValues.argMax()
    return choosedAction

  def getObserverPolicy(self, state):
    """
    Compute the best prediction to take in a state.
    :param state:
    :return:
    """
    possibleStateQValues = util.Counter()
    possibleActions = state.getFood().asList()
    if len(possibleActions) == 0:
      return None

    for (x, y) in possibleActions:
      possibleStateQValues[(x, y)] = self.getObserverQValue(state, (x, y))
    # print "(%s,%s) Q values:" % (state.getPacmanPosition()[0], state.getPacmanPosition()[1])
    # print possibleStateQValues
    if possibleStateQValues.totalCount() == 0:
      return random.choice(possibleActions)
    else:
      return possibleStateQValues.argMax()

  def getAction(self, state):
    """
      Compute the action to take in the current state.  With
      probability self.epsilon, we should take a random action and
      take the best policy action otherwise.  Note that if there are
      no legal actions, which is the case at the terminal state, you
      should choose None as the action.

      HINT: You might want to use util.flipCoin(prob)
      HINT: To pick randomly from a list, use random.choice(list)
    """
    # Pick Action
    legalActions = self.getLegalActions(state)
    action = None
    "*** YOUR CODE HERE ***"
    if len(legalActions) > 0:
    	if util.flipCoin(self.epsilon):
    	  action = random.choice(legalActions)
        else:
			action = self.getPolicy(state)

    return action

  def getObserverAction(self, state):
    """
    Pick one of the possible goal as based on the Q value of the state
    :param state:
    :return: predict a possible goal by the policy
    """
    # Pick Action
    possibleGoals = state.getFood().asList()
    action = []
    if len(possibleGoals) > 0:
      if util.flipCoin(self.epsilon):
        action.append(random.choice(possibleGoals))
      else:
        action.append(self.getObserverPolicy(state))
    return action[0]

  def update(self, state, action, nextState, reward):
    """
      The parent class calls this to observe a
      state = action => nextState and reward transition.
      You should do your Q-Value update here

      NOTE: You should never call this function,
      it will be called on your behalf
    """
    # print "State: ", state, " , Action: ", action, " , NextState: ", nextState, " , Reward: ", reward
    print "QVALUE", self.getQValue(state, action)
    print "VALUE", self.getValue(nextState)
    self.qValues[(state, action)] = self.getQValue(state, action) + self.alpha * (reward + self.discount * self.getValue(nextState) - self.getQValue(state, action))

class PacmanQAgent(QLearningAgent):
  "Exactly the same as QLearningAgent, but with different default parameters"

  def __init__(self, epsilon=0.1,gamma=0.8,alpha=0.2, numTraining=0, **args):
    """
    These default parameters can be changed from the pacman.py command line.
    For example, to change the exploration rate, try:
        python pacman.py -p PacmanQLearningAgent -a epsilon=0.1

    alpha    - learning rate
    epsilon  - exploration rate
    gamma    - discount factor
    numTraining - number of training episodes, i.e. no learning after these many episodes
    """
    args['epsilon'] = epsilon
    args['gamma'] = gamma
    args['alpha'] = alpha
    args['numTraining'] = numTraining
    self.index = 0  # This is always Pacman
    QLearningAgent.__init__(self, **args)


  def getAction(self, state):
    """
    Simply calls the getAction method of QLearningAgent and then
    informs parent of action for Pacman.  Do not change or remove this
    method.
    """
    action = QLearningAgent.getAction(self,state)
    self.doAction(state,action)
    return action


class ApproximateQAgent(PacmanQAgent):
  """
     ApproximateQLearningAgent

     You should only have to overwrite getQValue
     and update.  All other QLearningAgent functions
     should work as is.
  """
  # DeceptivePlanerExtractor
  # IdentityExtractor
  def __init__(self, extractor='DeceptivePlannerExtractor', **args):
    self.featExtractor = util.lookup(extractor, globals())()
    PacmanQAgent.__init__(self, **args)
    # weight of agent
    self.weights = util.Counter()
    # weight of observer
    self.observerWeight = util.Counter()
    self.stateStack = []

  def getQValue(self, state, action):
    """
      Should return Q(state,action) = w * featureVector
      where * is the dotProduct operator
    """
    qValue = 0.0
    features = self.featExtractor.getFeatures(state, action)
    for key in features.keys():
    	qValue += (self.weights[key] * features[key])
    return qValue

  def getObserverQValue(self, state, action):
    """
      Should return the Q of observer's prediction at each state
      Q(state,action) = w * featureVector
      feature vectors are the path completion respect to each possible goal
      where * is the dotProduct operator
    """
    observersFeatures = self.featExtractor.getObserverFeatures(state, action)
    # TODO considering only to fetch the feature which is predicted by the observer
    # qValue = (self.observerWeight[action] * observersFeatures[action])
    qValue = 0.0
    for key in observersFeatures.keys():
      qValue += self.observerWeight[(state, key)] * observersFeatures[key]
    return qValue

  def update(self, state, action, nextState, reward):
    """
       Should update weights based on transition
       the reward is passed in by interacting with the environment: learingAgents.py line 200
    """
    # update observer's weight
    # print "===============start================="
    if state not in self.stateStack:
      self.stateStack.append(state)

    #####################################################################################
    # observerAction = self.getObserverAction(state)
    # # observer takes action and rewarded
    # observerReward = self.observerDoAction(state, observerAction)
    # # observer gets features
    # observerFeatures = self.featExtractor.getObserverFeatures(state, observerAction)
    # state.getPacmanPosition() != state.getTrueGoal() or
    self.featExtractor.calculateHeatMap(nextState)
    # print "nextState(%s,%s) == TrueGoal(%s,%s)" % (nextState.getPacmanPosition()[0], nextState.getPacmanPosition()[1], state.getTrueGoal()[0], state.getTrueGoal()[1])
    # print observerFeatures
    # if not nextState.getPacmanPosition() == state.getTrueGoal():
    #   # observerReward = state.getObserverReward()
    #   if observerReward != 0:
    #     print "current pos (%s, %s), observer reward:%f" % (state.getPacmanPosition()[0], state.getPacmanPosition()[1], observerReward)
    #   # observer update weights
    #   for key in observerFeatures.keys():
    #     # key is the action, and the state is implicitly contain in the feature(path completion is calculated by position)
    #     # print "feature[%s], reward: %f, V(s',a'): %f, Q(s,a): %f, f(s,a): %f" % (key, observerReward,self.getObserverValue(nextState),self.getObserverQValue(state, observerAction),observerFeatures[key])
    #     self.observerWeight[(state, key)] += self.alpha * (
    #             observerReward + self.discount * self.getObserverValue(nextState) - self.getObserverQValue(state, observerAction)) * observerFeatures[key]
    #####################################################################################

    features = self.featExtractor.getFeatures(state, action)
    # update reward of agent respect to the reward of observer
    # calculate reward according to probability
    scaleCons = 1
    observerReward = self.transformProb2Value(nextState)
    reward += (scaleCons * observerReward)
    # print "reward:", reward
    for key in features.keys():
      self.weights[key] += self.alpha * (
                reward + self.discount * self.getValue(nextState) - self.getQValue(state, action)) * features[key]
    # print "===============end================="

  def transformProb2Value(self, state):
    '''
    Calculate additional reward based on the probabilities by Gaussian distribution
    diffProb = min difference of (dummy goal probability - true goal probability)
    if diffProb = 0: reward is maximum
    if diffProb > 0: reward > 0
    if diffProb < 0: reward < 0
    '''
    value = 0.0
    if state.getTrueGoal() not in state.getFood().asList():
      return value
    probOfTrueGoal = state.data.statePossibility[state.getTrueGoal()]
    probDiffOfDummyGoals = {key:prob - probOfTrueGoal for key, prob in state.data.statePossibility.items()
                        if key != state.getTrueGoal()}
    # if all dummy goals are ate, retween 0
    if len(probDiffOfDummyGoals) == 0:
      return value

    diffProb = min(probDiffOfDummyGoals.values())
    variance = 0.2
    miu = 0
    value = 1 / (variance * math.sqrt(math.pi * 2)) * math.exp(-1 * (diffProb-miu)**2 / 2 * variance)
    # if diffProb < miu:
    #   return value * (-1)
    # else:
    #   return value
    return value

  def observerDoAction(self, state, observerAction):
    '''
    if observer predict correctly, get positive reward,
    else get negative reward
    '''
    print "ob (%s,%s) ? (%s, %s)" % (observerAction[0], observerAction[1], state.getTrueGoal()[0], state.getTrueGoal()[1])
    if observerAction == state.getTrueGoal():
      reward = 50.0
    else:
      reward = -10.0
    return reward

  def final(self, state):
    "Called at the end of each game."
    # call the super-class final method
    PacmanQAgent.final(self, state)
    # did we finish training?
    if self.episodesSoFar == self.numTraining:
      # you might want to print your weights here for debugging
      print "--TRAINING VARIABLES--"
      print state.data.__dict__
      print self.weights
      for state in self.stateStack:
        print "state: (%s, %s)" % (state.getPacmanPosition()[0], state.getPacmanPosition()[1])
        for action in self.getLegalActions(state):
          print "action: %s, Qvalue: %f" % (action, self.getQValue(state, action))
      pass

    for state in self.stateStack:
      print "state: (%s, %s)" % (state.getPacmanPosition()[0], state.getPacmanPosition()[1])
      for action in self.getLegalActions(state):
        print "%s: %f" % (action, self.getQValue(state, action))
      for goal in state.getFood().asList():
        print "%s: %f" % (goal, self.getObserverQValue(state, goal))
      print "\n"
