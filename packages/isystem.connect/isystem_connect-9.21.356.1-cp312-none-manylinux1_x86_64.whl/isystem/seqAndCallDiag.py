"""
 This script processes data recorded by profiler and creates two types
 of diagrams - UML sequence diagrams and call graphs.


 Requirements for custom Python installations
 ============================================

 Python, which is bundled with winIDEA, already has all dependencies
 configured.

 1. - For sequence diagrams module 'seqdiag' has to be installed.
      First download setuptools from:
        https://pypi.python.org/pypi/setuptools#files
      and install.
    - Install 'seqdiag' (use correct path for your Python installation):
        C:/Python27/Scripts/easy_install seqdiag

    Alternatively (if the above steps failed) you can download seqdiag from:
        https://pypi.python.org/pypi/seqdiag/
    Uncompress it (7-zip can be used) and run:
        python setup.py

 2. Install graphviz. Windows installer can be downloaded from:
        http://www.graphviz.org/Download_windows.php
    The console or IDE where the scripts will be ran should be restarted
    after the graphviz has been installed.

 See also help text in function _parseCmdLineOptions().

 (c) TASKING Germany GmbH, 2023
"""

from __future__ import print_function

import os
import sys
import argparse
import collections
import subprocess as sp
import traceback

import isystem.connect as ic
import isystem.diagutils as diagutils


def _printStatistics(stats):
    print('  Statistics:')
    print('    Id:        ', hex(stats.getAreaId()))
    print('    Handle:    ', stats.getHandle())
    print('    Name:      ', stats.getAreaName())
    print('    Value:     ', stats.getAreaValue())
    print('    Num hits:  ', stats.getNumHits())
    print('    Net times: ')
    print('      total:   ', stats.getNetTotalTime())
    print('      min:     ', stats.getNetMinTime())
    print('      max:     ', stats.getNetMaxTime())
    print('      average: ', stats.getNetAverageTime())
    print('    Gross times:')
    print('      total:   ', stats.getGrossTotalTime())
    print('      min:     ', stats.getGrossMinTime())
    print('      max:     ', stats.getGrossMaxTime())
    print('      average: ', stats.getGrossAverageTime())
    print('    Call times:')
    print('      total:   ', stats.getCallTotalTime())
    print('      min:     ', stats.getCallMinTime())
    print('      max:     ', stats.getCallMaxTime())
    print('      average: ', stats.getCallAverageTime())
    print('    Period:')
    print('      min:     ', stats.getPeriodMinTime())
    print('      max:     ', stats.getPeriodMaxTime())
    print('      average: ', stats.getPeriodAverageTime())
    print('    Outside times:')
    print('      total:   ', stats.getOutsideTotalTime())
    print('      min:     ', stats.getOutsideMinTime())
    print('      max:     ', stats.getOutsideMaxTime())
    print('      average: ', stats.getOutsideAverageTime())


def _printArea(area):
    print('Area:')
    print('  Id:        ', hex(area.getAreaId()))
    print('  Handle:    ', area.getHandle())
    print('  Name:      ', area.getAreaName())
    print('  Value:     ', area.getValue())
    print('  Line num.: ', area.getLineNumber())
    print('  Parent h.: ', area.getParentHandle())
    print('  Parent a.: ', area.getParentAreaName())


def _printAreas(profilerData, areaType):

    areaIterator = profilerData.getAreaIterator(areaType)

    while areaIterator.hasNext():
        area = areaIterator.next()
        _printArea(area)

        if profilerData.hasStatisticsForArea(area.getAreaId()):
            stats = profilerData.getStatistics(area.getAreaId())
            _printStatistics(stats)
        else:
            print('No statistic for area ', hex(area.getAreaId()), 'found.')



def printTimeEvent(timeEvent):
    """
    Utility function used for diagnostic.
    """
    print('TimeEvent:')
    print('  handle: ', timeEvent.getHandle())
    print('  evType: ', timeEvent.getEventType())
    print('  value:  ', timeEvent.getValue())
    print('  time:   ', timeEvent.getTime())


