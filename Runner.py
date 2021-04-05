from lexer.B2LangLexer import B2LangLexer
from B2LangParser import B2LangParser


def main():
    with open('temp_test.b2lang', 'r') as f:
        source_code = f.read()
        lexer = B2LangLexer(source_code)
        lexer.start()
        lexer.print_symbols_table()
        print(f"\n{lexer.table_of_symb}\n")
        if not lexer.success[0]:
            return False

        parser = B2LangParser(lexer.table_of_symb)
        parser.run()


if __name__ == '__main__':
    main()
