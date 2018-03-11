import dash
print('imported dash')
import dash_core_components as dcc
print('dcc')
import dash_html_components as html
print('html')
import pandas as pd
print('imported pandas')
from dash.dependencies import Input, Output
print("imported dash dependencies")
import os
print("os")
import plotly.graph_objs as go
print('imported go')



app = dash.Dash(__name__)
server = app.server


## bootstamp CSS (From https://github.com/amyoshino/DASH_Tutorial_ARGO_Labs/blob/master/app.py)
app.css.append_css(
    {'external_url':'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})
sql_con = os.environ.get('pg_db')
print("set sql_con")
def mentions_marketcap(pg_conn = sql_con):
    sql = """Select e.name, count(distinct a.post_id) as post_count,c.market_cap_usd , b.created:: date 
            from coin.xref_post_to_coin a
            inner join coin.dim_reddit_post b
            on a.post_id = b.post_id
            inner join (select id, avg(market_cap_usd) as market_cap_usd, insert_timestamp:: date from coin.price_24h where insert_timestamp >= current_date -8 group by 1,3 ) c
            on a.coin_id = c.id and b.created:: date = c.insert_timestamp:: date
            inner join coin.coin_rank d
            on a.coin_id = d.id
            inner join coin.dim_coin e
            on a.coin_id = e.id
            where coin_id is not null and created >= current_date -8 and d.current_rank < 101
            group by 1,3,4;"""
    df = pd.read_sql(sql,pg_conn)
    return df

## get market cap data frame
def market_cap_df(pg_conn=sql_con):
    """Returns the dataframe used for marketcap graphs"""
    sql = """
    select id, name, current_rank, last_updated,insert_timestamp, market_cap_usd
    From coin.mc_graph_data 
    group by 1,2,3,4,5,6
        """
    df = pd.read_sql(sql, pg_conn)
    return df
## execute mc data function:
def reddit_posts(pg_conn=sql_con):
    "returns all reddit posts "
    sql = """Select title, 
                --c.source, a.post_id, 
                b.score, c.sentiment, c.confidence 
                --, array_agg(d.keyword) as keyword
            from coin.dim_reddit_post a
            inner join (Select max(score) as score, post_id from coin.reddit_post_trends group by 2) b
            on a.post_id = b.post_id
            inner join coin.sentiment c
            on a.post_id = c.source_id 
            inner join (select post_id, unnest(keyword) as keyword from coin.xref_post_to_coin d group by 1,2) d
            on a.post_id = d.post_id
            where created >= current_Date -7
            and b.score >10 
            and d.keyword != '{null}'
            group by 1,2,3,4"""
    df = pd.read_sql(sql,pg_conn)
    return df

def reddit_agg_by_day(pg_conn=sql_con):
    "queries database for reddit post data"
    sql = """select num_posts, name, created, sentiment
        from coin.reddit_post_by_day_agg"""
    df = pd.read_sql(sql, pg_conn)
    return df

def reddit_trends_df(pg_conn=sql_con):
    "queries database for reddit post trends data"
    sql = """Select post_id, created, title, diff, score, num_comments, name
    from coin.reddit_trends
    where diff <= 1000 """
    df = pd.read_sql(sql, pg_conn)
    return df

df_rt = reddit_trends_df(sql_con)
df_mc = market_cap_df(sql_con)
coin_list = list(df_mc['name'].unique())
df_red_agg = reddit_agg_by_day(sql_con)
df_post = reddit_posts(sql_con) 
df_scatter = mentions_marketcap()
print("ran all sql")
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
                        multi=True
                    ),
                ], className='five columns'
            ),
            html.Div(
                [
                    html.Div("Quick Coin Select",
                        style={'text-align':'center'}),
                    dcc.RadioItems(
                        id='quick_filter',
                        options=[
                            {'label':'Top 5', 'value':5},
                            {'label':'Top 10', 'value':10}
                        ],
                        labelStyle={'display':'inline-block'},
                        style={'text-align':'center'}
                    ),
                ], className='two columns'
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
                ], className='two columns'
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
            html.Div(
                [
                    dcc.Graph(
                        id='total_mc'
                    ),
                ], className='six columns',
            ),
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
            # html.Div(
            #     [   dcc.Tabs(
            #             tabs=[
            #                 {'label': 'Reddit Post Trends', 'value': 1},
            #                 {'label': 'Sentiment by Coin', 'value': 2},
            #                 {'label': 'Mentions by Day', 'value': 3}
            #             ],
            #             value = 2,
            #             id='tabs',
            #         ),
            #         html.Div(id='tab-output')
            #         ], className='six columns'
            # ),
            html.Div(
                [dcc.Graph(id = 'scatterpolot'), 
                    ], className='six columns'
            ),
        ], className="row", style={'marginTop': 5,'marginRight':15, 'marginLeft':15}
    )
], 
    style={'backgroundColor':'#F1F1F1'}
)

