# Crypto Sentiment Analysis 

Welcome! 

This is a project to measure and analyze how various social media / news sites correspond with market fluctuations for crypto currency.

The main purpose of this project is:

1) Create a useful application for those interested in cryptocurrency

2) Get hands on experience with various tools/technology I'm interested in.

I've broken up the project into two repositories, one holds the frontend code for the web applicaiton, the other holds the backend code. 

Frontend: https://github.com/vantaka2/crypto_sentiment_analysis-

Backend: https://github.com/vantaka2/crypto_dash_app

Here is a link to the current state of the web app: 
https://crypto-sentiment-keerthan.herokuapp.com/ 

(Please keep in mind this is running on heroku's free tier. In Heroku's free tier applications are put to sleep if no one uses it for 30 minutes, so the first person to check it out after its put to sleep will have a to wait a minute or two for the app to start up again.)

## Frontend

### Framework

I've chosen to create the frontend using Plotly Dash. Plotly Dash is a python framework for building analytical web applications without javascript. 

Check out the project here: 

https://github.com/plotly/dash/

https://plot.ly/products/dash/

### Hosting

The application is currently being hosted on Heroku. For the time being I am using the free tier until the application is in a better state or there is increased interest in it. Some options moving forward are to move it to Heroku's Standard plan or have it run on the AWS server that I am already paying for to do the backend work.  

You can find the application here: 
https://crypto-sentiment-keerthan.herokuapp.com/ 

### Design: 

I am not a UI/UX person, if you have feedback on how the design of the application can be improved please let me know via github issues!

For now I've chosen the color scheme after a quick google on what color combinations to use for dashboards. 

Source: https://aesalazar.com/blog/3-professional-color-combinations-for-dashboards-or-mobile-bi-applications/

HEX color codes used: #F1F1F1, #202020, #7E909A, #1C4E80, #A5D8DD, #EA6A47, #0091D5

## Backend

### Server 

The backend processes are running on 2 AWS servers. 

1 m5.large & 1 t2.micro. 

The m5.large is running apache airflow and is preforming the ETL processing from various data sources. 

The t2.micro is hosting a postgres database

### Tools/Tech

#### Apache Airflow

Airflow is a platform to programmatically author, schedule, and monitor workflows. 

Check out airflow at : https://github.com/apache/incubator-airflow

#### PostgreSQL

I'm using PostgreSQL as my database. 

Version: postgreSQL 9.5.3 

https://www.postgresql.org/

### DATA

#### Coinmarketcap

I'm using the coinmarketcap API to obtain data on the current price & market cap of all the coins. They have a awesome API, check it out! 

https://coinmarketcap.com/api/

#### reddit

I'm using the praw library to access the reddit API. 

Check out Praw here: https://github.com/praw-dev/praw

Info on reddit's API: https://www.reddit.com/dev/api/

