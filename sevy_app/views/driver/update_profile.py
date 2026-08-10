from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models.driver import Driver

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_driver_profile(request, driver_id):
    try:
        driver = Driver.objects.get(userid=driver_id)
    except Driver.DoesNotExist:
        return Response({
            "code": 404,
            "status": False,
            "message": "Driver not found.",
            "body": {}
        }, status=status.HTTP_404_NOT_FOUND)

    data = request.data
    updated = False

    if 'full_name' in data:
        driver.full_name = data['full_name']
        updated = True
    if 'names' in data:
        driver.full_name = data['names']
        updated = True
    if 'phone_number' in data:
        driver.phone_number = data['phone_number']
        updated = True
    if 'vehicle_make_color' in data:
        driver.vehicle_make_color = data['vehicle_make_color']
        updated = True
    if 'plate_number' in data:
        driver.plate_number = data['plate_number']
        updated = True
    if 'experience_years' in data:
        driver.experience_years = data['experience_years']
        updated = True
    if 'sex' in data:
        driver.sex = data['sex']
        updated = True
    if 'home_location_name' in data:
        driver.home_location_name = data['home_location_name']
        updated = True
    if 'home_latitude' in data:
        driver.home_latitude = data['home_latitude']
        updated = True
    if 'home_longitude' in data:
        driver.home_longitude = data['home_longitude']
        updated = True
    if 'owns_car' in data:
        # Check for boolean or string representation
        val = data['owns_car']
        if isinstance(val, str):
            driver.owns_car = val.lower() == 'true'
        else:
            driver.owns_car = bool(val)
        updated = True

    if updated:
        # Note: We are NOT unapproving the driver automatically as requested.
        driver.save()
        
        body = {
            "userid": driver.userid.custom_id,
            "names": driver.full_name,
            "phone_number": driver.phone_number,
            "vehicle_make_color": driver.vehicle_make_color,
            "plate_number": driver.plate_number,
            "experience_years": driver.experience_years,
            "sex": driver.sex,
            "home_location_name": driver.home_location_name,
            "owns_car": driver.owns_car,
        }

        return Response({
            "code": 200,
            "status": True,
            "message": "Driver profile updated successfully.",
            "body": body
        }, status=status.HTTP_200_OK)
        
    return Response({
        "code": 400,
        "status": False,
        "message": "No valid fields provided to update.",
        "body": {}
    }, status=status.HTTP_400_BAD_REQUEST)
