"""
MDL Lexer - JavaScript-style syntax with curly braces and semicolons
Handles unlimited nesting with explicit block boundaries
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class TokenType(Enum):
    # Keywords
    PACK = "PACK"
    NAMESPACE = "NAMESPACE"
    FUNCTION = "FUNCTION"
    ON_TICK = "ON_TICK"
    ON_LOAD = "ON_LOAD"
    TAG = "TAG"
    ADD = "ADD"
    
    # Variable keywords
    VAR = "VAR"
    LET = "LET"
    CONST = "CONST"
    NUM = "NUM"
    STR = "STR"
    LIST = "LIST"
    
    # Control flow
    IF = "IF"
    ELSE = "ELSE"
    ELSE_IF = "ELSE_IF"
    WHILE = "WHILE"
    FOR = "FOR"
    IN = "IN"
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"
    SWITCH = "SWITCH"
    CASE = "CASE"
    DEFAULT = "DEFAULT"
    TRY = "TRY"
    CATCH = "CATCH"
    THROW = "THROW"
    RETURN = "RETURN"
    
    # Operators
    ASSIGN = "ASSIGN"  # =
    PLUS = "PLUS"      # +
    MINUS = "MINUS"    # -
    MULTIPLY = "MULTIPLY"  # *
    DIVIDE = "DIVIDE"  # /
    MODULO = "MODULO"  # %
    EQUAL = "EQUAL"    # ==
    NOT_EQUAL = "NOT_EQUAL"  # !=
    LESS = "LESS"      # <
    LESS_EQUAL = "LESS_EQUAL"  # <=
    GREATER = "GREATER"  # >
    GREATER_EQUAL = "GREATER_EQUAL"  # >=
    AND = "AND"        # &&
    OR = "OR"          # ||
    NOT = "NOT"        # !
    
    # Literals
    STRING = "STRING"
    NUMBER = "NUMBER"
    IDENTIFIER = "IDENTIFIER"
    
    # Punctuation
    SEMICOLON = "SEMICOLON"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACKET = "LBRACKET"  # [
    RBRACKET = "RBRACKET"  # ]
    COMMA = "COMMA"
    
    # Special
    NEWLINE = "NEWLINE"
    EOF = "EOF"
    COMMENT = "COMMENT"
    COMMAND = "COMMAND"
    IMPORT = "IMPORT"
    FROM = "FROM"
    AS = "AS"

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

class MDLLexer:
    """Lexer for JavaScript-style MDL language with curly braces."""
    
    def __init__(self, source: str):
        self.source = source
        self.lines = source.splitlines()
        self.tokens: List[Token] = []
        
    def tokenize(self) -> List[Token]:
        """Tokenize the MDL source code."""
        self.tokens = []
        
        for line_num, line in enumerate(self.lines):
            self.current_line = line_num + 1
            
            # Skip empty lines
            stripped = line.strip()
            if not stripped:
                continue
            
            # Handle comments
            if stripped.startswith('//'):
                self.tokens.append(Token(TokenType.COMMENT, stripped, line_num + 1, 0))
                continue
            
            # Tokenize the line content
            self._tokenize_line(stripped, line_num + 1)
            
            # Add newline token
            self.tokens.append(Token(TokenType.NEWLINE, "\n", line_num + 1, len(line)))
        
        self.tokens.append(Token(TokenType.EOF, "", len(self.lines) + 1, 0))
        return self.tokens
    
    def _tokenize_line(self, line: str, line_num: int):
        """Tokenize a single line of MDL code."""
        # Keywords that start statements
        keyword_patterns = [
            (r'^pack\b', TokenType.PACK),
            (r'^namespace\b', TokenType.NAMESPACE),
            (r'^function\b', TokenType.FUNCTION),
            (r'^on_tick\b', TokenType.ON_TICK),
            (r'^on_load\b', TokenType.ON_LOAD),
            (r'^tag\b', TokenType.TAG),
            (r'^add\b', TokenType.ADD),
            (r'^if\b', TokenType.IF),
            (r'^var\b', TokenType.VAR),
            (r'^let\b', TokenType.LET),
            (r'^const\b', TokenType.CONST),
            (r'^num\b', TokenType.NUM),
            (r'^str\b', TokenType.STR),
            (r'^list\b', TokenType.LIST),
            (r'^else\b', TokenType.ELSE),
            (r'^while\b', TokenType.WHILE),
            (r'^for\b', TokenType.FOR),
            (r'^in\b', TokenType.IN),
            (r'^break\b', TokenType.BREAK),
            (r'^continue\b', TokenType.CONTINUE),
            (r'^switch\b', TokenType.SWITCH),
            (r'^case\b', TokenType.CASE),
            (r'^default\b', TokenType.DEFAULT),
            (r'^try\b', TokenType.TRY),
            (r'^catch\b', TokenType.CATCH),
            (r'^throw\b', TokenType.THROW),
            (r'^return\b', TokenType.RETURN),
            (r'^import\b', TokenType.IMPORT),
            (r'^from\b', TokenType.FROM),
            (r'^as\b', TokenType.AS),
        ]
        
        # Check for keywords first (but handle for loops specially)
        if line.startswith('for '):
            self.tokens.append(Token(TokenType.FOR, "for", line_num, 0))
            remaining = line[4:].strip()
            if remaining:
                self._tokenize_remaining(remaining, line_num)
            return
        
        # Check for other keywords
        for pattern, token_type in keyword_patterns:
            if token_type == TokenType.FOR:  # Skip for, we handled it above
                continue
            match = re.match(pattern, line)
            if match:
                self.tokens.append(Token(token_type, match.group(0), line_num, 0))
                remaining = line[match.end():].strip()
                if remaining:
                    self._tokenize_remaining(remaining, line_num)
                return
        
        # Check for "else if" pattern
        if line.startswith('else if'):
            self.tokens.append(Token(TokenType.ELSE_IF, "else if", line_num, 0))
            remaining = line[8:].strip()
            if remaining:
                self._tokenize_remaining(remaining, line_num)
            return
        
        # Check for function call
        if line.startswith('function '):
            self.tokens.append(Token(TokenType.FUNCTION, "function", line_num, 0))
            remaining = line[9:].strip()
            if remaining:
                self._tokenize_remaining(remaining, line_num)
            return
        
        # Check for function calls (identifier followed by parentheses)
        if '(' in line and not line.startswith('if ') and not line.startswith('while ') and not line.startswith('for '):
            # This might be a function call
            parts = line.split('(', 1)
            if parts[0].strip() and re.match(r'^[a-zA-Z_][a-zA-Z0-9_:]*$', parts[0].strip()):
                # This looks like a function call
                self.tokens.append(Token(TokenType.IDENTIFIER, parts[0].strip(), line_num, 0))
                self.tokens.append(Token(TokenType.LPAREN, "(", line_num, 0))
                if len(parts) > 1:
                    self._tokenize_remaining(parts[1], line_num)
                return
        
        # Check for switch statements with parentheses
        if line.startswith('switch '):
            self.tokens.append(Token(TokenType.SWITCH, "switch", line_num, 0))
            remaining = line[7:].strip()
            if remaining:
                self._tokenize_remaining(remaining, line_num)
            return
        
        # Check for try statements
        if line.startswith('try '):
            self.tokens.append(Token(TokenType.TRY, "try", line_num, 0))
            remaining = line[4:].strip()
            if remaining:
                self._tokenize_remaining(remaining, line_num)
            return
        
        # Check for catch statements
        if line.startswith('catch '):
            self.tokens.append(Token(TokenType.CATCH, "catch", line_num, 0))
            remaining = line[6:].strip()
            if remaining:
                self._tokenize_remaining(remaining, line_num)
            return
        
        # Check for catch statements that might be on the same line as closing brace
        if '} catch' in line:
            # Split the line at '} catch'
            parts = line.split('} catch', 1)
            
            # Always generate the RBRACE token for the } before catch
            self.tokens.append(Token(TokenType.RBRACE, "}", line_num, 0))
            
            # Check if there was content before the }
            if parts[0].strip() and parts[0].strip() != '}':
                # This is a command that ends with }
                self.tokens.append(Token(TokenType.COMMAND, parts[0].strip(), line_num, 0))
            
            # Handle the catch part
            self.tokens.append(Token(TokenType.CATCH, "catch", line_num, 0))
            if len(parts) > 1:
                # Handle the catch parameters and body
                catch_part = parts[1].strip()
                if catch_part.startswith('('):
                    # Parse catch parameters
                    self.tokens.append(Token(TokenType.LPAREN, "(", line_num, 0))
                    # Find the closing parenthesis
                    paren_end = catch_part.find(')', 1)
                    if paren_end > 0:
                        param_part = catch_part[1:paren_end].strip()
                        if param_part:
                            self.tokens.append(Token(TokenType.IDENTIFIER, param_part, line_num, 0))
                        self.tokens.append(Token(TokenType.RPAREN, ")", line_num, 0))
                        
                        # Handle the rest (opening brace and body)
                        remaining = catch_part[paren_end + 1:].strip()
                        if remaining:
                            self._tokenize_remaining(remaining, line_num)
                    else:
                        # No closing parenthesis found, treat as command
                        self.tokens.append(Token(TokenType.COMMAND, catch_part, line_num, 0))
                else:
                    # No parentheses, treat as command
                    self.tokens.append(Token(TokenType.COMMAND, catch_part, line_num, 0))
            return
        
        # Check for catch statements on their own line
        if line.strip() == 'catch':
            self.tokens.append(Token(TokenType.CATCH, "catch", line_num, 0))
            return
        
        # Check for control flow constructs
        stripped_line = line.strip()
        
        # Check for "} else if" pattern
        if stripped_line.startswith('} else if '):
            self.tokens.append(Token(TokenType.RBRACE, "}", line_num, 0))
            self.tokens.append(Token(TokenType.ELSE_IF, "else if", line_num, 0))
            # Extract the condition (everything between "else if " and " {")
            condition_start = stripped_line.find('else if ') + 8
            condition_end = stripped_line.rfind(' {')
            if condition_end > condition_start:
                condition = stripped_line[condition_start:condition_end].strip()
                self.tokens.append(Token(TokenType.STRING, condition, line_num, 0))
                self.tokens.append(Token(TokenType.LBRACE, "{", line_num, 0))
            return
            
        # Check for "} else {" pattern
        elif stripped_line == '} else {':
            self.tokens.append(Token(TokenType.RBRACE, "}", line_num, 0))
            self.tokens.append(Token(TokenType.ELSE, "else", line_num, 0))
            self.tokens.append(Token(TokenType.LBRACE, "{", line_num, 0))
            return
            
        # Check for single braces
        elif stripped_line == '{':
            self.tokens.append(Token(TokenType.LBRACE, "{", line_num, 0))
            return
        elif stripped_line == '}':
            self.tokens.append(Token(TokenType.RBRACE, "}", line_num, 0))
            return
        
        # Check if this looks like a variable assignment (identifier = expression)
        assignment_pattern = r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$'
        match = re.match(assignment_pattern, line.strip())
        
        if match:
            # This is a variable assignment - tokenize it properly
            var_name = match.group(1)
            expression = match.group(2).rstrip(';').strip()
            
            # Add identifier token
            self.tokens.append(Token(TokenType.IDENTIFIER, var_name, line_num, 0))
            # Add assignment token
            self.tokens.append(Token(TokenType.ASSIGN, "=", line_num, 0))
            # Tokenize the expression
            self._tokenize_expression(expression, line_num)
        else:
            # Otherwise, treat as a command
            # Remove trailing semicolon if present
            command_line = line.rstrip(';').strip()
            if command_line:
                self.tokens.append(Token(TokenType.COMMAND, command_line, line_num, 0))
            # Add semicolon token if the line ended with one
            if line.rstrip().endswith(';'):
                self.tokens.append(Token(TokenType.SEMICOLON, ";", line_num, 0))
    
    def _tokenize_expression(self, expression: str, line_num: int):
        """Tokenize an expression (right side of assignment)."""
        # Handle quoted strings first
        import re
        
        # Find all quoted strings
        quoted_strings = re.findall(r'"([^"]*)"', expression)
        remaining_expr = expression
        
        # Replace quoted strings with placeholders
        for i, quoted in enumerate(quoted_strings):
            placeholder = f"__QUOTED_{i}__"
            remaining_expr = remaining_expr.replace(f'"{quoted}"', placeholder, 1)
        
        # Handle Minecraft selectors
        selector_pattern = r'@[a-zA-Z]+\[[^\]]+\]'
        selectors = re.findall(selector_pattern, remaining_expr)
        
        # Replace selectors with placeholders
        for i, selector in enumerate(selectors):
            placeholder = f"__SELECTOR_{i}__"
            remaining_expr = remaining_expr.replace(selector, placeholder, 1)
        
        # Add spaces around operators
        remaining_expr = re.sub(r'([+\-*/%<>!&|=])', r' \1 ', remaining_expr)
        
        # Split the expression
        parts = remaining_expr.split()
        
        # Process each part
        quoted_index = 0
        selector_index = 0
        for part in parts:
            if part.startswith("__QUOTED_") and part.endswith("__"):
                # This is a placeholder for a quoted string
                self.tokens.append(Token(TokenType.STRING, quoted_strings[quoted_index], line_num, 0))
                quoted_index += 1
            elif part.startswith("__SELECTOR_") and part.endswith("__"):
                # This is a placeholder for a Minecraft selector
                self.tokens.append(Token(TokenType.STRING, selectors[selector_index], line_num, 0))
                selector_index += 1
            elif part.isdigit():
                self.tokens.append(Token(TokenType.NUMBER, part, line_num, 0))
            elif re.match(r'^[a-zA-Z_][a-zA-Z0-9_:]*$', part):
                self.tokens.append(Token(TokenType.IDENTIFIER, part, line_num, 0))
            elif part == "+":
                self.tokens.append(Token(TokenType.PLUS, "+", line_num, 0))
            elif part == "-":
                self.tokens.append(Token(TokenType.MINUS, "-", line_num, 0))
            elif part == "*":
                self.tokens.append(Token(TokenType.MULTIPLY, "*", line_num, 0))
            elif part == "/":
                self.tokens.append(Token(TokenType.DIVIDE, "/", line_num, 0))
            elif part == "=":
                self.tokens.append(Token(TokenType.ASSIGN, "=", line_num, 0))
            else:
                # Unknown token - treat as string
                self.tokens.append(Token(TokenType.STRING, part, line_num, 0))
    
    def _tokenize_remaining(self, line: str, line_num: int):
        """Tokenize remaining parts of a line."""
        # Handle quoted strings first (they might contain spaces)
        import re
        
        # Find all quoted strings
        quoted_strings = re.findall(r'"([^"]*)"', line)
        remaining_line = line
        
        # Replace quoted strings with placeholders
        for i, quoted in enumerate(quoted_strings):
            placeholder = f"__QUOTED_{i}__"
            remaining_line = remaining_line.replace(f'"{quoted}"', placeholder, 1)
        
        # Handle Minecraft selectors (like @e[type=value,distance=..5]) as single tokens
        # Find all Minecraft selectors
        selector_pattern = r'@[a-zA-Z]+\[[^\]]+\]'
        selectors = re.findall(selector_pattern, remaining_line)
        
        # Replace selectors with placeholders
        for i, selector in enumerate(selectors):
            placeholder = f"__SELECTOR_{i}__"
            remaining_line = remaining_line.replace(selector, placeholder, 1)
        
        # Handle compound tokens like (identifier) by adding spaces around special characters
        remaining_line = re.sub(r'([(){}\[\]{}=+\-*/%<>!&|,;])', r' \1 ', remaining_line)
        
        # Split the remaining line
        parts = remaining_line.split()
        
        # Process each part
        quoted_index = 0
        selector_index = 0
        for part in parts:
            if part.startswith("__QUOTED_") and part.endswith("__"):
                # This is a placeholder for a quoted string
                self.tokens.append(Token(TokenType.STRING, quoted_strings[quoted_index], line_num, 0))
                quoted_index += 1
            elif part.startswith("__SELECTOR_") and part.endswith("__"):
                # This is a placeholder for a Minecraft selector
                self.tokens.append(Token(TokenType.STRING, selectors[selector_index], line_num, 0))
                selector_index += 1
            elif part.endswith(";"):
                # Handle parts that end with semicolon
                base_part = part[:-1]
                if base_part:  # Only process base_part if it's not empty
                    if base_part.startswith("__QUOTED_") and base_part.endswith("__"):
                        # This is a placeholder for a quoted string
                        self.tokens.append(Token(TokenType.STRING, quoted_strings[quoted_index], line_num, 0))
                        quoted_index += 1
                    elif base_part.startswith("__SELECTOR_") and base_part.endswith("__"):
                        # This is a placeholder for a Minecraft selector
                        self.tokens.append(Token(TokenType.STRING, selectors[selector_index], line_num, 0))
                        selector_index += 1
                    elif base_part.isdigit():
                        self.tokens.append(Token(TokenType.NUMBER, base_part, line_num, 0))
                    elif re.match(r'^[a-zA-Z_][a-zA-Z0-9_:]*$', base_part):
                        self.tokens.append(Token(TokenType.IDENTIFIER, base_part, line_num, 0))
                    else:
                        self.tokens.append(Token(TokenType.STRING, base_part, line_num, 0))
                self.tokens.append(Token(TokenType.SEMICOLON, ";", line_num, 0))
            elif part == ";":
                self.tokens.append(Token(TokenType.SEMICOLON, ";", line_num, 0))
            elif part == "{":
                self.tokens.append(Token(TokenType.LBRACE, "{", line_num, 0))
            elif part == "}":
                self.tokens.append(Token(TokenType.RBRACE, "}", line_num, 0))
            elif part == "(":
                self.tokens.append(Token(TokenType.LPAREN, "(", line_num, 0))
            elif part == ")":
                self.tokens.append(Token(TokenType.RPAREN, ")", line_num, 0))
            elif part == "[":
                self.tokens.append(Token(TokenType.LBRACKET, "[", line_num, 0))
            elif part == "]":
                self.tokens.append(Token(TokenType.RBRACKET, "]", line_num, 0))
            elif part == ",":
                self.tokens.append(Token(TokenType.COMMA, ",", line_num, 0))
            elif part == "=":
                self.tokens.append(Token(TokenType.ASSIGN, "=", line_num, 0))
            elif part == "+":
                self.tokens.append(Token(TokenType.PLUS, "+", line_num, 0))
            elif part == "-":
                self.tokens.append(Token(TokenType.MINUS, "-", line_num, 0))
            elif part == "*":
                self.tokens.append(Token(TokenType.MULTIPLY, "*", line_num, 0))
            elif part == "/":
                self.tokens.append(Token(TokenType.DIVIDE, "/", line_num, 0))
            elif part == "%":
                self.tokens.append(Token(TokenType.MODULO, "%", line_num, 0))
            elif part == "==":
                self.tokens.append(Token(TokenType.EQUAL, "==", line_num, 0))
            elif part == "!=":
                self.tokens.append(Token(TokenType.NOT_EQUAL, "!=", line_num, 0))
            elif part == "<":
                self.tokens.append(Token(TokenType.LESS, "<", line_num, 0))
            elif part == "<=":
                self.tokens.append(Token(TokenType.LESS_EQUAL, "<=", line_num, 0))
            elif part == ">":
                self.tokens.append(Token(TokenType.GREATER, ">", line_num, 0))
            elif part == ">=":
                self.tokens.append(Token(TokenType.GREATER_EQUAL, ">=", line_num, 0))
            elif part == "&&":
                self.tokens.append(Token(TokenType.AND, "&&", line_num, 0))
            elif part == "||":
                self.tokens.append(Token(TokenType.OR, "||", line_num, 0))
            elif part == "!":
                self.tokens.append(Token(TokenType.NOT, "!", line_num, 0))
            elif part.isdigit():
                self.tokens.append(Token(TokenType.NUMBER, part, line_num, 0))
            elif part == "in":
                self.tokens.append(Token(TokenType.IN, "in", line_num, 0))
            elif re.match(r'^[a-zA-Z_][a-zA-Z0-9_:]*$', part):
                self.tokens.append(Token(TokenType.IDENTIFIER, part, line_num, 0))
            else:
                self.tokens.append(Token(TokenType.STRING, part, line_num, 0))

def lex_mdl_js(source: str) -> List[Token]:
    """Convenience function to lex JavaScript-style MDL source code."""
    lexer = MDLLexer(source)
    return lexer.tokenize()
