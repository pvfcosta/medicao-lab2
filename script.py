
import requests
import pandas as pd
import datetime
from pathlib import Path
import pygit2
import subprocess
import json
import numpy as np
import shutil
import os
import stat
from git import Repo
import matplotlib.pyplot as plot
import seaborn as sns

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
repos = pd.read_csv(reposCsvPath, header=0, sep=';', usecols=[1, 2, 3, 4, 6])

if ckCsvPath.is_file():
    ckResults = pd.read_csv(ckCsvPath, header= 0, sep=';')
else:
    ckResults = pd.DataFrame()

for index, repo in enumerate(repos.values.tolist()):
    if repo[0] in ckResults['name'].tolist():
        continue
    else:
        print(repo[0])
        print(repo[1])
        
        repoFolder = "./repos/"+repo[0]

        ckFileSubstring = repo[0]+"ck"

        ckMetricsFilePath = f"./metrics/{ckFileSubstring}class.csv"

        if not os.path.isdir(repoFolder) and not (os.path.isfile(ckMetricsFilePath) and os.stat(ckMetricsFilePath).st_size != 0):
            Repo.clone_from(repo[1]+".git", repoFolder, depth=1, filter='blob:none')

        # repositorio clonado: clonedRepo, uma classe que contem info do repositorio

        if not os.path.isfile(ckMetricsFilePath) or os.stat(ckMetricsFilePath).st_size == 0:
            powershellCommand = f"java -jar ck/target/ck-0.7.1-SNAPSHOT-jar-with-dependencies1.jar repos/{repo[0]} true 0 False metrics/{ckFileSubstring}"

            process = subprocess.Popen(["powershell",powershellCommand], stdout=subprocess.PIPE)

            output, error = process.communicate()

        if os.path.isfile(ckMetricsFilePath) and os.stat(ckMetricsFilePath).st_size != 0:
            print(index)
            ckMetricsFile = pd.read_csv(ckMetricsFilePath,sep=',')
            metrics = {
                "name": repo[0],
                "popularity": repo[2],
                "releases":repo[3],
                "age": repo[4],
                "loc": np.sum(ckMetricsFile['loc']) if len(ckMetricsFile['loc']) > 0 else None,
                "cbo": np.median(ckMetricsFile['cbo']) if len(ckMetricsFile['cbo']) > 0 else None,
                "dit": np.amax(ckMetricsFile['dit']) if len(ckMetricsFile['dit']) > 0 else None,
                "lcom":np.median(ckMetricsFile['lcom']) if len(ckMetricsFile['lcom']) > 0 else None,
            }
        else:
            metrics = {
                "name": repo[0],
                "popularity": repo[2],
                "releases":repo[3],
                "age": repo[4],
                "loc":  None,
                "cbo": None,
                "dit": None,
                "lcom": None,
            }

        # depois append no data frame do pandas e grava no csv pra não perder o progresso do script
        ckResults = pd.concat([ckResults,pd.DataFrame.from_records([metrics])])
        ckResults.to_csv(ckCsvName, index=False, sep=';')

        shutil.rmtree(repoFolder, ignore_errors=True)



# cria gráfico
ckResultsGraph = pd.read_csv(ckCsvPath, header= 0, sep=';')

# ckResultsGraph.plot.scatter(x='popularity', y='cbo')
# plot.savefig('graphs/sct_popularity_cbo.png')
lmplot = sns.lmplot(x='popularity',y='cbo',data=ckResultsGraph,fit_reg=True) 
lmplot.savefig('graphs/lm_popularity_cbo.png') 
print("Coeficiente de correlação popularidade x cbo : ")
print(ckResultsGraph['popularity'].corr(ckResultsGraph['cbo']))

# ckResultsGraph.plot.scatter(x='popularity', y='dit')
# plot.savefig('graphs/sct_popularity_dit.png')
lmplot = sns.lmplot(x='popularity',y='dit',data=ckResultsGraph,fit_reg=True) 
lmplot.savefig('graphs/lm_popularity_dit.png') 
print("Coeficiente de correlação popularidade x dit : ")
print(ckResultsGraph['popularity'].corr(ckResultsGraph['dit']))

