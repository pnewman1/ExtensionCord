#!/bin/sh
python ../extension_cord/static/scripts/InputTestResultsInEC.py rest_result_01.json http://127.0.0.1:8000/api/result
python ../extension_cord/static/scripts/InputTestResultsInEC.py rest_result_02.json http://127.0.0.1:8000/api/result
