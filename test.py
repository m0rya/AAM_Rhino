import rhinoscriptsyntax as rs

curve = rs.GetObject()
cutter = rs.GetObject()



'''
filter 1 => cut outside of cutter
filter 2 => cut inside of cutter
'''
def trim(curve, cutter, filter = 1):
    resultLines = []

    intersectedPoints = rs.CurveCurveIntersection(curve, cutter)
    tmpSurface = rs.AddPlanarSrf(cutter)

    intersectedPoints = [n[1] for n in intersectedPoints]

    intersectedPoints.insert(0, rs.CurveStartPoint(curve))
    intersectedPoints.insert(len(intersectedPoints), rs.CurveEndPoint(curve))

    for i in range(len(intersectedPoints)-1):

        x = intersectedPoints[i][0] + intersectedPoints[i+1][0]
        y = intersectedPoints[i][1] + intersectedPoints[i+1][1]
        z = intersectedPoints[i][2] + intersectedPoints[i+1][2]

        mid = (x/2.0, y/2.0, z/2.0)

        if rs.IsPointOnSurface(tmpSurface, mid):
            if filter == 1:
                resultLines.append(rs.AddLine(intersectedPoints[i], intersectedPoints[i+1]))
            elif filter == 2:
                continue

        else:
            if filter == 1:
                continue
            elif filter == 2:
                resultLines.append(rs.AddLine(intersectedPoints[i], intersectedPoints[i+1]))


    rs.DeleteObject(curve)
    rs.DeleteObject(tmpSurface)

    return resultLines



trim(curve, cutter, 2)
