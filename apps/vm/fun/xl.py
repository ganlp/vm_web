import xlrd


class Excel:
    bk = None
    table = None

    def __init__(self, filename, table):
        self.__open(filename)
        self.set_table(table)

    def __open(self, filename):
        self.bk = xlrd.open_workbook(filename)

    def set_table(self, by):
        if isinstance(by, str):
            self.table = self.bk.sheet_by_name(by)
        if isinstance(by, int):
            self.table = self.bk.sheet_by_index(by)

    def get_row(self, row, start_colx=0, end_colx=None):
        if end_colx is not None:
            if (end_colx-start_colx) == 1:
                return self.table.row_values(row, start_colx, end_colx)[0]
            if (end_colx-start_colx) == 0:
                return ''
        return self.table.row_values(row, start_colx, end_colx)

    def get_col(self, col, start_rowx=0, end_rowx=None):
        if end_rowx is not None:
            if (end_rowx-start_rowx) == 1:
                return self.table.row_values(col, start_rowx, end_rowx)[0]
            if (end_rowx-start_rowx) == 0:
                return ''
        return self.table.col_values(col, start_rowx, end_rowx)

    def get_num(self, row_or_col):
        if row_or_col == 'row':
            return self.table.nrows
        elif row_or_col == 'col':
            return self.table.ncols
        else:
            raise ValueError('row_or_col=[row/col]')

    def col_spe(self, name, startrow=0):
        # 按表头查找，返回那一列除表头的数据
        namelist = self.get_row(startrow)
        index = [namelist.index(cname) for cname in namelist if cname == name]
        if index:
            return self.get_col(a[0], startrow+1)
        return ''
