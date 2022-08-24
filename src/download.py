import urllib.request
import json
import sys
import requests
import os
from jsonpath_ng import jsonpath, parse

ehri_terms_first_part = """{
  Repository(id: \""""

ehri_terms_second_part = """\") {
    id
    documentaryUnits(after: \""""

ehri_terms_last_part = """\") {
      items {
        identifier
        descriptions {
          accessPoints {
            name
          }
        }
      }
      pageInfo {
        hasPreviousPage
        previousPage
        hasNextPage
        nextPage
  		}
    }
  }
}"""

def extract_terms_from_json(type_name, number_of_files):
    for i in range(1, number_of_files + 1):
        filename = type_name + "/" + type_name + "_" + str(i) + ".json"
        with open(filename, "r", encoding="utf-8") as file:
            json_data = json.loads(file.read())
            jsonpath_exp = parse("$.data.Repository.documentaryUnits.items[*].descriptions[*].accessPoints[*].name")
            result = jsonpath_exp.find(json_data)
            with open("result.txt", "w", encoding="utf-8") as output_file:
                output_file.write("") #Removes old content
            with open("result.txt", "a", encoding="utf-8") as output_file:
                for value in result:
                    output_file.write(value.value + "\n")


def download_from_graphql(type_name, url, query_start, query_end):
    i = 1
    after = ""
    next_page = True
    while next_page:
        filename = type_name + "/" + type_name + "_" + str(i) + ".json"
        final_query = query_start + after + query_end
        json_query = {'query': final_query}
        headers = {'Content-type': 'application/json'}
        r = requests.post(url=url, json=json_query, headers=headers)
        with open(filename, "w", encoding="utf-8") as file:
            file.write(r.text)
        json_content = r.text
        data = json.loads(json_content)
        next_page = data['data']['Repository']['documentaryUnits']['pageInfo']['hasNextPage']
        after = data['data']['Repository']['documentaryUnits']['pageInfo']['nextPage']
        i += 1
    return i - 1

if __name__ == '__main__':
    institution_id = sys.argv[1]
    use_stage = len(sys.argv) > 2 and sys.argv[2] == "--stage"

    if(use_stage):
      grapql_url = "https://portal.ehri-project-stage.eu/api/graphql"
    else:
      grapql_url = "https://portal.ehri-project.eu/api/graphql"
    
    
    print("Downloading terms for " + institution_id + "...")
    query_start = ehri_terms_first_part + sys.argv[1] + ehri_terms_second_part
    total = download_from_graphql("terms", grapql_url, query_start, ehri_terms_last_part)

    print("Extracting the terms...")
    extract_terms_from_json("terms", total)

    print("Applying distinct to the results...")
    os.system("more result.txt | sort | uniq > resultUnique.txt")





