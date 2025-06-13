from django import forms

from .models import *
from django.contrib.admin.widgets import  AdminDateWidget, AdminTimeWidget, AdminSplitDateTime


class coupon_Form(forms.ModelForm):
    class Meta:
        model = coupon
        fields = '__all__'  # Include all fields
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Coupon Code'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Coupon Code'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'min_purchase': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }




class home_banner_Form(forms.ModelForm):

    is_for_web = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = home_banner
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'discription': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),

        }





from django import forms
from .models import FAQ

class ScamCategoryForm(forms.ModelForm):
    class Meta:
        model = ScamCategory
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Enter your question'
            }),
        }

class occupation_category_Form(forms.ModelForm):
    class Meta:
        model = occupation_category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Enter Occupation Category'
            }),
        }

class occupation_subcategory_Form(forms.ModelForm):
    class Meta:
        model = occupation_subcategory
        fields = ['name', 'category']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-control', 'placeholder': 'Enter Occupation Category'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Enter Occupation Category'
            }),
        }

class occupation_Form(forms.ModelForm):
    class Meta:
        model = occupation
        fields = ['name', 'category', 'subcategory']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'subcategory': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Enter Name'
            }),
        }

class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['question', 'answer', 'is_active']
        widgets = {
            'question': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Enter your question'
            }),
            'answer': forms.Textarea(attrs={
                'class': 'form-control', 'placeholder': 'Enter the answer', 'rows': 3
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }



