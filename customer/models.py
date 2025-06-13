from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ScamComplaint(models.Model):
    CATEGORY_CHOICES = [
        ('phishing', 'Phishing'),
        ('investment', 'Investment Scam'),
        ('fake_product', 'Fake Product'),
        ('job_fraud', 'Job Fraud'),
        ('other', 'Other'),
    ]

    SOCIAL_MEDIA_CHOICES = [
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter'),
        ('telegram', 'Telegram'),
        ('whatsapp', 'WhatsApp'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_review', 'In Review'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="scam_complaints")
    name = models.CharField(max_length=255)
    website = models.URLField(blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    category = models.ForeignKey("masters.ScamCategory", on_delete=models.CASCADE)
    description = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    social_media = models.CharField(max_length=50, choices=SOCIAL_MEDIA_CHOICES)

    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ScamProof(models.Model):
    complaint = models.ForeignKey(ScamComplaint, on_delete=models.CASCADE, related_name='proofs')
    file = models.FileField(upload_to='scam_proofs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
