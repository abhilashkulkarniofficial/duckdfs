import click
import json
import os
import time
import datetime as dt
import random
import requests
import pandas as pd
import socket
import warnings


warnings.filterwarnings("ignore", category=FutureWarning)

f = open('duckdfsimage.json')
directory = json.load(f)
f.close()
curr_directory = directory["DuckDFSCurrentINode"]

def updateFireBase(directory):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    s.getsockname()[0]
    url = 'https://dsci551x86-default-rtdb.firebaseio.com/duckdfsimage-'+str('-'.join(s.getsockname()[0].split('.')))+'.json'
    requests.put(url, data = json.dumps(directory))


def parsePermission(d,permission):
    table = {'0':'','1':'--x','2':'-w-','3':'-wx','4':'r--','5':'r-x','6':'rw-','7':'rwx'}
    converted_permission = 'd' if d else '-'
    for x in permission:
        converted_permission += table[x]
    return converted_permission

def createFile(input_filename, data, parent_id, size):
    try:
        max_id = int(directory["DuckDFSGlobal"]["max_id"])
        file_id = max_id+1
        filename = f'{file_id:03}___{input_filename}'
        block_filenames = [f'{file_id:03}___{x:03}___{input_filename}' for x in range(len(data))]
        block_data = {}
        for index, file in enumerate(block_filenames):
            block_data[f'{index+1:03}'] = {
                "name": file,
                "block_id": f'block_{random.randrange(1,directory["DuckDFSConfiguration"]["blocks"]+1):03}'
            }
        directory["DuckDFSINodeSection"][file_id] = {"name": filename, "id": str(file_id), "permission": "744", "ctime":time.time(), "type": "FILE", "size": size, "blocks":block_data}
        if parent_id in directory["DuckDFSINodeDirectorySection"]["children"].keys():
            directory["DuckDFSINodeDirectorySection"]["children"][parent_id].append(str(file_id))
        else:
            directory["DuckDFSINodeDirectorySection"]["children"][parent_id] = [str(file_id)]
        directory["DuckDFSINodeDirectorySection"]["parent"][file_id] = parent_id
        index = 0
        for file in block_data:
            f = open(f'files/{block_data[file]["block_id"]}/{block_data[file]["name"]}', "w")
            if data is not None:
                f.write(data[index])
            f.close()
            index+=1
        directory["DuckDFSGlobal"]["max_id"] = str(file_id)
        with open("duckdfsimage.json", "w") as outfile:
            outfile.write(json.dumps(directory))
            updateFireBase(directory)
        click.echo(f'File created with name {input_filename}')
    except:
        click.echo(f'File could not be created :(')

@click.group()
def cli():
    pass

@cli.command()
def pwd():
    click.echo(f'Current directory is {directory["DuckDFSCurrentINode"]["path"]}')

@cli.command()
@click.argument('directory_name')
def cd(directory_name):
    global curr_directory   
    
    # Check if the directory name is ..
    if directory_name == '..':
        if curr_directory['id'] == '0':
            click.echo(f'Already in root directory')
            return
        parent = directory["DuckDFSINodeDirectorySection"]["parent"][curr_directory["id"]]
        directory["DuckDFSCurrentINode"]["id"] = parent
        directory["DuckDFSCurrentINode"]["path"] = '/' + '/'.join(directory["DuckDFSCurrentINode"]["path"].split('/')[:-2])
        with open("duckdfsimage.json", "w") as outfile:
            outfile.write(json.dumps(directory))
            updateFireBase(directory)
        return

    # Check if the directory name is ~
    if directory_name == '~':
        directory["DuckDFSCurrentINode"]["id"] = "0"
        directory["DuckDFSCurrentINode"]["path"] = '/'
        with open("duckdfsimage.json", "w") as outfile:
            outfile.write(json.dumps(directory))
            updateFireBase(directory)
        click.echo(f'In root.')
        return
    
    # Check if the directory is in current directory
    if curr_directory["id"] in directory["DuckDFSINodeDirectorySection"]["children"].keys():
        children = directory["DuckDFSINodeDirectorySection"]["children"][curr_directory["id"]]
        children_names = [directory["DuckDFSINodeSection"][x]["name"] for x in children] 

        if directory_name in children_names:
            file_id = children[children_names.index(directory_name)]
            # Check if the directory name is a DIRECTORY
            if directory["DuckDFSINodeSection"][file_id]["type"] == "DIR":
                directory["DuckDFSCurrentINode"]["id"] = file_id
                directory["DuckDFSCurrentINode"]["path"] = directory["DuckDFSCurrentINode"]["path"] + directory_name + '/'
                with open("duckdfsimage.json", "w") as outfile:
                    outfile.write(json.dumps(directory))
                    updateFireBase(directory)
                return
            else:
                click.echo(f'There is no Directory called {directory_name}')
        else:
            click.echo(f'There is no Directory called {directory_name}')
    else:
        click.echo(f'There is no Directory called {directory_name}')


