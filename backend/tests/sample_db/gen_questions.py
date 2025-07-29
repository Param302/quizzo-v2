from datetime import datetime, timedelta
import json
import random

# Helper functions (redefined for fresh session)
def generate_mcq(question_text, options, correct_index):
    return {
        "question_statement": question_text,
        "question_type": "MCQ",
        "options": options,
        "correct_answer": [correct_index],
        "marks": 1.0
    }

def generate_msq(question_text, options, correct_indices):
    return {
        "question_statement": question_text,
        "question_type": "MSQ",
        "options": options,
        "correct_answer": correct_indices,
        "marks": 1.0
    }

def generate_nat(question_text, answer):
    return {
        "question_statement": question_text,
        "question_type": "NAT",
        "options": None,
        "correct_answer": answer,
        "marks": 1.0
    }

def generate_quizzes(questions):
    quizzes = []
    today = datetime.now()
    for i in range(3):
        quizzes.append({
            "title": f"Upcoming Quiz {i+1}",
            "date_of_quiz": (today + timedelta(days=i+1)).isoformat(),
            "time_duration": "00:30",
            "is_scheduled": True,
            "remarks": "",
            "questions": random.sample(questions, 5)
        })
    quizzes.append({
        "title": "General Quiz",
        "date_of_quiz": None,
        "time_duration": "00:30",
        "is_scheduled": False,
        "remarks": "",
        "questions": random.sample(questions, 5)
    })
    quizzes.append({
        "title": "Past Quiz",
        "date_of_quiz": (today - timedelta(days=5)).isoformat(),
        "time_duration": "00:30",
        "is_scheduled": True,
        "remarks": "",
        "questions": random.sample(questions, 5)
    })
    return quizzes

# Define Generative AI course
genai_course = {
    "name": "Generative AI",
    "description": "A beginner-friendly course introducing concepts and technologies behind Generative AI systems.",
    "chapters": []
}

# Questions per chapter
chapters_data = {
    "Intro to GenAI": [
        generate_mcq("What does Generative AI primarily focus on?", ["Data analysis", "Data generation", "Data storage", "Data cleaning"], 1),
        generate_nat("Year GPT-2 was released?", 2019),
        generate_mcq("Which model is an example of Generative AI?", ["ResNet", "BERT", "GPT-3", "VGG"], 2),
        generate_msq("Applications of Generative AI include:", ["Image generation", "Text summarization", "Sorting", "Music composition"], [0,1,3]),
        generate_mcq("Which company developed DALL·E?", ["Google", "OpenAI", "Meta", "NVIDIA"], 1),
    ],
    "Models": [
        generate_mcq("GAN stands for:", ["General AI Network", "Generative Adversarial Network", "Generative Average Net", "Gradient AI Network"], 1),
        generate_nat("How many networks are involved in a GAN?", 2),
        generate_mcq("Which is NOT a generative model?", ["GPT", "VAE", "GAN", "ResNet"], 3),
        generate_msq("Which are types of generative models?", ["GAN", "VAE", "CNN", "Transformer"], [0,1,3]),
        generate_mcq("Autoencoders are primarily used for:", ["Classification", "Data generation", "Regression", "Clustering"], 1),
    ],
    "LLMs": [
        generate_mcq("LLM stands for?", ["Large Learning Module", "Long Language Model", "Large Language Model", "Light Language Machine"], 2),
        generate_mcq("Which of these is an LLM?", ["T5", "ResNet", "YOLO", "MobileNet"], 0),
        generate_msq("Capabilities of LLMs include:", ["Summarization", "Translation", "Image Segmentation", "Q&A"], [0,1,3]),
        generate_nat("GPT-4 has context length up to?", 128000),
        generate_mcq("Which transformer component is key for LLMs?", ["Convolution", "Attention", "Pooling", "Recurrence"], 1),
    ],
    "MCP": [
        generate_mcq("What does MCP stand for in GenAI context?", ["Model Configuration Pipeline", "Multi-Component Prompting", "Multi-Choice Processor", "Massive Chatbot Protocol"], 1),
        generate_msq("Prompt engineering techniques include:", ["Few-shot", "Zero-shot", "Chain-of-thought", "Reinforcement Learning"], [0,1,2]),
        generate_mcq("Chain-of-thought prompting improves:", ["Response time", "Accuracy", "Multilingual output", "Memory"], 1),
        generate_nat("Typical token limit in GPT-3.5?", 4096),
        generate_mcq("What is zero-shot prompting?", ["No examples provided", "One example provided", "Multiple examples", "Requires fine-tuning"], 0),
    ],
    "Agents": [
        generate_mcq("Agents in AI are systems that:", ["Only store data", "Act autonomously", "Only predict values", "Only visualize graphs"], 1),
        generate_mcq("Which is a popular agent framework?", ["AutoGPT", "CNN", "GAN", "Pandas"], 0),
        generate_nat("If an agent solves 4 tasks with 80% accuracy, expected correct = ?", 3.2),
        generate_msq("Agent features may include:", ["Planning", "Tool usage", "Static response", "Memory"], [0,1,3]),
        generate_mcq("What is LangChain used for?", ["Data storage", "Model training", "Agent orchestration", "Web scraping"], 2),
    ]
}

# Add chapters with quizzes
for chapter_name, questions in chapters_data.items():
    genai_course["chapters"].append({
        "name": chapter_name,
        "description": f"This chapter covers {chapter_name.lower()} in the Generative AI domain.",
        "quizzes": generate_quizzes(questions)
    })

# Final JSON structure
genai_json = {
    "courses": [genai_course]
}

# Save to file
file_path = "tests/sample_db/data/generative_ai_course.json"
with open(file_path, "w") as f:
    json.dump(genai_json, f, indent=2)

file_path
