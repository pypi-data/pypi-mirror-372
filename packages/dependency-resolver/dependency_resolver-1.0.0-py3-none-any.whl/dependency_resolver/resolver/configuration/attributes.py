try :
    from strenum import StrEnum  # for Python versions pre 3.11
except ImportError :
    from enum import StrEnum   # for Python versions 3.11+

class ConfigAttributes(StrEnum) :
    # top level
    PROJECT_NAME:str = "project"
    VERSION:str = "version"

    # config
    TARGET_ROOT:str = "target_root"
    CACHE_ROOT:str = "cache_root"

    # sources
    SOURCES:str = "sources"
    SOURCE_NAME:str = "name"
    SOURCE_BASE:str = "base"
    SOURCE_DESCRIPTION:str = "description"

    SOURCE_PROTOCOL:str = "protocol"
    PROTOCOL_HTTPS:str = "https"
    PROTOCOL_FS:str = "filesystem"

    SOURCE_TYPE:str = "type"
    TYPE_ABSOLUTE:str = "absolute"
    TYPE_PROJECT:str = "project"

    # dependencies
    DEPENDENCIES:str = "dependencies"
    DEPENDENCY_NAME:str = "name"
    DEPENDENCY_DESCRIPTION:str = "description"
    DEPENDENCY_TARGET_DIR:str = "target_dir"
    DEPENDENCY_TARGET_NAME:str = "target_name"
    DEPENDENCY_SOURCE_DEPENDENCY:str = "source"
    DEPENDENCY_SOURCE_PATH:str = "source_path"
    DEPENDENCY_TARGET_RELATIVE_ROOT:str = "target_relative_root"
    DEPENDENCY_ALWAYS_UPDATE:str = "always_update"

    RESOLVE_ACTION:str = "resolve_action"
    RESOLVE_COPY:str = "copy"
    RESOLVE_UNZIP:str = "unzip"
    RESOLVE_UNTAR:str = "untar"
