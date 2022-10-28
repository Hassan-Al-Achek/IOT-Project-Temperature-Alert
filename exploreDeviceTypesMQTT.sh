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
        *_metrics.csv files and explore device types available on each file"
}

function getAllMQTTFiles {
    echo "[+] Getting all MQTT collected files"
    echo "[+] Reading from the following directory: $1"
    files=$(ls $dataDirectory | grep "[[:digit:]]_metrics\.csv$")
}

function displayResult {
    echo "[+] Start reading all files from $dataDirectory"
    echo "[+] Devices types availables in each file"
    
    for file in $files
    do
        echo "$dataDirectory$file" 
        devicetypes=$(cat "$dataDirectory$file" | cut -d, -f3 | sort | uniq | sed 1d)
        {
            printf "File Name\tDevice Types\n";
            printf "%s\t%s\n" $file $devicetypes;
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