# ckResultsGraph.plot.scatter(x='popularity', y='lcom')
# plot.savefig('graphs/sct_popularity_lcom.png')
lmplot = sns.lmplot(x='popularity',y='lcom',data=ckResultsGraph,fit_reg=True) 
lmplot.savefig('graphs/lm_popularity_lcom.png') 
print("Coeficiente de correlação popularidade x lcom : ")
print(ckResultsGraph['popularity'].corr(ckResultsGraph['lcom']))

# ckResultsGraph.plot.scatter(x='loc', y='cbo')
# plot.savefig('graphs/sct_loc_cbo.png')
lmplot = sns.lmplot(x='loc',y='cbo',data=ckResultsGraph,fit_reg=True) 
lmplot.savefig('graphs/lm_loc_cbo.png') 
print("Coeficiente de correlação loc x cbo : ")
print(ckResultsGraph['loc'].corr(ckResultsGraph['cbo']))

# ckResultsGraph.plot.scatter(x='loc', y='dit')
# plot.savefig('graphs/sct_loc_dit.png')
lmplot = sns.lmplot(x='loc',y='dit',data=ckResultsGraph,fit_reg=True) 
lmplot.savefig('graphs/lm_loc_dit.png') 
print("Coeficiente de correlação loc x dit : ")
print(ckResultsGraph['loc'].corr(ckResultsGraph['dit']))

# ckResultsGraph.plot.scatter(x='loc', y='lcom')
# plot.savefig('graphs/sct_loc_lcom.png')
lmplot = sns.lmplot(x='loc',y='lcom',data=ckResultsGraph,fit_reg=True) 
lmplot.savefig('graphs/lm_loc_lcom.png') 
print("Coeficiente de correlação loc x lcom : ")
print(ckResultsGraph['loc'].corr(ckResultsGraph['lcom']))

# ckResultsGraph.plot.scatter(x='releases', y='cbo')
# plot.savefig('graphs/sct_releases_cbo.png')
lmplot = sns.lmplot(x='releases',y='cbo',data=ckResultsGraph,fit_reg=True) 
lmplot.savefig('graphs/lm_releases_cbo.png') 
print("Coeficiente de correlação releases x cbo : ")
print(ckResultsGraph['releases'].corr(ckResultsGraph['cbo']))

# ckResultsGraph.plot.scatter(x='releases', y='dit')
# plot.savefig('graphs/sct_releases_dit.png')
lmplot = sns.lmplot(x='releases',y='dit',data=ckResultsGraph,fit_reg=True) 
lmplot.savefig('graphs/lm_releases_dit.png') 
print("Coeficiente de correlação releases x dit : ")
print(ckResultsGraph['releases'].corr(ckResultsGraph['dit']))

# ckResultsGraph.plot.scatter(x='releases', y='lcom')
# plot.savefig('graphs/sct_releases_lcom.png')
lmplot = sns.lmplot(x='releases',y='lcom',data=ckResultsGraph,fit_reg=True) 
lmplot.savefig('graphs/lm_releases_lcom.png') 
print("Coeficiente de correlação releases x lcom : ")
print(ckResultsGraph['releases'].corr(ckResultsGraph['lcom']))

# ckResultsGraph.plot.scatter(x='age', y='cbo')
# plot.savefig('graphs/sct_age_cbo.png')
lmplot = sns.lmplot(x='age',y='cbo',data=ckResultsGraph,fit_reg=True) 
lmplot.savefig('graphs/lm_age_cbo.png') 
print("Coeficiente de correlação age x cbo : ")
print(ckResultsGraph['age'].corr(ckResultsGraph['cbo']))

# ckResultsGraph.plot.scatter(x='age', y='dit')
# plot.savefig('graphs/sct_age_dit.png')
lmplot = sns.lmplot(x='age',y='dit',data=ckResultsGraph,fit_reg=True) 
lmplot.savefig('graphs/lm_age_dit.png') 
print("Coeficiente de correlação age x dit : ")
print(ckResultsGraph['age'].corr(ckResultsGraph['dit']))

# ckResultsGraph.plot.scatter(x='age', y='lcom')
# plot.savefig('graphs/sct_age_lcom.png')
lmplot = sns.lmplot(x='age',y='lcom',data=ckResultsGraph,fit_reg=True) 
lmplot.savefig('graphs/lm_age_lcom.png') 
print("Coeficiente de correlação age x lcom : ")
print(ckResultsGraph['age'].corr(ckResultsGraph['lcom']))