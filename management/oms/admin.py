from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser,Admin, Mentor, PartOrg, Student, Session, FeedBackStudent, FeedBackmentors, AttendanceReportStudent, AttendanceReportMentor
from .models import Assignment, AssignmentSubmission

class UserModel(UserAdmin):
    pass
admin.site.register(CustomUser, UserModel)

admin.site.register(Admin)
admin.site.register(Mentor)
admin.site.register(PartOrg)
admin.site.register(Student)
admin.site.register(Session)
admin.site.register(FeedBackStudent)
admin.site.register(FeedBackmentors)
admin.site.register(AttendanceReportMentor)
admin.site.register(AttendanceReportStudent)
admin.site.register(Assignment)
admin.site.register(AssignmentSubmission)