# dependency-resolver
Define external dependencies for a project using a JSON file, then fetch and resolve them into the project.

Ideally for python versions > 3.11, but should be cope with 3.10, although different dependencies will be introduced (see requirements.txt)

For list of supported commands run dependency-resolver/resolve.py -h

Better notes will be added here in due course!

## Description
Define external dependencies (publicly (https) available files) for a project using a JSON file, then fetch and resolve them into the project.

The JSON file can then be versioned controlled with the project instead of the dependencies themselves.

Each dependency has a source and a target that defines where the dependency is and where it should be resolved to locally.

### Fetching and Resolving
Getting dependencies is a two-step process. 

1. The dependency source is fetched (downloaded) and added to a local cache as is.
2. This source can then be resolved from the cache to the local dependency target.

Each dependency can specify an action to be carried out when resolving the source from the cache to the dependency target:
- Copy the fetched file.
- Unzip the fetched .zip.
- Untar the fetched .tar.

Multiple dependencies can use the same source and each can resolve it to different target locations using different actions.

Using a cache means the same dependency source is fetch only once for all dependencies that use it, but resolved any number of times.

Static dependencies can only be fetched on its initial run, and dynamic ones can be fetched every time its run.

## Configuration
The JSON configuration file (examples are in the examples folder in the repository):
{
    "project" : "MyProject", // The name of the project (mandatory). This will also determine the top level of the cache where all sources are fetched to, allowing different projects to have different caches.
        
    "dependencies" :
    [
        {
                                                                // Example of a dependency which is copied to a target directory.   
            "name" : "Download_Latest_Version",                 // The name of the dependency (mandatory). Must be unique.
            "description" : "The latest version of myThing.",   // A description for this dependency (optional).
            "target_dir" : "/put/latest/here",                  // The local directory to resolve this dependency to (mandatory).
            "target_name" : "myThing.app",                      // The target file name (optional).
            "source" : "latest"                                 // The source to use (mandatory).
        },
        {
                                                    // Example of a dependency which is unzipped to a target directory.   
            "name" : "Unzip_Useful_Stuff",          // The name of the dependency (mandatory). Must be unique.
            "description" : "A useful zip file.",   // A description for this dependency (optional).
            "target_dir" : "/useful/stuff/",        // The local directory to resolve this dependency to (mandatory).
            "source" : "myfiles",                   // The source to use (mandatory).
            "source_path" : "this/zip/useful.zip",  // A path relative to the "base" directory defined in the source (optional, unless using a source with a protocol of 'filesystem').
            "resolve_action" : "unzip"              // The action to perform when resolving the dependency (optional). Options: unzip, untar, copy - defaults to copy.
        }
    ],
    "sources" :
    [
        {
            "name" : "internal",        // The name of the source (mandatory). Must be unique.
            "protocol" : "filesystem",  // The protocol used to fetch the source (optional). Options: filesystem (from some local directory), https - defaults to https.
            "type" : "project"          // Options are: project (the dependency's source_path is relative to this configuration file) or absolute (the dependency's source_path is an absolute path) - defaults to project.
        },
        {
            "name" : "latest",                                                          // The name of the source (mandatory). Must be unique.
            "protocol" : "https",                                                       // The protocol used to fetch the source (optional). Options: filesystem (from some local directory), https - defaults to https.
            "base" : "https://downloads.example.com/latest/myThing_5_13_5_linux64.app"  // The address of the source (mandatory). The dependency's 'source_path' can extend this address.
        },       
        {
            "name" : "myfiles",                             // The name of the source (mandatory). Must be unique.
            "protocol" : "https",                           // The protocol used to fetch the source (optional). Options: filesystem (from some local directory), https - defaults to https.
            "base" : "https://downloads.example.com/stuff"  // The address of the source (mandatory). The dependency's 'source_path' can extend this address.
        }
    ]
}

## Installation
### Create a virtual environment (optional)
`python3 -m venv .env/dependency-resolver`</br>
`. .env/dependency-resolver/bin/activate`

### Install archive-and-release
`pip install dependency-resolver`

### Exit the virtual environment
`deactivate`

## Commands
### See all commands/help
`dependency-resolver -h`

### Individual command options/help
`dependency-resolver <cmd> -h`

### Print the configuration JSON
Can be used to make sure the configuration JSON file being used is the expected one.

`dependency-resolver print_config --configPath examples/sample.json`

### Test the configuration JSON
Tests the given JSON file to make sure it valid. Its quite a basic test, but should detect anything glaring.

`dependency-resolver validate_config --configPath examples/sample.json`

### Print dependency target
This can be used to programmatically determine where a given dependency will be resolved to. This could be used to refer to the dependency from other places in your project.

`dependency-resolver print_dependency_target --configPath examples/sample.json --name Download_Latest_Version`

### Fetch all dependencies
Downloads all sources into the cache.

`dependency-resolver update_cache --configPath examples/sample.json`

Empty the cache and then download all sources into the cache.
`dependency-resolver update_cache --configPath examples/sample.json --clean`

### Resolve all fetched dependencies
Resolves all dependencies that have previously been fetched. If they have not been fetched then this will thrown an error.

`dependency-resolver resolve_from_cache --configPath examples/sample.json`

### Fetch and resolve all dependencies
Fetches all sources (if required) and resolves them.
`dependency-resolver resolve --configPath examples/sample.json`