@cli.command()
def ls():
    global curr_directory
    click.echo(f'{"Name":20}\t\t{"Permission":20}\t\t{"Create Time (UTC)":20}\n{"----":20}\t\t{"----------":20}\t\t{"-----------------":20}')
    click.echo(f'{".":20}\t\t{"":20}\t\t{"":20}\n{"..":20}\t\t{"":20}\t\t{"":20}')
    if curr_directory["id"] in directory["DuckDFSINodeDirectorySection"]["children"].keys():
        children = directory["DuckDFSINodeDirectorySection"]["children"][curr_directory["id"]]
        children_names = []
        for x in children:
            ctime = "-"
            try:
                ctime = dt.datetime.utcfromtimestamp(directory["DuckDFSINodeSection"][x]["ctime"]).strftime("%m/%d/%Y %H:%M")
            except:
                ctime = "-"
            fname = directory["DuckDFSINodeSection"][x]["name"].split("___")[-1]
            permission = parsePermission(True if directory["DuckDFSINodeSection"][x]["type"] == "DIR" else False, directory["DuckDFSINodeSection"][x]["permission"])
            children_names.append(f'{fname:20}\t\t{permission:20}\t\t{ctime:20}')
        
        for child in children_names:
            click.echo(f'{child}')


@cli.command()
@click.argument('name')
def mkdir(name):
    # Parse the name of the Directory
    parsed_name = name.split('/')
    if '' in parsed_name:
        parsed_name.remove('')
    # print(parsed_name)
    file_name = parsed_name[-1]
    parent_id = None

    # Check if the name is a path with Parent name
    if len(parsed_name) > 1:
        parent_name = parsed_name[-2]
        for x in directory["DuckDFSINodeSection"]:
            if directory["DuckDFSINodeSection"][str(x)]["name"] == parent_name:
                parent_id = directory["DuckDFSINodeSection"][str(x)]["id"]
        # Check if parent exists
        if parent_id is None:
            click.echo(f'There is no Directory called {parent_name}')
            return
    else:
        parent_id = curr_directory["id"]

    # Check if directory with same name exists in current directory
    if parent_id in directory["DuckDFSINodeDirectorySection"]["children"].keys():
        children_names = [directory["DuckDFSINodeSection"][x]["name"] for x in directory["DuckDFSINodeDirectorySection"]["children"][parent_id]] 
        if file_name in children_names:
            click.echo(f'Directory with name {file_name} already exists')
            return

    # Create a new Directory
    max_id = int(directory["DuckDFSGlobal"]["max_id"])
    file_id = str(max_id+1)
    directory["DuckDFSGlobal"]["max_id"] = file_id
    directory["DuckDFSINodeSection"][file_id] = {"name": file_name, "id": file_id, "permission": "744", "type": "DIR", "ctime":time.time()}
    # print(parent_id, file_id, directory["DuckDFSINodeSection"][file_id])
    if parent_id in directory["DuckDFSINodeDirectorySection"]["children"].keys():
        directory["DuckDFSINodeDirectorySection"]["children"][parent_id].append(file_id)
    else:
        directory["DuckDFSINodeDirectorySection"]["children"][parent_id] = [file_id]
    directory["DuckDFSINodeDirectorySection"]["parent"][file_id] = parent_id
    with open("duckdfsimage.json", "w") as outfile:
        outfile.write(json.dumps(directory))
        updateFireBase(directory)
    click.echo(f'Directory created with name {file_name}')


@cli.command()
@click.argument('path')
def cat(path):
    global curr_directory
    parsed_path = path.split('/')
    if '' in parsed_path:
        parsed_path.remove('')
    if len(parsed_path) == 1:
        if curr_directory["id"] in directory["DuckDFSINodeDirectorySection"]["children"].keys():
            children_names = [directory["DuckDFSINodeSection"][y]["name"].split("___")[-1] for y in directory["DuckDFSINodeDirectorySection"]["children"][curr_directory["id"]]]
            children_id = [directory["DuckDFSINodeSection"][y]["id"].split("___")[-1] for y in directory["DuckDFSINodeDirectorySection"]["children"][curr_directory["id"]]]
            if parsed_path[0] in children_names:
                file_id = children_id[children_names.index(parsed_path[0])]
                blocks = directory["DuckDFSINodeSection"][file_id]["blocks"]
                fsstream = ''
                for block in blocks:
                    f = open("files/"+blocks[block]['block_id']+"/"+blocks[block]['name'], "r")
                    fsstream += f.read()
                    f.close()
                click.echo(fsstream)
            return

    file_id = None
    for i, x in enumerate(parsed_path):
        current_id = None
        for z in directory["DuckDFSINodeSection"]:
            if directory["DuckDFSINodeSection"][str(z)]["name"] == x:
                current_id = directory["DuckDFSINodeSection"][str(z)]["id"] 
        if current_id is not None and current_id in directory["DuckDFSINodeDirectorySection"]["children"].keys() and i!=len(parsed_path)-1:
            children_names = [directory["DuckDFSINodeSection"][y]["name"].split("___")[-1] for y in directory["DuckDFSINodeDirectorySection"]["children"][current_id]] 
            children_id = [directory["DuckDFSINodeSection"][y]["id"].split("___")[-1] for y in directory["DuckDFSINodeDirectorySection"]["children"][current_id]]
            # print(children_names)
            if parsed_path[i+1] not in children_names:
                click.echo(f'There is no directory or file called {parsed_path[i+1]}')
            else:
                file_id = children_id[children_names.index(parsed_path[i+1])]
        elif i==len(parsed_path)-1:
            blocks = directory["DuckDFSINodeSection"][file_id]["blocks"]
            fsstream = ''
            for block in blocks:
                f = open("files/"+blocks[block]['block_id']+"/"+blocks[block]['name'], "r")
                fsstream += f.read()
                f.close()
            click.echo(fsstream)
        else:
            click.echo(f'There is no directory or file called {x}')
            return
            

@cli.command()
@click.argument('path')
def rm(path):
    global curr_directory
    parsed_path = path.split('/')
    if '' in parsed_path:
        parsed_path.remove('')
    if len(parsed_path) == 1:
        if curr_directory["id"] in directory["DuckDFSINodeDirectorySection"]["children"].keys():
            children_names = [directory["DuckDFSINodeSection"][y]["name"].split("___")[-1] for y in directory["DuckDFSINodeDirectorySection"]["children"][curr_directory["id"]]]
            children_id = [directory["DuckDFSINodeSection"][y]["id"].split("___")[-1] for y in directory["DuckDFSINodeDirectorySection"]["children"][curr_directory["id"]]]
            if parsed_path[0] in children_names:
                file_id = children_id[children_names.index(parsed_path[0])]
                del directory["DuckDFSINodeSection"][file_id]
                parent_id = directory["DuckDFSINodeDirectorySection"]["parent"][file_id]
                del directory["DuckDFSINodeDirectorySection"]["parent"][file_id]
                directory["DuckDFSINodeDirectorySection"]["children"][parent_id].remove(file_id)
                with open("duckdfsimage.json", "w") as outfile:
                    outfile.write(json.dumps(directory))
                    updateFireBase(directory)
                click.echo("File Deleted")
            else:
                click.echo('The file does not exist!')
            return

    file_id = None
    for i, x in enumerate(parsed_path):
        current_id = None
        for z in directory["DuckDFSINodeSection"]:
            if directory["DuckDFSINodeSection"][str(z)]["name"] == x:
                current_id = directory["DuckDFSINodeSection"][str(z)]["id"] 
        if current_id is not None and current_id in directory["DuckDFSINodeDirectorySection"]["children"].keys() and i!=len(parsed_path)-1:
            children_names = [directory["DuckDFSINodeSection"][y]["name"].split("___")[-1] for y in directory["DuckDFSINodeDirectorySection"]["children"][current_id]] 
            children_id = [directory["DuckDFSINodeSection"][y]["id"].split("___")[-1] for y in directory["DuckDFSINodeDirectorySection"]["children"][current_id]]
            # print(children_names)
            if parsed_path[i+1] not in children_names:
                click.echo(f'There is no directory or file called {parsed_path[i+1]}')
            else:
                file_id = children_id[children_names.index(parsed_path[i+1])]
        elif i==len(parsed_path)-1:
            del directory["DuckDFSINodeSection"][file_id]
            parent_id = directory["DuckDFSINodeDirectorySection"]["parent"][file_id]
            del directory["DuckDFSINodeDirectorySection"]["parent"][file_id]
            directory["DuckDFSINodeDirectorySection"]["children"][parent_id].remove(file_id)
            with open("duckdfsimage.json", "w") as outfile:
                outfile.write(json.dumps(directory))
                updateFireBase(directory)
                click.echo("File Deleted")
        else:
            click.echo(f'There is no directory or file called {x}')
            return


