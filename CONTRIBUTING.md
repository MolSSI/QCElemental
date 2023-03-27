# QCElemental

QCElemental is a project collecting fundamental tools for computational molecular sciences (CMS) into a lightweight Python interface. It is maintained by the Molecular Sciences Software Institute (MolSSI) and contributed to by a number of community CMS code developers and users.

The project welcomes new contributions and comments! Pull requests are tested and linted to ensure code integrity and quality. New feature contributors are encouraged to first open a new issue or follow the "chat on slack" badge on [README.md](https://github.com/MolSSI/QCElemental/blob/master/README.md) to the QCArchive workspace.

# How to contribute

We welcome contributions from external contributors, and this document describes how to submit code changes to QCElemental.

- Make sure you have a [GitHub account](https://github.com/signup/free).
- [Fork](https://help.github.com/articles/fork-a-repo/) this repository on GitHub by clicking "Fork" on the top of the [GitHub repo](https://github.com/MolSSI/QCElemental).
- On your local machine,
  [clone](https://help.github.com/articles/cloning-a-repository/) your fork of QCElemental.
  ```sh
  git clone https://github.com/{YOUR-GITHUB-USERNAME}/QCElemental.git
  cd QCElemental
  ```
- Create a virtual environment into which you can install QCElemental. Make sure to use Python3.7+. Source this environment to use it for development.

  ```sh
  python -m venv env
  source env/bin/activate
  ```

- Install `QCElemental` into this virtual environment and then source the new command line tools. The command below installs QCElemental in "editable" mode--meaning all changes to the code will be instantly available to the python interpreter--and with all associated development tools.

  ```sh
  pip install -e '.[docs,tests,align,viz,lint]'
  source env/bin/activate
  ```

- Check your installation by running the tests.

  ```sh
  bash devtools/scripts/test.sh
  ```

- Look at the code coverage by opening the newly created `htmlcov/index.html` in your browser. This can help you evaluate the test coverage of new code that you add.

  ```sh
  open htmlcov/index.html
  ```

- Create a new branch for your work beginning with the word `feature-`:

  ```sh
  git checkout -b feature-my-cool-feature-name
  ```

- Install pre-commit hooks to have your code automatically formatted and linted when running `git commit`. If linting was required you'll need to run `git add .` again to stage the newly linted files and then try your commit again. Tests will run when you execute `git push`. If tests don't pass, the code will not push. Fix your tests/code, then commit and push again.

  ```sh
  pre-commit install
  pre-commit install --hook-type pre-push
  ```

- If you ever need to commit or push without running the hooks add `--no-verify` to your command, i.e.,

  ```sh
  git commit --no-verify -m 'My commit message.'
  ```

- Make changes to the code and commit your changes using git. You can lint your code (make sure it adheres to our code guidelines by standardizing code format, import ordering, spacing, etc.) without needing to deal with these details yourself by running:

  ```sh
  bash devtools/scripts/format.sh
  ```

- If you're providing a new feature, you must add test cases and documentation.

- Push to your repo. When you are ready to submit your changes open a [Pull Request](https://github.com/MolSSI/QCElemental/pulls) on the MolSSI/QCElemental repo from your fork into the QCElemental `master` branch. When you're ready to be considered for merging, check the "Ready to go" box on the PR page to let the QCElemental developers know that the changes are complete. The code will not be merged until this box is checked, the continuous integration returns check marks, and multiple core developers give "Approved" reviews.

## Additional Resources

- [General GitHub documentation](https://help.github.com/)
- [PR best practices](http://codeinthehole.com/writing/pull-requests-and-other-good-practices-for-teams-using-github/)
- [A guide to contributing to software packages](http://www.contribution-guide.org)
- [Thinkful PR example](http://www.thinkful.com/learn/github-pull-request-tutorial/#Time-to-Submit-Your-First-PR)
