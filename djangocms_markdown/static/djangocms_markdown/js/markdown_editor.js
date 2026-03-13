(function () {
    "use strict";

    var initialized = new WeakSet();

    // Regex to match markdown links: [text](url) but not images: ![alt](url)
    var MD_LINK_RE = /(?<!!)\[([^\]]*)\]\(([^)]*)\)/g;

    function getJQuery() {
        if (typeof django !== "undefined" && django.jQuery && django.jQuery.fn.select2) {
            return django.jQuery;
        }
        return null;
    }

    function findLinkAtPos(lineText, ch) {
        MD_LINK_RE.lastIndex = 0;
        var match;
        while ((match = MD_LINK_RE.exec(lineText)) !== null) {
            var linkStart = match.index; // the "["
            var linkEnd = match.index + match[0].length; // after ")"
            var textStart = match.index + 1; // after "["
            var textEnd = textStart + match[1].length; // before "]"
            var urlStart = match.index + match[1].length + 3; // after "[text]("
            var urlEnd = urlStart + match[2].length; // before ")"
            if (ch >= linkStart && ch <= linkEnd) {
                return {
                    linkStart: linkStart,
                    linkEnd: linkEnd,
                    textStart: textStart,
                    textEnd: textEnd,
                    urlStart: urlStart,
                    urlEnd: urlEnd,
                    text: match[1],
                    url: match[2],
                };
            }
        }
        return null;
    }

    function selectionInsideLink(cm) {
        var fromCur = cm.getCursor("from");
        var toCur = cm.getCursor("to");
        if (fromCur.line !== toCur.line) {
            return null;
        }
        var lineText = cm.getLine(fromCur.line);
        var linkFrom = findLinkAtPos(lineText, fromCur.ch);
        if (!linkFrom) {
            return null;
        }
        if (fromCur.ch !== toCur.ch) {
            var linkTo = findLinkAtPos(lineText, toCur.ch);
            if (!linkTo || linkTo.linkStart !== linkFrom.linkStart) {
                return null;
            }
        }
        linkFrom.line = fromCur.line;
        return linkFrom;
    }

    // ── Floating reference picker (select2 dropdown) ──────────
    function createRefPopup() {
        var popup = document.createElement("div");
        popup.className = "md-ref-popup";

        var select = document.createElement("select");
        select.className = "md-ref-select";
        popup.appendChild(select);

        return { popup: popup, select: select };
    }

    function initSelect2($, select, autocompleteUrl, dropdownParent, placeholder) {
        var $select = $(select);
        $select.select2({
            ajax: {
                url: autocompleteUrl,
                dataType: "json",
                delay: 250,
                cache: true,
                data: function (params) {
                    return {
                        term: params.term || "",
                        page: params.page || 1,
                    };
                },
                processResults: function (data) {
                    return {
                        results: data.results,
                        pagination: data.pagination,
                    };
                },
            },
            placeholder: placeholder,
            allowClear: true,
            minimumInputLength: 0,
            width: "350px",
            dropdownParent: dropdownParent,
        });
        return $select;
    }

    function positionPopup(popup, cm, linkInfo) {
        // Get pixel coordinates of the URL start in the editor
        var coords = cm.charCoords({ line: linkInfo.line, ch: linkInfo.urlStart }, "local");
        var cmWrapper = cm.getWrapperElement();
        var cmRect = cmWrapper.getBoundingClientRect();
        var scrollInfo = cm.getScrollInfo();

        var left = coords.left - scrollInfo.left;
        var spaceAbove = coords.top - scrollInfo.top;
        var spaceBelow = cmRect.height - (coords.bottom - scrollInfo.top);

        popup.style.left = left + "px";

        // Prefer above the line; fall back to below if not enough space
        if (spaceAbove > 60) {
            popup.style.bottom = (cmRect.height - (coords.top - scrollInfo.top)) + "px";
            popup.style.top = "auto";
        } else {
            popup.style.top = (coords.bottom - scrollInfo.top) + "px";
            popup.style.bottom = "auto";
        }
    }

    function initMarkdownEditor(textarea) {
        if (initialized.has(textarea)) {
            return;
        }
        if (!textarea.classList.contains("markdown-editor")) {
            return;
        }
        if (textarea.closest(".empty-form")) {
            return;
        }

        initialized.add(textarea);

        // Wrap textarea for styling
        var wrapper = document.createElement("div");
        wrapper.className = "markdown-editor-wrapper";
        textarea.parentNode.insertBefore(wrapper, textarea);
        wrapper.appendChild(textarea);

        var easyMDE = new EasyMDE({
            element: textarea,
            autoDownloadFontAwesome: true,
            spellChecker: false,
            nativeSpellcheck: true,
            inputStyle: "contenteditable",
            toolbar: [
                "bold",
                "italic",
                "strikethrough",
                "heading",
                "|",
                "code",
                "quote",
                "unordered-list",
                "ordered-list",
                "checklist",
                "|",
                "link",
                "image",
                "table",
                "horizontal-rule",
                "|",
                "preview",
                "side-by-side",
                "fullscreen",
                "|",
                "guide",
            ],
            status: ["lines", "words", "cursor"],
            minHeight: "300px",
            renderingConfig: {
                singleLineBreaks: false,
                codeSyntaxHighlighting: true,
            },
            tabSize: 4,
            forceSync: true,
        });

        var cm = easyMDE.codemirror;

        // Sync on change for Django form submission
        cm.on("change", function () {
            textarea.value = easyMDE.value();
        });

        // ── Reference picker popup ────────────────────────────
        var autocompleteUrl = textarea.getAttribute("data-link-autocomplete-url");
        var refState = null; // { popup, $select, linkInfo }

        function showRefPopup(linkInfo) {
            var $ = getJQuery();
            if (!$) {
                return;
            }

            var parts = createRefPopup();
            var cmWrapper = cm.getWrapperElement();

            // Append inside CM wrapper so it scrolls/clips with the editor
            cmWrapper.appendChild(parts.popup);
            positionPopup(parts.popup, cm, linkInfo);

            // Prevent interactions from stealing CM focus
            parts.popup.addEventListener("mousedown", function (e) {
                e.preventDefault();
                e.stopPropagation();
            });

            var placeholder = textarea.getAttribute("data-ref-placeholder") || "";
            var $select = initSelect2($, parts.select, autocompleteUrl, $(parts.popup), placeholder);

            // Insert immediately on selection — re-find the URL position
            // since the user may have edited the link while the popup was open.
            $select.on("select2:select", function (e) {
                var lineText = cm.getLine(linkInfo.line);
                var current = findLinkAtPos(lineText, linkInfo.urlStart);
                if (current) {
                    var refUrl = "ref:" + e.params.data.id;
                    // Replace URL first, then fill in text if empty.
                    // Do URL first so text insertion doesn't shift URL positions.
                    cm.replaceRange(refUrl,
                        { line: linkInfo.line, ch: current.urlStart },
                        { line: linkInfo.line, ch: current.urlEnd }
                    );
                    if (!current.text.trim()) {
                        var displayText = e.params.data.text.trim();
                        cm.replaceRange(displayText,
                            { line: linkInfo.line, ch: current.textStart },
                            { line: linkInfo.line, ch: current.textEnd }
                        );
                    }
                }
                hideRefPopup();
                cm.focus();
            });

            refState = {
                popup: parts.popup,
                $select: $select,
                linkInfo: linkInfo,
            };
        }

        function hideRefPopup() {
            if (!refState) {
                return;
            }
            refState.$select.select2("destroy");
            refState.popup.remove();
            refState = null;
        }

        if (autocompleteUrl) {
            cm.on("cursorActivity", function () {
                var linkInfo = selectionInsideLink(cm);

                if (linkInfo) {
                    if (
                        refState &&
                        refState.linkInfo.line === linkInfo.line &&
                        refState.linkInfo.linkStart === linkInfo.linkStart
                    ) {
                        return;
                    }
                    hideRefPopup();
                    showRefPopup(linkInfo);
                } else {
                    hideRefPopup();
                }
            });
        }

        // Start in fullscreen mode
        easyMDE.toggleFullScreen();

        // Store reference for cleanup
        textarea._easyMDE = easyMDE;
    }

    function initAllEditors() {
        var textareas = document.querySelectorAll("textarea.markdown-editor");
        textareas.forEach(initMarkdownEditor);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initAllEditors);
    } else {
        initAllEditors();
    }

    if (typeof django !== "undefined" && django.jQuery) {
        django.jQuery(document).on(
            "formset:added",
            function (_event, $row) {
                var textarea = $row[0].querySelector("textarea.markdown-editor");
                if (textarea) {
                    initMarkdownEditor(textarea);
                }
            }
        );
    }

    function startObserver() {
        var observer = new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {
                mutation.addedNodes.forEach(function (node) {
                    if (node.nodeType !== Node.ELEMENT_NODE) {
                        return;
                    }
                    var textareas = node.querySelectorAll
                        ? node.querySelectorAll("textarea.markdown-editor")
                        : [];
                    textareas.forEach(initMarkdownEditor);
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
        });
    }

    if (document.body) {
        startObserver();
    } else {
        document.addEventListener("DOMContentLoaded", startObserver);
    }
})();
