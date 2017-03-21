#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import math

from random import randint
from time import sleep

from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.setReturnFormat(JSON)


def descent_categories():
    sparql.setQuery("""
    SELECT DISTINCT(?value)
    WHERE { 
        ?resource <http://purl.org/dc/terms/subject> ?value .
        FILTER regex(?value, "Category:American_people_of_.*descent", "i") 
    }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    return results
    
def get_personalities(category):

    query = """
    SELECT ?isValueOf
    WHERE { 
        ?isValueOf <http://purl.org/dc/terms/subject> <%s> .      
    }
    """ % category
    
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    return results

def get_person_info(person_url):
    
    while True:        
        try:
            query = """
            SELECT ?property ?hasValue
            WHERE {
                <%s> ?property ?hasValue
            }
            """ % person_url
                        
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
		    
            return results
        
        except Exception, e:
            print e
            print "Sleeping "
            sleep(randint(1,10))
                
def get_all_persons_urls():
    
    result_json = descent_categories()
    
    personalities = set()
    
    for x in result_json['results']['bindings']:
        categ =  x['value']['value']
        sleep(randint(1,5))
        print categ
        results = get_personalities(categ)
        for person in results['results']['bindings']:
            personalities.add(person['isValueOf']['value'])
            
    print len(personalities)
    
    f_output = open("personalities_dbpedia_url.txt","wb")
    
    for x in sorted(personalities):
        f_output.write(str(x.encode("utf8"))+'\n')
    
    f_output.close()

def main():
    
    #get_all_persons_urls()

    # all urls
    with open("personalities_dbpedia_url.txt") as f:
        content = f.readlines()    
    to_process = [x.strip() for x in content]
    total = len(content)

    # urls already processed
    f_processed = open("personalities_dbpedia_url_processed.txt", "r+")
    content = f_processed.readlines()
    processed = [x.strip() for x in content]
    
    # urls to process
    to_process = sorted(list(set(to_process) - set(processed)))
    
    # file to store the results as they are fetched
    f_all_results = open("all_results.json", "a+")
        
    count = 0
    all_results = []
        
    for person_url in to_process:
                        
        print person_url
        
        try:
    	    results = get_person_info(person_url)        
            f_all_results.write(json.dumps(results)+'\n')
            f_all_results.flush()
                
            f_processed.write(str(person_url.encode("utf8"))+'\n')
            f_processed.flush()
            
        except Exception, e:
            print e
            os.fsync(f_all_results)
            os.fsync(f_processed)
        
        count += 1
        
        if count % 100 == 0:
            print count,"of",total    
        
        sleep(randint(1,10))
                

if __name__ == '__main__':
	main()
