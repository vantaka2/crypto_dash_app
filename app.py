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
    select name as coin_name, last_updated, insert_timestamp, market_cap_usd
    From coin.mc_graph_data 
    group by 1,2,3,4
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
df_mc = market_cap_df()
df_rt = reddit_trends_df()
coin_list = list(df_mc['coin_name'].sort_values().unique())

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
                        value=['VeChain','Nano']
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
                    html.P(html.A(html.Button('Submit Feedback'),href="https://github.com/vantaka2/crypto_dash_app/issues/new",
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
                    html.Div(children="Market Cap",
                    style={'textAlign':'center','fontSize':20}),
                    html.Div([
                        html.Div(id = 'display_total_mc',
                            style={'textAlign':'center'}
                            ),
                    ]),

                ], className = 'three columns'
                ),
            html.Div(
                [
                    html.Div(children="Market Cap % Change",
                    style={'textAlign':'center','fontSize':20}),
                    html.Div(id='display_pct_change',
                    style={'textAlign':'center' })
                ], className = 'three columns'
                ),
            html.Div(
                [
                    html.Div(children="Mentions",
                    style={'textAlign':'center','fontSize':20}),
                    html.Div(id='reddit_mentions',
                    style={'textAlign':'center',
                        })
                ], className = 'three columns'
                ),
            html.Div(
                [
                    html.Div(children="Mentions by Sentiment",
                    style={'textAlign':'center','fontSize':20}),
                    html.Div(id='sentiment_cnt',
                    style={'textAlign':'center'})
                ], className = 'three columns'
                ),
        ], className="row",style={'marginTop': 5}
    ),

    ## Total MC chart & MC Percent Change 
    html.Div(
        [
            # html.Div(
            #     [
            #         dcc.Graph(
            #             id='total_mc'
            #         ),
            #     ], className='six columns',
            # ),
            html.Div(
                [
                    dcc.Graph(
                        id='mc_by_coin'
                    ),
                ], className='six columns'
            )
        ], className="row", style={'marginTop': 5,'marginRight':15, 'marginLeft':15}
    ),
    html.Div(
        [
            html.Div(
                [   dcc.Tabs(
                        tabs=[
                            {'label': 'Reddit Post Trends', 'value': 1},
                            {'label': 'Sentiment by Coin', 'value': 2},
                            {'label': 'Mentions by Day', 'value': 3}
                        ],
                        value = 2,
                        id='tabs',
                    ),
                    html.Div(id='tab-output')
                    ], className='six columns'
            ),
            html.Div(
                [dcc.Graph(id = 'scatterpolot'), 
                    ], className='six columns'
            ),
        ], className="row", style={'marginTop': 5,'marginRight':15, 'marginLeft':15}
    )
], 
    #style={'backgroundColor':'#F1F1F1'}, 
    className='ten columns offset-by-one'
)

## Dynamically assigns Percent Change KPI
@app.callback(
    dash.dependencies.Output('display_pct_change', 'children'),
    [dash.dependencies.Input('coin_select', 'value'),
    dash.dependencies.Input('date_filter', 'value')])
def pct_change(coin_select, date_filter):
    df = filter_mc_df(df_mc, coin_select, date_filter)
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

## Dynamically shows Total Marketcap
@app.callback(
    dash.dependencies.Output('display_total_mc', 'children'),
    [dash.dependencies.Input('coin_select', 'value')])
def mc_total(coin_select):
    df = df_mc[df_mc['insert_timestamp'] == df_mc.max()['insert_timestamp']]
    df_stg = df[df['coin_name'].isin(coin_select)]
    tmc = int(df_stg.sum()['market_cap_usd']/1000000)
    return '{:,} MM'.format(tmc)

## Dynamically shows sentiment
@app.callback(
    dash.dependencies.Output('sentiment_cnt', 'children'),
    [dash.dependencies.Input('coin_select', 'value'),
    dash.dependencies.Input('date_filter', 'value')])
