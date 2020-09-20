documentation:
	R -e "bookdown::render_book('index.Rmd', 'bookdown::pdf_book', config_file='_bookdown.yml')"

serve:
	R -e "bookdown::serve_book(dir='.', output_dir='_book', preview=T, in_session=F, quiet=T)"

.PHONY: clean
clean:
	R -e "bookdown::clean_book(TRUE)"
