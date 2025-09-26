#! /usr/bin/env bash

set -e
set -x

cd backend
hatch run dev:server & npm --prefix ../frontend run dev
