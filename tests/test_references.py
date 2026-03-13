from unittest.mock import patch, MagicMock

from djangocms_markdown.references import (
    collect_references,
    fetch_objects,
    resolve_references,
)


class TestCollectReferences:
    def test_no_references(self):
        html = '<a href="https://example.com">link</a>'
        assert collect_references(html) == {}

    def test_empty_string(self):
        assert collect_references("") == {}

    def test_single_reference(self):
        html = '<a href="ref:myapp.mymodel:42">link</a>'
        refs = collect_references(html)
        assert refs == {("myapp", "mymodel"): {42}}

    def test_multiple_references_same_model(self):
        html = (
            '<a href="ref:myapp.mymodel:1">one</a><a href="ref:myapp.mymodel:2">two</a>'
        )
        refs = collect_references(html)
        assert refs == {("myapp", "mymodel"): {1, 2}}

    def test_multiple_references_different_models(self):
        html = '<a href="ref:myapp.page:1">page</a><a href="ref:blog.post:5">post</a>'
        refs = collect_references(html)
        assert refs == {
            ("myapp", "page"): {1},
            ("blog", "post"): {5},
        }

    def test_ignores_non_ref_hrefs(self):
        html = (
            '<a href="https://example.com">normal</a><a href="ref:myapp.page:1">ref</a>'
        )
        refs = collect_references(html)
        assert refs == {("myapp", "page"): {1}}

    def test_ref_outside_href_ignored(self):
        html = "<p>ref:myapp.page:1</p>"
        assert collect_references(html) == {}


class TestFetchObjects:
    def test_empty_refs(self):
        assert fetch_objects({}) == {}

    @patch("djangocms_markdown.references.apps")
    def test_model_not_found(self, mock_apps):
        mock_apps.get_model.side_effect = LookupError("No such model")
        refs = {("noapp", "nomodel"): {1, 2}}
        url_map = fetch_objects(refs)
        assert url_map == {
            "noapp.nomodel:1": "#",
            "noapp.nomodel:2": "#",
        }

    @patch("djangocms_markdown.references.apps")
    def test_object_with_absolute_url(self, mock_apps):
        obj = MagicMock()
        obj.pk = 1
        obj.get_absolute_url.return_value = "/pages/1/"

        model = MagicMock()
        model.objects.filter.return_value = [obj]
        mock_apps.get_model.return_value = model

        refs = {("myapp", "page"): {1}}
        url_map = fetch_objects(refs)
        assert url_map == {"myapp.page:1": "/pages/1/"}

    @patch("djangocms_markdown.references.apps")
    def test_object_without_absolute_url(self, mock_apps):
        obj = MagicMock(spec=[])  # no get_absolute_url
        obj.pk = 1

        model = MagicMock()
        model.objects.filter.return_value = [obj]
        mock_apps.get_model.return_value = model

        refs = {("myapp", "page"): {1}}
        url_map = fetch_objects(refs)
        assert url_map == {"myapp.page:1": "#"}

    @patch("djangocms_markdown.references.apps")
    def test_missing_object(self, mock_apps):
        model = MagicMock()
        model.objects.filter.return_value = []  # no objects found
        mock_apps.get_model.return_value = model

        refs = {("myapp", "page"): {1}}
        url_map = fetch_objects(refs)
        assert url_map == {"myapp.page:1": "#"}

    @patch("djangocms_markdown.references.apps")
    def test_partial_missing_objects(self, mock_apps):
        obj = MagicMock()
        obj.pk = 1
        obj.get_absolute_url.return_value = "/pages/1/"

        model = MagicMock()
        model.objects.filter.return_value = [obj]
        mock_apps.get_model.return_value = model

        refs = {("myapp", "page"): {1, 2}}
        url_map = fetch_objects(refs)
        assert url_map["myapp.page:1"] == "/pages/1/"
        assert url_map["myapp.page:2"] == "#"


class TestResolveReferences:
    def test_none_input(self):
        assert resolve_references(None) is None

    def test_empty_string(self):
        assert resolve_references("") == ""

    def test_no_ref_in_html(self):
        html = '<a href="https://example.com">link</a>'
        assert resolve_references(html) == html

    @patch("djangocms_markdown.references.fetch_objects")
    def test_resolves_single_ref(self, mock_fetch):
        mock_fetch.return_value = {"myapp.page:1": "/pages/1/"}
        html = '<a href="ref:myapp.page:1">My Page</a>'
        result = resolve_references(html)
        assert result == '<a href="/pages/1/">My Page</a>'

    @patch("djangocms_markdown.references.fetch_objects")
    def test_resolves_multiple_refs(self, mock_fetch):
        mock_fetch.return_value = {
            "myapp.page:1": "/pages/1/",
            "blog.post:5": "/blog/5/",
        }
        html = '<a href="ref:myapp.page:1">Page</a> <a href="ref:blog.post:5">Post</a>'
        result = resolve_references(html)
        assert 'href="/pages/1/"' in result
        assert 'href="/blog/5/"' in result

    @patch("djangocms_markdown.references.fetch_objects")
    def test_unresolved_ref_becomes_hash(self, mock_fetch):
        mock_fetch.return_value = {"myapp.page:999": "#"}
        html = '<a href="ref:myapp.page:999">Missing</a>'
        result = resolve_references(html)
        assert result == '<a href="#">Missing</a>'

    @patch("djangocms_markdown.references.fetch_objects")
    def test_mixed_refs_and_normal_links(self, mock_fetch):
        mock_fetch.return_value = {"myapp.page:1": "/pages/1/"}
        html = (
            '<a href="https://example.com">Normal</a> '
            '<a href="ref:myapp.page:1">Ref</a>'
        )
        result = resolve_references(html)
        assert 'href="https://example.com"' in result
        assert 'href="/pages/1/"' in result


class TestRefSurvivesSanitization:
    """Ensure ref: URLs survive nh3 sanitization."""

    def test_ref_url_not_stripped(self):
        from djangocms_markdown.rendering import render_markdown

        result = render_markdown("[My Page](ref:myapp.page:42)")
        assert 'href="ref:myapp.page:42"' in result
