import os
import re

''' 
    len('class="') is taken as the offset for class 
    len('href="') is taken as the offset for href
'''
START_INDEX_OFFSET_CLASS = 7
START_INDEX_OFFSET_HREF = 6


class Milder:
    def __init__(self, filename, source_filename=None, working_dir=None, source_dir=None):
        self.html_filename = filename
        self.source_filename = source_filename
        self.html_dir = working_dir
        self.css_dir = self.html_dir if source_dir is None else source_dir
        self.classes = []
        self.stylesheet_content = ''
        self.html_elements = []
        self.styles = ''

    @staticmethod
    def get_attribute_values(content: str, start_token: str, end_token: str, offset: int, keyword=None):
        attribute_values = []
        lines = content.splitlines()

        if keyword is None:
            keyword = start_token

        for (index, line) in enumerate(lines):
            if line.__contains__(keyword):
                start_index = line.find(start_token) + offset
                if start_index is not -1:
                    end_index = line.find(end_token, start_index)

                    if end_index is not -1:
                        value = line[start_index:end_index]
                        attribute_values.append(value)
                        continue

                    return f'closing " for {start_token} is not found at line no. {index + 1}'

        return attribute_values

    @staticmethod
    def __get_code_snippets(content: str, start_token: str, end_token: str):
        snippet = ''
        start_index = content.find(start_token)

        if start_index is not -1:
            end_token = content.find(end_token, start_index) + 1
            if end_token is not -1:
                snippet = content[start_index:end_token]
        return snippet

    @staticmethod
    def get_stylesheets(content):
        res = Milder.get_attribute_values(content, start_token='href="', end_token='"', offset=START_INDEX_OFFSET_HREF,
                                          keyword='stylesheet')
        print("stylesheets:", res)
        return res

    @staticmethod
    def get_file_content(filename: str = None, file_dir: str = None):

        if file_dir:
            filename = os.path.join(file_dir, filename)
            print(f"filename resolved to {filename}")

        with open(filename) as file:
            content = file.read()
        return content

    def __get_class_snippet(self, class_name, content):
        snippet = Milder.__get_code_snippets(content, start_token=class_name + " {", end_token="}")
        self.styles += snippet+"\n"
        return

    def get_html_elements(self, content: str):

        regex = re.compile(r'<[a-zA-Z][a-zA-z0-9]* ?', re.MULTILINE)
        lines = content.splitlines()

        for (index, line) in enumerate(lines):
            match = regex.search(line)

            if match:
                element = match.group().split('<')[1]
                self.html_elements.append(element)

        # print("self.html_elements:", self.html_elements)
        return

    def copy_classes_from_stylesheet(self):
        for _class in self.classes:
            self.__get_class_snippet(_class, self.stylesheet_content)

    def copy_html_elements_from_stylesheet(self):
        for element in self.html_elements:
            snippet = self.__get_code_snippets(content=self.stylesheet_content, start_token=element + "{",
                                               end_token="}")
            print(snippet)
            self.styles += snippet+"\n"

    def __get_individual_classes(self, res):
        for _class in res:
            classes_in_same_line = _class.split(" ")
            if len(classes_in_same_line) > 1:
                for temp_class in classes_in_same_line:
                    self.classes.append(temp_class)
                continue
            self.classes.append(_class)

    def create_individual_classes(self, res):
        self.__get_individual_classes(res)

    def get_classes(self, html_content):
        return self.get_attribute_values(html_content, start_token='class="', end_token='"',
                                         offset=START_INDEX_OFFSET_CLASS)

    def process(self):
        html_content = self.get_file_content(self.html_filename, self.html_dir)

        if len(html_content) <= START_INDEX_OFFSET_CLASS:
            return

        self.get_html_elements(html_content)
        classes = self.get_classes(html_content)

        '''
        if the instance of the classes is not a list, that implies that no classes are found in the html file
        '''

        if isinstance(classes, list):
            # to convert ["primary-text bg-gray title"] into ["primary-text", "bg-gray", "title"]

            self.create_individual_classes(classes)

            stylesheets = self.get_stylesheets(html_content)
            if len(stylesheets) > 0:
                for stylesheet in stylesheets:
                    abs_path = os.path.join(self.css_dir, stylesheet)

                    self.stylesheet_content = self.get_file_content(abs_path)
                    self.copy_html_elements_from_stylesheet()
                    self.copy_classes_from_stylesheet()

        return self.styles


if __name__ == "__main__":
    html_file = 'index.html'
    html_file_dir = os.path.join(os.getcwd(), "../input/")

    print(Milder(filename=html_file, working_dir=html_file_dir).process())
