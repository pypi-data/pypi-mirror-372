#!/usr/bin/env python3
"""
PPTX 文件自定义属性读取工具
"""

import os
import sys
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional


def read_pptx_properties(filepath: str) -> Dict[str, Any]:
    """
    读取 PPTX 文件的自定义属性
    
    Args:
        filepath: PPTX 文件路径
        
    Returns:
        包含文件属性的字典
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"文件不存在: {filepath}")
    
    if not filepath.lower().endswith('.pptx'):
        raise ValueError(f"文件不是 PPTX 格式: {filepath}")
    
    properties = {
        'core_properties': {},
        'app_properties': {},
        'custom_properties': {}
    }
    
    try:
        with zipfile.ZipFile(filepath, 'r') as pptx_zip:
            # 读取核心属性 (core.xml)
            if 'docProps/core.xml' in pptx_zip.namelist():
                core_xml = pptx_zip.read('docProps/core.xml')
                properties['core_properties'] = parse_core_properties(core_xml)
            
            # 读取应用属性 (app.xml)
            if 'docProps/app.xml' in pptx_zip.namelist():
                app_xml = pptx_zip.read('docProps/app.xml')
                properties['app_properties'] = parse_app_properties(app_xml)
            
            # 读取自定义属性 (custom.xml)
            if 'docProps/custom.xml' in pptx_zip.namelist():
                custom_xml = pptx_zip.read('docProps/custom.xml')
                properties['custom_properties'] = parse_custom_properties(custom_xml)
    
    except zipfile.BadZipFile:
        raise ValueError(f"文件不是有效的 PPTX 格式: {filepath}")
    except Exception as e:
        raise RuntimeError(f"读取文件时发生错误: {e}")
    
    return properties


def parse_core_properties(xml_content: bytes) -> Dict[str, str]:
    """解析核心属性 XML"""
    properties = {}
    
    # 定义命名空间
    namespaces = {
        'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'dcterms': 'http://purl.org/dc/terms/',
        'dcmitype': 'http://purl.org/dc/dcmitype/',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }
    
    try:
        root = ET.fromstring(xml_content)
        
        # 提取常用属性
        property_mappings = {
            'title': './/dc:title',
            'subject': './/dc:subject',
            'creator': './/dc:creator',
            'keywords': './/cp:keywords',
            'description': './/dc:description',
            'language': './/dc:language',
            'category': './/cp:category',
            'version': './/cp:version',
            'revision': './/cp:revision',
            'lastModifiedBy': './/cp:lastModifiedBy',
            'created': './/dcterms:created',
            'modified': './/dcterms:modified'
        }
        
        for prop_name, xpath in property_mappings.items():
            element = root.find(xpath, namespaces)
            if element is not None and element.text:
                properties[prop_name] = element.text.strip()
    
    except ET.ParseError as e:
        print(f"解析核心属性 XML 时出错: {e}", file=sys.stderr)
    
    return properties


def parse_app_properties(xml_content: bytes) -> Dict[str, str]:
    """解析应用属性 XML"""
    properties = {}
    
    # 定义命名空间
    namespaces = {
        'ep': 'http://schemas.openxmlformats.org/officeDocument/2006/extended-properties'
    }
    
    try:
        root = ET.fromstring(xml_content)
        
        # 提取常用属性
        property_mappings = {
            'application': './/ep:Application',
            'docSecurity': './/ep:DocSecurity',
            'scaleCrop': './/ep:ScaleCrop',
            'linksUpToDate': './/ep:LinksUpToDate',
            'pages': './/ep:Pages',
            'words': './/ep:Words',
            'characters': './/ep:Characters',
            'presentationFormat': './/ep:PresentationFormat',
            'paragraphs': './/ep:Paragraphs',
            'slides': './/ep:Slides',
            'notes': './/ep:Notes',
            'totalTime': './/ep:TotalTime',
            'hiddenSlides': './/ep:HiddenSlides',
            'mmClips': './/ep:MMClips',
            'headingPairs': './/ep:HeadingPairs',
            'titlesOfParts': './/ep:TitlesOfParts',
            'manager': './/ep:Manager',
            'company': './/ep:Company',
            'lines': './/ep:Lines',
            'paragraphs': './/ep:Paragraphs',
            'slides': './/ep:Slides',
            'notes': './/ep:Notes',
            'totalTime': './/ep:TotalTime',
            'hiddenSlides': './/ep:HiddenSlides',
            'mmClips': './/ep:MMClips'
        }
        
        for prop_name, xpath in property_mappings.items():
            element = root.find(xpath, namespaces)
            if element is not None and element.text:
                properties[prop_name] = element.text.strip()
    
    except ET.ParseError as e:
        print(f"解析应用属性 XML 时出错: {e}", file=sys.stderr)
    
    return properties


def parse_custom_properties(xml_content: bytes) -> Dict[str, str]:
    """解析自定义属性 XML"""
    properties = {}
    
    # 定义命名空间
    namespaces = {
        'cp': 'http://schemas.openxmlformats.org/officeDocument/2006/custom-properties',
        'vt': 'http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes'
    }
    
    try:
        root = ET.fromstring(xml_content)
        
        # 查找所有自定义属性 - 使用正确的命名空间
        for prop in root.findall('.//cp:property', namespaces):
            name = prop.get('name')
            if name:
                # 查找属性值
                value_elem = prop.find('.//vt:lpwstr', namespaces)
                if value_elem is not None and value_elem.text:
                    properties[name] = value_elem.text.strip()
                else:
                    # 尝试其他数据类型
                    for vt_type in ['vt:i4', 'vt:r8', 'vt:bool', 'vt:filetime']:
                        value_elem = prop.find(f'.//{vt_type}', namespaces)
                        if value_elem is not None and value_elem.text:
                            properties[name] = value_elem.text.strip()
                            break
    
    except ET.ParseError as e:
        print(f"解析自定义属性 XML 时出错: {e}", file=sys.stderr)
    
    return properties


def format_properties(properties: Dict[str, Any]) -> str:
    """格式化属性输出"""
    output = []
    
    # 核心属性
    if properties['core_properties']:
        output.append("=== 核心属性 ===")
        for key, value in properties['core_properties'].items():
            output.append(f"  {key}: {value}")
        output.append("")
    
    # 应用属性
    if properties['app_properties']:
        output.append("=== 应用属性 ===")
        for key, value in properties['app_properties'].items():
            output.append(f"  {key}: {value}")
        output.append("")
    
    # 自定义属性
    if properties['custom_properties']:
        output.append("=== 自定义属性 ===")
        for key, value in properties['custom_properties'].items():
            output.append(f"  {key}: {value}")
        output.append("")
    
    if not any(properties.values()):
        output.append("未找到任何属性信息")
    
    return "\n".join(output)


def command_fileattr(filepath: str) -> None:
    """
    执行 fileattr 命令
    
    Args:
        filepath: PPTX 文件路径
    """
    try:
        properties = read_pptx_properties(filepath)
        print(f"文件: {filepath}")
        print(format_properties(properties))
    
    except FileNotFoundError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"未知错误: {e}", file=sys.stderr)
        sys.exit(1) 