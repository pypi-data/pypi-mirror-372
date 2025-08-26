"""
This script generates a flow chart for a function from its disassembly
information.

(c) TASKING Germany GmbH, 2023


Seq  Dir  Indir  Cond  Call/Jump  |  Shape          Color
-------------------------------------------------------------
 1                0       0       | rectangle      cornsilk
 1                1       0       |  frame         cornsilk
      1           0       0       |  queue         moccasin
      1           0       1       |   node         moccasin
      1           1       0       | collections    moccasin
      1           1       1       |   file         moccasin
            1     0       0       |  queue         thistle
            1     0       1       |   node         thistle
            1     1       0       | collections    thistle
            1     1       1       |   file         thistle
"""

import sys
import collections
import subprocess as sp

import isystem.connect as ic
import isystem.diagutils as diagutils


LINK_TRUE_LBL = 'True'
LINK_FALSE_LBL = 'False'
IS_DEBUG = False
all_link_strings = []

# Key is node ID, value is the number of jumps to this node,
# including sequential execution (most nodes will have this
# value set to 1 or greater value.
g_nodeJumpNumber = collections.defaultdict(int)

g_externalNodes = set() # nodes for called functions and jumps outside function range


class Link:
    """
    Contains information for PlantUML link.
    """
    def __init__(self, sourceNodeId, destNodeId, linkLabel=''):
        self.sourceNodeId = sourceNodeId
        self.destNodeId = destNodeId
        self.linkLabel = linkLabel
        self.style = None
        self.weight = -1
        self.isConstraint = True


    def setStyle(self, style):
        """
        Parameters:
        style - one of puml link styles, for example 'invis' for invisible link
        """
        self.style = style


    def setConstraint(self, isConstraint):
        """
        Parameters:
        isConstraint - if false, this link is not used when ranking
                       nodes (placing them up to bottom)
        """
        self.isConstraint = isConstraint

    def getNodeId(self, nodeId):
        """
        Sometimes self.nodeId is n_XXXXXXXXXn_YYYYYYYYY,
        in that case it returns only n_XXXXXXXXX. If self.nodeId
        is n_XXXXXXXXX, then it returns n_XXXXXXXXX, if its something
        that doesn't contain n_, it is returned unchanged.
        """
        if "n_" in nodeId:
            return f"n_{nodeId.split("n_")[1]}"
        return nodeId

    def append(self, direction="down", dashed=False):
        """
        Appends links to a global list all_link_strings. They are not written
        in this function to ensure they are written all at once after nodes.
        """
        global all_link_strings

        arrow_sign = "-"

        if self.style == "invis" or dashed:
            arrow_sign = "." # Makes the arrow dashed

        src_node = self.getNodeId(self.sourceNodeId)
        dest_node = self.getNodeId(self.destNodeId)

        link = f"{src_node} {arrow_sign}{direction}{arrow_sign}> {dest_node}"

        if self.linkLabel:
            link +=  f" : {self.linkLabel}"

        all_link_strings.append(link)



