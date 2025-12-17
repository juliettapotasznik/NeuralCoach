import csv
import json
import random
import time
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#rozdzielenie stylu na liste
def style_matches(ex_style: str, wanted: set[str]) -> bool:
    tokens = {t.strip() for t in ex_style.split(",")}
    return not tokens.isdisjoint(wanted)

SECONDS_PER_REP = 5             
SECONDS_REST_BETWEEN_SETS = 60 

def estimate_exercise_time(ex: dict) -> float:
    unit = ex.get("duration_unit", "reps")
    
    try:
        sets = int(ex.get("default_sets", 1) or 1)
        reps_or_time = int(ex.get("default_reps", 10) or 10)
    except (ValueError, TypeError):

        sets = 3
        reps_or_time = 10
        unit = "reps" 

    total_seconds = 0

    if unit == "reps":
        work_seconds = sets * reps_or_time * SECONDS_PER_REP
        rest_seconds = (sets - 1) * SECONDS_REST_BETWEEN_SETS
        total_seconds = work_seconds + rest_seconds
    
    elif unit == "seconds":
        work_seconds = sets * reps_or_time
        total_seconds = work_seconds

    elif unit == "minutes":
        work_minutes = sets * reps_or_time
        total_seconds = work_minutes * 60
    
    else:
        total_seconds = 240

    return round(total_seconds / 60, 1)

def filter_exercises(user, exercises):
    # by location
    filtered_exercises = [ex for ex in exercises if ex["location"] in ["both", user["training_location"]]]

    # by equipment
    if user["training_location"] in {"home", "both"} and user.get("equipment"):
        allowed = set(user["equipment"])
        allowed.add("body weight")
        filtered_exercises = [ex for ex in filtered_exercises if ex["equipment"] in allowed]
    
    # by goal
    if user["goal"] == "build_muscle":
        filtered_exercises = [
            ex for ex in filtered_exercises
            if style_matches(ex["style"], {"strength_training", "calisthenics"})
        ]
    elif user["goal"] == "lose_weight":
        filtered_exercises = [
            ex for ex in filtered_exercises
            if style_matches(ex["style"], {"hiit", "cardio", "strength_training", "calisthenics"})
        ]
    elif user["goal"] == "improve_flexibility":
        filtered_exercises = [
            ex for ex in filtered_exercises
            if style_matches(ex["style"], {"mobility_flexibility"})
        ]
    elif user["goal"] == "improve_endurance":
        filtered_exercises = [
            ex for ex in filtered_exercises
            if style_matches(ex["style"], {"hiit", "cardio"})
        ]
    elif user["goal"] == "improve_overall_fitness":
        filtered_exercises = [
            ex for ex in filtered_exercises
            if style_matches(ex["style"], {"strength_training", "hiit", "cardio", "calisthenics", "mobility_flexibility"})
        ]
    elif user["goal"] == "other":
        filtered_exercises = [
            ex for ex in filtered_exercises
            if style_matches(ex["style"], {"strength_training", "hiit", "cardio", "calisthenics", "mobility_flexibility"})
        ]
    
    # by experience_level
    if user["experience_level"] == "beginner":
        filtered_exercises = [ex for ex in filtered_exercises if ex["difficulty"] in ["beginner"]]
    elif user["experience_level"] == "intermediate":
        filtered_exercises = [ex for ex in filtered_exercises if ex["difficulty"] in ["beginner", "intermediate"]]
    elif user["experience_level"] == "advanced":
        filtered_exercises = [ex for ex in filtered_exercises if ex["difficulty"] in ["beginner", "intermediate", "advanced"]]

    # by preferred training style
    # if user["preferred_training_style"] == "strength_training":
    #     filtered_exercises = [ex for ex in filtered_exercises if style_matches(ex["style"], {"strength_training"})]
    # elif user["preferred_training_style"] == "cardio":
    #     filtered_exercises = [ex for ex in filtered_exercises if style_matches(ex["style"], {"cardio"})]
    # elif user["preferred_training_style"] == "hiit":
    #     filtered_exercises = [ex for ex in filtered_exercises if style_matches(ex["style"], {"hiit"})]
    # elif user["preferred_training_style"] == "crossfit":
    #     filtered_exercises = [ex for ex in filtered_exercises if style_matches(ex["style"], {"crossfit"})]
    # elif user["preferred_training_style"] == "calisthenics":
    #     filtered_exercises = [ex for ex in filtered_exercises if style_matches(ex["style"], {"calisthenics"})]
    # elif user["preferred_training_style"] == "mobility_flexibility":
    #     filtered_exercises = [ex for ex in filtered_exercises if style_matches(ex["style"], {"mobility_flexibility"})]

    return filtered_exercises

