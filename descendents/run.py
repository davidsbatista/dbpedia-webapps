import random

from datetime import datetime
from SPARQLWrapper import SPARQLWrapper, JSON
from flask import Flask, render_template
from flask import request

app = Flask(__name__)


def get_descendants(category):

    query = '''
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX quepy: <http://www.machinalis.com/quepy#>
    PREFIX dbpedia: <http://dbpedia.org/ontology/>
    PREFIX dbpprop: <http://dbpedia.org/property/>
    PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
    PREFIX dbc:<http://dbpedia.org/resource/Category:>

    SELECT ?X
    WHERE {
        ?X dct:subject dbc:%s .
        ?X dbpedia-owl:abstract ?abstract .
        ?X dbpedia-owl:thumbnail ?thumbnail .
        filter(langMatches(lang(?abstract),"en"))
    }

    ''' % category

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    results = map(
        lambda x:
        x['X']['value'],
        results['results']['bindings']
    )

    return results


def get_info(name_url):

    query = """
    PREFIX dbpedia: <http://dbpedia.org/resource/>
    SELECT ?property ?hasValue ?isValueOf
    WHERE {
      { dbpedia:%s ?property ?hasValue }
    }""" % name_url

    results = None

    try:
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
    except Exception, e:
        print e

    abstracts = []
    birth_date = ''
    death_date = ''
    birthName = ''
    foaf_name = ''
    dbpedia_name = ''
    thumbnail = ''
    shortDescription = ''
    occupation = ''
    knownFor = ''
    description = ''
    subjects = []

    # print json.dumps(results, indent=4, sort_keys=True)

    # http://dbpedia.org/ontology/abstract
    # http://dbpedia.org/property/shortDescription
    # http://purl.org/dc/elements/1.1/description

    # http://dbpedia.org/property/occupation
    # http://dbpedia.org/ontology/knownFor
    # http://purl.org/dc/terms/subject

    # http://dbpedia.org/ontology/birthYear
    # http://dbpedia.org/ontology/birthDate
    # http://dbpedia.org/ontology/deathDate
    # http://dbpedia.org/ontology/birthPlace
    # http://dbpedia.org/property/deathPlace
    # http://dbpedia.org/ontology/deathYear

    # http://dbpedia.org/ontology/thumbnail

    # http://dbpedia.org/property/birthName
    # http://xmlns.com/foaf/0.1/name
    # http://dbpedia.org/property/name

    for result in results["results"]["bindings"]:

        if result['property']['value'] == 'http://dbpedia.org/ontology/abstract':
            abstracts.append(result['hasValue'])

        if result['property']['value'] == 'http://dbpedia.org/property/shortDescription':
            shortDescription = result['hasValue']['value']

        if result['property']['value'] == 'http://purl.org/dc/elements/1.1/description':
            description = result['hasValue']['value']

        if result['property']['value'] == 'http://dbpedia.org/property/occupation':
            occupation = result['hasValue']['value']

        if result['property']['value'] == 'http://dbpedia.org/property/knownFor':
            knownFor = result['hasValue']['value']

        if result['property']['value'] == 'http://purl.org/dc/terms/subject':
            subjects = result['hasValue']['value']

        #########

        if result['property']['value'] == 'http://dbpedia.org/ontology/birthDate':
            birth_date = result['hasValue']['value']

        if result['property']['value'] == 'http://dbpedia.org/ontology/deathDate':
            death_date = result['hasValue']['value']

        #########

        if result['property']['value'] == 'http://xmlns.com/foaf/0.1/name':
            foaf_name = result['hasValue']['value']

        if result['property']['value'] == 'http://dbpedia.org/property/name':
            dbpedia_name = result['hasValue']['value']

        if result['property']['value'] == 'http://dbpedia.org/property/birthName':
            birthName = result['hasValue']['value']

        #########

        if result['property']['value'] == 'http://dbpedia.org/ontology/thumbnail':
            thumbnail = result['hasValue']['value']

    for abstract in abstracts:
        if abstract['xml:lang'] == 'en':
            text = abstract['value']

    data = {'abstract': text,
            'birth_date': birth_date,
            'death_date': death_date,
            'thumbnail': thumbnail,
            'name': foaf_name,
            'dbpedia_name': dbpedia_name,
            'birthName': birthName,
            'shortDescription': shortDescription,
            'occupation': occupation,
            'knownFor': knownFor,
            'description': description,
            'subject': subjects
            }

    return data


def load_categories():
    with open("categories.txt") as f:
        content = f.readlines()
    content = [x.strip().replace("http://dbpedia.org/resource/Category:", "")
               for x in content]
    return content


@app.route("/")
def template_test():
    f_logs = open('access.log', 'a+')
    request_vars = request.__dict__['environ']
    try:
	user_agent_value=request_vars['HTTP_USER_AGENT']
    except Exception, e:
	user_agent_value = "Error"
    access = str('{ip_address} , {date_time} , "{method} {path} {query} '
                 '{protocol} , {user_agent}"'.
                 format(ip_address=request_vars['REMOTE_ADDR'],
                        date_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        method=request_vars['REQUEST_METHOD'],
                        path=request_vars['PATH_INFO'],
                        protocol=request_vars['SERVER_PROTOCOL'],
                        query=request_vars['QUERY_STRING'],
                        user_agent=user_agent_value))
    f_logs.write(access+'\n')
    f_logs.flush()

    # get a list of descendants from a random category
    category = random.choice(descendants_categories)
    #i = random.randint(0, len(descendants_categories) - 1)
    #category = descendants_categories[i]
    descendants = get_descendants(category)
    while len(descendants)==0:
	category = random.choice(descendants_categories)
        descendants = get_descendants(category)

    try:
       name_url = random.choice(descendants).replace('http://dbpedia.org/resource/', '')
    except Exception, e:
       print len(descendants)
       print descendants
    
    # TODO: fix this
    while "(" in name_url or "'" in name_url or "," in name_url:
        #i = random.randint(0, len(descendants))
        #name_url = descendants[i].replace('http://dbpedia.org/resource/', '')
	 name_url = random.choice(descendants).replace('http://dbpedia.org/resource/', '')

    # get info/properties of a person(descendant
    info = get_info(name_url)

    info['wiki_url'] = "https://www.wikiwand.com/en/"+name_url
    info['category'] = category

    if info['description'] == '' and info['shortDescription'] != '':
        info['description'] = info['shortDescription']

    elif info['description'] == '' == info['shortDescription']:
        info['description'] = info['occupation'].\
            replace('http://dbpedia.org/resource/', '')

    if "," in info['name'] and info['birthName'] != '':
        info['name'] = info['birthName']

    return render_template('template.html', **info)

if __name__ == '__main__':
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setReturnFormat(JSON)
    descendants_categories = load_categories()
    app.run(host="0.0.0.0", port=80, debug=True)
