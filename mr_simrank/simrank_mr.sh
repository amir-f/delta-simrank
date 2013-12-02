#!/usr/bin/env bash


usage(){
  echo "Usage: $0 graph_filename.graphml"
  exit 1
}


run_mr(){
  set -e
  TMP_DIR=/tmp/$1_simrank_$(date +"%Y%m%d%H%M")
  mkdir -p $TMP_DIR
  PRTN_FILE=$TMP_DIR/$1.txt
  GRPH_FILE=$TMP_DIR/$1.digraph
  python preprocess_graph_mr.py $1 $TMP_DIR
  python simrank_mr.py --graph-file $GRPH_FILE --decay-factor 0.8 --iters 10 $PRTN_FILE -r hadoop > $1.simrank
  rm -r $TMP_DIR
}

[[ $# -ne 1 ]] && usage

if [[ -f $1 ]]; then
  run_mr $1
else
  echo "Input file not found: $1"
  exit 1
fi
