from lang.syntax import mdtype,Sheet

from typing import Any

def text2md(text:dict[str,Any]) -> str:
    check_field(text, 'type')
    texttype=str(text['type'])
    match texttype:
        # arg(None)
        case 'Horizontalline'|'Catalog':
            return mdtype[texttype]()

        # arg(word:str|obj)
        case 'Title1'|'Title2'|'Title3'|'Title4'|'Title5'|'Title6'|\
            'Header1'|'Header2'|'Header3'|'Header4'|'Header5'|'Header6'|\
            'Paragraph'|'Paragraphs'|\
            'MathFormula'|'Quote'|'Blockquotes'|\
            'Bold'|'Italic'|'Underline'|'Code'|'DeleteLine'|'Strikethrough'|'Comment'|\
            'URL'|'Email'|'Subscript'|'Superscipt':
            check_field(text, 'word')
            textword=text['word']
            check_type('word', textword, [str,dict])
            return mdtype[texttype](trans_word(textword))
        
        # arg(words:list[str|obj])
        case 'NoteFrame'|'TipFrame'|'ImportantFrame'|'WarningFrame'|'CautionFrame'|\
            'OrderList'|'OrderedLists'|'UnorderList'|'UnorderedLists':
            check_field(text, 'words')
            textwords=text['words']
            check_type('words', textwords, [list])
            textwords=[trans_word(textword) for textword in textwords]
            return mdtype[texttype](textwords)
        
        case 'Sheet':
            check_field(text, 'object')
            textobject=text['object']
            check_field(textobject, 'sheet')
            return mdtype[texttype](Sheet(
                sheet=textobject['sheet'],
                rowhdr=textobject['rowhdr'] if 'rowhdr' in textobject else None,
                linehdr=textobject['linehdr'] if 'linehdr' in textobject else None,
                cell00=textobject['cell00'] if 'cell00' in textobject else None,
                align=textobject['align'] if 'align' in textobject else None,
                hdrhll=textobject['hdrhll'] if 'hdrhll' in textobject else False,
            ))
        
        case 'CodeBlock':
            check_field(text, 'word')
            return mdtype[texttype](
                trans_word(text['word']), text['lang'] if 'lang' in text else '',
            )
        
        case 'TaskList':
            check_field(text, 'words')
            return mdtype[texttype](text['words'])

        case 'Href'|'Image'|'SectionLink'|'CustomAnchors':
            check_field(text, 'word');check_field(text, 'url')
            return mdtype[texttype](trans_word(text['word']), text['url'])

        case 'Footnotes_ref':
            check_field(text, 'th')
            return mdtype[texttype](text['th'])
        case 'Footnotes_def':
            check_field(text, 'th');check_field(text, 'word')
            return mdtype[texttype](text['th'], text['word'])
        case _:
            raise JSONException(f'unsupport "type": {text["type"]}', 400102)

def check_field(obj:dict[str,Any], field:str):
    if field not in obj:
        raise JSONException(f'field "{field}" not in JSONObject', 400101)
def check_type(key:str,val:Any,typelist:list[type]):
    if type(val) not in typelist:
        raise JSONException(f'key "{key}" type not in {typelist}', 400103)
def trans_word(word:str|dict[str,Any]) -> str:
    if type(word)==str:
        return word
    elif type(word)==dict:
        return text2md(word)
    return 'ERROR'
        


def json2md(texts:list[dict[str,Any]]) -> list[str]:
    return [
        text2md(text)
        for text in texts
    ]

class JSONException(Exception):
    def __init__(self, message:str, error_code:int) -> None:
        super().__init__(message)
        self.error_code=error_code
        