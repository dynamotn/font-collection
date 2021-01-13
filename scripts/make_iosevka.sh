#!/bin/bash
set -Eeuo pipefail

DIR=$(dirname "$(readlink -f "$0")")
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT
source $DIR/message.sh

FONT_FAMILY_NAME="Iosevka Dynamo"
FIRACODE_VERSION="3.1"
IOSEVKA_VERSION="latest"
IOSEVKA_VARIANT="fixed-ss05" # Use fixed version of Fira Mono style variant

_check_prequisite_command() {
  if ! command -v "$1" &> /dev/null; then
    _die "You must install ${2:-$1} to use this script"
  fi
}

_prequisite() {
  _check_prequisite_command "curl"
  _check_prequisite_command "unzip"
  _check_prequisite_command "python3"
  _check_prequisite_command "fontforge" "python-fontforge"

  OUTPUT_DIR=$DIR/../files/DIY/Iosevka
  mkdir -p $OUTPUT_DIR $TEMP_DIR/iosevka
}

_download_iosevka() {
  if [ "$IOSEVKA_VERSION" == "latest" ]; then
    IOSEVKA_VERSION=$(curl -sSL https://api.github.com/repos/be5invis/Iosevka/releases/latest | grep -Po "tag_name\": \"(\K.*)(?=\",)")
  fi
  _notice "Downloading Iosevka font version: $IOSEVKA_VERSION"
  curl -SLC - https://github.com/be5invis/Iosevka/releases/download/$IOSEVKA_VERSION/ttf-iosevka-${IOSEVKA_VARIANT}-${IOSEVKA_VERSION:1}.zip -o $TEMP_DIR/original-${IOSEVKA_VARIANT}.zip
  unzip -qqo $TEMP_DIR/original-${IOSEVKA_VARIANT}.zip -d $TEMP_DIR/iosevka
  _success "Downloaded Iosevka"
}

_download_firacode() {
  _notice "Downloading FiraCode font version: $FIRACODE_VERSION"
  fira_style_names=("Regular" "Bold")
  for style in ${fira_style_names[@]}; do
    curl -SLC - https://raw.githubusercontent.com/tonsky/FiraCode/$FIRACODE_VERSION/distr/otf/FiraCode-$style.otf -o $TEMP_DIR/FiraCode-$style.otf
  done
  _success "Downloaded FiraCode"
}

_main() {
  _download_iosevka
  _download_firacode
  _success "Test"
}

_prequisite
_main
