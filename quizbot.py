import json
import random
import os
import requests
from selenium import webdriver



class Quizzer:
    def __init__(self):
        self.url1 = "https://opentdb.com/api.php"
        self.url2 = "https://quizapi.io/api/v1/questions"
        self.API_KEY = "oy1unagWWoNHBglsdVLYeGfx5VO3KUX4Fvj8eiep"
        self.difficulty = random.choice(['easy', 'medium', 'hard'])
        self.category1 = {
            'gk': 9, 'cs': 18, 'maths': 19, 'games': 15, 'nature': 17
        }
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        execpath = os.environ.get("CHROMEDRIVER_PATH")
        self.driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
        self.quiz_func = random.choice([self.quizgetter1, self.quizgetter2])
        self.quiz_question = self.quiz_func()

    def quizgetter1(self):
        category = random.choice(['gk', 'cs', 'maths', 'games', 'nature'])
        category_id = self.category1[category]
        difficulty = self.difficulty
        qtype = random.choice(['boolean', 'multiple'])
        url = self.url1 + f'?amount=1&category={category_id}&difficulty={difficulty}&type={qtype}'
        response = requests.get(url).json()
        response = response["results"][0]
        if not response == []:
            question = response["question"]
            if question.__contains__('&#039;'):
                question = question.replace('&#039;', "\'")
            if question.__contains__('&quot;'):
                question = question.replace('&#039;', "\"")
            answer = response["correct_answer"]
            if answer.__contains__('&#039;'):
                answer = question.replace('&#039;', "\'")
            if qtype == 'boolean':
                options = ['True', 'False']
            else:
                options: list = response["incorrect_answers"]
                options.insert(random.randint(0, len(options) - 1), answer)
            return {"Question": question,
                    "CORRECT": answer,
                    "OPTIONS": options,
                    "MULTIPLE ANSWER": False}

    def quizgetter2(self):
        browser = self.driver
        browser.get(f"https://quizapi.io/api/v1/questions?apiKey={self.API_KEY}&limit=1")
        result = browser.find_element_by_tag_name('pre').text
        result_json = json.loads(result[1:len(result) - 1])
        question = result_json['question']
        options = list(result_json['answers'].values())
        multipleans = True if result_json['multiple_correct_answers'] == 'true' else False
        CORRECT = []
        a = result_json['correct_answers']
        for i in a.keys():
            if a[i] == 'true':
                CORRECT.append(result_json['answers'][i[:8]])
        if len(CORRECT) == 1:
            CORRECT = CORRECT[0]
        options = list(filter(lambda x: x is not None, options))
        quiz = {
            "Question": question,
            "CORRECT": CORRECT,
            "OPTIONS": options,
            "MULTIPLE ANSWER": multipleans

        }
        return quiz


