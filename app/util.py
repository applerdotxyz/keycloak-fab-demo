import functools
from flask import jsonify,g
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from functools import wraps
def has_role(roles):
    """Decorator to check if the user has at least one required role."""
    if not isinstance(roles, list):
        roles = [roles]  # Convert single role to list

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_roles = g.user_data.get("realm_access", {}).get("roles", [])
            if not any(role in user_roles for role in roles):
                return jsonify({"message": "Access denied! Required roles: {}".format(roles)}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator


def has_permission(resource, permissions):
    """Decorator to check if the user has at least one required permission for a resource."""
    if not isinstance(permissions, list):
        permissions = [permissions]  # Convert single permission to list

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            resource_roles = g.user_data.get("resource_access", {}).get(resource, {}).get("roles", [])
            if not any(permission in resource_roles for permission in permissions):
                return jsonify({"message": "Permission denied! Required permissions: {} for '{}'.".format(permissions, resource)}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator
