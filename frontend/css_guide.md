# CSS, Explained Through Your Miwa Frontend

This guide doesn't add any new code. It only points at lines in your existing files.

---

## 0. What your project looks like right now

| File | Status | What it is |
|---|---|---|
| [index.css](file:///home/samar/miwa/frontend/src/index.css) | **Active.** Imported in [main.tsx](file:///home/samar/miwa/frontend/src/main.tsx#L4) | Mostly leftover styles from the Vite starter template |
| [global.css](file:///home/samar/miwa/frontend/src/styles/global.css) | **Inactive.** Nothing imports it | Your own design system (dark theme, buttons, ELO colors) |
| [App.css](file:///home/samar/miwa/frontend/src/App.css) | Empty | — |

> [!IMPORTANT]
> The header comment in [global.css](file:///home/samar/miwa/frontend/src/styles/global.css#L2) says "imported once in main.tsx", but that isn't true right now. A CSS file only has an effect if something imports it. That means none of your `.btn`, `.elo-gain`, or dark theme styles are being applied. What you see in the browser comes from `index.css`.

Two more things to know:
- None of your components use `className` yet. The only rules that reach your pages are the ones that target plain tags, such as `h1` and `body`.
- `index.css` styles things that don't exist in your app, like `#frontend`, `#social`, and `.counter`. Those came from the Vite demo page.

---

## 1. The basic idea: rules

CSS is a list of **rules**. Each rule says: *"find these elements, and give them these looks."*

A rule has two parts:
- **Selector**: which elements to target. Example: `body` in [global.css L40](file:///home/samar/miwa/frontend/src/styles/global.css#L40-L46).
- **Declarations**: a list of `property: value` pairs inside the braces. Example: `background-color` set to a dark color.

Most of CSS is learning two things: how to **select** elements, and which **properties** exist.

---

## 2. How CSS reaches the page

1. `index.html` contains an empty `<div id="root">`.
2. [main.tsx](file:///home/samar/miwa/frontend/src/main.tsx) renders React into that div and imports `index.css`.
3. Vite sees the import, bundles the CSS, and puts it into the page. In the production build it ends up in `dist/assets/index-….css`.
4. The browser checks every rule against every HTML element React produced.

So "is this CSS doing anything?" really asks two questions: *is the file imported?* and *does the selector match a real element?*

---

## 3. Selectors (the "who")

Here are the selector types your files use:

| Type | Example in your code | Matches |
|---|---|---|
| Element / tag | `body`, `h1`, `a`, `p` ([index.css L69-96](file:///home/samar/miwa/frontend/src/index.css#L69-L96)) | Every tag of that name |
| Class (`.`) | `.btn`, `.elo-gain` ([global.css](file:///home/samar/miwa/frontend/src/styles/global.css#L67-L90)) | Elements with `className="btn"` |
| ID (`#`) | `#root`, `#frontend` | The one element with that id |
| Universal (`*`) | the reset ([global.css L25-31](file:///home/samar/miwa/frontend/src/styles/global.css#L25-L31)) | Every element |
| Pseudo-element (`::`) | `::before`, `::after` | Invisible "virtual" boxes the browser can create before or after an element's content |
| Pseudo-class (`:`) | `:hover`, `:disabled`, `:focus-visible`, `:not(...)` | Elements in a certain **state** |
| `:root` | [both files, top](file:///home/samar/miwa/frontend/src/styles/global.css#L9) | The `<html>` element. This is where global variables usually go |
| Grouping (`,`) | `h1, h2` | "Apply to this **or** that" |
| Descendant (space) | `#social .button-icon` ([index.css L48](file:///home/samar/miwa/frontend/src/index.css#L48)) | `.button-icon` elements *inside* `#social` |

You can chain selectors. `.btn-primary:hover:not(:disabled)` ([global.css L102](file:///home/samar/miwa/frontend/src/styles/global.css#L102)) reads as: *a primary button, while the mouse is over it, but only if it isn't disabled.*

---

## 4. The cascade: who wins when rules conflict

The "C" in CSS stands for **Cascading**. When two rules set the same property on the same element, the browser decides the winner in this order:

1. **`!important`** wins over normal declarations. You use it in `.hidden` ([global.css L64](file:///home/samar/miwa/frontend/src/styles/global.css#L63-L65)) so that "hidden" can never be accidentally undone. Use it sparingly.
2. **Specificity**: the more precise selector wins. Roughly: **ID > class / pseudo-class > tag**. `#frontend` beats `.something`, which beats `div`.
3. **Source order**: if specificity is equal, the rule that comes **later** wins. That's why `.btn-primary` can override `.btn`'s transparent border: it comes after it and has the same specificity.

### Inheritance
Some properties automatically **pass down** to child elements. These are mostly text-related: `color`, `font-family`, `line-height`. That's why setting `color` and `font-family` once on `body` ([global.css L40-46](file:///home/samar/miwa/frontend/src/styles/global.css#L40-L46)) styles the text of your whole app.

Layout properties like `padding`, `border`, and `background` are **not** inherited.

Buttons are a known exception: browsers give them their own font. So `.btn` uses `font: inherit` ([L86](file:///home/samar/miwa/frontend/src/styles/global.css#L86)) to force buttons to use the page's font instead.

---

## 5. Custom properties (CSS variables) and theming

Anything starting with `--` is a **variable** you define yourself. `var(--name)` reads it.

- [global.css L9-22](file:///home/samar/miwa/frontend/src/styles/global.css#L9-L22) defines your **design tokens**: colors, radius, and font. Every other rule reuses these names instead of raw hex codes. To change your accent color everywhere, you'd edit only `--primary`.
- Variables follow the cascade, and they can be **redefined**. [index.css L33-46](file:///home/samar/miwa/frontend/src/index.css#L33-L46) shows a neat trick. It defines light colors first, then says "if the user's OS is in dark mode, redefine the same variables with dark values." Every rule that uses `var(--bg)` switches theme automatically. This is the standard way to do light/dark mode.

> [!WARNING]
> The two files use **different variable names** for the same ideas (`--bg` vs `--bg-dark`, `--text` vs `--text-main`). They also both set the page background and text color. If you import both, they'll fight, and the one loaded later wins. Pick one file as your source of truth. `global.css` is the one that matches your app.

---

## 6. The box model: every element is a box

From the inside out, each element is made of layers:

**content → padding → border → margin**

- **padding**: space *inside* the border. In `.btn` ([L83](file:///home/samar/miwa/frontend/src/styles/global.css#L83)) it's the breathing room around the button text.
- **border**: the visible edge.
- **margin**: space *outside* the border that pushes neighbors away.

**`box-sizing: border-box`** ([reset, L28](file:///home/samar/miwa/frontend/src/styles/global.css#L28)) changes what `width` means. With it, `width` includes the padding and border. Without it, padding gets added on top of the width, which surprises everyone. Almost every modern project turns it on globally.

The **reset** block also sets margin and padding to 0 on every element. Browsers add default spacing (for example, around `h1` and `p`), and the reset clears it so you start from a clean slate.

**Shorthands with several values** follow a pattern:
- 1 value = all four sides
- 2 values = top/bottom, then left/right. Example: `margin: 32px 0` on `h1` ([index.css L79](file:///home/samar/miwa/frontend/src/index.css#L79)).
- 4 values = top, right, bottom, left (clockwise)

---

## 7. Layout: `display` and Flexbox

`display` decides how a box behaves:
- `block`: takes the full width and starts on a new line (`div`, `p`, `h1`).
- `inline`: flows inside text like a word (`a`, `span`).
- `none`: removed entirely. This is what `.hidden` does.
- `flex` / `inline-flex`: turns the element into a **flex container**, so it controls how its children are arranged.

**Flexbox** is your main layout tool for rows and columns. In `.btn` ([L79-82](file:///home/samar/miwa/frontend/src/styles/global.css#L79-L82)):
- `display: inline-flex`: the button sits inline, but arranges its own children (icon + text) with flex.
- `align-items: center`: centers the children on the **cross axis** (vertically, in a row).
- `justify-content: center`: centers them on the **main axis** (horizontally, in a row).
- `gap`: space between the children.

`flex-direction: column` ([index.css L61](file:///home/samar/miwa/frontend/src/index.css#L61)) turns the main axis vertical, so the children stack top to bottom.

**Centering a page column**: `width: 1126px` + `max-width: 100%` + `margin: 0 auto` ([index.css L54-56](file:///home/samar/miwa/frontend/src/index.css#L54-L56)). This means "be 1126px wide, but never wider than the screen, and split the leftover space equally on the left and right."

The other big layout tool is **CSS Grid**, for two-dimensional layouts like the "stats grid" mentioned in your global.css comment. You'll likely need it for the leaderboard and profile pages.

---

## 8. Units and values

| Unit | Meaning | Where you use it |
|---|---|---|
| `px` | Fixed pixels | borders, font sizes in index.css |
| `rem` | Multiple of the root font size. Scales if the user enlarges text | `.btn` padding and gap |
| `%` | Relative to the parent (or to the font size, for line-height) | `max-width: 100%`, `145%` |
| unitless | Line-height as a multiplier of the font size | `line-height: 1.5` |
| `svh` | % of the visible screen height. Handles mobile browser toolbars properly | `min-height: 100svh` |
| `s` | Seconds, for animations | `0.15s` transition |

Colors: `#6366f1` is hex. `rgba(170, 59, 255, 0.1)` is red, green, blue plus **alpha** (transparency, from 0 to 1).

---

## 9. Responsive design: media queries

`@media (max-width: 1024px) { … }` means *"apply these rules only when the screen is 1024px wide or narrower."* That's how `h1` shrinks from 56px to 36px on smaller screens ([index.css L76-84](file:///home/samar/miwa/frontend/src/index.css#L76-L84)).

Notice that in index.css the media query is written **inside** the `h1` rule. That's **native CSS nesting**, a fairly new feature. The more traditional style puts media queries at the top level, as in [index.css L33](file:///home/samar/miwa/frontend/src/index.css#L33). Both work in modern browsers.

Media queries can also respond to **user preferences**, not just screen size:
- `prefers-color-scheme: dark`: the user's OS is in dark mode.
- `prefers-reduced-motion: reduce` ([global.css L125-129](file:///home/samar/miwa/frontend/src/styles/global.css#L125-L129)): the user asked for less animation, so you turn off transitions. This is good accessibility practice.

---

## 10. Interactivity and feedback

- **`transition`** ([L89](file:///home/samar/miwa/frontend/src/styles/global.css#L89)): when `background-color` changes (for example on hover), it fades over 0.15s instead of snapping.
- **`cursor`**: `pointer` (hand) for clickable things, `not-allowed` for disabled ones.
- **`opacity`**: 0.5 makes disabled buttons look faded.
- **`filter`**: visual effects like `brightness(0.9)`, which darkens the danger button on hover.
- **`:focus-visible`** ([L57-60](file:///home/samar/miwa/frontend/src/styles/global.css#L57-L60)): shows an outline when someone moves through the page with the keyboard, but not when they click with the mouse. Important for accessibility.

---

## 11. How to organize CSS (the architecture in your global.css comment)

Your `global.css` header describes a good plan:

1. **Global file**: only things shared by the whole app: tokens, reset, base tag styles, utilities, buttons.
2. **CSS Modules** (`Navbar.module.css` next to `Navbar.tsx`): styles for one component.

**Why CSS Modules?** Plain CSS is **global**: a `.title` class in one file affects every `.title` in the app. CSS Modules make Vite rename each class to something unique behind the scenes, so component styles can't leak into or collide with each other. Vite supports this out of the box. Any file ending in `.module.css` gets this behavior.

Two class patterns already in your file:
- **Utility classes**: small, single-purpose classes like `.hidden`, `.elo-gain`, and `.elo-loss`. You turn them on and off from React based on state (for example, a positive or negative ELO change).
- **Base + modifier**: `.btn` holds what all buttons share, and `.btn-primary`, `.btn-secondary`, and `.btn-danger` only add the differences. An element gets **both** classes at once. This avoids repeating code.

---

## 12. Connecting CSS to React

- In React you write `className` instead of HTML's `class` attribute. The value is a string with one or more class names separated by spaces.
- With a CSS Module, you import the module as an object and read class names from it, instead of typing plain strings.
- Right now your pages (for example [Home.tsx](file:///home/samar/miwa/frontend/src/pages/Home.tsx)) render bare tags with no classes. So only tag selectors like `h1` from index.css are affecting them.

---

## 13. How to learn by poking at it

Open your app in the browser and press **F12**, then go to the **Elements / Inspector** tab:
- Click any element to see **every rule that applies** to it, and which file and line each one comes from.
- Declarations that lost the cascade are shown **crossed out**. This is the fastest way to understand specificity in practice.
- The **Computed** tab shows the final values and a diagram of the box model (margin/border/padding).
- You can edit values live to experiment without touching your files.

---

## 14. Decisions you'll want to make (when you're ready to write code)

1. Import `global.css` in `main.tsx`.
2. Delete or empty `index.css`. Most of it is Vite demo leftovers, and it conflicts with your theme.
3. Decide on dark-only (as global.css is now) or light + dark (using the variable-redefinition trick from index.css).
4. Start adding `className` to components, and create `*.module.css` files for page-specific styles.
