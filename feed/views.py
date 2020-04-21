import os
from flask import redirect, render_template, url_for, abort, Blueprint, session, request

from feed.process import process_message
from user.models import User
from feed.models import Feed, Message
from feed.forms import FeedPostForm
from feed.models import COMMENT, LIKE, MESSAGE_TYPE
from user.decorators import login_required
from werkzeug.utils import secure_filename
from settings import Config
from utils.image_upload import image_height_transform
from utils.database import Database


feed_blueprint = Blueprint('feed_blueprint', __name__)


@feed_blueprint.route('/message/add', methods=('GET', 'POST'))
@login_required
def add_message():
    ref = request.referrer
    form = FeedPostForm()

    if form.validate_on_submit():
        from_user = User.getByName(session.get('username'))
        from_user = from_user.id
        # process images
        post_images = []
        uploaded_files = request.files.getlist('images')
        if uploaded_files and uploaded_files[0].filename != '':
            for file in uploaded_files:
                filename = secure_filename(file.filename)
                folder_path = os.path.join(Config.UPLOAD_FOLDER, 'posts_' + from_user)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                file_path = os.path.join(folder_path, filename)
                file.save(file_path)
                post_images.append(file_path)

        # process post
        to_user = User.getByName(request.values.get('to_user'))
        to_user = to_user.id
        post = form.post.data
        # if this is a self post
        if from_user == to_user:
            to_user = None
        message = Message(
            from_user=from_user,
            to_user=to_user,
            text=post,
        )

        message.save_database()
        feed = Feed(
            user=from_user,
            message=message.id
        )
        feed.save_database()
        # store images
        if len(post_images):
            images = []
            for file_path in post_images:
                (image_ts, width) = image_height_transform(file_path, 'posts', str(message.id))
                images.append({"ts": str(image_ts), "w": str(width)})
            message.images = images
            message.update_record()

        # process the message
        process_message(message)
        if ref:
            return redirect(ref)
        else:
            return redirect(url_for('user_blueprint.home'))

    else:
        return abort(404)


@feed_blueprint.route('/comment/<string:message_id>', methods=['GET', 'POST'])
@login_required
def comment(message_id):
    form = FeedPostForm()
    message = Message.getMessage(message_id)
    if not message:
        abort(404)

    if message and message.parent:
        abort(404)

    if form.validate_on_submit() and session.get('username'):
        # process post
        from_user = User.getByName(session.get('username'))
        post = form.post.data

        # process write
        comment_ = Message(
            from_user=from_user.id,
            text=post,
            parent=message_id,
            message_type=MESSAGE_TYPE.get(COMMENT),
        )

        comment_.save_database()
        return redirect(url_for('feed_blueprint.comment', message_id=message_id))

    return render_template('feed/message.html',
                           message=message,
                           form=form
                           )


@feed_blueprint.route('/like/<string:message_id>', methods=['GET', 'POST'])
@login_required
def like(message_id):
    message = Message.getMessage(message_id)

    if not message:
        abort(404)

    if message and message.parent:
        abort(404)

    from_user = User.getByName(session.get('username'))

    # check if first like or not
    existing_like = Database.find('messages', {
                                                "parent": message_id,
                                                "from_user": from_user.id,
                                                "message_type": MESSAGE_TYPE.get(LIKE)
                                            }).count()

    if not existing_like:
        # write like
        like_ = Message(
            from_user=from_user.id,
            to_user=message.from_user,
            parent=message_id,
            message_type=MESSAGE_TYPE.get(LIKE)
        )

        like_.save_database()

    return redirect(url_for('feed_blueprint.comment', message_id=message.id))
