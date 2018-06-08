import rhinoscriptsyntax as rs
import math

class gcodeGenerater():

    def __init__(self):

        self.fileName = "testGcode.gcode"
        self.textGcode = ""

        self.layerHeight = 0.15
        self.extruderDiameter = 0.4
        self.filamentDiameter = 1.75
        self.extrudeTemperture = 195
        self.infillRatio = 15

        self.numBottomLayer = 2
        self.numTopLayer = 4
        self.numShellOutline = 2

        self.EValue = 0
        #self.EValueRatio = 1.0
        self.EValueRatio = 1.0

        self.retractionDistance = -1.0

        self.f = None



    def initGcode(self, fileN):
        self.textGcode = ""

        self.textGcode += "G90\n" # set to absolute positioning
        self.textGcode += "M82\n" # set extruder to absolute mode
        self.textGcode += "M106 S255\n" # fan on
        self.textGcode += "M104 S" + str(self.extrudeTemperture) + " T0\n" # set extruder temperture
        self.textGcode += "M109 S" + str(self.extrudeTemperture) + " T0\n" # set extruder temperture and wait
        self.textGcode += "G28\n" #go home

        self.textGcode += "G92 E0\n" # set position: E -> new extruder position
        self.textGcode += "G1 E-1.0000 F1800\n" # retract

        self.f = open(fileN, "w")
        self.f.writelines(self.textGcode)

    def addGcode(self, code):
        #self.textGcode += code
        self.f.writelines(code)

    def finishGcode(self):
        self.textGcode = "G92 E0\n"
        self.textGcode += "G1 E-1.0000 F18000\n"
        self.textGcode += "M104 S0\n"
        self.textGcode += "M140 S0\n"
        self.textGcode += "G28\n"
        self.textGcode += "M84\n"

        self.f.writelines(self.textGcode)

    def outputFile(self):
        '''
        with open(fileN, "w") as f:
            f.writelines(self.textGcode)
            f.close()
        '''

        self.f.close()
        print("Successfly gcode file is output")


    def calcEValue(self, dist):
        self.EValue += self.EValueRatio * float(dist * self.getLayerHeight() * self.getExtruderDiameter()) / \
                        float(math.pi * (float(self.getFilamentDiameter()/2.0) ** 2))

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
        self.numShellOutline = _numShellOutline

    def setNumTopLayer(self, _numTopLayer):
        self.numTopLayer = _numTopLayer

    def setNumBottomLayer(self, _numBottomLayer):
        self.numBottomLayer = _numBottomLayer

    def initEValue(self):
        self.f.writelines("G92 E0\n")
        self.EValue = 0

    def setEValue(self, _EValue):
        self.EValue = _EValue

    def setExtrudeTemperture(self, _extrudeTemperture):
        self.extrudeTemperture = _extrudeTemperture

    def setRetractionDistance(self, _retractionDistance):
        self.retractionDistance = _retractionDistance

    def setEValueRatio(self, _EValueRatio):
        self.EValueRatio = _EValueRatio



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

    def getEValue(self):
        return self.EValue
    def getExtrudeTemperture(self):
        return self.extrudeTemperture

    def getFilamentDiameter(self):
        return self.filamentDiameter

    def getExtruderDiameter(self):
        return self.extruderDiameter

    def getRetractionDistance(self):
        return self.retractionDistance


