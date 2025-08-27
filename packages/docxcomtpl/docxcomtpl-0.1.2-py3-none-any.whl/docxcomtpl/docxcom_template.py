# coding=utf-8
import os.path
import sys
from typing import Dict, Any, Callable
from docxtpl import DocxTemplate, InlineImage, RichText, RichTextParagraph
__all__=["DocxComTemplate"]

class DocxComTemplate:
    """Version of the DocxTemplate generator that supports COM-based postprocessing"""
    PLACEHODER_TEMPLATE = "EIWOSCVY{:05d}HFBJSYXO"
    PLACEHOLDER_WORD_SEARCH_PATTERN = "EIWOSCVY[0-9]{5}HFBJSYXO"

    def __init__(self, docx_file):
        self._base_template = DocxTemplate(docx_file)
        self.insert_counter = 0

    def _prepare_data(self, data):
        """Data can contain string values, lists and inserters.
        Base template engine supports only basic values, and
        """
        placeholder2inserter = {}
        def new_placeholder():
            self.insert_counter += 1
            return self.PLACEHODER_TEMPLATE.format(self.insert_counter)

        def walk_data(data): #type: (Any)->Any
            if isinstance(data, (str, RichText, RichTextParagraph, InlineImage)):
                return data

            elif callable(data):
                # store the inserter
                placeholder = new_placeholder()
                placeholder2inserter[placeholder] = data
                return placeholder
            elif isinstance(data, list):
                return [walk_data(item) for item in data]
            elif isinstance(data, dict):
                prepared = {}
                for key, value in data.items():
                    prepared[key] = walk_data(value)
                return prepared
            else:
                return data
        return walk_data(data), placeholder2inserter

    def generate(self, data:Dict[str, Any], output:str, postprocess=None, jinja_env=None):
        """Generate the DOCX file from the template and data.
        Additional COM-based post-processing can be done.
        :param data: Data to fill the template. A dictionary with string keys and values can be strings, lists, or inserter functions
        :param output: Output file path for the generated DOCX
        :param postprocess: Optional post-processing function that takes the opened Word document as an argument.
        """
        prepared_data, inserters = self._prepare_data(data)
        self._base_template.render(prepared_data, jinja_env=jinja_env)
        self._base_template.save(output)
        if inserters or postprocess:
            self._run_inserters(output, inserters, postprocess)

    def _run_inserters(self, docx_file, placeholder2inserter, postprocess):
        """Run inserters in the DOCX file"""
        # Initialize the Word Application
        import win32com.client
        word = win32com.client.Dispatch("Word.Application")
        doc = None

        def find_placeholder_in_range(range_obj):
            placeholders_with_ranges = []
            find = range_obj.Find
            find.ClearFormatting()
            find.Text = self.PLACEHOLDER_WORD_SEARCH_PATTERN
            #accept wildcards
            find.MatchWildcards = True
            while True:
                if not find.Execute():
                    break
                found_range = find.Parent.Duplicate
                matched_text = str(found_range.Text)
                placeholders_with_ranges.append((matched_text, found_range))
            return placeholders_with_ranges

        def find_and_process_markers(range_getter):
            #we need getter because for document it is doc.Range(), for headers and footers it is header.Range
            range_obj = range_getter()
            assert not isinstance(range_obj, str)
            #let's do it in 2 passes.
            # Pass 1
            #First, we find all placeholders and hold Ranges for them in a list
            placeholders_with_ranges = find_placeholder_in_range(range_obj)
            # Pass 2
            for matched_text, found_range in placeholders_with_ranges[::-1]:
                try:
                    inserter = placeholder2inserter.get(matched_text)
                    if inserter is not None:
                        inserter(found_range)
                    else:
                        pass
                except Exception as err:
                    print("Error running inserter:", err, file=sys.stderr)
                self.insert_counter += 1
            #pass 3: remove all placeholders, if they are still there
            range_obj = range_getter()
            placeholders_with_ranges = find_placeholder_in_range(range_obj)
            #remove all found ranges
            for matched_text, found_range in placeholders_with_ranges[::-1]:
                try:
                    found_range.Delete()
                except Exception as err:
                    print("Error replacing placeholder:", err, file=sys.stderr)

        try:
            word.Visible = False
            # Open the DOCX file
            word.DisplayAlerts = 0
            word.ScreenUpdating = False
            doc = word.Documents.Open(os.path.abspath(docx_file)) #need to take absolute path, because Word might have different idea about the current folder
            # Search for the marker string
            # Search for the marker string in headers and footers
            if placeholder2inserter:
                for section in doc.Sections:
                    find_and_process_markers(lambda : section.Range)
                    for header in section.Headers:
                        find_and_process_markers(lambda : header.Range)
                    for footer in section.Footers:
                        find_and_process_markers(lambda : footer.Range)
            if postprocess is not None:
                postprocess(doc)

        finally:
            word.ScreenUpdating = True
            if doc is not None:
                doc.Close(SaveChanges=True)
            # Quit Word
            word.Quit()


