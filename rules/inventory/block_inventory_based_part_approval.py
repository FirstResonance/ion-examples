"""This rule will block inventory creation if the part is not approved.

The organization must create a custom attribute called "Approved" with a boolean value to use this rule.
"""

input = {
  "enabled": true,
  "title": "Part must be approved before creating inventory",
  "target": "PARTINVENTORY",
  "eventType": "CREATE",
  "ruleType": "VALIDATION",
  "errorState": "ALLOW",
  "context": "{ partInventory(id: $id) { part { id attributes { key value } } } }",
  "code": "if (context.get('partInventory', {}).get('part', {}).get('attributes', {}).get('key') == 'Approved' and context.get('partInventory', {}).get('part', {}).get('attributes', {}).get('value') != True): raise ValidationError()"
}
