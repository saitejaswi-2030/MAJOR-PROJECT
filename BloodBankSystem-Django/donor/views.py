from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum,Q
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.core.mail import send_mail
from django.contrib.auth.models import User,auth
from blood import forms as bforms
from blood import models as bmodels
from donor.models import forgot_pwd_model
from donor.models import Donor
from django.contrib import messages

def donor_signup_view(request):
    userForm=forms.DonorUserForm()
    donorForm=forms.DonorForm()
    mydict={'userForm':userForm,'donorForm':donorForm}
    if request.method=='POST':
        userForm=forms.DonorUserForm(request.POST)
        donorForm=forms.DonorForm(request.POST,request.FILES)
        if userForm.is_valid() and donorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            donor=donorForm.save(commit=False)
            donor.user=user
            donor.bloodgroup=donorForm.cleaned_data['bloodgroup']
            donor.save()
            my_donor_group = Group.objects.get_or_create(name='DONOR')
            my_donor_group[0].user_set.add(user)
        return HttpResponseRedirect('donorlogin')
    return render(request,'donor/donorsignup.html',context=mydict)


def donor_dashboard_view(request):
    donor= models.Donor.objects.get(user_id=request.user.id)
    dict={
        'requestpending': bmodels.BloodRequest.objects.all().filter(request_by_donor=donor).filter(status='Pending').count(),
        'requestapproved': bmodels.BloodRequest.objects.all().filter(request_by_donor=donor).filter(status='Approved').count(),
        'requestmade': bmodels.BloodRequest.objects.all().filter(request_by_donor=donor).count(),
        'requestrejected': bmodels.BloodRequest.objects.all().filter(request_by_donor=donor).filter(status='Rejected').count(),
    }
    return render(request,'donor/donor_dashboard.html',context=dict)


def donate_blood_view(request):
    donation_form=forms.DonationForm()
    if request.method=='POST':
        donation_form=forms.DonationForm(request.POST)
        if donation_form.is_valid():
            blood_donate=donation_form.save(commit=False)
            blood_donate.bloodgroup=donation_form.cleaned_data['bloodgroup']
            donor= models.Donor.objects.get(user_id=request.user.id)
            blood_donate.donor=donor
            blood_donate.save()
            return HttpResponseRedirect('donation-history')  
    return render(request,'donor/donate_blood.html',{'donation_form':donation_form})

def donation_history_view(request):
    donor= models.Donor.objects.get(user_id=request.user.id)
    donations=models.BloodDonate.objects.all().filter(donor=donor)
    return render(request,'donor/donation_history.html',{'donations':donations})

def make_request_view(request):
    request_form=bforms.RequestForm()
    if request.method=='POST':
        request_form=bforms.RequestForm(request.POST)
        if request_form.is_valid():
            blood_request=request_form.save(commit=False)
            blood_request.bloodgroup=request_form.cleaned_data['bloodgroup']
            name=request_form.cleaned_data['patient_name']
            mobile=request_form.cleaned_data['phone_no']
            donor= Donor.objects.get(user_id=request.user.id)
            blood_request.request_by_donor=donor
            blood_request.save()
            matching_donors = Donor.objects.filter(
                bloodgroup=blood_request.bloodgroup,
                address__icontains=blood_request.location
            )

            donor_mail=[]
            
            for donor in matching_donors:
                donor_mail.append(donor.email)
            subject = 'Request for Blood'
            message = str(name)+" needs "+str(blood_request.bloodgroup)+"  blood. Which matches to your blood group and that person is in your location . So please contact him and donate blood . Contact No : "+str(mobile)
                #user=Donor.objects.get(name=username)
                #print(type(user.email))
            from_email = '2k24cst@gmail.com'
            recipient_list = donor_mail
            send_mail(subject, message, from_email, recipient_list)
            return HttpResponseRedirect('request-history')  
    return render(request,'donor/makerequest.html',{'request_form':request_form})

def request_history_view(request):
    donor= models.Donor.objects.get(user_id=request.user.id)
    blood_request=bmodels.BloodRequest.objects.all().filter(request_by_donor=donor)
    return render(request,'donor/request_history.html',{'blood_request':blood_request})


# def forgotpwd_view(request):
   
#     try:
#         if request.method=="POST":
#             email=request.POST['email']
#             db_mail_store=models.forgot_pwd_model.objects.create(emails=email)
#             db_mail_store.save()

#             check_email=User.objects.get(email=email)
#             # print(check_email.email)
            
#             # print(check_email.id)
#             try:
#                 name=check_email
#                 message="Please click the following link to change your password: http://127.0.0.1:8000/pwd_change/"
#                 send_mail(name,message,"settings.EMAIL_HOST_USER",[email],fail_silently=False)
#                 msg="Mail sent successfully"
#                 return render(request,"home/reset_password.html",{"msg":msg})
#             # return email
#             except:
#                 print("Problem with sending mail")
#     except:
#         msg="No email found"
#         return render(request,"home/reset_password.html",{"msg":msg})
#     return render(request,"home/reset_password.html")


def pwd_change_view(request):
    return render(request,"donor/pwd_change.html")

def forgotpwd_view(request):
    try:
        if request.method=="POST":
            mail=request.POST['email']
            check_email=Donor.objects.get(email=mail)
            db_mail_store=forgot_pwd_model.objects.create(emails=mail)
            db_mail_store.save()
            # print(check_email.id)
            try:
                name=check_email
                message="http://127.0.0.1:8000/donor/pwd_change/"
                from_email = '2k24cst@gmail.com'
                send_mail(name,message,from_email,[mail],fail_silently=False)
                msg="Mail sent successfully"
                return render(request,"donor/forgotpwd.html",{"msg":msg})# return email
            except:
                print("Problem with sending mail")
    except:
        msg="No email found"
        return render(request,"donor/forgotpwd.html",{"msg":msg})
    return render(request,"donor/forgotpwd.html")

# def update_password(request):
#     mail_id=forgot_pwd_model.objects.all().first()
#     # print(mail_id)
#     user_details=User.objects.get(email=mail_id.emails)
#     # print(user_details)
#     # print(mail_id.emails)
#     # print(user_details.user.password)
#     if request.method=="POST":
#         password=request.POST['password']
#         print(password)
#         confirm=request.POST['confirmpassword'] 
#         user_details.set_password(password)
#         user_details.save()
#         print("password updated")
        
#     return render(request,"donor/pwd_change.html")


def update_password(request):
    mail_ids = forgot_pwd_model.objects.all().first()
    
    if request.method == "POST":
        password = request.POST['password']
        confirm = request.POST['confirmpassword']
        try:
            user_details = User.objects.get(email=mail_ids.emails)
            user_details.set_password(password)
            user_details.save()
            mail_ids.delete()
            print(f"Password updated for user with email: {mail_ids.emails}")
        except User.DoesNotExist:
            print(f"User with email {mail_ids.emails} not found.")

    print("All passwords updated")

    return render(request, "donor/pwd_change.html")

# def save(self):  # create new user
#         the_user = User.objects.get(id=int(self.cleaned_data['user_id']))
#         if self.cleaned_data['password1'] != "":
#             the_user.set_password(self.cleaned_data['password1'])
#             the_user.save()
#         return the_user