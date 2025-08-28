### AI web app for internal corporate use


#### Development notes
Note that `uv run` will inherit and prioritize env variables from parent environment, 
which may lead to unexpected behaviour if for some reason these variables are set,
for example VS Code may automatically inject variables from .env file.
