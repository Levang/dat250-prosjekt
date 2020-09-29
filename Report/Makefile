documentation:
	R -e "bookdown::render_book('index.Rmd', 'bookdown::pdf_book', config_file='_bookdown.yml')"

serve:
	R -e "bookdown::serve_book(dir='.', output_dir='_book', T, F, T)"

.PHONY: clean
clean:
	-rm -rf _book
