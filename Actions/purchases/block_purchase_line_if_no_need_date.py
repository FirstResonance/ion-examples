"""This rule will block adding a purchase line item if there is not need date."""

input = {
    "enabled": true,
    "title": "Purchase line items must have a need date",
    "target": "PURCHASEORDERLINE",
    "eventType": "UPDATE",
    "ruleType": "VALIDATION",
    "errorState": "ALLOW",
    "context": "{ purchaseOrderLine(id: $id) { id needDate } }",
    "code": "if context.get('changes', {}).get('purchaseOrderLines', {}).get('status', {}).get('new') == 'ordered' and context.get('purchaseOrderLine', {}).get('needDate') is None: raise ValidationError()",
}
