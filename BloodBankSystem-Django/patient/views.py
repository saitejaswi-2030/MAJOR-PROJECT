from django.shortcuts import render,redirect,reverse

from donor.models import Donor
from . import forms,models
from django.db.models import Sum,Q
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta

from django.core.mail import send_mail
from django.contrib.auth.models import User
from blood import forms as bforms
from blood import models as bmodels
from patient.models import *


def patient_signup_view(request):
    userForm=forms.PatientUserForm()
    patientForm=forms.PatientForm()
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST)
        patientForm=forms.PatientForm(request.POST,request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.user=user
            patient.bloodgroup=patientForm.cleaned_data['bloodgroup']
            patient.save()
            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)
        return HttpResponseRedirect('patientlogin')
    return render(request,'patient/patientsignup.html',context=mydict)

def patient_dashboard_view(request):
    patient= Patient.objects.get(user_id=request.user.id)
    dict={
        'requestpending': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).filter(status='Pending').count(),
        'requestapproved': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).filter(status='Approved').count(),
        'requestmade': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).count(),
        'requestrejected': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).filter(status='Rejected').count(),

    }
   
    return render(request,'patient/patient_dashboard.html',context=dict)

def make_request_view(request):
    request_form=bforms.RequestForm()
    if request.method=='POST':
        request_form=bforms.RequestForm(request.POST)
        if request_form.is_valid():
            blood_request=request_form.save(commit=False)
            blood_request.bloodgroup=request_form.cleaned_data['bloodgroup']
            #blood=request_form.cleaned_data['bloodgroup']
            name=request_form.cleaned_data['patient_name']
            mobile=request_form.cleaned_data['phone_no']
            patient= Patient.objects.get(user_id=request.user.id)
            
            
            blood_request.request_by_patient=patient
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
            return HttpResponseRedirect('my-request')  
    return render(request,'patient/makerequest.html',{'request_form':request_form})

    #         blood_request=request_form.save(commit=False)
    #         blood_request.bloodgroup=request_form.cleaned_data['bloodgroup']
    #         patient= models.Patient.objects.get(user_id=request.user.id)
    #         blood_request.request_by_patient=patient
    #         blood_request.save()
    #         return HttpResponseRedirect('my-request')  
    # return render(request,'patient/makerequest.html',{'request_form':request_form})

def my_request_view(request):
    patient= Patient.objects.get(user_id=request.user.id)
    blood_request=bmodels.BloodRequest.objects.all().filter(request_by_patient=patient)
    return render(request,'patient/my_request.html',{'blood_request':blood_request})


def pwd_change_view(request):
    return render(request,"patient/pwd_change.html")

def forgotpwd_view(request):
    try:
        if request.method=="POST":
            mail=request.POST['email']
            check_email=User.objects.get(email=mail)
            db_mail_store=forgot_pwd_patient.objects.create(emails=mail)
            db_mail_store.save()
            # print(check_email.id)
            try:
                name=check_email
                message="http://127.0.0.1:8000/patient/pwd_change/"
                from_email = '2k24cst@gmail.com'
                send_mail(name,message,from_email,[mail],fail_silently=False)
                msg="Mail sent successfully"
                return render(request,"patient/forgotpwd.html",{"msg":msg})# return email
            except:
                print("Problem with sending mail")
    except:
        msg="No email found"
        return render(request,"patient/forgotpwd.html",{"msg":msg})
    return render(request,"patient/forgotpwd.html")


def update_password(request):
    mail_ids = forgot_pwd_patient.objects.all().first()
    
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

    return render(request, "patient/pwd_change.html")