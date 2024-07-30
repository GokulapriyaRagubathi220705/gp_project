from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
#from django.shortcuts import redirect
import pymongo as py
con=py.MongoClient("mongodb+srv://gokulapriya:openpass@cluster0.jdrv7jt.mongodb.net/")
db=con['userdata']

# lbm-->library management-->it stores the signup datas
col=db['lbm']

# adbook-->add book-->added books are stored 
collection=db['adbook']

# lended books-->lended book details are stored
lend=db['lended_student_details']

#in this home page.we have two button.Admin and Student
def home_view(request):
    return render(request,"home_view.html")

# in this function process post request to determine whether the user is an admin or a student based on a form submission
def choose_admin_or_student(request):
    if request.POST["adm"]=="admi":
        return render(request,"Admin.html")                   
    else:
        return render(request,"student.html")
       
#  in this function check the admin id and password are correct    
def admin(request):
    if request.POST['ad']=="enter":
        if request.POST['id']=="22121045" and request.POST['pass']=='220705':
            return render(request,"add_or_report.html")
        else:
            return render(request,"admin.html",{'msg':'invalid'})
        
#  The add_and_report function processes a POST request to either render a form for adding a book or generate a report of all books, including lended books      
def add_and_report(request):
    if request.POST['adb'] == 'addb':
            return render(request, 'adbook.html')
    if request.POST['adb']=='back':
        return render(request,'home_view.html')
    if request.POST['adb']=='report':
        books = collection.find()
        books_list = list(books)
        lended_books = lend.find()
        lended_books_list = list(lended_books)
        all_books = books_list + lended_books_list  # Combine both lists for the report        
        return render(request, 'report.html', {'books': all_books})
    if request.POST['adb']=='bk':
        return render(request,"add_or_report.html")    
    
# this function handling the addition of new books.
def handle_added_books(request):
    if request.POST['btn'] == 'add':
        if request.POST['bname']=='' or request.POST['aname']=='':
            return render(request,'adbook.html',{'msg1':'all fields are required'})
        bname = request.POST['bname']
        aname = request.POST['aname']
        # Set the default book ID to 100
        default_bid = 100
        # Find the highest existing BOOK_ID
        highest_book = collection.find_one(sort=[("BOOK_ID", -1)])
        if highest_book:
            highest_bid = highest_book['BOOK_ID']
            bid = highest_bid + 1
        else:
            bid = default_bid
        
        val = {
            'BOOKNAME': bname,
            'AUTHORNAME': aname,
            'BOOK_ID': bid,
            'STATUS':0
        }
        collection.insert_one(val)
        return render(request, "adbook.html",{'msg':'Book added succesfully.enter a next book for add else click back'})
    else:
        return render(request, 'add_or_report.html')
    
# This function handles the signup and login button
def student(request):
    if request.POST['btn']=='sign':
        return render(request,"signup.html")
    elif request.POST['btn']=='log':
        return render(request,"login.html")
    else:
        return render(request,'home_view.html')
# The signup data are stored in the col collection            
def signup(request):
    if request.POST['signup']=='back':
        return render(request,'student.html')
    
    s = []
    required_fields = ['name', 'reg', 'gender', 'dept', 'psw', 'eml', 'signup']
    
    # Check if all required fields are in the POST data
    if all(field in request.POST for field in required_fields):
        if request.POST['signup'] == 'check':
            name = request.POST['name']
            reg = request.POST['reg']
            gender = request.POST['gender']
            dept = request.POST['dept']
            psw = request.POST['psw']
            eml = request.POST['eml']

            # Save the entered data to pass back to the template
            form_data = {
                'name': name,
                'reg': reg,
                'gender': gender,
                'dept': dept,
                'psw': psw,
                'eml': eml
            }

            # Validate the inputs
            if not name:
                return render(request, "signup.html", {'msg': "Name is required", 'form_data': form_data})
            elif name.isdigit():
                return render(request, "signup.html", {'msg': "Name should contain only characters", 'form_data': form_data})
            elif not reg.isdigit():
                return render(request, "signup.html", {'msg1': "Registration number should contain only digits", 'form_data': form_data})
            elif gender not in ["Male", "Female", "Other"]:
                return render(request, "signup.html", {'msg5': "Please choose a valid gender", 'form_data': form_data})
            elif dept not in ['ComputerScience', 'ComputerApplication', 'BusinessAdministration', 'DataScience']:
                return render(request, "signup.html", {"msg3": "Please choose a valid department", 'form_data': form_data})
            elif len(psw) != 8:
                return render(request, "signup.html", {"msg4": "Password must be 8 characters long", 'form_data': form_data})
            elif not eml:
                return render(request, "signup.html", {"msg6": "Email is required", 'form_data': form_data})
            else:
                s.append(name)
                s.append(reg)
                s.append(gender)
                s.append(dept)
                s.append(eml)
                s.append(psw)
                keys = ["Name", "Register Number", "Gender", "Department", "Email", "Password"]
                d = {keys[i]: s[i] for i in range(len(keys))}
                col.insert_one(d)
                return render(request, "signup.html", {'msg2': 'You have signed up successfully'})
    else:
        # If any required field is missing, return with an error message
        return render(request, "signup.html", {'msg': "All fields are required", 'form_data': {}})



    
