# Bulk print location labels
Use this script to bulk print location barcodes via a script from a csv file.


## Setup
1. Add a `config.py` to this directory and store your ION API key information there. Check out `config_example.py` for the format.
2. Add real csv info to `locations.csv` with column 1 being the id. 
3. Run `bulk_print_location_labels/bulk_print_location_labels.py`
4. Populate the requested information of barcode template ID and printer IP.
5. Follow along with the `log.txt` file for progress
6. Assuming no errors, your printer should print labels for all locations in csv.