PLAN_TEMPLATES = {
    "full_body": [
        "squat",             
        "horizontal_push",   
        "horizontal_pull",   
        "hinge",             
        "core",              
    ],
    "upper_body": [
        "horizontal_push",   
        "horizontal_pull",   
        "vertical_push",     
        "vertical_pull",     
        "isolation_biceps",  
        "isolation_triceps"  
    ],
    "lower_body": [
        "squat",             
        "hinge",             
        "lunge",             
        "isolation_calves",  
        "core"              
    ],
    
    "glutes": [
        "hinge",             
        "squat",             
        "lunge",             
        "glute_isolation",   
        "glute_isolation"    
    ],
    "arms": [
        "isolation_biceps",  
        "isolation_triceps", 
        "isolation_biceps",  
        "isolation_triceps", 
        "isolation_forearms" 
    ],
    "legs": [
        "squat",             
        "hinge",             
        "lunge",             
        "isolation_quads",   
        "isolation_hamstrings", 
        "isolation_calves"   
    ],
    "back": [
        "vertical_pull",    
        "horizontal_pull",   
        "vertical_pull",     
        "horizontal_pull",   
        "isolation_lats"    
    ],
    "chest": [
        "horizontal_push",  
        "horizontal_push",   
        "isolation_chest",   
        "isolation_triceps"  
    ],
    "shoulders": [
        "vertical_push",       
        "isolation_shoulders", 
        "isolation_shoulders", 
        "isolation_upper_back" 
    ],
    "core": [
        "core", 
        "core", 
        "core", 
        "isolation_spine"    
    ]
}

