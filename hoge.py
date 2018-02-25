import rhinoscriptsyntax as rs
import Rhino as rhino


#Trim Debuging




def offsetNonPlanarCurve(curve, sliceSurface, planarSurface):

    """
    1. project curve to planarBaseSurface
    2. projected curve is planar, so it can be offset
    3. project offseted curve to contactSurface
    4. move projected curve to place should be, Z-Axis

    i guess that this procedure works
    Try it
    """

    planarCurve = rs.ProjectCurveToSurface(curve, planarSurface, (0, 0, 1))

    offsetedCurve = rs.OffsetCurve(planarCurve, (0,0,1), -0.4)



    if rs.CurveArea(offsetedCurve)[0] > rs.CurveArea(planarCurve)[0] or len(offsetedCurve) > 1:
        rs.DeleteObjects(offsetedCurve)
        offsetedCurve = rs.OffsetCurve(planarCurve, (0,0,1), 0.4)


    reProjectedCurve = rs.ProjectCurveToSurface(offsetedCurve, sliceSurface, (0, 0, 1))

    return reProjectedCurve


"""
if offseted curve is open Curve
you can fix that curve to closed curve by below code
"""

def fixOpenCurve2ClosedCurve(curve):


    startPoint = rs.CurveStartPoint(curve)

    explodedCurves = rs.ExplodeCurves(curve)
    editPoints = rs.CurveEditPoints(curve)

    rs.DeleteObject(explodedCurves[0])
    rs.DeleteObject(explodedCurves[-1])

    #debug
    rs.AddPoint(rs.CurveStartPoint(explodedCurves[1]))
    rs.AddPoint(rs.CurveEndPoint(explodedCurves[-2]))
    rs.AddPoint(startPoint)

    fixedLine1 = rs.AddLine(startPoint, rs.CurveStartPoint(explodedCurves[1]))
    fixedLine2 = rs.AddLine(startPoint, rs.CurveEndPoint(explodedCurves[-2]))

    del explodedCurves[0]
    del explodedCurves[-1]
    explodedCurves.append(fixedLine1)
    explodedCurves.append(fixedLine2)
    rs.DeleteObjects(explodedCurves)

    resultLine = rs.JoinCurves(explodedCurves)

    return resultLine



curve = rs.GetObject()
surface = rs.GetObject()

result = rs.OffsetCurveOnSurface(curve, surface, -0.6)
print('result is')
print(result)


'''
print(rs.IsCurveClosable(offsetedCurve))
rs.CloseCurve(offsetedCurve)
'''
'''
print(offseted)

print(rs.IsCurveClosed(offseted))



if rs.IsCurveClosed(offseted) is False:
    print('fixing')
    closedCurve = fixOpenCurve2ClosedCurve(offseted)
'''





def trim(curve, cutter):
    resultLines = []

    intersectedPoints = rs.CurveCurveIntersection(curve, cutter)
    if intersectedPoints == None:
        return None

    #when cutter is not planar, tmpSurface will be non

    intersectedPoints = [n[1] for n in intersectedPoints]

    if len(intersectedPoints)%2 == 1:
        print("In trim(), there is weird")
        return resultLines

    #convert point to curve parameter
    curveParas = []
    for i in intersectedPoints:
        curveParas.append(rs.CurveClosestPoint(curve, i))
    print(curveParas)

    for i in range(int(len(curveParas)/2)):
        tmp = []
        tmp.append(curveParas[i*2])
        tmp.append(curveParas[i*2+1])

        resultLines.append(rs.TrimCurve(curve, tmp))

    '''
    for i in range(int(len(intersectedPoints)/2)):
        resultLines.append(rs.AddLine(intersectedPoints[i*2], intersectedPoints[i*2+1]))
    '''

    return resultLines




'''
projectedLine = rs.ProjectCurveToSurface(testLine, planarSurface, (0,0,1))

offseted = rs.OffsetCurve(projectedLine, (0,0,1), -0.15)

reProjectedLine = rs.ProjectCurveToSurface(offseted, baseSurface, (0,0,1))

rs.MoveObject(reProjectedLine, (0, 0, 1.5))
'''





def offsetNonPlanarCurve(self, curve, distance, layerIndex):

    """
    1. project curve to planarBaseSurface
    2. projected curve is planar, so it can be offset
    3. project offseted curve to contactSurface
    4. move projected curve to place should be, Z-Axis

    i guess that this procedure works
    Try it
    """


    return True

'''
contactSurface = rs.GetObject("Select contact surface")

explodedSurface = rs.ExplodePolysurfaces(contactSurface)
editPoint = []
for i in explodedSurface:
    meshed = rhino.Geometry.Mesh.CreateFromBrep(rs.coercebrep(i))
    editPoint.extend(rs.MeshVertices(meshed[0]))

'''

'''
borderLine = rs.DuplicateSurfaceBorder(contactSurface)

#normalVec = rs.CurveAreaCentroid(borderLine)
nozzleDia = 0.4
#offsetBorderLine = rs.OffsetCurve(borderLine, (0,0,0), -(nozzleDia/2.0 + nozzleDia*1))
rs.OffsetCurveOnSurface(borderLine, contactSurface, 1)
rhino.Geometry.Curve.Offset()
'''


'''
result = rs.ProjectCurveToSurface(line, surface, (0,0,1))
print(result)

border = rs.DuplicateSurfaceBorder(surface)

offseted = rs.OffsetCurve(border, (0,0,1), -0.15)
projectedOffset = rs.ProjectCurveToSurface(offseted, surface, (0,0,1))
'''




