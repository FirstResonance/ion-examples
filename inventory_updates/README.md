# Overview
Update quantities for inventory in bulk

## Setup
1. Add a `config.py` to this directory and store your ION API key information there. Check out `config_example.py` for the format
2. Add csv information to `inventory_update.csv` with id and new quantity
2. Run `python3 inventory_updates/update_inventory_quantities.py`
4. Follow along with the `log.txt` file for progress
5. Assuming no errors, all inventory quantities will be updated with the new quantity

## Rounding query
To use this script to correct rounding errors, run this query first and use it to feed the csv.
```
SELECT
  pi.id as inventory_id,
  --pi.quantity,
  ROUND(CAST(pi.quantity AS numeric), 5) AS new_quantity
FROM
  parts_inventory pi
WHERE
  pi.quantity > ROUND(CAST(pi.quantity AS numeric), 5)
  or pi.quantity < ROUND(CAST(pi.quantity AS numeric), 5)
```