# General imports
import os
import csv
import logging

# For model-related processing
import numpy as np
import pandas

# For encryption-related processing
import base64
from Crypto.Cipher import AES as aes
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import shutil


#google cloud
from gcloud import storage

# Configure this environment variable 
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "typinghabits-313215-4a15ed67186f.json"

def processRawTypingData(dwell_time, flight_time):
    calculation_array = []

    if len(flight_time)>len(dwell_time):
        counter = len(dwell_time)
    else:
        counter = len(flight_time)
    
    for x in range(counter):
        dt = float(dwell_time[x])/1000
        ft = float(flight_time[x])/1000
        d_plus_f = float(dt - ft)

        # save inside the calculation array --> 1 row of data
        calculation_array.append(dt)
        calculation_array.append(d_plus_f)
        calculation_array.append(ft)

    return calculation_array #return nicely processed flight/dwell time data (eg: array = [dwell1, dwell-flight1, flight1, dwell2, dwell-flight2, flight2, ... ])

def packTypingDataIntoArray(user, session, saving_attempt, accuracy, wpm, calculation_array):
    csv_obj = np.array([user, session, saving_attempt, accuracy, wpm], dtype=object)
    for i in calculation_array:
        csv_obj = np.append(csv_obj, i)
    return csv_obj

def ensureDirectoryExists(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

def saveCSV(username, csv_obj):
    folder = 'typing-habits' + '\\' + username
    
    # Checks
    ensureDirectoryExists('typing-habits') # ensure the typing habit folder exists
    ensureDirectoryExists(folder)

    # get your current directory .../typing-habits/user
    folder_path = os.path.dirname(os.path.realpath(folder))
    filename = folder_path + '\\' + username + '\\' + username + ".csv"
    with open(filename, 'a+', newline='\n') as x:
        csv_writer = csv.writer(x, delimiter=',')
        csv_writer.writerow(csv_obj)

# Opens the user's .csv file, get session number of last row of data,
def getLastSessionNumber(user):
    decryptCSV(user)
    folder = 'typing-habits' + '\\' + user
    folder_path = os.path.dirname(os.path.realpath(folder))
    filename = folder_path + '\\' + user + '\\' + user + ".csv"
    data = []
    row_index = 0
    with open(filename, "r", encoding="utf-8", errors="ignore") as scraped:
        reader = csv.reader(scraped, delimiter=',')
        for row in reader:
            if row:  # avoid blank lines
                row_index += 1
                columns = [str(row_index), row[0], row[1], row[2]]
                data.append(columns)
    last_row = data[-1]
    encryptCSV(user)
    return last_row[2]

def encryptCSV(username):

    key = get_random_bytes(16)
    iv = get_random_bytes(16)

    folder = 'typing-habits' + '\\' + username
    
    # Checks
    ensureDirectoryExists('typing-habits') # ensure the typing habit folder exists
    ensureDirectoryExists(folder)

    # get your current directory .../typing-habits/user
    folder_path = os.path.dirname(os.path.realpath(folder))
    filename = folder_path + '\\' + username + '\\' + username + ".csv"

    # open the unencrypted .csv 
    with open(filename, 'rb') as f:
        original = f.read()
    cipher = aes.new(key, aes.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(original, aes.block_size)) 

    appendedStr = bytearray(iv)
    appendedStr.extend(key)
    appendedStr.extend(encrypted)
    # replace with an encrypted version of the .csv
    with open(filename, 'wb+') as f:
        f.write(appendedStr)

    client = storage.Client()
    #bucket name
    bucket = client.get_bucket('typing-habit')

    #destination of storage
    blob = bucket.blob(username + '/' + username + ".csv")

    #Upload data based on the name of the file
    blob.upload_from_filename(filename)

    blob = bucket.blob(username + '/' + username + "_model.sav")

    blob.upload_from_filename(folder_path + '\\' + username + '\\' + username + "_model.sav")

    #remove local file
    shutil.rmtree('typing-habits\\' + username)

def decryptCSV(username):

    folder = 'typing-habits' + '\\' + username
    
    # Checks
    ensureDirectoryExists('typing-habits') # ensure the typing habit folder exists
    ensureDirectoryExists(folder)

    # get your current directory .../typing-habits/user
    folder_path = os.path.dirname(os.path.realpath(folder))
    filename = folder_path + '\\' + username + '\\' + username + ".csv"

    #Download from cloud
    storage_client = storage.Client()

    bucket = storage_client.bucket('typing-habit')

    blob = bucket.blob(username + '/' + username + ".csv")
    blob.download_to_filename(filename)

    blob = bucket.blob(username + '/' + username + "_model.sav")
    blob.download_to_filename(folder_path + '\\' + username + '\\' + username + "_model.sav")

    with open(filename, 'rb') as f:
        iv = f.read(16)
        f.seek(16)
        key = f.read(16)
        f.seek(32)
        enc = f.read()

    cipher = aes.new(key, aes.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(enc), aes.block_size)

    with open(filename, 'wb+') as f:
        f.write(decrypted)

# encryption
# key = get_random_bytes(16)
# iv = get_random_bytes(16)

# with open("key.txt", 'wb+') as f:
#     f.write(key)

# encryptCSV("test")

# decryption
# with open("key.txt", 'rb') as f:
#     key = f.read()

# decryptCSV("test")




# backup
#
# def encryptCSV(username, key, iv):
#     folder = 'typing-habits' + '\\' + username
    
#     # Checks
#     ensureDirectoryExists('typing-habits') # ensure the typing habit folder exists
#     ensureDirectoryExists(folder)

#     # get your current directory .../typing-habits/user
#     folder_path = os.path.dirname(os.path.realpath(folder))
#     filename = folder_path + '\\' + username + '\\' + username + ".csv"

#     # open the unencrypted .csv 
#     with open(filename, 'rb') as f:
#         original = f.read()
#     cipher = aes.new(key, aes.MODE_CBC, iv)
#     encrypted = cipher.encrypt(pad(original, aes.block_size))
#     # replace with an encrypted version of the .csv
#     with open(filename, 'wb+') as f:
#         f.write(encrypted)

# def decryptCSV(username, key, iv):
#     folder = 'typing-habits' + '\\' + username
    
#     # Checks
#     ensureDirectoryExists('typing-habits') # ensure the typing habit folder exists
#     ensureDirectoryExists(folder)

#     # get your current directory .../typing-habits/user
#     folder_path = os.path.dirname(os.path.realpath(folder))
#     filename = folder_path + '\\' + username + '\\' + username + ".csv"

#     with open(filename, 'rb') as f:
#         enc = f.read()
#     cipher = aes.new(key, aes.MODE_CBC, iv)
#     decrypted = unpad(cipher.decrypt(enc), aes.block_size)
    
#     with open(filename, 'wb+') as f:
#         f.write(decrypted)
