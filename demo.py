from gameboard import GameBoard
'''
This file demonstrates everything you can do with a GameBoard
'''

def __setup():  # in this demo, this function runs on startup
    gb = GameBoard.get_board()  # get a reference to the game board
    max_rows = gb.get_row_count()  # how many rows in the board
    max_cols = gb.get_column_count()  # how many columns in the board

    colors = ["red", "yellow"]
    count = 0
    for r in range(max_rows):
        for c in range(max_cols):
            cell = gb.get_cell(r, c)  # get a reference to the cell/tile at that location
            cell.set_color(colors[count % 2])  # set its color
            cell.set_label("?")  # set its label
            count = count + 1


def reset():  # all functions whose names do not begin with underscore will appear as menu options under MyFuncs
    gb = GameBoard.get_board()
    max_rows = gb.get_row_count()
    max_cols = gb.get_column_count()

    for r in range(max_rows):
        for c in range(max_cols):
            cell = gb.get_cell(r, c)
            cell.set_color("GRAY")

    __change_labels('O')


def __change_labels(label):  # any function named with two leading underscores does not appear on menu
    gb = GameBoard.get_board()
    max_rows = gb.get_row_count()
    max_cols = gb.get_column_count()

    for r in range(max_rows):
        for c in range(max_cols):
            cell = gb.get_cell(r, c)
            cell.set_label(label)


def __click(cell):  # in this demo, this function is invoked whenever a tile in the game board is clicked
    row = cell.get_row()
    col = cell.get_col()
    cell.set_label(str(row) + "," + str(col))
    cell.set_color("LIGHT PINK")


if __name__ == '__main__':
    GameBoard(4, 3, title="Demo Board", start=__setup, handle=__click)
    # first parameter is number of rows in the gameboard
    # second parameter is number of columns in the gameboard
    # start keyword specifies function to execute on start up
    # handle keyword specifies function to invoke whenever a cell in the gameboard is clicked
    # both are optional
