from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import User, Test, Question, Choice, TestQueue, Answer, Option, TestCompletion, UserTest, UserProfile, Task, Result, Subject, Topic, QuestionImage, Payment, UploadedFile, TestSession, UserAnswer, TestAnswer, Group, GroupMembership, OlympiadGroup, OlympiadParticipant, OlympiadAnswer, ClosedTest, ClosedQuestion, ClosedTestSession, ClosedAnswer, CaseTest, CaseQuestion
from .models import UserProfile
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.validators import UniqueValidator
from .models import Test
from django.contrib.auth import get_user_model
from .models import Group, GroupMembership, ChatMessage
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
import json



class DashboardStatsSerializer(serializers.Serializer):
    total_tests = serializers.IntegerField()
    active_tests = serializers.IntegerField()
    total_users = serializers.IntegerField()
    new_users = serializers.IntegerField()
    total_groups = serializers.IntegerField()
    olympiad_groups = serializers.IntegerField()
    total_olympiads = serializers.IntegerField()
    upcoming_olympiads = serializers.IntegerField()


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="Bu login band.")]
    )
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="Bu email band.")]
    )
    password = serializers.CharField(write_only=True, min_length=6)
    
    first_name = serializers.CharField(required=True, allow_blank=False)
    last_name = serializers.CharField(required=True, allow_blank=False)

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name"]

    def create(self, validated_data):
        
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"], 
            last_name=validated_data["last_name"],
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Bunday foydalanuvchi yo‘q")

        user = authenticate(username=user.username, password=password)
        if not user:
            raise serializers.ValidationError("Parol noto‘g‘ri")

        data["user"] = user
        return data
    

class ClosedAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClosedAnswer
        fields = ['id', 'session', 'question', 'selected_answers', 'is_correct']


class ClosedTestSessionSerializer(serializers.ModelSerializer):
    answers = ClosedAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = ClosedTestSession
        fields = [
            'id', 'user', 'test', 'started_at', 'completed_at', 
            'score_obtained', 'answers'
        ]


class CaseTestSerializer(serializers.ModelSerializer):
    creator_name = serializers.SerializerMethodField() 
    questions_count = serializers.SerializerMethodField()
    subject_name = serializers.ReadOnlyField(source='subject.name')
    # id uchun source='pk' modeldagi primary keyni olishni kafolatlaydi
    id = serializers.ReadOnlyField(source='pk')
    toifa = serializers.ReadOnlyField(source='get_type_label')
    
    # 🔥 ASOSIY TUZATISH: 
    # Modelda 'duration' bor, lekin JS 'duration_minutes' kutmoqda.
    # ReadOnlyField orqali 'duration' ustunidagi qiymatni 'duration_minutes' nomi bilan uzatamiz.
    duration_minutes = serializers.ReadOnlyField(source='duration')

    class Meta:
        model = CaseTest
        fields = [
            'id', 'creator', 'creator_name', 'subject', 'subject_name',
            'title', 'case_text', 'file', 'duration_minutes', 
            'questions_count', 'created_at', 'toifa'
        ]

    def get_creator_name(self, obj):
        """Foydalanuvchi ism-familiyasini birlashtirib qaytaradi"""
        if obj.creator:
            full_name = obj.creator.get_full_name()
            return full_name if full_name else obj.creator.username
        return "Noma'lum"

    def get_questions_count(self, obj):
        """Kazus testga biriktirilgan savollar sonini hisoblaydi"""
        # Modelda related_name='questions' deb berilgan bo'lishi kerak
        return obj.questions.count()


# 🚀 MASHU YERGA QO'SHING
class CaseQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseQuestion # CaseTest uchun model
        fields = '__all__'
    

class QuestionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionImage
        fields = ['id', 'image']
    

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct']


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text', 'is_correct']
    

