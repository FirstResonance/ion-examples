# Bulk Purchase Order Status Update
Use this script to update the status of the purchase orders in `update_purchase_orders.csv`. 


## Setup
1. Add a `config.py` to this directory and store your ION API key information there. Check out `config_example.py` for the format
2. replace `update_purchase_orders.csv` with a similarily formatted csv file with the IDs of the POs whose status you want to update. 
3. Run `python bulk_update_purchase_orders/bulk_update_purchase_order_status.py --status RECEIVED`
    - Other Valid Status: DRAFT", REQUESTED, APPROVED, ORDERED, CANCELED, RECEIVED
4. Use the `log.txt` file to monitor progress
5. Assuming no errors, all purchases order statuses will be updated to the status set in the command.  
