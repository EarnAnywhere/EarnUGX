from flask import Flask, jsonify, session
from flask_cors import CORS
from config import Config
from models import db, User, Task, Ledger, TaskCompletion, Withdrawal
from routes.auth import auth_bp, bcrypt, login_required

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, supports_credentials=True)
    db.init_app(app)
    bcrypt.init_app(app)

    with app.app_context():
        db.create_all()
        if Task.query.count() == 0:
            db.session.add_all([
                Task(
                    title="Welcome task",
                    description="Complete this demo task to test the earning flow.",
                    reward_ugx=500
                ),
                Task(
                    title="Read the platform rules",
                    description="Read the rules and confirm that you understand them.",
                    reward_ugx=250
                )
            ])
            db.session.commit()

    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    @app.get("/")
    def home():
        return jsonify({"name": "Lite UGX Earn", "status": "online", "version": "1.0"})

    @app.get("/api/health")
    def health():
        return jsonify({"status": "healthy"})

    @app.get("/api/dashboard")
    @login_required
    def dashboard():
        user_id = session["user_id"]
        user = db.session.get(User, user_id)
        credits = db.session.query(db.func.coalesce(db.func.sum(Ledger.amount_ugx), 0)).filter(
            Ledger.user_id == user_id
        ).scalar() or 0
        tasks = Task.query.filter_by(status="active").all()
        completed = {
            row.task_id for row in TaskCompletion.query.filter_by(user_id=user_id).all()
        }
        ledger = Ledger.query.filter_by(user_id=user_id).order_by(Ledger.created_at.desc()).limit(50).all()

        return jsonify({
            "user": {
                "name": user.name,
                "phone": user.phone,
                "referral_code": user.referral_code
            },
            "balance_ugx": int(credits),
            "tasks": [{
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "reward_ugx": t.reward_ugx,
                "completed": t.id in completed
            } for t in tasks],
            "ledger": [{
                "type": x.type,
                "amount_ugx": x.amount_ugx,
                "reference": x.reference,
                "created_at": x.created_at.isoformat()
            } for x in ledger]
        })

    @app.post("/api/tasks/<int:task_id>/complete")
    @login_required
    def complete_task(task_id):
        user_id = session["user_id"]
        task = db.session.get(Task, task_id)
        if not task or task.status != "active":
            return jsonify({"error": "Task not available"}), 404

        if TaskCompletion.query.filter_by(user_id=user_id, task_id=task_id).first():
            return jsonify({"error": "Task already completed"}), 409

        completion = TaskCompletion(user_id=user_id, task_id=task_id)
        ledger = Ledger(
            user_id=user_id,
            type="TASK_REWARD",
            amount_ugx=task.reward_ugx,
            reference=f"TASK-{task.id}"
        )
        db.session.add(completion)
        db.session.add(ledger)
        db.session.commit()

        return jsonify({"message": "Task completed", "reward_ugx": task.reward_ugx})

    @app.post("/api/withdrawals")
    @login_required
    def request_withdrawal():
        data = request.get_json(silent=True) or {}
        try:
            amount = int(data.get("amount_ugx", 0))
        except (TypeError, ValueError):
            amount = 0
        phone = str(data.get("phone", "")).strip()

        if amount <= 0 or not phone:
            return jsonify({"error": "Valid amount and phone are required"}), 400

        user_id = session["user_id"]
        balance = db.session.query(db.func.coalesce(db.func.sum(Ledger.amount_ugx), 0)).filter(
            Ledger.user_id == user_id
        ).scalar() or 0

        if amount > balance:
            return jsonify({"error": "Insufficient balance"}), 400

        withdrawal = Withdrawal(
            user_id=user_id,
            amount_ugx=amount,
            phone=phone,
            status="pending"
        )
        ledger = Ledger(
            user_id=user_id,
            type="WITHDRAWAL_HOLD",
            amount_ugx=-amount,
            reference="WITHDRAWAL-PENDING"
        )
        db.session.add(withdrawal)
        db.session.add(ledger)
        db.session.commit()

        return jsonify({"message": "Withdrawal request submitted", "status": "pending"}), 201

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