def create_plan(user: dict, exercises: list) -> dict:
  
    all_allowed_exercises = filter_exercises(user, exercises)
    
    training_focus = user.get("training_focus", "full_body") 
    days = int(user.get("available_days_per_week", 3) or 3)
    max_duration = float(user.get("session_duration_max", 90) or 90)
    
    SPECIALIZED_PLANS = ["glutes", "arms", "chest", "back", "shoulders", "core", "legs"]
    DEFAULT_SPLIT = ["upper_body", "lower_body", "full_body"]
    
    templates_for_the_week = []

    focus_is_list = isinstance(training_focus, list) and training_focus

    if focus_is_list:

        if len(training_focus) == days:
            templates_for_the_week = training_focus
        
        elif len(training_focus) > days:
            templates_for_the_week = DEFAULT_SPLIT[:days] 
        
        else: # len(training_focus) < days
            templates_for_the_week = list(training_focus) 
            
            fill_index = 0
            while len(templates_for_the_week) < days:
                fill_to_add = DEFAULT_SPLIT[fill_index % len(DEFAULT_SPLIT)]
                if fill_to_add not in templates_for_the_week:
                    templates_for_the_week.append(fill_to_add)
                fill_index += 1
                if fill_index > 10: 
                    templates_for_the_week.append("full_body")
            
            templates_for_the_week = templates_for_the_week[:days]

    elif isinstance(training_focus, str):

        if training_focus not in SPECIALIZED_PLANS:
            templates_for_the_week = [training_focus] * days

        else:

            templates_for_the_week = [training_focus]
            
            fill_index = 0
            while len(templates_for_the_week) < days:
                fill_to_add = DEFAULT_SPLIT[fill_index % len(DEFAULT_SPLIT)]
                
                if (fill_to_add == "lower_body" and training_focus in ["glutes", "legs"]):
                    fill_index += 1
                    continue 
                    
                if fill_to_add not in templates_for_the_week:
                    templates_for_the_week.append(fill_to_add)
                fill_index += 1
                if fill_index > 10: 
                    templates_for_the_week.append("full_body")
            
            templates_for_the_week = templates_for_the_week[:days]
    
    else:
        templates_for_the_week = ["full_body"] * days
            
    final_plan_structure = [] 
    day_counter = 1

    for template_name in templates_for_the_week:
        
        template = PLAN_TEMPLATES.get(template_name) 
        if not template:
            raise HTTPException(
                status_code=500,
                detail=f"Critical error: Template not found for '{template_name}'. This indicates a configuration error."
            ) 
            
        daily_exercises = []
        daily_pool = list(all_allowed_exercises) 
        current_day_duration = 0.0

        for pattern in template:
            options = [ex for ex in daily_pool if ex.get("movement_pattern") == pattern]
            if not options:
                raise HTTPException(
                    status_code=422,
                    detail=f"No exercises found for movement pattern '{pattern}' on day {day_counter}. Please adjust your preferences (equipment, location, difficulty) or training focus."
                )

            random.shuffle(options)
            
            chosen_exercise = None
            for ex in options:
                if ex.get("duration") is None:
                    ex["duration"] = estimate_exercise_time(ex)
                
                ex_duration = float(ex["duration"])
                
                if current_day_duration + ex_duration <= max_duration:
                    chosen_exercise = ex
                    break 
            
            if chosen_exercise:
                daily_exercises.append(chosen_exercise)
                daily_pool.remove(chosen_exercise) 
                current_day_duration += float(chosen_exercise["duration"])
            else:
                pass
            
        if not daily_exercises:
            raise HTTPException(
                status_code=422,
                detail=f"No exercises could be added for day {day_counter} (focus: {template_name}). This may be due to time constraints or lack of available exercises. Please adjust session_duration_max or training preferences."
            )
        
        plan_day = {
            "day": day_counter,
            "focus": template_name, 
            "estimated_duration_minutes": round(current_day_duration, 1),
            "exercises": [
                {
                    "exercise": ex["exercise_name"], 
                    "sets": ex["default_sets"],
                    "reps": ex["default_reps"],
                    "unit": ex["duration_unit"] 
                } for ex in daily_exercises
            ]
        }
        final_plan_structure.append(plan_day)
        day_counter += 1

    if not final_plan_structure:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate any training days. This indicates a critical error in plan generation."
        )

    return {"weeks": 4, "plan": final_plan_structure}

def load_exercises(dataset_path: str = 'exercises_dataset.csv') -> list:
    exercises = []

    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')

            for row in reader:
                row["duration"] = estimate_exercise_time(row)
                exercises.append(row)
                
    except FileNotFoundError as e:
        print(f"ERROR: Dataset file not found: {dataset_path}")
        print("Make sure the CSV file is in the same folder as generator.py")
        raise RuntimeError(f"Exercises dataset not found at {dataset_path}") from e

    except Exception as e:
        print(f"ERROR: Failed to load exercises file: {e}")
        raise RuntimeError(f"Failed to load exercises dataset: {e}") from e
    
    print(f"Loaded {len(exercises)} exercises from {dataset_path}")
    return exercises


EXERCISES_DATA = load_exercises()


def generate_plan(user_profile: dict):
    start_time = time.perf_counter()
    plan = create_plan(user_profile, EXERCISES_DATA)
    elapsed_seconds = time.perf_counter() - start_time
    return plan, elapsed_seconds

