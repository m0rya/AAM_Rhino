
def slice(self):

    self.gcoder.initGcode()

    tmpText = ""

    multiplier = float(self.gcoder.getLayerHeight() * math.cos(math.radians(self.angleOfBaseSurface)))

    #layer by layer
    for layer in range(int(self.distancePrinting/multiplier)+1):

        tmpText = "; layer " + str(layer) + "\n"
        #init evalue
        tmpText += "G92 E0\n"
        self.gcoder.initEValue()

        nextVec = (0, 0, float(multiplier*i))
        slicer = rs.CopyObject(self.sliceSurface, nextVec)

        slicedCurves = rs.IntersectBreps(self.addtiveObj, slicer)

        if slicedCurves == None:
            print('slicing done')
            return

        #slicedCurve one by one
        for slicedCurve in slicedCurves:

            makeGcodeFromSlicedCurve(slicedCurve, layer, nextVec)




def makeGcodeFromSlicedCurve(self, slicedCurve, layer, vec):

    editPointsOfIntersectCurve = rs.CurveEditPoints(slicedCurve)

    dirVec = [0,0,0]
    for l in editPointsOfIntersectCurve:
        dirVec[0] += l[0]
        dirVec[1] += l[1]
        dirVec[2] += l[2]

    dirVec = [i/len(editPointsOfIntersectCurve) for i in dirVec]

    #shell by shell
    for shell in range(self.gcoder.getNumShellOutline()):

        offsetCurve = rs.OffsetCurve(slicedCurve, tuple(dirVec), self.gcoder.getLayerHeight() * k)

        explodedCurve = rs.ExplodeCurves(offsetCurve)

        #lines from explodedCurve
        #from outline to gcode
        prePoint = None
        for line in range(len(explodedCurve)):

            startPoint = rs.CurveStartPoint(explodedCurve[line])
            tmpText += "G1 X" + str(startPoint[0]) + " Y" + str(startPoint[1]) + " Z" + str(startPoint[2])

            if line == 0:
                #just move
                tmpText += " F1800\n"
            else:
                self.gcoder.calcEValue(self.prePoint, startPoint)
                tmpText + " E" + str(self.gcoder.getEValue()) + "\n"

            if line == (len(explodedCurve)-1):
                endPoint = rs.CurveEndPoint(explodedCurve[line])
                self.calcEValue(startPoint, endPoint)
                tmpText += "G1 X" + str(endPoint[0]) + " Y" + str(endPoint[1]) + " Z" + str(endPoint[2]) + " E" + str(self.gcoder.getEValue) + "\n"

            prePoint = startPoint
        self.gcoder.addGcode(tmpText)


        #from outline to fill gocde
        #if shell is last one, it needs to fill layer or infill
        '''
        if shell == (self.gcoder.getNumShellOutline()-1):
            newOffsetCurve = rs.OffsetCurve(offsetCurve, tuple(dirVec), self.gcoder.getLayerHeight())

            if layer == (self.gcoder.getBottomLayer()):
                self.setLayerFill(vec, newOffsetCurve, layer)

            elif i > (int(self.distancePrinting/multilier) - self.gcoder.getNumTopLayer()):

                self.setLayerFill(vec, newOffsetCurve, layer)

            else:
                self.setInfill(vec, newOffsetCurve)
        '''

        def setLayerFill(self, vec, intersectCurve, index):

        #set baseline, baseVec, dist
        newSliceSurface = rs.CopyObject(self.sliceSurface, vec)
        editPoints = rs.SurfaceEditPoints(newSliceSurface)

        #vertical
        if index%2 == 0:

            baseLine = rs.AddLine(editPoints[0], editPoints[1])
            baseVec = (editPoints[2][0]-editPoints[0][0], editPoints[2][1]-editPoints[0][1], editPoints[2][2]-editPoints[0][2])
            dist = rs.Distannce(editPonts[0], editPoints[2])

        #horizontal
        elif index%2 == 1:

            baseLine = rs.AddLine(editPoints[0], editPoints[2])
            baseVec = (editPoints[1][0]-editPoints[0][0], editPoints[1][1]-editPoints[0][1], editPoints[1][2]-editPoints[0][2])
            dist = rs.Distannce(editPonts[0], editPoints[1])

        #normalize baseVec
        forNormal = math.sqrt(baseVec[0]**2 + baseVec[1]**2 + baseVec[2]**2)
        baseVec = [i/forNormal for i in baseVec]

        #end set baseLine, baseVec, dist

        self.gcoder.addGcode("; layer filling\n")

        for i in range(int(dist/self.gcoder.getLayerHeight())+1):
            lines = []

            nextVec = [v*self.gcoder.getLayerHeight()*i for v in baseVec]

            #vertical
            if index%2 == 0:
                nextStartPoint = (editPoints[0][0]+nextVec[0], editPoints[0][1]+nextVec[1], editPoints[0][2]+nextVec[2])
                nextEndPoint = (editPoints[1][0]+nextVec[0], editPoints[1][1]+nextVec[1], editPoints[1][2]+nextVec[2])

            if index%2 == 1:
                nextStartPoint = (editPoints[0][0]+nextVec[0], editPoints[0][1]+nextVec[1], editPoints[0][2]+nextVec[2])
                nextEndPoint = (editPoints[2][0]+nextVec[0], editPoints[2][1]+nextVec[1], editPoints[2][2]+nextVec[2])

            nextLine = (nextStartPoint), (nextEndPoint)

            intersectedPoint = rs.CurveCurveIntersect(nextLine, intersectCurve)
            intersectedPoint = [n[1] for n in intersectedPoint]


            if intersectedPoint == None:
                print('there is no intersectedPoint')
                rs.DeleteObject(nextLine)
                rs.DeleteObject(intersectedPoint)
                continue

            if len(intersectedPoint)%2 == 0:
                for j in range(int(len(intersectedPoint)/2)):
                    if i%2 == 0:
                        lines.append(rs.AddLine(intersectedPoint[2*j], intersectedPoint[(2*j)+1]))
                    else:
                        lines.append(rs.AddLine(intersectedPoint[2*int(len(intersectedPoint)/2-j)-1], intersectedPoint[2*int(len(intersectedPoint)/2-j)-2]))

            elif len(intersectedPoint)%2 == 1:
                #check there is no duplicate point with intersectCurve
                #DEBUG needs
                intersectedPoint = self.deleteAlonePoint(intersectedPoint, intersectCurve)

            rs.DeleteObject(nextLine)

            for j in lines:
                startPoint = rs.CurveStartPoint(j)
                endPoint = rs.CurveEndPoint(j)

                self.gcoder.calcEValue(startPoint, endPoint)

                tmpText = "G1 X" + str(startPoint[0]) + " Y" + str(startPoint[1]) + " Z" + str(startPoint[2]) + " F3600\n"
                tmpText += "G1 X" + str(endPoint[0]) + " Y" + str(endPoint[1]) + " Z" + str(endPoint[2]) + " E" + str(self.gcoder.getEValue()) + " F1800\n"

                self.gcoder.addGcode(tmpText)

            rs.DeleteObjects(lines)

    def deleteAlonePoint(self, points, intersectCurve):
        editPoint = rs.CurveEditPoint(intersectCurve)

        for i in editPoint:

            for j in range(len(points)):

                if rs.Distance(i,points[j]) == 0.0:
                    points.pop(j)

        return points


    def setInfill(self, vec, intersectCurve):
        if self.gcoder.getInfillRatio == 0:
            return

        newSliceSurface = rs.CopyObject(self.sliceSurface, vec)
        editPoints = rs.SurfaceEditPoints(newSliceSurface)

        #horizontal

        baseLien = rs.AddLine(editPonts[0], editPoints[1])
        baseVec = (editPoints[2][0]-editPoints[0][0], eidtPoints[2][1]-editPoints[0][1], editPoints[2][1]-editPoints[0][2])
        forNormalize = math.sqrt(baseVec[0]**2 + baseVec[1]**2 + baseVec[2]**2)
        baseVec = [i/forNormalize for i in baseVec]

        dist = rs.Distance(editPoints[0], editPoints[2])


        lines = []

        interval = self.gcoder.getLayerHeight() * (1.0 / self.gcoder.getInfillRatio())

        #prepare horizontal lines
        for i in range(int(dist/interval + 1)):
            nextVec = [j*(interval*i) for j in baseVec]

            nextStartPoint = (editPoints[0][0]+nextVec[0], editPoints[0][1]+nextVec[1], editPoints[0][2]+nextVec[2])
            nextEndPoint = (editPoints[1][0]+nextVec[0], editPoints[1][1]+nextVec[1], editPoints[1][2]+nextVec[2])

            nextLine = rs.AddLine(nextStartPoint, nextEndPoint)

            if nextLine == None or intersectCurve == None:
                print("hogehoge")
                continue

            intersectedPoint  = rs.CurveCurveIntersection(nextLine, intersectCurve)
            intersectedPoint = [n[1] for n in intersectedPoint]


            if intersectedPoint == None:
                print('there is no intersectedPoint')
                rs.DeleteObject(nextLine)
                rs.DeleteObject(intersectedPoint)
                continue

            if len(intersectedPoint)%2 == 0:
                for j in range(int(len(intersectedPoint)/2)):
                    if i%2 == 0:
                        lines.append(rs.AddLine(intersectedPoint[2*j], intersectedPoint[(2*j)+1]))
                    else:
                        lines.append(rs.AddLine(intersectedPoint[2*int(len(intersectedPoint)/2-j)-1], intersectedPoint[2*int(len(intersectedPoint)/2-j)-2]))

            elif len(intersectedPoint)%2 == 1:
                #check there is no duplicate point with intersectCurve
                #DEBUG needs
                intersectedPoint = self.deleteAlonePoint(intersectedPoint, intersectCurve)

            rs.DeleteObject(nextLine)

        self.gcoder.addGcode("; layer infill\n")

        for i in range(len(lines)):
            startPoint = rs.CurveStartPont(lines[i])
            endPoint = rs.CurveEndPoint(liens[i])

            self.gcoder.clacEValue(startPoint, endPoint)

            if i%2 == 0:
                tmpText = "G1 X" + str(startPoint[0]) + " Y" + str(startPoint[1]) + " Z" + str(startPoint[2]) + " F3600\n"
                tmpText += "G1 X" + str(endPoint[0]) + " Y" + str(endPoint[1]) + " Z" + str(endPoint[2]) + " E" + str(self.gcoder.getEValue()) + " F1800\n"
            else:

                tmpText += "G1 X" + str(endPoint[0]) + " Y" + str(endPoint[1]) + " Z" + str(endPoint[2]) + " F3600\n
                tmpText = "G1 X" + str(startPoint[0]) + " Y" + str(startPoint[1]) + " Z" + str(startPoint[2]) +" E" + str(self.gcoder.getEValue()) + " F1800\n"

            self.gcoder.addGcode(tmpText)

        rs.DeleteObjects(lines)
        rs.DeleteObject(baseLine)



        #vertical

        baseLien = rs.AddLine(editPonts[0], editPoints[2])
        baseVec = (editPoints[1][0]-editPoints[0][0], eidtPoints[1][1]-editPoints[0][1], editPoints[1][1]-editPoints[0][2])
        forNormalize = math.sqrt(baseVec[0]**2 + baseVec[1]**2 + baseVec[2]**2)
        baseVec = [i/forNormalize for i in baseVec]

        dist = rs.Distance(editPoints[0], editPoints[1])


        lines = []

        interval = self.gcoder.getLayerHeight() * (1.0 / self.gcoder.getInfillRatio())

        #prepare horizontal lines
        for i in range(int(dist/interval + 1)):
            nextVec = [j*(interval*i) for j in baseVec]

            nextStartPoint = (editPoints[0][0]+nextVec[0], editPoints[0][1]+nextVec[1], editPoints[0][2]+nextVec[2])
            nextEndPoint = (editPoints[2][0]+nextVec[0], editPoints[2][1]+nextVec[1], editPoints[2][2]+nextVec[2])

            nextLine = rs.AddLine(nextStartPoint, nextEndPoint)

            if nextLine == None or intersectCurve == None:
                print("hogehoge")
                continue

            intersectedPoint  = rs.CurveCurveIntersection(nextLine, intersectCurve)
            intersectedPoint = [n[1] for n in intersectedPoint]


            if intersectedPoint == None:
                print('there is no intersectedPoint')
                rs.DeleteObject(nextLine)
                rs.DeleteObject(intersectedPoint)
                continue

            if len(intersectedPoint)%2 == 0:
                for j in range(int(len(intersectedPoint)/2)):
                    if i%2 == 0:
                        lines.append(rs.AddLine(intersectedPoint[2*j], intersectedPoint[(2*j)+1]))
                    else:
                        lines.append(rs.AddLine(intersectedPoint[2*int(len(intersectedPoint)/2-j)-1], intersectedPoint[2*int(len(intersectedPoint)/2-j)-2]))

            elif len(intersectedPoint)%2 == 1:
                #check there is no duplicate point with intersectCurve
                #DEBUG needs
                intersectedPoint = self.deleteAlonePoint(intersectedPoint, intersectCurve)

            rs.DeleteObject(nextLine)

        self.gcoder.addGcode("; layer infill\n")

        for i in range(len(lines)):
            startPoint = rs.CurveStartPont(lines[i])
            endPoint = rs.CurveEndPoint(liens[i])

            self.gcoder.clacEValue(startPoint, endPoint)

            if i%2 == 0:
                tmpText = "G1 X" + str(startPoint[0]) + " Y" + str(startPoint[1]) + " Z" + str(startPoint[2]) + " F3600\n"
                tmpText += "G1 X" + str(endPoint[0]) + " Y" + str(endPoint[1]) + " Z" + str(endPoint[2]) + " E" + str(self.gcoder.getEValue()) + " F1800\n"
            else:

                tmpText += "G1 X" + str(endPoint[0]) + " Y" + str(endPoint[1]) + " Z" + str(endPoint[2]) + " F3600\n
                tmpText = "G1 X" + str(startPoint[0]) + " Y" + str(startPoint[1]) + " Z" + str(startPoint[2]) +" E" + str(self.gcoder.getEValue()) + " F1800\n"

            self.gcoder.addGcode(tmpText)

        rs.DeleteObjects(lines)
        rs.DeleteObject(baseLine)


        return
