from flask import Blueprint, request, session, render_template, redirect, url_for, abort
from user.models import User
from relationship.models import Relationship
from utils.commons import email

relationship_blueprint = Blueprint('relationship_blueprint', __name__)


@relationship_blueprint.route('/add_friend/<to_username>')
def add_friend(to_username):
    ref = request.referrer

    logged_user = User.getByName(session.get('username'))
    to_user = User.getByName(to_username)
    if to_user:

        rel_status = Relationship.get_relationship_status(logged_user, to_user)
        if rel_status == "REVERSE_FRIENDS_PENDING":

            Relationship(
                from_user=logged_user.id,
                to_user=to_user.id,
                rel_type=Relationship.RELATIONSHIP_TYPE.get(Relationship.FRIENDS),
                status=Relationship.STATUS_TYPE.get(Relationship.APPROVED)
            ).save_database()

            reverse_rel = Relationship.get_relationship(to_user, logged_user)
            reverse_rel.status = Relationship.STATUS_TYPE.get(Relationship.APPROVED)
            reverse_rel.update_record()

        elif rel_status is None:  # and rel_status != "REVERSE_BLOCKED"

            Relationship(
                from_user=logged_user.id,
                to_user=to_user.id,
                rel_type=Relationship.RELATIONSHIP_TYPE.get(Relationship.FRIENDS),
                status=Relationship.STATUS_TYPE.get(Relationship.PENDING)
            ).save_database()

            # email the user
            body_html = render_template(
                'mail/relationship/added_friend.html',
                from_user=logged_user,
                to_user=to_user,
            )
            body_text = render_template(
                'mail/relationship/added_friend.txt',
                from_user=logged_user,
                to_user=to_user,
            )

            # email(to_user.email,
            #       ("%s has requested to be friends") % logged_user.first_name,
            #       body_html,
            #       body_text)

        if ref:
            return redirect(ref)
        else:
            return redirect(url_for('user_blueprint.profile', username=to_user.username))
    else:
        abort(404)


@relationship_blueprint.route('/remove_friend/<to_username>')
def remove_friend(to_username):
    ref = request.referrer
    logged_user = User.getByName(session.get('username'))
    to_user = User.getByName(to_username)

    if to_user:

        rel_status = Relationship.get_relationship_status(logged_user, to_user)
        if rel_status == "FRIENDS_PENDING" \
            or rel_status == "FRIENDS_APPROVED" \
            or rel_status == "REVERSE_FRIENDS_PENDING":

            rel = Relationship.get_relationship(logged_user, to_user)
            rel.delete_record()
            reverse_rel = Relationship.get_relationship(to_user, logged_user)
            reverse_rel.delete_record()

        if ref:
            return redirect(ref)
        else:
            return redirect(url_for('user_blueprint.profile', username=to_user.username))
    else:
        abort(404)


@relationship_blueprint.route('/block/<to_username>')
def block(to_username):
    ref = request.referrer
    logged_user = User.getByName(session.get('username'))
    to_user = User.getByName(to_username)

    if to_user:

        rel_status = Relationship.get_relationship_status(logged_user, to_user)
        if rel_status == "FRIENDS_PENDING" \
            or rel_status == "FRIENDS_APPROVED" \
            or rel_status == "REVERSE_FRIENDS_PENDING":

            rel = Relationship.get_relationship(logged_user, to_user)
            rel.delete_record()
            reverse_rel = Relationship.get_relationship(to_user, logged_user)
            reverse_rel.delete_record()

        Relationship(
            from_user=logged_user.id,
            to_user=to_user.id,
            rel_type=Relationship.RELATIONSHIP_TYPE.get(Relationship.BLOCKED),
            status=Relationship.STATUS_TYPE.get(Relationship.APPROVED)
        ).save_database()

        if ref:
            return redirect(ref)
        else:
            return redirect(url_for('user_blueprint.profile', username=to_user.username))
    else:
        abort(404)


@relationship_blueprint.route('/unblock/<to_username>')
def unblock(to_username):
    ref = request.referrer
    logged_user = User.getByName(session.get('username'))
    to_user = User.getByName(to_username)

    if to_user:
        rel_status = Relationship.get_relationship_status(logged_user, to_user)

        if rel_status == "BLOCKED":
            rel = Relationship.get_relationship(logged_user, to_user)
            rel.delete_record()
        if ref:
            return redirect(ref)
        else:
            return redirect(url_for('user_blueprint.profile', username=to_user.username))

    else:
        abort(404)
