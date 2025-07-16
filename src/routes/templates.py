from flask import Blueprint, jsonify, request
from src.models.resume import Template
from src.models import db
from src.routes.auth import token_required

templates_bp = Blueprint('templates', __name__)

def init_default_templates():
    """Initialize default templates if they don't exist"""
    if Template.query.count() > 0:
        return

    default_templates = [
        {
            "template_id": "tech_modern", "name": "Tech Modern", "category": "modern", "industry": "Technology",
            "description": "Clean, contemporary design with a focus on skills and projects.", "rating": 4.9,
            "color_options": "[\"#3B82F6\", \"#10B981\", \"#8B5CF6\"]", "preview_url": "/images/template-tech.png"
        },
        {
            "template_id": "finance_professional", "name": "Finance Professional", "category": "professional", "industry": "Finance",
            "description": "A classic, trusted layout for corporate and financial roles.", "rating": 4.8,
            "color_options": "[\"#1F2937\", \"#059669\", \"#D97706\"]", "preview_url": "/images/template-finance.png"
        },
        {
            "template_id": "creative_bold", "name": "Creative Bold", "category": "creative", "industry": "Creative & Design",
            "description": "A visually striking design perfect for creative industries.", "rating": 4.7,
            "color_options": "[\"#EF4444\", \"#F59E0B\", \"#EC4899\"]", "preview_url": "/images/template-creative.png"
        }
    ]

    for template_data in default_templates:
        template = Template(**template_data)
        db.session.add(template)

    db.session.commit()
    print("Default templates initialized.")

@templates_bp.route('/', methods=['GET'])
@token_required
def get_templates(current_user):
    try:
        init_default_templates()

        category = request.args.get('category')
        industry = request.args.get('industry')

        query = Template.query.filter_by(is_active=True)

        if category:
            query = query.filter_by(category=category)
        if industry:
            query = query.filter_by(industry=industry)

        templates = query.order_by(Template.rating.desc()).all()

        return jsonify({
            "success": True,
            "templates": [template.to_dict() for template in templates]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
