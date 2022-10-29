import networkx as nx 

from constants import *
import variables as var

from utils.developerClass import DeveloperEmpirical

class Network:
    def __init__(self, net):
        self.net = net
    
    def getNet(self):
        return self.net

    # net attribs
    def setNetAttrib(self, attribName, attribValue):
        self.net.graph[attribName] = attribValue

    def setInitialDate(self, d):
        self.net.graph[NET_INITIAL_DATE] = d

    def attribInNet(self, attribName):
        return attribName in self.net.graph

    def getNetAttrib(self, attribName):
        return self.net.graph[attribName]

    # nodes
    def addNode(self, item, type=None, otherAttribs=None):
        if item not in self.net:
            if type != None and otherAttribs != None:
                self.net.add_node(item, type=type, **otherAttribs)
            if type != None:
                self.net.add_node(item, type=type)
            else:
                self.net.add_node(item)

    def hasNode(self, item):
        return self.net.has_node(item)

    def getOrCreateDeveloper(self, devInfo):
        sDevInfo = devInfo.split(";")

        if len(sDevInfo) == 2:
            name, email, login = sDevInfo[0], sDevInfo[1], "None"
        elif len(sDevInfo) == 3:
            login, name, email = sDevInfo[0], sDevInfo[1], sDevInfo[2]

        devsPoints = {}
        for devEmpiricalInstance in self.getDeveloperNodes():
            points = 0
            if name != "None":
                if devEmpiricalInstance.getName() == name:
                    points += 1
            if email != "None":
                if devEmpiricalInstance.getEmail() == email:
                    points += 1
            if login != "None":
                if devEmpiricalInstance.getLogin() == login:
                    points += 1
            if points != 0:
                devsPoints[devEmpiricalInstance] = points

        if devsPoints == {}:
            d = DeveloperEmpirical(name, login, email)
            self.net.add_node(d, type=DEV_TYPE)
        else:
            d = max(devsPoints, key=devsPoints.get)
        
        return d

    def removeNode(self, item):
        if item in self.net.nodes():
            self.net.remove_node(item)

    def getNodes(self, getAttribs = False):
        return self.net.nodes(data=getAttribs) 

    def getFileNodes(self):
        return list(dict(filter(lambda n: n[1]["type"] == FILE_TYPE, self.net.nodes(data=True))).keys())

    def getMethodNodes(self):
        return list(dict(filter(lambda n: n[1]["type"] == METHOD_TYPE, self.net.nodes(data=True))).keys())

    def getFileNodesNotEliminated(self):
        return list(filter(lambda x: not x.startswith("ELIMINATED_"), dict(filter(lambda n: n[1]["type"] == FILE_TYPE, self.net.nodes(data=True))).keys()))

    def getDeveloperNodes(self):
        return list(dict(filter(lambda n: type(n[0]) == DeveloperEmpirical, self.net.nodes(data=True))).keys())

    def getDevNamed(self, name):
        devs = {d.name: d for d in self.getDeveloperNodes()}
        if name in devs.keys():
            return devs[name]
        else:
            return -1

    def getNodeAttributes(self, attrib):
        return dict(nx.get_node_attributes(self.net, attrib))

    def setNodeAttributes(self, attrib):
        nx.set_node_attributes(self.net, attrib)

    def relabelNodes(self, relabel, copy=False):
        nx.relabel_nodes(self.net, relabel, copy=copy)

    # edges

    def addEdgeOrWeightToNetwork(self, item1, item2, newWeight=1, types=None, weightName=ST_WEIGHT, date=None):
        net = self.getNet()

        if types != None: 
            if item1 not in net.nodes():
                net.add_node(item1, type=types[0])
            if item2 not in net.nodes():
                net.add_node(item2, type=types[1])
        else:
            if item1 not in net.nodes():
                net.add_node(item1)
            if item2 not in net.nodes():
                net.add_node(item2)

        e = (item1, item2)
        if net.get_edge_data(*e) != None:
            if weightName not in net.get_edge_data(*e):
                edgeAttributes = net.get_edge_data(*e)
                edgeAttributes[weightName] = newWeight
                nx.set_edge_attributes(net, {e: edgeAttributes})
            else:
                edgeAttributes = net.get_edge_data(*e)
                edgeAttributes[weightName] += newWeight
                if date != None:
                    edgeAttributes["commitsInfo"][date] = PLACE_HOLDER
                nx.set_edge_attributes(net, {e: edgeAttributes})
        else:
            net.add_edge(*e, **{weightName: newWeight, "commitsInfo": {date: PLACE_HOLDER}})

    def getEdgesOfNode(self, node):
        return self.net.edges(node)

    def getEdgeData(self, n1, n2, attrib):
        return self.net.get_edge_data(n1, n2)[attrib]
    
    # degree
    def getDegrees(self, nbunch=None, weight=None):
        if nbunch == None and weight == None:
            return dict(nx.degree(self.net))
        elif nbunch == None and weight != None:
            return dict(nx.degree(self.net, weight=weight))
        elif nbunch != None and weight == None:
            return dict(nx.degree(self.net, nbunch=nbunch))
        elif nbunch != None and weight != None:
            return dict(nx.degree(self.net, nbunch=nbunch, weight=weight))

    def getDegree(self, n, weight=None):
        return self.getDegrees(weight=weight)[n]

    def degreeOfNode(self, node, weight=None):
        if weight == None:
            return self.net.degree(node)
        else:
            return self.net.degree(node, weight=weight)

    def saveNet(self):
        nx.write_gpickle(self.net, self.net.graph["netPath"])

