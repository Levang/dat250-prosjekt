# Getting started

To get started you will need `bookdown` an R package.

To install this simply enter the R shell (preferably in root mode to install the package globally), then install the package.

```
sudo R
> install.packages('bookdown')
```

Afterwards exit R and you're done.

Now you should be able to simply run `make` inside the `Report` directory. This requires you to also have make installed, but assuming you're not an idiot, you already have that.

I have arranged the structure of the report so that each part of the report can be built separately and hopefully all combined into one book at the end. I'll have to figure out how we'll do bibliography, but for now you should be able to enter any directory such as `Authentication` and build that part only. This can be helpful to avoid errors when multiple people are working on the report.

Alternatively, assuming you've installed the `bookdown` package you should also be able to compile the book from RStudio, but I have not attempted this.
