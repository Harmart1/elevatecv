from flask import Blueprint, jsonify, request
from src.ai_service import ai_service
from src.routes.auth import token_required
from src.models import db
from src.models.resume import InterviewSession

interview_bp = Blueprint('interview', __name__)

@interview_bp.route('/generate-questions', methods=['POST'])
@token_required
def generate_questions(current_user):
    try:
        data = request.get_json()
        if not data or not data.get('job_description'):
            return jsonify({'success': False, 'error': 'Job description is required'}), 400

        questions_result = ai_service.generate_interview_questions(
            data['job_description'], data.get('position_level', 'mid')
        )

        return jsonify({'success': True, 'questions': questions_result})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Question generation failed: {str(e)}'}), 500

@interview_bp.route('/evaluate-answer', methods=['POST'])
@token_required
def evaluate_answer(current_user):
    try:
        data = request.get_json()
        if not data or not data.get('question') or not data.get('answer'):
            return jsonify({'success': False, 'error': 'Question and answer are required'}), 400

        evaluation_prompt = f"""
        Evaluate the following interview answer and provide constructive feedback.
        Question: {data['question']}
        Answer: {data['answer']}

        Please provide evaluation in JSON format enclosed in ```json ... ```:
        {{
            "score": <score from 1-10>,
            "strengths": ["strength1", "strength2"],
            "areas_for_improvement": ["improvement1", "improvement2"],
            "overall_feedback": "detailed feedback"
        }}
        """

        ai_response = ai_service._call_google_ai(evaluation_prompt, max_tokens=1000)

        if ai_response:
            evaluation = ai_service._extract_json_from_response(ai_response)
            if evaluation:
                # Log this practice session
                new_session = InterviewSession(
                    user_id=current_user.id,
                    session_type='practice_answer',
                    performance_score=evaluation.get('score', 0)
                )
                db.session.add(new_session)
                db.session.commit()
                return jsonify({'success': True, 'evaluation': evaluation})

        # Fallback evaluation
        fallback_evaluation = {
            "score": 7, "strengths": ["Clear communication"],
            "areas_for_improvement": ["More specific details"],
            "overall_feedback": "Good response, but could be improved by using the STAR method to structure your answer."
        }
        return jsonify({'success': True, 'evaluation': fallback_evaluation})

    except Exception as e:
        return jsonify({'success': False, 'error': f'Answer evaluation failed: {str(e)}'}), 500
