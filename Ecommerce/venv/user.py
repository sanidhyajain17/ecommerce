import psycopg2

class user:
    def __init__(self, userName) -> None:
        self.conn = psycopg2.connect(database='sql_demo', host='localhost', user='postgres', password='postgres', port='5432') # always check the port number
        print("Connection to database successful")
        self.curr = self.conn.cursor()
        self.curr.execute("""SELECT id FROM admins WHERE username=%s""", (userName,))
        self.userId = self.curr.fetchall()[0] #user id 
    

    def addToCart(self, itemId, quantity):
        self.curr.execute("""SELECT * FROM cart 
                          WHERE item_id=%s AND user_id=%s""",(itemId, self.userId))
        res = self.curr.fetchall()
        if len(res) == 1:
            self.curr.execute("""UPDATE cart SET quantity=%s WHERE item_id=%s AND user_id=%s""",(quantity, itemId, self.userId))
            self.conn.commit()
            return 2
        else:
            self.curr.execute("""INSERT INTO cart(item_id, user_id, quantity) VALUES(%s, %s, %s)""", (itemId, self.userId, quantity))
            self.conn.commit()
        self.curr.close(); self.conn.commit()
        return 1
    
    def cartList(self):
        self.curr.execute("""SELECT item_id, quantity FROM cart WHERE user_id=%s""", (self.userId,))
        res = self.curr.fetchall()
        returnList = []
        if len(res) >= 1:
            for id in res:
                self.curr.execute("""SELECT * FROM items WHERE id=%s""", (id[0],))
                r = list(self.curr.fetchone()) 
                r.append(id[1])
                returnList.append(r)
            return returnList
        else:
            return returnList
    

    def totalPayment(self):
        self.curr.execute("""SELECT item_id,quantity FROM cart WHERE user_id=%s""", (self.userId,))
        res = self.curr.fetchall()
        total = 0
        for r in res:
            self.curr.execute("""SELECT price FROM items WHERE id=%s""", (r[0],))
            price = self.curr.fetchone()
            total += price[0] * r[1] # multiplying by the quantity
        return total
    
    def displayItems(self):
        self.curr.execute("""SELECT name, price, category, description FROM items""")
        res = self.curr.fetchall()
        return res
    
    def updateQuantity(self, quantity, itemId):
        self.curr.execute("""UPDATE cart SET quantity=%s WHERE item_id=%s AND user_id=%s""", (quantity, itemId, self.userId))
        self.conn.commit()
        self.curr.close(); self.conn.close()
        return 1
    
    def clearCart(self):
        self.curr.execute("""DELETE FROM cart WHERE user_id=%s""", (self.userId))
        self.conn.commit()
        self.curr.close(); self.conn.commit()
        return 1

    def deleteItem(self, itemId):
        self.curr.execute("""DELETE FROM cart WHERE item_id=%s AND user_id=%s""", (itemId, self.userId))
        self.conn.commit()
        self.curr.close(); self.conn.close()
        return 1