import pyomo.environ as pyo
from pyomo.core.util import quicksum
from pyomo.opt import SolverFactory
import pandas as pd
import requests
from itertools import islice
import os
import logging.config


# 'application' code
class SudokuSolver:
    # open logging configuration file
    logging.config.fileConfig('sudoku_log.config')
    # create self.logger
    logger = logging.getLogger('Sudoku')

    def __init__(self, size, fixed=None):
        # self.logger.debug('debug message')
        # self.logger.info('info message')
        # self.logger.warning('warn message')
        # self.logger.error('error message')
        # self.logger.critical('critical message')

        self.logger.info('Sudoku constructor')
        self.size = size
        self.base = int(size ** 0.5)
        self.fixed = fixed
        self.solution = [[0] * size for _ in range(size)]
        self.logger.info('Create optimization model')
        self.model = self.sudoku_model()

        if fixed is not None:
            # print(fixed)
            self.solve()

    def sudoku_model(self):
        """ define the optimization model
        """

        model = pyo.ConcreteModel()

        """Sets"""
        model.i = pyo.RangeSet(1, self.size)  # rows - 1 to size
        model.j = pyo.RangeSet(1, self.size)  # columns - 1 to size
        model.k = pyo.RangeSet(1, self.size)  # digits - 1 to size

        model.p = pyo.RangeSet(1, self.base)  # row boxes - 1 to base
        model.q = pyo.RangeSet(1, self.base)  # column boxes - 1 to base

        """Variables"""
        model.x = pyo.Var(model.i, model.j, model.k, bounds=(0, 1), domain=pyo.NonNegativeReals)  #domain=pyo.Binary)

        """Objective Function"""

        def obj_expression(m):
            return 0  #quicksum(m.x[i, j, k] for i in m.i for j in m.j for k in m.k)

        """Constraints"""

        # Unique digits
        def c_digits(m, i, j):
            return quicksum(m.x[i, j, k] for k in m.k) == 1

        # Unique in rows
        def c_rows(m, j, k):
            return quicksum(m.x[i, j, k] for i in m.i) == 1

        # Unique in columns
        def c_columns(m, i, k):
            return quicksum(m.x[i, j, k] for j in m.j) == 1

        # Unique in boxes
        def c_boxes(m, k, p, q):
            return quicksum(m.x[i, j, k] for i in range(self.base * (p - 1) + 1, self.base * p + 1)
                            for j in range(self.base * (q - 1) + 1, self.base * q + 1)) == 1

        """Define optimization problem"""
        model.obj = pyo.Objective(rule=obj_expression, sense=pyo.maximize)
        """Add constraints to optimization model"""
        model.c_digits = pyo.Constraint(model.i, model.j, rule=c_digits)
        model.c_rows = pyo.Constraint(model.j, model.k, rule=c_rows)
        model.c_columns = pyo.Constraint(model.i, model.k, rule=c_columns)
        model.c_boxes = pyo.Constraint(model.k, model.p, model.q, rule=c_boxes)

        # return model
        return model

    def decode(self):
        dec = [(i + 1, j + 1, self.fixed[i][j])
               for i in range(self.size)
               for j in range(self.size)
               if ((self.fixed[i][j] >= 1) and (self.fixed[i][j] <= self.size))]
        for i in dec:
            self.model.x[i].fix(1)

    def encode(self):
        for (i, j, k), v in self.model.x.items():
            # print(i, j, k, pyo.value(v))
            if pyo.value(v) >= 0.999999:
                self.solution[i - 1][j - 1] = k

    def solve(self):
        self.logger.info('Solving sudoku')

        self.decode()
        # with open('model.txt', 'w') as output_file:
        #     self.model.pprint(output_file)
        opt = pyo.SolverFactory('appsi_highs')
        opt.solve(self.model)
        self.encode()

        self.logger.info('Sudoku solution')
        # print(pd.DataFrame(self.solution))
