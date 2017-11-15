import rhinoscriptsyntax as rs

class gcodeGenerater():

    def __init__(self):

        self.fileName = "testGcode.gcode"
        self.textGcode = ""

        self.layerHeight = 0.15
        self.extruderDiameter = 0.4
        self.filamentDiameter = 1.75

        self.tempExtruder = 210


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

    def finishGcode():
        self.textGcode += "G92 E0\n"
        self.textGcode += "G1 E-1.0000 F18000\n"
        self.textGcode += "M104 S0\n"
        self.textGcode += "M140 S0\n"
        self.textGcode += "G28\n"
        self.textGcode += "M84\n"

    def outputFile():
        fileN = rs.saveFileName("Output file", "G-Code Files (*.gcode)|*.gcode|All Files (*.*)|*.*|", None, self.FileName)
        with ooen(fileN, "w") as f:
            f.writeliens(self.textGcode)
            f.close()

    #setter
    def setFileName(self, _fileName):
        self.fileName = _fileName

    def setLayerHeight(self, _layerHeight):
        self.layerHeight = _layerHeight

    def setExtruderDiameter(self, _extruderDiameter):
        self.extruderDiameter = _extruderDiameter

    def setFilamentDiameter(self, _filamentDiameter):
        self.filamentDiameter = _filamentDiameter
