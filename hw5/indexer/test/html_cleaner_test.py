import components.html_cleaner as html_cleaner

def test_clean_html():
    raw_html = "<html><body><h1>Title</h1><p>This is a <b>bold</b> paragraph.</p></body></html>"
    expected_output = "TitleThis is a bold paragraph."
    assert html_cleaner.clean_html(raw_html) == expected_output

    raw_html = "<div><a href='#'>Link</a></div>"
    expected_output = "Link"
    assert html_cleaner.clean_html(raw_html) == expected_output

    raw_html = "No HTML here!"
    expected_output = "No HTML here!"
    assert html_cleaner.clean_html(raw_html) == expected_output
# Remove all HTML tags from a given string

test_clean_html()