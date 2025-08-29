#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Created on Sun Dec 12 16:06:24 2021 by Thomas Bruns
# This file is part of dcc-xmljsonconv (https://gitlab1.ptb.de/digitaldynamicmeasurement/dcc_XMLJSONConv)
# Copyright 2024 [Thomas Bruns (PTB), Benedikt Seeger(PTB), Vanessa Stehr(PTB)]
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
import os

try:
    from fastapi import FastAPI, HTTPException, Response
    import json
    from .dccConv import XMLToJson, JSONToXML, converter
except ImportError as e:
    raise ImportError("FastAPI is not installed. Use `pip install dccXMLJSONConv[web]`.") from e




#remove proxy from env
for k in os.environ:
                if "proxy" in k.lower():
                    os.environ.pop(k)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello!\nBetter use the URL /json2dcc/?js={...} \n or /dcc2json (POST method)"}


from pydantic import BaseModel
class Data(BaseModel):
    xml: str

@app.post("/dcc2json/")
async def dcc2json(data: Data):
    """
    convert an XML-string into json by parsing through the document-tree

    Parameters
    ----------
    xml : str
        XML-document as string. 

    Returns
    -------
    str     
        A JSON-String representing the original XML

    """
    print("start of xml-input:")
    print(str(data.xml[0:40])+"\n")
        
    if data.xml == "": # error for empty json string
        raise HTTPException(status_code=400, detail="XML Content Empty!")  # 400 Bad Request
    else:
        try:
            return Response(XMLToJson(data.xml))
        except Exception as e:
            print("dcc_server.dcc2json(): failed !")
            # raise HTTPException(status_code=400, detail="xml parsing failed for: %s" % dcc.xml)
            raise HTTPException(status_code=400, detail="xml parsing failed: "+str(e))#400 Bad Request
        


###############################################################################
from pydantic import BaseModel
class Json(BaseModel):
    js: dict


@app.post("/json2dcc/")
async def json2dcc(data: Json):
    """
    convert an JSON-string into XML by parsing through the dict
    
    Parameters
    ----------
    data : str 
        JSON-document as string.

    Returns
    -------
    str     
        A XML-String representing the original JSON

    """
    print("type(data.js) = %s" % str(type(data.js)))
    #print(data.js)
    if data.js == {}: # error for empty json 
        raise HTTPException(status_code=400, detail="JSON Content Empty!")  # 400 Bad Request
    else:
            xml_str, converted_element, errors = converter.convert_json_to_xml(data.js)
            if len(errors)==0:
                return Response(xml_str)
            else:
                # generate error MSG
                tracbacklistAsStr=''
                for error in errors:
                    tracbacklistAsStr+=str(error)+' ...\n'
            raise HTTPException(status_code=400, detail="JSON parsing failed:"+tracbacklistAsStr)



####### To Do ######
# - CouchDB2dcc(_id)
