import os
import xmlschema
from jinja2 import Environment, PackageLoader, select_autoescape
import lxml.etree as ElementTree
import json
import re
from functools import reduce
import operator
from importlib import resources as imp_resources
from importlib.resources import files  # Python 3.9+

import warnings
from typing import Union #for python 3.8/3.9 compatibility

def strip_outer_xml_tag(xml_str: str, outer_tag: str) -> str:
    """Remove xml schema declaration and outer xml tag

    Args:
        xml_str (str): xml str from which to strip
        outer_tag (str): tag to remove

    Returns:
        str: stripped xml str
    """
    #TODO raise/check error if outer not found
    xml_str = re.sub(r'<\?xml.*?\?>', '', xml_str).strip()
    xml_str = re.sub(rf'<{outer_tag}[^>]*>', '', xml_str, count=1).strip()
    xml_str = re.sub(rf'</{outer_tag}>', '', xml_str, count=1).strip()
    return xml_str


def get_from_dict(data_dict: dict, map_list: list[Union[int,str]]):
    """get entry from dict at specified location

    Args:
        data_dict (dict): dict from which to get the element
        map_list (list[int | str]): list of keys describing the location at which to extract the element

    Returns:
        element at given location
    """
    return reduce(operator.getitem, map_list, data_dict)


def set_in_dict(data_dict: dict, map_list: list[Union[int,str]], value):
    """insert value into dict

    Args:
        data_dict (dict): dict into which to insert the item
        map_list (list[int | str]): location at which to insert the item
        value: item to insert
    """
    get_from_dict(data_dict, map_list[:-1])[map_list[-1]] = value


class XMLSchemaConverter:
    """Converter between XML and json/python dicts, based on a given XSD schema
    """
    def __init__(self):
        """Converter instance. Converts between XML and json/python dicts
        """
        schema_file = files("dccXMLJSONConv.schemata").joinpath('dcc.xsd')
        # Set the base directory for relative includes/imports
        schema_base_dir =  os.path.dirname(schema_file)

        self.schema = xmlschema.XMLSchema(schema_file, base_url=schema_base_dir)
        with imp_resources.files('dccXMLJSONConv.data').joinpath('template_descriptions.json').open('r',encoding='utf-8') as f:
            jsonData=json.load(f)
            self.templates=jsonData["templateInformation"]
            self.templateMapping=jsonData["elementMapping"]
        self.env = Environment(
            loader=PackageLoader('dccXMLJSONConv.data', '.'),
            autoescape=False)



    def _load_jinja_template(self, template_name: str, data_fragment: str) -> str:
        """Inserts XML fragment into template to create valid XML string

        Args:
            template_name (str): jinja template into which to insert
            data_fragment (str): fragment to insert into template

        Returns:
            str: full xml string
        """
        template = self.env.get_template(template_name)
        return template.render(data_fragment=data_fragment)

    def convert_xml_to_json(self, input_data) -> tuple[dict, list[Exception]]:
        """Deserialize XML to JSON

        Args:
            input_data: xml data to parse. Can be an XMLResource instance, a file-like object a path to a file or a URI of a resource or an Element instance or an ElementTree instance or a string containing the XML data.

        Returns:
            tuple[dict, list[Exception]]: converted dict; and list of exceptions that occurred during parsing
        """
        try:
            #TODO check if we have to parse the errors
            return self.schema.to_dict(input_data, validation="lax")
        except Exception as e:
            warnings.warn(f"XML->JSON Validation error: {e}. Attempting template insertion.")
            #TODO add logic to find fragments root tag
            root_tag = self._getRootElement(input_data)
            templateName = self.templateMapping.get(root_tag, "inData")
            template_info=self.templates[templateName]
            rendered_xml = self._load_jinja_template(template_info["template_path"] + '.xml', input_data)
            conversion_result = self.schema.to_dict(rendered_xml, validation="lax")
            converted_data = get_from_dict(conversion_result[0], template_info['json_path'])
            return converted_data, conversion_result[1]

    def convert_json_to_xml(self, input_data) -> tuple[str, ElementTree.ElementTree, list[Exception]]:
        """Serialize data back into XML format

        Args:
            input_data: the data that has to be encoded to XML data

        Raises:
            Exception: Any exceptions that made the serialization fail

        Returns:
            tuple[str, ElementTree, list[Exception]]: string containing the XML; ElementTree representation of the XML; and list of exceptions that occurred during serialization 
        """
        try:
            conversion_result = self.schema.encode(input_data, validation="lax")
            errors=conversion_result[1]
            if len(errors)>0:
                isNotCritical,errors,unCriticalErrors=self._checkIfValidationErrorIsUncritical(errors)
                if isNotCritical:
                    converted_element = conversion_result[0] # we take all since we had a complete XML tree
                    xml_str = xmlschema.etree_tostring(converted_element, namespaces=self.schema.namespaces)
                    return xml_str, converted_element, conversion_result[1]
                else:
                    raise Exception(f"Validation errors: {errors}")
            elif len(errors)==0:
                #evrything is fine
                converted_element = conversion_result[0]  # we take all since we had a complete XML tree
                xml_str = xmlschema.etree_tostring(converted_element, namespaces=self.schema.namespaces)
                return xml_str, conversion_result[0], conversion_result[1]
        except Exception as e:
            warnings.warn(f"JSON->XML Validation error: {e}. Attempting template insertion.")
            dictKeys=list(input_data.keys())
            if len(dictKeys)>1:
                #we will not handle this since the callee should have taken care of this
                raise Exception("Multiple root elements in JSON. Cannot determine template")
            root_tag=dictKeys[0]
            templateName = self.templateMapping.get(root_tag, "inData")
            template_info=self.templates[templateName]
            rendered_json = self._load_jinja_template(template_info["template_path"] + '.json', json.dumps(input_data))
            rendered_dict = json.loads(rendered_json)
            conversion_result = self.schema.encode(rendered_dict, validation="lax")
            converted_element = conversion_result[0].find(template_info["xPath"], namespaces=self.schema.namespaces)
            xml_str = xmlschema.etree_tostring(converted_element, namespaces=self.schema.namespaces)
            xml_str = strip_outer_xml_tag(xml_str, template_info["strip_outer_tag"])
            return xml_str, converted_element, conversion_result[1]

    def _getRootElement(self, xml_str:str ) -> str:
        """Returns tag name of first element

        Args:
            xml_str (str): XML to get the tag from

        Returns:
            str: contents of first tag, without any attributes
        """
        match = re.search(r'<\s*([\w:-]+)', xml_str)
        return match.group(1) if match else 'default'

    def _checkIfValidationErrorIsUncritical(self, errors: list[Exception]) -> tuple[bool, list[Exception], list[Exception]]:
        """Sort validation errors into critical and uncritical errors

        Args:
            errors (list[Exception]): Exceptions that occurred during XML validation

        Returns:
            tuple[bool, list[Exception], list[Exception]]: whether any critical exceptions were found; list of critical exceptions; list of uncritical exceptions
        """
        criticalErrors=[]
        unCriticalErrors=[]
        for error in errors:
            if "value doesn't match any pattern of ['3\\\\.4\\\\.0-rc\\\\.2']" in error.reason:
                unCriticalErrors.append(error)
            else:
                criticalErrors.append(error)
        isNotCritical=len(criticalErrors)==0
        return isNotCritical,criticalErrors,unCriticalErrors
    
