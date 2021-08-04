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

def mentor_home(request):
    students = Student.objects.filter(mentor_id=request.user.id)
    students_count = students.count()

    total = AttendanceReportMentor.objects.filter(mentor_id=request.user.id).count()
    present = AttendanceReportMentor.objects.filter(mentor_id=request.user.id).filter(status=True).count()
    
    feedback_count = FeedBackStudent.objects.all().count()

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
        "students_count": students_count,
        "total":total,
        "present":present,
        "feedback_count": feedback_count,
        "student_name_list": student_name_list,
        "attendance_present_list": student_attendance_present_list,
        "attendance_total_list": student_attendance_total_list
    }
    return render(request, "Mentor/mentor_home_template.html", context)

def mentor_feedback(request):
    mentor_obj = Mentor.objects.get(admin=request.user.id)
    feedback_data = FeedBackmentors.objects.filter(mentor_id=mentor_obj)
    context = {
        "feedback_data":feedback_data
    }
    return render(request, "Mentor/mentor_feedback_template.html", context)

def mentor_feedback_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method.")
        return redirect('mentor_feedback')
    else:
        feedback = request.POST.get('feedback_message')
        mentor_obj = Mentor.objects.get(admin=request.user.id)

        try:
            add_feedback = FeedBackmentors(mentor_id=mentor_obj, feedback=feedback, feedback_reply="")
            add_feedback.save()
            messages.success(request, "Feedback Sent.")
            return redirect('mentor_feedback')
        except:
            messages.error(request, "Failed to Send Feedback.")
            return redirect('mentor_feedback')

def mentor_attendance(request):
    sessions = Session.objects.filter(deadline__gte=datetime.datetime.now().date())
    context = {
        "sessions": sessions,
    }
    return render(request, "Mentor/mentor_attendance_template.html", context)

def save_mentor_attendance(request):
    session_id = request.POST.get("session_id")
    status = request.POST.get("status")
    try:
        attendance = AttendanceReportMentor(session_id=session_id, mentor_id=request.user.id, status=status)
        attendance.save()
        return redirect('mentor_attendance')
    except:
        return redirect('mentor_attendance')

def get_students_attendance(request):
    
    students = Student.objects.filter(mentor_id=request.user.id)
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
        "student_name_list": student_name_list,
        "attendance_present_list": student_attendance_present_list,
        "attendance_total_list": student_attendance_total_list
    }
    return render(request, "Mentor/mentor_student_attendance.html", context)

def mentor_add_result(request):
    assignments = Assignment.objects.filter(mentor_id=request.user.id)
    submission_list = []
    for assignment in assignments:
        submissions = AssignmentSubmission.objects.filter(assignment_id=assignment.id)
        for submission in submissions:
            submission_list.append(submission)
    context = {
        "submissions": submission_list,
    }
    return render(request, "Mentor/result_template.html", context)

def view_submission(request):
    submission_id = request.POST.get("submission_id")
    submission = AssignmentSubmission.objects.filter(id=submission_id)
    assignment = Assignment.objects.filter(id=submission.assignment_id)
    context = {
        "assignment":assignment,
        "submission": submission,
    }
    return render(request, "Mentor/add_result_template.html", context)

def mentor_add_result_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('mentor_add_result')
    else:
        marks = request.POST.get('marks')
        submission_id = request.POST.get('submission_id')
        try:
            subm=AssignmentSubmission.objects.get(id=submission_id)
            submission = AssignmentSubmission(instance=subm)
            submission.marks=marks
            submission.save()
            messages.success(request, "Result Updated Successfully!")
            return redirect('mentor_add_result')
        except:
            messages.error(request, "Failed to Add Result!")
            return redirect('mentor_add_result')

def add_student(request):
    form = AddStudentForm()
    context = {
        "form": form
    }
    if(request.user.user_type=='1'):
        return render(request, 'Admin/add_student_template.html', context)    
    return render(request, 'Mentor/add_student_template.html', context)

def add_student_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_student')
    else:
        form = AddStudentForm(request.POST, request.FILES)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            gender = form.cleaned_data['gender']

            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None
            try:
                user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=4)
                user.student.gender = gender
                user.student.profile_pic = profile_pic_url
                user.save()
                messages.success(request, "Student Added Successfully!")
                return redirect('add_student')
            except:
                messages.error(request, "Failed to Add Student!")
                return redirect('add_student')
        else:
            return redirect('add_student')

def manage_student(request):
    students = Student.objects.all()
    context = {
        "students": students
    }
    if(request.user.user_type=='1'):
        return render(request, 'Admin/manage_student_template.html', context)    
    return render(request, 'Mentor/manage_student_template.html', context)

def delete_student(request, student_id):
    student = Student.objects.get(admin=student_id)
    try:
        student.delete()
        messages.success(request, "Student Deleted Successfully.")
        return redirect('manage_student')
    except:
        messages.error(request, "Failed to Delete Student.")
        return redirect('manage_student')

def add_assignment(request):
    return render(request, "Mentor/add_assignment_template.html")

def add_assignment_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method ")
        return redirect('add_assignment')
    else:
        assignment_title = request.POST.get('assignment_title')
        deadline = request.POST.get('deadline')

        if len(request.FILES) != 0:
            assignment_file = request.FILES['assignment_file']
            fs = FileSystemStorage()
            filename = fs.save(assignment_file.name, assignment_file)
            assignment_file_url = fs.url(filename)
        else:
            assignment_file_url = None
        try:
            assi = Assignment(assignment_title=assignment_title,assignment_file=assignment_file_url,deadline=deadline)
            assi.save()
            messages.success(request, "Assignment Added Successfully!")
            return redirect('add_assignment')
        except:
            messages.error(request, "Failed to Add Assignment!")
            return redirect('add_assignment')            

def delete_assignment(request, assignment_id):
    assignment = Assignment.objects.get(id=assignment_id)
    try:
        assignment.delete()
        messages.success(request, "assignment Deleted Successfully.")
        return redirect('manage_assignment')
    except:
        messages.error(request, "Failed to Delete assignment.")
        return redirect('manage_assignment')

def manage_assignment(request):
    assignments = Assignment.objects.all()
    context = {
        "assignments": assignments
    }
    return render(request, 'Mentor/manage_assignment_template.html', context)