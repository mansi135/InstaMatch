from flask import Flask, redirect, url_for, session, request, render_template
from flask_oauth import OAuth
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined


SECRET_KEY = 'development key'
DEBUG = True
FACEBOOK_APP_ID = '1616471035080729'
FACEBOOK_APP_SECRET = 'c8361be5b9f39436dd6aa1442181fde6'


app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
oauth = OAuth()


# I added the following config otherwise, everytime the redirect was giving warning
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    # request_token_params={'scope': ['public_profile','user_friends','email']}
    request_token_params={'scope': 'public_profile, user_friends, email'}
)



# @app.route('/home-me')
# def check_something():
#     return render_template("homepage.html")


@app.route('/')
def index():

    # print session['token']
    
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))
     # return redirect(url_for('login'))


# @app.route('/login')
# def login():
#     return facebook.authorize(callback=url_for('facebook_authorized',
#         next=request.args.get('next') or request.referrer or None,
#         _external=True))


@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
    return 'Logged in as id=%s name=%s redirect=%s' % \
        (me.data['id'], me.data['name'], request.args.get('next'))


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')


if __name__ == '__main__':
    # app.run()
    app.debug = True

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")