## Callbacks

@app.callback(
    dash.dependencies.Output('coin_select', 'value'),
    [dash.dependencies.Input('quick_filter', 'value')])
def set_coin_select(qf_value):
    if qf_value == None:
        value = ['Nano', 'NEO', 'Walton','Ethereum','SALT','VeChain','Dent']
    else:
        value = df_mc[df_mc['current_rank'] <= qf_value]['name'].unique()
    return value

@app.callback(
    dash.dependencies.Output('display_pct_change', 'children'),
    [dash.dependencies.Input('coin_select', 'value'),
    dash.dependencies.Input('date_filter', 'value')])
def pct_change(coin_select, date_filter):
    df = filter_df(df_mc, coin_select, date_filter)
    print(coin_select)
    start = df[df['insert_timestamp'] == df.min()['insert_timestamp']].sum()['market_cap_usd']
    end = df[df['insert_timestamp'] == df.max()['insert_timestamp']].sum()['market_cap_usd']
    pct_change = round(((end-start)/start)*100)
    return ' {} % '.format(pct_change)

@app.callback(
    dash.dependencies.Output('reddit_mentions', 'children'),
    [dash.dependencies.Input('coin_select', 'value'),
    dash.dependencies.Input('date_filter', 'value')])
def mentions(coin_select, date_filter):
    df_reddit = filter_reddit(df_red_agg, coin_select, date_filter)
    return df_reddit.sum()['num_posts']

@app.callback(
    dash.dependencies.Output('display_total_mc', 'children'),
    [dash.dependencies.Input('coin_select', 'value')])
def mc_total(coin_select):
    df = df_mc[df_mc['insert_timestamp'] == df_mc.max()['insert_timestamp']]
    df_stg = df[df['name'].isin(coin_select)]
    tmc = int(df_stg.sum()['market_cap_usd']/1000000)
    return '{:,} MM'.format(tmc)

@app.callback(
    dash.dependencies.Output('sentiment_cnt', 'children'),
    [dash.dependencies.Input('coin_select', 'value'),
    dash.dependencies.Input('date_filter', 'value')])
def mentions_by_sentiment(coin_select,date_filter):
    df_reddit = filter_reddit(df_red_agg, coin_select, date_filter)
    df3 = df_reddit.groupby('sentiment', as_index=False).sum()
    negative_cnt = int(df3[df3['sentiment'] =='Negative']['num_posts'])
    positive_cnt = int(df3[df3['sentiment'] =='Positive']['num_posts'])
    neutral_cnt = int(df3[df3['sentiment'] =='Neutral']['num_posts'])
    return 'Postive:{} Neutral: {} Negative: {}'.format(positive_cnt,neutral_cnt,negative_cnt)

#total_MC_Graph
@app.callback(
    dash.dependencies.Output('total_mc', 'figure'),
    [dash.dependencies.Input('coin_select', 'value'),
    dash.dependencies.Input('date_filter', 'value')])
def update_total_mc(coin_select, date_filter):
    df_total_mc = filter_df(df_mc, coin_select, date_filter)
    data = [{
        'x':df_total_mc.groupby('insert_timestamp', as_index=False).agg('sum').sort_values('insert_timestamp')['insert_timestamp'],
        'y':df_total_mc.groupby('insert_timestamp', as_index=False).agg('sum').sort_values('insert_timestamp')['market_cap_usd'],
        'type': 'line',
        'name': 'Total MC'}]
    return {'data':data,
            'layout':{
                'title': 'Market Cap'}
            }
@app.callback(
    dash.dependencies.Output('scatterpolot', 'figure'),
    [dash.dependencies.Input('coin_select', 'value'),
    dash.dependencies.Input('date_filter', 'value')])
