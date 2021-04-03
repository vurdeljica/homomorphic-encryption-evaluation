import csv
import random
from lsvm.ext.lsvm_interface import LsvmInterface


class LsvmBase(LsvmInterface):
    def __init__(self, model_name):
        model_fn = "demoData/lsvm-" + model_name + "-model.csv"
        input_fn = "demoData/lsvm-" + model_name + "-input.csv"
        check_fn = "demoData/lsvm-" + model_name + "-check.csv"
        self._beta = []
        self._bias = []
        self._x = []
        self._y = []
        self._mu = []
        self._sigma = []
        self.__read_model_data(model_fn)
        self.__read_input_data(input_fn)
        self.__read_check_data(check_fn)
        self.__shuffle_data()

    def calc(self):
        raise NotImplemented

    def get_labels(self):
        return self._y

    def decrypt(self, labels):
        raise NotImplemented

    def __read_model_data(self, model_csv):
        csv_file = open(model_csv)
        csv_reader = csv.reader(csv_file, delimiter=",")
        beta = []
        mu = []
        sigma = []
        for index, row in enumerate(csv_reader):
            if index == 0:
                s = float(row[0])
            else:
                beta.append(float(row[0]))
                if len(row) > 1:
                    mu.append(float(row[1]))
                    sigma.append(float(row[2]))
        self._bias = beta[-1:]
        beta = beta[0:-1]
        beta[:] = [item / s for item in beta]
        self._beta = beta
        self._mu = mu
        self._sigma = sigma

    def __read_input_data(self, input_csv):
        csv_file = open(input_csv)
        csv_reader = csv.reader(csv_file, delimiter=",")
        x = []
        for row in csv_reader:
            xitem = []
            for index, column in enumerate(row):
                if len(self._mu) > 0 and len(self._sigma) > 0:
                    xitem.append((float(column) - float(self._mu[index])) / float(self._sigma[index]))
                else:
                    xitem.append(float(column))
            x.append(xitem)
        self._x = x

    def __read_check_data(self, check_csv):
        csv_file = open(check_csv)
        csv_reader = csv.reader(csv_file, delimiter=",")
        y = []
        for row in csv_reader:
            y.append(float(row[0]));

        self._y = y

    def __shuffle_data(self):
        dataset = list(zip(self._x, self._y))
        random.shuffle(dataset)
        self._x, self._y = zip(*dataset)
