"""
This rule will block receiving an item if the inventory does not have a serial number.
And the part is serial tracked.
"""

mutation {
  createRule(input: {
    title: "Receiving serial-tracked parts requires that a serial number is populated",
    target: RECEIPTITEM,
    ruleType: VALIDATION,
    eventType: CREATE,
    enabled: true,
    context: "{\n  receiptItem(id: $id) {\n    id\n    partInventory {\n      serialNumber\n      lotNumber\n      part {\n        id\n        trackingType\n      }\n    }\n  }\n}",
    code: "receipt_item = context.get('receiptItem') or {}\npart_inventory = receipt_item.get('partInventory') or {}\npart = part_inventory.get('part') or {}\n\ntracking_type = part.get('trackingType')\n\ntracking_type = (tracking_type or '').strip()\n\nif tracking_type == 'SERIAL':\n    if not part_inventory.get('serialNumber'):\n        raise ValidationError()",
    errorState: BLOCK
  }) {
    rule {
      id
    }
  }
}