def login(request):
    if request.POST['btn'] == 'check':
        name = request.POST['name']
        register_number = request.POST['reg']
        chk = col.find_one({'Name': name, 'Register Number': register_number})
        if chk:
            return render(request, "lendReturn.html", {'name': name, 'reg': register_number})
        else:
            return render(request, 'login.html', {'msg': 'invalid'})
    else:
        return render(request,"student.html")    

def lendReturn(request):
        if request.POST['len'] == 'lend':
            books = collection.find()
            book_list = list(books)
            return render(request, 'library.html', {'books': book_list, 'name': request.POST['name'], 'reg': request.POST['reg']})
        elif request.POST['len'] == 'return':
            lent_books = lend.find({'lended_by.student_name': request.POST['name'], 'lended_by.student_reg_no': request.POST['reg']})
            lent_book_list = list(lent_books)
            return render(request, 'return.html', {'lent_books': lent_book_list, 'name': request.POST['name'], 'reg': request.POST['reg']})
        else:
            return render(request,"login.html")

def lend_book(request):
    if request.POST['btn'] == 'le':
        book_name = request.POST['nbook']
        book_id = int(request.POST['bid'])
        student_name = request.POST['student_name']
        student_reg_no = request.POST['student_reg_no']
        # Validate that the student details match the login details
        if student_name != request.POST['name'] or student_reg_no != request.POST['reg']:
            books = collection.find()
            book_list = list(books)
            return render(request, 'library.html', {'msg5': 'Invalid user name and password','books': book_list})
        
        # Find the book in the collection
        book = collection.find_one({'BOOKNAME': book_name, 'BOOK_ID': book_id})
        if book:
            # Check if the book is available
            if book['STATUS'] == 0:
                # Remove the book from the collection
                collection.delete_one({'BOOKNAME': book_name, 'BOOK_ID': book_id})
                
                # Update the book status and lending information
                book['STATUS'] = 1
                book['lended_by'] = {
                    'student_name': student_name,
                    'student_reg_no': student_reg_no
                }
                
                # Insert the book into the lend collection
                lend.insert_one(book)
        else:
             books = collection.find()
             book_list = list(books)
             return render(request,'library.html',{'msg2':'invalid','books':book_list})   
        
        books = collection.find()
        book_list = list(books)
        return render(request, 'library.html', {'msg':'Book lended successfully','books':book_list})
    else:
        return render(request, 'lendReturn.html')

def return_book(request):
    if request.POST['bt']=='return':
        name = request.POST['name'] 
        reg = request.POST['reg']
        book_id = int(request.POST['bid'])
            # Check if the book exists and is lent by the current user
        book = lend.find_one({'BOOK_ID': book_id, 'lended_by.student_name': name, 'lended_by.student_reg_no': reg})
        if book:
                # Remove the book from the lend collection
            lend.delete_one({'BOOK_ID': book_id})
                
                # Update the book status and remove lending information
            book['STATUS'] = 0
            del book['lended_by']
                
                # Insert the book back into the collection
            collection.insert_one(book)
                
            msg = f'Book with ID {book_id} returned successfully'
        else:
            msg = f'Book with ID {book_id} not found or you are not authorized to return this book.'
            
            # Refresh list of lent books
        lend_books = lend.find({'lended_by.student_name': name, 'lended_by.student_reg_no': reg})
        lend_book_list = list(lend_books)
        return render(request, 'return.html', {'lent_books': lend_book_list, 'name': name, 'reg': reg, 'msg': msg})
    else:
        return render(request,"lendReturn.html")
