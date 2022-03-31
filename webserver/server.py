
"""hav
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for, flash
from flask_session import Session
from forms import *
from models import *
import random

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

sess = Session()
#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.74.246.148/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.74.246.148/proj1part2"
#
DATABASEURI = "postgresql://zy2447:9829@w4111.cisxo09blonu.us-east-1.rds.amazonaws.com/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request.

    The variable g is globally accessible.
    """
    g.user = None
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback; traceback.print_exc()
        g.conn = None

    if "user_id" in session and session["user_id"]:
        print(session["user_id"])
        g.user = Users(session["user_id"])


@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't, the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
    """
    request is a special object that Flask provides to access web request information:

    request.method:   "GET" or "POST"
    request.form:     if the browser submitted a form, this contains the data in the form
    request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

    See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data

    """

    # DEBUG: this is debugging code to see what request looks like
    print(request.args)


    #
    # example of a database query
    #
    cursor = g.conn.execute("SELECT name FROM test")
    names = []
    for result in cursor:
      names.append(result['name'])  # can also be accessed using result[0]
    cursor.close()

    #
    # Flask uses Jinja templates, which is an extension to HTML where you can
    # pass data to a template and dynamically generate HTML based on the data
    # (you can think of it as simple PHP)
    # documentation: https://realpython.com/primer-on-jinja-templating/
    #
    # You can see an example template in templates/index.html
    #
    # context are the variables that are passed to the template.
    # for example, "data" key in the context variable defined below will be
    # accessible as a variable in index.html:
    #
    #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
    #     <div>{{data}}</div>
    #
    #     # creates a <div> tag for each element in data
    #     # will print:
    #     #
    #     #   <div>grace hopper</div>
    #     #   <div>alan turing</div>
    #     #   <div>ada lovelace</div>
    #     #
    #     {% for n in data %}
    #     <div>{{n}}</div>
    #     {% endfor %}
    #
    context = dict(data = names)


    #
    # render_template looks in the templates/ folder for files.
    # for example, the below file reads template/index.html
    #
    return redirect('/login')

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#


# Example of adding new data to the database
@app.errorhandler(404)
def page_not_found(e):
    return "page not found"


@app.route('/login', methods=['GET', 'POST'])
def login():
    loginForm = LoginForm(request.form)
    if request.method == 'POST' and loginForm.validate():
        return redirect('/home')
    return render_template("login.html", form=loginForm)


@app.route('/logout', methods=['GET'])
def logout():
    session["user_id"] = None
    return redirect('/login')


@app.route('/home', methods=['GET', 'POST'])
def home():
    searchForm = SearchForm(request.form)
    cursor = g.conn.execute(
        "SELECT category_id, category_name FROM category"
    )
    for result in cursor:
        searchForm.category.choices.append((result["category_id"], result["category_name"]))

    products = []
    cursor = g.conn.execute(
        "SELECT * FROM product_own"
    )
    for result in cursor:
        user = Users(result[4])
        products.append(Products(
            id=result[0],
            name=result[1],
            price=result[2],
            description=result[3],
            owner=user,
            comment_obj=result[5]
        ))
    if request.method == 'POST' and searchForm.validate():
        # filter out rows that not meet this search condition
        #CASE INSENSITIVE SEARCH
        searchtxt = searchForm.text.data.casefold()
        category = searchForm.category.data
        update = []
        for prod in products:
            if category == 'All' and searchtxt in prod.name.casefold():
                update.append(prod)
            elif category != 'All' and int(category) in prod.categories and searchtxt in prod.name.casefold():
                update.append(prod)
        products = update

    context = dict(user=g.user, form=searchForm, products=products)
    return render_template("home.html", **context)


@app.route('/wishlist')
def wishlist():
    products = g.user.get_wishlist()
    context = dict(user=g.user, products=products)
    return render_template("wishlist.html", **context)


@app.route('/orders')
def orders():
    products = g.user.get_orders()
    context = dict(user=g.user, products=products)
    return render_template("orders.html", **context)


def create_product(form):
    """
    Create a new product in the database.
    Need to insert a row in belongs_to table, product_own table,
    and comment_obj table
    :param form: ProductForm
    """
    name = form.name.data
    category = form.category.data
    description = form.description.data
    price = form.price.data
    # get product_id
    product_id = None
    cursor = g.conn.execute(
        "SELECT MAX(p.product_id) FROM product_own p"
    )
    for result in cursor:
        product_id = int(result[0]) + 1
    # get comment_obj_id
    obj_id = None
    cursor = g.conn.execute(
        "SELECT MAX(c.obj_id) FROM comment_obj c"
    )
    for result in cursor:
        obj_id = int(result[0]) + 1
    # insert into comment_obj
    g.conn.execute(
        "INSERT INTO comment_obj VALUES (%s)",
        obj_id
    )
    # insert into a product_own
    g.conn.execute(
        "INSERT INTO product_own VALUES (%s, %s, %s, %s, %s, %s)",
        product_id,
        name,
        price,
        description,
        g.user.user_id,
        obj_id
    )
    # insert into belongs
    g.conn.execute(
        "INSERT INTO belongs_to VALUES (%s, %s)",
        product_id,
        category
    )


@app.route('/sell', methods=['GET', 'POST'])
def upload_product():
    productForm = ProductForm(request.form)
    cursor = g.conn.execute(
        "SELECT category_id, category_name FROM category"
    )
    for result in cursor:
        productForm.category.choices.append((result["category_id"], result["category_name"]))

    if request.method == 'POST' and productForm.validate():
        create_product(productForm)
        return redirect('/home')
    context = dict(user=g.user, form=productForm)
    return render_template("sell.html", **context)


