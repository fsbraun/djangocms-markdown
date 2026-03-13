(function () {
    "use strict";

    var initialized = new WeakSet();

    function initMarkdownEditor(textarea) {
        if (initialized.has(textarea)) {
            return;
        }
        if (!textarea.classList.contains("markdown-editor")) {
            return;
        }
        // Skip hidden textareas (e.g. inline templates)
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
            // Ensure the textarea value is synced
            forceSync: true,
        });

        // Sync on change for Django form submission
        easyMDE.codemirror.on("change", function () {
            textarea.value = easyMDE.value();
        });

        // Store reference for cleanup
        textarea._easyMDE = easyMDE;
    }

    function initAllEditors() {
        var textareas = document.querySelectorAll("textarea.markdown-editor");
        textareas.forEach(initMarkdownEditor);
    }

    // Initialize when DOM is ready
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initAllEditors);
    } else {
        initAllEditors();
    }

    // Re-initialize after Django admin inline additions
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

    // Support CMS modal plugin forms (loaded via AJAX)
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
})();
