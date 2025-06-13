from django.http import JsonResponse
from django.shortcuts import render


# Create your views here.


from .models import *
from .forms import *
from .filters import *
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.urls import reverse
from django.http.response import HttpResponseRedirect
from .serializers import *

from users.permissions import *

from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger






@login_required(login_url='login_admin')
def add_coupon(request):

    if request.method == 'POST':

        forms = coupon_Form(request.POST, request.FILES)

        if forms.is_valid():
            forms.save()
            return redirect('list_coupon')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_coupon.html', context)
    
    else:

        forms = coupon_Form()

        context = {
            'form': forms
        }
        return render(request, 'add_coupon.html', context)

        

@login_required(login_url='login_admin')
def update_coupon(request, coupon_id):

    if request.method == 'POST':

        instance = coupon.objects.get(id=coupon_id)

        forms = coupon_Form(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            return redirect('list_coupon')
        else:
            print(forms.errors)
    
    else:

        instance = coupon.objects.get(id=coupon_id)
        forms = coupon_Form(instance=instance)

        context = {
            'form': forms
        }
        return render(request, 'add_coupon.html', context)

        

@login_required(login_url='login_admin')
def delete_coupon(request, coupon_id):

    coupon.objects.get(id=coupon_id).delete()

    return HttpResponseRedirect(reverse('list_coupon'))


@login_required(login_url='login_admin')
def list_coupon(request):

    data = coupon.objects.all()
    context = {
        'data': data
    }
    return render(request, 'list_coupon.html', context)




@login_required(login_url='login_admin')
def add_occupation_category(request):

    if request.method == 'POST':

        forms = occupation_category_Form(request.POST, request.FILES)

        if forms.is_valid():
            forms.save()
            return redirect('list_occupation_category')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_occupation_category.html', context)
    
    else:

        forms = occupation_category_Form()

        context = {
            'form': forms
        }
        return render(request, 'add_occupation_category.html', context)

        

@login_required(login_url='login_admin')
def update_occupation_category(request, occupation_category_id):

    if request.method == 'POST':

        instance = occupation_category.objects.get(id=occupation_category_id)

        forms = occupation_category_Form(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            return redirect('list_occupation_category')
        else:
            print(forms.errors)
    
    else:

        instance = occupation_category.objects.get(id=occupation_category_id)
        forms = occupation_category_Form(instance=instance)

        context = {
            'form': forms
        }
        return render(request, 'add_occupation_category.html', context)

        

@login_required(login_url='login_admin')
def delete_occupation_category(request, occupation_category_id):

    occupation_category.objects.get(id=occupation_category_id).delete()

    return HttpResponseRedirect(reverse('list_occupation_category'))


@login_required(login_url='login_admin')
def list_occupation_category(request):

    data = occupation_category.objects.all()
    context = {
        'data': data
    }
    return render(request, 'list_occupation_category.html', context)

@login_required(login_url='login_admin')
def add_occupation_subcategory(request):

    if request.method == 'POST':

        forms = occupation_subcategory_Form(request.POST, request.FILES)

        if forms.is_valid():
            forms.save()
            return redirect('list_occupation_subcategory')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_occupation_subcategory.html', context)
    
    else:

        forms = occupation_subcategory_Form()

        context = {
            'form': forms
        }
        return render(request, 'add_occupation_subcategory.html', context)

        

@login_required(login_url='login_admin')
def update_occupation_subcategory(request, occupation_subcategory_id):

    if request.method == 'POST':

        instance = occupation_subcategory.objects.get(id=occupation_subcategory_id)

        forms = occupation_subcategory_Form(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            return redirect('list_occupation_subcategory')
        else:
            print(forms.errors)
    
    else:

        instance = occupation_subcategory.objects.get(id=occupation_subcategory_id)
        forms = occupation_subcategory_Form(instance=instance)

        context = {
            'form': forms
        }
        return render(request, 'add_occupation_subcategory.html', context)

        

@login_required(login_url='login_admin')
def delete_occupation_subcategory(request, occupation_subcategory_id):

    occupation_subcategory.objects.get(id=occupation_subcategory_id).delete()

    return HttpResponseRedirect(reverse('list_occupation_subcategory'))


@login_required(login_url='login_admin')
def list_occupation_subcategory(request):

    data = occupation_subcategory.objects.all()
    context = {
        'data': data
    }
    return render(request, 'list_occupation_subcategory.html', context)


@login_required(login_url='login_admin')
def add_occupation(request):

    if request.method == 'POST':

        forms = occupation_Form(request.POST, request.FILES)

        if forms.is_valid():
            forms.save()
            return redirect('list_occupation')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_occupation.html', context)
    
    else:

        forms = occupation_Form()

        context = {
            'form': forms
        }
        return render(request, 'add_occupation.html', context)

        

@login_required(login_url='login_admin')
def update_occupation(request, occupation_id):

    if request.method == 'POST':

        instance = occupation.objects.get(id=occupation_id)

        forms = occupation_Form(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            return redirect('list_occupation')
        else:
            print(forms.errors)
    
    else:

        instance = occupation.objects.get(id=occupation_id)
        forms = occupation_Form(instance=instance)

        context = {
            'form': forms
        }
        return render(request, 'add_occupation.html', context)

        

@login_required(login_url='login_admin')
def delete_occupation(request, occupation_id):

    occupation.objects.get(id=occupation_id).delete()

    return HttpResponseRedirect(reverse('list_occupation'))


@login_required(login_url='login_admin')
def list_occupation(request):

    data = occupation.objects.all()
    context = {
        'data': data
    }
    return render(request, 'list_occupation.html', context)





def add_home_banner(request):
    
    if request.method == "POST":

        forms = home_banner_Form(request.POST, request.FILES)

        if forms.is_valid():
            forms.save()
            return redirect('list_home_banner')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }

            return render(request, 'add_home_banner.html', context)
    
    else:

        # create first row using admin then editing only

        

        return render(request, 'add_home_banner.html', { 'form' : home_banner_Form()})

def update_home_banner(request, home_banner_id):
    
    instance = home_banner.objects.get(id = home_banner_id)

    if request.method == "POST":


        instance = home_banner.objects.get(id=home_banner_id)

        forms = home_banner_Form(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            return redirect('list_home_banner')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }

            return render(request, 'add_home_banner.html', context)

    
    else:

        # create first row using admin then editing only

        forms = home_banner_Form(instance=instance)
                
        context = {
            'form': forms
        }

        return render(request, 'add_home_banner.html', context)


def list_home_banner(request):

    data = home_banner.objects.all()

    return render(request, 'list_home_banner.html', {'data' : data})


def delete_home_banner(request, home_banner_id):

    data = home_banner.objects.get(id = home_banner_id).delete()

    return redirect('list_home_banner')


from django.views import View

def get_home_banner(request):
  
    filtered_qs = home_bannerFilter(request.GET, queryset=home_banner.objects.all()).qs

    serialized_data = HomeBannerSerializer(filtered_qs, many=True, context={'request': request}).data
    return JsonResponse({"data": serialized_data}, status=200)





def add_faq(request):
    
    if request.method == "POST":

        forms = FAQForm(request.POST, request.FILES)

        if forms.is_valid():
            forms.save()
            return redirect('list_faq')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }

            return render(request, 'add_faq.html', context)
    
    else:

        # create first row using admin then editing only

        

        return render(request, 'add_faq.html', { 'form' : FAQForm()})

def update_faq(request, faq_id):
    
    instance = FAQ.objects.get(id = faq_id)

    if request.method == "POST":


        instance = FAQ.objects.get(id=faq_id)

        forms = FAQForm(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            return redirect('list_faq')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }

            return render(request, 'add_faq.html', context)

    
    else:

        # create first row using admin then editing only

        forms = FAQForm(instance=instance)
                
        context = {
            'form': forms
        }

        return render(request, 'add_faq.html', context)


def list_faq(request):

    data = FAQ.objects.all()

    return render(request, 'list_faq.html', {'data' : data})


def delete_faq(request, faq_id):

    data = FAQ.objects.get(id = faq_id).delete()

    return redirect('list_faq')



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import FAQ
from .serializers import FAQSerializer


class FAQListAPIView(APIView):
    def get(self, request):
        faqs = FAQ.objects.all()
        serializer = FAQSerializer(faqs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


def add_scam_category(request):
    
    if request.method == "POST":

        forms = ScamCategoryForm(request.POST, request.FILES)

        if forms.is_valid():
            forms.save()
            return redirect('list_scam_category')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }

            return render(request, 'add_scam_category.html', context)
    
    else:

        # create first row using admin then editing only

        

        return render(request, 'add_scam_category.html', { 'form' : ScamCategoryForm()})

def update_scam_category(request, scam_category_id):
    
    instance = ScamCategory.objects.get(id = scam_category_id)

    if request.method == "POST":


        instance = ScamCategory.objects.get(id=scam_category_id)

        forms = ScamCategoryForm(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            return redirect('list_scam_category')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }

            return render(request, 'add_scam_category.html', context)

    
    else:

        # create first row using admin then editing only

        forms = ScamCategoryForm(instance=instance)
                
        context = {
            'form': forms
        }

        return render(request, 'add_scam_category.html', context)


def list_scam_category(request):

    data = ScamCategory.objects.all()

    return render(request, 'list_scam_category.html', {'data' : data})


def delete_scam_category(request, scam_category_id):

    data = ScamCategory.objects.get(id = scam_category_id).delete()

    return redirect('list_scam_category')



from .serializers import *
from rest_framework import viewsets


class scamcategory(APIView):
    def get(self, request):
        faqs = ScamCategory.objects.all()
        serializer = ScamCategorySerializer(faqs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class OccupationCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = occupation_category.objects.all()
    serializer_class = OccupationCategorySerializer

class OccupationSubcategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = occupation_subcategory.objects.all()
    serializer_class = OccupationSubcategorySerializer

class OccupationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = occupation.objects.all()
    serializer_class = OccupationSerializer
