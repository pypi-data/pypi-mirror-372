# Marinerg-i Test Access Service #

This software is part of the [Marinerg-i preparatory phase project](https://www.marinerg-i.eu).

This service supports management of test facility access.

# Quick Start #

This is a Python `Django` application and can be managed through the standard Django APIs.

If you want a quick demo of it running locally you can inspect this script on Linux or Mac and run it if happy with it:

``` sh
./infra/quick_start.sh
```

which will:

* Set up a Python virtual environment and install dependencies
* Populate the shell environment with demo Django settings, such as Admin credentials
* Set up a local database and create an admin user
* Launch the development server

You can then go to [localhost:8000/api](http://localhost:8000/api) in a browser to interact with the backend API.

For more detailed deployment information more suitable for production you can see the [Developer Guide](/docs/DeveloperGuide.md).

# Licensing #

This software is copyright of the Irish Centre for High End Computing (ICHEC). It may be used under the terms of the GNU AGPL version 3 or later, with license details in the included `LICENSE` file. Exemptions are available for Marinerg project partners and possibly others on request.
