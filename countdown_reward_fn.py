import re
import random
import torch


def extract_solution(solution_str):
    """Extract the equation from the solution string."""
    # Remove everything before the first "Assistant:"
    if "Assistant:" in solution_str:
        solution_str = solution_str.split("Assistant:", 1)[1]
    elif "<|im_start|>assistant" in solution_str:
        solution_str = solution_str.split("<|im_start|>assistant", 1)[1]
    else:
        return None
    solution_str = solution_str.split('\n')[-1]

    answer_pattern = r'<answer>(.*?)</answer>'
    match = re.finditer(answer_pattern, solution_str)
    matches = list(match)
    if matches:
        final_answer = matches[-1].group(1).strip()
    else:
        final_answer = None
    return final_answer


def validate_equation(equation_str, available_numbers):
    """Validate that equation only uses available numbers and each number once."""
    try:
        # Extract all numbers from the equation
        numbers_in_eq = [int(n) for n in re.findall(r'\d+', equation_str)]
        
        # Check if all numbers in equation are available
        available_numbers = sorted(available_numbers)
        numbers_in_eq = sorted(numbers_in_eq)
        
        # Each number should be used exactly once
        return numbers_in_eq == available_numbers
    except:
        return False


def evaluate_equation(equation_str):
    """Safely evaluate the arithmetic equation using eval() with precautions."""
    try:
        # Define a regex pattern that only allows numbers, operators, parentheses, and whitespace
        allowed_pattern = r'^[\d+\-*/().\s]+$'
        if not re.match(allowed_pattern, equation_str):
            raise ValueError("Invalid characters in equation.")

        # Evaluate the equation with restricted globals and locals
        result = eval(equation_str, {"__builtins__": None}, {})
        return result
    except Exception:
        return None


def compute_score(solution_str, ground_truth, method='strict', format_score=0.1, score=1.):
    """The scoring function for countdown task.
    
    Args:
        solution_str: the solution text
        ground_truth: dictionary containing target number and available numbers
        method: the method to extract the solution
        format_score: the score for correct format but wrong answer
        score: the score for the correct answer
    """
    target = ground_truth['target']
    numbers = ground_truth['numbers']
    
    equation = extract_solution(solution_str=solution_str)
    do_print = random.randint(1, 256) == 1
    
    if do_print:
        print("--------------------------------")
        print(f"Target: {target} | Numbers: {numbers}")
        print(f"Extracted equation: {equation}")
        print(f"Solution string: {solution_str}")

    if equation is None:
        if do_print:
            print("No equation found")
        return 0
    
    # Validate equation uses correct numbers
    if not validate_equation(equation, numbers):
        if do_print:
            print("Invalid equation")
        return format_score
        
    # Evaluate equation
    try:
        result = evaluate_equation(equation)
        if result is None:
            if do_print:
                print("Could not evaluate equation")
            return format_score
            
        if abs(result - target) < 1e-5:  # Account for floating point precision
            if do_print:
                print(f"Correct equation: {equation} = {result}")
            return score
        else:
            if do_print:
                print(f"Wrong result: equation = {result}, target = {target}")
            return format_score
    except:
        if do_print:
            print("Error evaluating equation")
        return format_score 
    
def reward_func(queries, prompts, labels):
    # Compute the score
    return torch.Tensor([compute_score(solution_str=query, ground_truth=eval(label)) for query, label in zip(queries, labels)])

