# Handle file in Python - demo
# By Tomasz Gołaszewski
# 2025.04.14

import logging


class FileWithConstantWidth():
    def __init__(self, path: str):
        """
        Initializing and building the file object structure.
        Creates empty file in case the file does not exist.

        Args:
            path (str): Path to file.
        """
        self.path = path

        # building the object
        # class Line(id, [Fields' inits' arguments' list])
        # class Field(position_from: int, position_to: int, name: str, data_type=str, has_decimals=False, value=False)
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
            (9, 20, "Amount", int, True),
            (21, 23, "Currency"),
            (24, 120, "Reserved", False),
        ])
        self.footer = Line(3, [
            (1, 2, "Field ID", int),
            (3, 8, "Total Counter", int),
            (9, 20, "Control sum", int, True),
            (21, 120, "Reserved", False),
        ])
 
        try:
            with open(self.path, "r") as file:
                pass
        except FileNotFoundError:
            print("No file was found!")
            self.create_empty_file()

    def get_value(self, block: str, field: str, transaction_no: int = 0) -> str:
        """
        Retrieves the value of a specified field from a file.

        This function opens a file, iterates through its lines, and searches for the specified block and fild
        (and optionally transaction number). If found, it retrieves the value of the requested field from the line.
        Raises an error if the block name is invalid and handles file-related errors gracefully.

        Args:
            block (str): The name of the block to search ("header", "transaction", or "footer").
            field (str): The name of the field which value is to be retrieved.
            transaction_no (int, optional): The transaction number to locate within the transaction block. Defaults to 0.

        Returns:
            str: The value of the specified field if found, or a message indicating the result of the search.

        Raises:
            ValueError: If the block name is invalid.
        """
        if not hasattr(self, block):
            raise NameError("Wrong block name!")
        block_id = getattr(self, block).id
        try:
            with open(self.path, "r") as file:
                for line in file:
                    if block_id == line[0:2] and self.transaction_check(block, line, transaction_no):
                        return getattr(self, block).get_field_value_from_line(field, line)
                return f"NO SUCH LINE {block} " + str(transaction_no) if block_id == "02" else ""
        except FileNotFoundError:
            return f"NO SUCH FILE {self.path}"
        
    def insert_value(self, block: str, field: str, value, transaction_no=0):
        """
        Inserts a specified value into a field within the lines of a file.

        This function opens a file, iterates through its lines, and attempts to insert a given
        value into the specified field of a particular block. Certain blocks (e.g., "transaction"
        and "footer") are restricted from modification, and an error is raised for invalid block names.

        Args:
            block (str): The name of the block to modify ("header", "transaction", or "footer").
            field (str): The name of the field in which the value will be inserted.
            value (Any): The value to be inserted into the specified field.
            transaction_no (int, optional): The transaction number to find, if applicable. Defaults to 0.

        Returns:
            str: A message indicating the result of the process or comments about errors during the search.

        Raises:
            ValueError: If the block name is invalid.
        """
        if not hasattr(self, block):
            raise NameError("Wrong block name!")
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
                    else:
                        new_file_content += line
        except FileNotFoundError:
            return f"NO SUCH FILE {self.path}"
        
        self.drop_payload_to_file(new_file_content)
        return "DONE!"

    def add_transaction(self, amount: float, currency: str):
        """
        Adds a new transaction to the file and updates the footer with the new total counter and control sum.

        This function validates the transaction amount and currency, calculates the formatted amount,
        iterates through the existing file content, and performs the following actions:
        - Copies header and transaction lines.
        - Inserts a new transaction with the provided details.
        - Updates the footer with the total counter and control sum.

        Args:
            amount (float): The transaction amount in floating-point format. Must be non-negative.
            currency (str): The currency of the transaction. Supported currencies are "PLN", "EUR", and "USD".

        Returns:
            str: A message indicating the result of the process or comments about errors during the search.
        
        Raises:
            ValueError: If the amount is negative or the currency is not one of the supported options.
        """
        if amount < 0:
            raise ValueError("Amount can't be negative!")
        if currency not in ["PLN", "EUR", "USD"]:
            raise ValueError("Wrong currency!")
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
                        new_file_content += new_line # replace
                        # create new footer
                        new_line = self.footer.create_empty_line()
                        new_line = self.footer.insert_field_value_to_line("Total Counter", new_line, counter+1)
                        new_line = self.footer.insert_field_value_to_line("Control sum", new_line, amount_sum)
                        new_file_content += new_line # replace

        except FileNotFoundError:
            return f"NO SUCH FILE {self.path}"
        
        self.drop_payload_to_file(new_file_content)
        return "DONE!"
        
    def transaction_check(self, block_name: str, line: str, transaction_no: int = 0) -> bool:
        """
        Checks if the given line is the transaction line we are looking for.
        For non-transaction lines returns True.

        Args:
            block_name (str): The name of the block: "header", "transaction" or "footer".
            line (str): File line.
            transaction_no (int, optional): The transaction number to validate against. Defaults to 0.

        Returns:
            bool: True if the line "Counter" field value matches checked transaction number \
                        or the block is non-transaction type, False otherwise.
        """
        if block_name == "transaction":
            counter = int(self.transaction.get_field_value_from_line("Counter", line))
            if counter != transaction_no: return False
        return True
    
    def drop_payload_to_file(self, payload: str):
        """
        Writes the provided payload to a file at the path specified in object attribute.

        Args:
            payload (str): The content to be written to the file.
        """
        with open(self.path, "w") as file:
            file.write(payload)

    def create_empty_file(self):
        """
        Creates a new file with empty header's and footer's placeholders.
        """
        new_file_content = self.header.create_empty_line() + self.footer.create_empty_line()
        self.drop_payload_to_file(new_file_content)
        print("New file created!")


