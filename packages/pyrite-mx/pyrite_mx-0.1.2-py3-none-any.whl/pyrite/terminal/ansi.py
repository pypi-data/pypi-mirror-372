import re

class AnsiEscapeParser:
    pattern = re.compile(r"""
    (
        \x1b(?:
            (?P<CSI>\[[\x30-\x3F]*[\x20-\x2F]*[\x40-\x7E])   #CSI
            |
            (?P<OSC>\][^\x07\x9C]*(?:[\x07\x9C]|\x1b\x5C))   #OSC
            |
            (?P<Fs>[\x60-\x7E])                              #Fs
            |
            (?P<Fp>[\x30-\x3F])                              #Fp
            |                               
            (?P<nF>[\x20-\x2F]*[\x30-\x7E])                  #nF
            |
            (?P<partial>.*$)                                 #unterminated ESC
        )
        |
        (?P<text>[^\x1b]+)                                   #normal text
    )
    """, re.VERBOSE)
    def __init__(self):
        self.sequence_order = 0
        self.pending_text = ''
        self.last_item = None
        pass
    def parse(self, text):
        all_text = self.pending_text + text
        self.pending_text = ''
        pending_text = ''
        for i, match in enumerate(self.pattern.finditer(all_text), self.sequence_order+1):
            token = match.group()
            kind = tuple([k for k,v in match.groupdict().items() if v is not None])            
            if 'text' in kind:
                token = pending_text + token
                pending_text = ''
                if token != '' and self.last_item is not None:
                    if token=='\r\n' and self.last_item[2]=='\x1b[K':
                        self.last_item = (i,kind,token)
                        continue
                    if 'CSI' in self.last_item[1] and self.last_item[2].endswith(';1H'):
                        token = '\r\n' + token
                if token.endswith('\r'):
                    pending_text = '\r'
                    token = token[:-1]            
            self.last_item = (i,kind,token)
            yield self.last_item
        self.pending_text = pending_text
        if match.groupdict()['partial'] is not None:
            self.pending_text += token
            self.sequence_order = i - 1
        else:
            self.sequence_order = i  
    def reset(self):
        self.sequence_order = 0
        self.pending_text = ''
        self.last_item = None
        pass