def scatter_plot(coin_select, datefilter):
    df = filter_reddit(df_scatter, coin_select, datefilter)
    data = [
        go.Scatter(
            y=df[df['name'] == i]['post_count'],
            x=df[df['name'] == i]['market_cap_usd'],
            opacity=0.8,
            hovertext=df[df['name'] == i]['created'],
            mode = 'markers',
            marker = dict(size = 15),
            name=i

        ) for i in coin_select
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

@app.callback(
    dash.dependencies.Output('mc_by_coin', 'figure'),
    [dash.dependencies.Input('coin_select', 'value'),
    dash.dependencies.Input('date_filter', 'value')])
def update_mc_by_coin(coin_select, date_filter):
    df_coin_mc_stg = filter_df(df_mc, coin_select, date_filter)
    df_coin_mc = df_coin_mc_stg.sort_values(by=['id','insert_timestamp'])
    data = [
        go.Scatter(
            x=df_coin_mc[df_coin_mc['name'] == i]['last_updated'],
            y=df_coin_mc[df_coin_mc['name'] == i]['pct_change'],
            mode='line',
            opacity=0.8,
            name=i
        ) for i in coin_select
    ]
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



# #reddit post trends
# @app.callback(
#     dash.dependencies.Output('tab-output', 'children'),
#     [dash.dependencies.Input('coin_select', 'value'),
#      dash.dependencies.Input('date_filter', 'value'),
#      dash.dependencies.Input('tabs','value')])
# def update_tabs(coin_select, date_filter,tabs):
#     if tabs == 1: 
#         df_2 = filter_reddit(df_rt, coin_select, date_filter)
#         df_trends = df_2.sort_values(['diff']).reset_index(drop=True)
#         posts = list(df_trends['post_id'].unique())
#         print(df_trends)
#         data2 = [
#             go.Scatter( 
#                 x=df_trends[df_trends['post_id'] == i]['diff'],
#                 y=df_trends[df_trends['post_id'] == i]['score'],
#                 mode='line',
#                 opacity=0.8,
#                 name=str(df_trends[df_trends['post_id'] == i]['name'].unique()[0]),
#                 hovertext=str(df_trends[df_trends['post_id'] == i]['title'].unique()[0])
#             ) for i in posts
#         ]
#         layout = go.Layout(
#             title='Reddit Post Trends',
#             yaxis=dict(
#                 title='Score'
#             ),
#             hovermode='closest',
#             showlegend=False
#         )
#         figure1 = {
#         'data':data2,
#         'layout':layout
#         }
#         return html.Div([
#             dcc.Graph(
#             id='graph',
#             figure=figure1
#         )
#         ])
#     elif tabs == 2:
#         df_reddit = filter_reddit(df_red_agg, coin_select, date_filter)
#         df_reddit2 = df_reddit.groupby(by=['sentiment','name'],as_index=False).sum()
#         sentiment = ['Neutral','Negative','Positive']
#         data = [
#             go.Bar(
#                 x = df_reddit2[df_reddit2['sentiment'] == i]['name'],
#                 y = df_reddit2[df_reddit2['sentiment'] == i]['num_posts'],
#                 name = i
#             ) for i in sentiment 
#         ]
#         layout = go.Layout(
#             title='Sentiment By Coin',
#             yaxis=dict(
#                 title='Mention Count'
#             )
#         )
#         figure1={'data':data,
#             'layout':layout}
#         return html.Div([
#             dcc.Graph(id='graph',
#             figure = figure1)])

#     elif tabs ==3:
#         df_reddit = filter_reddit(df_red_agg, coin_select, date_filter)
#         df_reddit2 = df_reddit.groupby(by=['created','name'],as_index=False).sum()
#         data = [
#             go.Bar(
#                 x=df_reddit2[df_reddit2['name'] == i]['created'],
#                 y=df_reddit2[df_reddit2['name'] == i]['num_posts'],
#                 name = i#,
#                 #hovertext=df_reddit[df_reddit['name'] == i]['sentiment']
#             ) for i in coin_select
#         ]
#         layout = go.Layout(
#             title='Mentions per Day',
#             barmode='stack', 
#             yaxis=dict(title='Mention Count'),
#             hovermode='closest'
#             )
#         figure1={'data':data,
#             'layout':layout}
#         return html.Div([
#             dcc.Graph(id='graph',
#             figure = figure1)])



#helper function for price data
def filter_df(df=None, coin_select=None, date_filter=None):
    date_cutoff = df.max()['insert_timestamp'] - pd.Timedelta(days=date_filter)
    #coin_filter
    df_stg = df[df['name'].isin(coin_select)]
    #date_filter
    df_stg_2 = df_stg[df_stg['insert_timestamp'] >= date_cutoff]
    coin_list = list(df_stg_2['name'].unique())
    frame = []
    for i in coin_list:
        df_stg_3 = df_stg_2[df_stg_2['name']== i]
        base = df_stg_3[df_stg_3['insert_timestamp'] == df_stg_3.min()['insert_timestamp']]['market_cap_usd'].reset_index(drop=True)[0]
        df_stg_3['pct_change'] = (((df_stg_3['market_cap_usd']-base)/ base) * 100 )
        frame.append(df_stg_3)
    df_stg_4 = pd.concat(frame)
    return df_stg_4


def filter_reddit(df=None, coin_select=None, date_filter=None):
    df_stg = df[df['name'].isin(coin_select)]
    date_cutoff = df.max()['created'] - pd.Timedelta(days=date_filter)
    df_stg_2 = df_stg[df_stg['created'] >= date_cutoff]
    return df_stg_2

if __name__ == '__main__':
    app.run_server(debug=True)