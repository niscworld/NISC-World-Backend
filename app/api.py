from flask import Blueprint, request, jsonify

from .util_mail import send_email as send_mail_util # Assuming you have a utility function to send emails

api_route = Blueprint('api', __name__)

@api_route.route('/v1/sendMail', methods=['POST'])
def send_mail():
    data = request.get_json()
    if not data or 'email' not in data or 'subject' not in data or 'message' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    email = data['email']
    subject = data['subject']
    message = data['message']
    if not email or not subject or not message:
        return jsonify({'error': 'Email, subject, and message are required'}), 400
    # Call the utility function to send the email
    try:
        result = send_mail_util(email, subject, message)
        if not result:
            return jsonify({'error': 'Failed to send email'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Here you would implement the logic to send the email
    # For now, we will just return a success message
    return jsonify({'status': 'success', 'message': f'Email sent to {email} with subject "{subject}"'}), 200


