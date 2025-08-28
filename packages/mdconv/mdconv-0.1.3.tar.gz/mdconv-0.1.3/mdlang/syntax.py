from typing import Literal, Callable
from typing_extensions import Self

# Both Markdown(MD) and HTML: Rendered Output same
# Only HTML or Only Markdown: to avoid vague in different parent section format

# Headings
def Title1(word:str) -> str:
    return title_k(word,1)
def Title2(word:str) -> str:
    return title_k(word,2)
def Title3(word:str) -> str:
    return title_k(word,3)
def Title4(word:str) -> str:
    return title_k(word,4)
def Title5(word:str) -> str:
    return title_k(word,5)
def Title6(word:str) -> str:
    return title_k(word,6)
def title_k(word:str, k:int) -> str:
    if k<=0 or k>6:
        raise SyntaxException('Title Level 1~6', 400001)
    return f'{"#"*k} {word}'
def Header1(word:str) -> str:
    return header_k(word,1)
def Header2(word:str) -> str:
    return header_k(word,2)
def Header3(word:str) -> str:
    return header_k(word,3)
def Header4(word:str) -> str:
    return header_k(word,4)
def Header5(word:str) -> str:
    return header_k(word,5)
def Header6(word:str) -> str:
    return header_k(word,6)
def header_k(word:str, k:int) -> str:
    if k<=0 or k>6:
        raise SyntaxException('Headings Level 1~6', 400002)
    return format_word(word, (f'<h{k}>', f'</h{k}>'))

# Styling text, Emphasis # Only HTML
def Bold(word:str) -> str:
    # return f'**{word}**' # MD
    return format_word(word, ('<strong>','</strong>'))
def Italic(word:str) -> str:
    # return f'*{word}*' # MD
    return format_word(word, ('<em>','</em>'))
def Strikethrough(word:str) -> str:
    return format_word(word, ('~~','~~'))
def Subscript(word:str) -> str:
    return format_word(word, ('<sub>','</sub>'))
def Superscipt(word:str) -> str:
    return format_word(word, ('<sup>','</sup>'))
def Underline(word:str) -> str:
    # return f'<ins>{word}</ins>' OR
    return format_word(word, ('<u>','</u>'))

# Blockquotes
def Blockquotes(word:str) -> str:
    return f'> {word}'

# Quoting code
def Code(word:str) -> str:
    return format_word(word, ('`','`'))

# Links, Relative links
def Href_html(word:str, url:str):
    return f'<a href="{url}">{word}</a>'
def Href_plain(word:str,url:str):
    return f'[{word}]({url})'
def Image(word:str, url:str):
    return f'![{word}]({url})'
def URL_or_Email(word:str) -> str:
    return format_word(word, ('<','>'))
def format_word(word:str, pair:tuple[str,str]) -> str:
    if len(word)==0:
        return word
    return f'{pair[0]}{word}{pair[1]}' if not (word.startswith(pair[0]) and word.endswith(pair[1])) else word
def LinkedImage(image_desc:str,image_url:str,link_url:str) -> str:
    return Href_plain(Image(image_desc, image_url), link_url)

# Section links (current markdown page)
# Custom anchors
def SectionLink(word:str, section_url:str) -> str:
    # return f'<a name="{section_url}">{word}</a>' # HTML
    return f'[{word}](#{section_url})'

# Lists
def OrderedLists(words:list[str]) -> str:
    # MD
    orderls=''
    for idx,word in enumerate(words):
        orderls += f'{idx}. {word}\n'
    return f'{orderls}'
    # HTML
    # orderls=''
    # for word in words:
    #     orderls += f'<li>{word}</li>\n'
    # return f'<ol>\n{orderls}</ol>'

def UnorderedLists(words:list[str]) -> str:
    # MD
    orderls=''
    for word in words:
        orderls += f'- {word}\n'
    return f'{orderls}'
    # HTML
    # orderls=''
    # for word in words:
    #     orderls += f'<li>{word}</li>\n'
    # return f'<ul>\n{orderls}</ul>'

def TaskLists(words:list[tuple[str, bool]]) -> str:
    tasks=''
    for line in words:
        tasks += (('- [x] ' if line[1] else '- [ ] ') + line[0]) + '\n'
    return tasks

# Paragraphs
def Paragraphs(word:str) -> str:
    # return format_word(word, ('<p>','</p>')) # HTML
    return word # MD

# Line Breaks
paragraph_line_breaks=[
    '\n',   # txt mode
    '<br>', # inner html
    '<br/>',# inner html v2
]

