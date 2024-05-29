"""Block a user from creating inventory through run creation unless they have the CreatePartInventory permission."""

input = {
    "create_rule": {
        "enabled": true,
        "title": "Block inventory creation from run creation unless user has createPartInventory permission",
        "target": "RUN",
        "eventType": "CREATE",
        "ruleType": "VALIDATION",
        "errorState": "ALLOW",
        "context": "{run(id: $id) {partInventory {createdById}} me {id permissionGroups{name}}}",
        "code": "if context.get('me').get('id') == context.get('run', {}).get('partInventory', {}).get('createdById') and 'CreatePartInventory' not in {perm['name'] for perm in context.get('me', {}).get('permissionGroups', {})}: raise ValidationError()",
    }
}
