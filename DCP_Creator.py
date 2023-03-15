import os
import hashlib
import xml.etree.ElementTree as ET
import base64 
import uuid
import mimetypes
import datetime
from lxml import etree

def findHash(file_path):
    with open(file_path, "rb") as f:
        return (base64.b64encode(hashlib.sha1(f.read()).digest())).decode('utf-8')

def generate_uuid():
    return str(uuid.uuid4())

def create_pkl(root_directory, uuid_mapping):
    pkl_path = os.path.join(root_directory, "DCP_PKL.xml")
    root_pkl = ET.Element("PackingList", xmlns="http://www.smpte-ra.org/schemas/429-8/2007/PKL")

    dir_uuid = uuid_mapping.get(root_directory,generate_uuid())
    uuid_mapping[root_directory] = dir_uuid
    dir_name = os.path.basename(root_directory)
    dir_date = datetime.datetime.utcnow().isoformat(timespec="seconds")+"+00:00"

    ET.SubElement(root_pkl,"Id").text = "urn:uuid:"+dir_uuid
    ET.SubElement(root_pkl,"AnnotationText").text = dir_name
    ET.SubElement(root_pkl,"IssueDate").text = dir_date
    ET.SubElement(root_pkl,"Issuer").text = "Gowtham S S"
    ET.SubElement(root_pkl,"Creator").text = "Qube"  

    for subDirectory, directories, files in os.walk(root_directory):
        subDirectory_element_pkl = ET.SubElement(root_pkl,"AssetList")

        for file in files:
            file_path = os.path.relpath(os.path.join(subDirectory,file),root_directory)
            file_size = os.path.getsize(os.path.join(root_directory, file_path))
            file_hash = findHash(os.path.join(root_directory, file_path))
            file_uuid = uuid_mapping.get(file_path,generate_uuid())
            uuid_mapping[file_path] = file_uuid
            file_type = mimetypes.guess_type(file)[0] 

            file_element_pkl = ET.SubElement(subDirectory_element_pkl, "Asset")
            ET.SubElement(file_element_pkl,"Id").text = "urn:uuid:"+file_uuid
            ET.SubElement(file_element_pkl, "AnnotationText").text = file
            ET.SubElement(file_element_pkl, "Hash").text = file_hash
            ET.SubElement(file_element_pkl, "Size").text = str(file_size)
            ET.SubElement(file_element_pkl, "Type").text = file_type
    tree_pkl = ET.ElementTree(root_pkl)
    tree_pkl.write(pkl_path, encoding="utf-8", xml_declaration=True, short_empty_elements=False)

def create_amp(root_directory, uuid_mapping):
    amp_path = os.path.join(root_directory, "ASSETMAP.xml")
    root_amp = ET.Element("AssetMap", xmlns="http://www.smpte-ra.org/schemas/429-9/2007/AM")

    dir_uuid = uuid_mapping.get(root_directory,generate_uuid())
    dir_name = os.path.basename(root_directory)
    dir_date = datetime.datetime.utcnow().isoformat(timespec="seconds")+"+00:00"

    ET.SubElement(root_amp,"Id").text = "urn:uuid:"+dir_uuid
    ET.SubElement(root_amp,"AnnotationText").text = dir_name
    ET.SubElement(root_amp,"Creator").text = "Qube"
    ET.SubElement(root_amp,"VolumeCount").text = "1"
    ET.SubElement(root_amp,"IssueDate").text = dir_date
    ET.SubElement(root_amp,"Issuer").text = "Gowtham S S"
    

    for subDirectory, directories, files in os.walk(root_directory):
        subDirectory_element_amp = ET.SubElement(root_amp,"AssetList")

        for file in files:
            file_path = os.path.relpath(os.path.join(subDirectory,file),root_directory)
            file_uuid = uuid_mapping.get(file_path,generate_uuid())

            file_element_amp = ET.SubElement(subDirectory_element_amp,"Asset")
            ET.SubElement(file_element_amp,"Id").text = "urn:uuid:"+file_uuid
            ET.SubElement(file_element_amp, "AnnotationText").text = file
            if "PKL" in str(file):
                ET.SubElement(file_element_amp, "PackingList").text = 'true'
            chunk_element = ET.SubElement(file_element_amp,"ChunkList")
            chunkList_element = ET.SubElement(chunk_element,"Chunk")
            ET.SubElement(chunkList_element,"Path").text = file_path

    tree_amp = ET.ElementTree(root_amp)
    tree_amp.write(amp_path, encoding="utf-8", xml_declaration=True, short_empty_elements=False)    

uuid_mapping = {}
root_directory = input("Enter the directory path: ")
pkl_file = create_pkl(root_directory, uuid_mapping)   
amp_file = create_amp(root_directory, uuid_mapping)

pkl_file = os.path.join(root_directory, "DCP_PKL.xml")
pkl_xsd_file = "/Users/gowthamss/Desktop/XML Schema/PKL_schema.xsd"
amp_file = os.path.join(root_directory, "ASSETMAP.xml")
amp_xsd_file = "/Users/gowthamss/Desktop/XML Schema/st-429-9-2014.xsd"

pkl_xml = etree.parse(pkl_file)
pkl_schema = etree.parse(pkl_xsd_file)
amp_xml = etree.parse(amp_file)
amp_schema = etree.parse(amp_xsd_file)

pkl_validator = etree.XMLSchema(pkl_schema)
amp_validator = etree.XMLSchema(amp_schema)

if pkl_validator.validate(pkl_xml):
    print("PKL is valid")
else:
    print("PKL is not valid")
    print(pkl_validator.error_log)

if amp_validator.validate(amp_xml):
    print("ASSETMAP is valid")
else:
    print("ASSETMAP is not valid")
    print(amp_validator.error_log)   