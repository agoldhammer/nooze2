from textwrap import TextWrapper

wrapper = TextWrapper(width=60, initial_indent="+====>", subsequent_indent="       ")


def _ptWrite(text):
    print(wrapper.fill(text))
    print("__________")


def printStatus(status):
    _ptWrite(
        "\n<{}> [{} {}] doc: {}".format(
            status["author"], status["created_at"], status["source"], status["text"]
        )
    )


def printMatches(cursor):
    """
    """
    for status in cursor:
        printStatus(status)
    print("")
