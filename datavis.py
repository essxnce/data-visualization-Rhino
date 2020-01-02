import rhinoscriptsyntax as rs
import Rhino
import scriptcontext
import System.Drawing

def exportData():
    # Generating sensor points
    pts = setSensorLocation()

    # Make csv file
    file_object = open("points1.csv", "w")

    # import sensor value
    file_data = open("values.csv", "r")
    data = file_data.readlines()

    valList = []

    for index in range(0, len(data)):
        valNum = float(data[index])
        valList.append(valNum)

    maxNum = max(valList)
    minNum = min(valList)

    # index initialization
    i = 0

    # Writing csv file: iteration
    for pt in pts:
        coord = rs.PointCoordinates(pt)

        dataLine = str(coord)
        dataLine = dataLine + " ," + data[i]

        val = float(data[i])

        visLine = makeHeight(pt, val)
        pipe = makePipe(visLine)

        # Making layers and their colors depending on value
        color = mapVal2Color(minNum, maxNum, i, val)

        rs.EnableRedraw(False)

        # Visualization: assigning layer to point
        #rs.ObjectLayer(pt, layername)
        #rs.ObjectLayer(visLine, layername)
        #rs.ObjectLayer(pipe, layername)

        # GUID to Brep
        pipeBrep = rs.coercebrep(pipe)

        AddMaterial(pipeBrep, i, color)
        
        rs.DeleteObject(pt)
        rs.DeleteObject(visLine)
        rs.DeleteObject(pipe)

        i = i + 1
        file_object.writelines(dataLine)

    file_object.close()
    file_data.close()
    print("data export done")



# Making curve corresponding heights
def makeHeight(pt, val):
    originalPt = rs.CopyObject(pt)
    vector = (0, 0, val)
    movedPt = rs.MoveObject(pt, vector)
    
    line = [originalPt, movedPt]
    lineID = rs.AddLine(line[0], line[1])

    return lineID


# Making pipe based on curves
def makePipe(lineID):
    pipe = rs.AddPipe(lineID, 0, 0.1, cap = 1)

    return pipe



def mapVal2Color(minNum, maxNum, i, val):
    startNum = minNum
    endNum = maxNum
    length = (endNum - startNum) / 5


    val = float(val)
    
    if val > (startNum + 4*length):
        Red = 255
        Green = 125 - ((val - (startNum + 4*length)) / length) * 125 
        Blue = 0
        
        color = Red, Green, Blue
            
    elif val > (startNum + 3*length):
        Red = 255
        Green = 255 - ((val - (startNum + 3*length)) / length) * 125
        Blue = 0
        
        color = Red, Green, Blue
        
    elif val > (startNum + 2*length):
        Red = ((val - (startNum + 2*length)) / length) * 255
        Green = 255
        Blue = 0
        
        color = Red, Green, Blue
        
    elif val > (startNum + length):
        Red = 0
        Green = 255
        Blue = 255 - ((val - (startNum + length)) / length) * 125
        
        color = Red, Green, Blue
        
    else:
        color = 0, 255, 255
    
    # layername = str(i + 1)
    # rs.AddLayer(layername)
    # rs.LayerColor(layername, color)
    
    return color




def AddMaterial(obj, index, color):   
    # materials are stored in the document's material table
    index = scriptcontext.doc.Materials.Add()
    mat = scriptcontext.doc.Materials[index]
    color = System.Drawing.Color.FromArgb(color[0], color[1], color[2])

    mat.DiffuseColor = color
    mat.Name = str(index)
    mat.CommitChanges()

    # set up object attributes to say they use a specific material
    attr = Rhino.DocObjects.ObjectAttributes()
    attr.MaterialIndex = index
    attr.MaterialSource = Rhino.DocObjects.ObjectMaterialSource.MaterialFromObject
    scriptcontext.doc.Objects.AddBrep(obj, attr)




def setSensorLocation():
    projectedPtList = []

    # Select boundary surface
    boundarySrf = rs.GetObject("Select surface for making boundary", rs.filter.surface)

    # For making location point with grid
    direction = (0, 0, 100)
    plane = rs.MoveObject(boundarySrf, direction)


    # Dividing surface to points
    ptList = ArrayPointsOnSurface(plane)

    # point projection
    projectedSrf = rs.GetObject("Select surface for projection", rs.filter.surface)
    for point in ptList:
        pointsOnModel = rs.ProjectPointToSurface(point, projectedSrf, (0, 0, 1))
        projectedPt = rs.AddPoint(pointsOnModel[0][0], pointsOnModel[0][1], pointsOnModel[0][2])
        projectedPtList.append(projectedPt)

    rs.DeleteObjects(plane)
    rs.DeleteObjects(ptList)

    return projectedPtList




def ArrayPointsOnSurface(srf):
    ptList = []
    
    # Get the number of rows
    rows = 51

    # Get the number of columns
    cols = 51

    # Get the domain of the surface
    u, v = rs.SurfaceDomain(srf, 0), rs.SurfaceDomain(srf, 1)


    # Turn off redrawing (faster)
    rs.EnableRedraw(False)


    # Add the points
    for i in range(rows):
        s = u[0] + ((u[1]-u[0])/(rows-1))*i
        for j in range(cols):
            t = v[0] + ((v[1]-v[0])/(cols-1))*j
            pt = rs.EvaluateSurface(srf, s, t)
            obj = rs.AddPoint(pt) # add the point
            ptList.append(obj)

    return ptList

    # Turn on redrawing
    rs.EnableRedraw(True)




if __name__ == '__main__':
    exportData()
    rs.EnableRedraw(True)
