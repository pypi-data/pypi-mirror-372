""" NOTE: spacy is not provided as a requirement for this library"""
import spacy
from spacy import displacy


class EntityDisplayer:

    def __init__(self, language="en") -> None:
        self.nlp = spacy.blank(language)

    def render_doc(self, text, matches_list):
        doc = self.nlp.tokenizer(text)
        doc_spans = []
        for match in matches_list:
            aux_span = doc.char_span(
                match[0],
                match[1],
                match[2],
                alignment_mode="expand")

            doc_spans.append(aux_span)
        doc.spans["sc"] = doc_spans
        displacy.render(doc, style="span", jupyter=True)