# -----

class devToDevNetworks():
    def __init__(self, fileOrMethodAnalysis, net, devToItem, save=True):
        self.fileOrMethodAnalysis = fileOrMethodAnalysis
        self.D2INet: Network = devToItem

        self.net: Network = net
        self.createAndSaveD2DNets()

        if save:
            self.net.saveNet()
    
    def createAndSaveD2DNets(self):
        if self.fileOrMethodAnalysis == FILE_TYPE:
            itemNodes = self.D2INet.getFileNodes()
        elif self.fileOrMethodAnalysis == METHOD_TYPE:
            itemNodes = self.D2INet.getMethodNodes()
        
        collaborationPerFile = {}

        for iNo in itemNodes: # item can be a file or a method.
            collaborationPerFile[iNo] = 0
            devsConnectedToItem = list(map(lambda x: x[1], self.D2INet.getEdgesOfNode(iNo)))
            for di in range(len(devsConnectedToItem)):
                d1 = devsConnectedToItem[di]
                diDates = self.D2INet.getEdgeData(d1, iNo, 'commitsInfo')
                if di + 1 != len(devsConnectedToItem):
                    for dj in range(di + 1, len(devsConnectedToItem)):
                        d2 = devsConnectedToItem[dj]

                        djDates = self.D2INet.getEdgeData(d2, iNo, 'commitsInfo')
                        numberOfCommitsInCollaborationTR = self.c_count(diDates, djDates)
                        collaborationPerFile[iNo] += numberOfCommitsInCollaborationTR
                        if numberOfCommitsInCollaborationTR != 0:
                            self.net.addEdgeOrWeightToNetwork(d1, d2, newWeight=numberOfCommitsInCollaborationTR, weightName=D2D_WEIGHT)


        n: Network = self.net

        # Saving D2I weighted degree to D2D nodes attributes
        devNodes = self.D2INet.getDeveloperNodes()
        if self.fileOrMethodAnalysis == FILE_TYPE:
            attribName = F_CHANGES_BY_DEV
        else:
            attribName = M_CHANGES_BY_DEV
        n.setNodeAttributes({k: {attribName: v} for k, v in self.D2INet.getDegrees(nbunch=devNodes, weight=ST_WEIGHT).items()})
        
        self.net.setNetAttrib(COLLAB_PER_FILE, collaborationPerFile)
    
    def c_count(self, commitsInfo1, commitsInfo2):
        maximumSecondsIntervalToConsiderCollaboration = 60 * 60 * 24 * 31 * var.MAX_MONTHS_COLLAB
        collabNr = 0
        i, j = 0, 0
        datesI, datesJ = list(commitsInfo1.keys()), list(commitsInfo2.keys())
        while (i < len(datesI) and j < len(datesJ)):
            d1 = datesI[i]
            d2 = datesJ[j]

            if abs((d2 - d1).total_seconds()) < maximumSecondsIntervalToConsiderCollaboration:
                collabNr += 1
                i += 1
                j += 1
            
            elif d1 > d2:
                j += 1
            
            elif d1 < d2:
                i += 1
        
        return collabNr