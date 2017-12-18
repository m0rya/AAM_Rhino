import rhinoscriptsyntax as rs
import Rhino as rhino



class TextureOnSurface():

    def __init__(self, _gcoder):
        self.gcoder = _gcoder



    def main(self):
        self.setContactSurface()

        self.setBaseSurface()

        #self.setPrintingSetting(self)




        return

    def setContactSurface(self):
        self.contactSurface = rs.GetObject("Select contact Surface")


        return


    def setBaseSurface(self):


        explodedSurfaces = rs.ExplodePolysurfaces(self.contactSurface)
        editPoint = []


        #get editPoint from polysurfaces
        if len(explodedSurfaces) == 0:
            #use obj
            meshed = rhino.Geometry.Mesh.CreateFromBrep(rs.coercebrep(self.addtiveObj))
            editPoint = rs.MeshVertices(meshed[0])

        else:
            for i in explodedSurfaces:
                meshed = rhino.Geometry.Mesh.CreateFromBrep(rs.coercebrep(i))
                vertices = rs.MeshVertices(meshed[0])
                editPoint.extend(vertices)

        rs.DeleteObjects(explodedSurfaces)



        minValue = []
        maxValue = []
        basePointForPlane = None
        basePointForDistance = None

        for i in range(len(editPoint)):
            if i == 0:
                basePointForPlane = editPoint[0]
                basePointForDistance = editPoint[0]

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

        #why?

        plane = rs.PlaneFromNormal(basePointForPlane, (0,0,1))

        #make base surface
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


        joinedCurve = rs.JoinCurves(lineForSur)
        #curveForSur = rs.OffsetCurve(joinedCurve, rs.CurveNormal(joinedCurve), 50)


        self.sliceSurface = rs.AddPlanarSrf(joinedCurve)

        if rs.IsPointOnSurface(self.sliceSurface, rs.CurveStartPoint(joinedCurve)) is False:

            rs.DeleteObject(curveForSur)
            rs.DeleteObject(self.sliceSurface)

            curveForSur = rs.OffsetCurve(joinedCurve, rs.CurveNormal(joinedCurve), 50)
            self.baseSurface = rs.AddPlanarSrf(curveForSur)


        #Delete lines used for making sliceSurface
        rs.DeleteObjects(lineForSur)
        rs.DeleteObject(joinedCurve)


    def makeTexture(self):
        return




    def setPrintingSetting(self):
        self.setExtruderDiameter()
        self.setFilamentDiameter()
        self.setExtrudeTemperture()

        self.setLayerHeight()
        self.setNumShellOutline()
        self.setNumTopLayer()
        self.setNumBottomLayer()
        self.setInfillRatio()


    #setter

    def setExtruderDiameter(self):
        self.gcoder.setExtruderDiameter(rs.GetReal("Extruder Diameter", 0.4))

    def setFilamentDiameter(self):
        self.gcoder.setFilamentDiameter(rs.GetReal("Filament Diameter", 1.75))

    def setExtrudeTemperture(self):
        self.gcoder.setExtrudeTemperture(rs.GetReal("Extrude Temperture", 195))

    def setLayerHeight(self):
        self.gcoder.setLayerHeight(rs.GetReal("Layer Height", 0.15))

    def setNumShellOutline(self):
        self.gcoder.setNumShellOutline(int(rs.GetReal("Num of Shell Outline", 2)))


    def setNumTopLayer(self):
        self.gcoder.setNumTopLayer(int(rs.GetReal("Num of Top Layer", 2)))

    def setNumBottomLayer(self):
        self.gcoder.setNumBottomLayer(int(rs.GetReal("Num of Bottom Layer", 2)))

    def setInfillRatio(self):
        self.gcoder.setInfillRatio(rs.GetReal("Infill Ratio", 5))






class gcodeGenerater():

    def __init__(self):

        self.fileName = "testGcode.gcode"
        self.textGcode = ""

        self.layerHeight = 0.2
        self.extruderDiameter = 0.4
        self.filamentDiameter = 1.75
        self.extrudeTemperture = 210
        self.infillRatio = 0.02

        self.numBottomLayer = 2
        self.numTopLayer = 4
        self.numShellOutline = 3

        self.EValue = 0

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
        self.EValue += float(dist * self.getLayerHeight() * self.getExtruderDiameter()) / \
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
        self.EValue = 0

    def setExtrudeTemperture(self, _extrudeTemperture):
        self.extrudeTemperture = _extrudeTemperture




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


def main():
    gcoder = gcodeGenerater()
    hoge = TextureOnSurface(gcoder)
    hoge.main()

if __name__ == "__main__":
    main()
