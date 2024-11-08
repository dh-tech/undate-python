# Contributing to undate

Hey there!

If you found your way here that probably means you are curious about how to contribute to this project. This is great! We are always looking for new contributors. If you can't find the information you are looking for in this document or anywhere else in the repo, please consider [opening a ticket](https://github.com/dh-tech/undate-python/issues) so we know there is something we need to address.

## Project Setup
Instructions on how to set up the project locally and how to run the tests can be found in [Developer Notes](DEVELOPER_NOTES.md).

## Submitting Changes

If you would like to contribute by submitting bug fixes, improvements, or new features, please fork the repository and then make a pull request to undate **develop** branch when you are ready. If you haven't contributed like this before, we recommend reading [GitHub's documentation on Contributing to a Project](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project).

We use **git flow** branching conventions, so the current release is on the **main** branch and new feature development happens on **develop**. Pull requests for new features or bug fixes should be made to **develop** for inclusion in the next release. For more details, read a longer explanation of the [Git Flow Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)

Recommended branch naming conventions:

- For a new feature, create a branch named `feature/i##-short-name` where `##` is the relevant GitHub issue number (if there is one) and `short-name` is a brief label that relates to the changes or feature

In most cases branches should be created from the most recent **develop** branch. Make sure you check out develop and pull any remote changes. 
```sh
git checkout develop
git pull
```

If you have `git flow` installed, you can start, you can use:
```sh
git flow feature start i##-short-name
```

If not, you can do the same thing with git commands:
```sh
git checkout -b feature/i##-short-name
```

When you are ready to contribute your changes, open a pull request from your branch to the main undate repository. Please be sure to link to the GitHub issue in your pull request comments.

Ideally contributions should include documentation and tests for the proposed changes, but if that is a barrier please let us know when you submit a pull request.

Please be aware that any contributions will fall under the existing Apache 2.0 license applied to this software.

## Submitting Bug Reports and Feature Requests

If you find a bug or can think a feature you would really like to see being implemented, you can [create a new issue](https://github.com/dh-tech/undate-python/issues). Please first look through the existing issues, however, to avoid duplication of issues.

If you report a bug, please include any error messages you get and a full description of the steps to reproduce the bug. For new feature requests, please clearly describe the functionality you are looking for and, if applicable, why any existing workflow does not suffice. Please also consider fixing bugs and implementing new features yourself and submitting them via pull request! :)

## Submitting Use Cases and Example Data

We are particularly interested in collecting more use cases and example data where undate would be helpful!

Example data can be added to the [examples/](https://github.com/dh-tech/undate-python/tree/main/examples/) folder by a pull request. 

## Getting Help
The best and recommended way to get help is to join the [DHTech Slack](https://dh-tech.github.io/join/) and ask for help there. Only in cases when this is not feasible at all, you can open a new issue and tag it with "Help Request".

## DHTech
This project started during the DHTech 2022 Hackathon. If you do technical work in the digital humanities and are intersted in meeting like-minded people, [consider joining](https://dh-tech.github.io/join/)!
