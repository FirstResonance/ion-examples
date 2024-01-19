"""This rule will block changing the issues status to anything besides pending
unless the disposition, cause condition, expected condition, and all custom attributes are filled out

"""

input = {
  "create_rule": {
    "enabled": true,
    "title": "Cannot change issue status without disposition, cause condition, expected condition, and all custom attributes filled out.",
    "target": "ISSUE",
    "eventType": "UPDATE",
    "ruleType": "VALIDATION",
    "errorState": "ALLOW",
    "context": "{issue(id: $id){id status disposition expectedCondition causeCondition attributes{key value}}}",
    "code": "if context.get('issue').get('status') != 'PENDING' and (not context.get('issue').get('disposition') or not context.get('issue').get('expectedCondition') or not context.get('issue').get('causeCondition') or not all('value' in a and a['value'] for a in context.get('issue').get('attributes'))): raise ValidationError()"
  }
}
