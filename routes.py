from flask import Blueprint, jsonify, request
from app import db
from models import Task, Comment
from schemas import TaskSchema, CommentSchema

bp = Blueprint("api", __name__)

task_schema = TaskSchema()
comment_schema = CommentSchema()

@bp.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    errors = task_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    task = Task(title=data["title"], description=data.get("description"))
    db.session.add(task)
    db.session.commit()
    return jsonify(task_schema.dump(task)), 201


@bp.route("/tasks/<int:task_id>/comments", methods=["GET"])
def list_comments(task_id):
    Task.query.get_or_404(task_id)
    comments = Comment.query.filter_by(task_id=task_id).all()
    return jsonify([comment_schema.dump(c) for c in comments])


@bp.route("/tasks/<int:task_id>/comments", methods=["POST"])
def add_comment(task_id):
    Task.query.get_or_404(task_id)
    data = request.get_json()
    data["task_id"] = task_id

    errors = comment_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    comment = Comment(
        task_id=task_id,
        author=data["author"],
        body=data["body"]
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment_schema.dump(comment)), 201


@bp.route("/comments/<int:comment_id>", methods=["PUT"])
def update_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    data = request.get_json()

    if "author" in data:
        comment.author = data["author"]
    if "body" in data:
        comment.body = data["body"]

    db.session.commit()
    return jsonify(comment_schema.dump(comment))


@bp.route("/comments/<int:comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    return jsonify({"message": "Deleted"})
