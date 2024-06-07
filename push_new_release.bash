#!/usr/bin/env bash

registry_path=r.deso.tech/desowarehouse
api_path="$registry_path/api"
ui_path="$registry_path/ui"

if [ "$#" -lt 1 ]
then
  echo "Usage: $(basename "$0") <VERSION>" >&2
  exit 1
fi

IFS=. read -r major minor patch <<< "$1"

if [ -z "$major" ]
then
  echo "fatal: major version is missing" >&2
  exit 1
fi

if [ -z "$minor" ]
then
  echo "fatal: minor version is missing" >&2
  exit 1
fi

if [ -z "$patch" ]
then
  echo "fatal: patch version is missing" >&2
  exit 1
fi

echo "Building $api_path"
docker image build -t "$api_path:$major.$minor.$patch" -t "$api_path:$major.$minor" -t "$api_path:$major" -t "$api_path:latest" api

echo "Building $ui_path"
docker image build -t "$ui_path:$major.$minor.$patch" -t "$ui_path:$major.$minor" -t "$ui_path:$major" -t "$ui_path:latest" ui

echo "Pushing $api_path"
docker image push -a "$api_path"

echo "Pushing $ui_path"
docker image push -a "$ui_path"