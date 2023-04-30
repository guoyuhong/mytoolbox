#!/bin/sh

YAPF_VERSION=`yapf --version`
YAPF_WANT_VERSION="0.32.0"
if [[ $YAPF_VERSION != "yapf ${YAPF_WANT_VERSION}" ]]; then
  echo "yapf version is $YAPF_VERSION, reinstall."
  pip install yapf==${YAPF_WANT_VERSION} -i https://mirrors.aliyun.com/pypi/simple/
fi

# Python lint test.
TEST_MODE="false"

script_dir=$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)


function usage() {
  echo "Usage: python_lint.sh [<args>]"
  echo
  echo "Options:"
  echo "  -t|--test               test mode"
  echo "  -h|--help               help messag."
  echo
}

# Parse options
while [[ $# > 0 ]]; do
  key="$1"
  case $key in
    -h|--help)
      usage
      exit 0
      ;;
    -t|--test)
      TEST_MODE="true"
      ;;
    *)
      echo "ERROR: unknown option \"$key\""
      echo
      usage
      exit -1
      ;;
  esac
  shift
done

FLAGS=(
  '-i'
  '--style' "$script_dir/.yapf"
  '--recursive'
  '--parallel'
)

if [[ $TEST == "true" ]]; then
  FLAGS[0]='--diff'
fi

EXCLUDES=(
  '--exclude' '../build'
  # Other files are with the same format as above.
)

APPLY_FILES=(
  '../gtbox/onnxruntime'
  '.'
)

set -e
pushd $script_dir
yapf "${FLAGS[@]}" "${EXCLUDES[@]}" "${APPLY_FILES[@]}"
CODE=$?
if [[ $CODE != 0 ]]; then
  echo "Lint test failed, please run this script local before pushing."
  popd
  exit $CODE
fi

popd
