import sys
from os import path, remove
from pathlib import PurePath, Path

from PyQt5.QtCore import Qt, QPointF, QSizeF
from PyQt5.QtGui import QTextDocument, QFont
from qgis._core import QgsGeometry, QgsFeature, QgsPoint, QgsFeatureSink, QgsTextAnnotation
from qgis._gui import QgsRubberBand
from qgis.utils import iface

from .Connection_2_Jar import Connection

ruta = str(Path(path.join(path.dirname(__file__), r'sbrpaux.txt')))
rutasolucion = str(Path(path.join(path.dirname(__file__), r'sbrpsolucion.txt')))

def writePoint2File(file,layer):

        with(open(file, 'a'))as file2jar:
            for featureDict in layer.getFeatures():
                xpoint, ypoint = featureDict.geometry().asPoint() #is not a point return [0,0]
                file2jar.write(str(xpoint) + ' ')
                file2jar.write(str(ypoint) + '\n')



def process_solution(path_solution, stopFeatures,feedback):

    students_2_stops = []

    try:

        with open(path_solution, 'r') as solution_file:
            line_solution = solution_file.readline().split(';')
            students_2_stops = line_solution[0].replace('[', '').replace(']', '').strip().split(',')
            students_2_stops = list(map(lambda x: int(x), students_2_stops))
            routes = line_solution[1].replace('[', '').strip().split('],')
            route_result = []

            for indexf, r in enumerate(routes):
                routes_format = r.replace(']]', '').split(',')
                points_routes = []
                for r_format in routes_format:
                    index = int(r_format)
                    points_routes.append(stopFeatures[index])


                route_result.append(points_routes)


            solution_file.close()

    except Exception as e:
        feedback.reportError('Not solution found for this data form', True)


    if path.exists(rutasolucion):
       pass

    return True,students_2_stops,stopFeatures,route_result


def file2jar(depotPoint, cantidad_autobuses, capacity, layer_stops, layer_students, maximum_walking,feedback):

    with open(ruta, 'w') as file:

        cantidad_paradas = layer_stops.featureCount()
        cantidad_estudiantes = layer_students.featureCount()

        file.write(str(cantidad_paradas) + ' ' + str(cantidad_estudiantes) + ' ' + str(cantidad_autobuses) + ' '
                       + str(capacity) + ' ' +
                       str(maximum_walking) + '\n')

        file.write(str(depotPoint.x()) + ' ')
        file.write(str(depotPoint.y()) + '\n')

        file.close()

    writePoint2File(ruta, layer_stops)
    writePoint2File(ruta, layer_students)

    p = Path(path.dirname(__file__))
    path_join = path.join(p, 'jarAccess', 'JARSBRP.jar')
    jarConnection = Connection(Path(path_join))
    jarConnection.run_jar(ruta + ' ' + rutasolucion)
    feedback.pushInfo(str('Jar connection sucess'))
    feedback.setProgress(50)

    featureList = list(layer_stops.getFeatures())
    f = QgsFeature()
    f.setGeometry(QgsGeometry.fromPointXY(depotPoint))

    featureList.insert(0,f)
    return process_solution(rutasolucion,featureList ,feedback)



def addAnotation(text,point,crs):
    annotation = QgsTextAnnotation()

    document = QTextDocument(text)
    document.setDefaultFont(QFont("Arial", 15))
    annotation.setDocument(document)

    annotation.setFrameSize(QSizeF(100, 50))

    annotation.setFrameOffsetFromReferencePoint(QPointF(30, 30))
    annotation.setMapPosition(point)
    annotation.setMapPositionCrs(crs)
    return annotation


def addRubberBand(feature,color='red'):
    rubber = QgsRubberBand(iface.mapCanvas(), False)  # si no es un poligono
    rubber.setToGeometry(feature.geometry())
    rubber.setWidth(0.9)
    rubber.setColor(color)
    rubber.setLineStyle(Qt.PenStyle(Qt.DashLine))