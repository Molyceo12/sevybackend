from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Company, Car

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_company(request):
    """
    Soft deletes a company and all of its associated cars.
    Expects JSON body: {"company_id": "id"}
    """
    company_id = request.data.get('company_id')

    if not company_id:
        return Response({
            "status": "error",
            "message": "company_id is required in the request body",
            "body": {}
        }, status=400)

    try:
        company = Company.objects.get(company_id=company_id)
        
        if company.is_deleted:
            return Response({
                "status": "error",
                "message": "Company is already deleted",
                "body": {}
            }, status=400)

        # Soft delete the company
        company.is_deleted = True
        company.save()

        # Cascade the soft delete to all cars owned by this company
        deleted_cars_count = Car.objects.filter(companyid=company, is_deleted=False).update(is_deleted=True)

        return Response({
            "status": "success",
            "message": f"Successfully deleted company and {deleted_cars_count} associated cars.",
            "body": {
                "company_id": company.company_id_id,
                "is_deleted": company.is_deleted,
                "deleted_cars_count": deleted_cars_count
            }
        }, status=200)

    except Company.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Company not found",
            "body": {}
        }, status=404)
    except Exception as e:
        return Response({
            "status": "error",
            "message": f"An error occurred: {str(e)}",
            "body": {}
        }, status=500)
