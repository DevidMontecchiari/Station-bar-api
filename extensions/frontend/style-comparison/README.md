# Station Bar: custom CSS and Bootstrap

These are two prepared versions of the same static prototype. Both use the same
fictional menu, shared JavaScript, labelled fields and simulated result. They do
not send an order to the API or save data. Reload clears the result.

## Open the comparison

Extract the whole ZIP, then open **index.html** in your browser. Open the two
versions in separate tabs. All styles, images, data and scripts are included:
no installation, internet connection or generation prompt is needed.

Do not open files from inside the ZIP. Keep the folder structure intact.

## A short walkthrough

1. Compare the inputs, menu, buttons and spacing in the two prepared pages.
2. Submit the same order in both. The simulated message is the same.
3. Resize both pages below 768px: the menu moves below the form.
4. Inspect custom/index.html with custom/styles.css, then bootstrap/index.html.
   Find form-control, form-select, btn btn-primary, row and col-12 col-md-6.
5. Open shared/app.js: both HTML files load the same behaviour. Reload to show
   that a different appearance does not add persistence or business rules.

This is a prepared styling comparison, not another mandatory exercise. It can be
shown directly after the Bootstrap examples; the API/Jinja comparison remains
part of the later class demonstration.

| Responsibility | Custom CSS | Bootstrap CSS |
|---|---|---|
| Layout | .workspace grid and our media query | row + col-12 col-md-6 |
| Input/select appearance | input/select rules in styles.css | form-control/form-select |
| Button appearance | button rule in styles.css | btn btn-primary w-100 |
| Shared identity | shared/brand.css and the existing illustration | Same files |
| Interaction and menu | shared/app.js and shared/menu-data.js | Same files |

The Bootstrap version uses **Bootstrap 5.3.8 CSS only**, not Bootstrap Studio.
No JavaScript widgets are used, so Bootstrap's JS bundle is unnecessary here.
The custom version has CSS; “without Bootstrap” does not mean “unstyled”.

## Codespaces or an HTTP preview

From the Station Bar repository root:

```sh
python -m http.server 8090 --bind 0.0.0.0 --directory extensions/frontend/style-comparison
```

Open port **8090** in the Codespaces **Ports** tab, keeping it private. Add the
port manually if it is not listed. Opening HTML in the editor shows its source.
No backend, optional frontend dependencies or container rebuild is needed.
Stop the server with Ctrl+C. This uses Python's standard library only.

For an extracted standalone folder, run the following from that folder:

```sh
python -m http.server 8090 --bind 127.0.0.1
```

Open http://127.0.0.1:8090 locally. Directly opening index.html also works.
Hosted Codespaces authentication/forwarding still needs a rehearsal; local
file and HTTP behaviour are checked separately in the teaching workspace.

## Files and sources

- custom/: readable HTML and our layout/control CSS.
- bootstrap/: readable HTML using Bootstrap classes.
- shared/: common behaviour, sample menu and visual identity.
- assets/: the existing Station Bar illustration.
- screenshots/: actual desktop and narrow-screen renders of these files.
- vendor/bootstrap/: pinned CSS, source map and the original MIT licence.
- SOURCES.json: asset provenance, versions and hashes.

Menu values come from the existing static/menu.json fixture. Here they are
packaged as a small ordinary script so double-click use needs no fetch/server.
The existing static, API-client and Jinja examples are unchanged.

Official references: [Bootstrap download](https://getbootstrap.com/docs/5.3/getting-started/download/),
[forms](https://getbootstrap.com/docs/5.3/forms/overview/),
[grid](https://getbootstrap.com/docs/5.3/layout/grid/).