if __name__ == "__main__":
    solution_str = """<|im_start|>system\nYou are a helpful assistant. You first thinks about the reasoning process in the mind and then provides the user with the answer.<|im_end|>\n<|im_start
>user\n Using the numbers {numbers}, create an equation that equals {target}. You can use basic arithmetic operations (+, -, *, /) and each number can only be used once. Show your work in <think> </think> tags. And return the final answer in <answer> </answer> tags, for example <answer> (1 + 2) / 3 </answer>.<|im_end|>\n<|im_start|>assistant\nLet me solve this step by step.\n<think>
Okay, let's see. I need to use the numbers 34, 98, 1, and 96 each exactly once to make an equation that equals 33. Hmm. Let me start by thinking about possible operations and how they can combine these numbers.
First, maybe I should look for pairs that can subtract or divide to get closer to 33. Let's check subtraction first. The largest numbers here are 98 and 96. If I subtract them, 98 - 96 is 2. That's too small. But maybe combining that with others. Like 98 - 96 = 2, then maybe 34 - 1 = 33. Oh wait! But then I would have used 34 and 1, and 98 and 96. But that's all four numbers. Wait, how would that combine? So if I do (34 - 1) - (98 - 96), that would be 33 - 2 = 31, which is not 33. Hmm, no.
Alternatively, maybe 98 divided by something. Let's see. 98 divided by... Hmm, 98 divided by 34 is approximately 2.88. Then maybe subtract something. 98/34 ≈2.88, then subtract 1 would be around 1.88. Not helpful.
What if I use multiplication? 34 times 1 is 34. Then maybe subtract something. If I take 96 and 98, perhaps 98 - 96 = 2. So 34 * 1 - (98-96) = 34 -2 =32. Close but not 33.
Wait, maybe reverse the subtraction. 98 - (96/ something). Let's try 96 divided by a number. 96 divided by 1 is 96. Then 98 -96 = 2. Not helpful. 96 divided by 34 is roughly 2.82. Then 98 - (96/34) ≈98 -2.82 ≈95.18. No.
How about combining 34 and 98? 34 +98=132. Then maybe subtract something. 132 -96=36, then subtract 1 to get 35. Not 33. Alternatively, 132 - (96 +1)=132 -97=35. Still no.
Wait, maybe 96 divided by something else. 96 divided by (98-34) is 96/64=1.5. Then multiply by 1? Still 1.5. Not helpful.
Another approach: Let's see target is 33. Maybe 34 -1=33. Then need to use the other two numbers 98 and 96. But how? Because if I just have 34 -1=33, but then I need to somehow involve 98 and 96 in the equation. But since each number must be used once, perhaps the equation would need to have 98 and 96 somehow cancel out or result in 0. For example, 34 -1 + (98 -98), but that uses 98 twice. Wait, not allowed. Alternatively, 34 -1 + (96 -96), same problem. So that's not possible.
Alternatively, maybe use division where the other numbers cancel. For example, (98 -96) =2. Then maybe 34 - (2/1) =34 -2=32. Not 33. Or 34 - (1/(98-96))? That would be 34 - 0.5=33.5. Close, but not exact. And also, do we allow decimal points? The original numbers are integers, but using division could result in fractions. The problem says basic arithmetic operations, so fractions are allowed. Wait, 34 - (1/(98-96)) =34 - 0.5=33.5. Still not 33.
Hmm. Maybe multiplication and division. Let's see: 98 divided by something. 98 divided by (34/ something). Let's try 98/(34/1) = 98/34 ≈2.88. Then subtract 96? No. 98/(34/1) -96 is way negative. Not helpful.
What if I take 96 - (something). Let's see 96 - (98 -34) =96 -64=32. Then add 1: 32 +1=33. Wait, that works! Let me check: 96 - (98 -34) +1. Let's parse that: 98-34 is 64. 96-64=32. 32+1=33. Yes! And all numbers are used once: 96, 98,34,1. Each exactly once. So the equation is 96 - (98 -34) +1 =33. Let me verify the order of operations. Subtraction and addition are left to right, but parentheses first. So yes, 98-34=64. Then 96-64=32. Then 32+1=33. Correct.
</think>
<answer> 96 - (98 - 34) + 1 </answer>"""

    print(compute_score(solution_str=solution_str, ground_truth={'target': 33, 'numbers': [34, 98, 1, 96]}))