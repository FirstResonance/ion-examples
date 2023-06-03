# Procedure export
Use this script to delete all purchases in your environment.


## Setup
1. Add a `config.py` to this directory and store your ION API key information there. Check out `config_example.py` for the format
2. Use `PURCHASES_TO_SKIP` to skip purchases that you don't want to delete.
3. Run `python3 delete_purchases/delete_purchases.py`
4. Use the `log.txt` file to monitor progress
5. Assuming no errors, all purchases should be deleted from your environment.

