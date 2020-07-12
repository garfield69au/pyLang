python ..\..\pyduq\pyduqmain.py -i "failing-food-report-data-july-2019.csv" --infer -o . -v -p
python ..\..\pyduq\pyduqmain.py -i "failing-food-report-data-august-2019-for-publishing.csv" -m food_safety.json --extend -o . -v -p
python ..\..\pyduq\pyduqmain.py -i "failing-food-report-data-september-2019-for-publishing_correction.csv" -m food_safety.json --extend -o . -v -p
python ..\..\pyduq\pyduqmain.py -i "failing-food-report-data-october-2019-for-publishing.csv" -m food_safety.json --extend -o . -v -p
python ..\..\pyduq\pyduqmain.py -i "failing-food-report-data-november-2019.csv" -m food_safety.json --extend -o . -v -p
python ..\..\pyduq\pyduqmain.py -i "failing-food-report-data-december-2019.csv" -m food_safety.json --extend -o . -v -p


pause