def build_prompt(plan: dict) -> str:
    return f"""
    You are a certified strength and conditioning coach (CSCS). Your task is to analyze the following training plan JSON and present it to the user in a clear, motivational, and safe manner.

    INPUT PLAN (JSON):
    {json.dumps(plan, ensure_ascii=False, indent=2)}

    YOUR TASKS:
    1.  **PLAN ACCURACY:** Stick to the plan exactly. Do not change exercise names, sets, or rep counts.
    2.  **INTERPRET UNITS:** Correctly read the new "unit" column.
        * If "unit" is "reps", write "reps".
        * If "unit" is "seconds", write "seconds".
        * If "unit" is "minutes", write "minutes".
    3.  **SESSION DURATION:** Acknowledge the estimated duration for the day (e.g., "Estimated time: 65 minutes").
    4.  **ADD VALUE (TIPS):** For *each* exercise, add a brief, one-sentence "Coach's Tip". This should be the single most important cue to remember (e.g., "Keep your back straight," "Control the movement on the way down," "Look straight ahead").
    5.  **EXTRAS:** Suggest a brief (3-5 min) warm-up and cool-down.
    6.  **REST:** Explain our rest rule in the "Final Tips" section.

    TONE:
    -   Supportive, expert, motivational. Be like the best trainer in the gym—specific and encouraging.

    OUTPUT FORMAT (Markdown):
    ------------------------------------------------
    ## Your New Training Plan!

    Hello! Here is your personalized training plan for the week, designed to help you reach your goal. Let's get started!

    ---

    ### Day 1 — Focus: [Focus from JSON] 

    **1.[Exercise Name] — [X] sets × [Y] [unit]**
        *Coach's Tip: [Your one-sentence tip for this specific exercise]*
    **2.[Exercise Name 2] — [X] sets × [Y] [unit]**
        *Coach's Tip: [Your one-sentence tip for this specific exercise]*
    **3. ... (etc.)**

    ---

    ### Day 2 — Focus: [Focus from JSON]

    1. [Exercise Name] — [X] sets × [Y] [unit]
        *Coach's Tip: [Your one-sentence tip for this ex.]*
    2. ... (etc.)

    ---

    (Repeat for all days in the plan)

    ---

    ### Final Coach's Tips

    **Warm-up Suggestion (3-5 minutes):**
    * [Suggest 2-3 dynamic drills, e.g., arm circles, high knees, jumping jacks, or light core activation]

    **Cool-down Suggestion (3-5 minutes):**
    * [Suggest 2-3 static stretches for the main muscle groups worked in the plan, e.g., chest, quad, back stretches]

    **Rest Between Sets:**
    * For strength exercises (those with "reps"), rest for approximately **60 seconds** between each set to maintain intensity. For timed exercises ("seconds" or "minutes"), focus on completing the task as prescribed.

    **Scaling (Adjustments):**
    * **To make it easier:** If an exercise feels too difficult, reduce the number of reps or use a lighter weight.
    * **To make it harder:** If it feels too easy, try to slightly increase the weight or focus on a slower, more controlled movement.

    Remember, consistency and proper form are the keys to success. Listen to your body. You've got this!
    ------------------------------------------------
    """

def ask_groq(prompt):
    start_time = time.perf_counter()

    api_url = "https://api.groq.com/openai/v1/chat/completions"
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set in environment.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 3000,
        "temperature": 0.7,
        "top_p": 0.9,
        "stream": False,
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=90)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_error:
        status_code = http_error.response.status_code if http_error.response else 502
        detail = http_error.response.text if http_error.response else str(http_error)
        raise HTTPException(status_code=status_code, detail=f"Groq API HTTP error: {detail}") from http_error
    except requests.exceptions.Timeout as timeout_error:
        raise HTTPException(status_code=504, detail="Groq API request timed out.") from timeout_error
    except requests.exceptions.RequestException as request_error:
        raise HTTPException(status_code=502, detail=f"Failed to reach Groq API: {request_error}") from request_error

    data = response.json()
    text = data.get("choices", [{}])[0].get("message", {}).get("content", "") or ""
    elapsed_seconds = time.perf_counter() - start_time

    return text, elapsed_seconds

def validate_user_profile(user_profile: dict):
    required_fields = [
        "training_location",
        "goal",
        "experience_level",
        "training_focus",
        "available_days_per_week",
    ]
    missing = [field for field in required_fields if field not in user_profile]
    if missing:
        raise HTTPException(status_code=422, detail=f"Missing required fields: {', '.join(missing)}")
    return user_profile


@app.post("/generate_plan")
async def generate_plan_endpoint(user: dict):
    if not isinstance(user, dict):
        raise HTTPException(status_code=400, detail="Invalid user profile payload.")

    print("Generating plan...")
    try:
        user_profile = validate_user_profile(user)
        plan, elapsed_seconds_plan = generate_plan(user_profile)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate plan: {e}") from e

    prompt = build_prompt(plan)
    llm_text, elapsed_seconds_llm = ask_groq(prompt)
    seconds_total = elapsed_seconds_plan + elapsed_seconds_llm
    print(f"Plan creation finished in {seconds_total:.2f}s.")
    print(llm_text)

    return {
        "plan": plan,
        "llm_response": llm_text,
    }