def setSurfaceForSlicing(_surface):


    explodedSurfaces = rs.ExplodePolysurfaces(_surface)
    editPoint = []

    #get editPoint from polysurfaces
    if len(explodedSurfaces) == 0:
        #use obj
        meshed = rhino.Geometry.Mesh.CreateFromBrep(rs.coercebrep(_surface))
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

    plane = rs.PlaneFromNormal((0,0,80), (0, 0, 1))
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
    curveForSur = rs.OffsetCurve(joinedCurve, rs.CurveNormal(joinedCurve), 10)

    sliceSurface = rs.AddPlanarSrf(curveForSur)

    #Delete lines used for making sliceSurface
    rs.DeleteObjects(lineForSur)

    return sliceSurface



#sliceSurface = setSurfaceForSlicing(surface)



'''
offseted = rs.OffsetCurve(obj, rs.CurveNormal(obj), 10)
sliceSurface = rs.AddPlanarSrf(offseted)

if rs.IsPointOnSurface(sliceSurface, rs.CurveStartPoint(obj)):
    print('done')
else:
    rs.DeleteObject(offseted)
    rs.DeleteObject(sliceSurface)
    offseted = rs.OffsetCurve(obj, rs.CurveNormal(obj), -10)
    sliceSurface = rs.AddPlanarSrf(offseted)

'''


'''
if rs.IsCurveClosed(obj) is False:
    print('hoge')
    hoge = rs.CloseCurve(obj)
    print(rs.IsCurveClosable(obj))
    print(hoge)

'''



#print(rs.CurveEditPoints(rs.ConvertCurveToPolyline(obj)))

'''
print(obj)
meshed = rhino.Geometry.Mesh.CreateFromBrep(rs.coercebrep(obj))
hoge = rs.MeshVertices(meshed[0])
tmp = rs.SurfaceEditPoints(obj)
print(tmp)
for i in hoge:
    rs.AddPoint(i)
'''
'''

def setSurfaceForSlicing(_obj):

    explodedSurfaces = rs.ExplodePolysurfaces(_obj)
    editPoint = []

    #get editPoint from polysurfaces
    if len(explodedSurfaces) == 0:
        #use obj
        meshed = rhino.Geometry.Mesh.CreateFromBrep(rs.coercebrep(_obj))
        editPoint = rs.MeshVertices(meshed[0])

        #de
        for i in editPoint:
            rs.AddPoint(i)
        return 0

    for i in explodedSurfaces:
        meshed = rhino.Geometry.Mesh.CreateFromBrep(rs.coercebrep(i))
        vertices = rs.MeshVertices(meshed[0])
        editPoint.extend(vertices)

    #de
    for i in editPoint:
        rs.AddPoint(i)

    rs.DeleteObjects(explodedSurfaces)


    #make surface fro slicing
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
    self.basePointForPlane = basePointForPlane

    plane = rs.PlaneFromNormal(basePointForPlane, self.normalVec)


    #calculating distance printing
    self.calcDistance(plane, editPoint)

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

    self.sliceSurface = rs.AddEdgeSrf(lineForSur)

    self.fixedLayerHeight = float(self.gcoder.getLayerHeight() * (1.0 / math.cos(math.radians(self.angleOfSurface))))

    self.sliceSurface = rs.MoveObject(self.sliceSurface, (0, 0, self.fixedLayerHeight*0.9))


    #Delete lines used for making sliceSurface
    rs.DeleteObjects(lineForSur)
    rs.DeleteObjects(explodedSurfaces)




setSurfaceForSlicing(obj)

'''



'''
explodedSurfaces = rs.ExplodePolysurfaces(obj)

for i in explodedSurfaces:
    tmp = rs.SurfaceEditPoints(i)

    if isinstance(tmp, list):
        for j in tmp:
            #if rs.IsPointOnSurface(i, j):
            rs.AddPoint(j)
    else:
        #if rs.IsPointOnSurface(tmp, j):
        rs.AddPoint(j)
rs.DeleteObjects(explodedSurfaces)
'''

'''

def setSurfaceForSlicing(self):
    explodedSurfaces = None

    editPoint = []
    explodedSurfaces = rs.ExplodePolysurfaces(self.addtiveObj)
    for i in explodedSurfaces:
        tmp = rs.SurfaceEditPoints(i)

        if isinstance(tmp, list):
            for j in tmp:
                if rs.IsPointOnSurface(i, j):
                    editPoint.append(j)
        else:
            if rs.IsPointOnSurface(tmp, j):
                editPoint.append(j)
        #editPoint.extend(tmp)

    #rs.CullDuplicatePoints(editPoint)


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
    self.basePointForPlane = basePointForPlane

    plane = rs.PlaneFromNormal(basePointForPlane, self.normalVec)


    #calculating distance printing
    self.calcDistance(plane, editPoint)

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

    self.sliceSurface = rs.AddEdgeSrf(lineForSur)

    self.fixedLayerHeight = float(self.gcoder.getLayerHeight() * (1.0 / math.cos(math.radians(self.angleOfSurface))))

    self.sliceSurface = rs.MoveObject(self.sliceSurface, (0, 0, self.fixedLayerHeight*0.9))


    #Delete lines used for making sliceSurface
    rs.DeleteObjects(lineForSur)
    rs.DeleteObjects(explodedSurfaces)
'''
