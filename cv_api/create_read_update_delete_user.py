from django.http import JsonResponse
from django.conf import settings
import requests
import json
from Homepage.models import CustomUser


# Question: difference between class method and instance method in python

# Instance methods need a class instance and can access the instance through self .
# Class methods don't need a class instance. They can't access the instance ( self )
#  but they have access to the class itself via cls . Static methods don't have access to cls or self .


# End result : staticmethod register_user cannot call get_user
# End result : if register_user were a @classmethod, then it can call get_user via cls


class TokenUtils:

    @staticmethod
    def register_user(user):
        # Define the URL of the API endpoint for user registration
        if settings.DEBUG:
            api_url = (
                "https://diverse-intense-whippet.ngrok-free.app/api/auth/crud-user/"
            )
        else:
            api_url = "https://osamaaslam.pythonanywhere.com/api/auth/crud-user/"

        headers = {"Content-Type": "application/json"}

        user_data = {
            "email": user.email,
            "username": user.username,
            "password": "password123",
        }

        try:
            # Send a POST request to the API endpoint to register the user
            response = requests.post(
                api_url, data=json.dumps(user_data), headers=headers, verify=False
            )

            # display the Headers in response
            print(response.headers)
            # display the response body equivalent to request.body
            print(response.content)

            # Check if the user is created (status code 201)
            if response.status_code == 201:
                # Parse the JSON response to extract the access and refresh tokens
                json_response = response.json()
                print(f"response_register___________{json_response}")
                return json_response
            else:
                return None

        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": f"Request failed: {e}"}, status=500)

    @staticmethod  # It can be called either on the class (e.g. C.f()) or on an instance (e.g. C().f()).
    def get_user(user):

        if settings.DEBUG:
            api_url = "https://diverse-intense-whippet.ngrok-free.app/api/auth/get-api-user-id-for-user/"
        else:
            api_url = "https://osamaaslam.pythonanywhere.com/api/auth/get-api-user-id-for-user/"

        headers = {"Content-Type": "application/json"}

        user_data = {
            "email": user.email,
            "username": user.username,
            "password": "password123",
        }

        try:
            response = requests.post(
                api_url, data=json.dumps(user_data), headers=headers, verify=False
            )
            if response.status_code == 200:
                print(f"response_get_____________{response.status_code}")
                # Parse the JSON response to extract the access and refresh tokens
                json_response = response.json()
                # display the Headers in response
                print(response.headers)

                # display the response body equivalent to request.body
                print(response.content)

                print(f"user_get_____{json_response}")

                print(f"json_response________________{json_response}")
                if json_response and "id" in json_response:
                    print(f"json_response________________{json_response}")
                    return json_response
                else:
                    return None  # response is list who 0th element id dict containg user details
            else:
                return None
        except requests.exceptions.RequestException as e:
            # Return an error message if there was an issue with the request
            return JsonResponse({"error": f"Request failed: {e}"}, status=500)

        # Caution : if you have already acquired the tokens, then django_rest_framework_jwt library will
        #            generate new tokens (both access, and refresh), and send these in Response()

    @staticmethod  # It can be called either on the class (e.g. C.f()) or on an instance (e.g. C().f()).
    def get_tokens_for_user(user_id):

        if settings.DEBUG:
            api_url = "https://diverse-intense-whippet.ngrok-free.app/api/auth/token/"
        else:
            api_url = "https://osamaaslam.pythonanywhere.com/api/auth/token/"

        headers = {"Content-Type": "application/json"}

        user = CustomUser.objects.filter(id=user_id).first()
        print(f"user_get_tokens_for_user________________{user}")

        # Define the user data to be sent in the request body
        user_data = {
            "email": user.email,
            "username": user.username,
            "password": "password123",
        }

        try:
            # Send a POST request to the API endpoint to register the user
            response = requests.post(
                api_url, data=json.dumps(user_data), headers=headers, verify=False
            )

            # display the Headers in response
            print(f"headers_get_tokens_for_user________{response.headers}")
            # display the response body equivalent to request.body
            print(f"content_get_tokens_for_user--------------{response.content}")

            if response.status_code == 200:
                tokens = response.json()
                print(f"tokens________________{tokens}")
                return tokens
            else:
                return JsonResponse({"status": response.json()})

        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": f"Request failed: {e}"}, status=500)

    @staticmethod  # It can be called either on the class (e.g. C.f()) or on an instance (e.g. C().f()).
    def get_new_access_token_for_user(refresh_token):
        # Define the URL of the API endpoint for acquiring fresh access token using refresh token

        # Caution :RuntimeError: You called this URL via POST, but the URL doesn't end in a slash and you have APPEND_SLASH set
        if settings.DEBUG:
            api_url = (
                "https://diverse-intense-whippet.ngrok-free.app/api/auth/token/refresh/"
            )
        else:
            api_url = "https://osamaaslam.pythonanywhere.com/api/auth/token/refresh/"

        headers = {"Content-Type": "application/json"}

        user_data = {
            "refresh": refresh_token
        }  # key must be "refresh" else 400 Bad request
        try:
            response = requests.post(
                api_url, data=json.dumps(user_data), headers=headers, verify=False
            )
            print(response.content)  # json containing the access_token

            if response.status_code == 200:
                response = response.json()
                access_token = response["access"]

                print(access_token)
                return access_token
            else:
                return {
                    "json_response": response.json(),
                    "status": response.status_code,
                }

        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": f"Request failed: {e}"}, status=500)

    @staticmethod  # It can be called either on the class (e.g. C.f()) or on an instance (e.g. C().f()).
    def verify_access_token_for_user(access_token):

        # Caution :RuntimeError: You called this URL via POST, but the URL doesn't end in a slash and you have APPEND_SLASH set
        if settings.DEBUG:
            api_url = (
                "https://diverse-intense-whippet.ngrok-free.app/api/auth/token/verify/"
            )
        else:
            api_url = "https://osamaaslam.pythonanywhere.com/api/auth/token/verify/"

        headers = {"Content-Type": "application/json"}

        user_data = {
            "token": access_token
        }  # key must be "token" else error status with 400/Bad request
        try:
            # Send a POST request to the API endpoint to register the user
            response = requests.post(
                api_url, data=json.dumps(user_data), headers=headers, verify=False
            )

            # print(response.content) will {} for 200

            if response.status_code == 200:
                return True
            else:
                return False
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": f"Request failed: {e}"}, status=500)
