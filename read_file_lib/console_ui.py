# Handle file in Python - demo
# By Tomasz Gołaszewski
# 2025.04.14

from . import file_handling

ALLOWED_CURRENCES = ["PLN", "USD", "EUR"]

class QuestionBase:
    def __init__(self, kw={}):
        """Initialization of the question."""
        self.next = self # unless changed, next question is this question
        self.kw = kw # some context to pass between questions
    
    def process_question(self):
        """Handle all logic for current question.
        Overwrite to build new question.
        """
        raise RuntimeError("It is required that the derived class provides an implementation of the process question.")

    def switch_scene(self, next_scene):
        """Set next scene object."""
        self.next = next_scene
    
    def terminate(self):
        """Closes questions sequence by seting next question to None."""
        self.switch_scene(None)

# ===== FILE ==========================================

class StartQuestion(QuestionBase):
    def process_question(self):
        question = """Hello in my demo program :)
Enter the file name with extension (enter "exit" to exit, leave empty to use demo.txt):
>>>"""
        answer = input(question)
        if answer == "exit": 
            self.terminate()
        else: 
            if not answer: 
                answer = "demo.txt"
            file_handling.FileWithConstantWidth(answer) # checks if does file exist, create if it doesn't
            self.switch_scene(ChooseFunctionQuestion({'path': answer}))

# ===== FUNCTION ==========================================

class ChooseFunctionQuestion(QuestionBase):
    def process_question(self):
        question = """Do you want:
* get value - enter: "get",
* add transaction - enter: "add",
* update value - enter: "update",
* exit - enter: "exit"
>>>"""
        answer = input(question)
        self.kw.update({"function": answer})
        if answer == "exit": 
            self.terminate()
        elif answer in ["get"]: 
            self.switch_scene(GetValueQuestionBlock(self.kw))
        elif answer in ["add"]: 
            self.switch_scene(AddTransactionQuestionAmount(self.kw))
        elif answer in ["update"]: 
            self.switch_scene(UpdateValueQuestionField(self.kw))
        else:
            print("Invalid command!")

# ===== GET VALUE ==========================================        

class GetValueQuestionBlock(QuestionBase):
    def process_question(self):
        question = """Which block are you intrested in?
* header,
* transaction,
* footer?
>>>"""
        answer = input(question)
        self.kw.update({"block": answer})
        if answer == "exit": 
            self.terminate()
        elif answer in ["header", "footer"]: 
            self.switch_scene(GetValueQuestionField(self.kw))
        elif answer == "transaction": 
            self.switch_scene(GetValueQuestionTransaction(self.kw))
        else:
            print("Invalid block name!")

class GetValueQuestionTransaction(QuestionBase):
    def process_question(self):
        question = """Which transaction number (int type)?
>>>"""
        answer = input(question)
        if answer == "exit": 
            self.terminate()
        elif answer.isnumeric(): 
            self.kw.update({"transaction_no": int(answer)})
            self.switch_scene(GetValueQuestionField(self.kw))
        else:
            print("Enter number!")
                              
class GetValueQuestionField(QuestionBase):
    def process_question(self):
        path = self.kw.get("path")
        file = file_handling.FileWithConstantWidth(path)
        block = self.kw.get("block")
        fields_list = getattr(file, block).fields_list
        question = f"""Which field do you want to see {fields_list}?
>>>"""
        field = input(question)
        if field == "exit": 
            self.terminate()
        elif field in fields_list:
            transaction_no = self.kw.get("transaction_no")
            print("\nAnswer from file => ", file.get_value(block, field, transaction_no), "\n")
            self.switch_scene(StartQuestion({}))
        else:
            print("Invalid field name!")

# ===== ADD TRANSACTION ========================================== 

class AddTransactionQuestionAmount(QuestionBase):
    def process_question(self):
        question = """Enter value (float type)?
>>>"""
        answer = input(question)
        if answer == "exit": 
            self.terminate()
        else: 
            self.kw.update({"amount": answer})
            self.switch_scene(AddTransactionQuestionCurrency(self.kw))

class AddTransactionQuestionCurrency(QuestionBase):
    def process_question(self):
        question = f"""Enter currency {ALLOWED_CURRENCES}?
>>>"""
        currency = input(question)
        if currency == "exit": 
            self.terminate()
        elif currency in ALLOWED_CURRENCES:
            path = self.kw.get("path")
            amount = float(self.kw.get("amount"))
            file = file_handling.FileWithConstantWidth(path)
            print(file.add_transaction(amount, currency))
            self.switch_scene(StartQuestion({}))
        else:
            print("Invalid currency!")

# ===== UPDATE VALUE ========================================== 

class UpdateValueQuestionField(QuestionBase):
    def process_question(self):
        path = self.kw.get("path")
        file = file_handling.FileWithConstantWidth(path)
        fields_list = getattr(file, 'header').fields_list
        question = f"""Which field do you want to update {fields_list}?
>>>"""
        field = input(question)
        if field == "exit": 
            self.terminate()
        elif field in fields_list:
            self.kw.update({"field": field})
            self.switch_scene(UpdateValueQuestionValue(self.kw))
        else:
            print("Invalid field name!")

class UpdateValueQuestionValue(QuestionBase):
    def process_question(self):
        question = """Enter value:
>>>"""
        value = input(question)
        if value == "exit": 
            self.terminate()
        else:
            path = self.kw.get("path")
            field = self.kw.get("field")
            file = file_handling.FileWithConstantWidth(path)
            print(file.insert_value("header", field, value))
            self.switch_scene(StartQuestion({}))

# ===== MAIN PROGRAM ==========================================

def main_program():
    """
    Executes the main program logic by processing a sequence of questions.

    This function starts with an initial question and iteratively processes 
    each question while transitioning to the next one. The loop continues until 
    there are no more questions to handle.
    """
    active_question = StartQuestion()

    # main loop
    while active_question != None:
        # handling question
        active_question.process_question()
        
        # jump to next scene (or to self)
        active_question = active_question.next