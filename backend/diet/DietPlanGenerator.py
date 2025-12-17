# -*- coding: utf-8 -*-
import sys
import io
# Force UTF-8 encoding for stdout on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
import json
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import google.generativeai as genai
from UserProfile import UserProfile
from NutritionCalculator import NutritionCalculator
from RecipeRag import RecipeRAG


class DietPlanGenerator:


    def __init__(self,
                 rag: RecipeRAG,
                 gemini_api_key: str = None):

        self.rag = rag

        # Inicjalizacja Gemini
        api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("Brak klucza API Gemini. Ustaw zmienną środowiskową GEMINI_API_KEY.")
        
        genai.configure(api_key=api_key)
        
        target_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        
        self.model = genai.GenerativeModel(target_model)
        self.gemini_model = target_model
        self._is_generating = False
        
        print(f"Zainicjalizowano Gemini z modelem: {self.gemini_model}")

    def generate_meal_plan(self,
                          user: UserProfile,
                          diversity_seed: Optional[int] = None) -> Dict[str, Any]:
        if self._is_generating:
            raise RuntimeError("Plan diety jest już generowany.")
        self._is_generating = True
        try:
            print("GENEROWANIE PLANU DIETETYCZNEGO")

            # Obliczanie BMR, TDEE, BMI i makroskładników
            calc = NutritionCalculator()
            bmi = calc.calculate_bmi(user)
            tdee = calc.calculate_tdee(user)
            macros = calc.calculate_macros(user, tdee)

            print(f"   BMI: {bmi['bmi']} ({bmi['category']})")
            print(f"   TDEE: {tdee} kcal")
            print(f"   Makro: P={macros['protein_g']}g C={macros['carbs_g']}g F={macros['fat_g']}g")

            # Ustawienie ziarna różnorodności
            if diversity_seed is None:
                diversity_seed = int(datetime.now().timestamp() * 1000) % 10000

            np.random.seed(diversity_seed)

            # Filtracja przepisów na podstawie profilu użytkownika
            preferred_df = self.rag.filter_recipes(user)
            # filtracja bez preferowanych składników
            user_dict = user.to_dict()
            user_dict_no_pref = dict(user_dict)
            user_dict_no_pref['prefer_ingredients'] = None
            user_no_pref = UserProfile(**user_dict_no_pref)
            broad_df = self.rag.filter_recipes(user_no_pref)

            print(f"   Preferowanych przepisów: {len(preferred_df)}")
            print(f"   Pasujących (bez preferencji): {len(broad_df)}")

            # Sprawdzenie czy przepisów jest wystarczająco dużo
            num_days = 7 if user.time_frame == 'week' else 1
            required_unique = num_days * user.num_meals
            preferred_unique_count = preferred_df['recipe_name'].nunique() if len(preferred_df) > 0 else 0
            prefer_strict = preferred_unique_count >= required_unique
            if prefer_strict:
                print(f"   Preferencje będą stosowane ({preferred_unique_count} unikalnych >= {required_unique} wymaganych).")
            else:
                print(f"    Nie wystarczająco preferowanych unikalnych przepisów ({preferred_unique_count} < {required_unique}) ")

            if len(broad_df) == 0:
                return {
                    'error': 'No recipes found matching your preferences',
                    'user_profile': user.to_dict(),
                    'nutrition': {'bmi': bmi, 'tdee': tdee, 'macros': macros}
                }

            # Generowanie planu z użyciem obu zestawów przepisów
            meal_plan = self._generate_plan_with_gemini(
                user=user,
                preferred_df=preferred_df,
                broad_df=broad_df,
                prefer_strict=prefer_strict,
                num_days=num_days,
                target_calories_per_day=tdee,
                target_macros=macros,
                diversity_seed=diversity_seed
            )

            # Budowanie odpowiedzi
            response = {
                'user_profile': user.to_dict(),
                'nutrition': {
                    'bmi': bmi,
                    'tdee': tdee,
                    'daily_targets': macros
                },
                'meal_plan': meal_plan,
                'diversity_seed': diversity_seed,
                'generated_at': datetime.now().isoformat()
            }

            return response
        finally:
            self._is_generating = False

    def _generate_plan_with_gemini(self,
                                   user: UserProfile,
                                   preferred_df: pd.DataFrame,
                                   broad_df: pd.DataFrame,
                                   prefer_strict: bool,
                                   num_days: int,
                                   target_calories_per_day: float,
                                   target_macros: Dict[str, float],
                                   diversity_seed: int) -> List[Dict[str, Any]]:
        print(f"\n Generowanie planu na {num_days} dni")

        # Obliczanie kalorii na posiłek
        calories_per_meal = target_calories_per_day / user.num_meals

        # Definiowanie slotów posiłków
        if user.num_meals == 3:
            meal_slots = ['breakfast', 'lunch', 'dinner']
            calorie_distribution = [0.3, 0.35, 0.35]  # 30%, 35%, 35%
        elif user.num_meals == 4:
            meal_slots = ['breakfast', 'lunch', 'dinner', 'snack']
            calorie_distribution = [0.25, 0.3, 0.35, 0.1]
        else:  # 5 posiłków
            meal_slots = ['breakfast', 'snack1', 'lunch', 'snack2', 'dinner']
            calorie_distribution = [0.25, 0.1, 0.3, 0.1, 0.25]

        # Generowanie planu na każdy dzień
        plan = []
        used_recipes = set()  # Śledzenie, aby unikać powtórek między dniami

        for day in range(1, num_days + 1):
            print(f"\n   Dzien {day}...")
            daily_plan = {
                'day': day,
                'meals': [],
                'daily_totals': {
                    'calories': 0,
                    'protein_g': 0,
                    'carbs_g': 0,
                    'fat_g': 0
                }
            }

            for slot_idx, meal_slot in enumerate(meal_slots):
                target_calories = target_calories_per_day * calorie_distribution[slot_idx]

                #Traktowanie lunch/obiad jako wymienne główne posiłki
                search_slots = [meal_slot]
                if meal_slot == 'dinner':
                    search_slots = ['lunch', 'dinner']
                elif meal_slot == 'lunch':
                    search_slots = ['lunch', 'dinner']

                # Wybór kandydatów
                candidates = pd.DataFrame()
                if len(preferred_df) > 0:
                    candidates = preferred_df[
                        (preferred_df['meal_slot'].isin(search_slots)) &
                        (~preferred_df['recipe_name'].isin(used_recipes))
                    ].copy()

                # Jeśli wymagana jest ścisła preferencja i mamy wystarczająco dużo preferowanych przepisów, wymuszamy je
                if prefer_strict:
                    if len(candidates) == 0:

                        candidates = preferred_df[
                            preferred_df['meal_slot'].isin(search_slots)
                        ].copy()
                else:
                    # Jeśli brak kandydatów w preferowanych
                    if len(candidates) == 0:
                        candidates = broad_df[
                            (broad_df['meal_slot'].isin(search_slots)) &
                            (~broad_df['recipe_name'].isin(used_recipes))
                        ].copy()

                    # jeżeli nadal brak
                    if len(candidates) == 0 and len(preferred_df) > 0:
                        candidates = preferred_df[
                            preferred_df['meal_slot'].isin(search_slots)
                        ].copy()

                if len(candidates) == 0:
                    candidates = broad_df[
                        broad_df['meal_slot'].isin(search_slots)
                    ].copy()

                # Filtruje według zakresu kalorii (±30%)
                calorie_min = target_calories * 0.7
                calorie_max = target_calories * 1.3

                if 'calories_per_serving' in candidates.columns:
                    candidates_by_cal = candidates[
                        (candidates['calories_per_serving'] >= calorie_min) &
                        (candidates['calories_per_serving'] <= calorie_max)
                    ]
                    if len(candidates_by_cal) > 0:
                        candidates = candidates_by_cal

                if len(candidates) == 0:
                    print(f"       Brak przepisów w zakresie kalorii dla {meal_slot}")
                    candidates = broad_df.head(20).copy()

                # Dodawanie losowości
                if len(candidates) > 0:
                    candidates = candidates.sample(frac=1, random_state=diversity_seed + day + slot_idx)

                # Wybór najlepszego przepisu za pomocą Gemini
                selected_recipe = self._select_recipe_with_gemini(
                    candidates=candidates.head(10),  # Top 10 kandydatów
                    meal_slot=meal_slot,
                    target_calories=target_calories,
                    target_macros=target_macros,
                    already_used=list(used_recipes)
                )

                if selected_recipe is not None:
                    # Dodawanie do planu
                    meal_info = {
                        'meal_slot': meal_slot,
                        'recipe_name': selected_recipe['recipe_name'],
                        'servings': 1,
                        'calories': selected_recipe['calories_per_serving'],
                        'protein_g': selected_recipe['protein_per_serving'],
                        'carbs_g': selected_recipe['carbs_per_serving'],
                        'fat_g': selected_recipe['fat_per_serving'],
                        'fiber_g': selected_recipe.get('fiber_per_serving', 0),
                        'cuisine': selected_recipe.get('primary_cuisine'),
                        'ingredients': selected_recipe.get('ingredient_lines'),
                        'instructions': selected_recipe.get('instructions')
                    }

                    daily_plan['meals'].append(meal_info)

                    # Aktualizacja dziennych zapotrzebowań
                    daily_plan['daily_totals']['calories'] += meal_info['calories']
                    daily_plan['daily_totals']['protein_g'] += meal_info['protein_g']
                    daily_plan['daily_totals']['carbs_g'] += meal_info['carbs_g']
                    daily_plan['daily_totals']['fat_g'] += meal_info['fat_g']

                    # Oznaczanie przepisu jako użytego
                    used_recipes.add(selected_recipe['recipe_name'])
                else:
                    print(f" Nie znaleziono przepisu dla {meal_slot}")

            # Zaokrąglanie dziennych ZAPOTRZEBOWAŃ
            for key in daily_plan['daily_totals']:
                daily_plan['daily_totals'][key] = round(daily_plan['daily_totals'][key], 1)

            plan.append(daily_plan)

        print(f"\n Plan wygenerowany!")
        return plan

    def _select_recipe_with_gemini(self,
                               candidates: pd.DataFrame,
                               meal_slot: str,
                               target_calories: float,
                               target_macros: Dict[str, float],
                               already_used: List[str]) -> Optional[Dict[str, Any]]:

        if len(candidates) == 0:
            return None

        #  informacje o kandydatach dla modelu
        candidate_info = []
        for idx, row in candidates.iterrows():
            info = {
                'name': row['recipe_name'],
                'calories': row['calories_per_serving'],
                'protein': row['protein_per_serving'],
                'carbs': row['carbs_per_serving'],
                'fat': row['fat_per_serving'],
                'cuisine': row['primary_cuisine']
            }
            candidate_info.append(info)


        prompt = f"""You are a nutrition expert helping select the best recipe for a meal.

MEAL SLOT: {meal_slot}
TARGET CALORIES: {target_calories:.0f} kcal
TARGET MACROS: Protein {target_macros['protein_g']}g, Carbs {target_macros['carbs_g']}g, Fat {target_macros['fat_g']}g

CANDIDATES:
{json.dumps(candidate_info, indent=2)}

ALREADY USED TODAY: {', '.join(already_used[-5:]) if already_used else 'None'}

Select the BEST recipe that:
1. Is closest to target calories
2. Balances macros well
3. Provides variety (different from already used)
4. Is nutritious
5. Do not select a recipe that has intolerances ingredients
6. Prioritize preferred ingredients if possible


Respond with ONLY the recipe name, nothing else."""

        try:
            response = self.model.generate_content(prompt)
            selected_name = getattr(response, "text", None) or getattr(response, "output_text", None) or str(response)
            if isinstance(selected_name, str):
                selected_name = selected_name.strip().strip('"')
        except Exception as e:
            print(f"    Gemini error: {e}")
            selected_name = None

        # Wybór przepisu na podstawie odpowiedzi modelu
        if selected_name:
            selected = candidates[candidates['recipe_name'] == selected_name]
            if len(selected) > 0:
                return selected.iloc[0].to_dict()

        # zwracanie pierwszego kandydata, który nie był jeszcze użyty, w przeciwnym razie pierwszego kandydata
        for _, row in candidates.iterrows():
            if row['recipe_name'] not in already_used:
                return row.to_dict()
        if len(candidates) > 0:
            return candidates.iloc[0].to_dict()
        return None
