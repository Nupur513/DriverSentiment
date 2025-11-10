from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token
from models.user import User, UserRole
from backend.database import db_session

# Create a Blueprint for authentication routes
auth_bp = Blueprint('auth_api', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user (rider or admin).
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role_str = data.get('role', 'user') # Default to 'user'

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if role_str not in [role.value for role in UserRole]:
        return jsonify({"error": f"Invalid role. Must be one of: {[role.value for role in UserRole]}"}), 400
    
    role = UserRole(role_str)
    
    # Check if user already exists
    if db_session.query(User).filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409

    try:
        new_user = User(username=username, role=role)
        new_user.set_password(password)
        
        db_session.add(new_user)
        db_session.commit()
        
        return jsonify({
            "message": "User created successfully",
            "user": {
                "id": new_user.id,
                "username": new_user.username,
                "role": new_user.role.value
            }
        }), 201

    except IntegrityError:
        db_session.rollback()
        return jsonify({"error": "Database error, user may already exist"}), 409
    except Exception as e:
        db_session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        db_session.remove()

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Log in a user and return a JWT access token.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    try:
        user = db_session.query(User).filter_by(username=username).first()

        if user and user.check_password(password):
            # Create token with user ID as identity and role in claims
            additional_claims = {"role": user.role.value}
            access_token = create_access_token(
                identity=str(user.id), 
                additional_claims=additional_claims
            )
            
            return jsonify({
                "message": "Login successful",
                "access_token": access_token
            }), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        db_session.remove()