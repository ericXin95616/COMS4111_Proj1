# COMS4111_Proj1
Project 1 for COMS 4111
BoChao Xin
ChangSu Nam

PostgreSQL account: 
bx2196


URL address of our web application:
http://35.237.109.152:8111/


We implemented everything specified in proposal of this project, except the bidding system, and recommendation system.

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

Another interesting feature implemented was

