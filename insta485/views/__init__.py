"""Views, one for each Insta485 page."""

# Index routes
from insta485.views.index import show_index
from insta485.views.users import show_user, show_followers, show_following
from insta485.views.posts import show_post, update_posts
from insta485.views.likes import update_likes
from insta485.views.comments import update_comments
from insta485.views.following import update_following
from insta485.views.accounts import *
from insta485.views.explore import show_explore
from insta485.views.uploads import show_upload