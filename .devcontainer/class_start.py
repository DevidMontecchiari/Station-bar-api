"""Show the class-start reminder when a Codespace or dev container attaches.

This hook only prints guidance. It does not run Git or change any files.
"""


def main():
    print("""
STATION BAR | Before continuing with the next class

Reopening this Codespace does not update your exercise files.

1. Save your files and check Source Control for your own changes.
2. Fetch to check for updates. If you use a fork, sync it with the teaching
   repository on GitHub first. Fetching a fork does not sync its source.
3. Review incoming changes before pulling. Keep your own work; if histories
   diverge or you see conflicts, ask for help before integrating updates.

Open docs/updating-your-codespace.md for the steps, then README.md for
this class's activity and the JSON / SQLite folder and port comparison.

This reminder does not pull or push. The editor can fetch in the background.
""")


if __name__ == "__main__":
    main()
