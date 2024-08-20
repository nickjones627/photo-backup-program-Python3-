import mysql.connector
import os
from getpass import getpass

#! DB connection
db = mysql.connector.connect(
    host='ipaddr', 
    user='username',
    password='password',
    database='db_name'
)


#! DB cursor object
cursor = db.cursor()

#############################!
###! ACTIVE USER ID ###

active_id = None

#! Clear the cursor objecct to prevent potential errors
def clear_cursor():
    try:
        cursor.fetchall()  #! Fetch all remaining results to clear the cursor
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_NO_RESULT_SET:
            pass
        else:
            raise

#! Fetch active_id and populate global variabe with the result
def active_user_id(username, password):
    global active_id
    cursor.execute("SELECT id FROM users WHERE username=%s AND password=%s", (username, password))
    result = cursor.fetchone()
    clear_cursor()  #! Clear cursor after fetching the result
    if result:
        active_id = result[0]  #! Extract the single value from the tuple

###! INTRO SECTION START ###

def accnt_verified(users):
    for key, value in users.items():
        greet_name = str(key).title()
    print(f'Welcome, {greet_name}.')

def create_account():
    name = input('Please enter a username: ')
    if len(name) < 1:
        print('Username cannot be blank..')
        create_account()
    pswd = input('Please enter a password: ')
    if len(pswd) < 1:
        print('Password cannot be blank..')
        create_account()
    users = {name: pswd}
    verify = input('Re-enter your password: ')
    if verify != pswd:
        print('Passwords did not match, please try again..')
        create_account()()
    else:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (name, pswd))
        db.commit()
        active_user_id(name, pswd)
        accnt_verified(users)
        menu()

def login():
    name = input('Username: ')
    pswd = getpass()
    cursor.execute("SELECT username FROM users WHERE username=%s AND password=%s", (name, pswd))
    result = cursor.fetchone()
    clear_cursor()  #! Clear cursor after fetching the result
    if result:
        print('Login Successful')
        active_user_id(name, pswd)
        menu()
    else:
        print('Unrecognized account.. Please try again')
        login()

def log_out():
    global active_id
    active_id = None
    print('\nLogged out successfully.\n')
    sign_up_or_sign_in()

def sign_up_or_sign_in():
    print('1. Create An Account\n2. Login To Your Account')
    up_or_in = input('')
    if up_or_in == '1':
        create_account()
    elif up_or_in == '2':
        login()
    else:
        print('Invalid selection.. Please try again')
        sign_up_or_sign_in()

def total_storage_available(gb):
    if gb > float(0.000001):
        print('Storage capacity exceeded. Please upgrade your plan for more space..')

###! INTRO SECTION END ###
#########################!
###! MAIN SECTION START ###


def get_image_name(path):
    print(path.split('\\')[-1])

#! Upload BLOB data to store picture
def InsertBlob(FilePath):
    global active_id
    if not active_id:
        print("No active user ID found. Please log in.")
        return

    try:
        with open(FilePath, "rb") as File:
            BinaryData = File.read()

        SQLStatement = 'INSERT INTO photos (user_id, title, photo) VALUES (%s, %s, %s)'

        fp = FilePath.split('\\')[-1][0:-4]

        #! Ensure any previous results are handled
        clear_cursor()  #! Fetch all remaining results to clear the cursor
        cursor.execute(SQLStatement, (active_id, fp, BinaryData))
        db.commit()
        print("Image inserted successfully.")
        menu()

    except FileNotFoundError:
        print('\nFile not found. Please double check the path and try again..\n')
        menu()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        menu()
    except PermissionError:
        print('Permission Denied')
        menu()

#! Read BLOB data to python and insert image into 'images' folder
def RetrieveBlob(ID):
    try:
        SQLStatement2 = "SELECT photo FROM photos WHERE user_id = %s AND photo_id = %s"
        cursor.execute(SQLStatement2, (active_id, ID))
        result = cursor.fetchone()
        
        if result is None:
            print(f"No photo found with ID {ID}.")
            menu()
            return
        
        MyResult = result[0]
        
        if not isinstance(MyResult, (bytes, bytearray)):
            print(f"Unexpected data type: {type(MyResult)}. Expected bytes or bytearray.")
            menu()
            return

        sqlstatement3 = "SELECT title FROM photos WHERE user_id = %s AND photo_id = %s"
        cursor.execute(sqlstatement3, (active_id, ID))
        result = cursor.fetchone()

        StoreFilePath = "my_images/{}.jpg".format(result[0][0:])
        print(f"Writing data to {StoreFilePath}")
        
        with open(StoreFilePath, "wb") as File:
            File.write(MyResult)
        
        print("Image retrieved and saved successfully.")
        menu()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        menu()
    except TypeError as err:
        print(f"TypeError: {err}")
        menu()

