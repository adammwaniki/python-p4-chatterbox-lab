from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():

    if request.method == 'GET':
        messages = [message.to_dict() for message in Message.query.all()]

        return make_response(
            jsonify(messages), 
            200
        )
    # I had initially made the mistake of handling form data as the end point instead of
    # JSON input. this was resulting in an error for this lab
    elif request.method == 'POST':
        data = request.get_json()
        new_message = Message(
            username=data.get("username"),
            body=data.get("body")
        )

        db.session.add(new_message)
        db.session.commit()

        message_dict = new_message.to_dict()

        response = make_response(
            jsonify(message_dict),
            201
        )

        return response
    
@app.route('/messages/<int:id>', methods=['GET', 'PATCH'])
def message(id):

    message = Message.query.filter_by(id=id).first()

    if request.method == 'GET':
        message_serialized = message.to_dict()
        return make_response(
            jsonify(message_serialized),
            200
        )
    elif request.method == 'PATCH':
        
        if message is None:
            return make_response(
                jsonify(
                    {"error": "Message not found"}),
                    404
            )
        
        # Same as in the POST method here i needed to handle json instead of form data for this lab
        data = request.get_json()
        if 'body' in data:
            message.body = data['body']

        db.session.add(message)
        db.session.commit()

        message_dict = message.to_dict()

        response = make_response(
            jsonify(message_dict),
            200
        )
        
        return response
    
@app.route('/messages/<int:id>', methods=['GET', 'DELETE'])
def delete_message(id):

    message = Message.query.filter_by(id=id).first()
    
    if message is None:
            return make_response(
                jsonify(
                    {"error": "Message not found"}),
                    404
            )
    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()

        response_body = {
            "delete_successful": True,
            "message": "Message deleted"
        }

        response = make_response(
            response_body,
            200
        )

        return response



if __name__ == '__main__':
    app.run(port=5555)
