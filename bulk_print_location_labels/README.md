# Bulk print location labels
Use this script to bulk print location barcodes via a script from a csv file.


## Setup
1. Add a `config.py` to this directory and store your ION API key information there. Check out `config_example.py` for the format.
2. Add real csv info to `locations.csv` with column 1 being the id. 
3. Run `bulk_print_location_labels/bulk_print_location_labels.py`
4. Select the barcode template ID when prompted.
5. Choose a print method:
   - **Network** — enter the printer's IP address. The script sends ZPL directly over TCP port 9100.
   - **USB** — requires [Zebra Browser Print](https://www.zebra.com/us/en/support-downloads/printer-software/browser-print.html) to be installed and running on your machine. The script discovers available printers automatically; if more than one is found you will be prompted to pick one.
6. Follow along with `log.txt` for progress.
7. Assuming no errors, your printer will print labels for all locations in the CSV.
