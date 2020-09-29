# Getting started

You will need pandoc and R.

```sh
sudo apt install pandoc r-base
```

You will need the R-packages `bookdown` and `servr` (for live preview).

```r
sudo R
> install.packages('bookdown')
> install.packages('servr')
> install.packages('tufte') # Probably gonna use this so just do it
```

When this is done you should be able to run `make documentation` or just `make` to build a pdf version of the report. This will be found in `_book/_main.pdf`.

While editing the report it may be beneficial to have a live preview. This can be done by opening another terminal, navigating to this directory `Report` and running `make serve`. This will start serving an HTML version of the report at `localhost:4321`.


# Structure

I have no clue how this report should be divided into chapters and bibliography is not yet handled.
