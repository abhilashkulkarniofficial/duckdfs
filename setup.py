from setuptools import setup, find_packages
import os
import json
import socket
import requests

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()
if not os.path.exists('files'):
    os.makedirs('files')
    if not os.path.exists('files/block_001'):
        os.makedirs('files/block_001')
    if not os.path.exists('files/block_002'):
        os.makedirs('files/block_002')
    if not os.path.exists('files/block_003'):
        os.makedirs('files/block_003')

duckdfsimage = {
	"DuckDFSConfiguration": {
		"partitions": 3,
		"blocks": 3
	},
	"DuckDFSGlobal": {
		"max_id": "0"
	},
	"DuckDFSCurrentINode": {
		"path": "/",
		"id": "0"
	},
	"DuckDFSINodeSection": {
		"0": {
			"name": "",
			"id": "0",
			"permission": "744",
			"type": "DIR"
		}
	},
	"DuckDFSINodeDirectorySection": {
		"children": {
            '-1':'-1'
		},
		"parent": {
            '-1':'-1'
		}
	}
}

if not os.path.isfile('duckdfsimage.json'):
    # Serializing json
    json_object = json.dumps(duckdfsimage, indent=4)
    
    # Writing to sample.json
    with open("duckdfsimage.json", "w") as outfile:
        outfile.write(json_object)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    s.getsockname()[0]
    url = 'https://dsci551x86-default-rtdb.firebaseio.com/duckdfsimage-'+str('-'.join(s.getsockname()[0].split('.')))+'.json'
    requests.put(url, data = json.dumps(duckdfsimage))

setup(
    name = 'test-duckdfs',
    version = '0.0.2',
    author = 'Abhilash Kulkarni',
    author_email = 'ak41739@usc.edu',
    license = 'Apache License 2.0',
    description = 'DuckDFS (Emulated Distributed File System)',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = 'https://github.com/abhilashkulkarniofficial/duckdfs',
    py_modules = ['my_tool', 'app'],
    packages = find_packages(),
    install_requires = [requirements],
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    entry_points = '''
        [console_scripts]
        duckdfs=my_tool:cli
    '''
)



