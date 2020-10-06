pdf_book:
	R -e "bookdown::render_book('index.Rmd', 'bookdown::pdf_book', config_file='_bookdown.yml')"

gitbook:
	R -e "bookdown::render_book('index.Rmd', 'bookdown::gitbook', config_file='_bookdown.yml')"

serve:
	R -e "bookdown::serve_book(dir='.', output_dir='../docs', T, F, T)"