converter=XMLSchemaConverter()

def XMLToJson(xml) -> str:
    """Deserialize XML to JSON

    Args:
        xml: xml data to parse. Can be an XMLResource instance, a file-like object a path to a file or a URI of a resource or an Element instance or an ElementTree instance or a string containing the XML data.

    Returns:
        str: JSON-String
    """
    dict, errors=converter.convert_xml_to_json(xml)
    return json.dumps(dict)

def XMLToDict(xml) -> tuple[dict, list[Exception]]:
    """Deserialize XML to dict

    Args:
        xml: xml data to parse. Can be an XMLResource instance, a file-like object a path to a file or a URI of a resource or an Element instance or an ElementTree instance or a string containing the XML data.

    Returns:
        tuple[dict, list[Exception]]: data as dict; list of exceptions that occurred during parsing
    """
    dict, errors=converter.convert_xml_to_json(xml)
    return dict, errors


def JSONToXML(jsonData: str) -> str:
    """Serialize data from JSON format to XML

    Args:
        jsonData (str): the data that has to be encoded to XML

    Returns:
        str: XML string
    """
    xml_str, converted_element, errors=converter.convert_json_to_xml(json.loads(jsonData))
    return xml_str

def DictToXML(dataDict: dict) -> tuple[str, ElementTree.ElementTree, list[Exception]]:
    """Serialize data from dict to XML

    Args:
        dataDict (dict): data to be serialized

    Returns:
        tuple[str, ElementTree.ElementTree, list[Exception]]: string containing the XML; ElementTree representation of the XML; and list of exceptions that occurred during serialization 
    """
    xml_str, converted_element, errors=converter.convert_json_to_xml(dataDict)
    return xml_str,converted_element, errors


def beautify_xml(text: str) -> str:
    """Beautify XML string

    Args:
        text (str): ugly XML string

    Returns:
        str: pretty XML string
    """
    parser = ElementTree.XMLParser(remove_blank_text=True, ns_clean=True)
    test = text.replace("\\\"", "\"")
    # print(test)
    try:
        tree = ElementTree.fromstring(test, parser=parser)
        ret = ElementTree.tostring(tree, pretty_print=True, encoding="unicode")
    except:
        ret = "<ERROR>dcc_stuff:beautify_xml failed </ERROR>"
    return ret