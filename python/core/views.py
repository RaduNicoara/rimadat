import json
import polyline
import requests

from django.contrib.auth import login
from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView
from django.conf import settings
from rest_framework import generics
from math import radians, sin, cos, sqrt, atan2

from core.models import ConversationMessage, ChatConversation, Adventure, PointOfInterest
from core.serializers import ConversationMessageSerializer, ChatConversationSerializer, AdventureSerializer, \
    PointOfInterestSerializer
from rest_framework.authtoken.admin import User

from api.client import OpenAPIClient


def login_user(request, *args, **kwargs):
    data = json.loads(request.body.decode())
    user = User.objects.get(id=int(data["id"]))
    login(request, user)
    return HttpResponse(200)


def submit_response(request, *args, **kwargs):
    data = json.loads(request.body.decode())
    client = OpenAPIClient()
    conversation = ChatConversation.objects.get(id=data["conversation_id"])
    response = client.submit(conversation.get_messages_json())
    user = User.objects.get(username="system")
    ConversationMessage.objects.create(user=user, content=response["content"], conversation=conversation)
    content = json.dumps({"message": response["content"]}).encode()
    return HttpResponse(status=200, content_type="application_json", content=content)


class MainView(TemplateView):
    template_name = "main.html"

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        context["users"] = User.objects.all().values("id", "first_name")

        return context

# API Views


class ConversationMessageListCreateView(generics.ListCreateAPIView):
    queryset = ConversationMessage.objects.all()
    serializer_class = ConversationMessageSerializer
    authentication_classes = []


class ConversationMessageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ConversationMessage.objects.all()
    serializer_class = ConversationMessageSerializer
    authentication_classes = []


class ChatConversationListCreateView(generics.ListCreateAPIView):
    queryset = ChatConversation.objects.all()
    serializer_class = ChatConversationSerializer
    authentication_classes = []


class ChatConversationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ChatConversation.objects.all()
    serializer_class = ChatConversationSerializer
    authentication_classes = []


class AdventureListCreateView(generics.ListCreateAPIView):
    queryset = Adventure.objects.all()
    serializer_class = AdventureSerializer
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        start_location = request.data.get('start')
        end_location = request.data.get('end')
        return self.calculate_route(start_location, end_location)

    def calculate_route(self, start_location, end_location):
        url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start_location}&destination={end_location}&key={settings.GMAPS_API_KEY}"
        response = requests.get(url)
        data = response.json()

        # Extract the route polyline
        polyline = data["routes"][0]["overview_polyline"]["points"]

        decoded_coordinates = self.decode_polyline(polyline)

        desired_interval = 20  # Interval in kilometers
        trimmed_coordinates = []

        previous_coord = decoded_coordinates[0]
        total_distance = 0

        for coord in decoded_coordinates[1:]:
            distance = self.calculate_distance(previous_coord, coord)
            total_distance += distance

            if total_distance >= desired_interval:
                trimmed_coordinates.append(coord)
                total_distance = 0  # Reset the total distance

            previous_coord = coord

        pois = []
        for lat, lng in trimmed_coordinates:
            radius = 10000  # Adjust the radius as per your requirement
            types = ['amusement_park', 'park', 'library', 'aquarium', 'art_gallery', 'book_store', 'campground', 'church', 'city_hall',
                     'fire_station', 'hindu_temple', 'mosque', 'museum', 'post_office', 'primary_school', 'school', 'secondary_school',
                     'stadium', 'synagogue', 'tourist_attraction', 'train_station', 'university', 'zoo']  # Replace with desired types of POIs
            api_key = settings.GMAPS_API_KEY  # Replace with your actual API key

            pois_near_coordinate = self.get_pois_near_coordinate(lat, lng, radius, types, api_key)
            pois.extend(pois_near_coordinate)

        # Process the list of POIs retrieved
        return HttpResponse(status=200, content=json.dumps({"pois": pois}))

    def decode_polyline(self, polyline_str):
        return polyline.decode(polyline_str)

    def get_pois_near_coordinate(self, lat, lng, radius, types, api_key):
        url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
        params = {
            'location': f'{lat},{lng}',
            'radius': radius,
            'types': '|'.join(types),
            'key': api_key
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get('results', [])
        return []

    def calculate_distance(self, coord1, coord2):
        # Earth's radius in kilometers
        R = 6371.0

        lat1 = radians(coord1[0])
        lon1 = radians(coord1[1])
        lat2 = radians(coord2[0])
        lon2 = radians(coord2[1])

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        return distance


class AdventureRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Adventure.objects.all()
    serializer_class = AdventureSerializer
    authentication_classes = []


class PointOfInterestListCreateView(generics.ListCreateAPIView):
    queryset = PointOfInterest.objects.all()
    serializer_class = PointOfInterestSerializer
    authentication_classes = []


class PointOfInterestRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PointOfInterest.objects.all()
    serializer_class = PointOfInterestSerializer
    authentication_classes = []