def _addStandaloneFunction(timeEvent, seqDiagCalls, areaName):
    if timeEvent.getEventType() == ic.CProfilerTimeEvent.EEvEnter:
        # add only function name. Functions, which do not call
        # other functions and are not called by other functions, get
        # a placeholder, which is not connected anywhere. This happens
        # when only some functions are profiled, so some callers and
        # called functions may be missing from recording.
        seqDiagCalls.append(areaName + ';\n')


def _to_valid_area_name(area_name: str) -> str:
    """
    Area name must not contain characters, which confuse dot syntax, for
    example quotes in qualified function names: "utils.s#"myfunc
    """
    return area_name.replace('"', "'")

    
def timeline2SequenceDiagram(profilerData, timeIter):
    """
    This function iterates profiler XML output and creates data structures
    for both sequence diagram (array of calls) and call graph (map of sets,
    where key is caller, value is set with called functions).
    """
    prevAreaName = ''
    prevEvent = None
    seqDiagCalls = []
    callGraphMap = collections.defaultdict(set)
    # map<callerFuncName, map<calledFuncName, callCounter>>
    callGraphCountersMap = collections.defaultdict(int)
    callGraphNodesSet = set()  # contains all functions

    # print(ic.CProfilerTimeEvent.EEvSuspend)
    # print(ic.CProfilerTimeEvent.EEvResume)
    # print(ic.CProfilerTimeEvent.EEvEnter)
    # print(ic.CProfilerTimeEvent.EEvExit)

    while timeIter.hasNext():
        timeEvent = timeIter.next()
        #printTimeEvent(timeEvent)
        area = profilerData.getArea(timeEvent.getAreaId())

        if area.getAreaType() != ic.CProfilerArea2.EFunctions:
            continue

        # Add quotes, because otherwise commas in qualifies names interfere with
        # dot file syntax.
        areaName = '"' + _to_valid_area_name(area.getAreaName()) + '"'
        callGraphNodesSet.add(areaName)

        if prevAreaName:
            if prevEvent.getEventType() == ic.CProfilerTimeEvent.EEvSuspend and \
                timeEvent.getEventType() == ic.CProfilerTimeEvent.EEvEnter:

                # EX: "vehicle_init" -> "Vehicle::Vehicle" : Vehicle::Vehicle
                seqDiagCalls.append(f"{prevAreaName} -> {areaName} : {areaName}\n")
                callGraphMap[prevAreaName].add(areaName)

                # tuple of (caller, called) is used as a key
                callGraphCountersMap[prevAreaName, areaName] += 1
                # if areaName in counterMap:
                #     counterMap[areaName] += 1;
                # else:
                #     counterMap[areaName] = 0

                # print(prevAreaName + ' -> ' + areaName + ';')
            elif prevEvent.getEventType() == ic.CProfilerTimeEvent.EEvExit and \
                timeEvent.getEventType() == ic.CProfilerTimeEvent.EEvResume:
                # EX: "Vehicle::Vehicle" --> "vehicle_init"
                seqDiagCalls.append(f"{prevAreaName} --> {areaName}\n")
                # print(areaName + ' <-- ' + prevAreaName + ';')
            else:
                _addStandaloneFunction(timeEvent, seqDiagCalls, areaName)
        else:
            _addStandaloneFunction(timeEvent, seqDiagCalls, areaName)

        prevAreaName = areaName
        prevEvent = timeEvent

    return seqDiagCalls, callGraphMap, callGraphNodesSet, callGraphCountersMap


