from os.path import basename 
from .soup import Soup
from ..utils.logger import logger

class Ref:
    cli       = None
    raw:str   = ''
    soup:Soup = None
    _content  = None
    _bloked   = False

    def __init__(self, fpath , stg ):
        self.space    = stg.alias
        self.settings = stg
        self.fpath    = fpath
        self.basename = basename(fpath)

        parts         = self.basename.split(".")
        self.name     = parts[0]
        self.lang     = 'xml' if len(parts) == 1 else parts[-1]
        
        fallbacks = {
            'yml' : "yaml"
        }

        self.lang = fallbacks.get(self.lang,self.lang)

        # for non readable files
        self.just_copy = False
        try:
            with open(self.fpath, 'rb') as f:
                while chunk := f.read(4096):
                    chunk.decode('utf-8')
        except UnicodeDecodeError:
            self.just_copy = True

        self.log = logger('refs')
    
    @staticmethod
    def match( file:str , link:str ):
        bn = basename(file)
        np = bn.split('.')
        nm = np[0]
        if link == nm:
            return True
        en = "" if len(np) == 0 else np[-1]
        nm = file.strip(en)
        return '/' in link and nm.endswith(link)

    def __repr__( self ):
        return f"<ref link='{self.name}' />"

    def _compile(self):
        if self._content != None:
            return

        with open(self.fpath,'r') as f:
            self.raw = f.read()

        self.soup    = Soup( self.raw )
        self._bloked = True

        for t in self.soup.refs():
            self.log.info(t)
            space = t.get('space', self.settings.alias )
            name  = t.ref()

            ref   = self.settings.get_ref( space ,name )

            if ref is None:
                self.log.warning(f"{t} not found" )
                continue

            if ref is self:
                t.set_replace(ref.raw,ref.lang)
                continue

            t.set_replace(ref.content,ref.lang)

         
        self._content = self.soup.to_string()
        self._bloked  = False

    @property
    def content(self):
        if self._bloked:
            soup = Soup(self.raw)
            for t in soup.refs():
                t.set_replace('')
            return soup.to_string()
        self._compile()
        return self._content
