import datetime
import OpenSSL
import os
import random
import socket
from Core.File import File

# Reference: https://pyopenssl.org/en/stable/api/crypto.html
# Reference: https://skippylovesmalorie.wordpress.com/2010/02/12/how-to-generate-a-self-signed-certificate-using-pyopenssl/
# openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
class Security():

    @staticmethod
    def generateKeysAndCertificate(privateKeyPath, publicKeyPath, certificatePath):
        File.deletes([privateKeyPath, publicKeyPath, certificatePath])
        key = OpenSSL.crypto.PKey()
        key.generate_key(OpenSSL.crypto.TYPE_RSA, 2048)
        certificate = OpenSSL.crypto.X509()
        certificate.get_subject().C = "US"
        certificate.get_subject().ST = "Oregon"
        certificate.get_subject().L = "Portland"
        certificate.get_subject().O = "Georgia Tech"
        certificate.get_subject().OU = "Cocoscats"
        certificate.get_subject().CN = socket.gethostname()
        certificate.set_serial_number(random.randint(1, 99999999999))
        certificate.gmtime_adj_notBefore(0)
        certificate.gmtime_adj_notAfter(10*365*24*60*60)
        certificate.set_issuer(certificate.get_subject())
        certificate.set_pubkey(key)
        certificate.sign(key, "sha512")
        File.setContent(
            privateKeyPath,
            OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, key), True, True)
        File.setContent(
            publicKeyPath,
            OpenSSL.crypto.dump_publickey(OpenSSL.crypto.FILETYPE_PEM, key), True, True)
        File.setContent(
            certificatePath,
            OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, certificate), True, True)
