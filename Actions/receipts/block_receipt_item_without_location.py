"""This rule will block receiving an item if the inventory does not have a location."""

input = {
    "enabled": true,
    "title": "Receipt line items must have a location",
    "target": "PARTINVENTORY",
    "eventType": "CREATE",
    "ruleType": "VALIDATION",
    "errorState": "ALLOW",
    "context": "{ receiptItem(id: $id) { id partInventory{locationId} } }",
    "code": "if context.get('receiptItem', {}).get('partInventory', {}).get('locationId') is None: raise ValidationError()",
}
