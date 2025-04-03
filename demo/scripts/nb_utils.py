from pathlib import Path
import xml.etree.ElementTree as ET
import tempfile
import requests
import zipfile
import shutil
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


def download_from_url(url, target_dir, subdir_path=None):
    temp_dir = tempfile.mkdtemp()
    try:
        # download data
        response = requests.get(url)
        response.raise_for_status()
        zip_file_path = Path(temp_dir) / 'temp.zip'
        with open(zip_file_path, 'wb') as f:
            f.write(response.content)
        
        # unzip the file
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            if subdir_path:
                file_list = [f for f in zip_ref.namelist() if f.startswith(subdir_path)]
                zip_ref.extractall(temp_dir, members=file_list)
            else:
                zip_ref.extractall(temp_dir)
        # list content of temp_dir
        temp_file_path = [p for p in Path(temp_dir).glob('*') if p.is_dir()][0]

    except requests.exceptions.RequestException as e:
        print(f'Failed to download data: {e}')
    except zipfile.BadZipFile as e:
        print(f'Failed to unpack data: {e}')
    
    Path(target_dir).mkdir(parents=True, exist_ok=True)
    # copy from temp_dir to target_dir
    try:
        for f in Path(temp_file_path).glob('*'):
            shutil.move(f, target_dir)
        print(f'Successfully downloaded and unpacked data to "{target_dir}"')
    except Exception as e:
        print(e)
        print('To overwrite, delete the folder(s) in the target directory and try again.')
