
import requests
from prettytable import PrettyTable
from pymongo import MongoClient, results
import psycopg2
import re

class A():
    url='https://61d042a6cd2ee50017cc9810.mockapi.io/api/project/Flights'
    con_mongo= MongoClient("mongodb://localhost:27017/")
    con_postgres=psycopg2.connect(host='localhost',database='project',user='postgres',password='admin')
    #constructor to initialize ticket count and user count
    def __init__(self):
      self.tkt_ct=self.total_tickets()
      self.user_ct=self.total_users('project','users')
    ticket=[[10]*12]*30

    #check mongo connection
    def mongo_con(self):
        if(self.con_mongo):
            return True
        else:
            return False
    
    #check postgres connection
    def postgres_con(self):
        if(self.con_postgres):
            return True
        else:
            return False
    
    #check total tickets to get new ticket id
    def total_tickets(self):
        if(self.postgres_con()):
            cur=self.con_postgres.cursor()
            sql='''Select * from ticket''';
            cur.execute(sql)
            data=cur.fetchall()
            return len(data)
    

    #check total users to get new user id
    def total_users(self,db_name,collection_name):
        res=[]
        if(self.mongo_con()):
            for data in self.con_mongo[db_name][collection_name].find():
                res.append(data)
            return(len(res))
    
    #login function to check valid user or not
    def check_existing_user(self,db_name,collection_name,user_name,password):
        res=[]
        if(self.mongo_con()):
            for data in self.con_mongo[db_name][collection_name].find({"username" : user_name, "password" :password}):
                res.append(data)
            if(len(res)==0):
                return -1
            else:
                return res[0]["id"]
    
            
    #read mockapi server and display all flight data
    def view_flights(self):
        response=requests.get(self.url)
        data=response.json()
        t = PrettyTable(['id','From','To','Price','Time','Duration'])
        for i in range(0,len(data)):
          v=list(data[i].values())
          t.add_row(v)
        print(t) 

    #check availability of ticket
    def check_ticket(self,user_name,from_city,to_city,date):
        response=requests.get(self.url)
        data=response.json()
        for i in range(0,len(data)):
           v=list(data[i].values())
           if(data[i]["From"]==from_city and data[i]["To"]==to_city):
             flight_num=int(data[i]["id"])
        if(self.ticket[date-1][flight_num-1]>0):
            return flight_num
        else:
            return -1
    
    #book ticket if available
    def book_ticket(self,user_name,from_city,to_city,date,flight_num):
            if(self.postgres_con()):
              cur=self.con_postgres.cursor()
              sql='''INSERT INTO ticket values({},'{}','{}','{}',{},{});'''.format(self.tkt_ct+1,user_name,from_city,to_city,date,"1")
              cur.execute(sql)
              self.con_postgres.commit()
              print("Ticket booked")
              self.ticket[date-1][flight_num-1]-=1
              self.tkt_ct+=1
    
    #view all tickets booked by user
    def view_ticket(self,username):
        if(self.postgres_con()):
            cur=self.con_postgres.cursor()
            sql='''Select * from ticket where username='{}';'''.format(username)
            cur.execute(sql)
            data=cur.fetchall()
            t = PrettyTable(['id', 'username','from_city','to_city','date','status'])
            for data in data:
             t.add_row(data)
            print("1.Status->booked 0.Status->Cancelled")
            print(t)
            
    #view all active tickets of user
    def view_ticket_active(self,username):
        if(self.postgres_con()):
            cur=self.con_postgres.cursor()
            sql='''Select * from ticket where username='{}';'''.format(username)
            cur.execute(sql)
            data=cur.fetchall()
            t = PrettyTable(['id', 'username','from_city','to_city','date','status'])
            for data in data:
             if(data[5]=="1"):
              t.add_row(data)
            print(t)
                    
    #cancel ticket booked by user
    def cancel_ticket(self,bid):
       if (self.postgres_con()):
            cur=self.con_postgres.cursor()
            sql='''Select * from ticket where id={};'''.format(bid)
            cur.execute(sql)
            data=cur.fetchall()
            date=data[0][4]
            from_city=data[0][2]
            to_city=data[0][3]
            response=requests.get(self.url)
            data=response.json()
            for i in range(0,len(data)):
              v=list(data[i].values())
              if(data[i]["From"]==from_city and data[i]["To"]==to_city):
                flight_num=int(data[i]["id"])
                break;
            self.ticket[date-1][flight_num-1]+=1
            sql='''update ticket set status='{}' WHERE id={}'''.format("0",bid)
            cur.execute(sql)
            self.con_postgres.commit()
            print("Ticket Cancelled")   
    
      
    #function to register new user
    def register_user(self,db_name,collection_name,user_name,password,phoneno,pan,age):
        if self.mongo_con:
            data = {'id': self.user_ct+1, 'username': user_name, 'password': password,
                    'phoneno': phoneno, 'pan': pan,'age':age}
            self.con_mongo[db_name][collection_name].insert_one(data)
            print("User registered")
            self.user_ct+=1
    
    #pan regex matching function   
    def verify_pan(self,pan):
        PAN= r'^[A-Z]{5}[0-9]{4}[A-Z]'  
        res=re.match(PAN,pan)
        if(res):
            return True
        else:
            return False
    
    #phonenumber matching function 
    def verify_phoneno(self,phoneno):
        PN= r'^[98765][0-9]{9}'  
        res=re.match(PN,phoneno)
        if(res):
            return True
        else:
            return False
    