def timeline2StateDiagram(profilerData, timeIter, variableName):
    """
    This function iterates profiler XML output and creates data structures
    for both sequence diagram (array of calls) and state diagram (map of sets,
    where key is previous state, value is set of next states).
    """
    prevAreaName = ''
    seqDiagCalls = []
    callGraphMap = collections.defaultdict(set)

    while timeIter.hasNext():
        timeEvent = timeIter.next()
        #printTimeEvent(timeEvent)
        area = profilerData.getArea(timeEvent.getAreaId())
        areaName = area.getAreaName()

        if (areaName == variableName  and
                area.getAreaType() == ic.CProfilerArea2.EVariables  and
                area.hasStates() and
                timeEvent.getEventType() == ic.CProfilerTimeEvent.EEvWrite):

            value = timeEvent.getValue()
            stateArea = profilerData.getArea(ic.CProfilerArea2.EStateVariables, areaName,
                                             value)
            stateAreaName = stateArea.getAreaName()
            # print(areaName, stateAreaName, timeEvent.getEventType(), value)
            if not stateAreaName:
                # when enum for this value is not defined, use value
                stateAreaName = str(value)

            if prevAreaName:
                seqDiagCalls.append(f"{prevAreaName} -> {stateAreaName} : {stateAreaName}\n")
                callGraphMap[prevAreaName].add(stateAreaName)
            else:
                _addStandaloneFunction(timeEvent, seqDiagCalls, stateAreaName)

            prevAreaName = stateAreaName

    return seqDiagCalls, callGraphMap


def _parseProfilerData(profilerExportFile: str, variableName: str, is_binary_timeline: bool):

    profilerData = ic.CProfilerData2.createInstance(profilerExportFile, is_binary_timeline)

    # always check for parser warnings
    warnings = profilerData.getParserWarnings()
    if warnings:
        print('WARNING(S): ', warnings)

    timeIter = profilerData.getTimelineIterator()

    if variableName:
        lines, callGraphMap = timeline2StateDiagram(profilerData,
                                                    timeIter,
                                                    variableName)
    else:
        lines, callGraphMap, callGraphNodesSet, callGraphCountersMap = \
                               timeline2SequenceDiagram(profilerData, timeIter)

    profilerData.closeParser()  # releases memory and closes XML file

    return lines, callGraphMap, callGraphNodesSet, callGraphCountersMap


def replace(lines, eqCounter, lineIdx, seqStartIdx, offset, section,
            seqDiagCompactLevel):
    r"""
    Replaces repeating sequences of calls with one sequence and text
    indicating number of repeats, for example:
    a -> b                  === Repeats 2 times (section: 1) ===
    a <-- b    --\          a -> b
    a -> b     --/          a <-- b
    a <-- b                 ... End of repeated sequence  (section: 1) ...
    """
    numEqSequences = int(eqCounter / offset)
    if numEqSequences > (seqDiagCompactLevel - 2):
        eqCounter = 0
        endSeqIdx = seqStartIdx + numEqSequences * offset
        # remove lines
        del lines[seqStartIdx : endSeqIdx]
        lines.insert(seqStartIdx, '... Repeats ' + str(numEqSequences + 1) +
                     ' times  (section: ' + str(section) + ') ...\n')
        lines.insert(seqStartIdx + offset + 1, '=== End of Repeated Sequence  ' +
                     '(section: ' + str(section) + ') ===\n')
        lineIdx = seqStartIdx + offset + 2 # +2 for additional 2 inserted lines
    else:
        lineIdx += 1
        eqCounter = 0

    return eqCounter, lineIdx


def correlationStep(lines, offset, section, seqDiagCompactLevel):
    """
    This function looks for repeated sequence with correlation.
    """
    eqCounter = 0
    seqStartIdx = 0
    lineIdx = 0
    while lineIdx < (len(lines) - offset):
        if lines[lineIdx] == lines[lineIdx + offset]:
            if eqCounter == 0:
                seqStartIdx = lineIdx # remember start of block
            eqCounter += 1
            lineIdx += 1
        else:
            eqCounter, lineIdx = replace(lines, eqCounter, lineIdx, seqStartIdx,
                                         offset, section, seqDiagCompactLevel)

    replace(lines, eqCounter, lineIdx, seqStartIdx, offset, section,
            seqDiagCompactLevel)