#! Convert bytes to GB
def bytes_to_gb(bytes_size):
    try:
        gb_size = bytes_size / (1024 ** 3)
        return gb_size
    except TypeError:
        return 0

#! Check the storage capacity used
def check_total_storage_used():
    try:
        # SQL query to get the total size of all photo data
        SQLStatement = "SELECT SUM(LENGTH(photo)) AS total_size FROM photos"
        cursor.execute(SQLStatement)
        result = cursor.fetchone()
        try:
            total_size_in_bytes = result[0]
            total_size_in_gb = bytes_to_gb(total_size_in_bytes)
            print(f"Total storage used: ({total_size_in_gb:.6f} GB / 5 GB)")
        except TypeError:
            print('Total storage user: (0 GB / 5 GB)')
        if total_size_in_gb > 5:
            print('Storage Limit Exceeded..')

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        


#! Delete BLOB data from SQL database and 'images' folder
def DeleteBlob(ID):
    try:
        sqlstatement4 = "SELECT title FROM photos WHERE user_id=%s AND photo_id=%s"
        cursor.execute(sqlstatement4, (active_id, ID))
        result = cursor.fetchone()

        DelFilePath = "my_images/{}.jpg".format(result[0][0:])
        if os.path.exists(DelFilePath):
            os.remove(DelFilePath)
            print('Image successfully removed..')

        SQLStatement3 = "DELETE FROM photos WHERE user_id = %s AND photo_id = %s"
        cursor.execute(SQLStatement3, (active_id, ID))
        db.commit()
        menu()
    except FileNotFoundError:
        print('\nNo file with that ID exists..\n')
        menu()

#! View list of stored image ID's
def my_images():
    global active_id
    try:
        cursor.execute("SELECT photo_id FROM photos WHERE user_id=%s", (active_id,))
        result1 = cursor.fetchone()
        cursor.execute("SELECT title FROM photos WHERE user_id=%s", (active_id,))
        result2 = cursor.fetchone()
        print("Your images:")
        print(f"Image ID: {result1[0]} Title: {result2[0]}")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    except TypeError:
        print('No Images Found..')

    #! Ensure any previous results are handled
    clear_cursor()
    menu()

#! Main menu section 
def menu():
    print()
    check_total_storage_used()
    print()
    sqlstatement = "SELECT * FROM photos WHERE user_id=%s"
    cursor.execute(sqlstatement, (active_id,))
    result = cursor.fetchall()
    if result == []:
        id_reset = "ALTER TABLE photos AUTO_INCREMENT=1"
        cursor.execute(id_reset)
        db.commit()
    
    print(f"1. Insert Image\n2. Read Image\n3. Delete Image\n4. My Images\n5. Log Out")
    menu_input = input('')
    try:
        if int(menu_input) == 1:
            usr_file_path = input('Type "quit" to exit or Enter File Path: ')
            if usr_file_path == 'quit':
                menu()
            else:
                InsertBlob(usr_file_path)
        elif int(menu_input) == 2:
            UserIDChoice = input('Type "quit" to exit or Enter Image ID: ')
            if UserIDChoice == 'quit':
                menu()
            else:
                RetrieveBlob(UserIDChoice)
        elif int(menu_input) == 3:
            UserIDChoice = input('Type "quit" to exit or Enter Image ID: ')
            if UserIDChoice == 'quit':
                menu()
            else:
                DeleteBlob(UserIDChoice)
        elif int(menu_input) == 4:
            my_images()
        elif int(menu_input) == 5:
            log_out()
        else:
            print('Invalid Selection..')
            menu()
    except ValueError:
        print('Invalid Selection..')
        menu()

###! MAIN SECTION END ###

sign_up_or_sign_in()

