import rhinoscriptsyntax as rs
import Rhino as rhino
from System.Drawing import Color
import math
#import gcodeGenerater

"""
To do

warning for angle of baseSurface

num of outline shell
num of top,bottom layer

it needs to adapt for not only closed polysurface but also open polysurface

get variables of print setting
3d printing setting file by xml

"""

class AAM_Planar():

    def __init__(self, _gcoder):

        self.gcoder = _gcoder


        self.normalVec = None
        self.addtiveObj = None
        self.baseSurface = None
        self.layerHeight = None

        #sliceSurface is used for slicing addtiveObj
        self.sliceSurface = None

        self.prePoint = None
        self.angleOfBaseSurface = None

        self.EValue = 0


        self.infillRatio = 0.05

        return

    def main(self):
        print("####### AAM Starts #######")
        #this code is for only planar surface
        if not self.setNormalVec():
            return
        if not self.setAdditiveObj():
            return

        self.setSurfaceForSlicing()


        #set layer for sliced lines
        '''
        if rs.IsLayer("gcode_line"):
            pass
        else:
            rs.AddLayer("gcode_line", Color.Red, True, False, None)
        '''

        #self.setLayerFill()
        self.slice()

        self.clean()

    def setAngleOfBaseSurface(self):

        tmpVector = (1, 0, 0)
        _angleOfSurface = rs.VectorAngle(tmpVector, self.normalVec)

        self.angleOfBaseSurface = 90 - _angleOfSurface



    def setNormalVec(self):
        #set normal vector from selected base surface
        #if selected base surface isn't planar, return False

        self.baseSurface = rs.GetSurfaceObject("Select surface to be addded object")
        if self.baseSurface == None:
            return False

        rs.SelectObject(self.baseSurface[0])

        if not rs.IsSurfacePlanar(self.baseSurface[0]):
            print("Selected Surface is not planar\nPlease select planar surface")
            return False

        print("Confirm direction to add object")
        rs.Command("Dir")

        self.normalVec = rs.SurfaceNormal(self.baseSurface[0], [0,0])

        rs.UnselectAllObjects()



        self.setAngleOfBaseSurface()

        return True


    def setAdditiveObj(self):
        #set object to be additived
        #if selected obj isnt closed, return False

        tmp = rs.GetObject("Select object which you want additive")

        '''
        if rs.IsMesh(tmp):
            if IsMeshClosed(tmp):
                #if selected obj is closed mesh, make it polysurface
                self.addtiveObj = rs.MeshToNurb(tmp)
                return True
            else:
                print("you must select closed object")
                return False

        if rs.IsPolysurface(tmp):
            if rs.IsPolysurfaceClosed(tmp):
                self.addtiveObj = tmp

                return True
            else:
                print("you must select closed object")
                return False
        '''

        #adapt to unclosed polysurface
        if rs.IsMesh(tmp):
            self.addtiveObj = rs.MeshToNurb(tmp)

        elif rs.IsPolysurface(tmp):
            self.addtiveObj = tmp

        else:
            print("please select \"mesh\" or \"polysurface\"")

        return True



    def setSurfaceForSlicing(self):
        explodedSurfaces = None


        editPoint = []
        explodedSurfaces = rs.ExplodePolysurfaces(self.addtiveObj)
        for i in explodedSurfaces:
            tmp = rs.SurfaceEditPoints(i)
            for j in tmp:
                editPoint.append(j)


        minValue = []
        maxValue = []
        basePointForPlane = None
        basePointForDistance = None

        for i in range(len(editPoint)):
            if i == 0:
                basePointForPlane = editPoint[i]
                basePointForDistance = editPoint[i]

                for j in range(3):
                    minValue.append(editPoint[0][j])
                    maxValue.append(editPoint[0][j])
                continue

            else:
                if basePointForPlane[2] > editPoint[i][2]:
                    basePointForPlane = editPoint[i]
                if basePointForDistance[2] < editPoint[i][2]:
                    basePointForDistance = editPoint[i]

                for j in range(3):
                    if minValue[j] > editPoint[i][j]:
                        minValue[j] = editPoint[i][j]
                    elif maxValue[j] < editPoint[i][j]:
                        maxValue[j] = editPoint[i][j]

        plane = rs.PlaneFromNormal(basePointForPlane, self.normalVec)


        self.distancePrinting = rs.DistanceToPlane(plane, basePointForDistance)

        self.distancePrinting *= (1.0 / math.cos(math.radians(self.angleOfBaseSurface)))

        if self.distancePrinting < 0:
            self.distancePrinting *= -1

        plane = rs.PlaneFromNormal(basePointForPlane, self.normalVec)

        pntForSur = []
        line = (minValue[0], minValue[1], minValue[2]), (minValue[0], minValue[1], maxValue[2])
        pntForSur.append(rs.LinePlaneIntersection(line, plane))
        line = (minValue[0], maxValue[1], minValue[2]), (minValue[0], maxValue[1], maxValue[2])
        pntForSur.append(rs.LinePlaneIntersection(line, plane))
        line = (maxValue[0], maxValue[1], minValue[2]), (maxValue[0], maxValue[1], maxValue[2])
        pntForSur.append(rs.LinePlaneIntersection(line, plane))
        line = (maxValue[0], minValue[1], minValue[2]), (maxValue[0], minValue[1], maxValue[2])
        pntForSur.append(rs.LinePlaneIntersection(line, plane))

        lineForSur = []

        for i in range(4):
            lineForSur.append(rs.AddLine(pntForSur[i], pntForSur[(i+1)%4]))

        self.sliceSurface = rs.AddEdgeSrf(lineForSur)

        #Delete lines used for making sliceSurface
        for i in lineForSur:
            rs.DeleteObject(i)
        rs.DeleteObjects(explodedSurfaces)




    def slice(self):


        self.gcoder.initGcode()

        tmpText = ""

        multiplier = float(self.gcoder.getLayerHeight() * math.cos(math.radians(self.angleOfBaseSurface)))

        #layer by layer
        for i in range(int(self.distancePrinting/multiplier)+1):


            tmpText = "; layer " + str(i) + "\n"

            tmpText += "G92 E0\n"
            self.EValue = 0

            #vec = self.normalVec*(self.gcoder.getLayerHeight()*i)

            vec = (0, 0, float(multiplier*i))

            #tmp is slice surface at this height
            tmp = rs.CopyObject(self.sliceSurface, vec)


            #result is intersected curves
            result = rs.IntersectBreps(self.addtiveObj, tmp)

            if result == None:
                #at here, i need to fill layer
                return

            ##DEBUG needs
            #if result is array of lines?
            explodedCurve = rs.ExplodeCurves(result)


            #lines from explodedCurve
            for j in range(len(explodedCurve)):

                #gcode line is in gcode_line layer
                #rs.ObjectLayer(explodedCurve[j], "gcode_line")
                startPoint = rs.CurveStartPoint(explodedCurve[j])

                tmpText += "G1 X" + str(startPoint[0]) + " Y" + str(startPoint[1]) + " Z" + str(startPoint[2])


                if j == 0:
                    tmpText += " F1800\n"
                else:
                    self.calcEValue(self.prePoint, startPoint)
                    tmpText += " E" + str(self.EValue) + "\n"


                #if explodedCurve is last one
                if j == (len(explodedCurve)-1):
                    endPoint = rs.CurveEndPoint(explodedCurve[j])
                    self.calcEValue(startPoint, endPoint)
                    tmpText += "G1 X" + str(endPoint[0]) + " Y" + str(endPoint[1]) + " Z" + str(endPoint[2]) + " E" + str(self.EValue) + "\n"

                self.prePoint = startPoint

            self.gcoder.addGcode(tmpText)


            #DEBUG
            #below is making layer filled, but only one layer
            #i need to adapt to multi layer filling
            #layer filling at first layer


            if i < self.gcoder.getNumBottomLayer():
                self.setLayerFill(vec, result, i)

            elif i > (int(self.distancePrinting/multiplier) - self.gcoder.getNumTopLayer()):
                self.setLayerFill(vec, result, i)

            else:
                self.setInfill(vec, result)



            rs.DeleteObject(result)
            rs.DeleteObject(tmp)
            rs.DeleteObjects(explodedCurve)

        self.gcoder.finishGcode()
        self.gcoder.outputFile()

        return True


    def setLayerFill(self, vec, intersectCurve, index):
        #DEBUG needs
        #this function is not capable of wierd object
        #so you need to fix, about when you got pnts more than 2.

        #offset intersectCurve
        editPointsOfIntersectCurve = rs.CurveEditPoints(intersectCurve[0])
        dirVec = [0, 0, 0]
        for i in editPointsOfIntersectCurve:
            dirVec[0] += i[0]
            dirVec[1] += i[1]
            dirVec[2] += i[2]


        dirVec[0] /= len(editPointsOfIntersectCurve)
        dirVec[1] /= len(editPointsOfIntersectCurve)
        dirVec[2] /= len(editPointsOfIntersectCurve)

        dirVec = tuple(dirVec)

        intersectCurve = rs.OffsetCurve(intersectCurve[0], dirVec, self.gcoder.getLayerHeight())

        #DEBUG needs
        #intersectCurve = rs.OffsetCurve(intersectCurve[0], dirVec, self.gcoder.getLayerHeight()*self.gcoder.getNumShellOutline())

        #&offset intersectCurve



        newSliceSurface = rs.CopyObject(self.sliceSurface, vec)
        editPoints = rs.SurfaceEditPoints(newSliceSurface)




        #vertical
        if index%2 == 0:
            baseLine = rs.AddLine(editPoints[0], editPoints[1])

            baseVec = (editPoints[2][0]-editPoints[0][0], editPoints[2][1]-editPoints[0][1], editPoints[2][2]-editPoints[0][2])
            tmp = math.sqrt(baseVec[0]**2 + baseVec[1]**2 + baseVec[2]**2)
            baseVec = (baseVec[0]/tmp, baseVec[1]/tmp, baseVec[2]/tmp)

            dist = rs.Distance(editPoints[0], editPoints[2])


        #horizontal
        elif index%2 == 1:

            baseLine = rs.AddLine(editPoints[0], editPoints[2])

            baseVec = (editPoints[1][0]-editPoints[0][0], editPoints[1][1]-editPoints[0][1], editPoints[1][2]-editPoints[0][2])
            tmp = math.sqrt(baseVec[0]**2 + baseVec[1]**2 + baseVec[2]**2)
            baseVec = (baseVec[0]/tmp, baseVec[1]/tmp, baseVec[2]/tmp)

            dist = rs.Distance(editPoints[0], editPoints[1])




        '''
        lines = []

        for i in range(int(dist/self.gcoder.getLayerHeight()+1)):

            nextVec = (baseVec[0]*(self.gcoder.getLayerHeight()*i), baseVec[1]*(self.gcoder.getLayerHeight()*i), baseVec[2]*(self.gcoder.getLayerHeight()*i))

            #horizontal
            if index%2 == 0:

                nextStartPoint = (editPoints[0][0]+nextVec[0], editPoints[0][1]+nextVec[1], editPoints[0][2]+nextVec[2])
                nextEndPoint = (editPoints[1][0]+nextVec[0], editPoints[1][1]+nextVec[1], editPoints[1][2]+nextVec[2])

            #vertical
            elif index%2 == 1:
                nextStartPoint = (editPoints[0][0] + nextVec[0], editPoints[0][1] + nextVec[1], editPoints[0][2] + nextVec[2])
                nextEndPoint = (editPoints[2][0] + nextVec[0], editPoints[2][1] + nextVec[1], editPoints[2][2] + nextVec[2])

            nextLine = rs.AddLine(nextStartPoint, nextEndPoint)

            pnts = rs.CurveCurveIntersection(intersectCurve, nextLine)

            #debug
            if pnts == None:
                #DEBUG may needs
                rs.DeleteObject(nextLine)
                continue

            if len(pnts) < 2:
                continue
            elif len(pnts)%2 == 1:
                print('num of pnts is odd')

            else:
                for i in range(int(len(pnts)/2)):
                    lines.append(rs.AddLine(pnts[2*i][1], pnts[(2*i)+1][1]))


            rs.DeleteObject(nextLine)


        #make gcode from lines
        tmpText = "; layer filling\n"
        self.gcoder.addGcode(tmpText)

        for i in range(len(lines)):
            startPoint = rs.CurveStartPoint(lines[i])
            endPoint = rs.CurveEndPoint(lines[i])

            self.calcEValue(startPoint, endPoint)
            if i%2 == 0:
                tmpText = "G1 X" + str(startPoint[0]) + " Y" + str(startPoint[1]) + " Z" + str(startPoint[2]) + " F3600\n"
                tmpText += "G1 X" + str(endPoint[0]) + " Y" + str(endPoint[1]) + " Z" + str(endPoint[2]) + " E" + str(self.EValue) + " F1800\n"
            else:
                tmpText = "G1 X" + str(endPoint[0]) + " Y" + str(endPoint[1]) + " Z" + str(endPoint[2]) + " F3600\n"
                tmpText += "G1 X" + str(startPoint[0]) + " Y" + str(startPoint[1]) + " Z" + str(startPoint[2]) + " E" + str(self.EValue) + " F1800\n"

            self.gcoder.addGcode(tmpText)

        rs.DeleteObjects(lines)
        rs.DeleteObject(newSliceSurface)
        rs.DeleteObject(baseLine)
        '''


        self.gcoder.addGcode("; layer filling\n")
        for i in range(int(dist/self.gcoder.getLayerHeight()+1)):
            lines = []

            nextVec = (baseVec[0]*(self.gcoder.getLayerHeight()*i), baseVec[1]*(self.gcoder.getLayerHeight()*i), baseVec[2]*(self.gcoder.getLayerHeight()*i))

            #horizontal
            if index%2 == 0:

                nextStartPoint = (editPoints[0][0]+nextVec[0], editPoints[0][1]+nextVec[1], editPoints[0][2]+nextVec[2])
                nextEndPoint = (editPoints[1][0]+nextVec[0], editPoints[1][1]+nextVec[1], editPoints[1][2]+nextVec[2])

            #vertical
            elif index%2 == 1:
                nextStartPoint = (editPoints[0][0] + nextVec[0], editPoints[0][1] + nextVec[1], editPoints[0][2] + nextVec[2])
                nextEndPoint = (editPoints[2][0] + nextVec[0], editPoints[2][1] + nextVec[1], editPoints[2][2] + nextVec[2])

            nextLine = rs.AddLine(nextStartPoint, nextEndPoint)

            pnts = rs.CurveCurveIntersection(intersectCurve, nextLine)

            #debug
            if pnts == None:
                #DEBUG may needs
                rs.DeleteObject(nextLine)
                continue

            if len(pnts) < 2:
                continue
            elif len(pnts)%2 == 1:
                print('num of pnts is odd')

            else:
                for j in range(int(len(pnts)/2)):
                    if i%2 == 0:
                        lines.append(rs.AddLine(pnts[2*j][1], pnts[(2*j)+1][1]))
                    else:
                        lines.append(rs.AddLine(pnts[2*int(len(pnts)/2-j) - 1][1], pnts[2*int(len(pnts)/2-j) - 2][1]))


            rs.DeleteObject(nextLine)

            #make gcode from lines
            for j in lines:
                startPoint = rs.CurveStartPoint(j)
                endPoint = rs.CurveEndPoint(j)

                self.calcEValue(startPoint, endPoint)

                tmpText = "G1 X" + str(startPoint[0]) + " Y" + str(startPoint[1]) + " Z" + str(startPoint[2]) + " F3600\n"
                tmpText += "G1 X" + str(endPoint[0]) + " Y" + str(endPoint[1]) + " Z" + str(endPoint[2]) + " E" + str(self.EValue) + " F1800\n"

                self.gcoder.addGcode(tmpText)

            rs.DeleteObjects(lines)

        rs.DeleteObject(newSliceSurface)
        rs.DeleteObject(baseLine)





    """
    at now, infill is cross
    """

    def setInfill(self, vec, intersectCurve):

        '''
        DEBUG needs
        this functiono is to verbose
        '''

        '''
        horizontal
        '''

        if self.gcoder.getInfillRatio == 0:
            return


        #offset intersectCurve
        editPointsOfIntersectCurve = rs.CurveEditPoints(intersectCurve[0])
        dirVec = [0, 0, 0]
        for i in editPointsOfIntersectCurve:
            dirVec[0] += i[0]
            dirVec[1] += i[1]
            dirVec[2] += i[2]


        dirVec[0] /= len(editPointsOfIntersectCurve)
        dirVec[1] /= len(editPointsOfIntersectCurve)
        dirVec[2] /= len(editPointsOfIntersectCurve)

        dirVec = tuple(dirVec)

        intersectCurve = rs.OffsetCurve(intersectCurve[0], dirVec, self.gcoder.getLayerHeight())

        #&offset intersectCurve

        newSliceSurface = rs.CopyObject(self.sliceSurface, vec)
        editPoints = rs.SurfaceEditPoints(newSliceSurface)

        baseLine = rs.AddLine(editPoints[0], editPoints[1])

        baseVec = (editPoints[2][0]-editPoints[0][0], editPoints[2][1]-editPoints[0][1], editPoints[2][2]-editPoints[0][2])
        tmp = math.sqrt(baseVec[0]**2 + baseVec[1]**2 + baseVec[2]**2)
        baseVec = (baseVec[0]/tmp, baseVec[1]/tmp, baseVec[2]/tmp)

        dist = rs.Distance(editPoints[0], editPoints[2])

        lines = []


        interval = self.gcoder.getLayerHeight() * (1.0 / self.gcoder.getInfillRatio())

        for i in range(int(dist/interval + 1)):
            nextVec = (baseVec[0] * (interval * i), baseVec[1] * (interval * i) , baseVec[2] * (interval * i))

            nextStartPoint = (editPoints[0][0] + nextVec[0], editPoints[0][1] + nextVec[1], editPoints[0][2] + nextVec[2])
            nextEndPoint = (editPoints[1][0] + nextVec[0], editPoints[1][1] + nextVec[1], editPoints[1][2] + nextVec[2])

            nextLine = rs.AddLine(nextStartPoint, nextEndPoint)

            points = rs.CurveCurveIntersection(intersectCurve, nextLine)


            if points == None or len(points) < 2:
                rs.DeleteObject(nextLine)
                continue

            else:

                lines.append(rs.AddLine(points[0][1], points[1][1]))

            rs.DeleteObject(nextLine)

        tmpText = "; layer infill\n"
        self.gcoder.addGcode(tmpText)

        for i in range(len(lines)):

            startPoint = rs.CurveStartPoint(lines[i])
            endPoint = rs.CurveEndPoint(lines[i])

            self.calcEValue(startPoint, endPoint)
            if i%2 == 0:
                tmpText = "G1 X" + str(startPoint[0]) + " Y" + str(startPoint[1]) + " Z" + str(startPoint[2]) + " F1800\n"
                tmpText += "G1 X" + str(endPoint[0]) + " Y" + str(endPoint[1]) + " Z" + str(endPoint[2]) + " E" + str(self.EValue) + "\n"
            else:
                tmpText = "G1 X" + str(endPoint[0]) + " Y" + str(endPoint[1]) + " Z" + str(endPoint[2]) + " F1800\n"
                tmpText += "G1 X" + str(startPoint[0]) + " Y" + str(startPoint[1]) + " Z" + str(startPoint[2]) + " E" + str(self.EValue) + "\n"

            self.gcoder.addGcode(tmpText)

        rs.DeleteObjects(lines)
        rs.DeleteObject(newSliceSurface)
        rs.DeleteObject(baseLine)


        '''
        vertical
        '''
        newSliceSurface = rs.CopyObject(self.sliceSurface, vec)
        editPoints = rs.SurfaceEditPoints(newSliceSurface)

        baseLine = rs.AddLine(editPoints[0], editPoints[2])

        baseVec = (editPoints[1][0]-editPoints[0][0], editPoints[1][1]-editPoints[0][1], editPoints[1][2]-editPoints[0][2])
        tmp = math.sqrt(baseVec[0]**2 + baseVec[1]**2 + baseVec[2]**2)
        baseVec = (baseVec[0]/tmp, baseVec[1]/tmp, baseVec[2]/tmp)

        dist = rs.Distance(editPoints[0], editPoints[1])

        lines = []

        interval = self.gcoder.getLayerHeight() * (1.0 / self.gcoder.getInfillRatio())

        for i in range(int(dist/interval + 1)):
            nextVec = (baseVec[0] * (interval * i), baseVec[1] * (interval * i) , baseVec[2] * (interval * i))

            nextStartPoint = (editPoints[0][0] + nextVec[0], editPoints[0][1] + nextVec[1], editPoints[0][2] + nextVec[2])
            nextEndPoint = (editPoints[2][0] + nextVec[0], editPoints[2][1] + nextVec[1], editPoints[2][2] + nextVec[2])

            nextLine = rs.AddLine(nextStartPoint, nextEndPoint)

            points = rs.CurveCurveIntersection(intersectCurve, nextLine)


            if points == None or len(points) < 2:
                rs.DeleteObject(nextLine)
                continue

            else:

                lines.append(rs.AddLine(points[0][1], points[1][1]))

            rs.DeleteObject(nextLine)

        self.gcoder.addGcode(tmpText)

        for i in range(len(lines)):

            startPoint = rs.CurveStartPoint(lines[i])
            endPoint = rs.CurveEndPoint(lines[i])

            self.calcEValue(startPoint, endPoint)
            if i%2 == 0:
                tmpText = "G1 X" + str(startPoint[0]) + " Y" + str(startPoint[1]) + " Z" + str(startPoint[2]) + " F1800\n"
                tmpText += "G1 X" + str(endPoint[0]) + " Y" + str(endPoint[1]) + " Z" + str(endPoint[2]) + " E" + str(self.EValue) + "\n"
            else:
                tmpText = "G1 X" + str(endPoint[0]) + " Y" + str(endPoint[1]) + " Z" + str(endPoint[2]) + " F1800\n"
                tmpText += "G1 X" + str(startPoint[0]) + " Y" + str(startPoint[1]) + " Z" + str(startPoint[2]) + " E" + str(self.EValue) + "\n"

            self.gcoder.addGcode(tmpText)

        rs.DeleteObjects(lines)
        rs.DeleteObject(newSliceSurface)
        rs.DeleteObject(baseLine)

        return




    def calcEValue(self, prePoint, nextPoint):
        dist = rs.Distance(prePoint, nextPoint)

        self.EValue += (dist * self.gcoder.getLayerHeight() * self.gcoder.getExtruderDiameter()) / \
                        float(math.pi * (float(self.gcoder.getFilamentDiameter()/2.0) ** 2))


    def clean(self):

        rs.DeleteObject(self.sliceSurface)
        return




