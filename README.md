Designed to clean and combine csv data files and produce a master file for subsequent ingestion

### To set up:
1. Copy repository, navigate within
2. Create a new venv
`python3 -m venv venv`
3. Activate your new virtual environment
`source /venv/bin/activate`
4. Install the requirements
`pip install -r requirements.txt`
5. Determine directory path to the 'data' folder
`
cd data
pwd
`
Record this value

### To run:
1. Open the python console from the main project directory (don't forge to swap back from the last step)
`python3`
2. Import the cleaning file
```python
import data_cleaner.py
```
3. Run the cleaning fcn, providing the path recorded in setup Step 5
```python
output_cleaned_csv(rootdir="/path/to/data/folder"
```
4. Output should provide the path to the newly created cleaned data file, as well as the individual successfully processed data folders


### Notes and early planning/setup are included in the notes folder, and code is documented with more of the "as built" commentary
