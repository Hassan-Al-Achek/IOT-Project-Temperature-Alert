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
        *_metrics.csv files and extract temperatures available on each file"
}

function getAllMQTTFiles {
    echo "[+] Getting all MQTT collected files"
    echo "[+] Reading from the following directory: $1"
    files=$(ls $dataDirectory | grep "[[:digit:]]_metrics\.csv$")
}

function extractTemp {
    echo "[+] Start temperature extraction"
    mkdir result 2>/dev/null
    totalNumOfFiles=$(echo $files | tr " " "\n" | wc -l)
    echo "[+] Number of files to process: $totalNumOfFiles" 
    
    for file in $files
    do
        resultFile="result/temp_"$file
        head -n1 $dataDirectory$file > $resultFile
        temperatureData=$(grep "TEMP" "$dataDirectory$file" >> $resultFile)
        echo "result/temp_"$file
    done | pv -l -s "$totalNumOfFiles" > /dev/null
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
            if [[ -d $dataDirectory ]]; then
                if [[ "$dataDirectory" == */ ]]; then
                    # Global Variables
                    set files
                    getAllMQTTFiles $dataDirectory
                    extractTemp
                else
                    dataDirectory="$dataDirectory/"
                    # Global Variables
                    set files
                    getAllMQTTFiles $dataDirectory
                    extractTemp
                fi
            else
                echo "[!] Please enter a valid directory path"
            fi
            ;;
    esac
done
if [ $OPTIND -eq 1 ]; then
    usage
fi

