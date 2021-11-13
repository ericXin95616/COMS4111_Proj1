from flask import g


class Users:
    def __str__(self):
        return self.firstname + " " + self.lastname

    def __init__(self, id):
        self.user_id = id
        cursor = g.conn.execute(
            "SELECT first_name, last_name, username FROM users u WHERE u.user_id=(%s)",
            self.user_id,
        )
        for result in cursor:
            self.firstname = result[0]
            self.lastname = result[1]
            self.username = result[2]

    def get_wishlist(self):
        products = []
        cursor = g.conn.execute(
            "SELECT * FROM product_own p, wish w WHERE w.user_id=(%s) and w.product_id=p.product_id",
            self.user_id,
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
        return products

    def get_orders(self):
        products = []
        cursor = g.conn.execute(
            "SELECT * FROM product_own p, buy b WHERE b.user_id=(%s) and b.product_id=p.product_id",
            self.user_id,
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
        return products


class Products:
    def __str__(self):
        return self.name

    def __init__(self, id, name, price, description, owner, comment_obj):
        self.id = id
        self.name = name
        self.price = price
        self.description = description
        self.owner = owner
        self.comment_obj = comment_obj
        cursor = g.conn.execute(
            "SELECT b.category_id FROM product_own p, belongs_to b WHERE p.product_id=b.product_id and p.product_id=(%s)",
            self.id,
        )
        self.categories = []
        for result in cursor:
            self.categories.append(result[0])

    def get_rating(self):
        cursor = g.conn.execute(
            "SELECT AVG(c.rating) FROM product_own p, comment_obj o, comments_created_at_written_for c WHERE p.obj_id=(%s) and p.obj_id = o.obj_id AND c.obj_id = o.obj_id GROUP BY p.product_id",
            self.comment_obj,
        )
        rating = 0.0
        for result in cursor:
            rating = float("{:.1f}".format(float(result[0])))
        return rating
