import time
import mysql.connector
from flask import Flask, request, render_template,flash

useid=0
sid=0
conn = mysql.connector.connect(
        user="root",
        password="###",
        host="127.0.0.1",
        database="stock_project",
    )

cur=conn.cursor()

app = Flask(__name__, static_folder='static', static_url_path='/static')

@app.route('/')
def form():
    return render_template("one.html")

@app.route('/register')
def form1():
    return render_template("register.html")

@app.route('/login')
def form2():
    return render_template("login.html")

@app.route('/process_form', methods=['POST'])
def process_form():
    global useid
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password=request.form['password']

       # cur = conn.cursor() 
        para=(email,name,password)
        
        cur.callproc('insert_user',para)
        conn.commit()
        
        cur.execute("SELECT LAST_INSERT_ID()")
        last_inserted_id = cur.fetchone()[0]
        useid=last_inserted_id
        print(f"The auto-incremented value (new user ID) is: {last_inserted_id}")

        #cur.close()
        #conn.close()

        return render_template('/one.html')
    
    

@app.route('/home', methods=['POST'])
def home():
    global useid
    name=request.form['name']
    u_id=int(request.form['user_id'])
    password=request.form['password']
    useid=u_id
    #cursor = conn.cursor()

    cur.execute("SELECT * FROM users WHERE user_id = %s", (u_id,))
    user = cur.fetchone()
    
    # cur.close()
    # conn.close()

    if user and user[1] == name and user[2]==password:  
        cur.execute("SELECT * FROM stocks")
        stocks = cur.fetchall()
        return render_template('home.html',stocks=stocks)
    else:
        return render_template('one.html')
        
@app.route('/buystocks',methods=['post']) 
def buy():
    print(useid)
    sid1=request.form['s_id']
    num=int(request.form['num'])
    cur.callproc('buy_stocks',(useid,sid1,num))
    conn.commit()
    cur.execute("SELECT * FROM stocks")
    stocks = cur.fetchall()
    return render_template('home.html',stocks=stocks)


@app.route('/sellstocks',methods=['post'])
def sell_stock():
    try:  
        sid1=request.form['s_id']
        num=int(request.form['num']) 

        print(sid1)
        print(num)
        cur.execute('select * from holdings where user_id=%s and stock_id=%s',(useid,sid1))
        user=cur.fetchone()
        print(user)

        if(user==None or user[1]<num):
            return render_template('error.html', message="Not enough stocks to sell!") 
            # return render_template('home.html')
        
        cur.execute("SELECT get_amount(%s);", (sid1,))
        result = cur.fetchone()

        values = (float(result[0])*num, useid, sid1, num)
        cur.callproc('history_insert',values)

        if(user[1]==num):
            cur.execute('delete from holdings where user_id=%s and stock_id=%s',(useid,sid1))
        else:
            cur.execute('update holdings set num_count=%s where user_id=%s and stock_id=%s',(int(user[1])-num,useid,sid1))

    except mysql.connector.Error as error:
        print(f"Error: {error}")

    finally:
        if user is not None and user[1] >= num:
            conn.commit()
            cur.execute("SELECT * FROM stocks")
            stocks = cur.fetchall()
            return render_template('home.html',stocks=stocks)
             

@app.route('/portfolio',methods=['post'])
def show_portfo():
    print(useid)
    cur.execute('select h.user_id,h.num_count,h.stock_id,s.price from holdings h inner join stocks s on s.stock_id=h.stock_id where h.user_id=%s',(useid,))
    stocks = cur.fetchall()
    print(stocks)
    return render_template('portfolio.html',stocks=stocks)

@app.route('/slogin',methods=['post'])
def slogin():
    global sid
    sid=int(request.form['user_id'])
    cur.execute("SELECT * FROM stock_exchange WHERE supervisior_id = %s", (sid,))
    user = cur.fetchone()
    if(user==None):
        return render_template('invalid access')
    cur.execute('select * from history order by sold_date DESC')
    stocks = cur.fetchall()
    
    return render_template('suprevisor.html',stocks=stocks)

@app.route('/blockuser',methods=['post'])
def block():
    uid=int(request.form['user_id'])
    reason=request.form['reason']
    print(uid)
    print(reason)
    print(sid)
    cur.callproc('block_user',(uid,sid,reason))    
    
    cur.execute('select * from history order by sold_date DESC')
    stocks = cur.fetchall()
    print(stocks)
    conn.commit()
    return render_template('suprevisor.html',stocks=stocks)

@app.route('/blocked',methods=['post'])
def blocked():
    cur.execute('select b.user_id,b.s_id,s.reason from block_history b inner join block_history_reason s on s.block_id=b.user_id')
    stocks = cur.fetchall()
    return render_template('block.html',stocks=stocks)

@app.route('/activity',methods=['post'])
def act():
    cur.execute('select user_id ,count(user_id) as Totaltransactions,sum(net_income) as Netincome from history h group by user_id')
    stocks = cur.fetchall()
    return render_template('activity.html',stocks=stocks)

def my_periodic_function(stock_symbols):
   

    for symbol in stock_symbols:
        price = si.get_live_price(symbol)
        price=round(price,4)
        cur.execute("UPDATE stocks SET price = %s WHERE stock_id = %s", (price, symbol))
  
    
    conn.commit()
   

if __name__ == '__main__':
    
    # interval_seconds = 10  # 1 minute
    # stock_symbols = ["GOOG", "IDEA", "AAPL", "AMZN", "LMT", "NVDA", "ADANIPORTS.NS", "PAC", "ZS"]
    # while True:
    #     my_periodic_function(stock_symbols)
    #     time.sleep(interval_seconds)
    app.run(debug=True)
    
