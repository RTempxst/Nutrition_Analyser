from django.shortcuts import render, redirect
import requests
import re
from django.conf import settings  # Load API keys from settings


API_ENDPOINT = 'https://trackapi.nutritionix.com/v2/natural/nutrients/'

def search_ingredient(request):
    
    print("API Key:", settings.NUTRITIONIX_API_KEY)
    print("App ID:", settings.NUTRITIONIX_API_ID)

    nutrition_data = None
    error_message = None
    total_data = {'calories': 0, 'fat': 0, 'protein': 0, 'carbs': 0}

    # Retrieve API keys securely
    API_ID = settings.NUTRITIONIX_API_ID
    API_KEY = settings.NUTRITIONIX_API_KEY

    if 'ingredient_list' not in request.session:
        request.session['ingredient_list'] = []

    ingredient_list = request.session['ingredient_list']

    if request.method == 'POST':
        query = request.POST.get('ingredient')

        if query:
            try:
                # Parse quantity and ingredient name
                match = re.match(r'(\d+)\s*(.*)', query)
                if match:
                    quantity = match.group(1)
                    ingredient_name = match.group(2).strip()
                    full_query = f"{quantity} {ingredient_name}"
                else:
                    quantity = 1  # Default to 1
                    ingredient_name = query
                    full_query = query

                # API request setup
                headers = {
                    'x-app-id': API_ID,
                    'x-app-key': API_KEY,
                    'Content-Type': 'application/json'
                }
                data = {'query': full_query}

                # Fetch nutrition data
                response = requests.post(API_ENDPOINT, json=data, headers=headers)

                if response.status_code == 200:
                    nutrition_data = response.json()
                    food_info = nutrition_data.get('foods', [])[0]
                    food_info['quantity'] = quantity  # Add quantity
                    ingredient_list.append(food_info)
                    request.session['ingredient_list'] = ingredient_list
                else:
                    error_message = f"Error: {response.status_code} - Unable to fetch data."
            except Exception as e:
                error_message = f"Exception occurred: {str(e)}"
        else:
            error_message = "Please enter an ingredient."

    # Calculate totals
    for food in ingredient_list:
        total_data['calories'] += float(food.get('nf_calories', 0)) * int(food.get('quantity', 1))
        total_data['fat'] += float(food.get('nf_total_fat', 0)) * int(food.get('quantity', 1))
        total_data['protein'] += float(food.get('nf_protein', 0)) * int(food.get('quantity', 1))
        total_data['carbs'] += float(food.get('nf_total_carbohydrate', 0)) * int(food.get('quantity', 1))

    return render(request, 'Nutriapp/home.html', {
        'nutrition_data': nutrition_data,
        'ingredient_list': ingredient_list,
        'total_data': total_data,
        'error_message': error_message
    })


def clear_list(request):
    """Clear the ingredient list from the session."""
    request.session['ingredient_list'] = []
    return redirect('search_ingredient')


def about(request):
    return render(request, 'Nutriapp/about.html', {'title': 'About'})

