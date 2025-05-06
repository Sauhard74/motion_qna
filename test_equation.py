import sys
sys.path.append('.')
from app.services.ai_service import AIService

# Test our equation solver directly
ai = AIService()
print("Testing equation solver")
result = ai._solve_basic_equation('Solve for x: x + 9 = 34')
print("Result:", result)

# Try another format
result2 = ai._solve_basic_equation('find x : x + 9 = 34')
print("Result2:", result2) 