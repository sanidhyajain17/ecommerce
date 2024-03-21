import psycopg2

class admin:
    def __init__(self) :
        self.conn = psycopg2.connect(database='sql_demo', host='localhost', user='postgres', password='postgres', port='5432') # always check the port number
        print("Connection to database successful")
        self.curr = self.conn.cursor()
    
    def addItem(self, name, price, brand, category):
        self.curr.execute("""SELECT * FROM items WHERE
                              name=%s AND brand=%s AND category=%s""",(name, brand, category))
        res = self.curr.fetchall()
        if len(res) == 1: # item already exists
            return 0
        self.curr.execute("""INSERT INTO items(name, price, brand, category) VALUES (%s, %s, %s, %s)""",(name, int(price), brand, category))
        self.conn.commit()
        self.curr.close(); self.conn.close()
        self.curr.execute("""SELECT id FROM items WHERE name=%s AND brand=%s AND category=%s""", (name, brand, category))
        res = self.curr.fetchall()
        return res[0][1]


    def deleteItem(self, id):
        print("Inside delete item ")
        try:
            self.curr.execute("""SELECT * FROM items WHERE id=%s""", (id,))
            res = self.curr.fetchall()
            if len(res) == 0: # the item is not present in the database
                return 0
            else:
                self.curr.execute("""SELECT * FROM cart WHERE item_id=%s""", (id,)) # if the item is already present within the cart the item cannot be deleted
                res = self.curr.fetchall()
                if len(res) >0:
                    return -1
                else:
                    self.curr.execute("""DELETE FROM items WHERE id=%s""",(id,))
                    self.conn.commit()
                    return 1
        finally:
            self.curr.close(); self.conn.close()


    def addCategory(self, name):
        self.curr.execute("""SELECT * FROM categories WHERE category_name=%s""", (name,))
        res = self.curr.fetchall()
        if len(res) == 0:  # no category available 
            self.curr.execute("""INSERT INTO categories(category_name) VALUES (%s)""",(name,))
            self.conn.commit()
            return 1
        else: 
            return 0
    

    def categoryList(self):
        self.curr.execute('''SELECT category_name FROM categories''')
        res = self.curr.fetchall()
        return res
    

    def itemList(self):
        self.curr.execute('''SELECT * FROM items''')
        res = self.curr.fetchall()
        return res
    
    def userList(self):
        self.curr.execute('''SELECT * FROM admins''')
        res = self.curr.fetchall()
        return res