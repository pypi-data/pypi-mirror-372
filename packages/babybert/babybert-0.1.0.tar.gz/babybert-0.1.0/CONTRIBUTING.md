# Contributing to BabyBERT
Thanks for considering making a contribution to BabyBERT! Any help on this project is greatly welcomed. Feel free to open up an issue if you see a bug to fix, or a PR if you'd like to implement a new feature.

## Making code contributions
If you'd like to make a code contribution to BabyBERT, please follow these steps:
### Creating a development branch
Begin by [making your own fork](https://github.com/dross20/babybert/fork) of this repository. This is where you'll make your code changes.

Then, clone the fork to your personal machine:
```sh
git clone https://github.com/<your-github-username>/babybert
```

Next, navigate into the newly cloned directory and open up a branch in which to make your code changes. Pick a descriptive title!
```sh
cd babybert
git checkout -b <your-branch-name>
```
### Installing the development build
Now that you've created your own branch, install the development build of BabyBERT.
```sh
pip install -e ".[dev]"
```
### Committing your changes
After you've made your changes to the codebase, run the following command. This command ensures that **a)** your code follows the code style of the repository and **b)** your code doesn't break any existing unit tests.
```sh
make all
```
It's possible that you'll need to make some changes to your code before the command passes (eg. shorten lines that are too long).

Once the `make all` commands passes, you're ready to stage, commit, and push your changes!
### Creating a new pull request
Once you've pushed your changes, navigate to your forked repository and click "Pull Request" to create a new pull request. Make sure to leave a helpful description that outlines the changes you've made. You can also tag me too (by including "@dross20" in your description) so that I'll see your PR sooner!
