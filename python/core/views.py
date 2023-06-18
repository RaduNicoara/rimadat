import json
import polyline
import requests

from django.contrib.auth import login
from django.http import HttpResponse
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


def quiz_completed(request, *args, **kwargs):
    data = json.loads(request.body.decode())
    points_earned = data['points_earned']
    adventure = Adventure.objects.get(id=data['adventure_id'])
    adventure.points_earned += points_earned
    adventure.save()
    content = json.dumps({"message": 'Congratulations! You got %d answers right! You have a total of %d points!'
                                     % (points_earned, adventure.points_earned)})
    return HttpResponse(status=200, content_type="application_json", content=content)


class MainView(TemplateView):
    template_name = "main.html"

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        context["users"] = User.objects.all().values("id", "first_name")

        return context


class QuizView(TemplateView):
    template_name = "quiz.html"

    def get_context_data(self, **kwargs):
        questions = [
          {
            "question": "Who led the Legion of the Iron Wolves in the battle for independence?",
            "optionA": "General Adrian Vasilescu",
            "optionB": "Colonel Victor Popescu",
            "optionC": "Captain Radu Constantinescu",
            "optionD": "Major Alexandru Ionescu",
            "correctOption": "optionA"
          },
          {
            "question": "In which year did the famous battle for independence take place in Romania?",
            "optionA": "1910",
            "optionB": "1923",
            "optionC": "1935",
            "optionD": "1948",
            "correctOption": "optionB"
          },
          {
            "question": "What became a symbol of resistance in Romania after the victory in the battle?",
            "optionA": "The Legion of the Iron Wolves",
            "optionB": "The Legion of the Golden Eagles",
            "optionC": "The Battalion of the Silver Falcons",
            "optionD": "The Regiment of the Bronze Lions",
            "correctOption": "optionA"
          }
        ]
        context = super(QuizView, self).get_context_data(**kwargs)
        context['questions_dict'] = questions
        context['adventure_id'] = 1
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
        user_id = request.data.get('user')
        return self.calculate_route(start_location, end_location, user_id)

    def calculate_route(self, start_location, end_location, user_id):
        end = self.geocode_location(end_location)
        start_lat = start_location['lat']
        start_lng = start_location['lng']
        end_lat = end['results'][0]['geometry']['location']['lat']
        end_lng = end['results'][0]['geometry']['location']['lng']

        adv, _ = Adventure.objects.get_or_create(
            user=User.objects.get(pk=user_id),
            starting_point_longitude=start_lng,
            starting_point_latitude=start_lat,
            destination_longitude=end_lng,
            destination_latitude=end_lat
        )

        url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start_lat},{start_lng}&destination={end_location}&key={settings.GMAPS_API_KEY}"
        response = requests.get(url)
        data = response.json()

        # Extract the route polyline
        polyline = data["routes"][0]["overview_polyline"]["points"]

        decoded_coordinates = self.decode_polyline(polyline)

        desired_interval = 10  # Interval in kilometers
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
        final_pois = []
        for lat, lng in trimmed_coordinates:
            radius = 5000  # Adjust the radius as per your requirement
            types = ['tourist_attraction']
            api_key = settings.GMAPS_API_KEY  # Replace with your actual API key

            pois_near_coordinate = self.get_pois_near_coordinate(lat, lng, radius, types, api_key)
            pois.extend(pois_near_coordinate)

        previous_poi = pois[0]
        total_poi_dist = 0
        for poi in pois:
            poi_coord = [poi['geometry']['location']['lat'], poi['geometry']['location']['lng']]
            previous_poi_coord = [previous_poi['geometry']['location']['lat'], previous_poi['geometry']['location']['lng']]

            poi_dist = self.calculate_distance(previous_poi_coord, poi_coord)
            total_poi_dist += poi_dist

            if total_poi_dist >= desired_interval:
                obj, created = PointOfInterest.objects.get_or_create(
                    place_id=poi['place_id'],
                    defaults={
                        'name': poi['name'],
                        'longitude': poi['geometry']['location']['lng'],
                        'latitude': poi['geometry']['location']['lat']
                    }
                )
                if not obj.visited:
                    obj.adventure = adv
                    obj.save()
                    final_pois.extend([poi])

                total_poi_dist = 0
            previous_poi = poi

        # Process the list of POIs retrieved
        return HttpResponse(status=200, content=json.dumps({"pois": final_pois}))

    def geocode_location(self, location):
        geocode_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={settings.GMAPS_API_KEY}'
        response = requests.get(geocode_url)
        return response.json()

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