class AnswerSerializer(serializers.ModelSerializer):
    selected_choices = ChoiceSerializer(many=True, read_only=True)
    selected_choices_ids = serializers.PrimaryKeyRelatedField(
        queryset=Choice.objects.all(),
        many=True,
        write_only=True,
        source='selected_choices'
    )

    class Meta:
        model = Answer
        fields = ['id', 'user', 'question', 'selected_choices', 'selected_choices_ids', 'answered_at']
        read_only_fields = ['id', 'user', 'answered_at']

    def create(self, validated_data):
        user = self.context['request'].user
        selected_choices = validated_data.pop('selected_choices', [])
        answer = Answer.objects.create(user=user, **validated_data)
        answer.selected_choices.set(selected_choices)
        return answer

    def update(self, instance, validated_data):
        selected_choices = validated_data.pop('selected_choices', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if selected_choices is not None:
            instance.selected_choices.set(selected_choices)
        instance.save()
        return instance


class QuestionSerializer(serializers.ModelSerializer):
    # 🔹 Related fields
    options = serializers.SerializerMethodField() 
    images = serializers.SerializerMethodField()

    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        default=list
    )

    # 🔹 Read-only / computed fields
    access_key = serializers.ReadOnlyField()
    creator = serializers.ReadOnlyField(source='creator.username')
    info = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()

    # 🔹 Variant maydonlari
    answer_a = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    answer_b = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    answer_c = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    answer_d = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # 🔹 Correct answers
    correct_answers = serializers.JSONField(required=False, default=list)
    correct_option = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            'id', 'test', 'group', 'info', 'subject', 'creator', 'difficulty',
            'text', 'file', 'file_url', 'image', 'images', 'uploaded_images',
            'youtube_link', 'is_paid', 'price', 'access_key',
            'options', 'answer_a', 'answer_b', 'answer_c', 'answer_d',
            'correct_answers', 'correct_option', 
            'question_type', 'is_multiple_choice' 
        ]
        extra_kwargs = {
            'test': {'required': False, 'allow_null': True},
            'subject': {'required': False, 'allow_null': True},
            'question_type': {'required': False},
            'is_multiple_choice': {'required': False},
        }


    def get_correct_option(self, obj):
        """
        Bazadagi boolean flaglarni (is_correct_a/b/c/d) tekshirib,
        to'g'ri harfni (A, B, C, D) qaytaradi.
        """
        if getattr(obj, 'is_correct_a', False):
            return "A"
        if getattr(obj, 'is_correct_b', False):
            return "B"
        if getattr(obj, 'is_correct_c', False):
            return "C"
        if getattr(obj, 'is_correct_d', False):
            return "D"
            
        # Agar flaglar bo'sh bo'lsa, modelning o'zidagi correct_option'ni tekshiramiz
        raw_val = getattr(obj, 'correct_option', '')
        if raw_val:
            return str(raw_val).strip().upper()
            
        return None

    def get_options(self, obj):
        """
        Frontend 'A', 'B', 'C', 'D' kalitlari orqali matnni o'qishi uchun.
        Agar modelda answer_a kabi maydonlar bo'sh bo'lsa, bo'sh satr qaytaradi.
        """
        return {
            "A": str(getattr(obj, 'answer_a', '') or '').strip(),
            "B": str(getattr(obj, 'answer_b', '') or '').strip(),
            "C": str(getattr(obj, 'answer_c', '') or '').strip(),
            "D": str(getattr(obj, 'answer_d', '') or '').strip()
        }

    def get_images(self, obj):
        request = self.context.get('request')
        images = QuestionImage.objects.filter(question=obj)
        result = []
        for img in images:
            if img.image:
                url = img.image.url
                if request is not None:
                    url = request.build_absolute_uri(url)
                result.append({"id": img.id, "url": url})
        return result

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

    def get_info(self, obj):
        if getattr(obj, 'is_paid', False):
            price = getattr(obj, 'price', 0) or 0
            return f"Pullik savol. Narx: {price} so‘m"
        return "Bepul savol"

    def validate_correct_answers(self, value):
        if not value: return []
        if isinstance(value, str):
            value = [v.strip().upper() for v in value.split(',') if v.strip()]
        return [v.strip().upper() for v in value if v.strip().upper() in ['A','B','C','D']]

    def validate(self, attrs):
        correct_answers = attrs.get('correct_answers', [])
        attrs['is_multiple_choice'] = len(correct_answers) > 1
        return attrs

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        request = self.context.get('request')
        if request and request.user:
            validated_data['creator'] = request.user
            
        question = Question.objects.create(**validated_data)
        for image in uploaded_images:
            QuestionImage.objects.create(question=question, image=image)
        return question
    
    
class UniversalQuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    text = serializers.CharField()
    answer_a = serializers.SerializerMethodField()
    answer_b = serializers.SerializerMethodField()
    answer_c = serializers.SerializerMethodField()
    answer_d = serializers.SerializerMethodField()
    correct_option = serializers.SerializerMethodField()

    def _get_ans(self, obj, letter):
        # Katta yoki kichik harfdagi answer_a/A ni olish
        val = getattr(obj, f'answer_{letter.lower()}', None) or \
              getattr(obj, f'answer_{letter.upper()}', None)
        return str(val).strip() if val else ""

    def get_answer_a(self, obj): return self._get_ans(obj, 'a')
    def get_answer_b(self, obj): return self._get_ans(obj, 'b')
    def get_answer_c(self, obj): return self._get_ans(obj, 'c')
    def get_answer_d(self, obj): return self._get_ans(obj, 'd')

    def get_correct_option(self, obj):
        # 1. 'correct_option' yoki 'correct_answer'ni tekshirish (Oddiy testlar)
        c_opt = str(getattr(obj, 'correct_option', '') or getattr(obj, 'correct_answer', '') or '').strip().upper()
        if c_opt in ['A', 'B', 'C', 'D']:
            return c_opt

        # 2. 'correct_answers'ni tekshirish (Yopiq va Kazus testlar uchun)
        # Bu maydon massiv (['A']) yoki oddiy string ('A') bo'lishi mumkin
        c_ans = getattr(obj, 'correct_answers', None)
        
        if c_ans:
            if isinstance(c_ans, list) and len(c_ans) > 0:
                val = str(c_ans[0]).strip().upper()
            else:
                val = str(c_ans).strip().upper()
                
            if val in ['A', 'B', 'C', 'D']:
                return val

        # 3. is_correct_... flaglari (Admin panel uchun)
        if getattr(obj, 'is_correct_a', False): return "A"
        if getattr(obj, 'is_correct_b', False): return "B"
        if getattr(obj, 'is_correct_c', False): return "C"
        if getattr(obj, 'is_correct_d', False): return "D"

        return ""


