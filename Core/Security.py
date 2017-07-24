import base64
import datetime
import getpass
import hashlib
import OpenSSL
import os
from passlib.hash import pbkdf2_sha512
import random
import socket
import sys
import uuid
from Core.Error import Error
from Core.File import File
from Core.Msg import Msg
from Core.Text import Text

# Reference: https://pyopenssl.org/en/stable/api/crypto.html
# Reference: https://skippylovesmalorie.wordpress.com/2010/02/12/how-to-generate-a-self-signed-certificate-using-pyopenssl/
# Reference: https://tenzer.dk/generating-subresource-integrity-checksums/
# openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
class Security():

    @staticmethod
    def authenticate(path, password=None):
        if password == None:
            password = Security.promptForPassword(False)
        return Security.verifyPasswordByFile(password, path)

    @staticmethod
    def createPasswordFile(path):
        File.delete(path)
        p = Security.promptForPassword(True)
        Msg.flush()
        Msg.show("Thanks ... please wait")
        Msg.flush()
        h = Security.hashAndSaltPassword(p)
        File.setContent(path, {"Password": h}, asJson=True)

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
            OpenSSL.crypto.dump_privatekey(
                OpenSSL.crypto.FILETYPE_PEM, key), asBytes=True, mkdirs=True)
        File.setContent(
            publicKeyPath,
            OpenSSL.crypto.dump_publickey(
                OpenSSL.crypto.FILETYPE_PEM, key), asBytes=True, mkdirs=True)
        File.setContent(
            certificatePath,
            OpenSSL.crypto.dump_certificate(
                OpenSSL.crypto.FILETYPE_PEM, certificate), asBytes=True, mkdirs=True)

    @staticmethod
    def getRandomToken():
        return  uuid.uuid4()

    @staticmethod
    def getSubresourceIntegrityHash(path):
        content = File.getContent(path)
        hash = hashlib.sha512(content.encode("utf-8")).digest()
        return "sha512-{}".format(base64.b64encode(hash).decode())

    @staticmethod
    def hashAndSaltPassword(password):
        return pbkdf2_sha512.encrypt(password, rounds=999999, salt_size=64)

    @staticmethod
    def promptForPassword(isNewFlag=False):
        if isNewFlag:
            p1 = Security.__showHiddenPrompt("Enter a new password")
            p2 = Security.__showHiddenPrompt("Enter a new password again")
            if p1 != p2:
                Error.raiseException("Mismatched passwords")
            return p1
        return Security.__showHiddenPrompt("Enter your password")

    @staticmethod
    def __showHiddenPrompt(prompt):
        response = None
        sys.stdout.write("{0}: ".format(prompt))
        sys.stdout.flush()
        if sys.stdout.isatty():
            response = getpass.getpass(prompt="")
        else:
            if File.finds(["stty", "stty.exe"]) is not None:
                os.system("stty -echo")
                response = sys.stdin.readline()
                os.system("stty echo")
            else:
                response = input("")
        sys.stdout.write("\n")
        return response.rstrip()

    @staticmethod
    def verifyPassword(password, hash):
        return pbkdf2_sha512.verify(password, hash)

    @staticmethod
    def verifyPasswordByFile(password, path):
        return Security.verifyPassword(password, File.getContent(path, asJson=True)["Password"])