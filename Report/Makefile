pdf_book:
	R -e "bookdown::render_book('index.Rmd', 'bookdown::pdf_book', config_file='_bookdown.yml')"

gitbook:
	R -e "bookdown::render_book('index.Rmd', 'bookdown::gitbook', config_gile='_bookdown.yml')"

serve:
	R -e "bookdown::serve_book(dir='.', output_dir='../Documentation', T, F, T)"

.PHONY: clean
clean:
	-rm -rf ../Documentation/*
