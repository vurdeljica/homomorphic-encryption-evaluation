from lsvm.lsvm_base import LsvmBase
import pycrypto
from python.utility import util


class LsvmPalisade(LsvmBase):
    def __init__(self, model_name):
        super().__init__(model_name)

        # CKKS related parameters
        max_depth = 1
        scale_factor = 50
        batch_size = util.next_power_of_2(len(self._x[0]) + 1)
        crypto = pycrypto.CKKSwrapper()
        crypto.KeyGen(max_depth, scale_factor, batch_size)

        self.__crypto = crypto
        self.__enc_x = self.__enc_input()
        self.__enc_beta = crypto.Encrypt(self._beta)
        self.__enc_bias = crypto.Encrypt(self._bias)

    def calc(self):
        res = self.__lsvm(self.__enc_x)
        return res

    def decrypt(self, encrypted_labels):
        res = []
        for num in encrypted_labels:
            dec_res = self.__crypto.Decrypt(num)
            res.append(dec_res[0])
        return res

    def __enc_input(self):
        enc_x = []
        for i in range(len(self._x)):
            enc_x.append(self.__crypto.Encrypt(self._x[i]))
        return enc_x

    def __lsvm(self, x):
        res = []
        for i in range(len(x)):
            enc_betaxi = self.__crypto.EvalMult(self.__enc_beta, x[i])
            enc_ip = self.__crypto.EvalSum(enc_betaxi, util.next_power_of_2(len(self._x[0])))
            enc_svm = self.__crypto.EvalAdd(enc_ip, self.__enc_bias)
            res.append(enc_svm)
        return res

