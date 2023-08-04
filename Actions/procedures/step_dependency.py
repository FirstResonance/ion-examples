"""This rule will blocks a procedure from moving to "in review" if all steps don't have a dependency.

"""

input =  {
    "enabled": true,
    "title": "Check if Step has dependencies",
    "target": "PROCEDURE",
    "eventType": "UPDATE",
    "ruleType": "VALIDATION",
    "errorState": "ALLOW",
    "context": "{ procedure(id: $id) { id steps{location{name} upstreamStepIds downstreamStepIds } } }",
    "code": "if (context.get('changes', {}).get('procedures', {}).get('status', {}).get('new') == 'in_review' and any([step for step in context.get('procedure', {}).get('steps', []) if not (step.get('upstreamStepIds') or step.get('downstreamStepIds'))])): raise ValidationError()"
}