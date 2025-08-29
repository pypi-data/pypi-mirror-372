from typing import List, Dict
from SPARQLWrapper import SPARQLWrapper, JSON

from .json_cache import load_cache, save_cache, md5_hash

NERC_VOCAB_SPARQL_ENDPOINT = "https://vocab.nerc.ac.uk/sparql"

def get_exvs() -> Dict[str, str]:
    """ 
    Use nerc vocab services to get all available EXV variables
    """
    cache = load_cache("get_exvs")
    
    if cache is not None:
        return cache
    
    sparql = SPARQLWrapper(NERC_VOCAB_SPARQL_ENDPOINT)
    sparql.setQuery("""
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

        SELECT DISTINCT ?exv ?title WHERE {
            <http://vocab.nerc.ac.uk/collection/EXV/current/> skos:member ?exv .
            ?exv skos:prefLabel ?title .
            FILTER(LANG(?title) = "en")
        }
    """)
    
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()["results"]["bindings"]

    exv_map: Dict[str, str] = {}
    
    for row in results:
        uri = row["exv"]["value"]
        uri = uri.rstrip("/").split("/")[-1]
        
        label = row["title"]["value"]
        
        exv_map[uri] = label

    # Save the cache
    save_cache("get_exvs", exv_map)

    return exv_map


def exv_to_p01(exv_code: str) -> List[str]:
    
    cache_key = f"exv_to_p01_{md5_hash(exv_code)}"
    
    cache = load_cache(cache_key)
    
    if cache is not None:
       return cache
        
    # Construct full identifier

    exv_identifiers = map(lambda exv_code: f'"SDN:EXV::{exv_code}"', [exv_code])
    exv_identifiers = "\n".join(exv_identifiers)

    # Create the query with the user input
    sparql_query = f"""
    PREFIX dce: <http://purl.org/dc/elements/1.1/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX iadopt: <https://w3id.org/iadopt/ont#> 
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT DISTINCT ?p01 ?prefLabel ?notation
    WHERE {{
      VALUES ?exv_list {{
          {exv_identifiers}
      }}
      ?exv a skos:Concept .
      ?exv dce:identifier ?exv_list .

      OPTIONAL {{?exv iadopt:hasApplicableMatrix ?matrix .}}
      ?exv iadopt:hasApplicableObjectOfInterest ?ooi .
      ?exv iadopt:hasApplicableProperty ?property .

      <http://vocab.nerc.ac.uk/collection/P01/current/> skos:member ?p01 .

      OPTIONAL {{ ?p01 iadopt:hasMatrix ?matrix . }}
      ?p01 iadopt:hasObjectOfInterest ?ooi .
      ?p01 iadopt:hasProperty ?property .

       OPTIONAL {{ ?p01 skos:prefLabel ?prefLabel .
            FILTER(LANG(?prefLabel) = "en")
      }}
      OPTIONAL {{ ?p01 skos:notation ?notation . }}
    }}
    """
    # Set up the SPARQL request
    sparql = SPARQLWrapper(NERC_VOCAB_SPARQL_ENDPOINT)
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)

    # Run the query and parse results
    results = sparql.query().convert()

    p01s = []

    # Show results
    for result in results["results"]["bindings"]:
        uri = result.get("p01", {}).get("value", "")
        p01s.append(uri.rstrip("/").split("/")[-1])

    # Save the cache
    save_cache(cache_key, p01s)

    return p01s

