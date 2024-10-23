from dash import Dash, dcc, html, Input, Output, State, callback, ClientsideFunction, no_update
from assets.utils import sudoku_board, generate_random_sudoku
from sudoku_solver import SudokuSolver

app = Dash(__name__)
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
            html.Button('Reset', id='reset_button', n_clicks=0),
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
    app.run(debug=True)