class Node:
    """
    Contains information for PlantUML nodes.
    """

    def __init__(self, nodeId, shape, bkgColor, label,
                 style='', height='', address="", srcLine=''):
        """
        Parameters:
        label - usually object op-code of function name
        address - address of instruction presented by this node
        srcLine - source code line, which generated this instruction
        """
        self.nodeId = nodeId
        self.shape = shape
        self.bkgColor = bkgColor
        self.label = label
        self.style = style
        self.height = height
        self.address = address
        self.srcLine = srcLine
        self.debugInfo = None
        self.isHTMLLabel = False
        self.isMergeableFlag = False
        self.dotLink = None
        self.mergedNodes = []

    def setHTMLLabel(self, isHTML):
        self.isHTMLLabel = isHTML

    def setDebugInfo(self, debugInfo):
        self.debugInfo = debugInfo

    def setMergeableFlag(self, isSequential, isConditional, isCall):
        self.isMergeableFlag = isSequential and not isConditional and not isCall

    def setLink(self, dotLink):
        self.dotLink = dotLink

    def merge(self, node):
        """
        Merges two nodes into one by concatenating labels and preserving
        link of the second node. This method may be called only on nodes,
        which have links to parameter 'node'.
        """
        self.mergedNodes.append(node)
        self.dotLink.destNodeId = node.getLinkDestination()

    def isMergeable(self):
        return self.isMergeableFlag

    def getShape(self):
        return self.getShape

    def getBkgColor(self):
        return self.bkgColor

    def getLabel(self):
        return self.label

    def createNodeLabel(self):
        """
        Text in node (label) should be like: 
        "[Optional]:address\n[Optional]:srcLine\nopCode"
        
        EX1 (with address):                     "0x8000658\nVehicle::Vehicle"
        EX2 (with srcLine):                     "void vehicle_init()\npush {r7,r14}"
        EX3 (without any optional additions):   "adds r7,#0x10"
        """
        
        label = ""

        if self.address:
            label += f"<color:red>{hex(self.address)}</color>\\n"

        if self.srcLine:
            label += f"<color:green>{self.srcLine}</color>\\n"

        label += self.label

        return label

    def getFormattedLabel(self):
        label = self.createNodeLabel()
        for node in self.mergedNodes:
            label += f"\\n{node.createNodeLabel()}"
        return label


    def getStyle(self):
        return self.style

    def getHeight(self):
        return self.height

    def getLinkDestination(self):
        return self.dotLink.destNodeId
    
    def getNodeId(self):
        """
        Sometimes self.nodeId is n_XXXXXXXXXn_YYYYYYYYY,
        in that case it returns only n_XXXXXXXXX (the id of the first node merged). 
        If self.nodeId is n_XXXXXXXXX, then it returns n_XXXXXXXXX, if its something
        that doesn't contain n_, it returns as is. 
        """
        if "n_" in self.nodeId:
            return f"n_{self.nodeId.split("n_")[1]}"
        return self.nodeId

    def write(self, outFile):

        debug_info = ""
        if self.debugInfo:
            debug_info = f"debug:[{self.debugInfo}]"

        background_color = ""
        if self.bkgColor:
            background_color = f" #{self.bkgColor}"

        #Example: rectangle "0x8000508\nvehicle_upgrade" as v2 #paleturquoise
        outFile.write(f'{self.shape} "{self.getFormattedLabel()} {debug_info}" as {self.getNodeId()}{background_color}\n')


def _getJumpShape(instruction):

    height = ''

    if instruction.isConditional():
        if instruction.isCall():
            shape = "file"
        else:
            shape = "collections"
        height = '1'
    else:
        if instruction.isCall():
            shape = "node"
        else:
            shape = "queue"

    return shape, height


def _getLook(instruction, addrCtrl):
    """
    Defines node graphical properties according to instruction type.
    """
    shape = 'rectangle'
    bkgColor = 'white'
    peripheries = 1 # used to be used for RW access, but since it is not
                    # implemeneted on all disassemblers and the meaning of
                    # double or tripple borders is not intuitive, 'peripheries'
                    # is currently not used.
    height = ''

    if instruction.isFlowSequential():
        if instruction.isConditional():
            shape = 'frame'
        else:
            shape = 'rectangle'

        bkgColor = 'cornsilk'

    elif instruction.isFlowDirectJump():
        shape, height = _getJumpShape(instruction)
        bkgColor = 'moccasin'

    else: # instruction.isFlowIndirectJump():
        shape, height = _getJumpShape(instruction)
        bkgColor = 'thistle'

    opCode = instruction.getOpCode()
    # opcode may contain double quotes when file name is included in
    # branch address, so replace them with single quotes to not break
    # puml syntax
    opCode = opCode.replace('"', "'")
    opCode = opCode.replace(':', " ")
    # replace tabs with spaces, since DOT ignores tabs in HTML labels
    opCode = opCode.replace('\t', " ")

    addr = instruction.getAddress()
    if 'g_testIter' in globals():
        srcLine = ''  # no source lines during test
    else:
        srcLine = addrCtrl.getSymbolAtAddress(ic.IConnectDebug.sSourceCode, 0, addr,
                                              ic.IConnectDebug.sScopeExact)
    # replace special HTML chars
    srcLine = srcLine.replace('&', '&amp;')
    srcLine = srcLine.replace('<', '&lt;')
    srcLine = srcLine.replace('>', '&gt;')

    return shape, bkgColor, peripheries, opCode, height, srcLine


