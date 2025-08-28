from os.path import (
    exists,
    join,
    dirname,
    splitext,
    relpath,
    isdir
)
import configparser, json
from functools import lru_cache
from pathlib import Path

from .compiler import Ref
from .models.schedules import Schedule
from .models.contacts import Contact
from .gits.module import GitModule
from .utils import system, get_yaml, get_json, walker, walker_up


class Settings:
    # dev utils
    debug = False

    # if path provided leads to a repo upstream
    is_repo      : bool = False
    is_module    : bool = False
    is_ymvas     : bool = False # if repos if fetched from ymvas
    is_main      : bool = False # if repo is main git@ymvas.com/vas/vas.git

    # paths
    root         : str  = None # /root             -> folder of the repo
    git          : str  = None # /root/.git        -> folder , if module -> /root/../../.git
    hooks        : str  = None # /root/.git/hooks  -> folder , if module -> /root/../../.git/hooks
    ymvas        : str  = None # /root/.ymvas      -> folder

    # repo info
    url          : str  = None # example  -> git@ymvas.com/vas/ymvas.git
    name         : str  = None # from url -> ymvas
    user         : str  = None # from url -> vas
    alias        : str  = None # from url -> vas/ymvas

    # ymvas important folders
    d_references : str = None
    d_commands   : str = None
    d_settings   : str = None
    d_tasks      : str = None
    d_schedules  : str = None
    d_secrets    : str = None
    d_finance    : str = None
    d_hooks      : str = None
    d_endpoints  : str = None
    d_documents  : str = None
    d_contacts   : str = None
    d_spaces     : str = None

    # where are we going to complie the endpointss
    d_compile_prefix : str = None

    # submodules asociated
    modules: dict = {}

    # ymvas important files
    f_settings            : str = None
    f_settings_endpoints  : str = None
    f_settings_references : str = None
    f_settings_secrets    : str = None
    f_settings_tasks      : str = None
    f_settings_finance    : str = None
    f_settings_hooks      : str = None


    # private
    __references  = {}
    

    # init
    def __init__( self , pwd ):
        root, is_repo = Settings._find_repo_root(pwd)
     
        self.root = root
        if is_repo:
            self._setup_repo_paths()

        self.is_repo = is_repo
        

        if self.is_main:
            system.setup_global_config(**{
                "global-src"      : self.root,
                "global-commands" : self.d_commands
            })
        else:
            system.setup_global_config()

      
    # git command helpers
    @property
    def _git(self):
        return f"git --git-dir='{self.git}' --work-tree='{self.root}' "

    @property
    @lru_cache(maxsize=None)
    def is_server(self):
        return system.get_global_config().get( 'is-ymvas', False )

    @staticmethod
    def _find_repo_root(pwd):

        for p in walker_up(pwd):
            ymf = join(p,'.ymvas')
            git = join(p,'.git')

            if not exists(ymf) and exists(git):
                return p, False

            if exists(ymf):
                return p, True

        return pwd, False


    def _setup_repo_paths( self ):
        _git      = join( self.root , '.git' )
        is_module = not isdir( _git )

        if not exists(_git):
            return

        if is_module:
            with open( _git ,'r' ) as f:
                _git = Path(f.read().split("gitdir:")[1].strip())
                _git = str(Path( self.root ) / _git )

        self.git       = _git
        self.hooks     = join(_git,'hooks')
        self.is_module = is_module

        ######### config #########
        cnf = configparser.ConfigParser()
        cnf.read(join( _git , 'config' ))

        _url = None
        for section in cnf.sections():
            if 'origin' in section and 'remote':
                _url = cnf[section].get('url',None)
                break


        user, name, is_ymvas = system.git_url_parse(_url)

        self.is_ymvas = is_ymvas
        self.user     = user
        self.name     = name
        self.url      = _url

        self.is_main = user == name
        self.alias   = f'{name}'
        if user is not None:
            self.alias = f'{user}/{name}'

        # /repo/.ymvas folders
        self.ymvas = join(self.root, '.ymvas' )

        self.d_references = join( self.ymvas, 'references' )
        self.d_commands   = join( self.ymvas, 'commands'   )
        self.d_settings   = join( self.ymvas, 'settings'   )
        self.d_tasks      = join( self.ymvas, 'tasks'      )
        self.d_schedules  = join( self.ymvas, 'schedules'  )
        self.d_secrets    = join( self.ymvas, 'secrets'    )
        self.d_finance    = join( self.ymvas, 'finance'    )
        self.d_hooks      = join( self.ymvas, 'hooks'      )
        self.d_endpoints  = join( self.ymvas, 'endpoints'  )

        # /repo folders if account
        if self.is_main:
            self.d_endpoints = join(self.root, 'endpoints' )
            self.d_documents = join(self.root, 'documents' )
            self.d_contacts  = join(self.root, 'contacts'  )
            self.d_finance   = join(self.root, 'finance'   )
            self.d_spaces    = join(self.root, 'spaces'    )

        # ymvas endpoints paths
        self.d_compile_prefix = self.alias
        if self.is_main:
            self.d_compile_prefix = user

        self.modules   = self.get_modules()

        # sttings files
        self.f_settings            = join(self.d_settings, 'settings.yaml'   )
        self.f_settings_endpoints  = join(self.d_settings, 'endpoints.yaml'  )
        self.f_settings_references = join(self.d_settings, 'references.yaml' )
        self.f_settings_secrets    = join(self.d_settings, 'secrets.yaml'    )
        self.f_settings_tasks      = join(self.d_settings, 'tasks.yaml'      )
        self.f_settings_finance    = join(self.d_settings, 'finance.yaml'    )
        self.f_settings_hooks      = join(self.d_settings, 'hooks.yaml'      )
        self.f_settings_schedules  = join(self.d_settings, 'schedules.yaml'  )

    @lru_cache(maxsize=None)
    def relpath(self,path):
        return relpath(path,self.root)

    def refs(self, src = None):
        _dir = self.d_references

        if src is not None:
            _dir = join(self.d_references,src)

        for ff in walker(_dir):
            yield Ref(join(ff), self)

    def get_ref(self,space:str,fragment:str) -> Ref:
        _exists = self.__references.get(space,{}).get(fragment,None)

        if _exists:
            return _exists

        # get refs only for active or in scope of user
        module = self.get_modules().get(space,{})
        m_path = join(module.path , '.ymvas', 'references' )

        if not module.path or not module.active:
            return

        if not exists(m_path):
            return

        for ff in walker( m_path ):
            if not Ref.match(ff,fragment):
                continue
            r = Ref( ff , self )
            # store for later use
            if space not in self.__references:
                self.__references[space] = {fragment:r}
            else:
                self.__references[space][fragment] = r
            return r

        pass

    
    def schedules(self):
        for ff in walker( self.d_schedules ):
            schedule = Schedule(ff)
            if not schedule.active:
                continue
            yield schedule

        if not self.is_main:
            return 

        for ff in walker( self.d_contacts ):
            contact = Contact(ff)
            if contact.birthdate is None:
                continue
            yield contact.schedule()

    @lru_cache(maxsize=None)
    def get_modules(self):
        file = join( self.root , '.gitmodules' )

        if self.is_module:
            modules = join(".git","modules")
            fragment = modules + self.git.split(modules)[-1]
            main_path = self.git.replace(fragment,"")
            main_settings = Settings(main_path)
            return main_settings.get_modules()

        modules = { 
            self.alias : GitModule(
                self.root,
                root = True,
                url  = self.url,
                name = self.name,
                user = self.user
            )
        }

        if not exists( file ):
            return modules

        cnf = configparser.ConfigParser()
        cnf.read( file )

        for s in cnf.sections():
            p = cnf[s].get('path'   ,  None  )
            u = cnf[s].get('url'    ,  None  )

            if not 'submodule' in s or p is None or u is None:
                continue

            user, name, _ = system.git_url_parse(u)
            if name is None:
                continue

            modules[f"{user}/{name}"] = GitModule(
                join(self.root,p),
                active = cnf[s].get('active','True').lower().strip()=='true',
                url    = u,
                name   = name,
                user   = user
            )


        return modules

    @lru_cache(maxsize=None)
    def get_commands(self, is_global = False, filter = None):
        dr = self.d_commands
        if is_global or not self.is_repo:
            dr = system.get_global_config().get( 'global-commands',None )

        if dr is None: return

        # widnows git bash fixes
        dr = Path(dr)
        if str(dr).startswith("/c/") or str(dr).startswith("\\c\\"):
            dr = Path("C:" + str(dr)[2:])

        if not dr.exists():
            return

        valid = [
            {"ext" : 'py'   , "run" : "python3" },
            {"ext" : 'bash' , "run" : "bash"    },
            {"ext" : 'sh'   , "run" : "sh"      }
        ]

        vdict = {x['ext']:x['run'] for x in valid}

        if filter is None:
            for ab in walker(dr):
                fl = str(Path( ab ).relative_to( dr ))
                st = splitext(fl)
                rn = vdict.get(st[1].strip('.'),None)

                if rn is None:
                    continue

                yield {
                    "cmd"  : st[0],
                    "run"  : rn,
                    "path" : ab
                }

            return

        for t in valid:
            file = join(dr,f"{filter}." + t['ext'])
            if exists(file):
                yield {
                    "cmd"  : filter,
                    "run"  : t['run'],
                    "path" : file
                }
                break

 
    @lru_cache(maxsize=None)
    def get_ymvas_settings(self):
        return get_json(self.f_settings)

    @lru_cache(maxsize=None)
    def get_ymvas_hooks_settings(self):
        return get_yaml(self.f_settings_hooks)

    @lru_cache(maxsize=None)
    def get_ymvas_schedules_settings(self):
        return get_yaml(self.f_settings_schedules)


