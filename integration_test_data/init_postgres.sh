#!/bin/sh

# This is just an example of how to do it, hardcoded password etc.

psql postgresql://postgres:BJQmqgHbHjFSBw@localhost:5432/ -c "CREATE USER django WITH PASSWORD 'shae6woifaeTah7Eipax';"
psql postgresql://postgres:BJQmqgHbHjFSBw@localhost:5432/ -c "CREATE DATABASE demo_local_test WITH OWNER django ENCODING 'utf-8';"