def _createLinkLabel(label, address=''):
    if address:
        return f"<color:red>{hex(address)}</color>" + label

    return label


def createNodeId(address):
    return "n_" + str(address)


def _write_Direct_Conditional_CallLink(outFile, debug, instruction,
                                       isSingleCallNode, isAutoRank):
    # the difference between conditional and unconditional calls
    # is in node look only
    label = _createLinkLabel(LINK_TRUE_LBL)
    _write_Direct_Unconditional_CallLink(outFile, debug, instruction,
                                         isSingleCallNode, isAutoRank, label)


def _write_Direct_Conditional_JumpLink(outFile, iiter, instruction, isAutoRank):
    # the difference between conditional and unconditional jumps
    # is in node look only
    label = _createLinkLabel(LINK_TRUE_LBL, instruction.getJumpTarget())
    _write_Direct_Unconditional_JumpLink(outFile, iiter, instruction, isAutoRank, label)


def _write_Direct_Unconditional_CallLink(outFile, debug, instruction,
                                         isSingleCallNode, isAutoRank, label):

    targetAddr = instruction.getJumpTarget()

    if isSingleCallNode:
        # all calls to other functions link to the same node - better when
        # we are interested in called funtions, but layout is less readable
        calledNodeId = createNodeId(targetAddr)
    else:
        # make unique node ID for each call
        calledNodeId = createNodeId(targetAddr) + createNodeId(instruction.getAddress())

    currentNodeId = createNodeId(instruction.getAddress())

    if not calledNodeId in g_externalNodes:
        g_externalNodes.add(calledNodeId)
        calledFunction = debug.getSymbolAtAddress(ic.IConnectDebug.sFunctions,
                                                  0,
                                                  targetAddr,
                                                  ic.IConnectDebug.sScopeNarrow)
        node = Node(calledNodeId, 'usecase', 'paleturquoise', calledFunction, 'dashed', #ellipse
                       address=targetAddr)
        node.write(outFile)

    writeJumpLink(outFile, currentNodeId, calledNodeId, label, isAutoRank)


def _write_Direct_Unconditional_JumpLink(outFile, iiter, instruction, isAutoRank, label):
    # create link to node when condition is True
    jmpAddress = instruction.getJumpTarget()
    jmpNodeId = createNodeId(jmpAddress)

    if not jmpNodeId in g_externalNodes:
        g_externalNodes.add(jmpNodeId)
        if not iiter.isAddressInRange(jmpAddress):
            # jump to address outside function!
            node = Node(jmpNodeId, 'usecase', 'lightpink', str(jmpAddress), 'dotted')
            node.write(outFile)
        else:
            pass # node for jump inside function will be created later
            # iter.branch(jmpAddress)
            # jmpInstruction = iter.next()
            # shape, bkgColor, peripheries, label = _getLook(jmpInstruction)
            # writeNode(outFile, jmpNodeId, shape, bkgColor, peripheries, label)
            # iter.branch(instruction.getAddress())

    currentNodeId = createNodeId(instruction.getAddress())

    if not label: # not defined by caller, add address
        label = _createLinkLabel('', jmpAddress)

    writeJumpLink(outFile, currentNodeId, jmpNodeId, label, isAutoRank)
    g_nodeJumpNumber[jmpNodeId] += 1


