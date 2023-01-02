from app.core.db import db



class QuestionHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(800), index=False,
                         nullable=False, unique=True)
    answer = db.Column(db.Text, index=False,
                        nullable=True, unique=False)
    answer_approved = db.Column(db.Boolean, nullable=True, default=False)
    answer_approved_at = db.Column(db.DateTime(timezone=True))
    create_at = db.Column(db.DateTime(timezone=True), index=False, default=convert_datetime_to_local(datetime.utcnow()))
    create_user_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False)
    update_at = db.Column(db.DateTime(timezone=True))
    update_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    answer_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    answer_approve_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    answer_at = db.Column(db.DateTime(timezone=True))
    question_network_id = db.Column(
        db.Integer, db.ForeignKey('network.id'), nullable=False)
    answer_network_id = db.Column(
        db.Integer, db.ForeignKey('network.id'), nullable=True)
    active = db.Column(db.Boolean, nullable=False)