# Footnotes
def Footnotes_ref(th:int) -> str:
    return f'[^{th}]'
def Footnotes_def(th:int, word:str) -> str:
    return f'[^{th}]: {word}'

# Alerts
def NoteFrame(words:list[str]) -> str:
    return notice_frame(words, 'NOTE')
def TipFrame(words:list[str]) -> str:
    return notice_frame(words, 'TIP')
def ImportantFrame(words:list[str]) -> str:
    return notice_frame(words, 'IMPORTANT')
def WarningFrame(words:list[str]) -> str:
    return notice_frame(words, 'WARNING')
def CautionFrame(words:list[str]) -> str:
    return notice_frame(words, 'CAUTION')
def notice_frame(words:list[str], notice_type:Literal['NOTE','TIP','IMPORTANT','WARNING','CAUTION']) -> str:
    return f'> [!{notice_type}]\n> ' + '\n> '.join(words) + '\n'

def MathFormula(word:str) -> str:
    return f'$$\n{word}\n$$'

def InlineMathFormula(word:str) -> str:
    return f'$\n{word}\n$'

def CodeBlock(word:str, lang:str='') -> str:
    return f'```{lang}\n{word}\n```'

def Horizontalline() -> str:
    return '------'

def Catalog() -> str:
    return '[TOC]\n'

def Comment(word:str) -> str:
    return format_word(word, ('<!--','-->'))

def HTML_Video(url:str) -> str:
    return f'<video src="{url}" />'

def HTML_Audio(url:str) -> str:
    return f'<audio src="{url}" />'

def HTML_RawCode(raw_code:str) -> str:
    return raw_code

characters_escapes=["\\","`","*","_","{", "}","[", "]","<", ">","(", ")","#","+","-",".","!","|"]

columnalign=Literal['<','^','>']
class Sheet():
    sheet:list[list[str]]
    rowhdr:list[str]|None
    linehdr:list[str]|None
    cell00:str|None
    align:list[columnalign]|None
    hdrhll:bool

    def __init__(self, 
                 sheet:list[list[str]], 
                 rowhdr:list[str]|None=None, 
                 linehdr:list[str]|None=None, 
                 cell00:str|None=None,
                 align:list[columnalign]|None=None,
                 hdrhll:bool=True,
                ):
        # clean
        # c0 r0 r1 r2 r3 r4
        # -  -  -  -  -  -
        # l0 $0 $1 $2 $3 $4
        # l1 $0 $1 $2 '' ''
        # l2 $0 $1 $2 $3 ''
        # l3 $0 $1 '' '' ''
        maxcol=max([len(row) for row in sheet])
        for row in sheet:
            row.extend(['']*(maxcol-len(row)))
        if rowhdr:
            if len(rowhdr) < maxcol:
                rowhdr.extend(['']*(maxcol-len(rowhdr)))
            elif len(rowhdr) > maxcol:
                rowhdr = rowhdr[:maxcol]
        if linehdr:
            maxcol+=1
            if cell00==None:
                cell00=''
            if len(linehdr) < len(sheet):
                linehdr.extend(['']*(len(sheet)-len(linehdr)))
            elif len(linehdr) > len(sheet):
                linehdr = linehdr[:len(sheet)]
        alignsz=len(align) if align else 0
        if not align or alignsz==0:
            align=['<' for _ in range(maxcol)]
        elif alignsz < maxcol:
            for _ in range(maxcol-alignsz):
                align.append(align[alignsz-1])
        
        # assign
        self.sheet= sheet
        self.rowhdr= rowhdr
        self.linehdr= linehdr
        self.cell00= cell00
        self.align= align
        self.hdrhll= hdrhll

    def __str__(self) -> str:
        if self.hdrhll:
            if self.rowhdr:
                self.rowhdr = [Bold(cell) for cell in self.rowhdr]
            if self.linehdr:
                self.linehdr = [Bold(cell) for cell in self.linehdr]
            if self.cell00 != None:
                self.cell00 = Bold(self.cell00)
        grid:list[list[str]]=[]
        
        rowcnt=len(self.sheet) + (1 if self.rowhdr else 0)
        linecnt=max([len(row) for row in self.sheet]) + (1 if self.linehdr else 0)
        if self.rowhdr:
            grid.append(([self.cell00]+self.rowhdr) if self.cell00 != None and self.linehdr else self.rowhdr)
        for rowidx, row in enumerate(self.sheet):
            grid.append(([self.linehdr[rowidx]]+row) if self.linehdr else row)
        grid.insert(1, ['-']*(linecnt))
        
        linecell_maxsz=[0]*linecnt
        for j in range(linecnt):
            for i in range(rowcnt):
                linecell_maxsz[j] = max(linecell_maxsz[j], len(grid[i][j]))

        restable:list[str]=[]
        for i,row in enumerate(grid):
            resv=''
            for j,cell in enumerate(row):
                alignchar=self.align[j] if self.align else '<'
                resv+= (f'{cell:{alignchar}{linecell_maxsz[j]}}')+(' | ' if j<linecnt-1 else '')
            restable.append(f'| {resv} |')
        return '\n'.join(restable)

    def __repr__(self) -> str:
        return str(self)

    def insert_row_above(self, rowidx:int, rowadd:list[str]) -> Self:
        self.sheet.insert(rowidx, rowadd)
        return self
    
    # def insert_row_below(self, rowidx:int, rowadd:list[str]) -> Self:
    #     stsz=len(self.sheet)
    #     if stsz==0:
    #         self.sheet.append(rowadd)
    #         return self
        
    #     rowidx = (stsz+rowidx)%stsz
    #     if 0 <= rowidx < stsz-1:
    #         self.sheet.insert(rowidx+1, rowadd)
    #     elif rowidx == stsz-1:
    #         self.sheet.append(rowadd)
    #     else:
    #         raise IndexError()
    #     return self
    
    # def insert_line_left(self, lineidx:int, lineadd:list[str]) -> Self:
    #     return self
    
    # def insert_line_right(self, lineidx:int, lineadd:list[str]) -> Self:
    #     return self
    
    # def move_row_above(self, rowidx:int, cnt:int=1) -> Self:
    #     return self
    
    # def move_row_below(self, rowidx:int, cnt:int=1) -> Self:
    #     return self
    
    # def move_line_left(self, lineidx:int, cnt:int=1) -> Self:
    #     return self
    
    # def move_line_right(self, lineidx:int, cnt:int=1) -> Self:
    #     return self
    
    def del_row(self, rowidx:int) -> Self:
        self.sheet.pop(rowidx)
        return self
    
    # def del_line(self, lineidx:int) -> Self:
    #     for row in self.sheet:
    #         row.pop(lineidx)
    #     return self
    
    def copy(self) -> 'Sheet':
        return Sheet(
            sheet=[row.copy() for row in self.sheet], 
            rowhdr=self.rowhdr.copy() if self.rowhdr else None,
            linehdr=self.linehdr.copy() if self.linehdr else None,
            cell00=self.cell00,
            align=self.align.copy() if self.align else None,
            hdrhll=self.hdrhll,
        )

