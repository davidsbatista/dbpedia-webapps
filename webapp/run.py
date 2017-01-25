import random

from SPARQLWrapper import SPARQLWrapper, JSON
from flask import Flask, render_template

app = Flask(__name__)


def get_personalities():

    sparql.setQuery("""
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX quepy: <http://www.machinalis.com/quepy#>
    PREFIX dbpedia: <http://dbpedia.org/ontology/>
    PREFIX dbpprop: <http://dbpedia.org/property/>
    PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>

    SELECT ?X
    WHERE {
    { ?X dct:subject dbc:Portuguese_poets }
    UNION
    { ?X dct:subject dbc:Mozambican_poets }
    UNION
    { ?X dct:subject dbc:Portuguese_male_writers }
    UNION
    { ?X dct:subject dbc:Portuguese_poets }
    UNION
    { ?X dct:subject dbc:Portuguese_philosophers }
    UNION
    { ?X dct:subject dbc:Portuguese_women_writers }
    UNION
    { ?X dct:subject dbc:Portuguese_women_poets }
    }

    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    return results


def choose_personality(personalities):

    authors = personalities["results"]["bindings"]
    i = random.randint(0, len(authors) - 1)
    author_resource = authors[i]['X']['value']
    name_url = author_resource.split('/')[-1]

    return name_url


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
    name = ''
    thumbnail = ''

    # http://dbpedia.org/ontology/abstract
    # http://dbpedia.org/ontology/birthDate
    # http://dbpedia.org/ontology/deathDate
    # http://dbpedia.org/ontology/birthPlace
    # http://dbpedia.org/property/deathPlace
    # http://dbpedia.org/ontology/thumbnail
    # http://xmlns.com/foaf/0.1/name

    for result in results["results"]["bindings"]:

        if result['property']['value'] == 'http://dbpedia.org/ontology/abstract':
            abstracts.append(result['hasValue'])

        if result['property']['value'] == 'http://dbpedia.org/ontology/birthDate':
            birth_date = result['hasValue']['value']

        if result['property']['value'] == 'http://dbpedia.org/ontology/deathDate':
            death_date = result['hasValue']['value']

        if result['property']['value'] == 'http://dbpedia.org/ontology/thumbnail':
            thumbnail = result['hasValue']['value']

        if result['property']['value'] == 'http://xmlns.com/foaf/0.1/name':
            name = result['hasValue']['value']

    data = {'abstract': select_abstract_lang(abstracts),
            'birth_date': birth_date,
            'death_date': death_date,
            'thumbnail': thumbnail,
            'name': name,
            }

    return data


def select_abstract_lang(abstracts):

    for abstract in abstracts:
        if abstract['xml:lang'] == 'pt':
            selected_abstract = abstract['value']
            break

        elif abstract['xml:lang'] == 'en':
            selected_abstract = abstract['value']
            break

        elif abstract['xml:lang'] == 'es':
            selected_abstract = abstract['value']
            break

        elif abstract['xml:lang'] == 'de':
            selected_abstract = abstract['value']
            break

        elif abstract['xml:lang'] == 'fr':
            selected_abstract = abstract['value']
            break

        else:
            selected_abstract = None

    return selected_abstract


@app.route("/")
def template_test():
    personalities = get_personalities()
    name_url = choose_personality(personalities)

    while "(" in name_url or "'" in name_url or "," in name_url:
        name_url = choose_personality(personalities)

    info = get_info(name_url)

    while info['thumbnail'] == '':

        name_url = choose_personality(personalities)

        while "(" in name_url or "'" in name_url or "," in name_url:
            name_url = choose_personality(personalities)

        info = get_info(name_url)

    return render_template('template.html', **info)


if __name__ == '__main__':
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setReturnFormat(JSON)
    app.run(host="0.0.0.0", port=80, debug=True)