def exv_to_p02(exv_code: str) -> List[str]:

    cache_key = f"exv_to_p02_{md5_hash(exv_code)}"
    cache = load_cache(cache_key)
    if cache is not None:
        return cache
    
    # Construct full identifier
    exv_identifiers = map(lambda exv_code: f'<http://vocab.nerc.ac.uk/collection/EXV/current/{exv_code}/>', [exv_code])
    exv_identifiers = "\n".join(exv_identifiers)
    
    # Create the query with the user input
    sparql_query = f"""
        PREFIX dce: <http://purl.org/dc/elements/1.1/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX iadopt: <https://w3id.org/iadopt/ont#> 
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT DISTINCT ?p02 ?prefLabel ?notation
        WHERE {{
            VALUES ?exv {{
                {exv_identifiers}
            }}
                    
            OPTIONAL {{?exv iadopt:hasApplicableMatrix ?matrix .}}
            ?exv iadopt:hasApplicableObjectOfInterest ?ooi .
            ?exv iadopt:hasApplicableProperty ?property .

            <http://vocab.nerc.ac.uk/collection/P01/current/> skos:member ?p01 .

            OPTIONAL {{ ?p01 iadopt:hasMatrix ?matrix . }}
            ?p01 iadopt:hasObjectOfInterest ?ooi .
            ?p01 iadopt:hasProperty ?property .

            ?p01 skos:broader ?p02 . 
            <http://vocab.nerc.ac.uk/collection/P02/current/> skos:member ?p02 .
            
            OPTIONAL {{ ?p02 skos:prefLabel ?prefLabel .
                    FILTER(LANG(?prefLabel) = "en")
            }}
            OPTIONAL {{ ?p02 skos:notation ?notation . }}
        }}
    """
    
    # Set up the SPARQL request
    sparql = SPARQLWrapper(NERC_VOCAB_SPARQL_ENDPOINT)
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)

    # Run the query and parse results
    results = sparql.query().convert()

    p02s = []

    # Show results
    for result in results["results"]["bindings"]:
        uri = result.get("p02", {}).get("value", "")
        p02s.append(uri.rstrip("/").split("/")[-1])

    # Save the cache
    save_cache(cache_key, p02s)

    return p02s

def exv_to_p07(exv_code: str, return_preflabel: bool = False) -> List[str]:

    cache_key = f"exv_to_p07_{md5_hash(exv_code)}_{'preflabel' if return_preflabel else 'uri'}"
    cache = load_cache(cache_key)
    if cache is not None:
        return cache
    
    exv_identifiers = map(lambda exv_code: f'<http://vocab.nerc.ac.uk/collection/EXV/current/{exv_code}/>', [exv_code])
    exv_identifiers = "\n".join(exv_identifiers)
    
    sparql_query = f"""
    PREFIX dce: <http://purl.org/dc/elements/1.1/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX iadopt: <https://w3id.org/iadopt/ont#> 
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT DISTINCT ?p07 ?prefLabel ?notation
    WHERE {{
        VALUES ?exv {{
            {exv_identifiers}
        }} 

        OPTIONAL {{?exv iadopt:hasApplicableMatrix ?matrix .}}
        ?exv iadopt:hasApplicableObjectOfInterest ?ooi .
        ?exv iadopt:hasApplicableProperty ?property .

        <http://vocab.nerc.ac.uk/collection/P07/current/> skos:member ?p07 .

        OPTIONAL {{ ?p07 iadopt:hasMatrix ?matrix . }}
        ?p07 iadopt:hasObjectOfInterest ?ooi .
        ?p07 iadopt:hasProperty ?property .

        OPTIONAL {{ ?p07 skos:prefLabel ?prefLabel .
                FILTER(LANG(?prefLabel) = "en")
        }}
        OPTIONAL {{ ?p07 skos:notation ?notation . }}
    }}
    """
    
    # print(sparql_query)

    # Set up the SPARQL request
    sparql = SPARQLWrapper(NERC_VOCAB_SPARQL_ENDPOINT)
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)

    # Run the query and parse results
    results = sparql.query().convert()
    
    return_val = []
    
    if return_preflabel:
        for result in results["results"]["bindings"]:
            preflabel = result.get("prefLabel", {}).get("value", "")
            return_val.append(preflabel)
            
    else:
        # Show results
        for result in results["results"]["bindings"]:
            uri = result.get("p07", {}).get("value", "")
            return_val.append(uri.rstrip("/").split("/")[-1])

    # Save the cache
    save_cache(cache_key, return_val)
    
    return return_val