class hairBuilder():

    def __init__(self, _gcoder):

        self.gcoder = _gcoder

        self.hairRootLine = None
        self.intervalOfHair = 1.5
        self.lengthOfHair = 10



        #extruding
        self.speedOfExtrude = 500
        self.angleOfLine = 15
        self.ratioOfExtrudeHair = 0.9
        self.extrudeSpeedAtStartPoint = 100
        #endPoint
        self.waitTime = 0
        self.anotherAheadSpeed = 400
        self.retractAtEndPoint = 2.4
        #temperture
        self.extrudeTemperture = 230
        self.coolTemperture = 170

        #startPoint
        #self.extrudeValueAtStartPoint = 1 + self.retractAtEndPoint
        self.extrudeValueAtStartPoint = 2.4

        self.travelSpeed = 3600


        #gcoder
        self.gcoder.setEValueRatio(self.ratioOfExtrudeHair)
        self.gcoder.setExtruderDiameter(0.4)
        self.gcoder.setExtrudeTemperture(self.extrudeTemperture)


        #debug
        self.exportG = True


    def setHairRootLineFromRhino(self):
        self.hairRootLine = rs.GetObjects(filter=rs.filter.curve)

    def setHairRootLine(self, _line):
        self.hairRootLine = _line


    def setLengthOfHair(self, _length):
        self.lengthOfHair = _length

    def setIntervalOfHair(self, _interval):
        self.intervalOfHair = _interval


    def buildHair(self):
        self.setHairRootLineFromRhino()

        print("=================")
        print("parameters")
        print("interval of hair         : {0}".format(self.intervalOfHair))
        print("length of hair           : {0}".format(self.lengthOfHair))
        print("extrude at start point   : {0}".format(self.extrudeValueAtStartPoint))
        print("speed of extrude         : {0}".format(self.speedOfExtrude))
        print("angle of Line            : {0}".format(self.angleOfLine))
        print("ratio of extrude hair    : {0}".format(self.ratioOfExtrudeHair))
        print("wait time                : {0}".format(self.waitTime))
        print("retract at end point     : {0}".format(self.retractAtEndPoint))
        print("another ahead speed      : {0}".format(self.anotherAheadSpeed))
        print("extrude temperture       : {0}".format(self.extrudeTemperture))
        print("cool temperture          : {0}".format(self.coolTemperture))
        print("extrude speed at start point : {0}".format(self.extrudeSpeedAtStartPoint))
        print("================")

        if self.exportG:
            fileN = rs.SaveFileName("Output file", "G-Code Files (*.gcode)|*.gcode|All Files (*.*)|*.*|")
            self.gcoder.initGcode(fileN)


        self.rootCount = 0
        for i in self.hairRootLine:

            points = rs.DivideCurve(i, int(rs.CurveLength(i)/self.intervalOfHair))
            #fabnow
            rs.AddPoints(points)

            self.prePoint = None

            self.angleOfLine += 3
            self.rootCount += 1


            for itr, point in enumerate(points):

                '''
                #hairDir is selfish
                hairDir = (1, 0, 0)
                hairDir = rs.VectorScale(hairDir, self.lengthOfHair)
                '''

                '''
                #hairDir is normal
                if itr is 0:
                    tmpLine = rs.AddLine(point, points[itr+1])
                    tmpLine = rs.RotateObject(tmpLine, point, 180)

                elif itr is (len(points)-1):
                    tmpLine = rs.AddLine(point, points[itr-1])
                    rs.AddLine(rs.CurveStartPoint(tmpLine), rs.CurveEndPoint(tmpLine))

                else:
                    tmpLine = rs.AddLine(point, self.prePoint)


                rotatedLine = rs.RotateObject(tmpLine, point, 90)
                hairDir = rs.VectorCreate(rs.CurveEndPoint(rotatedLine), point)
                hairDir = rs.VectorScale(hairDir, self.lengthOfHair)

                rs.DeleteObject(tmpLine)
                self.prePoint = point


                endPoint = rs.PointAdd(point, hairDir)
                nextLine = rs.AddLine(point, endPoint)
                '''

                if(self.rootCount%2 == 1):
                    if(itr == len(points)-1):
                        continue
                    else:
                        tmpVec = (points[itr+1][0] - point[0], points[itr+1][1] - point[1], points[itr+1][2] - point[2])
                        point  = (point[0] + tmpVec[0]/2, point[1] + tmpVec[1]/2, point[2] + tmpVec[2]/2)




                nextLine = rs.AddLine(point, (point[0] + self.lengthOfHair, point[1], point[2]));

                vecLine = rs.VectorCreate(rs.CurveStartPoint(nextLine), rs.CurveEndPoint(nextLine))
                vecLine = rs.VectorRotate(vecLine, 90, (0,0,1))
                nextLine = rs.RotateObject(nextLine, rs.CurveStartPoint(nextLine), self.angleOfLine, vecLine)


                ePoint = rs.CurveEndPoint(nextLine)



                #G-Code

                if self.exportG:

                    #recover temperture
                    '''
                    tmpGcode = "M104 S{0} T0\n".format(self.extrudeTemperture)
                    tmpGcode += "M109 S{0} T0\n".format(self.extrudeTemperture)
                    self.gcoder.addGcode(tmpGcode)
                    self.gcoder.initEValue()
                    '''

                    #move to first point
                    tmpGcode = "G0 X{0} Y{1} Z{2} F3600\n".format(point[0], point[1], point[2])
                    self.gcoder.addGcode(tmpGcode)

                    #param1 : extrude at Start point
                    tmpGcode = "G1 Z{0} E{1} F{2}\n".format(point[2]+1.0, self.extrudeValueAtStartPoint, self.extrudeSpeedAtStartPoint)
                    self.gcoder.addGcode(tmpGcode)
                    self.gcoder.initEValue()

                    #param2 : ratio of extrude hair is already setup
                    self.gcoder.calcEValue(rs.CurveLength(nextLine))

                    #param3 : extrude speed
                    tmpGcode = "G1 X{0} Y{1} Z{2} F{3} E{4}\n".format(ePoint[0], ePoint[1], ePoint[2], self.speedOfExtrude, self.gcoder.getEValue())
                    self.gcoder.addGcode(tmpGcode)

                    '''
                    #param4 : wait at end point
                    tmpGcode = "G4 P{0}\n".format(self.waitTime)
                    self.gcoder.addGcode(tmpGcode)
                    '''

                    #param5 : retract at end point
                    '''
                    self.gcoder.initEValue()
                    tmpGcode = "G1 E{0}\n".format(-self.retractAtEndPoint)
                    self.gcoder.addGcode(tmpGcode)
                    '''
                    self.gcoder.initEValue();
                    tmpGcode = "G92 E0\n"



                    #move ahead
                    moveAheadVec = rs.VectorCreate(rs.CurveEndPoint(nextLine), rs.CurveStartPoint(nextLine))
                    '''
                    moveAheadVec[0] *= 2
                    moveAheadVec[1] *= 2
                    moveAheadVec[2] *= 2
                    '''
                    anotherTarget = rs.PointAdd(ePoint, moveAheadVec)

                    tmpGcode = "G0 X{0} Y{1} Z{2} E{3} F{4}\n".format(anotherTarget[0], anotherTarget[1], anotherTarget[2], -self.retractAtEndPoint, self.anotherAheadSpeed)
                    self.gcoder.addGcode(tmpGcode)

                    self.gcoder.addGcode("G92 E0\n")


                    #para temp : cool nozzle
                    '''
                    tmpGcode = "M104 S{0} T0\n".format(self.coolTemperture)
                    tmpGcode += "M109 S{0} T0\n".format(self.coolTemperture)
                    self.gcoder.addGcode(tmpGcode)
                    '''


                    #go to next start point
                    tmpGcode = "G0 Z{0} F{1}\n".format(ePoint[2] + 50, self.travelSpeed)
                    self.gcoder.addGcode(tmpGcode)

                    tmpGcode = "G0 X{0} Y{1} F{2}\n".format(point[0], point[1], self.travelSpeed)
                    self.gcoder.addGcode(tmpGcode)






                #fabnow
                #rs.DeleteObject(nextLine)

        if self.exportG:
            self.gcoder.finishGcode()
            self.gcoder.outputFile()

        return