'''
gcodeGenerater

this class is used for making gcode file
'''

class gcodeGenerater():

    def __init__(self):

        self.fileName = "testGcode.gcode"
        self.textGcode = ""

        self.layerHeight = 0.15
        self.extruderDiameter = 0.4
        self.filamentDiameter = 1.75
        self.tempExtruder = 210
        self.infillRatio = 0.02


        self.numBottomLayer = 2
        self.numTopLayer = 4
        self.numShellOutline = 2



    def initGcode(self):
        self.textGcode = ""

        self.textGcode += "G90\n" # set to absolute positioning
        self.textGcode += "M82\n" # set extruder to absolute mode
        self.textGcode += "M106 S255\n" # fan on
        self.textGcode += "M104 S" + str(self.tempExtruder) + " T0\n" # set extruder temperture
        self.textGcode += "M109 S" + str(self.tempExtruder) + " T0\n" # set extruder temperture and wait
        self.textGcode += "G28\n" #go home

        self.textGcode += "G92 E0\n" # set position: E -> new extruder position
        self.textGcode += "G1 E-1.0000 F1800\n" # retract

    def addGcode(self, code):
        self.textGcode += code

    def finishGcode(self):
        self.textGcode += "G92 E0\n"
        self.textGcode += "G1 E-1.0000 F18000\n"
        self.textGcode += "M104 S0\n"
        self.textGcode += "M140 S0\n"
        self.textGcode += "G28\n"
        self.textGcode += "M84\n"

    def outputFile(self):
        fileN = rs.SaveFileName("Output file", "G-Code Files (*.gcode)|*.gcode|All Files (*.*)|*.*|", None, self.fileName)
        with open(fileN, "w") as f:
            f.writelines(self.textGcode)
            f.close()

        print("Successfly gcode file is output")

    #setter
    def setFileName(self, _fileName):
        self.fileName = _fileName

    def setLayerHeight(self, _layerHeight):
        self.layerHeight = _layerHeight

    def setExtruderDiameter(self, _extruderDiameter):
        self.extruderDiameter = _extruderDiameter

    def setFilamentDiameter(self, _filamentDiameter):
        self.filamentDiameter = _filamentDiameter

    def setInfillRatio(self, _infillRatio):
        self.infillRatio = _infillRatio

    def setNumShellOutline(self, _numShellOutline):
        self.numShelOutline = _numShellOutline

    def setNumTopLayer(self, _numTopLayer):
        self.numTopLayer = _numTopLayer

    def setNumBottomLayer(self, _numBottomLayer):
        self.numBottomLayer = _numBottomLayer


    #getter
    def getLayerHeight(self):
        return self.layerHeight

    def getExtruderDiameter(self):
        return self.extruderDiameter

    def getFilamentDiameter(self):
        return self.filamentDiameter

    def getInfillRatio(self):
        return self.infillRatio

    def getNumShellOutline(self):
        return self.numShellOutline

    def getNumTopLayer(self):
        return self.numTopLayer

    def getNumBottomLayer(self):
        return self.numBottomLayer



'''
main
'''

def main():

    gcoder = gcodeGenerater()

    aam = AAM_Planar(gcoder)
    aam.main()


if __name__ == "__main__":
    main()
