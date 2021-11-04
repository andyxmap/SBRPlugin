from builtins import str

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.PyQt.QtGui import QIcon
from qgis.core import (QgsField, QgsProcessing,
                       QgsFields,
                       QgsProcessingProvider,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterPoint,
                       QgsProcessingParameterNumber,
                       QgsFeatureSink, QgsWkbTypes)

import os
from .util import *


plugin_dir = os.path.dirname(__file__)

routes_fields = QgsFields()
routes_fields.append(QgsField('Route id',QVariant.Int))

order_fields = QgsFields()
order_fields.append(QgsField('Route id',QVariant.Int))
order_fields.append(QgsField('Order',QVariant.String))
order_fields.append(QgsField('Stop id',QVariant.Int))

est_fields = QgsFields()
est_fields.append(QgsField('Stop id',QVariant.Int))


#Esta clase es la representacion de un algoritmo de procesamiento
class SBRProcessing(QgsProcessingAlgorithm):
    STOPS = 'STOPS'
    STUDENTS = 'STUDENTS'
    DEPOT = 'DEPOT'
    MAXDISTANCE = 'MAXDISTANCE'
    CAPACITY = 'CAPACITY'
    OUTPUT = 'OUTPUT'
    BUSES = 'BUSES'
    ROUTPUT = 'ROUTPUT'
    ESTOUTPUT = 'ESTOUTPUT'

    def __init__(self):
        QgsProcessingAlgorithm.__init__(self)


    def icon(self):
        return QIcon(os.path.join(plugin_dir, 'icon.png'))

    def name(self):
        return 'sbrprocessing'

    def groupId(self):
        return 'sbrplugin'

    def group(self):
        return'Creacion de Rutas'

    def displayName(self):
        return self.tr('SBRP')

    def createInstance(self):
        return SBRProcessing()

    def tr(self,string):
        return QCoreApplication.translate('Processing',string)

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(self.STOPS,
                                                              self.tr('Layer identify Stops'),
                                                              [QgsProcessing.TypeVectorPoint]))

        self.addParameter(QgsProcessingParameterFeatureSource(self.STUDENTS,
                                                              self.tr('Layer identify Students'),
                                                              [QgsProcessing.TypeVectorPoint]))
        self.addParameter(QgsProcessingParameterPoint(self.DEPOT,
                                                      self.tr('Depot point')))

        self.addParameter(QgsProcessingParameterNumber(self.BUSES,
                                                       self.tr('Number of Buses'),
                                                       QgsProcessingParameterNumber.Integer,minValue=0))

        self.addParameter(QgsProcessingParameterNumber(self.CAPACITY,
                                                       self.tr('Bus Capacity'),
                                                       QgsProcessingParameterNumber.Integer,minValue=0))

        self.addParameter(QgsProcessingParameterNumber(self.MAXDISTANCE,
                                                       self.tr('Max Walking Distance for the students'),
                                                       QgsProcessingParameterNumber.Double,minValue=0))


        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT,self.tr('Routes'),
                                                            QgsProcessing.TypeVectorLine))

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.ROUTPUT, self.tr('Routes Order'),
                                              QgsProcessing.TypeVectorPoint))

        self.addParameter(QgsProcessingParameterFeatureSink(self.ESTOUTPUT,self.tr('Students to Stops'),
                                                            QgsProcessing.TypeVectorLine))

        

    def processAlgorithm(self, parameters, context, feedback):
        feedback.pushInfo(self.tr('Init the algorithm'))

        stop = self.parameterAsSource(parameters,self.STOPS,context)
        students = self.parameterAsSource(parameters, self.STUDENTS, context)
        depotPoint = self.parameterAsPoint(parameters,self.DEPOT,context)
        maxd = self.parameterAsDouble(parameters,self.MAXDISTANCE,context)
        bus = self.parameterAsInt(parameters,self.BUSES,context)
        capacity = self.parameterAsInt(parameters, self.CAPACITY, context)




        ok,student,stopList,routes = file2jar(depotPoint,
                      bus,
                      capacity,
                      stop,
                      students,maxd,feedback)

        if ok:
            (sink, idOutput) = self.parameterAsSink(parameters,
                                                    self.OUTPUT, context,
                                                    routes_fields,
                                                    QgsWkbTypes.LineString,
                                                    context.project().crs())

            (sink_route, idOutput_route) = self.parameterAsSink(parameters,
                                                                self.ROUTPUT, context,
                                                                order_fields,
                                                                QgsWkbTypes.Point,
                                                                context.project().crs())

            (sink_est, idOutput_est) = self.parameterAsSink(parameters,
                                                            self.ESTOUTPUT, context,
                                                            est_fields,
                                                            QgsWkbTypes.Point,
                                                            context.project().crs())

            studentsList = list(students.getFeatures())


            for index,route in enumerate(routes):
                polyline = []

                for ind,o in enumerate(route):

                    f = QgsFeature()
                    f.setGeometry(QgsGeometry.fromWkt(o.geometry().asWkt()))
                    f.setAttributes([index,ind,o.id()])

                    sink_route.addFeature(f,QgsFeatureSink.FastInsert)
                    polyline.append(f.geometry().asPoint())

                f = QgsFeature()
                f.setGeometry(QgsGeometry.fromPolylineXY(polyline))
                f.setAttributes([index])
                sink.addFeature(f, QgsFeatureSink.FastInsert)

            for student_index in student:
                feat = QgsFeature()
                feat.setGeometry(QgsGeometry.fromWkt(studentsList[student_index].geometry().asWkt()))
                feat.setAttributes([stopList[student_index].id()])
                
                sink_est.addFeature(feat,QgsFeatureSink.FastInsert)

        feedback.setProgress(100)

        return {
                self.OUTPUT:idOutput,
                self.ROUTPUT:idOutput_route,
                self.ESTOUTPUT:idOutput_est
               }


class SBRProcessingProvider(QgsProcessingProvider):
    def __init__(self):
        QgsProcessingProvider.__init__(self)

    def unload(self):
        iface.messageBar().pushMessage('SBRP Plugin Removed')

    def id(self):
        return 'sbrprocessingprovider'

    def loadAlgorithms(self):
        self.addAlgorithm(SBRProcessing())

    def name(self):
        return 'Optimizacion'


