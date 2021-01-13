#!/bin/bash

_warn() {
  echo -e "\033[0;33mWARNING: $*\033[0m" >&2
}

_error() {
  echo -e "\033[0;31mERROR: $*\033[0m" >&2
}

_die() {
  _error "$*"
  exit 1
}

_success() {
  echo -e "\033[0;32mDONE: $*\033[0m"
}

_notice() {
  echo -e "\033[0;34m$*\033[0m"
}
