import os
import xml.etree.ElementTree as ET

def map_xml_file_to_json(file_name_xml, file_folder):
    file_path_xml = os.path.join(file_folder, file_name_xml)
    file_name_json = file_name_xml.replace('xml-', 'data-').replace('.xml', '.json')
    file_path_json = os.path.join(file_folder, file_name_json)

    tree = ET.parse(file_path_xml)
    root = tree.getroot()

    def xml_element_to_dict(element):
        result = {}
        
        for child in element:
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(
                    xml_element_to_dict(child) if len(child) > 0 else child.text.strip()
                )
            else:
                result[child.tag] = (
                    xml_element_to_dict(child) if len(child) > 0 else child.text.strip()
                )
                
        for attr, value in element.attrib.items():
            result[f"@{attr}"] = value
            
        return result

    data = xml_element_to_dict(root)

    with open(file_path_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f'|- json saved: {file_path_json}')
    return data