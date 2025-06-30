from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render


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
def add_city(request):

    if request.method == 'POST':

        forms = city_Form(request.POST, request.FILES)

        if forms.is_valid():
            forms.save()
            return redirect('list_city')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_city.html', context)
    
    else:

        forms = city_Form()

        context = {
            'form': forms
        }
        return render(request, 'add_city.html', context)

        

@login_required(login_url='login_admin')
def update_city(request, city_id):

    if request.method == 'POST':

        instance = city.objects.get(id=city_id)

        forms = city_Form(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            return redirect('list_city')
        else:
            print(forms.errors)
    
    else:

        instance = city.objects.get(id=city_id)
        forms = city_Form(instance=instance)

        context = {
            'form': forms
        }
        return render(request, 'add_city.html', context)

        

@login_required(login_url='login_admin')
def delete_city(request, city_id):

    city.objects.get(id=city_id).delete()

    return HttpResponseRedirect(reverse('list_city'))



@login_required(login_url='login_admin')
def list_city(request):

    data = city.objects.all()

    return render(request, 'list_city.html', {'data' : data})


from django.views import View

def get_city(request):
  
    filtered_qs =city.objects.all()

    serialized_data = city_Serializer(filtered_qs, many=True, context={'request': request}).data
    return JsonResponse({"data": serialized_data}, status=200)



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



def add_privacy_policy(request):
    
    if request.method == "POST":

        forms = privacy_policyForm(request.POST, request.FILES)

        if forms.is_valid():
            forms.save()
            return redirect('list_privacy_policy')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }

            return render(request, 'add_privacy_policy.html', context)
    
    else:

        # create first row using admin then editing only

        

        return render(request, 'add_privacy_policy.html', { 'form' : privacy_policyForm()})

def update_privacy_policy(request, privacy_policy_id):
    
    instance = privacy_policy.objects.get(id = privacy_policy_id)

    if request.method == "POST":


        instance = privacy_policy.objects.get(id=privacy_policy_id)

        forms = privacy_policyForm(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            return redirect('list_privacy_policy')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }

            return render(request, 'add_privacy_policy.html', context)

    
    else:

        # create first row using admin then editing only

        forms = privacy_policyForm(instance=instance)
                
        context = {
            'form': forms
        }

        return render(request, 'add_privacy_policy.html', context)


def list_privacy_policy(request):

    data = privacy_policy.objects.all()

    return render(request, 'list_privacy_policy.html', {'data' : data})


def delete_privacy_policy(request, privacy_policy_id):

    data = privacy_policy.objects.get(id = privacy_policy_id).delete()

    return redirect('list_privacy_policy')



class privacy_policyListAPIView(APIView):
    def get(self, request):
        faqs = privacy_policy.objects.all()
        serializer = privacy_policySerializer(faqs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

from customer.models import *

def all_shipments(request):


    data = Customer_Order.objects.all()

    context = {
        'data' : data
    }

    return render(request, 'all_shipments.html', context)

def view_order_detail(request, booking_id):


    data = Customer_Order.objects.get(id = booking_id)

    context = {
        'data' : data
    }

    return render(request, 'view_shipments.html', context)



@login_required(login_url='login_admin')
def list_support_tickets(request):
    data = SupportTicket.objects.all().order_by('-created_at')
    return render(request, 'support_chat.html', {'data': data})



@login_required(login_url='login_admin')
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    messages = ticket.messages.all().order_by('created_at')
    data = SupportTicket.objects.all().order_by('-created_at')

    if request.method == "POST":
        msg = request.POST.get('message')
        if msg:
            TicketMessage.objects.create(ticket=ticket, sender=request.user, message=msg)
            return redirect('ticket_detail', ticket_id=ticket_id)

    return render(request, 'support_chat.html', {
        'ticket': ticket,
        'messages': messages,
        'data': data,
        'active_id': ticket.id  # ✅ This enables active highlighting in template
    })
