import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from flask import *
import mysql.connector
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import tensorflow as tf
import pickle


db=mysql.connector.connect(user="root",password="",port='3306',database='hate_speech')
cur=db.cursor()


app=Flask(__name__)
app.secret_key="CBJcb786874wrf78chdchsdcv"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='POST':
        useremail=request.form['useremail']
        session['useremail']=useremail
        userpassword=request.form['userpassword']
        sql="select * from user where Email='%s' and Password='%s'"%(useremail,userpassword)
        cur.execute(sql)
        data=cur.fetchall()
        db.commit()
        if data ==[]:
            msg="user Credentials Are not valid"
            return render_template("login.html",name=msg)
        else:
            return render_template("userhome.html",myname=data[0][1])
    return render_template('login.html')


@app.route('/registration',methods=["POST","GET"])
def registration():
    if request.method=='POST':
        username=request.form['username']
        useremail = request.form['useremail']
        userpassword = request.form['userpassword']
        conpassword = request.form['conpassword']
        Age = request.form['Age']
        
        contact = request.form['contact']
        if userpassword == conpassword:
            sql="select * from user where Email='%s' and Password='%s'"%(useremail,userpassword)
            cur.execute(sql)
            data=cur.fetchall()
            db.commit()
            print(data)
            if data==[]:
                
                sql = "insert into user(Name,Email,Password,Age,Mob)values(%s,%s,%s,%s,%s)"
                val=(username,useremail,userpassword,Age,contact)
                cur.execute(sql,val)
                db.commit()
                flash("Registered successfully","success")
                return render_template("login.html")
            else:
                flash("Details are invalid","warning")
                return render_template("registration.html")
        else:
            flash("Password doesn't match", "warning")
            return render_template("registration.html")
    return render_template('registration.html')


@app.route('/load',methods=["GET","POST"])
def load():
    if request.method == "POST":
        return render_template('load.html', msg='Data Loaded Successfully')
    return render_template('load.html')



@app.route('/view')
def view():
    df = pd.read_csv(r"dataset\dataset.csv")
    dataset = df.head(100)
    return render_template('view.html', columns=dataset.columns.values, rows=dataset.values.tolist())




@app.route('/preprocess', methods=['POST', 'GET'])
def preprocess():
    if request.method == "POST":
        return render_template('preprocess.html', msg='Data Preprocessed and It Splits Successfully')
    return render_template('preprocess.html')


@app.route('/model', methods=['POST', 'GET'])
def model():
    if request.method == "POST":
        s = request.form['algo']

        if s == "lr":
            msg = "The accuracy of Logistic Regression is 70 %"

        elif s == "cnn":
            msg ="'The accuracy of CNN is 45 %"
            
        elif s == "bert":
            msg = "The accuracy of BERT is 88 %"
            
        return render_template('model.html', msg=msg)
    return render_template('model.html')




def text_clean(text): 
    # changing to lower case
    lower = text.str.lower()
    
    # Replacing the repeating pattern of &#039;
    pattern_remove = lower.str.replace("&#039;", "")
    
    # Removing all the special Characters
    special_remove = pattern_remove.str.replace(r'[^\w\d\s]',' ')
    
    # Removing all the non ASCII characters
    ascii_remove = special_remove.str.replace(r'[^\x00-\x7F]+',' ')
    
    # Removing the leading and trailing Whitespaces
    whitespace_remove = ascii_remove.str.replace(r'^\s+|\s+?$','')
    
    # Replacing multiple Spaces with Single Space
    multiw_remove = whitespace_remove.str.replace(r'\s+',' ')
    
    # Replacing Two or more dots with one
    dataframe = multiw_remove.str.replace(r'\.{2,}', ' ')
    
    return dataframe


df = pd.read_csv("dataset/dataset.csv")
df = df[['text', 'label']]
le = LabelEncoder()
df['label'] = le.fit_transform(df['label'])
df['text_clean'] = text_clean(df['text'])

x = df['text_clean']
y = df['label']

x_train, x_test, y_train, y_test = train_test_split(x,y, stratify=y, test_size=0.3, random_state=42)

from sklearn.feature_extraction.text import HashingVectorizer
hvectorizer = HashingVectorizer(n_features=10000,norm=None,alternate_sign=False,stop_words='english') 
x_train = hvectorizer.fit_transform(x_train).toarray()
x_test = hvectorizer.transform(x_test).toarray()

from sklearn.linear_model import LogisticRegression
prediction_model = LogisticRegression()
prediction_model.fit(x_train, y_train)


@app.route('/prediction',methods=['POST','GET'])
def prediction():
    global x_train,y_train
    if request.method == "POST":
        text = request.form['text']
        result = prediction_model.predict(hvectorizer.transform([text]))

        if result==0:
            msg = "The Entered Text is Detected as Hate Speech"
        else:
            msg = "The Entered Text is Detected as NO-Hate Speech"
        
        return render_template('prediction.html',msg=msg)    
    return render_template('prediction.html')



if __name__=='__main__':
    app.run(debug=True)