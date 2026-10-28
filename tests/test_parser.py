from src.parser import (
    extract_added_ruby_code,
    extract_changed_files,
    extract_ruby_files,
    is_test_file,
    parse_diff,
)


SAMPLE_DIFF = """\
diff --git a/app/models/user.rb b/app/models/user.rb
index 111..222 100644
--- a/app/models/user.rb
+++ b/app/models/user.rb
@@ -1,3 +1,4 @@
 class User < ApplicationRecord
+  scope :active, -> { where(active: true) }
   validates :email, presence: true
 end
diff --git a/spec/models/user_spec.rb b/spec/models/user_spec.rb
index 333..444 100644
--- a/spec/models/user_spec.rb
+++ b/spec/models/user_spec.rb
@@ -1,2 +1,3 @@
 RSpec.describe User do
+  it { is_expected.to validate_presence_of(:email) }
 end
diff --git a/README.md b/README.md
index 555..666 100644
--- a/README.md
+++ b/README.md
@@ -1 +1,2 @@
 # Project
+More docs.
"""


def test_is_test_file():
    assert is_test_file("spec/models/user_spec.rb")
    assert is_test_file("test/models/user_test.rb")
    assert not is_test_file("app/models/user.rb")


def test_extract_changed_files_counts_and_flags():
    files = extract_changed_files(SAMPLE_DIFF)

    names = [f["filename"] for f in files]

    assert names == [
        "app/models/user.rb",
        "spec/models/user_spec.rb",
        "README.md",
    ]

    by_name = {f["filename"]: f for f in files}

    assert by_name["app/models/user.rb"]["is_ruby"]
    assert not by_name["app/models/user.rb"]["is_test"]
    assert by_name["spec/models/user_spec.rb"]["is_test"]
    assert not by_name["README.md"]["is_ruby"]


def test_extract_ruby_files_excludes_non_ruby():
    assert extract_ruby_files(SAMPLE_DIFF) == [
        "app/models/user.rb",
        "spec/models/user_spec.rb",
    ]


def test_extract_added_ruby_code_captures_added_lines():
    code = extract_added_ruby_code(SAMPLE_DIFF)

    assert "scope :active" in code
    assert "validate_presence_of" in code
    # Non-Ruby additions are not included.
    assert "More docs." not in code


def test_parse_diff_splits_production_and_test():
    parsed = parse_diff(SAMPLE_DIFF)

    production = [f["filename"] for f in parsed["production_files"]]
    tests = [f["filename"] for f in parsed["test_files"]]

    assert production == ["app/models/user.rb"]
    assert tests == ["spec/models/user_spec.rb"]


def test_parse_diff_empty():
    parsed = parse_diff("")

    assert parsed["ruby_files"] == []
    assert parsed["added_ruby_code"] == ""
