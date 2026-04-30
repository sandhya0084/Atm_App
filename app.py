from flask import Flask, render_template, request
import pymysql

app = Flask(__name__)

db_config = {
    "host":"localhost",
    "user":"root",
    "password":"root",
    "database":"atm"
}
def db_init():
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS USERS
        (
         acc_no VARCHAR(15) PRIMARY KEY,  
         name VARCHAR(20) NOT NULL,
         balance INT NOT NULL
        )
        '''
    )
    cursor.close()
    conn.close()
    

db_init()

@app.route('/')
def home():
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT * FROM USERS
        '''
    )
    users = cursor.fetchall()
    accounts = {}
    for i in users:
        accounts[i[0]] = {'name':i[1], 'balance':i[2]}
        
    return render_template('home.html', accounts = accounts)

@app.route('/create', methods = ['POST', 'GET'])
def create():
    
    if request.method == 'POST':
        acc_no = request.form.get('acc_no')
        balance = int(request.form.get('balance'))
        name = request.form.get('name')
        
        if len(acc_no) <= 13 and len(acc_no) >= 10:
            #accounts[acc_no] = {'name':name, 'balance':balance}
            conn = pymysql.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO USERS
                VALUES
                (%s, %s, %s)''', (acc_no,name, balance)
                
            )
            conn.commit()
            cursor.close()
            conn.close()
            msg = "Account created"
            msg_type = 'success'
        
        else:
            msg = "Invalid Account number"
            msg_type = 'error'
            
        return render_template('create.html', message = msg, msg_type = msg_type )
    
    return render_template('create.html')
    
@app.route('/balance', methods = ['GET', 'POST'])
def balance():
    if request.method == 'POST':
        acc_no = request.form.get('acc_no')
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            '''
                SELECT balance, name FROM USERS
                WHERE acc_no = %s
            ''', (acc_no,)
        )
        accounts = cursor.fetchone()#tuple, None
        cursor.close()
        conn.close()
        
        if accounts:
            #account = accounts[acc_no]
            bal, name = accounts
            account = {'name':name, 'balance': bal}
            return render_template('balance.html', account = account)
        else:
            msg = "Account does not exist"
            msg_type = 'error'
            return render_template('balance.html', message = msg, msg_type = msg_type)
    return render_template('balance.html')
 
@app.route('/update', methods = ['GET', 'POST'])  
def update():
    if request.method == 'POST':
        acc_no = request.form.get('acc_no')
        amount = int(request.form.get('amount'))
        action = request.form.get('action')
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            '''
                SELECT balance, name FROM USERS
                WHERE acc_no = %s
            ''', (acc_no,)
        )
        accounts = cursor.fetchone()#tuple, None    
        if accounts:
            if action == 'deposit':
                cursor.execute(
                    '''UPDATE USERS
                    SET balance = balance + %s
                    WHERE acc_no = %s
                    ''', (amount, acc_no)
                )
                msg = "Amount deposited"
                msg_type = 'success'               
            if action == 'withdraw':
                cursor.execute(
                    '''UPDATE USERS
                    SET balance = balance - %s
                    WHERE acc_no = %s
                    ''', (amount, acc_no)
                )
                msg = "Amount withdrawn"
                msg_type = 'success'            
        else:
            msg = "Account does not exist"
            msg_type = 'error' 
        conn.commit()   
        cursor.close()
        conn.close()       
        return render_template('update.html', msg = msg, msg_type = msg_type)    
    return render_template('update.html')

@app.route('/delete', methods = ['GET', 'POST'])  
def delete():
    if request.method == 'POST':
        acc_no = request.form.get('acc_no')
        
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            '''
                SELECT balance, name FROM USERS
                WHERE acc_no = %s
            ''', (acc_no,)
        )
        accounts = cursor.fetchone()#tuple, None    
        if accounts:
            cursor.execute(
                '''DELETE FROM USERS
                WHERE acc_no = %s
                ''', (acc_no,)
            )
            cursor.close()
            conn.close()
            msg = "Account deleted successfully"
            msg_type = 'success'               
        else:
            msg = "Account does not exist"
            msg_type = 'error'        
        return render_template('delete.html', msg = msg, msg_type = msg_type)       
    return render_template('delete.html')  

if __name__ == '__main__':
    app.run(debug = True, port = 5007)
    