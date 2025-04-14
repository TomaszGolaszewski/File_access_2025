import logging


class FileWithConstantWidth():
    def __init__(self, path: str):
        self.path = path

        self.header = Line(1, [
            (1, 2, "Field ID", int), 
            (3, 30, "Name"), 
            (31, 60, "Surname"),
            (61, 90, "Patronymic"),
            (91, 120, "Address")
        ])
        self.transaction = Line(2, [
            (1, 2, "Field ID", int),
            (3, 8, "Counter", int),
            (9, 20, "Amount", int),
            (21, 23, "Currency"),
            (24, 120, "Reserved", False),
        ])
        self.footer = Line(3, [
            (1, 2, "Field ID", int),
            (3, 8, "Total Counter", int),
            (9, 20, "Control sum", int),
            (21, 120, "Reserved", False),
        ])
        print("File init")

        # print(self.insert_value("header", "Name", "Tomasz", 1))
        print(self.add_transaction(323.4567,  "PLN"))
        # print(self.get_value("transaction", "Amount", 3))
        try:
            with open(self.path, "r") as file:
                pass
        #         # for line in file:
        #         #     print(line)
        #         line = file.readline()
        #         print(self.header.get_field_value_from_line("Name", line))
        #         line = self.header.insert_field_value_to_line("Name", line, "Tomasz")
        #         print(self.header.get_field_value_from_line("Name", line))
        except FileNotFoundError:
            print("No file")
            self.create_empty_file()
        #     # with open(self.path, "w") as file:
        #     #     for i in range(5):
        #     #         file.write(str(i+1)*10 + "\n")

    def get_value(self, block: str, field: str, transaction_no=0):
        if not hasattr(self, block):
            raise NameError("Wrong block name!")
        block_id = getattr(self, block).id
        try:
            with open(self.path, "r") as file:
                for line in file:
                    if block_id == line[0:2] and self.transaction_check(block, line, transaction_no):
                        return getattr(self, block).get_field_value_from_line(field, line)
                return f"NO SUCH LINE {block}"
        except FileNotFoundError:
            return f"NO SUCH FILE {self.path}"
        
    def insert_value(self, block: str, field: str, value, transaction_no=0):
        if not hasattr(self, block):
            raise NameError("Wrong block name!")
            # return f"NO SUCH LINE {block}"
        if block == "transaction":
            # TODO: possible implementation of changes in transactions in the future
            return "YOU CAN'T CHANGE TRANSACTIONS' HISTORY!"
        if block == "footer":
            return "YOU CAN'T CHANGE FOOTER!"
        block_id = getattr(self, block).id
        new_file_content = ""
        try:
            with open(self.path, "r") as file:
                for line in file:
                    if block_id == line[0:2] and self.transaction_check(block, line, transaction_no):
                        new_file_content += getattr(self, block).insert_field_value_to_line(field, line, value)
                        # print(getattr(self, block).get_field_value_from_line(field, line))
                        # return f"VALUE {value} INSERTED :)"
                    else:
                        new_file_content += line
                # return f"NO SUCH LINE {block}"
        except FileNotFoundError:
            return f"NO SUCH FILE {self.path}"
        
        self.drop_payload_to_file(new_file_content)

    def add_transaction(self, amount_float: float, currency: str):
        if amount_float < 0:
            raise ValueError("Amount can't be negative!")
        if currency not in ["PLN", "EUR", "USD"]:
            raise ValueError("Wrong currency!")
        format_amount = lambda x: int(x * 100) # convert float into int with decimals
        amount = format_amount(amount_float)
        new_file_content = ""
        amount_sum = amount
        counter = 0
        try:
            with open(self.path, "r") as file:
                for line in file:
                    if line[0:2] == "01": # header
                        new_file_content += line # copy
                    elif line[0:2] == "02": # transactions
                        counter = self.transaction.get_field_value_from_line("Counter", line) # get counter
                        amount_sum += self.transaction.get_field_value_from_line("Amount", line) # sum total amount
                        new_file_content += line # copy
                    elif line[0:2] == "03": # footer - insert new transaction and create new footer
                        # add new transaction
                        new_line = self.transaction.create_empty_line()
                        new_line = self.transaction.insert_field_value_to_line("Counter", new_line, counter+1)
                        new_line = self.transaction.insert_field_value_to_line("Amount", new_line, amount)
                        new_line = self.transaction.insert_field_value_to_line("Currency", new_line, currency)
                        new_file_content += new_line
                        # create new footer
                        new_line = self.footer.create_empty_line()
                        new_line = self.footer.insert_field_value_to_line("Total Counter", new_line, counter+1)
                        new_line = self.footer.insert_field_value_to_line("Control sum", new_line, amount_sum)
                        new_file_content += new_line

        except FileNotFoundError:
            return f"NO SUCH FILE {self.path}"
        
        self.drop_payload_to_file(new_file_content)
        
    def transaction_check(self, block_name, line, transaction_no=0):
        if block_name == "transaction":
            counter = int(self.transaction.get_field_value_from_line("Counter", line))
            if counter != transaction_no: return False
        return True
    
    def drop_payload_to_file(self, payload):
        with open(self.path, "w") as file:
            file.write(payload)

    def create_empty_file(self):
        print("create_empty_file")
        new_file_content = self.header.create_empty_line() + self.footer.create_empty_line()
        self.drop_payload_to_file(new_file_content)