class TestSerializer(serializers.ModelSerializer):
    fan_nomi = serializers.SerializerMethodField()
    muallif = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    q_count = serializers.SerializerMethodField()
    cat = serializers.SerializerMethodField()
    uploaded_files = serializers.SerializerMethodField()
    type_key = serializers.SerializerMethodField()
    creation_method = serializers.SerializerMethodField()

    class Meta:
        model = Test
        fields = [
            'id', 'title', 'cat', 'category', 'description', 
            'subject', 'fan_nomi', 'creator', 'muallif',
            'duration', 'is_paid', 'price', 'access_key', 
            'view_mode', 'is_multiple_choice', 'q_count', 
            'uploaded_files', 'type_key', 'creation_method', 'test_type'
        ]
        extra_kwargs = {
            'creator': {'read_only': True},
            'access_key': {'read_only': True},
            'subject': {'required': False, 'allow_null': True},
        }

    def get_type_key(self, obj):
        # Model nomini aniq tekshirish (Eng ishonchli usul)
        model_name = obj.__class__.__name__
        if model_name == 'CaseTest' or hasattr(obj, 'casetest') or hasattr(obj, 'case_test_detail'):
            return 'kazus'
        if model_name == 'ClosedTest' or hasattr(obj, 'closedtest') or hasattr(obj, 'closed_test'):
            return 'closed'

        t_type = getattr(obj, 'test_type', 'ordinary')
        if t_type == 'kazus': return 'kazus'
        if t_type == 'closed': return 'closed'
        return 'regular'

    def get_fan_nomi(self, obj):
        # 1. Test turini model nomiga qarab aniqlaymiz
        model_name = obj.__class__.__name__
        
        if model_name == 'CaseTest' or hasattr(obj, 'casetest') or hasattr(obj, 'case_test_detail') or getattr(obj, 'test_type', '') == 'kazus':
            main_label = "KAZUS TEST"
        elif model_name == 'ClosedTest' or hasattr(obj, 'closedtest') or hasattr(obj, 'closed_test') or getattr(obj, 'test_type', '') == 'closed':
            main_label = "YOPIQ TEST"
        else:
            main_label = "ODDIY TEST"

        # 2. Fayldan yoki Qo'ldaligini aniqlash (Faqat toza usullar bilan)
        is_file = False
        db_method = getattr(obj, 'creation_method', '')
        title_lower = str(getattr(obj, 'title', '')).lower()

        # Agar bazada aniq 'file' deb yozilgan bo'lsa
        if db_method == 'file':
            is_file = True
        # Agar sarlavhada fayl nomlari qolib ketgan bo'lsa
        elif title_lower and any(ext in title_lower for ext in ['.doc', '.docx', '.pdf', '.xls', '.xlsx', 'savollar', 'fayl']):
            is_file = True
        # Model maydonlarida jismoniy fayl bor bo'lsa
        elif hasattr(obj, 'file') and obj.file:
            is_file = True
        elif hasattr(obj, 'case_test_detail') and getattr(obj.case_test_detail, 'file', None):
            is_file = True

        method_str = "(FAYLDAN)" if is_file else "(QO'LDA)"
        
        # 3. ⚠️ AGAR FRONTENDDA "fan_nomi" SIZNING MAXSUS FANINGIZNI QAYTARISHI KERAK BO'LSA:
        # Hozirgi holatda bu faqat "ODDIY TEST (QO'LDA)" matnini qaytaradi.
        # Agar sizga asl fan nomi ham kerak bo'lsa (Masalan: Matematika (Qo'lda)), quyidagi qatorni oching:
        # subject_name = obj.subject.name if obj.subject else ""
        # if subject_name: return f"{subject_name} {method_str}"

        return f"{main_label} {method_str}"

    def get_creation_method(self, obj):
        title_str = str(getattr(obj, 'title', '')).lower()
        
        # 🎯 Agar sarlavhada 'savollar' yoki fayl so'zi bo'lsa 100% 'file' qaytarsin
        if any(x in title_str for x in ['.docx', '.xlsx', '.txt', 'savollar', 'fayl']):
            return 'file'
            
        db_method = getattr(obj, 'creation_method', None)
        if db_method in ['file', 'manual']:
            return db_method
            
        return 'manual'

    def get_muallif(self, obj):
        user = getattr(obj, 'creator', None) or getattr(obj, 'user', None)
        if user:
            f_name = getattr(user, 'first_name', '')
            l_name = getattr(user, 'last_name', '')
            if f_name or l_name:
                return f"{f_name} {l_name}".strip()
            return user.username
        return "Noma'lum"

    def get_duration(self, obj):
        # 1. Savollar sonini sanaymiz
        q_count = self.get_q_count(obj)
    
        # 2. 1 ta savol = 1 minut mantiqi
        if q_count > 0:
           return q_count  # Nechta savol bo'lsa, shuncha minut qaytaradi
    
           # 3. Agar savol hali yuklanmagan bo'lsa (zaxira varianti)
        return 15

    def get_q_count(self, obj):
        # 1. Agar bu oddiy Test yoki CaseTest bo'lsa (chunki ular Question ga bog'langan)
        if hasattr(obj, 'questions'):
            count = obj.questions.count()
            if count > 0: return count

        # 2. Agar CaseTest bo'lsa va related_name ishlatilgan bo'lsa
        if hasattr(obj, 'case_test_detail'):
            return obj.case_test_detail.questions.count() if hasattr(obj.case_test_detail, 'questions') else 0

        # 3. Yopiq testlar uchun
        if hasattr(obj, 'closed_questions'):
            return obj.closed_questions.count()
            
        return 0

    def get_cat(self, obj):
        return str(obj.category) if obj.category else "Manual"

    def get_uploaded_files(self, obj):
        try:
            file_instance = UploadedFile.objects.filter(test=obj).first()
            if file_instance and file_instance.file:
                request = self.context.get('request')
                return request.build_absolute_uri(file_instance.file.url) if request else file_instance.file.url
        except: return None
        return None

    def _save_questions(self, test, questions_data, creator):
        db_objs = []
        for q in questions_data:
            # Variantlarni barcha mumkin bo'lgan JSON kalitlaridan qidirish
            ans_a = q.get('answer_a') or q.get('answer_A') or q.get('a') or q.get('ans_a') or ''
            ans_b = q.get('answer_b') or q.get('answer_B') or q.get('b') or q.get('ans_b') or ''
            ans_c = q.get('answer_c') or q.get('answer_C') or q.get('c') or q.get('ans_c') or ''
            ans_d = q.get('answer_d') or q.get('answer_D') or q.get('d') or q.get('ans_d') or ''
            
            # To'g'ri javobni formatlash
            raw_corr = q.get('correct_option') or q.get('correct') or q.get('correct_answer') or 'A'
            clean_corr = str(raw_corr).strip().upper()
            if clean_corr not in ['A', 'B', 'C', 'D']: clean_corr = 'A'
            
            db_objs.append(Question(
                test=test, 
                creator=creator,
                subject=getattr(test, 'subject', None),
                text=q.get('text') or q.get('question_text') or 'Savol matni',
                answer_a=ans_a, 
                answer_b=ans_b, 
                answer_c=ans_c, 
                answer_d=ans_d,
                correct_option=clean_corr,
                correct_answer=clean_corr,
                correct_answers=[clean_corr]
            ))
        
        if db_objs:
            with transaction.atomic():
                # Test turiga qarab eski savollarni tozalash va yangilarini qo'shish
                if hasattr(test, 'questions'):
                    test.questions.all().delete()
                    Question.objects.bulk_create(db_objs)

    def create(self, validated_data):
        request = self.context.get("request")
        
        # 1. Test turini aniqlaymiz
        test_type_input = request.data.get('test_type', '').strip().lower() if request else ''
        if not test_type_input:
            test_type_input = validated_data.get('test_type', 'ordinary')

        # 2. 🎯 ENG ASOSIY TEKSHIRUV: Har qanday nom bilan fayl kelyaptimi?
        is_file_upload = False
        if request:
            # Agar so'rovda 'file', 'files[]' yoki umuman har qanday fayl bo'lsa
            has_any_file = bool(request.FILES)
            has_file_method = request.data.get('creation_method') == 'file'
            
            # Sarlavhada fayl kengaytmasi borligini ham qo'shimcha sug'urta sifatida tekshiramiz
            title_str = str(request.data.get('title', '')).lower()
            has_file_ext = any(ext in title_str for ext in ['.docx', '.xlsx', '.xls', '.txt'])

            if has_any_file or has_file_method or has_file_ext:
                is_file_upload = True
            
        # 3. Agar fayl aniqlansa, bazaga METODni 'file' deb yozamiz
        if is_file_upload:
            validated_data['creation_method'] = 'file'
            # Agar sizda test_type ham fayldan yuklanganda o'zgarishi kerak bo'lsa (masalan kazusga)
            # test_type_input = 'kazus' 
            # validated_data['test_type'] = 'kazus'
        else:
            # Agar umuman fayl bo'lmasa va frontend qo'lda yaratyotgan bo'lsa
            # Lekin agar test_type 'kazus' bo'lsa va u faylsiz ham bo'lishi mumkin bo'lsa, creation_method'ni saqlab qolamiz
            if test_type_input not in ['kazus', 'case']:
                validated_data['creation_method'] = 'manual'

        if request and request.user.is_authenticated:
            validated_data['creator'] = request.user
        
        questions_raw = request.data.get('questions', []) if request else []
        validated_data['test_duration'] = len(questions_raw) if len(questions_raw) > 0 else 15

        with transaction.atomic():
            # Ota modelni yaratamiz (Endi creation_method aniq 'file' bo'lib saqlanadi)
            test = Test.objects.create(**validated_data)

            if test_type_input == 'kazus':
                from .models import CaseTest
                c_text = request.data.get('description') or request.data.get('case_text') or 'Fayldan yuklangan kazus matni'
                
                CaseTest.objects.get_or_create(
                    parent_test=test,
                    defaults={
                        'title': test.title,
                        'creator': test.creator,
                        'subject': test.subject,
                        'case_text': c_text,
                        'creation_method': 'file' if is_file_upload else 'manual'
                    }
                )

            if questions_raw:
                self._save_questions(test, questions_raw, request.user)
            
            return test

    def update(self, instance, validated_data):
        request = self.context.get("request")
        test_type_input = request.data.get('test_type')
        if test_type_input:
            validated_data['test_type'] = test_type_input

        validated_data.pop('creator', None) 
        questions_raw = request.data.get('questions')
        input_duration = request.data.get('duration_minutes') or request.data.get('duration')
        
        if input_duration is not None:
            try: validated_data['duration_minutes'] = int(input_duration)
            except: pass
        elif questions_raw is not None:
            validated_data['duration_minutes'] = len(questions_raw)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        with transaction.atomic():
            instance.save()
            if questions_raw is not None:
                creator = getattr(instance, 'creator', None) or getattr(instance, 'user', None)
                self._save_questions(instance, questions_raw, creator)
        return instance
    

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']
        

