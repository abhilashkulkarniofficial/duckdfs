COLOR_NC='\e[0m' # No Color
COLOR_BLACK='\e[0;30m'
COLOR_GRAY='\e[1;30m'
COLOR_RED='\e[0;31m'
COLOR_LIGHT_RED='\e[1;31m'
COLOR_GREEN='\e[0;32m'
COLOR_LIGHT_GREEN='\e[1;32m'
COLOR_BROWN='\e[0;33m'
COLOR_YELLOW='\e[1;33m'
COLOR_BLUE='\e[0;34m'
COLOR_LIGHT_BLUE='\e[1;34m'
COLOR_PURPLE='\e[0;35m'
COLOR_LIGHT_PURPLE='\e[1;35m'
COLOR_CYAN='\e[0;36m'
COLOR_LIGHT_CYAN='\e[1;36m'
COLOR_LIGHT_GRAY='\e[0;37m'
COLOR_WHITE='\e[1;37m'
echo "${COLOR_GREEN}/**********************************/"
echo "${COLOR_GREEN}/* Activating Virtual Environment */"
echo "${COLOR_GREEN}/**********************************/${COLOR_NC}"
pip3 install virtualenv
virtualenv duckdfsenv
source "duckdfsenv/bin/activate"
echo "${COLOR_GREEN}/**********************************/"
echo "${COLOR_GREEN}/* Installing necessary libraries */"
echo "${COLOR_GREEN}/**********************************/${COLOR_NC}"
pip3 install requests
echo "${COLOR_GREEN}/**********************/"
echo "${COLOR_GREEN}/* Setting up Duckdfs */"
echo "${COLOR_GREEN}/**********************/${COLOR_NC}"
python3 setup.py develop
echo "${COLOR_GREEN}/********************/"
echo "${COLOR_GREEN}/* DuckDFS is setup */"
echo "${COLOR_GREEN}/********************/${COLOR_NC}"
echo ""
echo "${COLOR_YELLOW}Emulated Distributed File System"
echo ""
echo "${COLOR_RED}Commands:"
echo "Usage: ducdfs COMMAND [OPTIONS] [ARGS] ...."
echo "${COLOR_BLUE}$ duckdfs pwd - ${COLOR_NC}Print current working directory"
echo "${COLOR_BLUE}$ duckdfs ls - ${COLOR_NC}List all files and directory in current working directory"
echo "${COLOR_BLUE}$ duckdfs cd PATH - ${COLOR_NC}Move into the directory"
echo "${COLOR_BLUE}$ duckdfs mkdir PATH - ${COLOR_NC}Create a directory"
echo "${COLOR_BLUE}$ duckdfs rm FILEPATH - ${COLOR_NC}Remove file in PATH"
echo "${COLOR_BLUE}$ duckdfs cat FILEPATH - ${COLOR_NC}Output the content of the file"
echo "${COLOR_BLUE}$ duckdfs config [OPTIONS] - ${COLOR_NC}Configure or describe the default block and partition sizes"
echo "${COLOR_BLUE}$ duckdfs put -i FILEPATH -o FILEPATH [OPTIONS] - ${COLOR_NC}Upload the file to the Distributed File System"
echo "${COLOR_BLUE}$ duckdfs mapreduce -i FILEPATH -q FILEPATH -o FILEPATH [OPTIONS] - ${COLOR_NC}Perform mapreduce on the file using a query"
echo "${COLOR_BLUE}$ duckdfs getpartitionlocations FILEPATH - ${COLOR_NC}Get locations of partitions of the file"