def _compressSeqDiagram(lines, seqDiagCompactLevel):
    print('    Processing data ...')
    section = 1
    for offset in range(2, int(len(lines)/2), 2):
        correlationStep(lines, offset, section, seqDiagCompactLevel)
        section += 1


def _writeSeqDiagram(graphFileName, lines):
    print('    Puml file: ', graphFileName)
    outf = open(graphFileName, 'w')
    outf.write("@startuml\n")
    outf.write("\n")
    # Enforce use of smetana to avoid graphwiz
    outf.write("!pragma layout smetana\n")
    outf.write("\n")
    # font is 12 in this graph because it gets bigger then others
    outf.write("' General parameters\n")
    outf.write("autonumber\n")
    outf.write("skinparam defaultFontSize 12\n")
    
    outf.write("\n")
    outf.write("' Links\n")
    for line in lines:
        if "->" not in line:
            continue
        outf.write(line)

    outf.write("\n@enduml\n\n")
    outf.close()


def _writeCallGraph(graphFileName,
                    callGraphMap,
                    callGraphNodesSet,
                    callGraphCountersMap,
                    functionUnderTest):

    print('    Puml file: ', graphFileName)
    outf = open(graphFileName, 'w')
    outf.write("@startuml\n")
    outf.write("\n")
    # Enforce use of smetana to avoid graphwiz
    outf.write("!pragma layout smetana\n")
    outf.write("\n")
    # font 10 in graphs should be big enough to be readable
    outf.write("' General parameters\n")
    outf.write("skinparam defaultFontSize 10\n")

    outf.write("\n")
    outf.write("' Nodes\n")
    # write list of nodes (function names) with their graphical attributes    
    for funcNode in callGraphNodesSet:
        outf.write(f"usecase {funcNode}")

        if funcNode == functionUnderTest:
            outf.write(f" #linen\n")
        else:
            outf.write(f" #azure\n")

    outf.write("\n")
    outf.write(f"' Links\n")
    for caller, setOfCalled in callGraphMap.items():
        for called in setOfCalled:
            if called:
                counter = callGraphCountersMap[caller, called]
                outf.write(f'{caller} -down-> {called} : {counter}\n')

    outf.write("\n@enduml\n\n")
    outf.close()


def _openImageWithViewer(imageFName):

    try:
        sp.check_call('start ' + imageFName, shell=True)
    except Exception:
        sp.check_call('gwenview ' + imageFName, shell=True)


