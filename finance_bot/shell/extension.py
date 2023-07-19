from IPython.core.magic import magics_class, Magics, line_magic


@magics_class
class FinanceBotMagics(Magics):

    @line_magic
    def hello(self, line):
        return line


def load_ipython_extension(ipython):
    ipython.register_magics(FinanceBotMagics)