def exv_to_r03(exv_code: str) -> List[str]:
    cache_key = f"exv_to_r03_{md5_hash(exv_code)}"
    cache = load_cache(cache_key)
    if cache is not None:
        return cache
    
    exv_identifiers = map(lambda exv_code: f'<http://vocab.nerc.ac.uk/collection/EXV/current/{exv_code}/>', [exv_code])
    exv_identifiers = "\n".join(exv_identifiers)
    sparql_query = f"""
        PREFIX dce: <http://purl.org/dc/elements/1.1/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX iadopt: <https://w3id.org/iadopt/ont#> 
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>

        SELECT DISTINCT ?r03 ?prefLabel ?notation
        WHERE {{
            VALUES ?exv {{
                {exv_identifiers}
            }}

            OPTIONAL {{?exv iadopt:hasApplicableMatrix ?matrix .}}
            ?exv iadopt:hasApplicableObjectOfInterest ?ooi .
            ?exv iadopt:hasApplicableProperty ?property .

            <http://vocab.nerc.ac.uk/collection/P01/current/> skos:member ?p01 .

            OPTIONAL {{ ?p01 iadopt:hasMatrix ?matrix . }}
            ?p01 iadopt:hasObjectOfInterest ?ooi .
            ?p01 iadopt:hasProperty ?property .

            <http://vocab.nerc.ac.uk/collection/R03/current/> skos:member ?r03 .
            
            ?r03 owl:sameAs ?p01 .
      
            OPTIONAL {{ ?r03 skos:prefLabel ?prefLabel .
                FILTER(LANG(?prefLabel) = "en")
            }}
            OPTIONAL {{ ?r03 skos:notation ?notation . }}
        }}
    """
    
    # print(sparql_query)

    # Set up the SPARQL request
    sparql = SPARQLWrapper(NERC_VOCAB_SPARQL_ENDPOINT)
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)

    # Run the query and parse results
    results = sparql.query().convert()

    r03s = []

    # Show results
    for result in results["results"]["bindings"]:
        uri = result.get("r03", {}).get("value", "")
        r03s.append(uri.rstrip("/").split("/")[-1])
        
    # Save the cache
    save_cache(cache_key, r03s)

    return r03s


IAGOS_MAPPING: Dict[str, List[str]] = {
    "mole_fraction_of_carbon_monoxide_in_air": ["CO"],
    "mole_fraction_of_carbon_dioxide_in_air": ["CO2"],
    "mole_fraction_of_methane_in_air": ["CH4"],
    "mole_fraction_of_nitrous_oxide_in_air": ["N2O"],
    "mole_fraction_of_nitrogen_dioxide_in_air": ["NO2"],
    "mole_concentration_of_dissolved_molecular_oxygen_in_sea_water": ["O2"],
    "mole_concentration_of_silicate_in_sea_water": ["SiO4"],
    # "mass_concentration_of_silicate_in_sea_water": ["SiO4_mass"],
    # "mass_concentration_of_phosphate_in_sea_water": ["PO4_mass"],
    "mole_concentration_of_phosphate_in_sea_water": ["PO4"],
    "mole_concentration_of_nitrate_and_nitrite_in_sea_water": ["NO3", "NO2"],
    "mole_concentration_of_nitrate_in_sea_water": ["NO3"],
    # "sea_surface_temperature": ["SST"],
    # "sea_surface_subskin_temperature": ["SST_subskin"],
    # "sea_water_temperature": ["WTMP"],
}

def p07_to_iagos(p07_codes: List[str]) -> List[str]:
    """ Convert P07 codes to IAGOS codes
    """
    
    result = list(dict.fromkeys(
        iagos_code
        for p07 in p07_codes
        for iagos_code in IAGOS_MAPPING.get(p07, [])
    ))
        
    return result


# --------------------


