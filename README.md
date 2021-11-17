# COMS4111_Proj1
Project 1 for COMS 4111
BoChao Xin
ChangSu Nam

PostgreSQL account: 
bx2196


URL address of our web application:
http://35.237.109.152:8111/


We implemented everything specified in proposal of this project, except the bidding system.
Originally, we wanted to include a bidding system where many buyers could insert price for a product that they are willing to buy, and the buyer that inserted the highest price gets the chance to buy it. However, we realized that this is a redundant feature, as multiples of the same product could be sold by a seller.




A webpage that uses interesting database operation used on this project is "My Wishlist". This page is used to display the wish list of the user, which is added from product details page. When user presses “Add to Wishlist” on product details page, in server.py, def wish_product(id) runs 

cursor = g.conn.execute(
        "SELECT * FROM product_own p WHERE p.product_id=%s",
        id
    )
, and retrieve information of the tuple with:

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

With the codes above and the following code, the product chosen is added to the user’s with list:
g.conn.execute(
            "INSERT INTO wish VALUES (%s,%s)",
            g.user.user_id,
            product.id
        )

One can see that database operation ("SELECT * FROM product_own p WHERE p.product_id=%s", id) was used in this step, to access the data of products such as id, name, etc. This was interesting because it was my first time working with coding project where I retrieve data by accessing a database with commands learned in class, not using an arbitrary input on a console. In addition, on the page “My Wishlist”, the rating of the product is updated whenever additional users contribute on the rating of the product in the list, which was fascinating.

Another interesting feature implemented was recommend. When “Recommend List” on /home is pressed, the web page /recommend shows a list of recommended products based on the wishlist of the user. 

Def recommend() uses the function get_most_wanted(), which runs:

cursor = g.conn.execute(
            "SELECT b.category_id, COUNT(*) FROM belongs_to b, wish w WHERE w.user_id=%s and w.product_id=b.product_id GROUP BY b.category_id",
            self.user_id,
        )
max_freq = 0
        for result in cursor:
            freq = int(result[1])
            if freq > max_freq:
                max_freq = freq
                category.clear()
                category.append(result[0])
            elif freq == max_freq:
                category.append(result[0])
        return category

We use database operation “COUNT(*)” , counting the total rows, where user_id of the wish equals that of self, or the current user, and product id of wish equals that of belongs_to. Category ID is selected from this. Then, we find which category shows up the most.

Knowing this information, on server.py:
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

This finds the product with rating greater than or equal to 3.5 and is displayed to the user. Recommend function is interesting because it uses the data of wishlist that was created by the user, and is processed for another round, leaving data for what we need-  finding the most frequently added category of products of a wishlist , and finding products with rating greater than or equal to 3.5 among the data creates a suitable recommendation list. We defined the condition to be “recommendable”, and found them using database operations.