class SyntaxException(Exception):
    def __init__(self, message:str, error_code:int) -> None:
        super().__init__(message)
        self.error_code=error_code

mdtype:dict[str, Callable]={
    'Title1': Title1, 'Header1': Header1,
    'Title2': Title2, 'Header2': Header2,
    'Title3': Title3, 'Header3': Header3,
    'Title4': Title4, 'Header4': Header4,
    'Title5': Title5, 'Header5': Header5,
    'Title6': Title6, 'Header6': Header6,
    'Paragraph': Paragraphs, 'Paragraphs': Paragraphs,
    'Sheet': Sheet.__str__,
    'MathFormula': MathFormula,
    'CodeBlock': CodeBlock,
    'NoteFrame': NoteFrame,
    'TipFrame': TipFrame,
    'ImportantFrame': ImportantFrame,
    'WarningFrame': WarningFrame,
    'CautionFrame': CautionFrame,
    'Quote': Blockquotes, 'Blockquotes': Blockquotes,
    'OrderList': OrderedLists, 'OrderedLists': OrderedLists,
    'UnorderList': UnorderedLists, 'UnorderedLists': UnorderedLists,
    'TaskList': TaskLists, 'TaskLists': TaskLists,
    'Horizontalline': Horizontalline,
    'Catalog': Catalog,
    'Bold': Bold,
    'Italic': Italic,
    'Underline': Underline,
    'Code': Code,
    'DeleteLine': Strikethrough, 'Strikethrough': Strikethrough,
    'Comment': Comment,
    'Href': Href_plain,
    'Image': Image,
    'URL': URL_or_Email, 'Email': URL_or_Email,
    'Subscript': Subscript, 
    'Superscipt': Superscipt,
    'SectionLink': SectionLink, 'CustomAnchors': SectionLink,
    'Footnotes_ref': Footnotes_ref,
    'Footnotes_def': Footnotes_def,
    'LinkedImage': LinkedImage,
}