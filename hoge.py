import rhinoscriptsyntax as rs


fileN = rs.SaveFileName("output file", "G-Code Files (*.gcode)|*.gcode|All Files (*.*)|*.*|", None, None)
