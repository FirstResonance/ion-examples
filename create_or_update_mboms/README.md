# Create or Update mBOMs
Use this script to upload an mBOM in your environment.


## Setup
1. Add a `config.py` to this directory and store your ION API key information there. Check out `config_example.py` for the format
2. Run `python3 create_or_update_mboms/bulk_create_or_update_mboms.py` if you want to use Depth notation or `python3 create_or_update_mboms/bulk_create_or_update_mboms.py --level` if you want to use Level notation.
3. Use the `log.txt` file to monitor progress
4. Assuming no errors, the mBOM should be generated for your environment.

