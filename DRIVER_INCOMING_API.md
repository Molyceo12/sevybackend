# Driver Incoming Requests API

## Endpoint
`POST /api/driver/trips/incoming/`

## Description
Returns all incoming requests (both trips AND bookings) for a driver that need attention or action.
Results are combined and sorted by newest first.

## Request Body
```json
{
    "driverid": "2309b77cc2d1fb2cc9a46783"
}
```

## Response Format
```json
{
    "code": 200,
    "status": true,
    "message": "Incoming requests fetched successfully. Found 2 trip(s) and 3 booking(s).",
    "total_count": 5,
    "trips_count": 2,
    "bookings_count": 3,
    "body": [
        // Array of trips and bookings, sorted by created_at descending (newest first)
    ]
}
```

## What It Returns

### Incoming Trips (Ride-Hailing)
**Filters:**
- `driverid` matches
- `service_type = 'driver_and_car'`
- `driver_status = 'waiting'` (waiting for driver acceptance)
- `status = 'upcoming'`

**Trip Object:**
```json
{
    "type": "trip",
    "trip_id": "f89afb0b3fa9e6f70f85c112",
    "tracking_number": "TRP-001-A-1",
    "userid": "2309b77cc2d1fb2cc9a46783",
    "customer_name": "irimaso Maurice",
    "start_place_name": "Dehradun, India",
    "destination_name": "Nyamata",
    "estimated_time": "15 mins",
    "distance": "6.08 km",
    "total_price": 2128.0,
    "status": "upcoming",
    "driver_status": "waiting",
    "payment_status": "paid",
    "service_type": "driver_and_car",
    "created_at": "2026-07-13T21:13:45.982118Z"
}
```

### Incoming Bookings (Car Rentals)
**Filters:**
- `driver` matches
- `status IN ['pending', 'confirmed']` (not yet started)

**Booking Object:**
```json
{
    "type": "booking",
    "booking_id": "abc123def456ghi789",
    "booking_number": "BKNG-001-A-0",
    "userid": "2309b77cc2d1fb2cc9a46783",
    "customer_name": "irimaso Maurice",
    "car": {
        "car_id": "car001",
        "name": "Toyota Camry",
        "brand": "Toyota"
    },
    "company": {
        "company_id": "comp001",
        "company_name": "Best Rentals Ltd"
    },
    "booking_type": "with_driver",
    "rental_plan": "daily",
    "start_date": "2026-07-15T08:00:00Z",
    "end_date": "2026-07-20T18:00:00Z",
    "pickup_location": "Kigali Airport",
    "dropoff_location": "Kigali City Center",
    "total_price": 250000.0,
    "status": "confirmed",
    "payment_status": "paid",
    "created_at": "2026-07-13T10:00:00Z"
}
```

## Key Features
1. ✅ **Combined Response** - Both trips and bookings in one API call
2. ✅ **Type Field** - Each item has `"type": "trip"` or `"type": "booking"` for easy identification
3. ✅ **Sorted by Newest** - All items sorted by `created_at` descending
4. ✅ **Counts Included** - Response includes `total_count`, `trips_count`, and `bookings_count`

## Use Case
Driver home screen showing all pending requests that need driver's attention:
- Trips waiting for acceptance
- Bookings that are confirmed but not yet started

## Flutter Model
The Flutter app uses `IncomingRequest` model that normalizes both trips and bookings:
- `type` - "trip" or "booking"
- `id` - trip_id or booking_id
- `locationInfo` - start_place_name or pickup_location
- `destinationInfo` - destination_name or dropoff_location
- `timeInfo` - estimated_time or date range
- `additionalInfo` - Map containing type-specific details
