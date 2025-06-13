from rest_framework import viewsets, permissions
from .models import ScamComplaint
from .serializers import ScamComplaintSerializer

class ScamComplaintViewSet(viewsets.ModelViewSet):
    serializer_class = ScamComplaintSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ScamComplaint.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


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




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from .models import ScamComplaint, ScamProof
from .serializers import ScamProofSerializer

class UploadScamProofView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]


    def get(self, request, complaint_id):
        complaint = ScamComplaint.objects.filter(id=complaint_id, user=request.user).first()
        if not complaint:
            return Response({'error': 'Complaint not found'}, status=404)

        proofs = complaint.proofs.all()
        serializer = ScamProofSerializer(proofs, many=True)
        return Response(serializer.data)

    def post(self, request, complaint_id):
        complaint = ScamComplaint.objects.filter(id=complaint_id, user=request.user).first()
        if not complaint:
            return Response({'error': 'Complaint not found'}, status=404)

        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        proof = ScamProof.objects.create(complaint=complaint, file=file)
        return Response(ScamProofSerializer(proof).data)





def add_complaint(request):
    
    if request.method == 'POST':
        complaint_form = ScamComplaintForm(request.POST)
        proof_formset = ScamProofFormSet(request.POST, request.FILES)

        if complaint_form.is_valid() and proof_formset.is_valid():
            complaint = complaint_form.save(commit=False)
            complaint.user = request.user
            complaint.save()

            # link formset to the saved complaint instance
            proof_formset.instance = complaint
            proof_formset.save()

            return redirect('list_complaint')  # change to your success URL
        else:

            print(complaint_form.errors)
    else:
        complaint_form = ScamComplaintForm()
        proof_formset = ScamProofFormSet()

    return render(request, 'add_complaint.html', {
        'complaint_form': complaint_form,
        'proof_formset': proof_formset,
    })

def update_complaint(request, complaint_id):
    
    complaint = get_object_or_404(ScamComplaint, pk=complaint_id, user=request.user)

    if request.method == 'POST':
        complaint_form = ScamComplaintForm(request.POST, instance=complaint)
        proof_formset = ScamProofFormSet(request.POST, request.FILES, instance=complaint)

        if complaint_form.is_valid() and proof_formset.is_valid():
            complaint = complaint_form.save()
            proof_formset.save()
            return redirect('list_complaint')  # change to your list or detail page URL
    else:
        complaint_form = ScamComplaintForm(instance=complaint)
        proof_formset = ScamProofFormSet(instance=complaint)

    return render(request, 'add_complaint.html', {
        'complaint_form': complaint_form,
        'proof_formset': proof_formset,
        'update': True,
    })


def list_complaint(request):

    data = ScamComplaint.objects.all()

    return render(request, 'list_complaint.html', {'data' : data})


def delete_complaint(request, complaint_id):

    data = ScamComplaint.objects.get(id = complaint_id).delete()

    return redirect('list_complaint')




@login_required
def delete_proof(request, pk):

    proof = get_object_or_404(ScamProof, pk=pk, complaint__user=request.user)
    complaint_id = proof.complaint.id

    # Delete file and entry
    proof.file.delete()
    proof.delete()

    # Redirect using reverse and URL name
    return redirect(reverse('update_complaint', kwargs={'complaint_id': complaint_id}))




from rest_framework import status
from django.db.models import Q
from .models import User
from users.serializer import UserProfileSerializer

class SearchUserView(APIView):
    permission_classes = [IsAuthenticated]  # Optional: remove if public

    def get(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({"error": "Query parameter 'q' is required."}, status=status.HTTP_400_BAD_REQUEST)

        users = User.objects.filter(
            Q(mobile__icontains=query) | Q(name__icontains=query) | Q(profession__icontains=query) 
        ).only('id', 'name', 'mobile', 'profile_photo')[:20]

        serialized_users = UserProfileSerializer(users, many=True)
        return Response(serialized_users.data)