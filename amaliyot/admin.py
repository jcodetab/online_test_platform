from django.contrib import admin
from .models import (
    Test, Question, Subject, Topic, Answer, Option, Choice, Result, 
    UserProfile, TestCompletion, QuestionImage, TestSession, 
    TestAnswer, Payment, TestQueue, Group, GroupMembership,
    Olympiad, OlympiadGroup, OlympiadParticipant, OlympiadAnswer, UploadedFile, ClosedTest, CaseQuestion, ClosedQuestion, CaseTest
)



admin.site.register(Choice)
admin.site.register(Option)
admin.site.register(Result)
admin.site.register(Subject)
admin.site.register(Topic)
admin.site.register(Answer)
admin.site.register(UserProfile)
admin.site.register(TestCompletion)
admin.site.register(QuestionImage)
admin.site.register(TestAnswer)
admin.site.register(TestQueue)




class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


class ClosedQuestionInline(admin.TabularInline):
    model = ClosedQuestion
    extra = 1


class CaseQuestionInline(admin.TabularInline):
    model = CaseQuestion  # Question emas, aynan CaseQuestion bo'lishi kerak
    extra = 1


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'amount', 'status', 'is_successful', 'created_at')
    list_filter = ('provider', 'status', 'is_successful', 'created_at')
    search_fields = ('user__username', 'transaction_id')
    readonly_fields = ('created_at', 'pay_time')
    ordering = ('-created_at',)


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'test', 'uploaded_at')
    search_fields = ('file', 'test__title')
    list_filter = ('uploaded_at',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'creator', 'created_at')
    search_fields = ('name', 'creator__username')
    list_filter = ('created_at',)
    ordering = ('-created_at',)


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'group', 'joined_at')
    search_fields = ('user__username', 'group__name')
    list_filter = ('joined_at', 'group')
    ordering = ('-joined_at',)


@admin.register(TestSession)
class TestSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_id', 'test', 'start_time', 'end_time', 'is_finished']
    readonly_fields = ['session_id']


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    # 'get_display_name' bu yerda ustun bo'lib xizmat qiladi
    list_display = ('title', 'get_display_name', 'subject', 'creator', 'created_at')
    list_filter = ('test_type', 'subject')
    search_fields = ('title',)


@admin.register(ClosedTest)
class ClosedTestAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'subject', 'user')
    inlines = [ClosedQuestionInline]


@admin.register(ClosedQuestion)
class ClosedQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'test', 'question_type', 'correct_answers')
    list_filter = ('test', 'question_type')
    search_fields = ('text',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'text', 'subject', 'topic', 'creator', 'test', 'closed_test', 'question_type', 'is_multiple_choice', 'is_paid', 'price', 'access_key']
    search_fields = ['text']
    list_filter = ['subject', 'topic', 'creator', 'question_type', 'is_multiple_choice', 'is_paid']


@admin.register(Olympiad)
class OlympiadAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'start_date', 'end_date', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['start_date', 'end_date']
    ordering = ('-created_at',)


@admin.register(OlympiadGroup)
class OlympiadGroupAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'olympiad', 'test', 
        'start_time', 'end_time', 'max_participants', 
        'get_creator_name'
    )
    
    # search_fields dagi userprofile qismini olib tashlang (agar profile bo'sh bo'lsa xato berishi mumkin)
    search_fields = ('name', 'test__title', 'created_by__username')
    
    # list_filter dan created_by ni vaqtincha olib tashlang
    list_filter = ('start_time', 'end_time', 'olympiad')
    
    ordering = ('-start_time',)

    def get_creator_name(self, obj):
        if obj.created_by:
            # Profil borligini tekshirishning xavfsiz usuli
            profile = getattr(obj.created_by, 'userprofile', None)
            if profile:
                return profile.full_name
            return obj.created_by.username
        return "Noma'lum"
        
    get_creator_name.short_description = "Yaratuvchi (Ism-Familiya)"


@admin.register(OlympiadParticipant)
class OlympiadParticipantAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'get_full_name',  # Ismni ko'rsatuvchi ustun
        'get_username',   # Loginni ko'rsatuvchi ustun (tekshirish uchun)
        'group', 
        'score', 
        'finished',
        'last_activity'
    )
    
    # Qidiruv tizimini yaxshilaymiz (Ism yoki login bo'yicha qidirish)
    search_fields = ('user__username', 'user__userprofile__first_name', 'user__userprofile__last_name')
    
    # Filtrlash (Guruh yoki natija bo'yicha)
    list_filter = ('group', 'finished')

    def get_full_name(self, obj):
        # Biz models.py da yozgan aqlli full_name property-sini chaqiramiz
        try:
            return obj.user.userprofile.full_name
        except:
            return "Profil yo'q"
    get_full_name.short_description = "Haqiqiy Ism-Familiya"

    def get_username(self, obj):
        # Foydalanuvchi loginini (username) chiqarish
        return obj.user.username
    get_username.short_description = "Login (Username)"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(user__is_staff=True) # Admin panelda ham xodimlarni ko'rsatmaydi


@admin.register(OlympiadAnswer)
class OlympiadAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'participant', 'question_id', 'is_correct', 'selected', 'answered_at')
    search_fields = ('participant__user__username', 'participant__group__name')
    list_filter = ('is_correct', 'answered_at')
    ordering = ('-answered_at',)


# admin.py
@admin.register(CaseTest)
class CaseTestAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'get_questions_count')

    def get_questions_count(self, obj):
        return obj.questions.count() # Question modelidagi related_name'ga qarang
    get_questions_count.short_description = "Savollar soni"


@admin.register(CaseQuestion)
class CaseQuestionAdmin(admin.ModelAdmin):
    # list_display - admin panelda ro'yxat bo'lib ko'rinadigan ustunlar
    # 'get_short_text' funksiyasi orqali matnni qisqartirib chiqaramiz
    list_display = ('id', 'get_short_text', 'case_test', 'get_answers_count')
    
    # Filtrlash (O'ng tomondagi panel)
    list_filter = ('case_test', 'case_test__subject')
    
    # Qidiruv maydoni (Savol matni va bog'langan test sarlavhasi bo'yicha)
    search_fields = ('text', 'case_test__title')
    
    # Savol matnini qisqartirib ko'rsatish uchun yordamchi funksiya
    def get_short_text(self, obj):
        return obj.text[:100] + "..." if len(obj.text) > 100 else obj.text
    get_short_text.short_description = 'Savol matni'

    # Nechta to'g'ri javob borligini ko'rsatish (JSONField tahlili)
    def get_answers_count(self, obj):
        if isinstance(obj.correct_answers, list):
            return len(obj.correct_answers)
        return 0
    get_answers_count.short_description = 'To\'g\'ri javoblar soni'
    
   














