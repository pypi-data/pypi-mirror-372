from . import (
    global_config_file,
    global_config_dir
)

errors = {
    # system errors
    "global-dir-not-created" : {
        "msg"  : (
            "Unable to create global directory, please check permisions!"
            f"[{global_config_dir()}]"
        ),
        "code" : "501"
    },
    "global-config-not-created" : {
        "msg" : (
            "Unable to create global config file please check permisions!"
            f"[{global_config_file()}]"
        ),
        "code" : "502"
    },
    "global-config-misconfigured": {
        "msg" : (
            f"Unable to parse config file [{global_config_file()}]"
            ", please remove it or fix the contents"
        ),
        "code" : "503"
    },










    # compiler errors
    "compiler-invalid-path" : {
        "msg" : (
            "[{src}] is not a valid repository!"
        ),
        "code" : '301'
    }



}
