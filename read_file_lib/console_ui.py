# Handle file in Python - demo
# By Tomasz Gołaszewski
# 2025.04.14

from . import file_handling


class QuestionBase:
    def __init__(self, kw={}):
    # initialization of the scene
        self.next = self
        self.kw = kw # some context to pass between questions
    
    def process_question(self):
    # handle all received events
    # question logic for the scene
        print("not overwritten process_question")

    def switch_scene(self, next_scene):
    # change scene
        self.next = next_scene
    
    def terminate(self):
    # close the game by changing scene tu None
        self.switch_scene(None)

# ===== FILE ==========================================

class StartQuestion(QuestionBase):
    def process_question(self):
        question = """Hello in my demo program :)
Enter the file name with extension (enter "exit" to exit):
>>>"""
        answer = input(question)
        if answer == "exit": self.terminate()
        else: 
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
                              
class GetValueQuestionField(QuestionBase):
    def process_question(self):
        question = """Which field do you want to see?
>>>"""
        field = input(question)
        if field == "exit": 
            self.terminate()
        else:
            block = self.kw.get("block")
            transaction_no = self.kw.get("transaction_no")
            path = self.kw.get("path")
            file = file_handling.FileWithConstantWidth(path)
            print("\nAnswer from file => ", file.get_value(block, field, transaction_no), "\n")
            self.switch_scene(StartQuestion({}))

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
        question = """Enter currency (PLN, USD, EUR)?
>>>"""
        currency = input(question)
        if currency == "exit": 
            self.terminate()
        elif currency in ["PLN", "USD", "EUR"]:
            path = self.kw.get("path")
            amount = float(self.kw.get("amount"))
            file = file_handling.FileWithConstantWidth(path)
            result = file.add_transaction(amount, currency)
            if result: print(result)
            else: print("DONE!")
            self.switch_scene(StartQuestion({}))

# ===== UPDATE VALUE ========================================== 

class UpdateValueQuestionField(QuestionBase):
    def process_question(self):
        question = """Which field do you want to update?
>>>"""
        field = input(question)
        if field == "exit": 
            self.terminate()
        else:
            self.kw.update({"field": field})
            self.switch_scene(UpdateValueQuestionValue(self.kw))

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
            result = file.insert_value("header", field, value)
            if result: print(result)
            else: print("DONE!")
            self.switch_scene(StartQuestion({}))

# ===== MAIN PROGRAM ==========================================

def main_program():
    active_question = StartQuestion()

    # main loop
    while active_question != None:
        # handling question
        active_question.process_question()
        
        # jump to next scene (or to self)
        active_question = active_question.next