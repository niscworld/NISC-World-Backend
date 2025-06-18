from flask import Blueprint, request, jsonify

api_route = Blueprint('api', __name__)

@api_route.route('/v1/sendMail', methods=['POST'])
def send_mail():
    data = request.get_json()
    if not data or 'email' not in data or 'subject' not in data or 'message' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    email = data['email']
    subject = data['subject']
    message = data['message']

    # Here you would implement the logic to send the email
    # For now, we will just return a success message
    return jsonify({'status': 'success', 'message': f'Email sent to {email} with subject "{subject}"'}), 200


