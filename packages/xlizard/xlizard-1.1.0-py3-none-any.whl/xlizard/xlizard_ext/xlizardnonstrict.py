'''
This is an extension of xlizard. It use a non strict standard to count
the cyclomatic complexity number, where the boolean operators (
&&, ||, and, or, not, !) would be counted.
'''


class xlizardExtension(object):  # pylint: disable=R0903

    # pylint: disable=W0221
    def __call__(self, tokens, reader):
        reader.conditions -= set(['&&', '||', 'and', 'or'])
        return tokens
