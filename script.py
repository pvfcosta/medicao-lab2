
import requests
import pandas as pd
import datetime
from pathlib import Path
import pygit2
import subprocess
import json
import numpy as np
import shutil

# colocar token aqui
token = "eOVIR7AwkNb7mzKjuY4UoGSqedkBkL0dC4nu"

headers = {"Authorization": "bearer ghp_"+token}

csvSize = 1000

reposCsvName = 'repositoriosLab2.csv'
reposCsvPath = Path('./'+reposCsvName)

ckCsvName = 'ckResult.csv'
ckCsvPath = Path('./'+ckCsvName)

def age(createdAt):
    today = datetime.datetime.utcnow()
    age = today.year - createdAt.year - \
        ((today.month, today.day) < (createdAt.month, createdAt.day))
    return age

# funcao para preencher csv com determinada quantidade de repositorios
def fillCsv():
    query = """
    {
        search(
            query: "stars:>100 language:java"
            type: REPOSITORY
            first: 10
            after: null
        ) {
            pageInfo {
            endCursor
            startCursor
            }
            nodes {
            ... on Repository {
                nameWithOwner
                name
                url
                stargazerCount
                releases(first: 1) {
                totalCount
                }
                createdAt
            }
            }
        }
    }
    """
    allResults = []
    endCursor = "null"
    error = 0
    while (len(allResults) < csvSize):
        request = requests.post('https://api.github.com/graphql',
                                json={'query': query}, headers=headers)
        result = request.json()
        if 'data' in result:
            allResults += result['data']['search']['nodes']
            query = query.replace(endCursor, '"'+result['data']
                                  ['search']['pageInfo']['endCursor']+'"')
            endCursor = '"' + \
                result['data']['search']['pageInfo']['endCursor']+'"'
        else:
            error += 1
            if (error > 5):
                print("Error na chamada da api do git hub")
                print(result)
                break
            else:
                continue

    for result in allResults:
        releases = result['releases']['totalCount']
        result['releases'] = releases
        createdAt = datetime.datetime.strptime(
            result['createdAt'], '%Y-%m-%dT%H:%M:%SZ')
        result['createdAt'] = datetime.datetime.strftime(
            createdAt, '%d/%m/%Y %H:%M:%S')
        result['ageInYears'] = age(createdAt)

    df = pd.DataFrame(allResults)

    df.to_csv(reposCsvName, index=False, sep=';')


# checa se csv de repositorios ja tem o numero suficiente, se nao tem preenche
if reposCsvPath.is_file():
    df = pd.read_csv(reposCsvName)
    if len(df.index) < (csvSize):
        fillCsv()
else:
    fillCsv()

# le do csv de repositorios e itera sobre eles
repos = pd.read_csv(reposCsvPath, header=1, sep=';', usecols=[1, 2, 3, 4, 6])

if ckCsvPath.is_file():
    ckResults = pd.read_csv(ckCsvPath, header= 1, sep=';')
else:
    ckResults = pd.DataFrame()

for repo in repos.values.tolist():
    if repo[0] in ckResults.values.tolist():
        continue
    else:
        clonedRepo = pygit2.clone_repository(repo[1], './repos/'+repo[0])
        # repositorio clonado: clonedRepo, uma classe que contem info do repositorio
        # inserir a logica do ck aqui

        ckFileSubstring = repo[0]+"ck"

        powershellCommand = "java -jar ck/target/ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar repos/"+repo[0]+" true 0 False metrics/"+ckFileSubstring

        process = subprocess.Popen(["powershell",powershellCommand], stdout=subprocess.PIPE)

        output, error = process.communicate()

        ckMetricsFilePath = "./metrics/"+ckFileSubstring+"class.csv"

        ckMetricsFile = pd.read_csv(ckMetricsFilePath,sep=',')

        metrics = {
            "name": repo[0],
            "popularity": repo[2],
            "releases":repo[3],
            "age": repo[4],
            "loc":sum(ckMetricsFile['loc']),
            "cbo": np.median(ckMetricsFile['cbo']),
            "dit":np.median(ckMetricsFile['dit']),
            "lcom":np.median(ckMetricsFile['lcom']),
        }

        # depois append no data frame do pandas e grava no csv pra não perder o progresso do script
        ckResults = pd.concat([ckResults,pd.DataFrame.from_records([metrics])])
        ckResults.to_csv(ckCsvName, index=False, sep=';')

        repoFolder = "./repos/"+repo[0]
        shutil.rmtree(repoFolder, ignore_errors=True)

        quit()



