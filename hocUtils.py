import os, itertools
import networkx as nx

class RinkGraph(object):
    """Base class for a graph of nodes representing a hockey rink. Description of nodes found in design documents."""
    G = nx.empty_graph()
    
    def __init__(self, nodeFilename:str=None, edgeFilename:str=None):
        if nodeFilename is not None:
            with open(os.path.join("Rinks","Graphs",nodeFilename)) as nodeFile:
                nodeListS = [node.strip() for node in nodeFile.readlines()]
                self.G = nx.empty_graph(create_using=nx.DiGraph)
                edges = itertools.permutations(nodeListS,2)
                self.G.add_edges_from(edges)
        elif edgeFilename is not None:
            self.G = nx.readwrite.edgelist.read_edgelist(os.path.join("Rinks","Graphs", edgeFilename), create_using=nx.DiGraph)

    def writeGraph(self, writeFilename:str):
        nx.readwrite.edgelist.write_edgelist(self.G, os.path.join("Rinks","Graphs",writeFilename))

    def nameToZones(self, name:str):
        column = int(name[1])
        row = int(name[0])

    def adjacencyRule(self):
        for node1, node2 in list(self.G.edges):
            self.G.edges[node1, node2]['actions'] = []
            if (abs(int(node1[0]) - int(node2[0])) <= 1 and abs(int(node1[1]) - int(node2[1])) <= 0) or (abs(int(node1[0]) - int(node2[0])) <= 0 and abs(int(node1[1]) - int(node2[1])) <= 1):
                self.G.edges[node1, node2]['adjacent'] = 1
            elif node1 == "01" and node2 == "10" or node1 == "10" and node2 == "01" or node1 == "06" and node2 == "17" or node1 == "17" and node2 == "06":
                self.G.edges[node1, node2]['adjacent'] = 1
            elif node1 == "41" and node2 == "30" or node1 == "30" and node2 == "41" or node1 == "46" and node2 == "37" or node1 == "37" and node2 == "46":
                self.G.edges[node1, node2]['adjacent'] = 1
            else:
                self.G.edges[node1, node2]['adjacent'] = 0

    def backSkateRule(self):
        for node1, node2 in list(self.G.edges):
            if node1[1] in ['1','2','3','4','6']:
                if abs(int(node1[0]) - int(node2[0])) <= 1 and int(node2[1]) == int(node1[1])-1:
                    self.G.edges[node1, node2]['actions'].append('SkateB')

    def forwardSkateRule(self):
        for node1, node2 in list(self.G.edges):
            access = False
            if node1[1] in ['0','1','2']:
                access = True
                distance = 2
            elif node1[1] in ['3','4']:
                access = True
                distance = 1
            
            if access and node2[1] >= node1[1]:
                atkDistance = int(node2[1]) - int(node1[1])
                horzDistance = abs(int(node2[0]) - int(node1[0]))
                if (atkDistance+horzDistance) <= distance:
                    self.G.edges[node1, node2]['actions'].append('SkateF')

    def throughSkateRule(self):
        for node1, node2 in list(self.G.edges):
            if node1[1] in ['5','6','7']:
                if node1[0] not in ['0','4']:
                    if node2 == '26':
                        self.G.edges[node1, node2]['actions'].append('SkateT')
                else:
                    if node1[0] == '0' and node2 == '16' or node1[0] == '4' and node2 == '36':
                        self.G.edges[node1, node2]['actions'].append('SkateT')

    def aroundSkateRule(self):
        for node1, node2 in list(self.G.edges):
            if node1[1] in ['5','6'] and node1[0] != '2' and node2 == '27':
                self.appendAction(node1, node2, 'SkateA')

    def stretchPassRule(self):
        for node1, node2 in list(self.G.edges):
            if node1[1] in ['1','2'] and node2[1] == '5':
                self.appendAction(node1, node2, "PassS")

    def forwardPassRule(self):
        for node1, node2 in list(self.G.edges):
            if node1[1] in ['1','2', '3', '5', '6']:
                if int(node2[1]) >= int(node1[1]) and int(node2[1]) - int(node1[1]) <= 2:
                    self.appendAction(node1, node2, 'PassF')
            elif node1[1] == '4' and node2[1] in ['4','5']:
                self.appendAction(node1, node2, 'PassF')
            elif node1[1] == '7' and node2[1] in ['5','6']:
                self.appendAction(node1, node2, 'PassF')

    def backwardPassRule(self):
        for node1, node2 in list(self.G.edges):
            if node1[1] not in ['0','5','7']: #back pass from column 7 is treated as forward pass for difficulty
                if int(node1[1]) - int(node2[1]) == 1 and node1[0] == node2[0]:
                    self.appendAction(node1, node2, 'PassB')


    def appendAction(self, node1, node2, actionString):
        self.G.edges[node1, node2]['actions'].append(actionString)
            

    def allRules(self):
        self.adjacencyRule()
        self.backSkateRule()
        self.forwardSkateRule()
        self.throughSkateRule()
        self.aroundSkateRule()
        self.stretchPassRule()
        self.forwardPassRule()
        self.backwardPassRule()
        self.writeGraph("defaultedges.nx")

    def getAllReachableFrom(self, nodeName):
        """Returns a dictionary where the keys are all reachable nodes, and the values are the list of actions that can reach the key node."""
        if isinstance(nodeName, int):
            nodeName = str(nodeName)
        allConnected = dict(self.G[nodeName])
        possibleReachable = {}
        for otherNode in allConnected:
            if allConnected[otherNode]['actions'] != []:
                possibleReachable[otherNode] = allConnected[otherNode]['actions']
        return possibleReachable

    def getAdjacentNodes(self, nodeName):
        """Returns a list of all nodes marked as adjacent by the current map."""
        if isinstance(nodeName, int):
            nodeName = str(nodeName)
        allConnected = dict(self.G[nodeName])
        adjacents = []
        for otherNodeName, nodeDic in allConnected.items():
            if nodeDic['adjacent']:
                adjacents.append(otherNodeName)
        return adjacents