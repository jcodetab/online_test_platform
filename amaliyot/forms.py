from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordChangeForm
from .models import UserProfile
import re



class CustomPasswordChangeForm(PasswordChangeForm):
    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get("new_password")
        new_password2 = self.cleaned_data.get("new_password2")
        
        
        if new_password1 != new_password2:
            raise ValidationError("Yangi parollar bir xil emas!")

        
        return new_password2


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
            raise ValidationError("Parol kamida 8 ta belgidan iborat bo'lishi kerak, bironta raqam, birorta katta yoki kichik harf, va maxsus belgi (@$!%*?&) bo'lishi kerak.")
        
        return password


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Iltimos, haqiqiy email manzilingizni kiriting.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class QuestionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions')  
        super().__init__(*args, **kwargs)
        
        for question in questions:
            choices = [(choice.choice_text, choice.choice_text) for choice in question.choices.all()]
            self.fields[f'question_{question.id}'] = forms.ChoiceField(
                label=question.question_text,
                choices=choices,
                widget=forms.RadioSelect,
                required=True
            )


class QuestionForm(forms.Form):
    question_text = forms.CharField(label='Savol matni', max_length=255)
    option_1 = forms.CharField(label='Variant 1', max_length=255)
    option_2 = forms.CharField(label='Variant 2', max_length=255)
    option_3 = forms.CharField(label='Variant 3', max_length=255)
    correct_option = forms.ChoiceField(label='To\'g\'ri javob', choices=[('1', 'Variant 1'), ('2', 'Variant 2'), ('3', 'Variant 3')])


class UserProfileForm(forms.ModelForm):
    
    first_name = forms.CharField(max_length=30, required=True, label='Ism')
    last_name = forms.CharField(max_length=30, required=True, label='Familiya')
    email = forms.EmailField(required=True, label='Elektron pochta manzili')
    birth_date = forms.DateField(required=False, label='Tug\'ilgan sana', widget=forms.SelectDateWidget(years=range(1900, 2025)))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    
    def save(self, user, commit=True):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()

        return user


class UserInformationForm(forms.Form):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)


class ChangePasswordForm(forms.Form):
    
    old_password = forms.CharField(widget=forms.PasswordInput, label='Eski Parol', required=True)
    new_password = forms.CharField(widget=forms.PasswordInput, label='Yangi Parol', required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Parolni Tasdiqlash', required=True)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password != confirm_password:
            raise forms.ValidationError("Yangi parollar bir xil bo'lishi kerak")
        return cleaned_data
    

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']  

    birthdate = forms.DateField(
        widget=forms.SelectDateWidget(years=range(1900, 2025)),  
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        
        if self.instance.pk and hasattr(self.instance, 'profile'):
            self.fields['birth_date'].initial = self.instance.profile.birthdate 


class ProfileUpdateForm(forms.ModelForm):
    # Qo'shimcha maydonlar (bular User modelidan keladi)
    first_name = forms.CharField(max_length=100, required=True, label="Ism")
    last_name = forms.CharField(max_length=100, required=True, label="Familiya")
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email', 'birth_date', 'bio', 'location', 'gender', 'avatar']

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        # Formani ochganda hozirgi ism va emailni User modelidan olib ko'rsatish
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        # 1. UserProfile ma'lumotlarini olish
        profile = super().save(commit=False)
        user = profile.user

        # 2. User modelidagi ma'lumotlarni yangilash (Eng muhim joyi!)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()   # Asosiy foydalanuvchini saqlash
            profile.save() # Profilni saqlash
        return profile
    

