from functools import wraps
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from flask import jsonify

def admin_required():
    """
    A custom decorator that verifies the JWT is present and confirms
    the user's role is 'admin'.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                # Verifies JWT is present, valid, and not expired
                verify_jwt_in_request()
                claims = get_jwt()
                
                # Check if the role claim is 'admin'
                if claims.get("role") != "admin":
                    return jsonify({"error": "Access forbidden: Admin role required."}), 403
                else:
                    # Proceed to the protected function
                    return fn(*args, **kwargs)
            
            except Exception as e:
                # Handle cases like missing token, expired token, etc.
                return jsonify({"error": f"Authentication error: {str(e)}"}), 401
                
        return decorator
    return wrapper