def _write_Indirect_CallLink(outFile, instruction, isAutoRank, label):
    # this node can not exist, as its ID contains current address
    currentNodeId = createNodeId(instruction.getAddress())
    calledNodeId = currentNodeId + '_indirectCall'
    node = Node(calledNodeId, 'usecase', 'paleturquoise', 'indirectCall', 'dotted')
    node.write(outFile)
    writeJumpLink(outFile, currentNodeId, calledNodeId, label, isAutoRank)


def _write_Indirect_JumpLink(instruction):
    # this node can not exist, as its ID contains current address
    currentNodeId = createNodeId(instruction.getAddress())
    jmpNodeId = currentNodeId + '_indirectBranch'

    # indirect jump nodes are currently not shown, as they are annoying in case of
    # 'blr', and indirect jumps are shown with special node color
    #writeNode(outFile, jmpNodeId, 'house', 'gold', 1, 'indirectBranch', 'dotted')
    #writeJumpLink(outFile, currentNodeId, jmpNodeId, label, isAutoRank)


def getInstructionIterator(socCodeInfo, addrCtrl, dataCtrl2, functionName):
    funcNameParts = functionName.split(',,')

    if len(funcNameParts) == 2:
        partitionCodeInfo = socCodeInfo.loadCodeInfo(dataCtrl2, funcNameParts[1])
    else:
        partitionCodeInfo = socCodeInfo.loadCodeInfo(dataCtrl2, '')

    iiter = ic.CInstructionIter(partitionCodeInfo,
                                addrCtrl,
                                functionName)
    return iiter


def createStartNode(nodesList, iiter, functionName):
    nextInstr = iiter.peek()
    node = Node(functionName, 'usecase', 'aquamarine', functionName,
                   address=nextInstr.getAddress())

    nextNodeId = createNodeId(nextInstr.getAddress())
    node.setLink(Link(functionName, nextNodeId))
    nodesList.append(node)


def createNode(instruction, addrCtrl):
    currentNodeId = createNodeId(instruction.getAddress())
    shape, bkgColor, _, opCode, height, srcLine = _getLook(instruction, addrCtrl)
    node = Node(currentNodeId, shape, bkgColor, opCode, height=height, srcLine=srcLine)
    node.setMergeableFlag(instruction.isFlowSequential(),
                          instruction.isConditional(),
                          instruction.isCall())

    if IS_DEBUG:
        node.setDebugInfo(instruction.toString())

    return node


def writeJumpLink(outFile, startNode, endNode, decoration, isAutoRank):
    link = Link(startNode, endNode, decoration)
    # if jump links do not influence ranking, nodes are placed top to
    # bottom following the address order
    if not isAutoRank:
        link.setConstraint(False)

    link.append(direction="right")


def linkToNextNode(instruction, currentNodeId, nextNodeId):

    link = None

    if (instruction.isFlowSequential() or instruction.isCall() or
            instruction.isConditional()):

        if instruction.isConditional():
            label = _createLinkLabel(LINK_FALSE_LBL)
            link = Link(currentNodeId, nextNodeId, label)
        else:
            link = Link(currentNodeId, nextNodeId)

        g_nodeJumpNumber[nextNodeId] += 1
    else:
        # jumps should have invisible links to next nodes, which contain
        # instructions on next addresses to maintain address order of nodes
        isIndirectUnconditionalJump = (instruction.isFlowIndirectJump() and
                                       not instruction.isConditional() and
                                       not instruction.isCall())
        # skip invisible links for nodes, which are not present, see comment in
        # write_Indirect_Unconditional_JumpLink() above
        if not isIndirectUnconditionalJump:
            link = Link(currentNodeId, nextNodeId)
            link.setStyle('invis')

    return link


def handleCallsAndJumps(outFile, instruction, debug, iiter,
                        isSingleCallNode, isAutoRank):

    if instruction.isFlowSequential():
        pass
    elif instruction.isFlowDirectJump():
        if instruction.isConditional():
            if instruction.isCall():
                _write_Direct_Conditional_CallLink(outFile, debug, instruction,
                                                   isSingleCallNode, isAutoRank)
            else:
                _write_Direct_Conditional_JumpLink(outFile, iiter,
                                                   instruction, isAutoRank)
        else:
            if instruction.isCall():
                _write_Direct_Unconditional_CallLink(outFile, debug, instruction,
                                                     isSingleCallNode, isAutoRank, '')
            else:
                _write_Direct_Unconditional_JumpLink(outFile, iiter, instruction,
                                                     isAutoRank, '')

    elif instruction.isFlowIndirectJump():
        if instruction.isConditional():
            if instruction.isCall():
                _write_Indirect_CallLink(outFile, instruction, isAutoRank, LINK_TRUE_LBL)
            else:
                _write_Indirect_JumpLink(instruction)
        else:
            if instruction.isCall():
                _write_Indirect_CallLink(outFile, instruction, isAutoRank, '')
            else:
                _write_Indirect_JumpLink(instruction)
    else:
        raise Exception("Invalid instruction - should be sequential, or direct, or indirect jump")


def mergeAndWriteNodesToFile(outFile, nodesList):

    mergedNode = None

    for node in nodesList:
        nodeId = node.getNodeId()

        if node.isMergeable():
            if mergedNode is None:
                mergedNode = node # First node in merged block
            else:
                if g_nodeJumpNumber[nodeId] < 2:
                    mergedNode.merge(node)
                else:
                    mergedNode.write(outFile) # Last node in the merged block
                    mergedNode = node
        else:
            if not mergedNode is None: # Last node in the merged block
                mergedNode.write(outFile)
                mergedNode = None
            node.write(outFile) # Not mergeble nodes



    if mergedNode: # write the last merged node, if exists
        mergedNode.write(outFile)

def appendLinks(nodesList):
    """
    Append links between nodes so that they can be written at the end of the file.

    NOTE:
    A block of merged nodes takes the id of the first node merged. Thus we 
    want to take the id of the first node and skip all other ids until we
    are over the ones used in the block. You can know which are used in the
    block because they have node.isMergeable() == True.
    The nodes which aren't mergeable are handled as distinct nodes.
    """

    is_mergeable = False
    is_append = True
    nodeIds = []

    for node in nodesList:
        nodeId = node.getNodeId()

        if node.isMergeable():
            if not is_mergeable: # take first from the ones merged
                is_mergeable = True
                toAppend = nodeId
            else: # Skip all other merged
                is_append = False
        else: # Handle non mergeable nodes.
            is_mergeable = False
            is_append = True
            toAppend = nodeId

        if is_append:
            nodeIds.append(toAppend)

    if not len(nodeIds) >= 2:
        raise ValueError(f"Need at least 2 nodes, you have {len(nodeIds)}. Your nodes: {nodeIds}")
    # Connect like: id0 -> id1, id1 -> id2, id2 -> id3, ...  
    for i in range(1, len(nodeIds)):
        link = Link(nodeIds[i - 1], nodeIds[i])
        link.append()
        

def writeNodesToFile(outFile, nodesList):
    for node in nodesList:
        node.write(outFile)


