from flask import Blueprint, jsonify
from src.models.user import User
from src.routes.auth import token_required

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@token_required
def get_user_profile(current_user):
    """Returns the profile of the currently logged-in user."""
    if not current_user:
        return jsonify({"success": False, "error": "User not found"}), 404

    return jsonify({
        "success": True,
        "user": current_user.to_dict()
    })

# Note: The admin routes already provide functionality for managing users.
# If you need users to be able to update their own profiles, you can add
# a PUT endpoint here, like this:
#
# @user_bp.route('/profile', methods=['PUT'])
# @token_required
# def update_user_profile(current_user):
#     data = request.get_json()
#     current_user.full_name = data.get('full_name', current_user.full_name)
#     current_user.headline = data.get('headline', current_user.headline)
#     # Add other updatable fields here
#     db.session.commit()
#     return jsonify({"success": True, "message": "Profile updated successfully"})
