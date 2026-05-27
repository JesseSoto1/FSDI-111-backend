from flask import Flask, jsonify, request, render_template
import sqlite3
from datetime import date

app = Flask(__name__) #create Flask instance




DB_NAME = "budget_manager.db"




def init_db():
    connection = sqlite3.connect(DB_NAME)# this is step number one to open a connection to the D.B "budget_manager.db"
    cursor = connection.cursor()# creates a cursor/tool that lets you send commands(SELEC, INSERT, ...) to the D.B.

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT NOT NULL,
            amount INTEGER NOT NULL,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    connection.commit()#Saves changes to the D.B.
    connection.close()  #Closes the connection to th D.B

# http://127.0.0.1:5000/api/health
@app.get("/api/health")
def health_check():
    return jsonify({
        "status":"OK"
}), 200


# ----users-----
# http://127.0.0.1:5000/api/users
@app.post("/api/users")
def register():
    new_user = request.get_json()
    print(new_user)

    username = new_user["username"]
    password = new_user["password"]

    connection = sqlite3.connect(DB_NAME)#open connection to DB
    cursor = connection.cursor()# create cursor/tool SQL keywords

    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))

    connection.commit()#saves changes
    connection.close()#closes the connection to DB

    return jsonify({
        "success":True,
        "message":"User created successfully"
    }), 201




# GET http://127.0.0.1:5000/api/users
@app.get("/api/users")
def get_users():
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(" SELECT * FROM users")
    rows = cursor.fetchall()
    print(rows)
    connection.close()


    users = []
    for row in rows:
        print(dict(row))
        users.append(dict(row))


    return jsonify({
        "success":True,
        "message":"Users retrieved successfully",
        "data":users
    })


# GET http://127.0.0.1:5000/api/users/2
@app.get("/api/users/<int:user_id>")
def get_user_by_id(user_id):
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()

    if not row:
        return jsonify({
            "success":False,
            "message":"User not found"
        }), 404

    print(f"row + {row}")
    user_info = dict(row)
    connection.close()

    

    return jsonify({
        "success":True,
        "message":"User Retrieved successfully",
        "data": user_info
    }), 200




# UPDATE http://127.0.0.1:5000/api/users
@app.put("/api/users/<int:user_id>")
def update_user_by_id(user_id):
    updated_user = request.get_json()
    username = updated_user["username"]
    password = updated_user["password"]

    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()

    if not row:
        return jsonify({
            "success":False,
            "message":"User not found"
        }), 404


    cursor.execute("UPDATE users SET username = ?, password = ? WHERE id = ?", (username, password, user_id))
    connection.commit()
    connection.close()

    return jsonify ({
        "success":True,
        "message":"User updated succesfully"
    }), 200

# DELETE http://127.0.0.1:5000/api/users/2
@app.delete("/api/users/<int:user_id>")
def delete_user_by_id(user_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()

    if not row:
        return jsonify({
            "success":False,
            "message":"User not found"
        }), 404
    
    cursor.execute("DELETE FROM users WHERE id = ?",(user_id,))
    connection.commit()
    connection.close()


    return jsonify({
        "success":True,
        "message":"User deleted succesfully"
    }), 200




# ----expenses----
# POST http://127.0.0.1:5000/api/expenses
@app.post("/api/expenses")
def create_expense():
    new_expense = request.get_json()
    print(new_expense)

    title = new_expense.get("title", "")
    description = new_expense.get("description", "")
    amount = new_expense.get("amount", 1)
    date_expense = new_expense.get("date", date.today())
    category = new_expense.get("category", "")
    user_id = new_expense.get("user_id", 2)


    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO expenses (title, description, amount, date, category, user_id)
        VALUES (?,?,?,?,?,?)""", (title, description, amount, date_expense, category, user_id))
    connection.commit()
    connection.close()



    return jsonify({
        "success":True,
        "message":"Expense created successfully"
    }),201




# GET http://127.0.0.1:5000/api/expenses
@app.get("/api/expenses")
def get_expenses():

    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row #######Allows columns values to be retreived by title,row["title"]
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    print(f"expenses{rows}")


    expenses = []
    for row in rows:
        print(f"row = {dict(row)}")
        expenses.append(dict(row))



    return jsonify({
        "success":True,
        "message":"Expenses retrieved succesfully",
        "data":expenses
    }), 200




# GET http://127.0.0.1:5000/api/expenses
@app.get("/api/expenses/<int:expense_id>")
def get_expenses_by_id(expense_id):
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM expenses WHERE id = ?",(expense_id,))
    row = cursor.fetchone()

    if not row:
        return jsonify({
            "success": False,
            "message":"Expense not found"
        }), 404


    print(f"row = {row}")
    expense = dict(row)



    return jsonify({
        "success": True,
        "message":"Expense retrieved successfully",
        "data":expense
    }), 200




# UPDATE
@app.put("/api/expenses/<int:expense_id>")
def update_expense_by_id(expense_id):

    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM expenses WHERE id=?", (expense_id,))
    expense = cursor.fetchone()

    if not expense:
        return jsonify({
            "success": False,
            "message": "Expense not found"
        })

    print(dict(expense))
    print(expense["title"])

    updated_expense = request.get_json()
    print(f".... {updated_expense.get("title", "test")}")

    title = updated_expense.get("title", expense["title"])
    description = updated_expense.get("description", expense["description"])
    amount = updated_expense.get("amount", expense["amount"])
    date_value = updated_expense.get("date", date.today())
    category = updated_expense.get("category", expense["category"])
    user_id = updated_expense.get("user_id", expense["user_id"])
    # description = updated_expense["description"]
    # # amount = updated_expense["amount"]
    # # date = updated_expense["date"]
    # # category = updated_expense["category"]
    # # user_id = updated_expense["user_id"]

    cursor.execute("UPDATE expenses SET title=?, description=?, amount=?, date=?, category=?, user_id=? WHERE id = ?", (title, description, amount, date_value, category,  user_id, expense_id))
    connection.commit()
    connection.close()

    return jsonify ({
        "success":True,
        "message":"User updated succesfully"
    }), 200




# DELETE http://127.0.0.1:5000/api/expenses
@app.delete("/api/expenses/<int:expense_id>")
def delete_expense_by_id(expense_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM expenses WHERE id = ?", (expense_id,))
    row = cursor.fetchone()

    if not row:
        return jsonify({
            "success":False,
            "message":"Expense not found"
        }), 404
    
    cursor.execute("DELETE FROM expenses WHERE id = ?",(expense_id,))
    connection.commit()
    connection.close()


    return jsonify({
        "success":True,
        "message":"Expense deleted succesfully"
    }), 200




##################### FRONT END ########################
@app.get("/")
@app.get("/home")
@app.get("/index")
def home():
    return render_template("home.html")




@app.get("/about")
def about():
    student_data = {
        "name":"Jesse",
        "cohort":"66",
        "year": 2026
    }
    return render_template("about.html",student = student_data)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)