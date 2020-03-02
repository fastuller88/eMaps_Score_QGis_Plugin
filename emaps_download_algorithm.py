# -*- coding: utf-8 -*-

"""
/***************************************************************************
 Emaps
                                 A QGIS plugin
 Herramienta de Evaluación a Microescala de Ambientes Peatonales
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-09-25
        copyright            : (C) 2019 by LlactaLab | Universidad de Cuenca
        email                : llactalab@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'LlactaLab | Universidad de Cuenca'
__date__ = '2019-09-25'
__copyright__ = '(C) 2019 by LlactaLab | Universidad de Cuenca'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import json
import time
import csv
import inspect
import qgis.core
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtCore import QCoreApplication, QVariant
import pyproj

from qgis.core import (QgsField,
                       QgsFields,
                       QgsProcessing,
                       QgsFeature,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterString,
                       QgsProcessingParameterAuthConfig,
                       QgsProcessingFeedback,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFileDestination,
                       QgsMessageLog,
                       QgsVectorLayer,
                       QgsProcessingUtils,
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsPointXY)
import processing
from processing.core.Processing import Processing
from .emaps_download_api import EmapsDownloadApi

epsg4326 = QgsCoordinateReferenceSystem('EPSG:4326')

class EmapsDownloadAlgorithm(QgsProcessingAlgorithm):
    """
    eMAPS Download evaluation data Algorithm
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT_SEGMENTS = 'OUTPUT_SEGMENTS'
    OUTPUT_PARCELS = 'OUTPUT_PARCELS'

    INPUT_KPI_LINK = 'INPUT_KPI_LINK'
    INPUT_USER = 'INPUT_USER'
    INPUT_PASSWORD = 'INPUT_PASSWORD'
    INPUT_FORM_ID = 'INPUT_FORM_ID'
    INPUT_COD_ESTUDIO = 'INPUT_COD_ESTUDIO'
    INPUT_NOMBRE_USUARIO = 'INPUT_NOMBRE_USUARIO'
    

    dest_segments = None
    dest_areas = None

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        self.addParameter(
            QgsProcessingParameterString(
                self.INPUT_KPI_LINK,
                self.tr('🔗 Dirección URL KoboToolBox)'),
                defaultValue='https://kf.kobotoolbox.org/'
            )
        )

         
        self.addParameter(
            QgsProcessingParameterString(
                self.INPUT_USER,
                self.tr('👤 Usuario KoboToolBox'),
                defaultValue='maps'
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.INPUT_PASSWORD,
                self.tr('🔑 Contraseña KoboToolBox'),
                defaultValue='maps_2018'
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.INPUT_FORM_ID,
                self.tr('🆔 Código del Formulario'),
                defaultValue='acqYb67ZLjbQnKXt9HdSn5'
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.INPUT_COD_ESTUDIO,
                self.tr('🔍 Código del Estudio (opcional)')
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.INPUT_NOMBRE_USUARIO,
                self.tr('🔍 Nombre de usuario evaluador (opcional)')
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT_SEGMENTS,
                self.tr('OUTPUT: Tabla de evaluación de segmentos .CSV'),
                'CSV files (*.csv)'
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT_PARCELS,
                self.tr('OUTPUT: Tabla de evaluación de lotes .CSV'),
                'CSV files (*.csv)'
            )
        )
       
       

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the pre processing itself takes place.
        """
        t = time.time()
        feedback.pushInfo("⚙ Conectando con servidor KoboToolBox 🌐💾...")

        kpi_url = self.parameterAsString(parameters, self.INPUT_KPI_LINK, context)
        kobo_user = self.parameterAsString(parameters, self.INPUT_USER, context)
        kobo_password = self.parameterAsString(parameters, self.INPUT_PASSWORD, context)
        kobo_form_id = self.parameterAsString(parameters, self.INPUT_FORM_ID, context)
        kobo_cod_estudio = self.parameterAsString(parameters, self.INPUT_COD_ESTUDIO, context)
        kobo_nombre_usuario = self.parameterAsString(parameters, self.INPUT_NOMBRE_USUARIO, context)

        params = {
            "form_id": kobo_form_id,
            "cod_estudio": kobo_cod_estudio,
            "nombre_usuario": kobo_nombre_usuario
        }
        kobo_api = EmapsDownloadApi(feedback, kpi_url, kobo_user, kobo_password)

        data = kobo_api.get_form_data(params)
        print(data)

        segments_csv = self.parameterAsFileOutput(parameters, self.OUTPUT_SEGMENTS, context)
        parcels_csv = self.parameterAsFileOutput(parameters, self.OUTPUT_PARCELS, context)

        segments_data = data["segments_data"]
        parcels_data = data["parcels_data"]

        csv_columns = sorted(segments_data[0].keys())
        print(csv_columns)
        csv_file = segments_csv
        try:
            with open(csv_file, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                writer.writeheader()
                for data in segments_data:
                    writer.writerow(data)
        except IOError:
            print("I/O error")
            
            
        csv_columns = sorted(parcels_data[0].keys())
        print(csv_columns)
        csv_file = parcels_csv
        try:
            with open(csv_file, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                writer.writeheader()
                for data in parcels_data:
                    writer.writerow(data)
        except IOError:
            print("I/O error")    


        return {
                  self.OUTPUT_SEGMENTS: segments_csv, 
                  self.OUTPUT_PARCELS: parcels_csv
               }

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Download eMAPS data'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return ''
    
    def icon(self):
        cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]
        icon = QIcon(os.path.join(os.path.join(cmd_folder, 'logo.png')))
        return icon

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return EmapsDownloadAlgorithm()