def create_comment(form, obj_id):
    rating = form.rating.data
    comment = form.comment.data
    # check if this user already write comment for this product
    cursor = g.conn.execute(
        "SELECT * FROM comments_created_at_written_for c WHERE c.user_id = %s and c.obj_id = %s",
        g.user.user_id,
        obj_id
    )
    for result in cursor:
        return False
    # get comment_id
    comment_id = None
    cursor = g.conn.execute(
        "SELECT MAX(c.comment_id) FROM comments_created_at_written_for c"
    )
    for result in cursor:
        comment_id = int(result[0]) + 1

    g.conn.execute(
        "INSERT INTO comments_created_at_written_for(comment_id, rating, comment_content, user_id, obj_id)  VALUES (%s,%s,%s,%s,%s)",
        comment_id,
        rating,
        comment,
        g.user.user_id,
        obj_id
    )
    return True


@app.route('/product-details/<id>', methods=['GET', 'POST'])
def product_details(id):
    product = None
    cursor = g.conn.execute(
        "SELECT * FROM product_own p WHERE p.product_id=%s",
        id
    )
    for result in cursor:
        user = Users(result[4])
        product = Products(
            id=result[0],
            name=result[1],
            price=result[2],
            description=result[3],
            owner=user,
            comment_obj=result[5]
        )
    if product is None:
        return redirect('/404')

    commentForm = CommentForm(request.form)
    comments = product.get_comments()
    if request.method == 'POST' and commentForm.validate():
        if not create_comment(commentForm, product.comment_obj):
            flash("You cannot write two comments for the same product")
            return redirect(url_for('product_details', id=id))
        else:
            flash("Thank you! We appreciate your comment!")
            return redirect(url_for('product_details', id=id))
    context = dict(product=product, comments=comments, form=commentForm)
    return render_template("details.html", **context)


@app.route('/buy/<id>')
def buy_product(id):
    product = None
    cursor = g.conn.execute(
        "SELECT * FROM product_own p WHERE p.product_id=%s",
        id
    )
    for result in cursor:
        user = Users(result[4])
        product = Products(
            id=result[0],
            name=result[1],
            price=result[2],
            description=result[3],
            owner=user,
            comment_obj=result[5]
        )
    if product is None:
        return redirect('/404')

    # insert a row into buy
    try:
        g.conn.execute(
            "INSERT INTO buy VALUES (%s,%s)",
            g.user.user_id,
            product.id
        )
    except:
        # if buy table already had such tuple
        flash("You already bought %s and you cannot buy it again" % product.name)
        return redirect(url_for('product_details', id=id))
    flash("You just bought %s" % product.name)
    return redirect(url_for('product_details', id=id))


@app.route('/wish/<id>')
def wish_product(id):
    product = None
    cursor = g.conn.execute(
        "SELECT * FROM product_own p WHERE p.product_id=%s",
        id
    )
    for result in cursor:
        user = Users(result[4])
        product = Products(
            id=result[0],
            name=result[1],
            price=result[2],
            description=result[3],
            owner=user,
            comment_obj=result[5]
        )
    if product is None:
        return redirect('/404')

    try:
        g.conn.execute(
            "INSERT INTO wish VALUES (%s,%s)",
            g.user.user_id,
            product.id
        )
    except:
        # if wish table already had such tuple
        flash("Item %s is already in your wishlist" % product.name)
        return redirect(url_for('product_details', id=id))

    flash("You just added %s into your wishlist" % product.name)
    return redirect(url_for('product_details', id=id))


@app.route('/seller-details/<id>', methods=['GET', 'POST'])
def seller_details(id):
    seller = Users(id)
    comments = seller.get_comments()
    commentForm = CommentForm(request.form)
    if request.method == 'POST' and commentForm.validate():
        if not create_comment(commentForm, seller.obj_id):
            flash("You cannot write two comments for the same seller")
            return redirect(url_for('seller_details', id=id))
        else:
            flash("Thank you! We appreciate your comment!")
            return redirect(url_for('seller_details', id=id))
    context = dict(seller=seller, comments=comments, form=commentForm)
    return render_template('seller.html', **context)


@app.route('/recommend', methods=['GET'])
def recommend():
    categories = g.user.get_most_wanted()
    if not categories:
        context = dict(user=g.user, products=[])
        return render_template('recommend.html', **context)
    products = []
    i = random.randint(0, len(categories) - 1)
    category = categories[i]
    cursor = g.conn.execute(
        "SELECT * FROM product_own p, belongs_to b WHERE p.product_id=b.product_id and b.category_id=%s",
        category,
    )
    for result in cursor:
        user = Users(result[4])
        p = Products(
            id=result[0],
            name=result[1],
            price=result[2],
            description=result[3],
            owner=user,
            comment_obj=result[5]
        )
        if p.get_rating() >= 3.5:
            products.append(p)

    context = dict(user=g.user, products=products)
    return render_template('recommend.html', **context)


if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
      """
      This function handles command line parameters.
      Run the server using:

          python3 server.py

      Show the help text using:

          python3 server.py --help

      """

      HOST, PORT = host, port
      print("running on %s:%d" % (HOST, PORT))
      app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    # set secret key for app session
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    sess.init_app(app)

    run()
