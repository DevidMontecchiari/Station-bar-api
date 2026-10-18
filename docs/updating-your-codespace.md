# Before continuing in an existing Codespace

[Repository overview](../README.md) > **Get the latest teaching material**

Reopening your Codespace resumes your working copy; it does not download the latest exercises. Check for teaching updates before each class. You can continue using the same Codespace and keep your previous work.

## Check, update, then continue

1. **Save your open files.** Open **Source Control** and inspect your changes. Commit work you want to keep before integrating updates. A commit records your work locally; it does not automatically upload it to GitHub.
2. **If you work in a fork:** open your fork on GitHub and use **Sync fork > Update branch** to bring in the lecturer's changes. If GitHub reports conflicts, keep your work and ask for help resolving them. Fetching from your fork alone cannot discover teaching updates that have not reached the fork.
3. **Fetch:** in Source Control, choose **... > Fetch**. Fetch updates Git's information about the remote repository without replacing your working files. Inspect the incoming commits in the Source Control graph. This devcontainer enables background fetch from the configured default remote (normally `origin`), so the editor can also refresh that information while you work.
4. **Pull after reviewing the changes.** For a clean working tree on a branch that tracks the corresponding remote branch, run the commands below from the repository root. The second command only integrates an update when Git can fast-forward your branch. If it refuses because of local work or divergent history, keep your changes and ask for help; do not reset your branch to force the update.

```sh
git status
git pull --ff-only
```

5. **Return to [the current class in the README](../README.md#current-class-persistence-and-databases-exercise-4).** Check which folder and port to use. Read any setup instructions for a new example before starting it. Earlier exercises remain available.

**Continuing with the ORM example?** Pulling its files or forwarding port8002 does not install the packages. Follow the [separate ORM environment setup](../extensions/orm/README.md#start-the-orm-example-in-part-d), then launch with `extensions/orm/.venv/bin/python extensions/orm/run.py --host 0.0.0.0` from the repository root. A normal Codespace rebuild still prepares the JSON dependencies; the optional ORM setup remains separate.

A clean working tree can still contain your own commits. If both you and the lecturer changed the history, combining the work may require a merge; `--ff-only` deliberately stops for that case. For a project you have adapted substantially, review and transfer selected changes rather than replacing your implementation with the reference application.

## Activate the new startup reminder once

If you created your Codespace before this reminder was added:

1. Get these changes using the steps above.
2. Save your work, open the Command Palette (**F1**) and run **Codespaces: Rebuild Container**. A normal rebuild is sufficient to apply the updated devcontainer configuration.
3. After connecting again, look for the terminal message **STATION BAR | Before continuing with the next class**. It is shown by the `postAttachCommand` each time a client attaches.

A rebuild applies environment settings; it does **not** pull repository changes. Files under the Codespace workspace survive a rebuild. If you installed tools elsewhere inside the container, you may need to install them again.

New Codespaces created from a repository containing this update already use the configuration. If the reminder terminal is no longer visible, reopen this guide from the README; you can also display the reminder yourself with `python .devcontainer/class_start.py` from the repository root.

## What the Git actions mean

| Action | What changes |
| --- | --- |
| **Fetch** | Refreshes information about remote commits; your working files stay as they are. |
| **Pull** | Fetches and integrates remote commits into your current branch and working files. |
| **Push** | Uploads your local commits to a remote repository where you have permission. |
| **Sync Changes** in VS Code | May both pull and push; use Fetch when you only want to check for updates. |

The startup reminder only prints guidance. Background fetch does not automatically pull, merge or push.

References: [VS Code: working with remotes](https://code.visualstudio.com/docs/sourcecontrol/repos-remotes), [GitHub: syncing a fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork), [GitHub: rebuilding a Codespace](https://docs.github.com/en/codespaces/developing-in-a-codespace/rebuilding-the-container-in-a-codespace).
