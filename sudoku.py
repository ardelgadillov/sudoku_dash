import base64
import datetime
import io

import pandas as pd
from assets.utils import sudoku_board, generate_random_sudoku
from dash import Dash, dcc, html, Input, Output, State, callback, ClientsideFunction, no_update
from sudoku_solver import SudokuSolver

app = Dash(__name__)
server = app.server
app.layout = html.Div(
    [
        dcc.Store(id='puzzle'),

        html.Div(className='container', id='sudoku_container'),  # children=sudoku_board(side)),

        html.Div(className='buttonContainer', children=[
            html.Div('Sudoku size'),
            dcc.Dropdown([4, 9, 16, 25, 36, 49, 64, 81, 100], 9, id='sudoku_size', clearable=False,
                         className='dropDown'),
            html.Div('Difficulty'),
            dcc.Dropdown(['Easy', 'Medium', 'Hard'], 'Medium', id='sudoku_difficulty', clearable=False,
                         className='dropDown'),
        ]),
        html.Div(className='buttonContainer', children=[
            html.Button('Solve', id='solve_button', n_clicks=0),
            dcc.Upload(html.Button('Upload Sudoku'), id='upload_sudoku'),
            html.Button('Generate Random Sudoku', id='reset_button', n_clicks=0),
        ]),
    ],
    id='document'
)


@callback(Output('sudoku_container', 'children'),
          Input('sudoku_size', 'value'))
def create_board(sudoku_size):
    return sudoku_board(sudoku_size)


@callback(Output('puzzle', 'data'),
          Input('sudoku_size', 'value'),
          Input('reset_button', 'n_clicks'),
          Input('sudoku_difficulty', 'value'))
def reset_board(size, n_clicks, difficulty):
    difficulty_value = {'Easy': 0.4, 'Medium': 0.6, 'Hard': 0.8}
    base = int(size ** 0.5)
    return generate_random_sudoku(base, difficulty_value[difficulty])


@callback(Output('puzzle', 'data', allow_duplicate=True),
          Input('solve_button', 'n_clicks'),
          State('sudoku_size', 'value'),
          State('puzzle', 'data'),
          prevent_initial_call=True)
def solve_board(n_clicks, size, puzzle):
    solver = SudokuSolver(size=size, fixed=puzzle)
    return solver.solution


@callback(Output('puzzle', 'data', allow_duplicate=True),
          Input('upload_sudoku', 'contents'),
          State('upload_sudoku', 'filename'),
          State('upload_sudoku', 'last_modified'),
          prevent_initial_call=True)
def upload_sudoku(contents, filename, last_modified):
    if contents is not None:

        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        data = []
        try:
            if 'csv' in filename:
                # Assume that the user uploaded a CSV file
                data = pd.read_csv(io.StringIO(decoded.decode('utf-8')), header=None, index_col=False).values.tolist()
            elif 'xls' in filename:
                # Assume that the user uploaded an Excel file
                data = pd.read_excel(io.BytesIO(decoded), header=None, index_col=None).values.tolist()
        except Exception as e:
            print(e)
        return data

# @callback(
#     [Output(f'{row}-{col}', 'value') for row in range(side) for col in range(side)],
#     [Output(f'{row}-{col}', 'disabled') for row in range(side) for col in range(side)],
#     Input('reset_button', 'n_clicks'),
#     prevent_initial_call=True,
# )
# def reset_board(n_clicks):
#     puzzle = generate_random_sudoku(base, 0.5)
#     return (
#         *[puzzle[row][col] if (1 <= puzzle[row][col] <= side) else '' for row in range(side) for col in range(side)],
#         *[True if (1 <= puzzle[row][col] <= side) else False for row in range(side) for col in range(side)])


app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='reset_board'
    ),
    Output('document', 'id'),
    Input('puzzle', 'data'),
)

if __name__ == "__main__":
    app.run(debug=False)
