from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models.company import Company

@api_view(['PUT'])
@permission_classes([AllowAny])
def edit_company(request, company_id):
    """
    Edit basic company profile fields.
    """
    try:
        company = Company.objects.get(company_id=company_id)
    except Company.DoesNotExist:
        return Response({"error": "Company not found."}, status=status.HTTP_404_NOT_FOUND)

    # Extract fields from request data
    host_name = request.data.get('host_name')
    company_name = request.data.get('company_name')
    phone_number = request.data.get('phone_number')
    contact_email = request.data.get('contact_email')
    location = request.data.get('location')
    profile_image = request.data.get('profile_image') # or from request.FILES if it's a file upload

    # If it's a file upload, check request.FILES
    if not profile_image and request.FILES.get('profile_image'):
        profile_image = request.FILES.get('profile_image')

    updated = False
    
    if host_name is not None:
        company.host_name = host_name
        updated = True
    if company_name is not None:
        company.company_name = company_name
        updated = True
    if phone_number is not None:
        company.phone_number = phone_number
        updated = True
    if contact_email is not None:
        company.contact_email = contact_email
        updated = True
    if location is not None:
        company.location = location
        updated = True
    if profile_image is not None:
        company.profile_image = profile_image
        updated = True
        
    if updated:
        company.save()
        
        return Response({
            "message": "Company profile updated successfully.",
            "body": {
                "host_name": company.host_name,
                "company_name": company.company_name,
                "phone_number": company.phone_number,
                "contact_email": company.contact_email,
                "location": company.location,
                "profile_image": str(company.profile_image) if company.profile_image else None
            }
        }, status=status.HTTP_200_OK)
        
    return Response({
        "message": "No fields provided to update."
    }, status=status.HTTP_400_BAD_REQUEST)