class ClosedQuestionSerializer(serializers.ModelSerializer):
    # Modelda answer_A bo'lsa, frontendga answer_a bo'lib boradi
    answer_a = serializers.CharField(source='answer_A', allow_blank=True, default="")
    answer_b = serializers.CharField(source='answer_B', allow_blank=True, default="")
    answer_c = serializers.CharField(source='answer_C', allow_blank=True, default="")
    answer_d = serializers.CharField(source='answer_D', allow_blank=True, default="")
    correct_option = serializers.CharField(source='correct_answers', allow_blank=True, default="")

    class Meta:
        model = ClosedQuestion
        fields = [
            'id', 'text', 'answer_a', 'answer_b', 
            'answer_c', 'answer_d', 'correct_option'
        ]


class ClosedTestSerializer(serializers.ModelSerializer):
    q_count = serializers.SerializerMethodField()
    muallif = serializers.SerializerMethodField()
    subject_name = serializers.ReadOnlyField(source='subject.name')
    type_key = serializers.SerializerMethodField()
    # related_name='closed_questions' modeldagi related_name ga mos
    questions = ClosedQuestionSerializer(source='closed_questions', many=True, read_only=True)

    class Meta:
        model = ClosedTest
        fields = [
            'id', 'title', 'duration', 'q_count', 'muallif', 
            'subject', 'subject_name', 'file', 'created_at', 'type_key',
            'questions'
        ]

    def get_type_key(self, obj):
        return 'closed'

    def get_q_count(self, obj):
        return obj.closed_questions.count()

    def get_muallif(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        return "Noma'lum"

    def create(self, validated_data):
        request = self.context.get('request')
        questions_raw = request.data.get('questions', [])
        
        if isinstance(questions_raw, str):
            try:
                questions_data = json.loads(questions_raw)
            except (json.JSONDecodeError, TypeError):
                questions_data = []
        else:
            questions_data = questions_raw

        if not validated_data.get('duration'):
            validated_data['duration'] = len(questions_data) if questions_data else 1
        
        validated_data['user'] = request.user
        
        try:
            with transaction.atomic():
                test = ClosedTest.objects.create(**validated_data)
                
                if questions_data:
                    question_objs = []
                    for q in questions_data:
                        question_objs.append(
                            ClosedQuestion(
                                test=test,
                                text=q.get('text', ''),
                                answer_A=q.get('answer_a') or q.get('answer_A', ''),
                                answer_B=q.get('answer_b') or q.get('answer_B', ''),
                                answer_C=q.get('answer_c') or q.get('answer_C', ''),
                                answer_D=q.get('answer_d') or q.get('answer_D', ''),
                                correct_answers=str(q.get('correct_option') or q.get('correct_answers', 'A')).upper(),
                                question_type=q.get('question_type', 'single')
                            )
                        )
                    ClosedQuestion.objects.bulk_create(question_objs)
                return test
        except Exception as e:
            raise serializers.ValidationError({"error": f"Saqlashda xatolik: {str(e)}"})
        

class ManualClosedTestSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    questions = ClosedQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = ClosedTest
        fields = ['id', 'title', 'description', 'user', 'created_at', 'questions', 'duration']

    def create(self, validated_data):
        request = self.context.get('request')
        questions_data = request.data.get('questions', [])
        
        # Savollar soniga qarab vaqtni hisoblash
        duration = request.data.get('duration') or len(questions_data)
        
        # 1. Testni yaratish
        test = ClosedTest.objects.create(
            user=request.user, 
            duration=duration, 
            **validated_data
        )

        # 2. Savollarni yaratish
        for q_data in questions_data:
            opts = q_data.get('options') or q_data.get('answers') or {}
            
            ClosedQuestion.objects.create(
                test=test, # related_name='closed_questions' bog'lanishi shu yerda ishlaydi
                text=q_data.get('text', 'Savol matni'),
                answer_A=opts.get('A') or opts.get('a') or '',
                answer_B=opts.get('B') or opts.get('b') or '',
                answer_C=opts.get('C') or opts.get('c') or '',
                answer_D=opts.get('D') or opts.get('d') or '',
                correct_answers=q_data.get('correct') or q_data.get('correct_answers') or 'A'
            )
        return test
    

class KazusTestSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, required=False)  

    class Meta:
        model = Test
        fields = [
            'id', 'title', 'description', 'subject', 'duration_minutes',
            'is_paid', 'price', 'view_mode', 'questions', 'correct_option'
        ]

    def validate(self, data):
        
        if data.get('is_paid') and not data.get('price'):
            raise serializers.ValidationError({
                "price": "Pulli testlar uchun narx kiritish shart"
            })
        return data

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        request = self.context.get('request')

        
        test = Test.objects.create(
            creator=request.user,
            **validated_data
        )

        
        for question_data in questions_data:
            QuestionSerializer(context={'request': request}).create(
                {**question_data, 'test': test}
            )

        return test

    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions', [])
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.duration_minutes = validated_data.get('duration_minutes', instance.duration_minutes)
        instance.is_paid = validated_data.get('is_paid', instance.is_paid)
        instance.price = validated_data.get('price', instance.price)
        instance.view_mode = validated_data.get('view_mode', instance.view_mode)
        instance.save()

        request = self.context.get('request')

        for question_data in questions_data:
            question_id = question_data.get('id')
            if question_id:
                
                question = Question.objects.filter(id=question_id, test=instance).first()
                if question:
                    for key, value in question_data.items():
                        if key not in ['id', 'uploaded_images']:
                            setattr(question, key, value)
                    question.save()
            else:
                
                QuestionSerializer(context={'request': request}).create(
                    {**question_data, 'test': instance}
                )

        return instance
    

