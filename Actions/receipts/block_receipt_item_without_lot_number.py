"""
This rule will block receiving an item if the inventory does not have a lot number.
And the part is lot tracked.
"""

input = {
    "enabled": true,
    "title": "Receiving lot-tracked parts requires that a lot number is populated",
    "target": "RECEIPTITEM",
    "eventType": "CREATE",
    "ruleType": "VALIDATION",
    "errorState": "ALLOW",
    "context": "{ receiptItem(id: $id) { id partInventory {serialNumber lotNumber part{id trackingType}} } }",
    "code": "if not context.get('receiptItem', {}).get('partInventory', {}).get('lotNumber') and context.get('receiptItem', {}).get('partInventory', {}).get('part', {}).get('trackingType') == 'LOT': raise ValidationError()",
}
