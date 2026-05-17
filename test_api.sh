#!/bin/bash

# Test API Endpoints

BASE_URL="http://localhost:8001/api/v1"

echo "=== Health Check ==="
curl -s http://localhost:8001/ | jq .

echo -e "\n=== Get All Deliveries ==="
curl -s $BASE_URL/deliveries | jq .

echo -e "\n=== Create Delivery ==="
DELIVERY_RESPONSE=$(curl -s -X POST $BASE_URL/deliveries \
  -H 'Content-Type: application/json' \
  -d '{"customer_id":"customer_001","courier_id":"courier_001","address":"Toshkent, Amir Temur ko'chasi 15","latitude":41.3111,"longitude":69.2797,"items":{},"estimated_time":15}')
echo $DELIVERY_RESPONSE | jq .
DELIVERY_ID=$(echo $DELIVERY_RESPONSE | jq -r '.id')

echo -e "\n=== Get Deliveries by Courier ==="
curl -s "$BASE_URL/deliveries?courier_id=courier_001" | jq .

echo -e "\n=== Create Building ==="
BUILDING_RESPONSE=$(curl -s -X POST $BASE_URL/buildings \
  -H 'Content-Type: application/json' \
  -d '{"address":"Toshkent, Amir Temur ko'chasi 15","latitude":41.3111,"longitude":69.2797,"building_type":"MODERN","floors":16,"has_elevator":true,"elevator_type":"CHIP_REQUIRED","difficulty_score":3,"access_notes":"Lift faqat chip bilan ishlaydi"}')
echo $BUILDING_RESPONSE | jq .
BUILDING_ID=$(echo $BUILDING_RESPONSE | jq -r '.id')

echo -e "\n=== Get Building by Address ==="
curl -s "$BASE_URL/buildings/address?address=Toshkent,%20Amir%20Temur%20ko'chasi%2015" | jq .

echo -e "\n=== Create Domofon Code ==="
curl -s -X POST $BASE_URL/domofon-codes \
  -H 'Content-Type: application/json' \
  -d "{\"building_id\":\"$BUILDING_ID\",\"entrance_number\":\"1\",\"code\":\"1234\",\"code_type\":\"NUMERIC\",\"added_by\":\"courier_001\"}" | jq .

echo -e "\n=== Get Most Verified Code ==="
curl -s "$BASE_URL/domofon-codes/building/$BUILDING_ID/verified" | jq .

echo -e "\n=== Save Location ==="
curl -s -X POST $BASE_URL/locations \
  -H 'Content-Type: application/json' \
  -d '{"courier_id":"courier_001","latitude":41.3111,"longitude":69.2797,"accuracy":10.0,"altitude":450.0,"timestamp":'$(date +%s%N)'}' | jq .

echo -e "\n=== Save Location Point ==="
curl -s -X POST $BASE_URL/locations/points \
  -H 'Content-Type: application/json' \
  -d "{\"delivery_id\":\"$DELIVERY_ID\",\"latitude\":41.3111,\"longitude\":69.2797,\"accuracy\":10.0,\"altitude\":450.0,\"timestamp\":$(date +%s%N),\"speed\":5.5,\"activity_type\":\"IN_VEHICLE\"}" | jq .

echo -e "\n=== Update Delivery Status ==="
curl -s -X PATCH "$BASE_URL/deliveries/$DELIVERY_ID/status" \
  -H 'Content-Type: application/json' \
  -d '{"status":"IN_TRANSIT"}' | jq .

echo -e "\n=== All Tests Complete ==="
