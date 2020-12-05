from flask import Flask, jsonify, abort, make_response
from flask_restful import Api, Resource, reqparse, fields, marshal
import sqlalchemy.orm
from cockroachdb.sqlalchemy import run_transaction
from backend.models import CheckIn, db

app = Flask(__name__, static_url_path="")
api = Api(app)
db.init_app(app)

app.config.from_pyfile('ketchup.cfg')
sessionmaker = sqlalchemy.orm.sessionmaker(db.engine)

class EmotionTranslater(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('text', type=str, required=True,
                                   help='No response provided',
                                   location='json')
        super(EmotionTranslater, self).__init__()

    def add_checkin_to_db(self, ketchup):
        def callback(session):
            session.add(ketchup)
        run_transaction(sessionmaker, callback)

    def checkin_by_user(self, user_id):
        def callback(session):
            return session.query(CheckIn).order_by(CheckIn.date.desc()).limit(10).all()
        run_transaction(sessionmaker, callback)

    def get(self, id):
        ketchup_bottle = self.checkin_by_user(id)
        #do some sort of analysis
        return {"most_freq_emotion": "", "average_sentiment": 0}

    def post(self, id):
        args = self.reqparse.parse_args()
        text = args["text"]
        #send text to google cloud translate api
        sentiment = 0
        emotion = ""
        ketchup = CheckIn(id, text, sentiment, emotion)
        self.add_checkin_to_db(ketchup)
        return {"emotion": emotion, "sentiment": sentiment}, 201

api.add_resource(EmotionTranslater, '/api/emotion/<int:id>', endpoint='tasks')


if __name__ == '__main__':
    app.run(debug=True)