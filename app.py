import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
import os
import plotly.graph_objs as go

app = dash.Dash(__name__)
server = app.server

## bootstamp CSS (From https://github.com/amyoshino/DASH_Tutorial_ARGO_Labs/blob/master/app.py)
app.css.append_css(
    {'external_url':'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})
sql_con = os.environ.get('pg_db')
print("set sql_con")

def reddit_post_info(pg_conn = sql_con):
    sql = """
        Select 
            post_id, 
            created, 
            title, 
            sentiment, 
            confidence, 
            coin_name
        From 
            coin.reddit_post_info """
    df = pd.read_sql(sql,pg_conn)
    return df

## get market cap data frame
def market_cap_df(pg_conn=sql_con):
    """Returns the dataframe used for marketcap graphs"""
    sql = """
    Select a.name as coin_name,market_cap_usd, insert_timestamp, ((market_cap_usd - base_7day)/base_7day)* 100 as pct_change_7d,((market_cap_usd-base_24H)/base_24H)* 100 as pct_change_L24H   
    from  coin.mc_graph_data a
    inner join coin.pct_change_base b
    on a.name= b.name
    """
    df = pd.read_sql(sql, pg_conn)
    return df

def reddit_trends_df(pg_conn=sql_con):
    "queries database for reddit post trends data"
    sql = """Select post_id, created, diff as delta_minute, score, num_comments
    from coin.reddit_trends
    where diff <= 1000 """
    df = pd.read_sql(sql, pg_conn)
    return df

df_reddit_post = reddit_post_info()
df_mc_pct = market_cap_df()
df_rt = reddit_trends_df()
coin_list = list(df_mc_pct['coin_name'].sort_values().unique())
colors = ['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd','#8c564b','#e377c2','#7f7f7f','#bcbd22','#17becf'] * 10
frame=[]
df2 = df_mc_pct.groupby(['insert_timestamp'],as_index=False).mean()
df2['coin_name']="Top 100"

## layout
app.layout = html.Div([
    ## Top header Author, Title & submit Feedback Button
    html.Div(
        [
            html.Div("created by: Keerthan Vantakala",style={'color':'#ffffff','textAlign':'center','marginTop': 5},
                    className='two columns'), 
            html.Div(
                children= 'Cryptocurrency Sentiment Analysis',
                style = dict(backgroundColor="#1C4E80",
                color='#ffffff ',
                textAlign='center',
                fontSize=25),
                 className='eight columns'),
            html.Div(html.A('https://github.com/vantaka2', href = "https://github.com/vantaka2/crypto_dash_app",style={'color':'#ffffff','textAlign':'center'}
                    ),style={'marginTop': 5},
                    className='two columns'),
            ],className="row", style={'backgroundColor':'#1C4E80'}
                ),
        ## Filters 
    html.Div(
        [
            html.Div(
                [
                    html.Div("Search by Coin - Please limit to 10 coins, This app is running on a weak server!:("),
                    dcc.Dropdown(
                        id='coin_select',
                        options=[
                            {'label':i, 'value':i}
                            for i in coin_list
                        ],
                        multi=True,
                        value=['VeChain','NEM']
                    ),
                ], className='six columns'
            ),
            html.Div(
                [
                    html.Div("Date Filter",
                        style={'text-align':'center'}),
                    dcc.RadioItems(
                        id='date_filter',
                        options=[
                            {'label':'Last 7 Days', 'value':7},
                            {'label':'Last 24 Hours', 'value':1},
                        ],
                        value=7,
                        labelStyle={'display': 'inline-block',
                                    'text-align':'center'},
                        style={'text-align':'center'}
                    ),
                ], className='three columns'
            ),
            html.Div(
                [                                       
                    html.P(html.A(html.Button('Feedback'),href="https://github.com/vantaka2/crypto_dash_app/issues/new",
                    ),style={'textAlign':'center','marginTop': '5'}  ),
                    ], className='two columns'),
            html.Div(
                [                                       
                    html.P(html.A(html.Button('FAQ'),href="https://medium.com/@keerthanvantakala/faq-for-crypto-currency-sentiment-dashboard-582624a00d89",
                    ),style={'textAlign':'center', 'float':'right','marginTop': '5'}  )
                    ], className='one columns'),

        ], className="row",style={'marginTop': 5,'marginRight':15, 'marginLeft':15}
    ),
    ### KPI Metrics Marketcap, MC percent change, Metnions & mentions Pct Change
    html.Div(
        [
            html.Div(
                [
                    html.Div(children="Market Cap % Change",
                    style={'textAlign':'center','fontSize':20}),
                    html.Div(id='display_pct_change',
                    style={'textAlign':'center' })
                ], className = 'four columns'
                ),
            html.Div(
                [
                    html.Div(children="Mentions by Sentiment",
                    style={'textAlign':'center','fontSize':20}),
                    html.Div(id='sentiment_cnt',
                    style={'textAlign':'center'})
                ], className = 'four columns'
                ),
            html.Div(
                [
                    html.Div(children="Mentions",
                    style={'textAlign':'center','fontSize':20}),
                    html.Div(id='reddit_mentions',
                    style={'textAlign':'center',
                        })
                ], className = 'four columns'
                ),

        ], className="row",style={'marginTop': 5}
    ),

    ## Total MC chart & MC Percent Change 
    html.Div(
        [
            html.Div(
                [
                    dcc.Graph(
                        id='mc_by_coin'
                        
                    ),
                ], 
            ),
        ], className="row", style={'marginTop': 5,'marginRight':15, 'marginLeft':15}
    ),
    html.Div(
        [
            html.Div(children="The chart above shows the percent change of the selected coins market cap overlayed with news posted",
            style = {'float':'middle'},
            className="twelve columns")
    ],className="row"),
    
    html.Div(
        [
            html.Div([
                html.Div(id='reddit_post_trends')
                ], className='six columns'
            ),
            html.Div([
                html.Div(id = 'reddit_sentiment_info'),
                ], className='six columns'),
            
        ], className="row", style={'marginTop': 5,'marginRight':15, 'marginLeft':15}
    ), 
    
],  
    className='ten columns offset-by-one'
)

## Dynamically assigns Percent Change KPI
@app.callback(
    dash.dependencies.Output('display_pct_change', 'children'),
    [dash.dependencies.Input('coin_select', 'value'),
    dash.dependencies.Input('date_filter', 'value')])
def pct_change(coin_select, date_filter):
    df = filter_mc_df(df_mc_pct, coin_select, date_filter)
    start = df[df['insert_timestamp'] == df.min()['insert_timestamp']].sum()['market_cap_usd']
    end = df[df['insert_timestamp'] == df.max()['insert_timestamp']].sum()['market_cap_usd']
    pct_change = round(((end-start)/start)*100)
    return ' {} % '.format(pct_change)

## Dynamically count of Mentions KPI
@app.callback(
    dash.dependencies.Output('reddit_mentions', 'children'),
    [dash.dependencies.Input('coin_select', 'value'),
    dash.dependencies.Input('date_filter', 'value')])
def mentions(coin_select, date_filter):
    df_reddit = filter_reddit(df_reddit_post, coin_select, date_filter)
    return df_reddit.count()['post_id']

## Dynamically shows sentiment
@app.callback(
    dash.dependencies.Output('sentiment_cnt', 'children'),
    [dash.dependencies.Input('coin_select', 'value'),
    dash.dependencies.Input('date_filter', 'value')])
def mentions_by_sentiment(coin_select,date_filter):
    df_reddit = filter_reddit(df_reddit_post, coin_select, date_filter)
    df3 = df_reddit.groupby('sentiment', as_index=False).count()
    if 'Postive' in df3['sentiment']:
        positive_cnt = int(df3[df3['sentiment'] =='Positive']['post_id'])
    else:
        positive_cnt = 0

    negative_cnt = int(df3[df3['sentiment'] =='Negative']['post_id'])
    
    neutral_cnt = int(df3[df3['sentiment'] =='Neutral']['post_id'])
    return 'Postive:{} | Neutral: {} | Negative: {}'.format(positive_cnt,neutral_cnt,negative_cnt)


##Graph of percent change 
@app.callback(
    dash.dependencies.Output('mc_by_coin', 'figure'),
    [dash.dependencies.Input('coin_select', 'value'),
    dash.dependencies.Input('date_filter', 'value')])
def update_mc_by_coin(coin_select, date_filter):
    df_mc_stg = filter_mc_df(df_mc_pct, coin_select, date_filter)
    if date_filter == 1:
        df_mc_stg.rename(columns={"pct_change_l24h":"pct_change"},inplace=True)
        df2.rename(columns={"pct_change_l24h":"pct_change"},inplace=True)
    elif date_filter == 7:
        df_mc_stg.rename(columns={"pct_change_7d":"pct_change"},inplace=True)
        df2.rename(columns={"pct_change_7d":"pct_change"},inplace=True)
    df_stg_4 = df_mc_stg.sort_values(by=['coin_name','insert_timestamp'])    
    data = [
        go.Scatter(
            x=df_stg_4[df_stg_4['coin_name'] == i]['insert_timestamp'],
            y=df_stg_4[df_stg_4['coin_name'] == i]['pct_change'],
            mode='line',
            line = dict(color=colors[idx]),
            hovertext=False,
            opacity=0.8,
            name=i
        ) for idx, i in enumerate(coin_select)
    ]
    #calculate average of top 100
    all_trace = go.Scatter(
        x=df2['insert_timestamp'],
        y=df2['pct_change'],
        mode='line',
        line=dict(dash='dot',width=6,color='#7E909A'),
        name='Top 100 Avg'
    )
    data.append(all_trace)
    #############
    df_reddit = filter_reddit(df_reddit_post, coin_select, date_filter)
    df_2 = filter_reddit(df_rt, coin_select, date_filter)
    df_2 = df_2.groupby(by=['post_id'],as_index = False).max()[['post_id','score']]
    df3 = pd.merge(left=df_reddit, right=df_2, on='post_id',how='inner',)

    data2 = [
        go.Scatter(
            x=df3[df3['coin_name'] == i]['created'],
            y=df3[df3['coin_name'] == i]['score'],
            name = i,#df3[df3['coin_name'] == i]['post_id'],
            mode='markers',
            marker=dict(symbol=2,size =15 ,color=colors[idx]),
            yaxis='y2',
            customdata=df3[df3['coin_name'] == i]['post_id']
        ) for idx, i in enumerate(coin_select)
    ]
    data3 = data + data2

    layout = go.Layout(
        title='Market Cap % Change by Coin',
        yaxis=dict(
            title='Percent Change',  
            showgrid=False   
        ),
        yaxis2=dict(title='Score',side='right',overlaying='y',showgrid=False, type='log'),
        legend=dict(
        #traceorder='reversed', 
        orientation = 'h'
    ),
        hovermode='closest',
        margin=dict(
            l=50,
            r=50,
            t=50,
            b=50,
            pad=10
        ),
        xaxis=dict(showgrid=False ),
        height=350
    )
    figure = {'data':data3,
    'layout':layout}
    return figure

@app.callback(
    dash.dependencies.Output('reddit_sentiment_info', 'children'),
    [dash.dependencies.Input('coin_select', 'value'),
     dash.dependencies.Input('date_filter', 'value'),
     dash.dependencies.Input('mc_by_coin','hoverData')])
def create_post_info(coin_select,date_filter,main_graph_hover):
    df_2 = filter_reddit(df_rt, coin_select, date_filter)
    df_reddit = filter_reddit(df_reddit_post, coin_select, date_filter)
    df_stg = pd.merge(left=df_2,right=df_reddit,how='inner',left_on='post_id',right_on='post_id')
    if main_graph_hover is None:
        customdata=df_stg.max()['post_id']
        main_graph_hover = {'points': [
            {'curveNumber': 3, 'pointNumber': 1, 'pointIndex': 1, 'x': '2018-03-14 14:06:13', 'y': 137, 'customdata':customdata }]}
    post = main_graph_hover['points'][0]['customdata']
    if 
    title = str(df_reddit[df_reddit['post_id']==post]['title'].unique()[0])
    sentiment = str(df_reddit[df_reddit['post_id']==post]['sentiment'].unique()[0])
    if sentiment == 'Negative':
        path = 'M 0.24 0.5 L 0.14 0.64 L 0.24 0.5 Z'
    elif sentiment == 'Positive':
        path = 'M 0.24 0.5 L 0.34 0.64 L 0.24 0.5 Z'
    else:
        path = 'M 0.24 0.5 L 0.24 0.75 L 0.24 0.5 Z'
    confidence = int(df_reddit[df_reddit['post_id']==post]['confidence'].unique()[0])
    text = """ {}  | Sentiment: {}  |  confidence {}  
        """.format(title,sentiment,confidence)

    base_chart = {
    "values": [40, 20, 20, 20],
    "domain": {"x": [0, .48]},
    "marker": {
        "colors": [
            'rgb(255, 255, 255)',
            'rgb(255, 255, 255)',
            'rgb(255, 255, 255)',
            'rgb(255, 255, 255)'
        ],
        "line": {
            "width": 1
        }
    },
    "name": "Gauge",
    "hole": .4,
    "type": "pie",
    "direction": "clockwise",
    "rotation": 108,
    "showlegend": False,
    "hoverinfo": "none"
    }
    meter_chart = {
        "values": [50, 16.68, 16.67, 16.5],
        "labels": [" ", "Negative", "Neutral", "Postive"],
        "marker": {
            'colors': [
                '#FDFEFE',
                '#FF3333',
                '#D7DBDD',
                '#33CC66',
            ]
        },
        "domain": {"x": [0, 0.48]},
        "name": "Gauge",
        "hole": .3,
        "type": "pie",
        "direction": "clockwise",
        "rotation": 90,
        "showlegend": False,
        "textinfo": "label",
        "textposition": "inside",
        "hoverinfo": "none"
        }

    layout = {
        'xaxis': {
            'showticklabels': False,
            'autotick': False,
            'showgrid': False,
            'zeroline': False,
        },
        'yaxis': {
            'showticklabels': False,
            'autotick': False,
            'showgrid': False,
            'zeroline': False,
        },
        'shapes': [
            {
                'type': 'path',
                'path': path,
                'fillcolor': 'rgba(44, 160, 101, 0.5)',
                'line': {
                    'width': 3
                },
                'xref': 'paper',
                'yref': 'paper'
            }
        ],
        'annotations': [
            {
                'xref': 'paper',
                'yref': 'paper',
                'x': 0.15,
                'y': 0.45,
                'text': 'Sentiment Prediction',
                'showarrow': False
            }
        ]
    }
    base_chart['marker']['line']['width'] = 0
    return html.Div(
            [html.Div(
                [
                    html.Div(children="Title: {}".format(title),
                    style=dict(textAlign='center',
                                fontSize=15)),
                    html.A(
                        html.Button('Link to Post',style=dict(float='center',textAlign='center')), 
                    href="https://www.reddit.com/r/CryptoCurrency/comments/{}".format(post),
                    style=dict(margin= 0,textAlign='center')
                    ),   
                ]
                ),
            dcc.Graph(id = 'graph',figure = {"data": [base_chart, meter_chart],
                    "layout": layout}, style=dict(float='center')
                    ),
        ]
        )

#reddit post trends
@app.callback(
    dash.dependencies.Output('reddit_post_trends', 'children'),
    [dash.dependencies.Input('coin_select', 'value'),
     dash.dependencies.Input('date_filter', 'value'),
     dash.dependencies.Input('mc_by_coin','hoverData')])
def update_tabs(coin_select, date_filter,main_graph_hover):
    df_2 = filter_reddit(df_rt, coin_select, date_filter)
    df_reddit = filter_reddit(df_reddit_post, coin_select, date_filter)
    df_stg = pd.merge(left=df_2,right=df_reddit,how='inner',left_on='post_id',right_on='post_id')
    df_trends = df_stg.sort_values(['delta_minute']).reset_index(drop=True)
    if main_graph_hover is None:
        customdata=df_trends.max()['post_id']
        print(customdata)
        main_graph_hover = {'points': [
            {'curveNumber': 3, 'pointNumber': 1, 'pointIndex': 1, 'x': '2018-03-14 14:06:13', 'y': 137, 'customdata':customdata }]}
    posts = main_graph_hover['points'][0]['customdata']       
    data2 = [
        go.Scatter( 
        x=df_trends[df_trends['post_id'] == posts]['delta_minute'],
        y=df_trends[df_trends['post_id'] == posts]['score'],
        mode='line',
        opacity=0.8,
        line =dict(color='#000000'),
        hovertext=df_trends[df_trends['post_id'] == posts]['coin_name'] 
        )]
    layout = go.Layout(
        title='Reddit Post Trends',
        yaxis=dict(
            title='Score'
        ),
        hovermode='closest',
        showlegend=False,
        xaxis=dict(title='Minutes After Creation')
        )
    figure1 = {
        'data':data2,
        'layout':layout
        }
    return html.Div([
            dcc.Graph(
            id='graph12',
            figure=figure1
        )
        ])

 
    


#helper function for price data
def filter_mc_df(df=None, coin_select=None, date_filter=None):
    date_cutoff = df.max()['insert_timestamp'] - pd.Timedelta(days=date_filter)
    #coin_filter
    print(type(coin_select))
    if coin_select != None:
        df_stg = df[df['coin_name'].isin(coin_select)]
    #date_filter
    else:
        df_stg = df
    df_stg_2 = df_stg[df_stg['insert_timestamp'] >= date_cutoff]
    return df_stg_2

def filter_reddit(df=None, coin_select=None, date_filter=None):
    if 'coin_name' in df.columns:
        df_stg = df[df['coin_name'].isin(coin_select)]
    else:
        df_stg = df
    date_cutoff = df.max()['created'] - pd.Timedelta(days=date_filter)
    df_stg_2 = df_stg[df_stg['created'] >= date_cutoff]
    return df_stg_2

if __name__ == '__main__':
    app.run_server(debug=True)