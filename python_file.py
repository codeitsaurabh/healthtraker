import mysql.connector
from datetime import datetime, timedelta
import getpass

# Database connection setup
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="fitness_tracker"
)
cursor = db.cursor()


# User login and registration
def register_user():
    username = input("Enter a new username: ")
    password = getpass.getpass("Enter a new password: ")
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    db.commit()
    print("Registration successful!")

def login_user():
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")
    cursor.execute("SELECT user_id, last_login FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    if user:
        user_id, last_login = user
        today = datetime.today().date()
        if last_login is None or last_login < today:
            daily_notification(user_id)
            cursor.execute("UPDATE users SET last_login = %s WHERE user_id = %s", (today, user_id))
            db.commit()
        print("Login successful!")
        print("Welcome",username)
        return user_id
    else:
        print("Invalid credentials")
        return None

# Daily notification
def daily_notification(user_id):
    print("\n--- Daily Notification ---")
    print("Remember to log your exercise, meals, and water intake!")
    print("--------------------------\n")

# Meal suggestions based on calorie target
def set_daily_calorie_target(user_id):
    calorie_target = float(input("Enter your daily calorie target: "))
    cursor.execute("INSERT INTO calorie_intake (user_id, date, meal, calories) VALUES (%s, %s, %s, %s)", (user_id, datetime.today().date(), 'Target', calorie_target))
    db.commit()
    print("Daily calorie target set!")

def suggest_meals(user_id):
    cursor.execute("SELECT calories FROM calorie_intake WHERE user_id = %s AND date = %s AND meal = 'Target'", (user_id, datetime.today().date()))
    target = cursor.fetchone()
    if target:
        calorie_target = target[0]
        cursor.execute("SELECT meal_name, calories FROM meals WHERE calories <= %s", (calorie_target,))
        meals = cursor.fetchall()
        print(f"\nMeal Suggestions for a Target of {calorie_target} Calories:")
        for meal in meals:
            print(f"- {meal[0]}: {meal[1]} calories")
    else:
        print("Please set a daily calorie target first.")

# Streaks and achievements
def update_streak(user_id):
    today = datetime.today().date()
    
    
    cursor.execute("SELECT last_logged_date, streak_count FROM streaks WHERE user_id = %s", (user_id,))
    streak = cursor.fetchone()
    
    if streak:
        last_logged_date, streak_count = streak
        
        
        if last_logged_date == today - timedelta(days=1):
            streak_count += 1  
        elif last_logged_date < today - timedelta(days=1):
            streak_count = 1  
        else:
            return

        
        cursor.execute("UPDATE streaks SET last_logged_date = %s, streak_count = %s WHERE user_id = %s",
                       (today, streak_count, user_id))
        
    else:
        
        streak_count = 1
        cursor.execute("INSERT INTO streaks (user_id, last_logged_date, streak_count) VALUES (%s, %s, %s)",
                       (user_id, today, streak_count))

    
    if streak_count >= 7:
        cursor.execute("INSERT INTO user_achievements (user_id, achievement, date_awarded) VALUES (%s, %s, %s)",
                       (user_id, '1-Week Streak Achieved!', today))
        print("Congratulations! You've achieved a 1-week streak!")
    
    db.commit()

# Exercise and nutrition recommendations
def recommend_exercise(user_goal):
    cursor.execute("SELECT exercise_name, duration, calories_burned FROM exercise_recommendations WHERE category = %s", (user_goal,))
    exercises = cursor.fetchall()
    print(f"\nExercise Recommendations for {user_goal}:")
    for exercise in exercises:
        print(f"- {exercise[0]}: {exercise[1]} mins, burns {exercise[2]} calories")

def recommend_nutrition(user_goal):
    cursor.execute("SELECT nutrition_tip FROM nutrition_recommendations WHERE category = %s", (user_goal,))
    tips = cursor.fetchall()
    print(f"\nNutrition Tips for {user_goal}:")
    for tip in tips:
        print(f"- {tip[0]}")

# Log user’s weight
def log_weight(user_id):
    date = datetime.today().date()
    weight = float(input("Enter your weight in kg: "))
    cursor.execute("INSERT INTO weight_logs (user_id, date, weight) VALUES (%s, %s, %s)", (user_id, date, weight))
    db.commit()
    print("Weight logged successfully.")

# Log user’s water intake
def log_water_intake(user_id):
    date = datetime.today().date()
    liters = float(input("Enter daily water intake in liters: "))
    cursor.execute("INSERT INTO water_intake (user_id, date, liters) VALUES (%s, %s, %s)", (user_id, date, liters))
    db.commit()
    print("Water intake logged successfully.")

# Log user’s exercise
def log_exercise(user_id):
    date = datetime.today().date()
    exercise = input("Enter the type of exercise: ")
    duration = int(input("Enter duration in minutes: "))
    calories_burned = float(input("Enter estimated calories burned: "))
    cursor.execute("INSERT INTO exercise_logs (user_id, date, exercise, duration, calories_burned) VALUES (%s, %s, %s, %s, %s)", (user_id, date, exercise, duration, calories_burned))
    db.commit()
    print("Exercise logged successfully.")

# Log user’s calorie intake
def log_calorie_intake(user_id):
    date = datetime.today().date()
    meal = input("Enter meal name: ")
    calories = float(input("Enter calories consumed: "))
    cursor.execute("INSERT INTO calorie_intake (user_id, date, meal, calories) VALUES (%s, %s, %s, %s)", (user_id, date, meal, calories))
    db.commit()
    print("Calorie intake logged successfully.")


# Main program loop
def main():
    print("Welcome to Health and Fitness Tracker!")
    choice = input("Do you have an account? (yes/no): ")
    user_id = None
    if choice.lower() == "yes":
        user_id = login_user()
    else:
        register_user()
        user_id = login_user()
    if user_id:
        while True:
            print("\n1. Log Weight")
            print("2. Log Water Intake")
            print("3. Log Exercise")
            print("4. Log Calorie Intake")
            print("5. Set Daily Calorie Target")
            print("6. Suggest Meals")
            print("7. View Exercise Recommendations")
            print("8. View Nutrition Tips")
            print("9. Exit")
            option = input("Choose an option: ")
            if option == '1':
                log_weight(user_id)
                update_streak(user_id)
            elif option == '2':
                log_water_intake(user_id)
                update_streak(user_id)
            elif option == '3':
                log_exercise(user_id)
                update_streak(user_id)
            elif option == '4':
                log_calorie_intake(user_id)
                update_streak(user_id)
            elif option == '5':
                set_daily_calorie_target(user_id)
            elif option == '6':
                suggest_meals(user_id)
            elif option == '7':
                recommend_exercise('Weight Loss')
            elif option == '8':
                recommend_nutrition('Weight Loss')
            elif option == '9':
                break
            else:
                print("Invalid option. Try again.")

main()
