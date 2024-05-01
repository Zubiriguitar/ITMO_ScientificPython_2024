import requests
import sys
import json
import re
import subprocess

# ! pip install biopython
# ! pip install -q condacolab

import condacolab
# condacolab.install()
# ! conda install -c bioconda seqkit
# ! conda update -n base -c conda-forge conda

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
        output[acc] = {'organism':species, 'geneInfo':gene}

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
        output[name] = {'object type':object_type, 'species':species, 'biotype':biotype}
    return output

def extract_id(input_string): # Extracting seq id from sequence header
    pattern = r'\|([^|]+)\|'
    match = re.search(pattern, input_string)
    if match:
        return match.group(1)
    else:
        return None
    
    
from Bio.PDB import *
from Bio import SeqIO

def fasta_parser (path):
  stats = subprocess.run(("seqkit", "stats", path, "-a"), capture_output=True, text=True) #running seqkit
  ext = 'fasta' 

  json_dict = {} 

  if stats.stdout != '' and stats.stderr == '': # no error result
    seqkit_out = seqkit.stdout.strip().split('\n')
    prop_names = seqkit_out[0].split()[1:]
    prop_vals = seqkit_out[1].split()[1:]
    seq_result = dict(zip(prop_names, prop_vals)) #extracting seqkit stats and dict formatting

    json_dict['Stats'] = seq_result #adding stats to json_dict

    sequences = SeqIO.parse(path, ext) #parsing with biopython
    seq_dict = {}

    if seq_result['type'] == 'Protein':
      id_list = []
      
      for seq in sequences: #extracting protein seq ID's
        seqid = extract_id(seq.id)
        if re.fullmatch(r'[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}', str(seqid)):
          id_list += [seqid]
          seq_dict[seqid] = {'Description': str(seq.description), 'Sequence': str(seq.seq), 'DB': {}}

      if len(id_list) >= 1:
        resp = get_uniprot(id_list)
        response = uniprot_parse_response(resp) #response from DB
        
        for key in response: #adding DB info to final dict
          if key in id_list:
            seq_dict[key]['DB'] = response[key]
        
        json_dict['Sequences'] = seq_dict 
      
    elif seq_result['type'] == 'DNA': #extracting DNA seq ID's
      id_list = []
      for seq in sequences: 
        seqid = str(seq.id)[:-2]
        if re.fullmatch(r'ENS[A-Z]{1,5}\d{11}', str(seqid)):
          id_list += [seqid]
          seq_dict[seqid] = {'Description': str(seq.description), 'Sequence': str(seq.seq), 'DB': {}}
      
      if len(id_list) >=1: 
        resp = get_ensembl(id_list)
        response = ensembl_parse_response(resp) #response from DB (one API call fol all ID's)
        
        for key in response: #adding DB info to final dict
          if key in id_list:
            seq_dict[key]['DB'] = response[key]
      
      json_dict['Sequences'] = seq_dict 
  
  elif stats.stdout == '' and stats.stderr != '': # error result
    json_dict['error'] = stats.stderr
  
  json_data = json.dumps(json_dict, indent=4) # converting dictionary to JSON format 

  with open('fasta_summary.json', 'w') as json_file:# writing JSON data to a .json file
    json_file.write(json_data)

  return json_dict

path = 'hw_file2.fasta'

fasta_parser(path)