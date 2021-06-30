import dash
import dash_cytoscape as cyto
import dash_html_components as html
import pandas as pd


my_stylesheet = [
    # Group selectors
    {
        'selector': 'node',
        'style': {
            'content': 'data(label)'
        }
    },

    # Class selectors
    {
        'selector': '.red',
        'style': {
            'background-color': 'red',
            'line-color': 'red'
        }
    },
    {
        'selector': '.triangle',
        'style': {
            'shape': 'triangle'
        }
    },
    {
        'selector': '.square',
        'style': {
            'shape': "square"
        }
    },

    {
        'selector': '.green',
        'style': {
            'background-color': 'green',
            'line-color': 'green'
        }
    }
]

sampNode = {'data': {'id': 'n6', 'label': '6'},
            'position': {'x': 250, 'y': 250},
            'classes': 'green square'
            }

my_elements = [
    # node data
    {
        'data': {'id': 'n1', 'label': '1'},
        'position': {'x': 50, 'y': 50},
        'classes': 'green triangle'
    },

    {
        'data': {'id': 'n2', 'label': '2'},
        'position': {'x': 200, 'y': 200},
        'classes': "square green"
    },

    {
        'data': {'id': 'n3', 'label': '3'},
        'position': {'x': 130, 'y': 100},
        'classes': 'circle'
    },
    {
        'data': {'id': 'n4', 'label': '4'},
        'position': {'x': 200, 'y': 100},
        'classes': 'circle'
    },
    {
        'data': {'id': 'n5', 'label': '5'},
        'position': {'x': 100, 'y': 120},
        'classes': 'circle',
        'selected': True
    },
    sampNode,
    # edge data
    {
        'data': {'source': 'n1',
                 'target': 'n2',
                 'label': 'n1-n2'},
        'selected': True
    },

    {
        'data': {'source': 'n1',
                 'target': 'n3',
                 'label': 'n1-n3'},
        'classes': 'red'
    },

    {
        'data': {'source': 'n3',
                 'target': 'n4'}
    },

    {
        'data': {'source': 'n1',
                 'target': 'n5'}
    }
]


app = dash.Dash(__name__)
app.layout = html.Div([
    cyto.Cytoscape(
        id='cytoscape',
        layout={'name': 'preset'},
        style={'width': '700px', 'height': '700px',
               'background-color': 'white'},
        stylesheet=my_stylesheet,
        elements=my_elements
    )
])

print('1', type(my_elements[0]['data']['label']), '2', type(my_elements))

if __name__ == '__main__':
    app.run_server(debug=True)
