from lsvm.lsvm_base import LsvmBase
from Pyfhel import Pyfhel


class LsvmPyfhel(LsvmBase):
    def __init__(self, model_name):
        super().__init__(model_name)
        crypto = Pyfhel()
        crypto.contextGen(p=63, m=2048, base=2, intDigits=16, fracDigits=16)
        crypto.keyGen()
        self.__crypto = crypto
        self.__enc_x = self.__enc_input()
        self.__enc_beta = self.__encrypt_arr(self._beta)
        self.__enc_bias = self.__encrypt_arr(self._bias)

    def calc(self):
        res = self.__lsvm(self.__enc_x)
        return res

    def decrypt(self, encrypted_labels):
        res = []
        for num in encrypted_labels:
            res.append(self.__crypto.decryptFrac(num))
        return res

    def __enc_input(self):
        enc_x = []
        for row in self._x:
            enc_x_row = []
            for num in row:
                enc_x_row.append(self.__crypto.encryptFrac(num))
            enc_x.append(enc_x_row)
        return enc_x

    def __sum_enc_arr(self, arr_enc):
        sum_enc = self.__crypto.encryptFrac(0)
        for num in arr_enc:
            sum_enc += num
        return sum_enc

    def __encrypt_arr(self, arr):
        arr_enc = []
        for num in arr:
            arr_enc.append(self.__crypto.encryptFrac(num))
        return arr_enc

    def __lsvm(self, x):
        res = []
        for i in range(len(self.__enc_x)):
            betaxi = [a * b for a, b in zip(self.__enc_beta, x[i])]
            ip = self.__sum_enc_arr(betaxi)
            ip = ip + self.__enc_bias[0]
            res.append(ip)
        return res