def main():
    _gcoder = gcodeGenerater()

    hair = hairBuilder(_gcoder)


    hair.buildHair()



'''
def main():

    gcoder = gcodeGenerater()

    fileN = rs.SaveFileName("Output file", "G-Code Files (*.gcode)|*.gcode|All Files (*.*)|*.*|")
    gcoder.initGcode(fileN)


    surface = rs.GetObject("select surface")

    editPoints = rs.SurfaceEditPoints(surface)

    baseLine = rs.AddLine(editPoints[0], editPoints[1])

    baseVec = (editPoints[2][0]-editPoints[0][0], editPoints[2][1]-editPoints[0][1], editPoints[2][2]-editPoints[0][2])
    forNormal = math.sqrt(baseVec[0]**2 + baseVec[1]**2 + baseVec[2]**2)
    baseVec = [i/forNormal for i in baseVec]







    for i in range(20):
        tmpText = ""
        gcoder.initEValue()

        nextVec = [1.0 * i * v for v in baseVec]

        line = rs.CopyObject(baseLine, nextVec)


        startP = rs.CurveStartPoint(line)
        endP = rs.CurveEndPoint(line)
        endP[2] += 20.0*math.tan(math.radians(45))

        hairLine = rs.AddLine(startP, endP)
        tmpText = "G1 X{0} Y{1} F2000\n".format(startP[0], startP[1])
        tmpText += "G1 Z{0}\n".format(startP[2])
        tmpText += "G1 E0.5 F1000\n"
        gcoder.setEValue(0.5)
        tmpText += "G4 P500\n"

        #tmpText += "G92 E0\n"
        gcoder.calcEValue(rs.Distance(startP, endP))
        tmpText += "G1 X{0} Y{1} Z{2} E{3} F1800\n".format(endP[0], endP[1], endP[2], gcoder.getEValue())




        retractEnd = (endP[0], endP[1]+10, endP[2])

        retractLine = rs.AddLine(endP, retractEnd)
        tmpText += "G4 P2000\n"
        tmpText += "G92 E0\n"
        tmpText += "G1 E-5 F1800\n"
        tmpText += "G1 X{0} Y{1} Z{2} F1000\n".format(retractEnd[0], retractEnd[1], retractEnd[2])
        tmpText += "G1 Z{0} F2000\n".format(retractEnd[2] + 50)


        gcoder.addGcode(tmpText)


        rs.DeleteObject(line)
        rs.DeleteObject(hairLine)
        rs.DeleteObject(retractLine)


    gcoder.finishGcode()
    gcoder.outputFile()

'''


if __name__ == "__main__":
    main()
