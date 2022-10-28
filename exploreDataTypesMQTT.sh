#!/bin/bash
#-----------Auther: Hassan Al Achek-----------#

function usage {
    echo "[?] Help Menu"
    echo -e "-h: help \n-d: script description \n-p: to specify the data directory"
    echo ""
    echo "Usage: $0 -p </path/to/data/directory>"
    echo "Example: $0 -p ../databat_data/"
}

function scriptDescription {
    echo "[?] Description:
        This script take a path to a directory that contains all 
        *_metrics.csv files and explore data types available on each file"
}

function getAllMQTTFiles {
    echo "[+] Getting all MQTT collected files"
    echo "[+] Reading from the following directory: $1"
    files=$(ls $dataDirectory | grep "[[:digit:]]_metrics\.csv$")
}

function displayResult {
    echo "[+] Start reading all files from $dataDirectory"
    echo "[+] Data types availables in each file"
    
    for file in $files
    do
        echo "$dataDirectory$file" 
        datatypes=($(cat "$dataDirectory$file" | cut -d, -f5 | sort | uniq | sed '$d'))
        {
            printf "File Name\tData Types\n";
            printf "%s\t%s\n" $file ${datatypes[0]};
            deleteFirstElem=${datatypes[0]}
            for elem in ${datatypes[@]/$deleteFirstElem}; do
                printf "%s\t%s\n" "" $elem;
            done
        } | ./prettytable.sh 2
    done
}


while getopts "hdp:" opt
do
    case "${opt}" in
        h)
            usage
            ;;
        d)
            scriptDescription
            ;;
        p)

            dataDirectory=${OPTARG}
            # Global Variables
            set files
            getAllMQTTFiles $dataDirectory
            displayResult
            ;;
    esac
done

