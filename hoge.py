import rhinoscriptsyntax as rs

curve = rs.GetCurveObject()
print('curve')
print(curve)

editPoints = rs.CurveEditPoints(curve[0])
print(editPoints)

x = 0
y = 0
z = 0
for i in editPoints:
    x += i[0]
    y += i[1]
    z += i[2]

x /= len(editPoints)
y /= len(editPoints)
z /= len(editPoints)

dir = rs.AddPoint((x,y,z))

rs.OffsetCurve(curve[0], dir, 2)
