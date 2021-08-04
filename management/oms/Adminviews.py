from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json

from .models import CustomUser, Mentor, Admin, PartOrg, Student, Session, FeedBackStudent, FeedBackmentors, AttendanceReportStudent, AttendanceReportMentor, Assignment, AssignmentSubmission
from .forms import AddStudentForm, AddMentorForm

def admin_home(request):
    all_student_count = Student.objects.all().count()
    session_count = Session.objects.all().count()
    mentor_count = Mentor.objects.all().count()
    partorg_count = PartOrg.objects.all().count()

    session_all = Session.objects.all()
    session_name_list = []
    mentor_count_list_in_session = []
    student_count_list_in_session = []

    for session in session_all:
        studentreport = AttendanceReportStudent.objects.all().filter(session_id=session.id).filter(status=True).count()        
        mentorreport = AttendanceReportMentor.objects.all().filter(session_id=session.id).filter(status=True).count()
        session_name_list.append(session.session_title)
        student_count_list_in_session.append(studentreport)
        mentor_count_list_in_session.append(mentorreport)
    
    # For Mentors
    mentor_attendance_total_list=[]
    mentor_attendance_present_list=[]
    mentor_name_list=[]

    mentors = Mentor.objects.all()
    for mentor in mentors:
        total = attendance = AttendanceReportMentor.objects.all().filter(mentor_id=mentor.id).count()
        attendance = AttendanceReportMentor.objects.all().filter(mentor_id=mentor.id).filter(status=True).count()
        mentor_attendance_present_list.append(attendance)
        mentor_attendance_total_list.append(total)
        mentor_name_list.append(mentor.admin.first_name)

    # For Students
    student_attendance_present_list=[]
    student_attendance_total_list=[]
    student_name_list=[]

    students = Student.objects.all()
    for student in students:
        attendance = AttendanceReportStudent.objects.filter(student_id=student.id, status=True).count()
        total = AttendanceReportStudent.objects.filter(student_id=student.id).count()
        student_attendance_present_list.append(attendance)
        student_attendance_total_list.append(total)
        student_name_list.append(student.admin.first_name)

    context={
        "all_student_count": all_student_count,
        "session_count": session_count,
        "partorg_count": partorg_count,
        "mentor_count": mentor_count,
        
        "session_name_list": session_name_list,
        "student_count_list_in_session": student_count_list_in_session,
        "mentor_count_list_in_session": mentor_count_list_in_session,

        "mentor_attendance_present_list": mentor_attendance_present_list,
        "mentor_attendance_total_list": mentor_attendance_total_list,
        "mentor_name_list": mentor_name_list,
        
        "student_attendance_present_list": student_attendance_present_list,
        "student_attendance_total_list": student_attendance_total_list,
        "student_name_list": student_name_list,
    }
    return render(request, "Admin/home_content.html", context)

def add_mentor(request):
    return render(request, "Admin/add_mentor_template.html")

def add_mentor_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method ")
        return redirect('add_mentor')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=2)
            user.save()
            messages.success(request, "mentor Added Successfully!")
            return redirect('add_mentor')
        except:
            messages.error(request, "Failed to Add mentor!")
            return redirect('add_mentor')

def manage_mentor(request):
    mentors = Mentor.objects.all()
    context = {
        "mentors": mentors
    }
    return render(request, "Admin/manage_mentor_template.html", context)

def delete_mentor(request, mentor_id):
    mentor = Mentor.objects.get(admin=mentor_id)
    try:
        mentor.delete()
        messages.success(request, "mentor Deleted Successfully.")
        return redirect('manage_mentor')
    except:
        messages.error(request, "Failed to Delete mentor.")
        return redirect('manage_mentor')

def add_partorg(request):
    return render(request, "Admin/add_partorg_template.html")

def add_partorg_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method ")
        return redirect('add_partorg')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=3)
            user.save()
            messages.success(request, "Participating Organization Added Successfully!")
            return redirect('add_partorg')
        except:
            messages.error(request, "Failed to Add Participating Organization!")
            return redirect('add_partorg')

def manage_partorg(request):
    partorgs = PartOrg.objects.all()
    context = {
        "partorgs": partorgs
    }
    return render(request, "Admin/manage_partorg_template.html", context)

def delete_partorg(request, partorg_id):
    partorg = PartOrg.objects.get(admin=partorg_id)
    try:
        partorg.delete()
        messages.success(request, "Participating Organization Deleted Successfully.")
        return redirect('manage_partorg')
    except:
        messages.error(request, "Failed to Delete Participating Organization.")
        return redirect('manage_partorg')

def manage_session(request):
    sessions = Session.objects.all()
    context = {
        "session": sessions
    }
    if(request.user.user_type=='1'):
        return render(request, 'Admin/manage_session_template.html', context)    
    return render(request, 'Mentor/manage_session_template.html', context)

def add_session(request):
    if(request.user.user_type=='1'):
        return render(request, "Admin/add_session_template.html")    
    return render(request, "Mentor/add_session_template.html")

def add_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method ")
        return redirect('add_session')
    else:
        session_title = request.POST.get('session_title')
        session_url = request.POST.get('session_url')
        session_start_date = request.POST.get('session_start_date')

        try:
            session = Session(session_title=session_title, session_url=session_url, session_start_date=session_start_date)
            session.save()
            messages.success(request, "Session Added Successfully!")
            return redirect('add_session')
        except:
            messages.error(request, "Failed to Add Session!")
            return redirect('add_session')

def delete_session(request, session_id):
    session = Session.objects.get(id=session_id)
    try:
        session.delete()
        messages.success(request, "session Deleted Successfully.")
        return redirect('manage_session')
    except:
        messages.error(request, "Failed to Delete session.")
        return redirect('manage_session')

@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    user_obj = CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)

def student_feedback_message(request):
    feedbacks = FeedBackStudent.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'Admin/student_feedback_template.html', context)

@csrf_exempt
def student_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedBackStudent.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")

def mentor_feedback_message(request):
    feedbacks = FeedBackmentors.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'Admin/mentor_feedback_template.html', context)


@csrf_exempt
def mentor_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedBackmentors.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")

def admin_view_attendance(request):
    ssessions = Session.objects.all()
    context = {
        "sessions": sessions,
    }
    return render(request, "Admin/admin_view_attendance.html", context)

@csrf_exempt
def admin_get_attendance(request):
    session_id = request.POST.get("session")
    studentreport = AttendanceReportStudent.objects.all().filter(session_id=session.id).filter(status=True).count()        
    mentorreport = AttendanceReportMentor.objects.all().filter(session_id=session.id).filter(status=True).count()
    list_data = []
    list_data.append(studentreport)
    list_data.append(mentorreport)
    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)

def mentor_profile(request):
    pass

def student_profile(requtest):
    pass



