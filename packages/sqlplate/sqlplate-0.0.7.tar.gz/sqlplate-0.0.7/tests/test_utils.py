from src.sqlplate.utils import get_env


def test_get_env(test_path):
    env = get_env(test_path.parent / "templates")
    template = env.get_template("base.jinja")
    assert template.render() == ""

    template = env.from_string("SELECT 'HELLO WORLD' AS GREETING")
    assert template.render() == "SELECT 'HELLO WORLD' AS GREETING"


def test_custom_filter_map_fmt(test_path):
    env = get_env(test_path.parent / "templates")
    template = env.from_string(
        "SET {{ cols | map_fmt(fmt='src.{0} = tgt.{0}') | join(', ') }}"
    )
    assert template.render(cols=["col01", "col02"]) == (
        "SET src.col01 = tgt.col01, src.col02 = tgt.col02"
    )


def test_merge_list(test_path):
    env = get_env(test_path.parent / "templates")
    template = env.from_string(
        """{%- set row_one = ['1', '2', '3', '4'] -%}
        {%- set row_two = ['a', 'b', 'c', 'd'] -%}
        SELECT {{ row_one + row_two }}
        """
    )
    assert template.render().strip().strip("\n") == (
        "SELECT ['1', '2', '3', '4', 'a', 'b', 'c', 'd']"
    )
