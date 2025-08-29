# This file is part of dcc-xmljsonconv (https://gitlab1.ptb.de/digitaldynamicmeasurement/dcc_XMLJSONConv)
# Copyright 2024 [Benedikt Seeger(PTB), Vanessa Stehr(PTB), Thomas Bruns (PTB)]
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import pytest
from dccXMLJSONConv.dccConv import XMLToJson,JSONToXML,DictToXML
import os
import json
def test_XMLToJson():
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    xml_file_path = os.path.join(data_dir, '20220708_8305_SN1842876.xml')
    # Read the XML file
    with open(xml_file_path, 'r') as xml_file:
        xml_data = xml_file.read()
    xmlDict=XMLToJson(str(xml_data))
    print(xmlDict)
    print("DONE")

def test_XMLToJsonFunction():
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    xml_file_path = os.path.join(data_dir, '20220708_8305_SN1842876.xml')
    # Read the XML file
    with open(xml_file_path, 'r') as xml_file:
        xml_data = xml_file.read()
    dict=XMLToJson(str(xml_data))
    print(dict)
    print("DONE")
    xml=JSONToXML(dict)
    print(xml)
    print("DONE")


#TODO add this as testcase with an file in this repo