# ====== Lines ======================================================


class Line():
    def __init__(self, id: int, fields_definition_list: list):
        self.fields_list = [field[2] for field in fields_definition_list]
        self.fields_dict = {field[2]: Field(*field) for field in fields_definition_list}
        # assign line ID to Line object (self.id) and to Field object (update_value)
        self.id = self.fields_dict[self.fields_list[0]].update_value(id)

    def create_empty_line(self):
        """
        Creates a new line with empty fields' placeholders.

        Returns:
            str: String with new line. End of line symbol is added at end. 
        """
        result = ""
        for field_name in self.fields_list:
            result += self.fields_dict[field_name].value
        return result + "\n"

    def get_field_value_from_line(self, field_name: str, line: str) -> str:
        """
        Retrieves the value of a specified field from a given line.

        Args:
            field_name (str): The name of the field whose value is to be retrieved.
            line (str): The line of data from which to extract the field value.

        Returns:
            str: The value of the specified field if it exists or error message.
        """

        if not self.fields_dict.get(field_name): return f"NO SUCH FIELD {field_name}"
        return self.fields_dict[field_name].get_value_from_line(line)

    def insert_field_value_to_line(self, field_name: str, line: str, value) -> str:
        """
        Inserts the value of a specified field to given line.

        Args:
            field_name (str): The name of the field whose value will be inserted.
            line (str): The line of data.
            value (Any): The value which will be inserted.

        Returns:
            str: The line with inserted new value or error message.
        """
        if not self.fields_dict.get(field_name): return f"NO SUCH FIELD {field_name}"
        return self.fields_dict[field_name].insert_value_to_line(line, value)


# ====== FIELDS ======================================================


class Field():
    def __init__(self, position_from: int, position_to: int, name: str, data_type=str, has_decimals=False, value=False):
        self.position_from = position_from
        self.position_to = position_to
        self.length = position_to - position_from + 1
        self.name = name
        self.data_type = data_type
        self.has_decimals=has_decimals
        if data_type == int:
            self.whitespace = "0"
        else:
            self.whitespace = " "
        self.update_value(value)

    def get_placeholder(self) -> str:
        if hasattr(self, "value"):
            return self.value
        return  self.whitespace * self.length

    def check_and_format_value(self, value):
        if not value:
            return self.get_placeholder()
        if self.has_decimals:
            value = int(value * 100)
        if type(value) != self.data_type:
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
        value = self.data_type(line[self.position_from-1: self.position_to])
        if self.has_decimals:
            return value / 100
        else:
            return value

    def insert_value_to_line(self, line: str, value) -> str:     
        if len(line) != 121: # 120 + end of line
            raise ImportError(f"Wrong line lenght, is: {len(line)}, line: {line}")
        self.value = self.check_and_format_value(value)
        return line[:self.position_from-1] + self.value + line[self.position_to:]



        