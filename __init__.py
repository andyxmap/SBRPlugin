def classFactory(iface):
     """Load SBRP class from file solution.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
     from .solution import SBRP
     return SBRP(iface)