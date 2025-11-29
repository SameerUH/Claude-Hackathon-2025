import json
import random
from datetime import datetime, timedelta

def generate_student_data(num_students=5):
    """Generate fake student data for testing"""
    
    subjects = ["Computer Science", "Mathematics", "Physics", "Engineering", "Business"]
    modules = {
        "Computer Science": ["Programming", "Data Structures", "Algorithms", "Databases", "Web Development"],
        "Mathematics": ["Calculus", "Linear Algebra", "Statistics", "Discrete Math", "Analysis"],
        "Physics": ["Mechanics", "Electromagnetism", "Quantum Physics", "Thermodynamics", "Optics"],
        "Engineering": ["Mechanics", "Circuits", "Materials", "Design", "Systems"],
        "Business": ["Accounting", "Marketing", "Finance", "Management", "Economics"]
    }
    
    skills_map = {
        "Programming": ["Problem Solving", "Logical Thinking", "Debugging", "Code Optimization"],
        "Data Structures": ["Analytical Thinking", "Memory Management", "Algorithm Design"],
        "Algorithms": ["Problem Solving", "Optimization", "Complexity Analysis"],
        "Databases": ["Data Modeling", "Query Optimization", "System Design"],
        "Web Development": ["Frontend Skills", "Backend Skills", "User Experience Design"],
        "Calculus": ["Analytical Thinking", "Mathematical Modeling", "Problem Solving"],
        "Linear Algebra": ["Abstract Thinking", "Pattern Recognition", "Problem Solving"],
        "Statistics": ["Data Analysis", "Critical Thinking", "Probability Reasoning"],
        "Mechanics": ["Physics Principles", "Problem Solving", "Mathematical Modeling"],
        "Accounting": ["Attention to Detail", "Financial Analysis", "Numerical Accuracy"],
        "Marketing": ["Communication", "Creative Thinking", "Market Research"],
        "Finance": ["Financial Analysis", "Risk Assessment", "Quantitative Reasoning"]
    }
    
    behaviors = ["Consistent", "Improving", "Declining", "Irregular", "Excellent"]
    
    students = []
    
    for i in range(num_students):
        student_id = f"STU{1000 + i}"
        name = f"Student_{i+1}"
        subject = random.choice(subjects)
        year = random.randint(1, 3)
        
        # Generate grades for modules
        student_modules = random.sample(modules[subject], k=random.randint(3, 5))
        grades = {}
        transferrable_skills = []
        
        for module in student_modules:
            grade = random.randint(40, 95)
            grades[module] = grade
            
            # Add skills based on modules taken
            if module in skills_map:
                transferrable_skills.extend(skills_map[module])
        
        # Remove duplicate skills and add proficiency levels
        unique_skills = list(set(transferrable_skills))
        skills_with_proficiency = {}
        for skill in unique_skills:
            # Proficiency correlates somewhat with grades
            avg_grade = sum(grades.values()) / len(grades)
            base_proficiency = (avg_grade - 40) / 55  # Normalize to 0-1
            proficiency = min(100, int((base_proficiency + random.uniform(-0.1, 0.1)) * 100))
            skills_with_proficiency[skill] = proficiency
        
        # Generate behavior pattern
        behavior = random.choice(behaviors)
        
        # Generate engagement metrics
        engagement = {
            "attendance_rate": random.randint(60, 100),
            "assignment_submission_rate": random.randint(70, 100),
            "participation_score": random.randint(50, 100),
            "last_login": (datetime.now() - timedelta(days=random.randint(0, 7))).isoformat()
        }
        
        student = {
            "student_id": student_id,
            "name": name,
            "subject": subject,
            "year": year,
            "grades": grades,
            "average_grade": round(sum(grades.values()) / len(grades), 2),
            "transferrable_skills": skills_with_proficiency,
            "behavior_pattern": behavior,
            "engagement": engagement
        }
        
        students.append(student)
    
    return students

def save_student_data(students, filename="student_data.json"):
    """Save student data to JSON file"""
    with open(filename, 'w') as f:
        json.dump(students, f, indent=2)
    print(f"Generated data for {len(students)} students and saved to {filename}")

if __name__ == "__main__":
    # Generate data for 5 students
    students = generate_student_data(5)
    save_student_data(students)
    
    # Display summary
    print("\nGenerated Students:")
    for student in students:
        print(f"- {student['name']} ({student['student_id']}): {student['subject']}, Year {student['year']}, Avg: {student['average_grade']}%")