def analyzeFunction(connectionMgr, functionName, isExpanded,
                    isSingleCallNode,
                    isAutoRank,
                    outFile):
    """
    This is top-level function for creation of puml file. It iterates from the
    firt to the last instruction in function and creates puml nodes and links
    of appropiate look.
    """
    global all_link_strings
    outFile.write("@startuml\n")
    outFile.write("\n")
    # Enforce use of smetana to avoid graphwiz
    outFile.write("!pragma layout smetana\n")
    outFile.write("\n")
    # font 10 in graphs should be big enough to be readable
    outFile.write("' General parameters\n")
    outFile.write("skinparam defaultFontSize 10\n")
    outFile.write("\n")
    outFile.write("' Nodes\n")

    debug = ic.CDebugFacade(connectionMgr)
    dataCtrl2 = ic.CDataController2(connectionMgr)
    addrCtrl = ic.CAddressController(connectionMgr)
    socCodeInfo = ic.CSOCCodeInfo()

    nodesList = []

    if 'g_testIter' in globals():
        iiter = g_testIter
    else:
        iiter = getInstructionIterator(socCodeInfo, addrCtrl, dataCtrl2, functionName)

    createStartNode(nodesList, iiter, functionName)

    while iiter.hasNext():

        instruction = iiter.next()

        if IS_DEBUG:
            print('instruction: addr = ', instruction.getAddress(),
                  '  opCode = ', instruction.getOpCode())

        node = createNode(instruction, addrCtrl)
        nodesList.append(node)
        currentNodeId = node.getNodeId()

        handleCallsAndJumps(outFile, instruction, debug, iiter,
                            isSingleCallNode, isAutoRank)

        if iiter.hasNext():
            nextInstr = iiter.peek()
            nextNodeId = createNodeId(nextInstr.getAddress())
        else:
            nextNodeId = 'OutOfFunction'  # should never be used

        link = linkToNextNode(instruction, currentNodeId, nextNodeId)
        node.setLink(link)

    # Write nodes
    if isExpanded:
        writeNodesToFile(outFile, nodesList)
    else:
        mergeAndWriteNodesToFile(outFile, nodesList)
    
    # Some links still need to be appended
    appendLinks(nodesList)

    # Write appended links
    outFile.write("\n")
    outFile.write("' Links\n")
    for link in all_link_strings:
        outFile.write(f"{link}\n")


    outFile.write("@enduml\n\n")


def main(cmdLineArgs):

    print('Creating flow chart:')

    opts = diagutils.parseArgs(cmdLineArgs,
                               [('-e',
                                 '--expand',
                                 'isExpanded',
                                 False,
                                 'if present, sequence instructions are shown in separate nodes'),
                                ('-s',
                                 '--singleCallNode',
                                 'isSingleCallNode',
                                 False,
                                 'if present, all calls to the same function are linked to the ' +
                                 'same node, otherwise each call has its own node, but results ' +
                                 'in more readable layout'),
                                ('-a',
                                 '--autoRank',
                                 'isAutoRank',
                                 False,
                                 'if present, then nodes are not ordered according to addresses, ' +
                                 'but to minimize length of links.'),
                                ('-o',
                                 '--open',
                                 'isOpenInSystemViewer',
                                 False,
                                 'if present, then generated diagram is opened in OS default ' +
                                 'viewer'),
                               ])

    cmgr = ic.ConnectionMgr()
    cmgr.connectMRU('')

    # make a variable that is outFileName without the .xxx (EX: image.png -> image)
    graphFileName = diagutils.createPumlGraphFileName(opts.outFileName, 'flow')
    
    with open(graphFileName, 'w') as outf:

        if IS_DEBUG:
            print(' '.join(cmdLineArgs))

        analyzeFunction(cmgr,
                        opts.functionName,
                        opts.isExpanded,
                        opts.isSingleCallNode,
                        opts.isAutoRank,
                        outf)

    # this statement must NOT be in with statement above. as outf must be
    # closed for puml to see complete file
    diagutils.createPumlGraphImage(opts.puml_fpath,
                               graphFileName,
                               opts.outFileName)

    if opts.isOpenInSystemViewer:
        sp.check_call('start ' + opts.outFileName, shell=True)

    print('    Done!')

if __name__ == "__main__":
    main(sys.argv[1:])
