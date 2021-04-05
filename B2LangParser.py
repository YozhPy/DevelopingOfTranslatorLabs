class B2LangParser:

    def __init__(self, table_of_symbols):
        self.table_of_symbols = table_of_symbols
        self.len_table_of_symbols = len(self.table_of_symbols)
        self.row_number = 1

        self.success = True

    def run(self):
        self.success = self.parse_program()
        print('\n\033[0m')

    @staticmethod
    def warning_parse(warning: str, *args):
        print("\033[33m")
        if warning == 'no_effect':
            row_number, = args
            print('B2LangParser Warning:'
                  f'\n\tВираз на рядку {row_number} не має ефекту.'
                  )
        print('\n\033[0m')

    @staticmethod
    def fail_parse(error: str, *args):
        print("\033[31m")
        if error == 'eop':
            # row_number, lexeme, token = args
            row_number, = args
            print('B2LangParser ERROR:'
                  f'\n\tНеочікуваний кінець програми - в таблиці символів немає запису з номером {row_number}.'
                  # f'\n\tОчікувалось - {row_number}'
                  )
            exit(1001)
        elif error == 'after_eop':
            print('B2LangParser ERROR:'
                  f'\n\tНеочікуваіні лексеми за межами головної програми.'
                  # f'\n\tОчікувалось - {row_number}'
                  )
            exit(1002)
        elif error == 'tokens':
            line_number, expected_lex, expected_tok, actual_lex, actual_tok = args
            print(f'B2LangParser ERROR:'
                  f'\n\tВ рядку {line_number} неочікуваний елемент ({expected_lex},{expected_tok}).'
                  f'\n\tОчікувався - ({actual_lex},{actual_tok}).')
            exit(1)
        elif error == 'not_expected':
            line_number, lex, tok, expected = args
            print(f'B2LangParser ERROR:'
                  f'\n\tВ рядку {line_number} неочікуваний елемент ({lex},{tok}).'
                  f'\n\tОчікувався - {expected}.')
            exit(2)

    @staticmethod
    def print_not_final_token(line_number, lex, tok, indent=''):
        print(indent + f'в рядку {line_number} - {(lex, tok)}')

    def get_symbol(self):
        if self.row_number > self.len_table_of_symbols:
            B2LangParser.fail_parse('eop', self.row_number)
        return self.table_of_symbols[self.row_number][0:-1]

    def parse_token(self, lexeme, token, indent=''):
        line_number, lex, tok = self.get_symbol()

        self.row_number += 1

        if lex == lexeme and tok == token:
            print(f"{indent}parseToken: В рядку {line_number} токен {(lex, tok)}")
            return True
        else:
            B2LangParser.fail_parse('tokens', line_number, lex, tok, lexeme, token)
            return False

    def parse_program(self):
        try:
            self.parse_token('start', 'keyword')
            self.parse_token('{', 'curve_brackets_op')

            self.parse_statements_list()

            if self.row_number < self.len_table_of_symbols:
                B2LangParser.fail_parse('after_eop')
            else:
                self.parse_token('}', 'curve_brackets_op')
        except SystemExit as e:
            print('Parser: Аварійне завершення програми з кодом {0}'.format(e))
            return False

        print("\033[32m")
        print('B2LangParser: Синтаксичний аналіз завершився успішно')
        return True

    def parse_statements_list(self):
        print('parse_statement_list:')
        while self.parse_statement():
            pass
        return True

    def parse_statement(self):
        print('\t', 'parse_statement', sep='')
        line_number, lex, tok = self.get_symbol()

        if tok == 'ident':
            print('\t' * 2, 'parse_assign', sep='')
            self.row_number += 1
            self.print_not_final_token(line_number, lex, tok, indent='\t' * 3)
            if self.get_symbol()[-1] == 'assign_op':
                self.parse_assign()
            else:
                self.row_number -= 1
                self.parse_expression()
                B2LangParser.warning_parse('no_effect', line_number)
            self.parse_token(';', 'op_end', '\t' * 3)
            return True

        elif lex == 'input' and tok == 'keyword':
            self.parse_input()
            self.parse_token(';', 'op_end', '\t' * 3)
            return True

        elif lex == 'print' and tok == 'keyword':
            self.parse_print()
            self.parse_token(';', 'op_end', '\t' * 3)
            return True

        elif lex == 'for' and tok == 'keyword':
            self.parse_for()
            return True

        elif lex == 'while' and tok == 'keyword':
            self.parse_for()
            return True

        elif lex == 'if' and tok == 'keyword':
            self.parse_if()
            return True

        elif lex in ('int', 'float', 'bool', 'label') and tok == 'keyword':
            self.parse_declaration()
            self.parse_token(';', 'op_end', '\t' * 3)
            return True

        elif lex == '}' and tok == 'curve_brackets_op':
            return False

        else:
            self.parse_expression()
            self.parse_token(';', 'op_end', '\t' * 3)
            B2LangParser.warning_parse('no_effect', line_number)
            return True

    def parse_input(self):
        print('\t' * 2, 'parse_input', sep='')

        line_number, lex, tok = self.get_symbol()
        self.row_number += 1
        self.print_not_final_token(line_number, lex, tok, indent='\t' * 3)

        self.parse_token('(', 'brackets_op', '\t' * 4)
        self.parse_var_list()
        self.parse_token(')', 'brackets_op', '\t' * 4)

    def parse_print(self):
        print('\t' * 2, 'parse_print', sep='')

        line_number, lex, tok = self.get_symbol()
        self.row_number += 1
        self.print_not_final_token(line_number, lex, tok, indent='\t' * 3)

        self.parse_token('(', 'brackets_op', '\t' * 4)
        self.parse_var_list_for_command()
        self.parse_token(')', 'brackets_op', '\t' * 4)

    def parse_var_list_for_command(self):
        print('\t' * 3, 'parse_var_list_to_command', sep='')
        line_number, lex, tok = self.get_symbol()
        self.row_number += 1

        if tok == 'ident':
            self.print_not_final_token(line_number, lex, tok, indent='\t' * 5)

        else:
            B2LangParser.fail_parse('not_expected', line_number, lex, tok,
                                 "ідентифікатор (ident)")

        line_number, lex, tok = self.get_symbol()
        if lex == ')' and tok == 'brackets_op':
            return True

        elif lex == ',' and tok == 'comma':
            self.row_number += 1
            self.print_not_final_token(line_number, lex, tok, indent='\t' * 5)
            self.parse_var_list()

    def parse_assign(self):
        print('\t' * 2, 'parse_assign', sep='')

        if self.parse_token('=', 'assign_op', '\t' * 3):
            self.parse_expression()
            return True
        else:
            return False

    def parse_expression(self, required=False):
        print('\t' * 3, 'parse_expression', sep='')
        self.parse_arithm_expression()

        while self.parse_bool_expr():
            pass

        return True

    def parse_bool_expr(self, required=False):
        print('\t' * 4, 'parse_bool_expr', sep='')
        line_number, lex, tok = self.get_symbol()
        if tok in ('rel_op', 'bool_op'):
            self.row_number += 1
            self.print_not_final_token(line_number, lex, tok, indent='\t' * 4)
            self.parse_arithm_expression()
            return True
        elif required:
            B2LangParser.fail_parse('not_expected', line_number, lex, tok,
                                 required)
        else:
            return False

    def parse_arithm_expression(self):
        print('\t' * 4, 'parse_arithm_expression', sep='')
        line_number, lex, tok = self.get_symbol()

        if lex == '-' and tok == 'add_op':
            self.row_number += 1
            self.print_not_final_token(line_number, lex, tok, indent='\t' * 5)

        self.parse_term()
        while True:
            line_number, lex, tok = self.get_symbol()
            if tok == 'add_op':
                self.row_number += 1
                self.print_not_final_token(line_number, lex, tok, indent='\t' * 5)
                self.parse_term()
            else:
                break
        return True

    def parse_term(self):
        print('\t' * 5, 'parse_term', sep='')
        self.parse_factor()
        while True:
            line_number, lex, tok = self.get_symbol()
            if tok in ('pow_op', 'mult_op'):
                self.row_number += 1
                self.print_not_final_token(line_number, lex, tok, indent='\t' * 6)
                self.parse_factor()
            else:
                break
        return True

    def parse_factor(self):
        print('\t' * 6, 'parse_factor', sep='')
        line_number, lex, tok = self.get_symbol()
        if tok in ('int', 'float', 'bool', 'ident', 'label'):
            self.row_number += 1
            self.print_not_final_token(line_number, lex, tok, indent='\t' * 7)
        elif lex == '(':
            self.row_number += 1
            self.parse_arithm_expression()
            self.parse_token(')', 'brackets_op', '\t' * 7)
            self.print_not_final_token(line_number, lex, tok, indent='\t' * 7)
        else:
            B2LangParser.fail_parse('not_expected', line_number, lex, tok,
                                 'rel_op, int, float, ident або \'(\' Expression \')\'')
        return True

    def parse_declaration(self):
        # Parse type
        print('\t' * 2, 'parse_declaration', sep='')
        line_number, lex, tok = self.get_symbol()
        self.row_number += 1
        if lex in ('int', 'float', 'bool', 'label') and tok == 'keyword':
            self.print_not_final_token(line_number, lex, tok, indent='\t' * 3)
            self.parse_var_list()
        else:
            B2LangParser.fail_parse('not_expected', line_number, lex, tok,
                                 'int, float або bool.')

    def parse_var_list(self):
        print('\t' * 3, 'parse_var_list', sep='')
        line_number, lex, tok = self.get_symbol()
        self.row_number += 1

        if tok == 'ident':
            self.print_not_final_token(line_number, lex, tok, indent='\t' * 5)

        else:
            B2LangParser.fail_parse('not_expected', line_number, lex, tok,
                                 "ідентифікатор (ident)")

        line_number, lex, tok = self.get_symbol()
        if lex == '=' and tok == 'assign_op':
            self.parse_assign()
            line_number, lex, tok = self.get_symbol()

        if lex == ',' and tok == 'comma':
            self.row_number += 1
            self.print_not_final_token(line_number, lex, tok, indent='\t' * 5)
            self.parse_var_list()

        elif lex == ';' and tok == 'op_end':
            return True

    def parse_if(self):
        print('\t' * 3, 'parse_if', sep='')
        self.parse_token('if', 'keyword', '\t' * 4)

        self.parse_expression(required=True)

        self.parse_token('goto', 'keyword', '\t' * 4)

    def parse_for(self):
        print('\t' * 3, 'parse_for', sep='')
        self.parse_token('for', 'keyword', '\t' * 4)
        self.parse_expression()
        self.parse_token('by', 'keyword', '\t' * 4)
        self.parse_expression()
        self.parse_token('to', 'keyword', '\t' * 4)
        self.parse_expression()
        self.parse_token('while', 'keyword', '\t' * 4)
        line_number, lex, tok = self.get_symbol()
        if lex == '(' and tok == 'brackets_op':
            self.row_number += 1
            self.parse_expression(required=True)
            self.parse_token(')', 'brackets_op', '\t' * 4)
            self.parse_statement()
        else:
            self.parse_statement()


    def parse_ind_expression(self):
        print('\t' * 4, 'parse_for', sep='')

        line_number, lex, tok = self.get_symbol()
        if tok == 'ident':
            self.row_number += 1
            self.print_not_final_token(line_number, lex, tok, indent='\t' * 3)
            self.parse_assign()
        else:
            B2LangParser.fail_parse('not_expected', line_number, lex, tok,
                                 "ідентифікатор (ident)")
        self.parse_token(';', 'op_end', '\t' * 5)
        self.parse_expression(required=True)
        self.parse_token(';', 'op_end', '\t' * 5)

        if tok == 'ident':
            self.row_number += 1
            self.print_not_final_token(line_number, lex, tok, indent='\t' * 3)
            self.parse_assign()
        else:
            B2LangParser.fail_parse('not_expected', line_number, lex, tok,
                                 "ідентифікатор (ident)")
