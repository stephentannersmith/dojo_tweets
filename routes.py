from config import app
from controller_functions import index, register, tweet_landing, login, add_tweet, delete_tweet, add_like, show_edit, update_tweet, show_users, follow_user, logout

app.add_url_rule("/", view_func=index)
app.add_url_rule("/register", view_func=register, methods={"POST"})
app.add_url_rule("/success", view_func=tweet_landing)
app.add_url_rule("/login", view_func=login, methods=["POST"])
app.add_url_rule("/tweet", view_func=add_tweet, methods=["POST"])
app.add_url_rule("/tweets/<tweet_id>/delete", view_func=delete_tweet, methods=["POST"])
app.add_url_rule("/tweets/<tweet_id>/like", view_func=add_like, methods=["POST"])
app.add_url_rule("/tweets/<tweet_id>/edit", view_func=show_edit)
app.add_url_rule("/tweets/<tweet_id>/update", view_func=update_tweet, methods=["POST"])
app.add_url_rule("/users", view_func=show_users)
app.add_url_rule("/follow/<user_id>", view_func=follow_user)
app.add_url_rule("/logout", view_func=logout)
