import requests
import sys
import json

def get_uniprot(ids: list):
    accessions = ','.join(ids)
    endpoint = "https://rest.uniprot.org/uniprotkb/accessions"
    http_function = requests.get
    http_args = {'params': {'accessions': accessions}}
    return http_function(endpoint, **http_args)

def uniprot_parse_response(resp: dict):
    resp = resp.json()
    resp = resp["results"]
    output = {}
    for val in resp:
        acc = val['primaryAccession']
        species = val['organism']['scientificName']
        gene = val['genes']
        seq = val['sequence']
        output[acc] = {'organism':species, 'geneInfo':gene, 'sequenceInfo':seq, 'type':'protein'}

    return output

def get_ensembl(ids: list):
    endpoint = "https://rest.ensembl.org/lookup/id"
    headers={ "Content-Type" : "application/json", "Accept" : "application/json"}
    data = {}
    data['ids'] = ids
    data_json = json.dumps(data)
    http_function = requests.post(endpoint, headers = headers, data = data_json)
    return http_function

def ensembl_parse_response(resp: dict):
    resp = resp.json()
    output = {}
    for id in resp:
        res = resp[id]
        name = str(id)
        object_type = res["object_type"]
        species = res["species"]
        biotype = res["biotype"]
        descpiption = res["description"]
        output[name] = {'object type':object_type, 'species':species, 'biotype':biotype, 'descpiption':descpiption }
    return output

import re

def db_id(ids:list):
    upf = []
    for x in ids:
        if re.fullmatch(r'[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}', x):
            upf += [x]

    ensf = []
    for x in ids: 
        if re.fullmatch(r'ENS[A-Z]{1,5}\d{11}', x):
            ensf += [x]

    if len(upf) >= 1:
        resp = get_uniprot(upf)
        return uniprot_parse_response(resp)
    elif len(ensf) >=1:
        resp = get_ensembl(ensf)
        return ensembl_parse_response(resp)
    else:
        return 'Error. Input data is not matching any accesible database input formats'
    return