def generateDiagrams(puml_fpath,
                     profilerExportFile,
                     callGraphImageFName,
                     seqDiagImageFName,
                     functionUnderTest,
                     isCreateSeqDiag=True, isCreateCallGraph=True,
                     seqDiagCompactLevel=4,
                     isCreateSeqDiagImage=True, isCreateCallGraphImage=True,
                     isOpenSeqDiagImage=True, isOpenCallGraphImage=True,
                     variableName='',
                     is_bin_timeline: bool=False):
    """
    This function creates diagrams based on profiler measurements as
    specified by parameters:

    profilerExportFile - name of the file with exported profiler data
    in XML format

    isCreateSeqDiag = True - if True, sequence diagram description
                             file is created

    isCreateCallGraph = True - if True, call graph description file is
                               created

    seqDiagCompactLevel = 4 - the minimum number of repeatitions
                              before sequence is shown as repeated
                              section. If 0 or 1, no compacting is
                              performed.

    isCreateSeqDiagImage = True - if True, image of sequence diagram
                                  is created

    isCreateCallGraphImage = True - if True, image of call graph is
                                    created

    isOpenSeqDiagImage = True - if true, sequence diagram image is
                                opened with default image viewer

    isOpenCallGraphImage = True - if true, call graph image is opened
                                  with default image viewer

    Some flags have no effect if previous steps are not executed. For
    example, if 'isCreateSeqDiag' is set to False, then
    'isCreateSeqDiagImage' and 'isOpenSeqDiagImage' are ignored.
    """

    try:
        lines, callGraphMap, callGraphNodesSet, callGraphCountersMap = \
                            _parseProfilerData(profilerExportFile, variableName, is_bin_timeline)
    except Exception as ex:
        print("ERROR: Can not open or parse profiler data file: " +
              profilerExportFile, file=sys.stderr)
        print("\nDetails: \n  ", str(ex), '\n', file=sys.stderr)
        traceback.print_exc()
        return

    if isCreateSeqDiag:
        if seqDiagCompactLevel > 1:
            _compressSeqDiagram(lines, seqDiagCompactLevel)

        graphFileName = \
            diagutils.createPumlGraphFileName(seqDiagImageFName,
                                          'seq')
        
        _writeSeqDiagram(graphFileName, lines)

        # do not generate sequence diagram for state variable, because
        # tool 'seqdiag' expects returns (equal number of -> and <--)
        # (otherwise it freezes with less than 1000 lines), and state
        # transitions are much less regular than function calls so
        # compression is not as good and results are not intuitive
        if isCreateSeqDiagImage and not variableName:
            if not puml_fpath: 
                raise Exception(r"Specify in command: --puml <C:\path\to\plantuml.jar>")
            diagutils.createPumlGraphImage(
                puml_fpath,
                graphFileName,
                seqDiagImageFName
            )

    if isCreateCallGraph:
        graphFileName = \
            diagutils.createPumlGraphFileName(callGraphImageFName,
                                          'call')
        _writeCallGraph(graphFileName,
                        callGraphMap,
                        callGraphNodesSet,
                        callGraphCountersMap,
                        functionUnderTest)

        if isCreateCallGraphImage:
            if not puml_fpath: 
                raise Exception(r"Specify in command: --puml <C:\path\to\plantuml.jar>")
            diagutils.createPumlGraphImage(
                puml_fpath,
                graphFileName,
                callGraphImageFName
            )


    if isOpenSeqDiagImage and not variableName:
        print('    Opening sequence diagram with default viewer for PNG images ...')
        _openImageWithViewer(seqDiagImageFName)

    if isOpenCallGraphImage:
        print('    Opening call graph with default viewer for PNG images ...')
        _openImageWithViewer(callGraphImageFName)

    print('    Done!')