a=A()
ans=1
while(ans!=0):
    print("="*100)
    print("="*100)
    print("Welcome to the airline system".upper())
    print("="*100)
    print("="*100)
    print()
    print("1.Existing user")
    print("2.New user")
    print("3.Exit")
    o=int(input())
    print()
    if(o==1):
        print("Enter username:")
        user_name=input()
        print("Enter password:")
        password=input()
        user_id=a.check_existing_user("project","users",user_name,password)     
        if(user_id==-1):
            print("wrong user credentials") 
            continue
        else:
            print("Welcome,{}".format(user_name))
            u=1
            while u!=0:
             print()
             print("1.View all flights")
             print("2.Book ticket")
             print("3.View ticket")
             print("4.Cancel ticket")
             print("5.Exit")
             op=int(input())
             print()
             city=["Chennai","Mumbai","Madurai","Bangalore"]
             if(op==1):
                a.view_flights()

             elif(op==2):
                print("Enter source city:")
                print("1:Chennai")
                print("2:Mumbai")
                print("3:Madurai")
                print("4:Bangalore")
                ops=int(input())
                from_city=city[ops-1]
                print("Enter destination city:")
                print("1:Chennai")
                print("2:Mumbai")
                print("3:Madurai")
                print("4:Bangalore")
                opd=int(input())
                to_city=city[opd-1]
                print("enter date:")
                date=int(input())
                print("Checking availability")
                flight_num=a.check_ticket(user_name,from_city,to_city,date)
                if(flight_num==-1):
                    print("Ticket unavailable")
                else:
                    print("Ticket available")
                    a.book_ticket(user_name,from_city,to_city,date,flight_num)
             elif(op==3):
                print("All TICKETS BOOKED BY YOU")
                a.view_ticket(user_name)
             elif(op==4):
                print("All ACTIVE TICKETS BOOKED BY YOU")
                a.view_ticket_active(user_name)
                print("Enter id")
                bid=int(input())
                a.cancel_ticket(bid)
             elif(op==5):
               print("good bye")
               u=0
    
    if(o==2):
       print()
       print("Welcome new user")
       print("Registering you into the system")
       print("Enter user_name:")
       user_name=input()
       print("Enter password:")
       password=input()
       print("Enter phone_number")
       #print("Enter phone_number")
       f=1
       while(f!=0):
         phoneno=input()  
         if(a.verify_phoneno(phoneno)==True):
            f=0
            break
         else: 
            print("phone number format incorrect:Enter correct Phone number!!!!")
       print("Enter PAN:")
       f=1
       while(f!=0):
         pan=input()  
         if(a.verify_pan(pan)==True):
           f=0
           break
         else: 
           print("PAN number format incorrect:Enter correct Phone number!!!!")
           
       print("Enter age:")
       age=int(input())
       a.register_user('project','users',user_name,password,phoneno,pan,age)
       print("Back to login module!!!!!!!!!!!")

    if(o==3):
      ans=0
      print("Goodbye!!!!")   

