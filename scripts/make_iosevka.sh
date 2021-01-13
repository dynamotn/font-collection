#!/bin/bash
set -Eeuo pipefail

DIR=$(dirname "$(readlink -f "$0")")
source $DIR/message.sh

_prequisite() {
  if ! command -v fontforge &> /dev/null; then
    _die "You must install python-fontforge to use this script"
  fi
}

_main() {
  _success "Test"
}

_prequisite
_main
