#!/bin/bash

DIR=$(dirname "$(readlink -f "$0")")
while getopts ":s" arg; do
  case $arg in
    s)
      find $DIR/../files/DIY/Iosevka -type f -iname '*.ttf' | xargs -I{} $DIR/stat.py {}
      ;;
  esac
done

cat $DIR/test_pattern
