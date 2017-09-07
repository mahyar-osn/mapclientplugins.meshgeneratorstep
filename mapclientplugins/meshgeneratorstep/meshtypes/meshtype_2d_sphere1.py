"""
Generates a 2-D unit sphere mesh with variable numbers of elements around and up.
"""

import math
from opencmiss.zinc.element import Element, Elementbasis, Elementfieldtemplate
from opencmiss.zinc.field import Field
from opencmiss.zinc.node import Node

class MeshType_2d_sphere1(object):
    '''
    classdocs
    '''
    @staticmethod
    def getName():
        return '2D Sphere 1'

    @staticmethod
    def getDefaultOptions():
        return {
            'Number of elements up' : 4,
            'Number of elements around' : 4,
            'Use cross derivatives' : False
        }

    @staticmethod
    def getOrderedOptionNames():
        return [
            'Number of elements up',
            'Number of elements around',
            'Use cross derivatives'
        ]

    @staticmethod
    def checkOptions(options):
        if (options['Number of elements up'] < 2) :
            options['Number of elements up'] = 2
        if (options['Number of elements around'] < 2) :
            options['Number of elements around'] = 2

    @staticmethod
    def generateMesh(region, options):
        """
        :param region: Zinc region to define model in. Must be empty.
        :param options: Dict containing options. See getDefaultOptions().
        :return: None
        """
        elementsCountUp = options['Number of elements up']
        elementsCountAround = options['Number of elements around']
        useCrossDerivatives = options['Use cross derivatives']

        fm = region.getFieldmodule()
        fm.beginChange()
        coordinates = fm.createFieldFiniteElement(3)
        coordinates.setName('coordinates')
        coordinates.setManaged(True)
        coordinates.setTypeCoordinate(True)
        coordinates.setCoordinateSystemType(Field.COORDINATE_SYSTEM_TYPE_RECTANGULAR_CARTESIAN)
        coordinates.setComponentName(1, 'x')
        coordinates.setComponentName(2, 'y')
        coordinates.setComponentName(3, 'z')

        nodes = fm.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        nodetemplateApex = nodes.createNodetemplate()
        nodetemplateApex.defineField(coordinates)
        nodetemplateApex.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_VALUE, 1)
        nodetemplateApex.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D_DS1, 1)
        nodetemplateApex.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D_DS2, 1)
        if useCrossDerivatives:
            nodetemplate = nodes.createNodetemplate()
            nodetemplate.defineField(coordinates)
            nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_VALUE, 1)
            nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D_DS1, 1)
            nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D_DS2, 1)
            nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D2_DS1DS2, 1)
        else:
            nodetemplate = nodetemplateApex


        mesh = fm.findMeshByDimension(2)
        bicubicHermiteBasis = fm.createElementbasis(2, Elementbasis.FUNCTION_TYPE_CUBIC_HERMITE)

        eft = mesh.createElementfieldtemplate(bicubicHermiteBasis)
        if not useCrossDerivatives:
            for n in range(4):
                eft.setFunctionNumberOfTerms(n*4 + 4, 0)

        # Apex1: collapsed on xi1 = 0
        eftApex1 = mesh.createElementfieldtemplate(bicubicHermiteBasis)
        eftApex1.setNumberOfLocalNodes(3)
        eftApex1.setNumberOfLocalScaleFactors(4)
        for s in range(4):
            si = s + 1
            sid = (s // 2)*100 + s + 1  # add 100 for different 'version'
            eftApex1.setScaleFactorType(si, Elementfieldtemplate.SCALE_FACTOR_TYPE_NODE_GENERAL)
            eftApex1.setScaleFactorIdentifier(si, sid)
        # basis node 1 -> local node 1
        eftApex1.setTermNodeParameter(1, 1, 1, Node.VALUE_LABEL_VALUE, 1)
        # 0 terms = zero parameter for d/dxi1 basis
        eftApex1.setFunctionNumberOfTerms(2, 0)
        # 2 terms for d/dxi2 via general linear map:
        eftApex1.setFunctionNumberOfTerms(3, 2)
        eftApex1.setTermNodeParameter(3, 1, 1, Node.VALUE_LABEL_D_DS1, 1)
        eftApex1.setTermScaling(3, 1, [1])
        eftApex1.setTermNodeParameter(3, 2, 1, Node.VALUE_LABEL_D_DS2, 1)
        eftApex1.setTermScaling(3, 2, [2])
        # 0 terms = zero parameter for cross derivative 1 2
        eftApex1.setFunctionNumberOfTerms(4, 0)
        # basis node 2 -> local node 1
        eftApex1.setTermNodeParameter(5, 1, 1, Node.VALUE_LABEL_VALUE, 1)
        # 0 terms = zero parameter for d/dxi1 basis
        eftApex1.setFunctionNumberOfTerms(6, 0)
        # 2 terms for d/dxi2 via general linear map:
        eftApex1.setFunctionNumberOfTerms(7, 2)
        eftApex1.setTermNodeParameter(7, 1, 1, Node.VALUE_LABEL_D_DS1, 1)
        eftApex1.setTermScaling(7, 1, [3])
        eftApex1.setTermNodeParameter(7, 2, 1, Node.VALUE_LABEL_D_DS2, 1)
        eftApex1.setTermScaling(7, 2, [4])
        # 0 terms = zero parameter for cross derivative 1 2
        eftApex1.setFunctionNumberOfTerms(8, 0)
        # basis nodes 3, 4 -> regular local nodes 2, 3
        for bn in range(2,4):
            fo = bn*4
            ni = bn
            eftApex1.setTermNodeParameter(fo + 1, 1, ni, Node.VALUE_LABEL_VALUE, 1)
            eftApex1.setTermNodeParameter(fo + 2, 1, ni, Node.VALUE_LABEL_D_DS1, 1)
            eftApex1.setTermNodeParameter(fo + 3, 1, ni, Node.VALUE_LABEL_D_DS2, 1)
            if useCrossDerivatives:
                eftApex1.setTermNodeParameter(fo + 4, 1, ni, Node.VALUE_LABEL_D2_DS1DS2, 1)
            else:
                eftApex1.setFunctionNumberOfTerms(fo + 4, 0)

        # Apex2: collapsed on xi1 = 1
        eftApex2 = mesh.createElementfieldtemplate(bicubicHermiteBasis)
        eftApex2.setNumberOfLocalNodes(3)
        eftApex2.setNumberOfLocalScaleFactors(4)
        for s in range(4):
            si = s + 1
            sid = (s // 2)*100 + s + 1  # add 100 for different 'version'
            eftApex2.setScaleFactorType(si, Elementfieldtemplate.SCALE_FACTOR_TYPE_NODE_GENERAL)
            eftApex2.setScaleFactorIdentifier(si, sid)
        # basis nodes 1, 2 -> regular local nodes 1, 2 (for each layer)
        for bn in range(2):
            fo = bn*4
            ni = bn + 1
            eftApex2.setTermNodeParameter(fo + 1, 1, ni, Node.VALUE_LABEL_VALUE, 1)
            eftApex2.setTermNodeParameter(fo + 2, 1, ni, Node.VALUE_LABEL_D_DS1, 1)
            eftApex2.setTermNodeParameter(fo + 3, 1, ni, Node.VALUE_LABEL_D_DS2, 1)
            if useCrossDerivatives:
                eftApex2.setTermNodeParameter(fo + 4, 1, ni, Node.VALUE_LABEL_D2_DS1DS2, 1)
            else:
                eftApex2.setFunctionNumberOfTerms(fo + 4, 0)

        # basis node 3 -> local node 3
        fo3 = 8
        eftApex2.setTermNodeParameter(fo3 + 1, 1, 3, Node.VALUE_LABEL_VALUE, 1)
        # 0 terms = zero parameter for d/dxi1 basis
        eftApex2.setFunctionNumberOfTerms(fo3 + 2, 0)
        # 2 terms for d/dxi2 via general linear map:
        eftApex2.setFunctionNumberOfTerms(fo3 + 3, 2)
        eftApex2.setTermNodeParameter(fo3 + 3, 1, 3, Node.VALUE_LABEL_D_DS1, 1)
        eftApex2.setTermScaling(fo3 + 3, 1, [1])
        eftApex2.setTermNodeParameter(fo3 + 3, 2, 3, Node.VALUE_LABEL_D_DS2, 1)
        eftApex2.setTermScaling(fo3 + 3, 2, [2])
        # 0 terms = zero parameter for cross derivative 1 2
        eftApex2.setFunctionNumberOfTerms(fo3 + 4, 0)
        # basis node 4 -> local node 3
        eftApex2.setTermNodeParameter(fo3 + 5, 1, 3, Node.VALUE_LABEL_VALUE, 1)
        # 0 terms = zero parameter for d/dxi1 basis
        eftApex2.setFunctionNumberOfTerms(fo3 + 6, 0)
        # 2 terms for d/dxi2 via general linear map:
        eftApex2.setFunctionNumberOfTerms(fo3 + 7, 2)
        eftApex2.setTermNodeParameter(fo3 + 7, 1, 3, Node.VALUE_LABEL_D_DS1, 1)
        eftApex2.setTermScaling(fo3 + 7, 1, [3])
        eftApex2.setTermNodeParameter(fo3 + 7, 2, 3, Node.VALUE_LABEL_D_DS2, 1)
        eftApex2.setTermScaling(fo3 + 7, 2, [4])
        # 0 terms = zero parameter for cross derivative 1 2
        eftApex2.setFunctionNumberOfTerms(fo3 + 8, 0)

        elementtemplate = mesh.createElementtemplate()
        elementtemplate.setElementShapeType(Element.SHAPE_TYPE_SQUARE)
        elementtemplate.defineField(coordinates, -1, eft)
        elementtemplateApex1 = mesh.createElementtemplate()
        elementtemplateApex1.setElementShapeType(Element.SHAPE_TYPE_SQUARE)
        elementtemplateApex1.defineField(coordinates, -1, eftApex1)
        elementtemplateApex2 = mesh.createElementtemplate()
        elementtemplateApex2.setElementShapeType(Element.SHAPE_TYPE_SQUARE)
        elementtemplateApex2.defineField(coordinates, -1, eftApex2)

        cache = fm.createFieldcache()

        # create nodes
        nodeIdentifier = 1
        radiansPerElementAround = 2.0*math.pi/elementsCountAround
        radiansPerElementUp = math.pi/elementsCountUp
        x = [ 0.0, 0.0, 0.0 ]
        dx_ds1 = [ 0.0, 0.0, 0.0 ]
        dx_ds2 = [ 0.0, 0.0, 0.0 ]
        zero = [ 0.0, 0.0, 0.0 ]
        radius = 0.5

        # create apex1 node
        node = nodes.createNode(nodeIdentifier, nodetemplateApex)
        cache.setNode(node)
        coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_VALUE, 1, [ 0.0, 0.0, -radius ])
        coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_D_DS1, 1, [ 0.0, radius*radiansPerElementUp, 0.0 ])
        coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_D_DS2, 1, [ radius*radiansPerElementUp, 0.0, 0.0 ])
        nodeIdentifier = nodeIdentifier + 1

        # create regular rows between apexes
        for n2 in range(1, elementsCountUp):
            radiansUp = n2*radiansPerElementUp
            cosRadiansUp = math.cos(radiansUp);
            sinRadiansUp = math.sin(radiansUp);
            for n1 in range(elementsCountAround):
                radiansAround = n1*radiansPerElementAround
                cosRadiansAround = math.cos(radiansAround)
                sinRadiansAround = math.sin(radiansAround)
                x = [
                    radius*cosRadiansAround*sinRadiansUp,
                    radius*sinRadiansAround*sinRadiansUp,
                    -radius*cosRadiansUp
                ]
                dx_ds1 = [
                    radius*-sinRadiansAround*sinRadiansUp*radiansPerElementAround,
                    radius*cosRadiansAround*sinRadiansUp*radiansPerElementAround,
                    0.0
                ]
                dx_ds2 = [
                    radius*cosRadiansAround*cosRadiansUp*radiansPerElementUp,
                    radius*sinRadiansAround*cosRadiansUp*radiansPerElementUp,
                    radius*sinRadiansUp*radiansPerElementUp
                ]
                node = nodes.createNode(nodeIdentifier, nodetemplate)
                cache.setNode(node)
                coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_VALUE, 1, x)
                coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_D_DS1, 1, dx_ds1)
                coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_D_DS2, 1, dx_ds2)
                if useCrossDerivatives:
                    coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_D2_DS1DS2, 1, zero)
                nodeIdentifier = nodeIdentifier + 1

        # create apex2 node
        node = nodes.createNode(nodeIdentifier, nodetemplateApex)
        cache.setNode(node)
        coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_VALUE, 1, [ 0.0, 0.0, radius ])
        coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_D_DS1, 1, [ 0.0, radius*radiansPerElementUp, 0.0 ])
        coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_D_DS2, 1, [ radius*-radiansPerElementUp, 0.0, 0.0 ])
        nodeIdentifier = nodeIdentifier + 1

        # create elements
        elementIdentifier = 1
        # create Apex1 elements, editing eft scale factor identifiers around apex
        # scale factor identifiers follow convention of offsetting by 100 for each 'version'
        bni1 = 1
        for e1 in range(elementsCountAround):
            va = e1
            vb = (e1 + 1)%elementsCountAround
            eftApex1.setScaleFactorIdentifier(1, va*100 + 1)
            eftApex1.setScaleFactorIdentifier(2, va*100 + 2)
            eftApex1.setScaleFactorIdentifier(3, vb*100 + 1)
            eftApex1.setScaleFactorIdentifier(4, vb*100 + 2)
            # redefine field in template for changes to eftApex1:
            elementtemplateApex1.defineField(coordinates, -1, eftApex1)
            element = mesh.createElement(elementIdentifier, elementtemplateApex1)
            bni2 = e1 + 2
            bni3 = (e1 + 1)%elementsCountAround + 2
            nodeIdentifiers = [ bni1, bni2, bni3 ]
            element.setNodesByIdentifier(eftApex1, nodeIdentifiers)
            # set general linear map coefficients
            radiansAround = e1*radiansPerElementAround
            radiansAroundNext = ((e1 + 1)%elementsCountAround)*radiansPerElementAround
            scalefactors = [
                math.sin(radiansAround), math.cos(radiansAround), math.sin(radiansAroundNext), math.cos(radiansAroundNext)
            ]
            result = element.setScaleFactors(eftApex1, scalefactors)
            elementIdentifier = elementIdentifier + 1

        # create regular rows between apexes
        for e2 in range(elementsCountUp - 2):
            for e1 in range(elementsCountAround):
                element = mesh.createElement(elementIdentifier, elementtemplate)
                bni1 = e2*elementsCountAround + e1 + 2
                bni2 = e2*elementsCountAround + (e1 + 1)%elementsCountAround + 2
                nodeIdentifiers = [ bni1, bni2, bni1 + elementsCountAround, bni2 + elementsCountAround ]
                result = element.setNodesByIdentifier(eft, nodeIdentifiers)
                elementIdentifier = elementIdentifier + 1

        # create Apex2 elements, editing eft scale factor identifiers around apex
        # scale factor identifiers follow convention of offsetting by 100 for each 'version'
        bni3 = 2 + (elementsCountUp - 1)*elementsCountAround
        for e1 in range(elementsCountAround):
            va = e1
            vb = (e1 + 1)%elementsCountAround
            eftApex2.setScaleFactorIdentifier(1, va*100 + 1)
            eftApex2.setScaleFactorIdentifier(2, va*100 + 2)
            eftApex2.setScaleFactorIdentifier(3, vb*100 + 1)
            eftApex2.setScaleFactorIdentifier(4, vb*100 + 2)
            # redefine field in template for changes to eftApex2:
            elementtemplateApex1.defineField(coordinates, -1, eftApex2)
            element = mesh.createElement(elementIdentifier, elementtemplateApex1)
            bni1 = bni3 - elementsCountAround + e1
            bni2 = bni3 - elementsCountAround + (e1 + 1)%elementsCountAround
            nodeIdentifiers = [ bni1, bni2, bni3 ]
            result = element.setNodesByIdentifier(eftApex2, nodeIdentifiers)
            # set general linear map coefficients
            radiansAround = e1*radiansPerElementAround
            radiansAroundNext = ((e1 + 1)%elementsCountAround)*radiansPerElementAround
            scalefactors = [
                -math.sin(radiansAround), math.cos(radiansAround), -math.sin(radiansAroundNext), math.cos(radiansAroundNext)
            ]
            result = element.setScaleFactors(eftApex2, scalefactors)
            elementIdentifier = elementIdentifier + 1

        fm.endChange()