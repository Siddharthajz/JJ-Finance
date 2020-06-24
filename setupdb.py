import mysql.connector

mydb = mysql.connector.connect(host="localhost", user="root", passwd="root", database="jjfinance", port=3306)
crsr=mydb.cursor()

crsr.execute("Drop table Portfolio")
crsr.execute("Drop table History")
crsr.execute("Drop table Watchlist")
crsr.execute("Drop table Users")

crsr.execute("Create table Users \
(Id int(10) primary key not null auto_increment, \
Username varchar(94) not null, \
Password varchar(94) not null, \
Cash int(11) DEFAULT '600000')")

crsr.execute("Create table Portfolio \
(Id int(10) primary key not null auto_increment, \
Symbol varchar(94) not null, \
Shares int not null, \
UserId int(10) not null, \
foreign key(UserId) references Users(Id))")

crsr.execute("Create table History( \
Id int(10) primary key not null auto_increment, \
Symbol varchar(94) not null, \
Shares int(10) not null, \
Price int(11) not null, \
Date_Time TIMESTAMP NOT NULL, \
UserId int(10) not null, \
foreign key(UserId) references Users(Id))")

crsr.execute("Create table WatchList( \
Id int(10) primary key not null auto_increment, \
Symbol varchar(94) not null, \
UserId int(10) not null, \
foreign key(UserId) references Users(Id))")

mydb.close()




''' 
Portfolio
    symbol
    number of shares
    current value of 1 stock
    how much money paid when stocks bought
    gain/loss [(numberofshares X current value of 1 stock)-{(how much money paid)]<- this we get from history table}
    total value (numberofshares X current value of 1 stock)

HISTORY
    
'''