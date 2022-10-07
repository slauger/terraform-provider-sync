# terraform-provider-sync

This is a small python script which can mirror terraform providers from `registry.terraform.io` to a local directory.

With the `terraform providers mirror` command you always need to define the fixed version which should be downloaded locally. This script talks directly to the registry API and fetches all available versions for a specific provider. This allows you to have a fully automated local mirror for all the providers you need.

## Usage 

```
usage: tfsync.py [-h] [--dryrun] [--config <file>]

command line arguments.

options:
  -h, --help       show this help message and exit
  --dryrun         if set the script will only run in dry-run and will not download files
  --config <file>  configuration file (defaults to "providers.json")
```

The providers which should be downloaded must be defined in a config file (`providers.json`) with the following format:

```
{
  "directory": ".",
  "providers": {
    "terraform-provider-local": {
      "url": "hashicorp/local",
      "since": "2.2.0"
    },
    "terraform-provider-opentelekomcloud": {
      "url": "opentelekomcloud/opentelekomcloud",
      "since": "1.28.0",
      "exclude": [
        "1.28.3"
      ]
    },
    "terraform-provider-openstack": {
      "url": "terraform-provider-openstack/openstack",
      "since": "1.48.0"
    }
  }
}
```

To reduce the required storage size you can use the `since` field to set a semantic version which should be the first version the script should download. This version and newer versions will be downloaded then. Older versions will be ignored.

*Important:* in some rare case it could be that packages are removed from `registry.terraform.io`, even if they are displayed in the API response. In this case you can use the `exclude` field to exclude this version from the download.

## Use your mirror

Just create a file `~/.terraformrc` and put in the URL to your local mirror.

```
provider_installation {
  network_mirror {
    url = "https://terraform-registry.example.com/"
  }
}
```

## Requirements

- python3-requests
- python3-packaging

## Author

- Simon Lauger
