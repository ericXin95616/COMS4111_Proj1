from flask import g


class Users:
    def __str__(self):
        return self.firstname + " " + self.lastname

    def __init__(self, id):
        self.user_id = id
        cursor = g.conn.execute(
            "SELECT u.first_name, u.last_name, u.username, s.obj_id FROM users u, sellers s WHERE u.user_id=(%s) and u.user_id=s.user_id",
            self.user_id,
        )
        for result in cursor:
            self.firstname = result[0]
            self.lastname = result[1]
            self.username = result[2]
            self.obj_id = result[3]

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
    
    def get_most_wanted(self):
        category= []
        #get the most added category(ies) in wishlist
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

    def get_rating(self):
        cursor = g.conn.execute(
            "SELECT AVG(c.rating) FROM sellers s, comment_obj o, comments_created_at_written_for c WHERE s.obj_id=(%s) and s.obj_id = o.obj_id AND c.obj_id = o.obj_id GROUP BY s.user_id",
            self.obj_id,
        )
        rating = 0.0
        for result in cursor:
            rating = float("{:.1f}".format(float(result[0])))
        return rating

    def get_comments(self):
        cursor = g.conn.execute(
            "SELECT c.comment_id FROM comments_created_at_written_for c WHERE c.obj_id = %s",
            self.obj_id,
        )
        comments = []
        for result in cursor:
            comments.append(Comment(result[0]))
        return comments


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

    def get_comments(self):
        cursor = g.conn.execute(
            "SELECT c.comment_id FROM comments_created_at_written_for c WHERE c.obj_id = %s",
            self.comment_obj,
        )
        comments = []
        for result in cursor:
            comments.append(Comment(result[0]))
        return comments


class Comment:
    def __str__(self):
        return self.content

    def __init__(self, id):
        self.id = id
        cursor = g.conn.execute(
            "SELECT * FROM comments_created_at_written_for c WHERE c.comment_id = %s",
            self.id,
        )
        for result in cursor:
            self.rating = result[1]
            self.content = result[2]
            self.author = Users(result[3])
            self.created_at = result[4]
            self.obj_id = result[5]
