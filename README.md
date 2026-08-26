# YouTube Summariser

The idea of this project is to create a locally run YouTube summariser in
Python using a handful of dependency.

Obviously, generating an actual summary entirely locally would require
downloading a video and running various ML models. So this project aims to act
as a simple local tool that acts as glue between a few Python dependencies like
`yt-dlp`, `webvtt-python`, and `openai`. Essentially, it is supposed to provide
a local application that can replace an online summariser tool.

## Development

The `docs/` folder contains various details on development.

In short this project is written for Python 3.13+ and uses the `uv` package
manager and environment for running various commands.

## Local Use

For now I am installing this locally with:

```sh
uv tool install --editable /home/lyndon/repos/youtube-summary
```

Where that path is the path to this repository.
