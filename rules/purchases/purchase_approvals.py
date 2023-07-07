"""This rule will blocks purchase workflow if the appropriate approver isn't added.
"to enable, you must add roles e.g. "manager" and assign users to those roles through the organization settings.

"""

input = {
  "enabled": true,
  "title": "Add a Manager for purchases over $10,000",
  "target": "PURCHASEORDERLINE",
  "eventType": "UPDATE",
  "ruleType": "VALIDATION",
  "errorState": "ALLOW",
  "context": "{purchaseOrderLine(id: $id) { id description purchaseOrder { estimatedTotalCost approvalRequests { reviewer { name roles { name } } } approvals { reviewer { name roles { name } } } } } }",
  "code": "if (context.get('changes', {}).get('purchaseOrderLines', {}).get('status', {}).get('new') == 'ordered' and context.get('purchaseOrderLine', {}).get('purchaseOrder', {}).get('estimatedTotalCost', 0) > 10000 and not any(role.get('name') == 'Manager' for approval in context.get('purchaseOrderLine', {}).get('purchaseOrder', {}).get('approvals', []) for role in approval.get('reviewer', {}).get('roles', []))): raise ValidationError()"
}