def mentions_by_sentiment(coin_select,date_filter):
    df_reddit = filter_reddit(df_reddit_post, coin_select, date_filter)
    df3 = df_reddit.groupby('sentiment', as_index=False).sum()
    negative_cnt = int(df3[df3['sentiment'] =='Negative']['post_id'])
    positive_cnt = int(df3[df3['sentiment'] =='Positive']['post_id'])
    neutral_cnt = int(df3[df3['sentiment'] =='Neutral']['post_id'])
    return 'Postive:{} Neutral: {} Negative: {}'.format(positive_cnt,neutral_cnt,negative_cnt)

## Scatter plot of mentions vs marketcap by day
@app.callback(
    dash.dependencies.Output('scatterpolot', 'figure'),
    [dash.dependencies.Input('coin_select', 'value'),
    dash.dependencies.Input('date_filter', 'value')])
def scatter_plot(coin_select, datefilter):
    df = filter_reddit(df_reddit_post, coin_select, datefilter)
    df['created']= df['created'].dt.date
    df = df.groupby(by=['created','coin_name'],as_index=False).count()[['coin_name','created','post_id']]
    df2 = filter_mc_df(df_mc,coin_select, datefilter)
    df2['insert_timestamp']=df2['insert_timestamp'].dt.date
    df2 = df2.groupby(by=['coin_name','insert_timestamp'], as_index = False).mean()[['coin_name','insert_timestamp','market_cap_usd']]
    df3 = pd.merge(df,df2,how='inner',left_on = ['coin_name','created'], right_on = ['coin_name','insert_timestamp'])[['coin_name','created','post_id','market_cap_usd']]
    df3.head()
    coin_list = list(df2['coin_name'].unique())
    data = [
        go.Scatter(
            y=df3[df3['coin_name'] == i]['post_id'],
            x=df3[df3['coin_name'] == i]['market_cap_usd'],
            opacity=0.8,
            hovertext=df3[df3['coin_name'] == i]['created'],
            mode = 'markers',
            marker = dict(size = 15),
            name=i

        ) for i in coin_list
    ]
    layout = go.Layout(
        title='Mentions vs Marketcap',
        xaxis=dict(
             title='Marketcap (Log Scale)',
             
        type='log',
        autorange=True,
        
    ),
    hovermode='closest',
    yaxis=dict(
        title='Mention Count',
        
        autorange=True
    )
    )
    figure = {'data':data,
    'layout':layout}
    return figure

##Graph of percent change 
@app.callback(
    dash.dependencies.Output('mc_by_coin', 'figure'),
    [dash.dependencies.Input('coin_select', 'value'),
    dash.dependencies.Input('date_filter', 'value')])
def update_mc_by_coin(coin_select, date_filter):
    df_mc_stg = filter_mc_df(df_mc, coin_select, date_filter)
    coin_list = list(df_mc_stg['coin_name'].unique())
    frame = []
    for i in coin_list:
        df_stg_3 = df_mc_stg[df_mc_stg['coin_name'] == i]
        base = df_stg_3[df_stg_3['insert_timestamp'] == df_stg_3.min()['insert_timestamp']]['market_cap_usd'].reset_index(drop=True)[0]
        df_stg_3['pct_change'] = (((df_stg_3['market_cap_usd']-base)/ base) * 100 )
        frame.append(df_stg_3)
    df_stg_4 = pd.concat(frame)
    df_stg_4 = df_stg_4.sort_values(by=['coin_name','insert_timestamp'])
    data = [
        go.Scatter(
            x=df_stg_4[df_stg_4['coin_name'] == i]['last_updated'],
            y=df_stg_4[df_stg_4['coin_name'] == i]['pct_change'],
            mode='line',
            opacity=0.8,
            name=i
        ) for i in coin_select
    ]
    #df_avg_all = df_stg_4.group_by(by=['insert_timestamp'], as_index = False).mean()[['pct_change','insert_timestamp']]
    # avg_all ={
    #     'type': 'scatter',
    #     'x': df_stg_4.group_by(by=['insert_timestamp'], as_index = False).mean()['insert_timestamp'],
    #     'y': df_stg_4.group_by(by=['insert_timestamp'], as_index = False).mean()['pct_change'],
    #     'mode':'line',
    #     'name':'Average Percent'
    # }

    layout = go.Layout(
        title='Market Cap % Change by Coin',
        yaxis=dict(
            title='Percent Change',     
        ),
        hovermode='closest',
        margin=dict(
            l=50,
            r=50,
            t=50,
            b=50,
            pad=10
        ),
        xaxis={'title':''}
    )
    figure = {'data':data,
    'layout':layout}
    return figure
