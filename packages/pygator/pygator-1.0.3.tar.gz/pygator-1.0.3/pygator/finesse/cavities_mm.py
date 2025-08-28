# my_package/__init__.py
# from pygator.module import *
# from ._version import __version__

# pygator/__init__.py

def get_cav_mismatches(model, print_tables=True):
    mismatch_x, mismatch_y = model.cavity_mismatches_table()

    # Extracting the tables from the mismatch data
    cav_mismatches_table_x = mismatch_x.table
    cav_mismatches_table_y = mismatch_y.table 

    arr_float_x = cav_mismatches_table_x[1:-1,1:-1].astype(float)

    arr_float_y = cav_mismatches_table_y[1:-1,1:-1].astype(float)

    n = arr_float_x.shape[0]
    num_elements = n * (n - 1) // 2  # = 21 for a 7x7 matrix

    x_avg = np.sum(np.triu(arr_float_x, k=1)) / num_elements
    y_avg = np.sum(np.triu(arr_float_y, k=1)) / num_elements
    total_avg = (x_avg + y_avg) / 2


    # Specific mismatch values
    XARM_YARM_x = cav_mismatches_table_x[2][3]
    XARM_YARM_y = cav_mismatches_table_y[2][3]
    PRX_XARM_x = cav_mismatches_table_x[4][2]
    PRX_XARM_y = cav_mismatches_table_y[4][2]
    PRY_YARM_x = cav_mismatches_table_x[5][3]
    PRY_YARM_y = cav_mismatches_table_y[5][3]
    SRX_XARM_x = cav_mismatches_table_x[6][2]
    SRX_XARM_y = cav_mismatches_table_y[6][2]
    SRY_YARM_x = cav_mismatches_table_x[7][3]
    SRY_YARM_y = cav_mismatches_table_y[7][3]

    # Optionally print the mismatch tables
    if print_tables==True:
        print(mismatch_x)
        print(mismatch_y)
        print("All cavities average mismatch (x and y) is", total_avg)

    # Return the results as a dictionary
    return {
        "XARM_YARM_x": XARM_YARM_x,
        "XARM_YARM_y": XARM_YARM_y,
        "PRX_XARM_x": PRX_XARM_x,
        "PRX_XARM_y": PRX_XARM_y,
        "PRY_YARM_x": PRY_YARM_x,
        "PRY_YARM_y": PRY_YARM_y,
        "SRX_XARM_x": SRX_XARM_x,
        "SRX_XARM_y": SRX_XARM_y,
        "SRY_YARM_x": SRY_YARM_x,
        "SRY_YARM_y": SRY_YARM_y,
        "x_avg": x_avg,
        "y_avg": y_avg,
        'total_avg': total_avg,
        'mismatch_x': mismatch_x,
        'mismatch_y': mismatch_y
    }