from flask import *
import pymysql

app = Flask( __name__ )

app.secret_key ='__No Secret__'

# Establish connection to MySQL database
db = pymysql.connect(host="localhost", 
                   port = 3306,
                   user="root", 
                   password="", 
                   database="fin-tracker", 
                   charset="utf8mb4", 
                   cursorclass=pymysql.cursors.DictCursor
)


@app.route('/', methods=['POST','GET'])
def login():
    if request.method=='POST':
        email= request.form.get('email')
        customer_password= request.form.get('customer_password')


        try:    

            if aunthenticate_customer(email, customer_password):
                print('login successful')
                session['email']=email
                return redirect(url_for('dashboard'))
       
        except Exception as e: 
            print(e)
            flash(e)
            
            return render_template('login.html')
        
    
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    email= request.form.get('email')
    first_name = request.form.get('first_name')
    last_name= request.form.get('last_name')
    customer_password= request.form.get('customer_password')

    if request.method == 'POST':

        try:
            if customer_exists(email):
                flash("Email exists! Please log IN")
                print("Email exists! Please log IN")

            cursor=db.cursor()
            query="INSERT INTO CUSTOMER VALUES(%s,%s,%s,%s)"

            cursor.execute(query, (email,first_name,last_name,customer_password))

            session['email']=email

            return redirect(url_for('dashboard'))
        
        except Exception as e:
            print(e)
            flash(e)
            return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        print("Please login")
        flash("Please Log In")
        return redirect(url_for('login'))
    
    email=session['email']

    cursor_greeting= db.cursor()
    cursor_balance= db.cursor()
    cursor_month_income = db.cursor()
    cursor_month_expenses = db.cursor()


    query_greeting="SELECT first_name FROM CUSTOMER WHERE email=%s"
    query_balance="SELECT((SELECT COALESCE(sum(income),0) FROM INCOME WHERE email=%s)-(SELECT COALESCE(sum(cost),0) FROM EXPENSES WHERE email=%s)) as difference"
    query_month_income="SELECT COALESCE(sum(income),0) as income_month FROM INCOME WHERE email=%s and MONTH(date_time)= MONTH(CURDATE()) and YEAR(date_time)=YEAR(CURDATE())"
    query_month_expenses="SELECT COALESCE(sum(cost),0) as expenses_month FROM EXPENSES WHERE email=%s and MONTH(date_time)= MONTH(CURDATE()) and YEAR(date_time)=YEAR(CURDATE())"

    cursor_greeting.execute(query_greeting, email)
    cursor_balance.execute(query_balance,(email,email))
    cursor_month_income.execute(query_month_income,email)
    cursor_month_expenses.execute(query_month_expenses,email)


    customer_greeting_dict= cursor_greeting.fetchone()
    customer_balance_dict=cursor_balance.fetchone()
    customer_month_income_dict = cursor_month_income.fetchone()
    customer_month_expenses_dict= cursor_month_expenses.fetchone()

    print(customer_month_expenses_dict)
    



    
     
    return render_template('dashboard.html', greeting=customer_greeting_dict, balance=customer_balance_dict,
                           month_income=customer_month_income_dict, month_expenses=customer_month_expenses_dict)

@app.route('/transaction')
def transaction():
    return render_template('transaction.html')


def customer_exists(email):
    cursor= db.cursor()

    query= "SELECT * FROM CUSTOMER WHERE email=%s"

    cursor.execute(query, email)

    customer = cursor.fetchall()

    if customer:
        return True
    
    return False

def aunthenticate_customer(email, password):
    if not customer_exists(email):
        print('customer no exist')
        flash('customer no exist')
        return False

    cursor= db.cursor()
    query="SELECT email,customer_password FROM CUSTOMER WHERE email=%s"

    cursor.execute(query, email)

    customer_dict= cursor.fetchone()
    
    if customer_dict['customer_password'] == password:
        return True
    
    return False

@app.route('/logout')
def logout():
    del session['email']

    return redirect(url_for('login'))









if __name__ == '__main__':
    app.run('0.0.0.0', debug= True)