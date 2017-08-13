# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 23:40:09 2017

Dash table for TopFirms

@author: XINYU HONG
"""

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import json
import pandas as pd

# prepare data
feature_file = 'features.json'
with open(feature_file, 'r') as INPUT:
    features = json.load(INPUT)
df = pd.read_json('firm_rank.json').T.reset_index()
newdcol = ['Firm',
         u'Midsize',
         u'Summer',
         u'Overall',
         u'Diversity',
         u'Practice',
         u'Region',
         u'BestWorkFor',
         u'Vault100']
url_file = 'firm_url.json'
with open(url_file, 'r') as INPUT:
    urls = json.load(INPUT)


# define helper function for filter
def filterFeat(df, featCategory, feats):
    # filter df with AND gate on all the feats
    if (len(feats) == 0) or (df.shape[0] == 0):
        return df
    inds = []
    for i in range(df.shape[0]):
        if type(df[featCategory].iloc[i]) == dict: # note df[featCategory][i] will return KeyError b.c. df[featCategory] might not have 'i' row
            valid = 1
            for feat in feats:
                if df[featCategory].iloc[i].get(feat) == None:
                    valid = 0
                    break
            if valid == 1:
                inds.append(i)
    return df.iloc[inds]
    
# define helper function to table generation
def stringify(elm):
    if type(elm) != dict:
        return str(elm)
    return ' '.join(["{}({}),".format(key,val) for key, val in elm.items()])

def generate_table(dataframe, max_rows=100):
    if dataframe.shape[0] == 0:
        return html.Table([html.Tr([html.Th(col) for col in dataframe.columns])])
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][dataframe.columns[j]]) if j > 0 
                        else html.Td(dcc.Markdown( "[{}]({})".format(dataframe.iloc[i][dataframe.columns[j]], urls[dataframe.iloc[i][dataframe.columns[j]]]) ) ) 
                        for j in range(len(dataframe.columns))]) 
                    for i in range(min(len(dataframe), max_rows))],
        style = {'textAlign': 'left', 'verticalAlign': 'middle',
                 'borderBottom': '1px solid #ddd'}
    )

# set up app
app = dash.Dash()

my_css_url = "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"
app.css.append_css({
    "external_url": my_css_url
})


app.layout = html.Div([
    html.Label('The Best Mid-sized Law Firms to work for'),
    dcc.Dropdown(
        id = 'midsize',
        options = [{'label': x, 'value': x} for x in features[u'BestMidsizeLawFirmstoWorkFor,2017(2018RankingsComingSoon!)']],
        value = [],
        multi = True
    ),
    html.Label('Summer Associate Programs'),
    dcc.Dropdown(
        id = 'summer',
        options = [{'label': x, 'value': x} for x in features[u'BestSummerAssociatePrograms']],
        value = [],
        multi = True
    ),
    html.Label('Diversity'),
    dcc.Dropdown(
        id = 'diversity',
        options = [{'label': x, 'value': x} for x in features[u'TheBestLawFirmsforDiversity']],
        value = [],
        multi = True
    ),
    html.Label('Practice'),
    dcc.Dropdown(
        id = 'practice',
        options = [{'label': x, 'value': x} for x in features[u'TheBestLawFirmsinEachPracticeArea']],
        value = [],
        multi = True
    ),
    html.Label('Best in Each US Region'),
    dcc.Dropdown(
        id = 'region',
        options = [{'label': x, 'value': x} for x in features[u'TheBestLawFirmsinEachUSRegion']],
        value = [],
        multi = True
    ),
    html.Label('Work Condition'),
    dcc.Dropdown(
        id = 'condition',
        options = [{'label': x, 'value': x} for x in features[u'TheBestLawFirmstoWorkFor']],
        value = [],
        multi = True
    ),
    html.Div(id = 'output_table')

])

@app.callback(
    Output('output_table', 'children'),
    [Input('midsize', 'value'),
     Input('summer', 'value'),
     Input('diversity', 'value'),
     Input('practice', 'value'),
     Input('region', 'value'),
     Input('condition', 'value')])
def filterTable(midsize, summer, diversity, practice, region, condition):
    df_temp = filterFeat(df, u'BestMidsizeLawFirmstoWorkFor,2017(2018RankingsComingSoon!)', midsize)
    df_temp = filterFeat(df_temp, u'BestSummerAssociatePrograms', summer)
    df_temp = filterFeat(df_temp, u'TheBestLawFirmsforDiversity', diversity)
    df_temp = filterFeat(df_temp, u'TheBestLawFirmsinEachPracticeArea', practice)
    df_temp = filterFeat(df_temp, u'TheBestLawFirmsinEachUSRegion', region)
    df_temp = filterFeat(df_temp, u'TheBestLawFirmstoWorkFor', condition)
    df_new = df_temp.copy().sort_values('OverallRank')
    df_new.columns = newdcol
    for col in df_new.columns:
        df_new[col] = map(lambda x: stringify(x), df_new[col])
    return generate_table(df_new)


if __name__ == '__main__':
    app.run_server(debug = True)