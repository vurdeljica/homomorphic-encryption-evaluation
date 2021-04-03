import math

from lsvm.lsvm_base import LsvmBase
import numpy as np
import seal


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


class LsvmSealBatch(LsvmBase):
    def __init__(self, model_name):
        super().__init__(model_name)

        parms = seal.EncryptionParameters(seal.scheme_type.ckks)
        poly_modulus_degree = 8192
        parms.set_poly_modulus_degree(poly_modulus_degree)
        parms.set_coeff_modulus(seal.CoeffModulus.Create(poly_modulus_degree, [60, 40, 40, 60]))
        scale = 2.0 ** 40
        context = seal.SEALContext(parms)
        ckks_encoder = seal.CKKSEncoder(context)
        slot_count = ckks_encoder.slot_count()
        keygen = seal.KeyGenerator(context)
        public_key = keygen.create_public_key()
        secret_key = keygen.secret_key()
        relin_key = keygen.create_relin_keys()
        galois_keys = keygen.create_galois_keys()

        encryptor = seal.Encryptor(context, public_key)
        evaluator = seal.Evaluator(context)
        decryptor = seal.Decryptor(context, secret_key)

        self.__crypto = CryptoContext(parms, scale, context, ckks_encoder, slot_count, keygen,
                                      public_key, secret_key, relin_key, galois_keys, encryptor, evaluator, decryptor)

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
            enc_x_row = self.__crypto.ckks_encoder.encode(row, self.__crypto.scale)
            enc_x_row = self.__crypto.encryptor.encrypt(enc_x_row)
            enc_x.append(enc_x_row)
        return enc_x

    def __sum_enc_arr(self, arr_enc, arr_len):
        all_rotations = [arr_enc]
        for i in range(arr_len):
            rot_arr = self.__crypto.evaluator.rotate_vector(all_rotations[-1], 1, self.__crypto.galois_key)
            all_rotations.append(rot_arr)

        return self.__crypto.evaluator.add_many(all_rotations)

    def __encrypt_arr(self, arr):
        enc_arr = self.__crypto.ckks_encoder.encode(arr, self.__crypto.scale)
        enc_arr = self.__crypto.encryptor.encrypt(enc_arr)
        return enc_arr

    def __lsvm(self, x):
        res = []
        for i in range(len(self.__enc_x)):
            betaxi = self.__crypto.evaluator.multiply(self.__enc_beta, self.__enc_x[i])
            self.__crypto.evaluator.relinearize_inplace(betaxi, self.__crypto.relin_key)
            self.__crypto.evaluator.rescale_to_next_inplace(betaxi)
            betaxi.scale(self.__crypto.scale)
            ip = self.__sum_enc_arr(betaxi, len(self._x[0]))

            if ip.parms_id() != self.__enc_bias.parms_id():
                self.__crypto.evaluator.mod_switch_to_inplace(ip, ip.parms_id())
                self.__crypto.evaluator.mod_switch_to_inplace(self.__enc_bias, ip.parms_id())

            self.__crypto.evaluator.add_inplace(ip, self.__enc_bias)
            res.append(ip)
        return res
