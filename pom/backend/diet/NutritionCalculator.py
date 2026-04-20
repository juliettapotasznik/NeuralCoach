from typing import Dict, Any
from UserProfile import UserProfile


class NutritionCalculator:
    @staticmethod
    def calculate_bmr(user: UserProfile) -> float:
        #BMR = Basal Metabolic Rate
        if user.gender.lower() == 'male':
            bmr = (10 * user.weight) + (6.25 * user.height) - (5 * user.age) + 5
        else:
            bmr = (10 * user.weight) + (6.25 * user.height) - (5 * user.age) - 161

        return round(bmr, 1)

    @staticmethod
    def calculate_tdee(user: UserProfile) -> float:
        #TDEE = Total Daily Energy Expenditure
        bmr = NutritionCalculator.calculate_bmr(user)

        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }

        tdee = bmr * activity_multipliers.get(user.activity_level, 1.55)

        # goal
        if user.goal == 'lose weight':
            tdee -= 500  # deficyt
        elif user.goal == 'gain weight':
            tdee += 500  # nadwyżka

        return round(tdee, 1)

    @staticmethod
    def calculate_bmi(user: UserProfile) -> Dict[str, Any]:

        #Oblicza BMI i kategorię
        height_m = user.height / 100
        bmi = user.weight / (height_m ** 2)

        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 25:
            category = "Normal weight"
        elif bmi < 30:
            category = "Overweight"
        else:
            category = "Obese"

        return {
            'bmi': round(bmi, 1),
            'category': category
        }

    @staticmethod
    def calculate_macros(user: UserProfile, tdee: float) -> Dict[str, float]:

        # Oblicza makroskładniki na podstawie profilu użytkownika i TDEE
        protein_ratio = 0.30
        carbs_ratio = 0.40
        fat_ratio = 0.30

        # Dostosuj na podstawie profilu makroskładników
        if user.macro_profile:
            profile = user.macro_profile.lower().replace('-', '_')

            if profile == 'high_protein':
                protein_ratio = 0.35
                carbs_ratio = 0.35
                fat_ratio = 0.30
            elif profile == 'low_carb':
                protein_ratio = 0.30
                carbs_ratio = 0.20
                fat_ratio = 0.50
            elif profile == 'low_fat':
                protein_ratio = 0.30
                carbs_ratio = 0.50
                fat_ratio = 0.20

        # Dostosuj na podstawie celu użytkownika
        if user.goal == 'gain weight':
            protein_ratio += 0.05
            carbs_ratio += 0.05
            fat_ratio -= 0.10
        elif user.goal == 'lose weight':
            protein_ratio += 0.05
            fat_ratio -= 0.05

        # Oblicz gramy makroskładników
        protein_calories = tdee * protein_ratio
        carbs_calories = tdee * carbs_ratio
        fat_calories = tdee * fat_ratio

        return {
            'calories': round(tdee, 1),
            'protein_g': round(protein_calories / 4, 1),
            'carbs_g': round(carbs_calories / 4, 1),
            'fat_g': round(fat_calories / 9, 1),
            'protein_percent': round(protein_ratio * 100, 1),
            'carbs_percent': round(carbs_ratio * 100, 1),
            'fat_percent': round(fat_ratio * 100, 1)
        }