def _parseCmdLineOptions(cmdLineArgs):

    desc = """

This script processes data recorded by profiler and creates several types
of diagrams - UML sequence diagrams and call graphs for functions

  Requirements
  ============

  1. - For sequence diagrams module, 'seqdiag' utility has to be installed.
       First download setuptools from:
         https://pypi.python.org/pypi/setuptools#files
       and install.
     - Install 'seqdiag' (use correct path for your Python installation):
         C:/Python27/Scripts/easy_install seqdiag

     Alternatively (if the above steps failed) you can download seqdiag from:
         https://pypi.python.org/pypi/seqdiag/
     Uncompress it (7-zip can be used) and run:
         python setup.py

  2. Install graphviz. Windows installer can be downloaded from:
         http://www.graphviz.org/Download_windows.php


  Notes
  =====

  PNG images produced with this script can be very large, especially when
  compacting is not used. The default Windows image viewer can not show
  very large images, so other viewers should be used (Irfanview and GIMP
  are OK, for example).

"""

    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("-l", '--level', dest="seqDiagCompactLevel", default='4',
                        help="the minimum number of repetitions before " + \
                        "sequence is shown as repeated section")

    parser.add_argument("-s", dest="isCreateSeqDiag", action='store_true',
                        default=False,
                        help="If specified, sequence diagram " + \
                        "file in 'seqdiag' format is created.")

    parser.add_argument("-d", dest="isCreateSeqDiagImage", action='store_true',
                        default=False,
                        help="If specified, sequence diagram PNG image " + \
                        "is created.")

    parser.add_argument("-i", dest="isOpenSeqDiagImage", action='store_true',
                        default=False,
                        help="If specified, sequence diagram image " + \
                        "is automatically opened.")

    parser.add_argument("-c", dest="isCreateCallGraph", action='store_true',
                        default=False,
                        help="If specified, call graph file in " + \
                        "'dot' format is created.")

    parser.add_argument("-g", dest="isCreateCallGraphImage", action='store_true',
                        default=False,
                        help="If specified, call graph PNG image is created.")

    parser.add_argument("-r", dest="isOpenCallGraphImage", action='store_true',
                        default=False,
                        help="If specified, call graph image is automatically opened.")

    parser.add_argument("-v", '--var', dest="variableName", default='',
                        help="If specified, diagrams for the given state " + \
                           "variable are produced instead of function diagrams.")

    parser.add_argument('--dot', dest="dotDir", default='',
                        help="If specified, dot utility is run from this path.")
    
    parser.add_argument('--puml', dest="puml_fpath", default='',
                        help="If specifies, PlantUml utility is run from this path.")

    parser.add_argument('--function', dest="functionName", default='',
                        help="Function under test.")
    
    parser.add_argument('--bin_timeline', dest="is_bin_timeline", default=False,
                        action='store_true',
                        help="Specify this flag if profiler export was made with binary timeline.")

    parser.add_argument(dest="profilerXmlFileName", default='',
                        help="Name of a file, which contains profiler recording "
                        "exported to XML format")

    parser.add_argument(dest="imageFName", default='',
                        help="output file name, which will contain graph image. " +
                        "If call graph and sequence diagram are requested, than " +
                        "this is the name of call graph output image, while sequence" +
                        "diagram gets name postfix '-sequence' (inserted before extension)")


    options = parser.parse_args(cmdLineArgs)

    callGraphImageFName = ""
    if options.isCreateCallGraphImage:
        callGraphImageFName = options.imageFName

    seqDiagImageFName = ""
    if options.isCreateSeqDiagImage:
        if options.isCreateCallGraphImage:
            # add postfix to file name to distinguish it from call graph
            root, ext = os.path.splitext(options.imageFName)
            seqDiagImageFName = root + '-sequence' + ext
        else:
            seqDiagImageFName = options.imageFName

    if not options.puml_fpath: 
        raise Exception(r"Specify path to 'plantuml.jar' as command line arg --puml, "
                        r"for example: --puml C:\path\to\plantuml.jar")

    return options, options.profilerXmlFileName, callGraphImageFName, seqDiagImageFName


def main(args):

    opts, profilerExportFile, callGraphImageFName, seqDiagImageFName = _parseCmdLineOptions(args)

    if opts.isCreateSeqDiag:
        print('Creating sequence diagram:')

    if opts.isCreateCallGraph:
        print('Creating call graph:')

    if not (opts.isCreateSeqDiag or opts.isCreateCallGraph):
        raise ValueError(r"Input parameters were entered incorrectly. Valid Example: " \
        r"python .\seqAndCallDiag.py -c -g -r --function function --puml path\to\plantuml.jar .\file.xml file.svg")

    try:
        generateDiagrams(opts.puml_fpath,
                         profilerExportFile,
                         callGraphImageFName,
                         seqDiagImageFName,
                         opts.functionName,
                         opts.isCreateSeqDiag, opts.isCreateCallGraph,
                         int(opts.seqDiagCompactLevel),
                         opts.isCreateSeqDiagImage, opts.isCreateCallGraphImage,
                         opts.isOpenSeqDiagImage, opts.isOpenCallGraphImage,
                         opts.variableName,
                         opts.is_bin_timeline)
    except Exception as ex:
        print(str(ex), file=sys.stderr)
        traceback.print_exc()




if __name__ == "__main__":
    main(sys.argv[1:])
