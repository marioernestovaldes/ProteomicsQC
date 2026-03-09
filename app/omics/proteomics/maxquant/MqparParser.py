import re


class MqparParser:
    """Parser for mqpar.xml files"""

    def __init__(self, filename=None, as_template=False):
        self._content = None

        if filename is not None:
            self.read(filename)

        if as_template:
            self.as_template()

    def read(self, filename):
        self._filename = filename
        with open(filename, "r") as file:
            self._content = "".join(file.readlines())
        return self

    def print(self):
        print(self._content)

    def as_template(self):
        new_content = self._content

        repls = {
            "<fastaFilePath>.*</fastaFilePath>": "<fastaFilePath>__FASTA__</fastaFilePath>",
            r"<string>[^<]*\.(?:raw|RAW)</string>": "<string>__RAW__</string>",
        }

        for pattern, repl in repls.items():
            new_content = re.sub(pattern, repl, new_content)

        new_content = re.sub(
            r"(<experiments>\s*<string>).*?(</string>\s*</experiments>)",
            r"\1__LABEL__\2",
            new_content,
            count=1,
            flags=re.DOTALL,
        )

        n_raws = len(re.findall("__RAW__", new_content))
        if n_raws > 1:
            raise AssertionError("Please use mqpar.xml for single RAW file.")
        self._content = new_content
        return self

    def write(self, filename=None):
        if filename is None:
            filename = self._filename
        with open(filename, "w") as file:
            file.write(self._content)
