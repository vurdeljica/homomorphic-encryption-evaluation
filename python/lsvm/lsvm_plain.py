from lsvm.lsvm_base import LsvmBase


class LsvmPlain(LsvmBase):
    def __init__(self, model_name):
        super().__init__(model_name)

    def calc(self):
        res = []
        for i in range(len(self._x)):
            betaxi = [a * b for a, b in zip(self._beta, self._x[i])]
            ip = sum(betaxi)
            ip = ip + self._bias[0]
            res.append(ip)
        return res

    def decrypt(self, labels):
        return labels
