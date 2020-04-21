from flask_wtf import form
from flask_wtf.file import FileField, FileAllowed
from wtforms import validators, StringField
from wtforms.widgets import TextArea


class FeedPostForm(form.FlaskForm):
    images = FileField(
        'Select images',
        render_kw={'multiple': True},
        validators=[
            FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Only JPEG, PNG and GIFs allowed')
        ]
    )

    post = StringField('Post',
                       widget=TextArea(),
                       validators=[
                           validators.DataRequired(),
                           validators.length(max=1024)]
                       )