@cli.command()
@click.option('--input_file_path','-i',help='Input file path')
@click.option('--output_file_path','-o',help='Output file path')
@click.option('--num_partitions','-p',help='Number of partitions')
def put(input_file_path, output_file_path, num_partitions):
    # TODO:
    # Cannot upload the file with same name in the folder

    # Check if input file exists, read input file content
    data = None
    size = None
    if num_partitions is None:
        num_partitions = directory["DuckDFSConfiguration"]["partitions"]
    try:
        num_partitions = int(num_partitions)
        split_filepath = os.path.splitext(input_file_path)
        file_extension = split_filepath[1]
        data = []
        if file_extension == '.txt':
            ifile = open(input_file_path, 'r')
            
            size = os.path.getsize(input_file_path)
            blocks = (size//num_partitions)+(size%num_partitions)
            seek = 0
            # print(data, size, num_partitions, blocks)
            while seek < size:
                ifile.seek(seek)
                data.append(ifile.read(blocks))
                seek+=blocks
            # print(data, size, num_partitions, blocks)
            ifile.close()
        elif file_extension == '.csv':
            file_data = [line for line in open(input_file_path)]
            # print(file_data[0])
            num_lines = len(file_data) - 1
            # print(num_lines)
            blocks = (num_lines//num_partitions)+(num_lines%num_partitions)
            seek = 1
            while seek < num_lines:
                temp = [file_data[0]]
                temp += file_data[seek:seek+blocks]
                # print(len(temp))
                data.append(''.join(temp))
                seek+=blocks
            # return
        else:
            click.echo(f'File extension is invalid, please put files with .txt and .csv')
    except:
        click.echo(f'{input_file_path} does not exist')
        return

    # Check if output path is valid
    parsed_path = output_file_path.split('/')
    if '' in parsed_path:
        parsed_path.remove('')
    for i, x in enumerate(parsed_path):
        current_id = None
        file_type = None
        for z in directory["DuckDFSINodeSection"]:
            if directory["DuckDFSINodeSection"][str(z)]["name"] == x:
                current_id = directory["DuckDFSINodeSection"][str(z)]["id"] 
                file_type = directory["DuckDFSINodeSection"][str(z)]["type"] 
        if current_id is not None and current_id in directory["DuckDFSINodeDirectorySection"]["children"].keys() and i!=len(parsed_path)-1:
            children_names = [directory["DuckDFSINodeSection"][y]["name"] for y in directory["DuckDFSINodeDirectorySection"]["children"][current_id]] 
            if parsed_path[i+1] not in children_names:
                click.echo(f'There is no directory or file called {x}')
                return
        elif i==len(parsed_path)-1:
            createFile(input_file_path.split('/')[-1], data, current_id, size)
            return
        else:
            click.echo(f'There is no directory or file called {x}')
            return
    pass

@cli.command()
@click.option('--partitions','-p',help='Default number of partitions')
@click.option('--clusters','-b',help='Default number of blocks')
@click.option('--describe','-d',is_flag=False, help='Default number of blocks')
def config(partitions, clusters, describe):
    if describe is None:
        partitions = int(partitions)
        clusters = int(clusters)
        if partitions in range(1, 10):
            directory["DuckDFSConfiguration"]["partitions"] = partitions
        else:
            click.echo("Invalid number of partitions (max 10)")
        
        if clusters in range(1, 10):
            files = next(os.walk('files'))
            block_count = max([int(x.split('_')[1]) for x in files[1]])
            if block_count < clusters:
                for i in range(block_count+1, clusters+1):
                    os.mkdir(f'files/block_{i:03}')
            directory["DuckDFSConfiguration"]["blocks"] = clusters
        else:
            click.echo("Invalid number of blocks (max 10)")

        with open("duckdfsimage.json", "w") as outfile:
            outfile.write(json.dumps(directory))
            updateFireBase(directory)
    else:
        click.echo(f'DUCKDFS Configuration:\n{"-"*21}\n{"Number of Partitions:":25}{directory["DuckDFSConfiguration"]["partitions"]:25}\n{"Number of Blocks:":25}{directory["DuckDFSConfiguration"]["blocks"]:25}\n')

def getPartitionLocations(file_id):
    blocks = [directory["DuckDFSINodeSection"][file_id]['blocks'][x] for x in directory["DuckDFSINodeSection"][file_id]['blocks']]
    click.echo(f'{"Partition":20}{"Cluster Location":20}')
    click.echo(f'{"-"*9:20}{"-"*16:20}')
    for block in blocks:
        partition = int(block['name'].split('___')[1])
        location = int(block['block_id'].split('_')[1])
        click.echo(f'{str(partition+1).ljust(20)}{str(location).ljust(20)}')
    return blocks

@cli.command()
@click.argument('filepath')
def getpartitionlocations(filepath):
    parsed_path = filepath.split('/')
    if '' in parsed_path:
        parsed_path.remove('')
    if len(parsed_path) == 1:
        if curr_directory["id"] in directory["DuckDFSINodeDirectorySection"]["children"].keys():
            children_names = [directory["DuckDFSINodeSection"][y]["name"].split("___")[-1] for y in directory["DuckDFSINodeDirectorySection"]["children"][curr_directory["id"]]]
            children_id = [directory["DuckDFSINodeSection"][y]["id"].split("___")[-1] for y in directory["DuckDFSINodeDirectorySection"]["children"][curr_directory["id"]]]
            if parsed_path[0] in children_names:
                file_id = children_id[children_names.index(parsed_path[0])]
                getPartitionLocations(file_id)
            else:
                click.echo(f'There is no directory or file called {parsed_path[0]}')
            return
    file_id = None
    for i, x in enumerate(parsed_path):
        current_id = None
        file_type = None
        for z in directory["DuckDFSINodeSection"]:
            if directory["DuckDFSINodeSection"][str(z)]["name"] == x:
                current_id = directory["DuckDFSINodeSection"][str(z)]["id"] 
                file_type = directory["DuckDFSINodeSection"][str(z)]["type"] 
        if current_id is not None and current_id in directory["DuckDFSINodeDirectorySection"]["children"].keys() and i!=len(parsed_path)-1:
            children_names = [directory["DuckDFSINodeSection"][y]["name"].split('___')[-1] for y in directory["DuckDFSINodeDirectorySection"]["children"][current_id]] 
            children_id = [directory["DuckDFSINodeSection"][y]["id"].split("___")[-1] for y in directory["DuckDFSINodeDirectorySection"]["children"][current_id]]
            if parsed_path[i+1] not in children_names:
                click.echo(f'There is no directory or file called {x}')
                
                return
            else:
                file_id = children_id[children_names.index(parsed_path[i+1])]
        elif i==len(parsed_path)-1:
            getPartitionLocations(file_id)
            return
        else:
            click.echo(f'--There is no directory or file called {x}')
            return
    click.echo(parsed_path)

def performMap(df, operator, columns):
    # print(df.head())
    gb = df.groupby(columns).agg(operator)
    # print(gb)
    return gb

def performWhere(df, whereclause):
    column = whereclause['column']
    where = whereclause['where']
    if 'lt' in where.keys():
        df = df[df[column] < where["lt"]]
    elif 'gt' in where.keys():
        df = df[df[column] > where["gt"]]
    elif 'lte' in where.keys():
        df = df[df[column] <= where["lte"]]
    elif 'gte' in where.keys():
        df = df[df[column] <= where["gte"]]
    elif 'et' in where.keys():
        df = df[df[column] == where["et"]]
    elif 'net' in where.keys():
        df = df[df[column] != where["net"]]
    return df


@cli.command()
@click.option('--path','-i',help='Absolute path of dataset')
@click.option('--query','-q',help='Query File path (local)')
@click.option('--output','-o',help='Output file path',default='output.csv')
@click.option('--describe','-d',help='1: Describe the dataset',default=0)
@click.option('--example','-e',help='Describe how to use map reduce function',default=0)
@click.option('--show','-s',help='Show results',default=1)
def mapreduce(path, query, output, describe, example, show):    
    if int(example) == 1:
        click.echo("""
How to perform Map Reduce:
--------------------------

Create a query JSON file (e.g. query.json) with the query in the following format:

{
    "project": [COLUMN1, COLUMN2, .....],
    "on": [
        {
            "column": COLUMNA,
            "where": {
                "WHERE-OPERATOR": VALUE1,
                "WHERE-OPERATOR": VALUE2,
                ......
            }
        },
        .....
    ],
    "operator": AGGREGATE-OPERATOR,
    "groupby": [COLUMN1, COLUMN2, .....]
    "limit": VALUE,
    "order": {
        "column": COLUMN,
        "ascending": [true|false]
    }
}

WHERE-OPERATORS:
lt : less than (<)
gt : greater than (>)
lte : less than or equal to (<=)
gte : greater than or equal to (>=)
et : equal to (==)
net : not equal to (!=)

AGGREGATE-OPERATOR:
count, min, max, sum, mean

Example:
--------

SQL: 
SELECT County, Count(Severity) as Severity
FROM [DATASET]
WHERE 
Severity <= 4
AND Severity >= 2
AND Humidity(%) < 80
GROUP BY County;

Equivalent Query:
{
    "on": [
        {
            "column":"Severity",
            "where":{"lte":4,"gte":2}
        },
        {
            "column":"Humidity(%)",
            "where":{"lt":80}
        }
    ],
    "project": ["Severity"],
    "operator":"count",
    "groupby":["County"],
}""")
        return
    else:
        try:
            
            parsed_path = path.split('/')
            if '' in parsed_path:
                parsed_path.remove('')
            file_id = None
            children_names = [directory["DuckDFSINodeSection"][y]["name"].split('___')[-1] for y in directory["DuckDFSINodeDirectorySection"]["children"]["0"]] 
            children_id = [directory["DuckDFSINodeSection"][y]["id"].split("___")[-1] for y in directory["DuckDFSINodeDirectorySection"]["children"]["0"]]
            for i, x in enumerate(parsed_path):
                current_id = None
                mapreduce_params = None
                for z in directory["DuckDFSINodeSection"]:
                    if directory["DuckDFSINodeSection"][str(z)]["name"] == x:
                        current_id = directory["DuckDFSINodeSection"][str(z)]["id"] 
                if current_id is not None and current_id in directory["DuckDFSINodeDirectorySection"]["children"].keys() and i!=len(parsed_path)-1:
                    children_names = [directory["DuckDFSINodeSection"][y]["name"].split('___')[-1] for y in directory["DuckDFSINodeDirectorySection"]["children"][current_id]]  
                    children_id = [directory["DuckDFSINodeSection"][y]["id"].split("___")[-1] for y in directory["DuckDFSINodeDirectorySection"]["children"][current_id]]
                    if parsed_path[i+1] not in children_names:
                        click.echo(f'There is no directory or file called {path}')
                        return
                    else:
                        file_id = children_id[children_names.index(parsed_path[i+1])]
                elif i==len(parsed_path)-1:
                    if len(parsed_path) == 1 and parsed_path[0] in children_names:
                        file_id = children_id[children_names.index(parsed_path[0])]
                    blocks = directory["DuckDFSINodeSection"][file_id]["blocks"]
                    
                    resframes = []

                    
                    for block in blocks:
                        file_name = blocks[block]["name"]
                        block_id = blocks[block]["block_id"]
                        split_filepath = os.path.splitext(file_name)
                        file_extension = split_filepath[1]
                        if file_extension != ".csv":
                            click.echo("Please use .csv files for map reduce.")
                            return
                            
                        df = pd.read_csv('files/'+block_id+'/'+file_name)

                        if int(describe) == 1:
                            print("The dataset has the following columns:")
                            print(list(df.columns))
                            return

                        
                        try:
                            f = open(query)
                            mapreduce_params = json.loads(f.read())
                            f.close()
                        except:
                            click.echo("Invalid query in file or the query file does not exist.")
                            return

                        mapreduce_keys = mapreduce_params.keys()
                        
                        if 'on' in mapreduce_keys:
                            temp = []
                            for cols in mapreduce_params["on"]:
                                temp.append(performWhere(df, cols))
                            df = pd.concat(temp)
                        
                            
                        if 'groupby' in mapreduce_keys:  
                            mapgroup = mapreduce_params["groupby"]
                            df = df.groupby(mapgroup)                          
                            # df = performMap(df, mapop,mapgroup)
                        
                        if 'operator' in mapreduce_keys:  
                            mapop = mapreduce_params["operator"]
                            df = df.agg(mapop) 
                            
                        if 'project' in mapreduce_keys:
                            df = df[mapreduce_params["project"]]

                        if "order" in mapreduce_keys:
                            df = df.sort_values(by=mapreduce_params["order"]["column"], ascending=True if mapreduce_params["order"]["ascending"] == 'true' else False)

                        df = df.drop_duplicates()

                        resframes.append(df)
                    
                    result = pd.concat(resframes)
                   
                    
                    hasindex = False
                    result_gb = result
                    if 'groupby' in mapreduce_keys:
                        hasindex = True
                        mapgroup = mapreduce_params["groupby"]
                        result_gb = result.groupby(mapgroup)

                    for i, x in enumerate(resframes):
                        click.echo("\nMap Reduce Partition " + str(i+1) + " Results:\n")
                        print(x[:5].to_markdown(index=hasindex))
                    click.echo("\nPS: Only top 5 results of each partition are shown\n")

                    
                    if 'operator' in mapreduce_keys:
                        mapop = mapreduce_params["operator"]
                        if mapop == 'count':
                            result_gb = result_gb.agg('sum')
                        else:
                            result_gb = result_gb.agg(mapop)
                    
                    if "order" in mapreduce_keys:
                        result_gb = result_gb.sort_values(by=mapreduce_params["order"]["column"], ascending=True if mapreduce_params["order"]["ascending"] == 'true' else False)

                    if "limit" in mapreduce_keys:
                        result_gb = result_gb[:mapreduce_params["limit"]]

                    result_gb = result_gb.drop_duplicates()
                    result_gb.to_csv(output,sep=',',encoding='utf-8', index=hasindex)
                    if show == 1:
                        print(result_gb.to_markdown(index=hasindex))
                    click.echo("\nCumulative result of map reduce is saved in "+output)
                else:
                    click.echo(f'There is no directory or file called {x}')
                    return
        except Exception as e:
            click.echo('The dataset does not exist' + e)
        return