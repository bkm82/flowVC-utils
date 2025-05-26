;; Set the package installation directory so that packages aren't stored in the
;; ~/.emacs.d/elpa path.
(require 'package)
(setq package-user-dir (expand-file-name "./.packages"))
(setq package-archives '(("melpa" . "https://melpa.org/packages/")
                         ("elpa" . "https://elpa.gnu.org/packages/")))

;; Initialize the package system
(package-initialize)
(unless package-archive-contents
  (package-refresh-contents))

;; Install dependencies
(package-install 'htmlize)

;; Load the publishing system
(require 'ox-publish)

;; Define the publishing project
(setq org-publish-project-alist
      (list
       '("my-org-site"
             :recursive t
             :base-directory "./content"
             :publishing-directory "./public"
	     :base-extension "org"
	     :publishing-function org-html-publish-to-html
	     :with-author nil           ;; Don't include author name
             :with-creator t            ;; Emacs and Org versions in footer

             :with-toc t                ;; Include a table of contents
             :section-numbers nil       ;; Don't include section numbers
             :time-stamp-file nil       ;; Don't include time stamp in file
	     )
             '("org-static"
             :base-directory "./content"
             :base-extension "css\\|js\\|png\\|jpg\\|gif\\|pdf\\|mp3\\|ogg\\|swf"
             :publishing-directory "./public"
             :recursive t
             :publishing-function org-publish-attachment
             )
       ))
;; Remove validate ling at bottom
(setq org-html-validation-link nil            ;; Dont show validation link
      org-html-head-include-scripts nil       ;; Use our own scripts
      org-html-head-include-default-style nil) ;; Use our own styles
      ;;org-html-head "<link rel=\"stylesheet\" href=\"https://cdn.simplecss.org/simple.min.css\" />")
      ;;org-html-head "<script type="text/javascript" src="http://www.pirilampo.org/styles/readtheorg/js/readtheorg.js"></script>")
;; Generate the site output
(org-publish-all t)


(message "Build complete!")
