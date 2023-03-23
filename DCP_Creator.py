import os
import hashlib
import xml.etree.ElementTree as ET
import base64
import uuid
import mimetypes
import datetime
from lxml import etree

def findHash(filePath):
    with open(filePath, "rb") as f:
        return (base64.b64encode(hashlib.sha1(f.read()).digest())).decode('utf-8')

def generateUuid():
    return str(uuid.uuid4())

def createPackingList(rootDirectory, uuidMapping):
    pklPath = os.path.join(rootDirectory, "DCP_PKL.xml")
    rootPkl = ET.Element("PackingList", xmlns="http://www.smpte-ra.org/schemas/429-8/2007/PKL")

    dirUuid = uuidMapping.get(rootDirectory,generateUuid())
    uuidMapping[rootDirectory] = dirUuid
    dirName = os.path.basename(rootDirectory)
    dirDate = datetime.datetime.utcnow().isoformat(timespec="seconds")+"+05:30"

    ET.SubElement(rootPkl,"Id").text = "urn:uuid:"+dirUuid
    ET.SubElement(rootPkl,"AnnotationText").text = dirName
    ET.SubElement(rootPkl,"IssueDate").text = dirDate
    ET.SubElement(rootPkl,"Issuer").text = "Gowtham S S"
    ET.SubElement(rootPkl,"Creator").text = "Qube"

    for subDirectory, directories, files in os.walk(rootDirectory):
        subDirectoryElementPkl = ET.SubElement(rootPkl,"AssetList")

        for file in files:
            filePath = os.path.relpath(os.path.join(subDirectory,file),rootDirectory)
            fileSize = os.path.getsize(os.path.join(rootDirectory, filePath))
            fileHash = findHash(os.path.join(rootDirectory, filePath))
            fileUuid = uuidMapping.get(filePath,generateUuid())
            uuidMapping[filePath] = fileUuid
            fileType = mimetypes.guess_type(file)[0]

            fileElementPkl = ET.SubElement(subDirectoryElementPkl, "Asset")
            ET.SubElement(fileElementPkl,"Id").text = "urn:uuid:"+fileUuid
            ET.SubElement(fileElementPkl, "AnnotationText").text = file
            ET.SubElement(fileElementPkl, "Hash").text = fileHash
            ET.SubElement(fileElementPkl, "Size").text = str(fileSize)
            ET.SubElement(fileElementPkl, "Type").text = fileType
    treePackingList = ET.ElementTree(rootPkl)
    treePackingList.write(pklPath, encoding="utf-8", xml_declaration=True, short_empty_elements=False)

def createAssetMap(rootDirectory, uuidMapping):
    ampPath = os.path.join(rootDirectory, "ASSETMAP.xml")
    rootAmp = ET.Element("AssetMap", xmlns="http://www.smpte-ra.org/schemas/429-9/2007/AM")

    dirUuid = uuidMapping.get(rootDirectory,generateUuid())
    dirName = os.path.basename(rootDirectory)
    dirDate = datetime.datetime.utcnow().isoformat(timespec="seconds")+"+05:30"

    ET.SubElement(rootAmp,"Id").text = "urn:uuid:"+dirUuid
    ET.SubElement(rootAmp,"AnnotationText").text = dirName
    ET.SubElement(rootAmp,"Creator").text = "Qube"
    ET.SubElement(rootAmp,"VolumeCount").text = "1"
    ET.SubElement(rootAmp,"IssueDate").text = dirDate
    ET.SubElement(rootAmp,"Issuer").text = "Gowtham S S"

    for subDirectory, directories, files in os.walk(rootDirectory):
        subDirectoryElementAmp = ET.SubElement(rootAmp,"AssetList")

        for file in files:
            filePath = os.path.relpath(os.path.join(subDirectory,file),rootDirectory)
            fileUuid = uuidMapping.get(filePath,generateUuid())

            fileElementAmp = ET.SubElement(subDirectoryElementAmp,"Asset")
            ET.SubElement(fileElementAmp,"Id").text = "urn:uuid:"+fileUuid
            ET.SubElement(fileElementAmp, "AnnotationText").text = file
            if "PKL" in str(file):
                ET.SubElement(fileElementAmp, "PackingList").text = 'true'
            chunkElement = ET.SubElement(fileElementAmp,"ChunkList")
            chunkListElement = ET.SubElement(chunkElement,"Chunk")
            ET.SubElement(chunkListElement,"Path").text = filePath

    treeAssetMap = ET.ElementTree(rootAmp)
    treeAssetMap.write(ampPath, encoding="utf-8", xml_declaration=True, short_empty_elements=False)

uuidMapping = {}
rootDirectory = input("Enter the directory path: ")
createPackingList(rootDirectory, uuidMapping)
createAssetMap(rootDirectory, uuidMapping)

packingListFile = os.path.join(rootDirectory, "DCP_PKL.xml")
pklXsdFile = "/Users/gowthamss/Desktop/XML Schema/PKL_schema.xsd"
assetMapFile = os.path.join(rootDirectory, "ASSETMAP.xml")
ampXsdFile = "/Users/gowthamss/Desktop/XML Schema/st-429-9-2014.xsd"

pklXml = etree.parse(packingListFile)
pklSchema = etree.parse(pklXsdFile)
ampXml = etree.parse(assetMapFile)
ampSchema = etree.parse(ampXsdFile)

pklValidator = etree.XMLSchema(pklSchema)
ampValidator = etree.XMLSchema(ampSchema)

if pklValidator.validate(pklXml):
    print("PKL is valid")
else:
    print("PKL is not valid")
    print(pklValidator.error_log)

if ampValidator.validate(ampXml):
    print("ASSETMAP is valid")
else:
    print("ASSETMAP is not valid")
    print(ampValidator.error_log)
