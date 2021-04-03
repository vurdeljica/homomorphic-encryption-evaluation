import math

from lsvm.lsvm_base import LsvmBase
import numpy as np
import seal
from utility import util
import gc


class CryptoContext:
    def __init__(self, _parms, _scale, _context, _ckks_encoder, _slot_count, _keygen,
                 _public_key, _secret_key, _relin_key, _galois_key, _encryptor, _evaluator, _decryptor):
        self.parms = _parms
        self.context = _context
        self.scale = _scale
        self.ckks_encoder = _ckks_encoder
        self.slot_count = _slot_count

        self.keygen = _keygen
        self.public_key = _public_key
        self.secret_key = _secret_key
        self.galois_key = _galois_key
        self.relin_key = _relin_key

        self.encryptor = _encryptor
        self.evaluator = _evaluator
        self.decryptor = _decryptor


class LsvmSeal(LsvmBase):
    def __init__(self, model_name):
        super().__init__(model_name)

        parms = seal.EncryptionParameters(seal.scheme_type.ckks)
        poly_modulus_degree = 4096
        parms.set_poly_modulus_degree(poly_modulus_degree)
        parms.set_coeff_modulus(seal.CoeffModulus.Create(poly_modulus_degree, [40, 25, 40]))
        scale = 2.0 ** 25
        context = seal.SEALContext(parms)
        ckks_encoder = seal.CKKSEncoder(context)
        slot_count = ckks_encoder.slot_count()
        keygen = seal.KeyGenerator(context)
        public_key = keygen.create_public_key()
        secret_key = keygen.secret_key()
        relin_key = keygen.create_relin_keys()

        encryptor = seal.Encryptor(context, public_key)
        evaluator = seal.Evaluator(context)
        decryptor = seal.Decryptor(context, secret_key)

        self.__crypto = CryptoContext(parms, scale, context, ckks_encoder, slot_count, keygen,
                                      public_key, secret_key, relin_key, None, encryptor, evaluator, decryptor)

        self.__enc_x = self.__enc_input()
        self.__enc_beta = self.__encrypt_arr(self._beta)
        self.__enc_bias = self.__encrypt_arr(self._bias)

    def calc(self):
        res = self.__lsvm(self.__enc_x)
        return res

    def decrypt(self, encrypted_labels):
        labels = []
        for encrypted_label in encrypted_labels:
            plain = self.__crypto.decryptor.decrypt(encrypted_label)
            plain = self.__crypto.ckks_encoder.decode(plain)
            labels.append(plain[0])
        return labels

    def __enc_input(self):
        enc_x = []
        for row in self._x:
            enc_row = []
            for num in row:
                enc_num = self.__crypto.ckks_encoder.encode([num], self.__crypto.scale)
                enc_num = self.__crypto.encryptor.encrypt(enc_num)
                enc_row.append(enc_num)
            enc_x.append(enc_row)
        return enc_x

    def __sum_enc_arr(self, arr_enc):
        return self.__crypto.evaluator.add_many(arr_enc)

    def __encrypt_arr(self, arr):
        enc_arr = []
        for num in arr:
            enc_num = self.__crypto.ckks_encoder.encode([num], self.__crypto.scale)
            enc_num = self.__crypto.encryptor.encrypt(enc_num)
            enc_arr.append(enc_num)
        return enc_arr

    def __lsvm(self, x):
        res = []
        for i in range(len(self.__enc_x)):
            betaxi = []
            for a, b in zip(self.__enc_beta, x[i]):
                enc_mul = self.__crypto.evaluator.multiply(a, b)
                self.__crypto.evaluator.relinearize_inplace(enc_mul, self.__crypto.relin_key)
                self.__crypto.evaluator.rescale_to_next_inplace(enc_mul)
                enc_mul.scale(self.__crypto.scale)
                betaxi.append(enc_mul)

            ip = self.__sum_enc_arr(betaxi)
            if ip.parms_id() != self.__enc_bias[0].parms_id():
                self.__crypto.evaluator.mod_switch_to_inplace(ip, ip.parms_id())
                self.__crypto.evaluator.mod_switch_to_inplace(self.__enc_bias[0], ip.parms_id())
            ip = self.__crypto.evaluator.add(ip, self.__enc_bias[0])
            res.append(ip)
        return res
