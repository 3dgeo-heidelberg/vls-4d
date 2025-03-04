from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import laspy


def read_pc(path, pt_src_id):
    las = laspy.read(path)
    pc = np.array([las.x, las.y, las.z]).T
    object_id = las['hitObjectId']
    classification = las['classification']
    helios_amplitude = las['heliosAmplitude']
    gps_time = las['gps_time']
    pt_src_id = np.repeat(pt_src_id, pc.shape[0])

    return pc, object_id, classification, helios_amplitude, gps_time, pt_src_id


def read_from_output_folder(folder):
    las_files = Path(folder).glob('*.la?')
    pc = []
    object_id = []
    classification = []
    helios_amplitude = []
    gps_time = []
    pt_src_id = []
    for i, las_file in enumerate(las_files):
        pc_, object_id_, classification_, helios_amplitude_, gps_time_, pt_src_id_ = read_pc(las_file, i)
        pc.append(pc_)
        object_id.append(object_id_)
        classification.append(classification_)
        helios_amplitude.append(helios_amplitude_)
        gps_time.append(gps_time_)
        pt_src_id.append(pt_src_id_)
    
    pc = np.concatenate(pc, axis=0)
    object_id = np.concatenate(object_id, axis=0)
    classification = np.concatenate(classification, axis=0)
    helios_amplitude = np.concatenate(helios_amplitude, axis=0)
    gps_time = np.concatenate(gps_time, axis=0)
    pt_src_id = np.concatenate(pt_src_id, axis=0)

    return pc, object_id, classification, helios_amplitude, gps_time, pt_src_id


def display_xml(path, item=None, line_limit=None):
    parser = ET.XMLParser(target = ET.TreeBuilder(insert_comments=True))
    root = ET.parse(path, parser=parser)
    tree = root.getroot()
    # ET.indent(tree)
    if item is None:
        # ET.indent(tree)
        xml_return = ET.tostring(tree, encoding='unicode')
    for e in tree:
        if 'id' in e.attrib and e.attrib['id'] == item:
            # ET.indent(e)
            xml_return = ET.tostring(e, encoding='unicode')
    if line_limit is not None:
        xml_return = '\n'.join(xml_return.split('\n')[:line_limit])
    
    return xml_return
