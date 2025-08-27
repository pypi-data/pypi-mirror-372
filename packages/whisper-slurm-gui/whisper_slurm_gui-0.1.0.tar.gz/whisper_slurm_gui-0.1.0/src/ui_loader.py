#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module converting new style ui-files to old style"""

import tempfile
import os
from xml.etree import ElementTree as ET
from PyQt5 import uic

def convert_newstyle_ui_to_pyqt5_compatible(input_ui_path, output_ui_path):
    # Map for QFrame Shadow enums to PyQt5 equivalents
    frame_shadow_map = {
        'QFrame::Shadow::Sunken': 'QFrame::Sunken',
        'QFrame::Shadow::Raised': 'QFrame::Raised',
        'QFrame::Shadow::Plain': 'QFrame::Plain',
        'QFrame::Shadow::None': 'QFrame::NoShadow',
    }
    # Map for QFrame Shape enums to PyQt5 equivalents
    frame_shape_map = {
        'QFrame::Shape::Panel': 'QFrame::Panel',
        'QFrame::Shape::NoFrame': 'QFrame::NoFrame',
        'QFrame::Shape::Box': 'QFrame::Box',
        'QFrame::Shape::HLine': 'QFrame::HLine',
        'QFrame::Shape::VLine': 'QFrame::VLine',
        'QFrame::Shape::StyledPanel': 'QFrame::StyledPanel',
        'QFrame::Shape::WinPanel': 'QFrame::WinPanel',
    }
    # Map for AlignmentFlag enums to PyQt5 equivalents
    alignment_map = {
        'Qt::AlignmentFlag::AlignRight': 'Qt::AlignRight',
        'Qt::AlignmentFlag::AlignTrailing': 'Qt::AlignTrailing',
        'Qt::AlignmentFlag::AlignVCenter': 'Qt::AlignVCenter',
        'Qt::AlignmentFlag::AlignLeft': 'Qt::AlignLeft',
        'Qt::AlignmentFlag::AlignLeading': 'Qt::AlignLeading',
        'Qt::AlignmentFlag::AlignHCenter': 'Qt::AlignHCenter',
        'Qt::AlignmentFlag::AlignTop': 'Qt::AlignTop',
        'Qt::AlignmentFlag::AlignBottom': 'Qt::AlignBottom',
        'Qt::AlignmentFlag::AlignCenter': 'Qt::AlignCenter',
    }
    tree = ET.parse(input_ui_path)
    root = tree.getroot()
    if 'version' in root.attrib:
        root.attrib['version'] = '4.0'
    for elem in root.iter():
        if 'stdset' in elem.attrib:
            del elem.attrib['stdset']
        if elem.tag == 'setProperty':
            elem.tag = 'property'
        if elem.tag.startswith('{http://www.qt-project.org/ui/2021}'):
            elem.tag = elem.tag.split('}', 1)[-1]
        # Fix enums for PyQt5 compatibility
        if elem.tag == 'enum' and elem.text:
            text = elem.text.strip()
            if text == 'Qt::Orientation::Horizontal':
                elem.text = 'Qt::Horizontal'
            elif text == 'Qt::Orientation::Vertical':
                elem.text = 'Qt::Vertical'
            elif text == 'Qt::LayoutDirection::LeftToRight':
                elem.text = 'Qt::LeftToRight'
            elif text in frame_shape_map:
                elem.text = frame_shape_map[text]
            elif text in frame_shadow_map:
                elem.text = frame_shadow_map[text]
        # Fix <set> tags for AlignmentFlag enums
        if elem.tag == 'set' and elem.text:
            text = elem.text.strip()
            for k, v in alignment_map.items():
                text = text.replace(k, v)
            elem.text = text
    tree.write(output_ui_path, encoding='utf-8', xml_declaration=True)

def load_ui(ui_file, baseinstance):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.ui') as tmp:
        convert_newstyle_ui_to_pyqt5_compatible(ui_file, tmp.name)
        uic.loadUi(tmp.name, baseinstance)
    os.unlink(tmp.name)
