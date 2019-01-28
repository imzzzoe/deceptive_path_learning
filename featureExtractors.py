# featureExtractors.py
# --------------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

"Feature extractors for Pacman game states"

from game import Directions, Actions
import util

class FeatureExtractor:
  def getFeatures(self, state, action):
    """
      Returns a dict from features to counts
      Usually, the count will just be 1.0 for
      indicator functions.  
    """
    util.raiseNotDefined()

class IdentityExtractor(FeatureExtractor):
  def getFeatures(self, state, action):
    feats = util.Counter()
    feats[(state,action)] = 1.0
    return feats

def closestFood(pos, food, walls):
  """
  closestFood -- this is similar to the function that we have
  worked on in the search project; here its all in one place
  """
  fringe = [(pos[0], pos[1], 0)]
  expanded = set()
  while fringe:
    pos_x, pos_y, dist = fringe.pop(0)
    if (pos_x, pos_y) in expanded:
      continue
    expanded.add((pos_x, pos_y))
    # if we find a food at this location then exit
    if food[pos_x][pos_y]:
      return dist
    # otherwise spread out from the location to its neighbours
    nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
    for nbr_x, nbr_y in nbrs:
      fringe.append((nbr_x, nbr_y, dist+1))
  # no food found
  return None

def distanceToNearest(pos, targetType, walls):
  """
  Returns distance to the nearest item of the specified type (e.g. food, Power Capsule)
  """
  # Open-list nodes consist of position x,y and distance (initialised at 0)
  fringe = [(pos[0], pos[1], 0)]

  # Closed list as a set (unordered list of unique elements)
  expanded = set()

  while fringe:
    # Pop latest node from open list, and add to closed list
    pos_x, pos_y, dist = fringe.pop(0)
    if (pos_x, pos_y) in expanded:
      continue
    expanded.add((pos_x, pos_y))
    # Exit if the target item already exists at this location
    if pos_x == targetType[0] and pos_y == targetType[1]:
      return dist
    # Otherwise, investigate neighbouring nodes and add them to the open list
    nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
    for nbr_x, nbr_y in nbrs:
      fringe.append((nbr_x, nbr_y, dist+1))

  # If target item not found
  return None


class SimpleExtractor(FeatureExtractor):
  """
  Returns simple features for a basic reflex Pacman:
  - whether food will be eaten
  - how far away the next food is
  - whether a ghost collision is imminent
  - whether a ghost is one step away
  """

  def getFeatures(self, state, action):
    # extract the grid of food and wall locations and get the ghost locations
    food = state.getFood()
    walls = state.getWalls()
    ghosts = state.getGhostPositions()

    features = util.Counter()

    features["bias"] = 1.0

    # compute the location of pacman after he takes the action
    x, y = state.getPacmanPosition()
    dx, dy = Actions.directionToVector(action)
    next_x, next_y = int(x + dx), int(y + dy)

    # count the number of ghosts 1-step away
    features["#-of-ghosts-1-step-away"] = sum((next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in ghosts)

    # if there is no danger of ghosts then add the food feature
    if not features["#-of-ghosts-1-step-away"] and food[next_x][next_y]:
      features["eats-food"] = 1.0

    dist = closestFood((next_x, next_y), food, walls)
    if dist is not None:
      # make the distance a number less than one otherwise the update
      # will diverge wildly
      features["closest-food"] = float(dist) / (walls.width * walls.height)
    features.divideAll(10.0)
    return features


class DeceptivePlannerExtractor(FeatureExtractor):
  """
  Returns features for an agent that seeks one of several candidate goals while aiming to hide its intention:
  - Distance to the last deceptive point (LDP), while it has not been reached
  - Distance to the intended goal, once the LDP has been reached
  """

  def getFeatures(self, state, action):
    # Extract the grid of wall locations and initialise the counter of features
    walls = state.getWalls()
    features = util.Counter()

    # Compute the location of pacman after he takes the next action
    x, y = state.getPacmanPosition()
    dx, dy = Actions.directionToVector(action)
    next_x, next_y = int(x + dx), int(y + dy)

    # First feature guides the agent to the last deceptive point (LDP)
    if not state.reachedLdp():
      dist = distanceToNearest((next_x, next_y), state.getLdp(), walls)
      features["LDP-distance"] = float(dist) / (walls.width * walls.height)

    # Once the LDP has been reached, switch to the second feature, which guides agent to the goal
    else:
      trueGoal = state.getTrueGoal()
      dist = distanceToNearest((next_x, next_y), trueGoal, walls)
      features["goal-distance"] = float(dist) / (walls.width * walls.height)

    # Divide values in order to prevent unstable divergence
    features.divideAll(10.0)

    return features

  def getObserverFeatures(self, state, action):
    # Extract the grid of wall locations and initialise the counter of features
    walls = state.getWalls()
    observerFeatures = util.Counter()

    # Compute the location of pacman after he takes the next action
    x, y = state.getPacmanPosition()
    dx, dy = Actions.directionToVector(action)
    next_x, next_y = int(x + dx), int(y + dy)

    foodList = state.data.food.asList()
    for food in foodList:
      print 'goal:', food
      dist = distanceToNearest((next_x, next_y), food, walls)
      observerFeatures[food] = 1.0

    # Divide values in order to prevent unstable divergence
    observerFeatures.divideAll(10.0)

    return observerFeatures