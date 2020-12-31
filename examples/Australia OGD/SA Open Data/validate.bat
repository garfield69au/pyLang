echo off
cls
echo Retrieving file from source location...
wget -O "SA development application register.csv" https://data.sa.gov.au/data/dataset/205c5d90-0522-4bdd-8be4-7a0e1f2cb85c/resource/7158ab0d-438f-48cf-baa4-0653b153fe76/download/dar2020.csv 
echo. 
echo Running pyduq!
python ..\..\..\pyduq\pyduqmain.py -i "SA development application register.csv" --infer -o . -v -p
rem python ..\..\..\pyduq\pyduqmain.py -i "SA development application register.csv" -m "SA development application register.csv" -o . -v -p
pause


 