##reddit agg graph

#reddit post trends
@app.callback(
    dash.dependencies.Output('tab-output', 'children'),
    [dash.dependencies.Input('coin_select', 'value'),
     dash.dependencies.Input('date_filter', 'value'),
     dash.dependencies.Input('tabs','value')])
def update_tabs(coin_select, date_filter,tabs):
    if tabs == 1: 
        df_2 = filter_reddit(df_rt, coin_select, date_filter)
        df_trends = df_2.sort_values(['delta_minute']).reset_index(drop=True)
        posts = list(df_trends['post_id'].unique())
        data2 = [
            go.Scatter( 
                x=df_trends[df_trends['post_id'] == i]['delta_minute'],
                y=df_trends[df_trends['post_id'] == i]['score'],
                mode='line',
                opacity=0.8,
                name=i
            ) for i in posts
        ]
        layout = go.Layout(
            title='Reddit Post Trends',
            yaxis=dict(
                title='Score'
            ),
            hovermode='closest',
            showlegend=False
        )
        figure1 = {
        'data':data2,
        'layout':layout
        }
        return html.Div([
            dcc.Graph(
            id='graph',
            figure=figure1
        )
        ])
    elif tabs == 2:
        df_reddit = filter_reddit(df_reddit_post, coin_select, date_filter)
        df_reddit2 = df_reddit.groupby(by=['sentiment','coin_name'],as_index=False).count()
        sentiment = ['Neutral','Negative','Positive']
        data = [
            go.Bar(
                x = df_reddit2[df_reddit2['sentiment'] == i]['coin_name'],
                y = df_reddit2[df_reddit2['sentiment'] == i]['post_id'],
                name = i
            ) for i in sentiment 
        ]
        layout = go.Layout(
            title='Sentiment By Coin',
            yaxis=dict(
                title='Mention Count'
            )
        )
        figure1={'data':data,
            'layout':layout}
        return html.Div([
            dcc.Graph(id='graph',
            figure = figure1)])

    elif tabs ==3:
        df_reddit = filter_reddit(df_reddit_post, coin_select, date_filter)
        df_reddit['created']=df_reddit['created'].dt.date
        df_reddit2 = df_reddit.groupby(by=['created','coin_name'],as_index=False).count()
        data = [
            go.Bar(
                x=df_reddit2[df_reddit2['coin_name'] == i]['created'],
                y=df_reddit2[df_reddit2['coin_name'] == i]['post_id'],
                name = i#,
                #hovertext=df_reddit[df_reddit['name'] == i]['sentiment']
            ) for i in coin_select
        ]
        layout = go.Layout(
            title='Mentions per Day',
            barmode='stack', 
            yaxis=dict(title='Mention Count'),
            hovermode='closest'
            )
        figure1={'data':data,
            'layout':layout}
        return html.Div([
            dcc.Graph(id='graph',
            figure = figure1)])

#helper function for price data
def filter_mc_df(df=None, coin_select=None, date_filter=None):
    date_cutoff = df.max()['insert_timestamp'] - pd.Timedelta(days=date_filter)
    #coin_filter
    df_stg = df[df['coin_name'].isin(coin_select)]
    #date_filter
    df_stg_2 = df_stg[df_stg['insert_timestamp'] >= date_cutoff]
    return df_stg_2

def filter_reddit(df=None, coin_select=None, date_filter=None):
    if 'coin_name' in df.columns:
        df_stg = df[df['coin_name'].isin(coin_select)]
    else:
        df_stg = df
        print('no coin filter')
    date_cutoff = df.max()['created'] - pd.Timedelta(days=date_filter)
    df_stg_2 = df_stg[df_stg['created'] >= date_cutoff]
    return df_stg_2

if __name__ == '__main__':
    app.run_server(debug=True)