##
# File:    ValidationReportReader.py
# Author:  J. Westbrook
# Date:    24-Jan-2019
# Version: 0.001
#
# Update:
# 12-Jun-2023 aae Handle unknown attributes and element names when converting XML
#
##
"""
Various utilities for extracting data wwPDB validation report data
and transforming these data into mmCIF objects/files.

"""

import copy
import logging
import operator

from mmcif.api.DataCategory import DataCategory
from mmcif.api.PdbxContainers import DataContainer

from rcsb.utils.validation.ValidationReportSchemaUtils import ValidationReportSchemaUtils

logger = logging.getLogger(__name__)


class ValidationReportReader(object):
    """Various utilities for extracting data from wwPDB validation report data
       and transforming these data into mmCIF objects/files.
    """

    def __init__(self, dictionaryMap, stringKey=True):
        self.__dictionaryMap = copy.deepcopy(dictionaryMap)
        if stringKey:
            sD = dictionaryMap["attributes"]
            tD = {}
            for sK in sD:
                sTup = tuple(sK.split("|"))
                tD[sTup] = sD[sK]
            self.__dictionaryMap["attributes"] = tD
        #
        vrsu = ValidationReportSchemaUtils()
        self.__atOrdD = vrsu.getAttributeOrder()
        self.__atMap = vrsu.getAttributeMap()
        self.__attribD = {}
        for (catName, atName) in self.__dictionaryMap["attributes"]:
            self.__attribD.setdefault(catName, []).append(atName)
        self.__version = self.__dictionaryMap["_version"] if "_version" in self.__dictionaryMap else None

    def toCif(self, xrt):
        """ Read input XML validation report data file and return data
            transformed mmCIF container objects.
        """
        myContainerList = []
        try:
            if xrt:
                rD = self.__extract(xrt)
                myContainerList = self.__buildCif(rD)
                # -- parse extra bits only if version is defined starting with V004
                if self.__version:
                    extraL = self.__extractExtra(xrt)
                    for extra in extraL:
                        myContainerList[0].append(extra)
                # --

        except Exception as e:
            logger.error("Failing with %s", str(e))
        return myContainerList

    def __buildCif(self, rD, containerName="vrpt"):
        """ Construct a mmCIF data category objects for the input
            extracted data.

        Args:
            rD (dict): extracted data organized by category.
            containerName (str) : data block name

        Returns:
            containers (list):  data container list
        """
        #

        curContainer = DataContainer(containerName)
        for elName in rD:
            catName = elName
            if (not rD[elName]) or (not self.__attribD.get(catName)) or (catName in ["programs"]):
                continue
            hasOrdinal = "ordinal" in self.__attribD[catName]
            rowList = rD[elName]
            # Find the unique attribute content across the rowlist and the ordinal value
            atS = set()
            for ii, rowD in enumerate(rowList, 1):
                if hasOrdinal:
                    rowD["ordinal"] = ii
                if "icode" in rowD:
                    rowD["icode"] = str(rowD["icode"]).strip()
                if "altcode" in rowD:
                    rowD["altcode"] = str(rowD["altcode"]).strip()
                atS.update(rowD.keys())
            attributeNameList = list(atS)
            #
            # Set a reasonable order for these attributes
            #
            sD = {ky: self.__atOrdD[ky] for ky in attributeNameList if ky in self.__atOrdD}
            srtAtL = [tup[0] for tup in sorted(sD.items(), key=operator.itemgetter(1))]
            logger.debug("Category %s sorted attributes %r", catName, srtAtL)

            aCat = DataCategory(catName, srtAtL, rowList)
            curContainer.append(aCat)
        #
        # Adjust schema names -
        #
        atD = self.__dictionaryMap["attributes"]
        for catName in curContainer.getObjNameList():
            catObj = curContainer.getObj(catName)
            atNameList = catObj.getAttributeList()
            mapD = {}
            mapCatName = self.__dictionaryMap["categories"][catName] if catName in self.__dictionaryMap["categories"] else catName
            for atName in atNameList:
                mapD[atName] = atD[(catName, atName)]["at"] if (catName, atName) in atD else atName
            catObj.renameAttributes(mapD)
            catObj.setName(mapCatName)
        #
        # Map provenance items from programs.properties -
        #
        catObj = curContainer.getObj("program")
        if catObj and catObj.hasAttribute("properties"):
            for iRow in range(catObj.getRowCount()):
                pV = catObj.getValue("properties", iRow)
                pVL = [v.strip() for v in pV.split(",")]
                nL = [self.__atMap[ky] if ky in self.__atMap else ky for ky in pVL]
                catObj.setValue(",".join(nL), "properties", iRow)
                # logger.info("Row %r properties %r" % (iRow, pV))
        #
        return [curContainer]

    def __extract(self, xrt):
        """ Extract data from the input document and return a dictionary
            of categories containing rows of dictionaries with attribute naming.

        Args:
            xrt: ElementTree root element

        Returns:
            Extracted data (dict): dictionary organized by category with
                                   XML native data names.
        """
        atD = self.__dictionaryMap["attributes"]
        skipElements = ["EM_validation"]
        atL = ["altcode", "chain", "ent", "model", "resname", "resnum", "said", "seq"]
        unAts = ["PDB-resolution-low", "PDB-resolution", "PDB-R", "PDB-Rfree", "DCC_Rfree", "absolute_RSRZ_percentile", "relative_RSRZ_percentile"]
        rD = {}
        for el in xrt.getroot():
            logger.debug("-- Element tag %r attrib count %d", el.tag, len(list(el.attrib.keys())))
            if el.tag in skipElements:
                continue
            qV = {}
            for atName in el.attrib:
                if (el.tag, atName) not in atD:
                    continue
                qV[atName] = None if ((atName in unAts) and (el.attrib[atName] == "NotAvailable")) else el.attrib[atName]

            # qV = {k: None if ((k in unAts) and (el.attrib[k] == "NotAvailable")) else el.attrib[k] for k in el.attrib}
            logger.debug("qV %r", qV)
            rD.setdefault(el.tag, []).append(qV)
            #
            msgD = el.attrib if el.tag == "ModelledSubgroup" else {}
            # for ch in el.getiterator(tag=None):
            for ch in el:
                logger.debug("-- --> child element tag %r attrib count %r", ch.tag, len(ch.attrib))
                # add parent cardinal attributes at residue level
                # d = {k: ch.attrib[k] for k in ch.attrib}
                # Filter the NotAvailable values for floatOrUnavailable types
                dD = {k: None if ((k in unAts) and (ch.attrib[k] == "NotAvailable")) else ch.attrib[k] for k in ch.attrib}
                dD.update({k: msgD[k] for k in atL if k in msgD})
                rD.setdefault(ch.tag, []).append(dD)
                logger.debug("-- --> child element tag %r attrib count %r", ch.tag, len(dD))
                #
                for gch in ch:
                    logger.debug("-- -- --> grand child element tag %r attrib count %r", gch.tag, len(gch.attrib))
                    # add parent cardinal attributes
                    rD.setdefault(gch.tag, []).append(gch.attrib)
        return rD
        #

    def __extractExtra(self, xrt):
        """ Separately extract and parse data from the input document related to EM graphs.
        Args:
            xrt: ElementTree root element

        Returns:
            (list): DataCategory objects
        """
        rL = []
        elV = xrt.find("EM_validation")
        if not elV:
            return rL
        #
        graphDataL = []
        #
        logger.debug("Starting extraExtract -- ")
        gAtList = ["graph_data_id", "graph_id", "title", "x_axis_title", "x_axis_scale", "x_axis_units", "y_axis_title", "y_axis_scale", "y_axis_units"]
        infObj = DataCategory("pdbx_vrpt_em_2d_graph_info", gAtList)
        #
        for el in elV:
            logger.debug("-- EM element tag %r attrib count (%d): %r", el.tag, len(list(el.attrib.keys())), list(el.attrib.keys()))
            if el.tag == "RecommendedContourLevel" and "value" in el.attrib:
                cObj = DataCategory("pdbx_vrpt_em_details", attributeNameList=["ordinal", "recommended_contour_level"])
                cObj.setValue(1, "ordinal", 0)
                cObj.setValue(el.attrib["value"], "recommended_contour_level", 0)
                rL.append(cObj)
            elif el.tag == "map_value_distribution":
                try:
                    dL = self.__getGraphDataElements(el, graphDataId="d_mvd")
                    cgD = self.__getCommonGraphAttributes(el)
                    if dL and cgD:
                        iRow = infObj.getRowCount()
                        for k, v in cgD.items():
                            infObj.setValue(v, k, iRow)
                        infObj.setValue("map_value_distribution", "graph_id", iRow)
                        infObj.setValue("d_mvd", "graph_data_id", iRow)
                        cObj = DataCategory("pdbx_vrpt_em_graph_map_value_distribution", attributeNameList=["graph_id"])
                        cObj.setValue("map_value_distribution", "graph_id", 0)
                        graphDataL.extend(dL)
                        rL.append(cObj)
                except Exception as e:
                    logger.exception("Failing with %s", str(e))
            elif el.tag == "volume_estimate":
                try:
                    dL = self.__getGraphDataElements(el, graphDataId="d_ve")
                    cgD = self.__getCommonGraphAttributes(el)
                    if dL and cgD:
                        iRow = infObj.getRowCount()
                        for k, v in cgD.items():
                            infObj.setValue(v, k, iRow)
                        infObj.setValue("volume_estimate", "graph_id", iRow)
                        infObj.setValue("d_ve", "graph_data_id", iRow)
                        cObj = DataCategory("pdbx_vrpt_em_graph_volume_estimate", attributeNameList=["graph_id"])
                        cObj.setValue("volume_estimate", "graph_id", 0)
                        graphDataL.extend(dL)
                        rL.append(cObj)
                except Exception as e:
                    logger.exception("Failing with %s", str(e))
            elif el.tag == "rotationally_averaged_power_spectrum":
                try:
                    dL = self.__getGraphDataElements(el, graphDataId="d_raps")
                    cgD = self.__getCommonGraphAttributes(el)
                    if dL and cgD:
                        iRow = infObj.getRowCount()
                        for k, v in cgD.items():
                            infObj.setValue(v, k, iRow)
                        infObj.setValue("rotationally_averaged_power_spectrum", "graph_id", iRow)
                        infObj.setValue("d_raps", "graph_data_id", iRow)
                        cObj = DataCategory("pdbx_vrpt_em_graph_rotationally_averaged_power_spectrum", attributeNameList=["graph_id"])
                        cObj.setValue("rotationally_averaged_power_spectrum", "graph_id", 0)
                        graphDataL.extend(dL)
                        rL.append(cObj)
                except Exception as e:
                    logger.exception("Failing with %s", str(e))
            elif el.tag == "atom_inclusion":
                # backbone or all_atoms
                try:
                    cObj = None
                    for cN in ["all_atoms", "backbone"]:
                        ch = el.find(cN)
                        abbrev = "aa" if cN == "all_atoms" else "bb"
                        if ch:
                            gId = "atom_inclusion_%s" % cN
                            gdId = "d_ai_%s" % abbrev
                            dL = self.__getGraphDataElements(ch, graphDataId=gdId)
                            cgD = self.__getCommonGraphAttributes(ch)
                            if dL and cgD:
                                iRow = infObj.getRowCount()
                                for k, v in cgD.items():
                                    infObj.setValue(v, k, iRow)
                                infObj.setValue(gId, "graph_id", iRow)
                                infObj.setValue(gdId, "graph_data_id", iRow)
                                #
                                if not cObj:
                                    cObj = DataCategory("pdbx_vrpt_em_graph_atom_inclusion", attributeNameList=["graph_id", "type"])
                                tRow = cObj.getRowCount()
                                cObj.setValue(gId, "graph_id", tRow)
                                cObj.setValue(cN, "type", tRow)
                                graphDataL.extend(dL)
                    if cObj.getRowCount():
                        rL.append(cObj)
                except Exception as e:
                    logger.exception("Failing with %s", str(e))
            elif el.tag == "fsc":
                for ch in el:
                    logger.debug("-- Child fsc element tag %r attrib count (%d): %r", ch.tag, len(list(ch.attrib.keys())), list(ch.attrib.keys()))
                    if ch.tag == "resolution_intersections":
                        try:
                            atList = ["ordinal", "resolution_units", "spatial_frequency_units", "correlation", "resolution", "spatial_frequency", "curve", "type"]
                            rObj = DataCategory("pdbx_vrpt_em_resolution_intersections", atList)
                            ru = ch.attrib["resolution_unit"] if "resolution_unit" in ch.attrib else "?"
                            sfu = ch.attrib["spatial_frequency_unit"] if "spatial_frequency_unit" in ch.attrib else "?"
                            ii = 0
                            for gch in ch:
                                if gch.tag == "intersection":
                                    for at in ["correlation", "resolution", "spatial_frequency", "curve", "type"]:
                                        atV = gch.attrib[at] if at in gch.attrib else "?"
                                        rObj.setValue(atV, at, ii)
                                    rObj.setValue(ru, "resolution_units", ii)
                                    rObj.setValue(sfu, "spatial_frequency_units", ii)
                                    rObj.setValue(ii + 1, "ordinal", ii)
                                    ii += 1
                            if rObj.getRowCount():
                                rL.append(rObj)
                        except Exception as e:
                            logger.exception("Failing with %s", str(e))
                    elif ch.tag == "fsc_curves":
                        try:
                            iCount = 0
                            cObj = None
                            for gch in ch:
                                if gch.tag == "fsc_curve":
                                    iCount += 1
                                    gdId = "fsc_%d" % iCount
                                    dL = self.__getGraphDataElements(gch, graphDataId=gdId)
                                    cgD = self.__getCommonGraphAttributes(gch)
                                    curveName = gch.attrib["curve_name"] if "curve_name" in gch.attrib else "?"
                                    gId = curveName
                                    fscType = gch.attrib["type"] if "type" in gch.attrib else "?"
                                    if dL and cgD and curveName != "?":
                                        iRow = infObj.getRowCount()
                                        for k, v in cgD.items():
                                            infObj.setValue(v, k, iRow)
                                        #
                                        infObj.setValue(gId, "graph_id", iRow)
                                        infObj.setValue(gdId, "graph_data_id", iRow)
                                        #
                                        iRow = iCount - 1
                                        if not cObj:
                                            cObj = DataCategory("pdbx_vrpt_em_graph_fsc_curve", attributeNameList=["graph_id", "type", "curve_name"])
                                        cObj.setValue(gId, "graph_id", iRow)
                                        cObj.setValue(fscType, "type", iRow)
                                        cObj.setValue(curveName, "curve_name", iRow)
                                        graphDataL.extend(dL)
                            if cObj:
                                rL.append(cObj)
                        except Exception as e:
                            logger.exception("Failing with %s", str(e))

                    elif ch.tag == "fsc_indicator_curves":
                        try:
                            iCount = 0
                            cObj = None
                            for gch in ch:

                                if gch.tag == "fsc_indicator_curve":
                                    iCount += 1
                                    gdId = "fsc_i_%d" % iCount
                                    dL = self.__getGraphDataElements(gch, graphDataId=gdId)
                                    cgD = self.__getCommonGraphAttributes(gch)
                                    curveName = gch.attrib["curve_name"] if "curve_name" in gch.attrib else "?"
                                    gId = curveName
                                    fscType = gch.attrib["type"] if "type" in gch.attrib else "?"
                                    dataCurveName = gch.attrib["data_curve"] if "data_curve" in gch.attrib else "?"
                                    if dL and cgD and curveName != "?" and dataCurveName != "?":
                                        iRow = infObj.getRowCount()
                                        for k, v in cgD.items():
                                            infObj.setValue(v, k, iRow)
                                        #
                                        infObj.setValue(gId, "graph_id", iRow)
                                        infObj.setValue(gdId, "graph_data_id", iRow)
                                        #
                                        iRow = iCount - 1
                                        if not cObj:
                                            cObj = DataCategory("pdbx_vrpt_em_graph_fsc_indicator_curve", attributeNameList=["graph_id", "type", "curve_name", "data_curve_name"])
                                        cObj.setValue(gId, "graph_id", iRow)
                                        cObj.setValue(fscType, "type", iRow)
                                        cObj.setValue(curveName, "curve_name", iRow)
                                        cObj.setValue(dataCurveName, "data_curve_name", iRow)
                                        graphDataL.extend(dL)
                            if cObj:
                                rL.append(cObj)
                        except Exception as e:
                            logger.exception("Failing with %s", str(e))

            #
            # -- end of element processing

        # -------
        if infObj.getRowCount():
            rL.append(infObj)
            #
            dObj = DataCategory("pdbx_vrpt_em_2d_graph_data", ["ordinal", "graph_data_id", "x_value", "y_value"])
            for ii, dD in enumerate(graphDataL):
                for k, v in dD.items():
                    dObj.setValue(v, k, ii)
                dObj.setValue(ii + 1, "ordinal", ii)
            rL.append(dObj)

        return rL

    def __getCommonGraphAttributes(self, el):
        """ Get common EM 2D graph attributes from the input element.

        Args:
            el (obj): ElementTree element (2D graph element)

        Returns:
            (dict): {'title': , 'x_axis_title': , 'x_axis_scale':, 'x_axis_units':, ... for y-axis}

        """
        rD = {}
        rD["title"] = el.attrib["Title"] if "Title" in el.attrib else "?"
        rD["x_axis_title"] = el.attrib["xTitle"] if "xTitle" in el.attrib else "?"
        rD["x_axis_scale"] = el.attrib["xScale"] if "xScale" in el.attrib else "?"
        rD["x_axis_units"] = el.attrib["xUnit"] if "xUnit" in el.attrib else "?"
        rD["y_axis_title"] = el.attrib["yTitle"] if "yTitle" in el.attrib else "?"
        rD["y_axis_scale"] = el.attrib["yScale"] if "yScale" in el.attrib else "?"
        rD["y_axis_units"] = el.attrib["yUnit"] if "yUnit" in el.attrib else "?"
        return rD

    def __getGraphDataElements(self, pEl, graphDataId="g_1"):
        """Extract graph data elements and append these to input data list.

        Args:
            pEl ([type]): [description]
            graphDataId ([type]): [description]

        Returns:
            (list): updated input graphDataL
        """
        rL = []
        for ch in pEl:
            if ch.tag == "coordinate":
                try:
                    tD = {"graph_data_id": graphDataId, "x_value": ch.attrib["x"], "y_value": ch.attrib["y"]}
                    rL.append(tD)
                except Exception as e:
                    logger.exception("Failing with %s", str(e))
        return rL

    def __traverse(self, xrt, ns):
        """ Internal routine to traverse the dom covering/logging all elements and attributes.

        Args:
            xrt (object): ElementTree root element
            ns (str): XML namespace

        """

        for el in xrt.getroot():
            pEl = el.tag.replace(ns, "")
            logger.info("-- %r %r", pEl, el.attrib)
            for ch in el:
                chEl = ch.tag.replace(ns, "")
                logger.info("-- -->  %r %r", chEl, ch.attrib)
                if ch.text is not None and ch.text:
                    logger.info("-- -->  %s", ch.text)
                for gch in ch:
                    gchEl = gch.tag.replace(ns, "")
                    logger.info("-- -- -->  %r %r", gchEl, gch.attrib)
                    if gch.text is not None and gch.text:
                        logger.info("-- -- -->  %s", gch.text)
                    for ggch in gch:
                        ggchEl = ggch.tag.replace(ns, "")
                        logger.info("-- -- -- -->  %r %r", ggchEl, ggch.attrib)
                        if ggch.text is not None and ggch.text:
                            logger.info("-- -- -- -->  %s", ggch.text)
                        for gggch in ggch:
                            gggchEl = gggch.tag.replace(ns, "")
                            logger.info("-- -- -- -- -->  %r %r", gggchEl, gggch.attrib)
                            if gggch.text is not None and gggch.text:
                                logger.info("-- -- -- -- -->  %s", gggch.text)