# 1. Oddiy testlar uchun (mavjud kod)
class ManualTestSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source='creator.id')
    class Meta:
        model = Test
        fields = ['id', 'title', 'description', 'subject', 'creator', 'created_at']


class OlympiadGroupSerializer(serializers.ModelSerializer):
    test_title = serializers.CharField(source='test.title', read_only=True)

    class Meta:
        model = OlympiadGroup
        fields = ['id', 'name', 'test', 'test_title', 'start_time', 'end_time', 'max_participants']

        extra_kwargs = {
            'name': {'required': False},
            'test': {'required': False},
            'start_time': {'required': False, 'allow_null': True},
            'end_time': {'required': False, 'allow_null': True},
            'max_participants': {'required': False},
        }


class OlympiadParticipantSerializer(serializers.ModelSerializer):
    
    username = serializers.CharField(source='user.username', read_only=True)
    
    
    full_name = serializers.SerializerMethodField()
    
    result = serializers.FloatField(source='score', read_only=True)
    correct_answers = serializers.IntegerField(read_only=True)
    wrong_answers = serializers.IntegerField(read_only=True)

    class Meta:
        model = OlympiadParticipant
        
        fields = ['id', 'username', 'full_name', 'result', 'correct_answers', 'wrong_answers']

    def get_full_name(self, obj):
        
        first = obj.user.first_name
        last = obj.user.last_name
        if first or last:
            return f"{first} {last}".strip()
        
        return obj.user.username


class OlympiadAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = OlympiadAnswer
        fields = ['id', 'participant', 'question_id', 'selected', 'is_correct', 'answered_at']


class SubmitResultSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    is_correct = serializers.BooleanField()
    correct_answers = serializers.IntegerField()
    wrong_answers = serializers.IntegerField()
    remaining = serializers.IntegerField()
    finished = serializers.BooleanField()
    score = serializers.FloatField()


class QuestionPublicSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    text = serializers.CharField()
    options = serializers.ListField(child=serializers.CharField())  


User = get_user_model()

class BasicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')


class GroupMembershipSerializer(serializers.ModelSerializer):
    user = BasicUserSerializer(read_only=True)
    
    class Meta:
        model = GroupMembership
        fields = ('id', 'user', 'joined_at')
        read_only_fields = ('joined_at',)


class ResultSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    group = serializers.CharField(source='group.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Result
        fields = ['id', 'name', 'username', 'score', 'correct_count', 'group', 'created_at']

    def get_name(self, obj):
        
        full_name = f"{obj.user.first_name} {obj.user.last_name}".strip()
        
        return full_name if full_name else obj.user.username


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = BasicUserSerializer(read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = ('id', 'group', 'sender', 'content', 'timestamp')
        read_only_fields = ('group', 'sender', 'timestamp')


class GroupSerializer(serializers.ModelSerializer):
    creator = BasicUserSerializer(read_only=True)
    members_count = serializers.SerializerMethodField()
    invite_token = serializers.UUIDField(read_only=True)

    test_title = serializers.CharField(source='test.title', read_only=True)
    start_time = serializers.DateTimeField(read_only=True)
    end_time = serializers.DateTimeField(read_only=True)
    max_participants = serializers.IntegerField(read_only=True)

    class Meta:
        model = Group
        fields = (
            'id',
            'name',
            'creator',
            'created_at',
            'invite_token',
            'members_count',
            'test_title',      
            'start_time',       
            'end_time',         
            'max_participants'  
        )
        read_only_fields = ('created_at', 'invite_token')

    def get_members_count(self, obj):
        return obj.memberships.count()

    
class GroupCreateSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Group
        fields = ('id', 'name', 'start_time', 'end_time', 'max_participants')
    

class TestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = [
            'id',
            'title',
            'description',
            'subject',
            'duration_minutes',
            'is_paid',
            'price',          
            'access_key',     
        ]
        read_only_fields = ['access_key']  


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'name', 'subject']


class TestSelectizeSerializer(serializers.ModelSerializer):
    """GET uchun serializer (faqat id va title)"""
    class Meta:
        model = Test
        fields = ["id", "title"]


class UserAnswerSerializer(serializers.ModelSerializer):
    selected_answers = serializers.PrimaryKeyRelatedField(
        queryset=Option.objects.all(),  
        many=True
    )

    class Meta:
        model = UserAnswer
        fields = ['question', 'selected_answers']


class SubmitAnswerSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
    question_id = serializers.IntegerField()
    selected_answers = serializers.ListField(
        child=serializers.CharField(), required=True
    )


class TestSessionSerializer(serializers.ModelSerializer):
    user_answers = UserAnswerSerializer(many=True, write_only=True)
    score = serializers.FloatField(read_only=True)
    correct_answers = serializers.IntegerField(read_only=True)
    incorrect_answers = serializers.IntegerField(read_only=True)
    total_questions = serializers.IntegerField(read_only=True)
    finished_at = serializers.DateTimeField(read_only=True)
    started_at = serializers.DateTimeField(read_only=True)
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = TestSession
        fields = [
            'id', 'user', 'test', 'user_answers',
            'started_at', 'finished_at', 'score',
            'correct_answers', 'incorrect_answers', 'total_questions'
        ]

    def create(self, validated_data):
        user_answers_data = validated_data.pop('user_answers')
        test_session = TestSession.objects.create(
            user=self.context['request'].user,
            test=validated_data['test']
        )
        correct_count = 0

        for answer_data in user_answers_data:
            question = answer_data['question']
            selected_answers = answer_data['selected_answers']
            correct_answers = set(
                Option.objects.filter(question=question, is_correct=True)
            )
            is_correct = set(selected_answers) == correct_answers

            if is_correct:
                correct_count += 1

            user_answer = UserAnswer.objects.create(
                session=test_session,
                question=question,
                is_correct=is_correct
            )
            user_answer.selected_answers.set(selected_answers)

        total_questions = len(user_answers_data)
        test_session.total_questions = total_questions
        test_session.correct_answers = correct_count
        test_session.incorrect_answers = total_questions - correct_count
        test_session.score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        test_session.finished_at = timezone.now()
        test_session.save()

        return test_session
    

class TestAnswerSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)
    selected_answers = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )

    class Meta:
        model = TestAnswer
        fields = ['id', 'session', 'question', 'selected_answers', 'created_at']
        read_only_fields = ['id', 'session', 'question', 'created_at']

    def create(self, validated_data):
        selected_answers = validated_data.pop('selected_answers')
        test_answer = TestAnswer.objects.create(**validated_data)
        test_answer.selected_answers = selected_answers
        test_answer.save()
        return test_answer
    

class TestQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestQueue
        fields = [
            'id',
            'user',
            'test',
            'start_time',
            'expected_end_time',
            'score',
            'stopped_by_user',
            'is_completed',
            'current_step',
            'status'
        ]
        read_only_fields = ['id', 'start_time', 'expected_end_time', 'status', 'score', 'is_completed']


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def create(self, validated_data):
        test = self.context.get('test')  
        return UploadedFile.objects.create(test=test, **validated_data)


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class TestCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCompletion
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password')

    def create(self, validated_data):
        user = User(
            username=validated_data['email'],  
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])  
        user.save()
        return user


class UserTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTest
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    gender = serializers.CharField(read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    date_joined = serializers.DateTimeField(source="user.date_joined", read_only=True)
    full_name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    solved_tests = serializers.IntegerField(default=0, read_only=True)
    average_score = serializers.FloatField(default=0, read_only=True)
    groups_count = serializers.IntegerField(default=0, read_only=True)
    group = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "username", "email", "date_joined", "full_name",
            "avatar_url", "solved_tests", "average_score", "groups_count", "gender","group"
        ]

    def get_full_name(self, obj):
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name if full_name else obj.user.get_full_name() or "—"

    def get_avatar_url(self, obj):
        if obj.avatar:
            return obj.avatar.url
        default_file = "defaults/female.png" if getattr(obj, "gender", "male") == "female" else "defaults/male.png"
        return settings.MEDIA_URL + default_file


class ProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    email = serializers.EmailField(source='user.email', required=False)

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email', 'birth_date', 'bio', 'location', 'gender']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        if user_data:
            instance.user.first_name = user_data.get('first_name', instance.user.first_name)
            instance.user.last_name = user_data.get('last_name', instance.user.last_name)
            instance.user.email = user_data.get('email', instance.user.email)
            instance.user.save()

        instance.birth_date = validated_data.get('birth_date', instance.birth_date)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.location = validated_data.get('location', instance.location)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.save()

        return instance
    

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Hozirgi parol noto‘g‘ri")
        return value

    def validate(self, attrs):
        if attrs['new_password1'] != attrs['new_password2']:
            raise serializers.ValidationError("Yangi parollar mos kelmadi")
        
        validate_password(attrs['new_password1'], user=self.context['request'].user)
        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password1'])
        user.save()
        return user


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'














