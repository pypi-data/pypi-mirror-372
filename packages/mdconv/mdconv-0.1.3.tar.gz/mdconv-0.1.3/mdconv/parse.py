from mdlang.syntax import mdtype,Sheet

from typing import Any

mdtype_str=str
mdtype_obj=dict
mdtype_text=mdtype_obj|mdtype_str
mdtype_list=list

def explain_text(text: mdtype_text) -> str:
    if type(text)==mdtype_str:
        return text
    
    elif type(text)==mdtype_obj:
        texttype = str(must_field(text, 'type'))
        match texttype:
            # recursive list
            case 'list':
                textlist=must_field(text, 'list')
                linebreak=str(text.get('line_break', '\n'))
                return linebreak.join(explain_list(textlist))

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
                textword=must_field(text, 'word')
                must_types('word', textword, [str,dict])
                return mdtype[texttype](explain_text(textword))

            # arg(words:list[str|obj])
            case 'NoteFrame'|'TipFrame'|'ImportantFrame'|'WarningFrame'|'CautionFrame'|\
                'OrderList'|'OrderedLists'|'UnorderList'|'UnorderedLists':
                textwords=must_field(text, 'words')
                must_types('words', textwords, [list])
                return mdtype[texttype](explain_list(textwords))

            case 'Sheet':
                textobject=dict(must_field(text, 'object'))
                sheetof=list[list](must_field(textobject, 'sheet'))
                return mdtype[texttype](Sheet(
                    sheet=[
                        explain_list(row)
                        for row in sheetof
                    ],
                    rowhdr=explain_list(textobject['rowhdr']) if 'rowhdr' in textobject else None,
                    linehdr=explain_list(textobject['linehdr']) if 'linehdr' in textobject else None,
                    cell00=textobject.get('cell00', None),
                    align=textobject.get('align', None),
                    hdrhll=textobject.get('hdrhll', False),
                ))

            case 'CodeBlock':
                textword=must_field(text, 'word')
                return mdtype[texttype](
                    explain_text(textword), text.get('lang', ''),
                )

            case 'TaskList':
                textwords=must_field(text, 'words')
                return mdtype[texttype](textwords)

            case 'Href'|'Image'|'SectionLink'|'CustomAnchors':
                must_fields(text, ['word', 'url'])
                return mdtype[texttype](explain_text(text['word']), text['url'])

            case 'Footnotes_ref':
                must_field(text, 'th')
                return mdtype[texttype](text['th'])
            case 'Footnotes_def':
                must_fields(text, ['th', 'word'])
                return mdtype[texttype](text['th'], text['word'])

            case 'LinkedImage':
                textword=must_field(text, 'word')
                must_fields(textword, ['image_desc', 'image_url', 'link_url'])
                return mdtype[texttype](textword['image_desc'], textword['image_url'], textword['link_url'])

            case _:
                raise JSONException(f'unsupport "type": {text["type"]}', 400102)
    else:
        return 'text ERROR'

def explain_list(texts: mdtype_list) -> list[str]:
    return [ explain_text(text) for text in texts ]

def must_fields(obj: mdtype_obj, fields: list[str]):
    for field in fields:
        must_field(obj, field)
def must_field(obj: mdtype_obj, field: str) -> Any:
    if field not in obj:
        raise JSONException(f'field "{field}" not in JSONObject', 400101)
    return obj.get(field, None)
def must_types(key: str, val: Any, typelist: list[type]):
    if type(val) not in typelist:
        raise JSONException(f'key "{key}" type not in {typelist}', 400104)
def must_type(key:str, val:Any, typeof: type):
    if type(val) != typeof:
        raise JSONException(f'key "{key}" type != {typeof}', 400103)

def explain_json(jsonobj: mdtype_list|mdtype_text) -> str:
    if type(jsonobj) == mdtype_list:
        return '\n\n'.join(explain_list(jsonobj))
    elif type(jsonobj) == mdtype_obj:
        return explain_text(jsonobj)
    elif type(jsonobj) == mdtype_str:
        return jsonobj
    return "json ERROR"

class JSONException(Exception):
    def __init__(self, message:str, error_code:int) -> None:
        super().__init__(message)
        self.error_code=error_code
        