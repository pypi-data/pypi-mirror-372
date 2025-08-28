# Changelogs

## Latest Changes

## 0.0.7

### :postbox: Dependencies

- :pushpin: deps: mark optional deps.
- :pushpin: deps: update python version support base 3.10 or upper.

### :book: Documentations

- :page_facing_up: docs: update readme file.

## 0.0.6

### :sparkles: Features

- :dart: feat: update select statement on sqlite.
- :dart: feat: add matrix quality.

### :black_nib: Code Changes

- :test_tube: tests: update utils test.

## 0.0.5

### :sparkles: Features

- :dart: feat: handle tag or version on target system that want to generate (#5)
- :dart: feat: add data quality and write report file after validation (#4)

### :broom: Deprecate & Clean

- :recycle: clean: rename class method for list formats on template folder.

### :package: Build & Workflow

- :toolbox: build: change env url that not valid.

### :postbox: Dependencies

- :package: deps: bump jinja2 from 3.1.5 to 3.1.6 (#1)

## 0.0.4

### :stars: Highlight Features

- :star: hl: add databricks/etl.scd2-transaction template.

### :sparkles: Features

- :dart: feat: add formats method on sqlplate obj for list supported template.
- :dart: feat: add support env var config.
- :dart: feat: add elt.transaction and etl.fulldump templates.

### :bug: Bug fixes

- :gear: fixed: mover config dataclass outside config func.

### :black_nib: Code Changes

- :test_tube: tests: add templates on tests.

### :broom: Deprecate & Clean

- :recycle: clean: move multiple strip funcs to trim.

## 0.0.3

### :sparkles: Features

- :dart: feat: add template type args on SQLPlate object for filter jinja variables.
- :dart: feat: add hash macro in utils.jinja.
- :dart: feat: add revert statement on etl scd1 soft delete template.
- :dart: feat: add config value and able to passing to jinja env.
- :dart: feat: add base template.
- :dart: feat: add scd2 and scd2 with delete flag templates on databricks sys.

### :package: Build & Workflow

- :toolbox: build: add gh issue template for request new template.
- :toolbox: build: add gh issue template.

### :postbox: Dependencies

- :pushpin: deps: update clishelf version to 0.2.17.

## 0.0.2

### :sparkles: Features

- :dart: feat: add remove comment flag in load method.
- :dart: feat: add databricks/scd1-soft-delete template.
- :dart: feat: add macros and utils for dynamic template generator.
- :dart: feat: add databricks/delta template.

### :package: Build & Workflow

- :toolbox: build: add name on publish workflow.

## 0.0.1.post1

### :black_nib: Code Changes

- :test_tube: tests: add list release cli on pre-release.

### :bug: Bug fixes

- :gear: fixed: remove repo name on upload to gh release cli.

### :package: Build & Workflow

- :toolbox: build: rename gh token env var.

## 0.0.1.post0

### :bug: Bug fixes

- :gear: fixed: change release name to tag_name on upload gh sign.
- :gear: fixed: change upload artifact sign cmd.

## 0.0.1

### :sparkles: Features

- :dart: feat: add the first draft of usage example of this project.
- :dart: feat: add jinja template deps to this project.
- :tada: initial: update the first template.

### :black_nib: Code Changes

- :test_tube: tests: add testcase for databricks/select template.
- :construction: refactored: Initial commit

### :bug: Bug fixes

- :gear: fixed: change import path on test utils.

### :package: Build & Workflow

- :toolbox: build: add header and remove token on publish workflow.
- :toolbox: build: add test workflow.
- :toolbox: build: add publish workflow for build this package.
- :package: build: create dependabot.yml
