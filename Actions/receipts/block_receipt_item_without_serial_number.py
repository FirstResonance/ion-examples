"""
This rule will block receiving an item if the inventory does not have a serial number.
And the part is serial tracked.
"""

input = {
    "enabled": true,
    "title": "Receiving serial-tracked parts requires that a serial number is populated",
    "target": "RECEIPTITEM",
    "eventType": "CREATE",
    "ruleType": "VALIDATION",
    "errorState": "ALLOW",
    "context": "{ receiptItem(id: $id) { id partInventory {serialNumber lotNumber part{id trackingType}} } }",
    "code": "if not context.get('receiptItem', {}).get('partInventory', {}).get('serialNumber') and context.get('receiptItem', {}).get('partInventory', {}).get('part', {}).get('trackingType') == 'SERIAL': raise ValidationError()",
}