# ====== Lines ======================================================


class Line():
    def __init__(self, id, fields_definition_list):
        self.fields_list = [field[2] for field in fields_definition_list]
        self.fields_dict = {field[2]: Field(*field) for field in fields_definition_list}
        # assign line ID to Line object (self.id) and to Field object (update_value)
        self.id = self.fields_dict[self.fields_list[0]].update_value(id)

    def create_empty_line(self):
        result = ""
        for field_name in self.fields_list:
            result += self.fields_dict[field_name].value
        return result + "\n"

    def get_field_value_from_line(self, field_name, line):
        if not self.fields_dict.get(field_name): return f"NO SUCH FIELD {field_name}"
        return self.fields_dict[field_name].get_value_from_line(line)

    def insert_field_value_to_line(self, field_name, line, value):
        if not self.fields_dict.get(field_name): return f"NO SUCH FIELD {field_name}"
        return self.fields_dict[field_name].insert_value_to_line(line, value)


# ====== FIELDS ======================================================


class Field():
    def __init__(self, position_from: int, position_to: int, name: str, data_type=str, value=False):
        self.position_from = position_from
        self.position_to = position_to
        self.length = position_to - position_from + 1
        self.name = name
        self.data_type = data_type        
        if data_type == str:
            self.whitespace = "_"
        elif data_type == int:
            self.whitespace = "0"
        else:
            self.whitespace = "."
        self.update_value(value)

    # def __str__(self) -> str:
    def get_placeholder(self):
        if hasattr(self, "value"):
            return self.value
        return  self.whitespace * self.length
        # return self.name[0] * self.length

    def check_and_format_value(self, value):
        if not value:
            return self.get_placeholder()
        elif type(value) != self.data_type:
            raise TypeError("Wrong type of inserted value! " + \
                    f"Should be: {self.data_type.__name__}, is: {type(value).__name__}, value: {value}")
        elif len(str(value)) > self.length:
            raise ValueError(f"Value to long!" + \
                    f"Should be: {self.length}, is: {len(str(value))}, value: {value}")
        else:
            return str(value).rjust(self.length, self.whitespace)

    def update_value(self, value):
        self.value = self.check_and_format_value(value)
        return self.value

    def get_value_from_line(self, line: str) -> str:
        if len(line) != 121: # 120 + end of line
            raise ImportError
        return self.data_type(line[self.position_from-1: self.position_to])

    def insert_value_to_line(self, line: str, value) -> str:     
        if len(line) != 121: # 120 + end of line
            raise ImportError(f"Wrong line lenght, is: {len(line)}, line: {line}")
        self.value = self.check_and_format_value(value)
        return line[:self.position_from-1] + self.value + line[self.position_to:]



        