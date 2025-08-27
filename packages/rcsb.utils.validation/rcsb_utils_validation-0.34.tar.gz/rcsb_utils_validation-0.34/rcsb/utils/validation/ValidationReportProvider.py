##
# File:    ValidationReportProvider.py (DEPRECATED)
# Author:  J. Westbrook
# Date:    16-Aug-2019
# Version: 0.001 Initial version
#
# Updates:
#  2-Jun-2020 jdw update with schema V4 mapping file
#  8-Oct-2021 jdw deprecated this module
##
"""
Resource provider for validation report reader and translator.

"""
__docformat__ = "google en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import logging
import os
import uuid

from rcsb.utils.io.FileUtil import FileUtil
from rcsb.utils.io.MarshalUtil import MarshalUtil
from rcsb.utils.io.SingletonClass import SingletonClass
from rcsb.utils.validation.ValidationReportReader import ValidationReportReader

logger = logging.getLogger(__name__)


class ValidationReportProvider(SingletonClass):
    """Resource provider for validation report reader and translator."""

    def __init__(self, **kwargs):
        """Resource provider for validation report reader and translator.

        Args:
            urlTarget (str): URL for schema mapping file
            dirPath (str): path to the directory containing cache files
            useCache (bool, optional): flag to use cached files. Defaults to True.

        """

        urlTarget = kwargs.get("urlTarget", "https://raw.githubusercontent.com/rcsb/py-rcsb_exdb_assets/master/dictionary_files/reference/vrpt_dictmap.json")
        dirPath = kwargs.get("dirPath", ".")
        useCache = kwargs.get("useCache", True)
        self.__mapD = self.__reload(urlTarget, dirPath, useCache=useCache)
        if not (self.__mapD and "attributes" in self.__mapD and "categories" in self.__mapD):
            logger.debug("Retrying loading validation mapping data")
            self.__mapD = self.__reload(urlTarget, dirPath, useCache=False)
        #
        logger.debug(
            "Loaded mapping attributes (%d) categories (%d)",
            len(self.__mapD["attributes"]) if "attributes" in self.__mapD else 0,
            len(self.__mapD["categories"]) if "categories" in self.__mapD else 0,
        )
        self.__reader = None
        logger.debug("Leaving constructor")

    def testCache(self):
        return self.__mapD and "categories" in self.__mapD and "attributes" in self.__mapD

    def __reload(self, urlTarget, dirPath, useCache=True):
        """Reload local cache of mapping resources to support validation report reader and translator.

        Args:
            urlTarget (list, str): URL for schema mapping file
            dirPath (str): path to the directory containing cache files
            useCache (bool, optional): flag to use cached files. Defaults to True.

        Returns:
            (object): instance of ValidationReportReader()
        """
        mapD = {}
        #
        mU = MarshalUtil()
        fU = FileUtil()
        fn = fU.getFileName(urlTarget)
        mappingFilePath = os.path.join(dirPath, fn)
        mU.mkdir(dirPath)
        #
        # if not useCache:
        #     for fp in [mappingFilePath]:
        #         try:
        #             os.remove(fp)
        #         except Exception:
        #             pass
        # #
        logger.debug("Loading validation mapping data in %s (useCache %r)", fn, useCache)
        if useCache and fU.exists(mappingFilePath):
            mapD = mU.doImport(mappingFilePath, fmt="json")
        else:
            logger.info("Fetching url %s to resource file %s", urlTarget, mappingFilePath)
            tS = uuid.uuid4().hex
            tP = os.path.join(dirPath, "._" + tS)
            ok = fU.get(urlTarget, tP)
            if ok:
                mapD = mU.doImport(tP, fmt="json")
                os.replace(tP, mappingFilePath)
        return mapD

    def getReader(self, **kwargs):
        """Return a ValidationReportReader object.

        Returns:
            [object] -- returns ValidationReportReader() object
        """
        if not self.__reader:
            self.__reader = ValidationReportReader(self.__mapD, **kwargs)
        return self.__reader
