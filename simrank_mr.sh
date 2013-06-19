#!/usr/bin/env bash


usage(){
  echo "Usage: $0 graph_filename.graphml"
  exit 1
}


run_mr(){
  set -e
  DATE=$(date +"%Y%m%d%H%M")
  TMP_FILENAME=$1_$DATE.txt
  TMP_FILE=/tmp/$TMP_FILENAME
  python prepare_graph_mr.py $1 $TMP_FILE
  hadoop fs -put $TMP_FILE 
  python simrank_mr.py --decay-factor 0.8 --iters 10 $TMP_FILE -r hadoop > $1.simrank
  hadoop fs -rm $TMP_FILE
  rm $TMP_FILE
}

[[ $# -ne 1 ]] && usage

if [[ -f $1 ]]; then
  run_mr $1
else
  echo "Input file not found: $1"
  exit 1
fi
