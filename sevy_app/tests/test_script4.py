import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy.settings')
django.setup()

from sevy_app.models import Company

comp = Company.objects.filter(company_id="0cb366251d73d1f20f519f81").first()
if comp:
    print(f"Company: {comp}")
    print(f"User attached to this company: {comp.user}")
    print(f"Company ID: {comp.company_id}")
    print(f"Company Name: {comp.company_name}")
else:
    print("Company not found")
