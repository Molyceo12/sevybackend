from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import CustomUser

@api_view(['POST', 'DELETE'])
@permission_classes([AllowAny])
def delete_account(request):
    try:
        userid = request.data.get('userid')
        
        if not userid:
            return Response({
                "code": 400,
                "status": False,
                "message": "Missing required field (userid).",
                "body": {}
            }, status=400)
            
        user = CustomUser.objects.filter(custom_id=userid).first()
        if not user:
            return Response({
                "code": 404,
                "status": False,
                "message": "User not found.",
                "body": {}
            }, status=404)
            
        # Perform a soft delete instead of hard delete to preserve historical records
        user.is_active = False
        user.is_deleted = True
        user.set_unusable_password()
        user.save()
        
        return Response({
            "code": 200,
            "status": True,
            "message": "User account has been successfully deactivated and deleted.",
            "body": {}
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": {}
        }, status=500)
