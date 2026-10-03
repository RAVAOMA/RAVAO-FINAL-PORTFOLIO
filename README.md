# Mark Angelo Ravao — Personal Portfolio

This is the same Django portfolio repository used for the earlier quizzes.
Quiz 5 and 6 add an owner-only sign-in page, a dashboard, and reusable tech
stacks. Public projects, contact inquiries, and testimonials remain available.

**Repository:** https://github.com/RAVAOMA/RAVAO-FINAL-PORTFOLIO

## Requirements

- **Python 3.12** (used by the automated checks on Windows, macOS, and Linux).
  Django 6 requires Python 3.12 or newer; Python 3.10/3.11 will not work.
- Git to clone the repository; VS Code is optional.
- Internet access for the initial dependency installation.

Install Python from [python.org](https://www.python.org/downloads/) and Git from
[git-scm.com](https://git-scm.com/downloads) if needed. On Windows, enable the
Python installer's PATH option.

The database, virtual environment, `.env`, and generated static files are
intentionally excluded from Git. Each clone creates its own database and admin
account. All migrations are committed: use **`migrate`**, not `makemigrations`,
to set up this project. There is no default username or password.

## Fresh installation — macOS / Linux

Open Terminal, choose the parent folder where you want the project, then run:

```bash
git clone https://github.com/RAVAOMA/RAVAO-FINAL-PORTFOLIO.git
cd RAVAO-FINAL-PORTFOLIO
python3.12 --version
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/setup_env.py
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Enter your own username, email, and password when `createsuperuser` asks.
Password input is hidden. If `python3.12` is unavailable but `python3 --version`
shows 3.12, use `python3` for the version check and virtual-environment command.
All remaining commands use `python` inside the activated environment.

## Fresh installation — Windows PowerShell

Open PowerShell, choose the parent folder where you want the project, then run:

```powershell
git clone https://github.com/RAVAOMA/RAVAO-FINAL-PORTFOLIO.git
cd RAVAO-FINAL-PORTFOLIO
py -3.12 --version
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/setup_env.py
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

If PowerShell blocks activation, you can use the environment's Python directly
without changing your execution policy:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/setup_env.py
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

If the `py` launcher is unavailable, use `python` for the first two Python
commands after checking that `python --version` is 3.12 or newer.

## Open and use the project

1. Open **http://127.0.0.1:8000/** while the development server is running.
2. Use **Owner sign-in** at **http://127.0.0.1:8000/sign-in/**. Enter the superuser
   account you created. Successful sign-in redirects to **`/dashboard`**.
3. Choose **Tech stacks → Create tech stack**. Add a technology such as Python.
   Add another, such as Django, to try a project with multiple technologies.
4. Choose **Projects → Create project**. Fill in the project name, description,
   technology selection, and a complete project URL, then publish it.
5. Visit the public homepage or project list. Your saved project and its
   technologies appear immediately, with no HTML changes needed.
6. Visitors can submit the **Contact** form and **Leave a Testimonial** form
   without signing in. Testimonials have a list and individual detail pages.
7. Use **Sign out** in the dashboard when finished.

The form uses **real radio buttons**, populated from the `TechStack` table.
Each group selects one stack. **Add another tech stack** adds another radio
group, so a project can use several stacks while meeting the radio-button
requirement. JavaScript enables additional groups; one stack can still be
selected without JavaScript. Existing stacks are reused across projects.
Duplicate names such as `Python` and `python` are rejected.

An active **superuser** is required for owner sign-in and all dashboard/create
routes. Regular users and staff-only users cannot use these pages, including
by sending a direct POST. There is intentionally no public registration page.
Anonymous visitors are redirected to sign-in; authenticated non-owners receive
403. Logout uses a CSRF-protected POST.

A fresh database has no projects or tech stacks; the empty states are expected.
The homepage still displays Mark's name and a short introduction. To customize
the full profile, sign in to **http://127.0.0.1:8000/admin/** and add one
**Personal information** record. The homepage uses the first such record.
The admin also lets the owner manage inquiries, testimonials, and existing data.
Contact submissions are saved in the database; this project does not send email.

### Open in VS Code and restart later

Use **File → Open Folder → RAVAO-FINAL-PORTFOLIO**. If the `code` command is
installed, `code .` opens the current folder. Select `.venv` as the Python
interpreter. The VS Code terminal must be in the folder containing `manage.py`.

For future sessions, open that folder, activate `.venv`, and run:

```bash
python manage.py runserver
```

Stop the server with **Ctrl+C**. Use `deactivate` to leave the virtual environment.
You do not need to reinstall packages or recreate the superuser every time.

## Environment variables

`python scripts/setup_env.py` copies `.env.example` into `.env` and generates a
unique secret using Python's `secrets` module. It never prints the secret and
never overwrites an existing `.env`. Settings load this file relative to the
project root, so PythonAnywhere's WSGI process can find it too. Existing process
environment variables take precedence over `.env`.

| Variable | Local value / purpose | PythonAnywhere value |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Generated private random secret; required | A separately generated private secret on the server |
| `DJANGO_DEBUG` | `True` for local development | `False` |
| `DJANGO_ALLOWED_HOSTS` | `127.0.0.1,localhost` | Your exact hostname, with no scheme or path |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Empty for the local same-origin forms | `https://YOUR_USERNAME.pythonanywhere.com` |
| `DJANGO_SECURE_SSL_REDIRECT` | `False` for local HTTP | `True` |

Separate multiple hosts/origins with commas. Never use `*` for production
hosts. Production settings use secure session/CSRF cookies, HTTPS redirection,
and a one-hour HSTS policy. PythonAnywhere supplies the trusted forwarded-HTTPS
header used by the settings. `.env.example` contains placeholders only. Do not
commit `.env`, reuse a secret from earlier repository history, or share passwords.

## Pages and implementation

| Page | URL | Access / implementation |
| --- | --- | --- |
| Portfolio | `/` | Public FBV; database projects and shared stacks |
| Public projects | `/projects/` | Public list; links to `/projects/<id>/` details |
| Owner sign-in | `/sign-in/` | AuthenticationForm restricted to active superusers |
| Dashboard | `/dashboard` | Owner only; summary and recent projects |
| Project table | `/dashboard/projects/` | Owner only; name, description truncated to 50 characters, comma-separated stacks, clickable link |
| Tech stack table | `/dashboard/tech-stacks/` | Owner only; name, projects using it, creation date |
| Create project | `/dashboard/projects/create/` | Owner-only ModelForm and function-based create view |
| Earlier create URL | `/projects/create/` | Same protected project create view |
| Create tech stack | `/dashboard/tech-stacks/create/` | Owner-only ModelForm and function-based create view |
| Contact | `/inquiry/` | Public explicit HTML form; FBV validates and saves `Inquiry` |
| Testimonials | `/testimonies/` | Public class-based `ListView` |
| Create testimony | `/testimonies/create/` | Public Django ModelForm and function-based create view |
| Testimony detail | `/testimonies/<id>/` | Public function-based detail view |
| Django admin | `/admin/` | Standard Django administration |

`Project.tech_stacks` is a many-to-many relationship to
`TechStack(name, created_at)`. A database constraint enforces case-insensitive
unique names. Project forms require every field and validate selected stack
IDs against the database. The homepage, lists, and detail views read this
relationship directly.

Migration `0003_reusable_tech_stacks` preserves existing projects and converts
the old text field into shared objects. Commas, semicolons, pipes, and newlines
separate legacy names; old whitespace-only lists are split into tokens. New
forms support multiword names normally. Back up any existing database before
upgrading. When upgrading an older clone, keep your local database backup
outside the repository: Git's removal of the previously tracked database may
remove that file during the update. Restore your backup as `db.sqlite3`, then
run `migrate`. Do not commit the restored database.

## Checks

After completing local setup, run:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test website --verbosity 2
python manage.py collectstatic --noinput
```

`makemigrations --check --dry-run` only checks for missing migration files; it
does not create migrations or replace the setup step `migrate`.

The test suite covers sign-in restrictions, direct-route permissions, CSRF,
required fields, invalid URLs/stack IDs, radio choices, duplicate stacks,
many-to-many reuse, table contents, public portfolio updates, contact forms,
testimonials, and upgrading a database containing older projects. Pull requests
run fresh migrations and checks on **Ubuntu, Windows, and macOS with Python
3.12**. Native checkout also checks that the file tree is compatible with each OS.

## Deploy on PythonAnywhere

Use the [official existing-Django deployment guide](https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/)
alongside these project-specific steps. Replace every `YOUR_USERNAME` below
with your actual PythonAnywhere username. If your account is on the EU site,
use the exact hostname shown on its Web tab instead of the `.com` examples.

### 1. Clone and create the server environment

Sign in to PythonAnywhere and open a **Bash console**. This project uses Python
3.12. Check `python3.12 --version`. If it is unavailable, consult
[supported Python versions](https://help.pythonanywhere.com/pages/PythonVersions)
and your Account → System image settings; `innit` supports Python 3.12.
Choose a supported system image and reopen the console before continuing.

```bash
git clone https://github.com/RAVAOMA/RAVAO-FINAL-PORTFOLIO.git
cd RAVAO-FINAL-PORTFOLIO
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/setup_env.py
```

In the **Files** tab, open
`/home/YOUR_USERNAME/RAVAO-FINAL-PORTFOLIO/.env`. Keep the generated secret and
set the other values as follows:

```dotenv
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=YOUR_USERNAME.pythonanywhere.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://YOUR_USERNAME.pythonanywhere.com
DJANGO_SECURE_SSL_REDIRECT=True
```

Back in the activated Bash console:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py check --deploy
```

Use your own production admin password. Do not put it in Git, the README, or
the submission PDF. The database is created on PythonAnywhere and persists
there independently of your local database.

### 2. Configure the Web app

In **Web → Add a new web app**, choose **Manual configuration → Python 3.12**.
Use the same Python version as the virtual environment. Set:

| Web setting | Value |
| --- | --- |
| Source code | `/home/YOUR_USERNAME/RAVAO-FINAL-PORTFOLIO` |
| Working directory | `/home/YOUR_USERNAME/RAVAO-FINAL-PORTFOLIO` |
| Virtualenv | `/home/YOUR_USERNAME/RAVAO-FINAL-PORTFOLIO/.venv` |
| Static files URL | `/static/` |
| Static files directory | `/home/YOUR_USERNAME/RAVAO-FINAL-PORTFOLIO/staticfiles` |

Open the **WSGI configuration file linked in the Web tab** (usually under
`/var/www/`), replace its contents with the following, and save:

```python
import os
import sys

project_path = '/home/YOUR_USERNAME/RAVAO-FINAL-PORTFOLIO'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'portfolio.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

The WSGI file in PythonAnywhere's Web tab is the file to edit for hosting.
`portfolio/settings.py` loads the project's `.env`; no credentials belong in
the WSGI file. Click **Reload** in the Web tab, then open the HTTPS URL shown
there. Do not run `manage.py runserver` to host the production website.

### 3. Verify the deployed website

- Open the homepage, Contact, Testimonials, and a project detail page. Confirm
  CSS, profile images, and Download CV load. A fresh database initially has no
  project detail page until you create a project.
- In a signed-out/private window, open `/dashboard` and both create URLs:
  they must redirect to owner sign-in.
- Sign in with your superuser and confirm the destination is `/dashboard`.
- Add two stacks. Try an empty name and a duplicate with different casing;
  neither should save.
- Try an empty project and an invalid link. Confirm errors appear. Create a
  valid project with two radio groups; verify both tables and the public
  homepage show it. Reuse a stack in a second project to check shared usage.
- Submit a contact inquiry and confirm it in Django admin. Submit a clearly
  identified test testimonial and verify its public list/detail flow. Remove
  disposable test records through admin after checking them.
- Verify a regular/staff-only account cannot sign in on `/sign-in/`, even if
  that account exists. The automated tests cover these cases without creating
  permanent test accounts on the live site.
- Sign out and confirm the dashboard is protected again.

### Deploy future updates

Merge the changes through a PR **before** updating the live site. Back up the
live database outside the repository, then in a Bash console run:

```bash
cd ~/RAVAO-FINAL-PORTFOLIO
source .venv/bin/activate
git pull --ff-only origin main
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
```

Reload the Web app and repeat the functional checks. Keep the existing `.env`
and database. Review your PythonAnywhere Web tab for any account-specific
renewal/expiry requirement so the site remains available for grading.

## Troubleshooting

| Problem | What to check |
| --- | --- |
| `No module named django` | Activate `.venv`, then install `requirements.txt` with that environment's Python. |
| Django cannot be installed | Check Python is 3.12 or newer; PythonAnywhere's Web app and `.venv` must use the same version. |
| `Set DJANGO_SECRET_KEY` | Run `python scripts/setup_env.py`; if you copied the example manually, replace its placeholder with a private generated secret. |
| `no such table` | Run `python manage.py migrate` in the folder containing `manage.py`. |
| Owner sign-in fails | Use an active superuser made with `createsuperuser`; regular and staff-only accounts are intentionally rejected. Reset a forgotten local password with `python manage.py changepassword YOUR_USERNAME`. |
| No projects or stack choices | Fresh databases are empty. Add tech stacks, then projects through the dashboard. |
| `DisallowedHost` / HTTP 400 | Set the exact hostname in `DJANGO_ALLOWED_HOSTS` (no `https://`), then restart/reload. |
| CSRF error on PythonAnywhere | Use HTTPS, set the matching trusted origin with `https://`, reload, and refresh the form before submitting again. |
| Local browser redirects to HTTPS | Local `.env` needs `DJANGO_DEBUG=True` and `DJANGO_SECURE_SSL_REDIRECT=False`; restart the server. |
| PythonAnywhere page is unstyled | Run `collectstatic`, check the `/static/` mapping above, then reload. |
| PythonAnywhere shows a server error | Open its Web tab error log; check virtualenv, WSGI path, `.env`, and migrations. Keep `DEBUG=False` on the public site. |

## Course workflow and submission

Continue using this repository. Make new changes on a separate branch, write
descriptive commits, open a pull request, review the checks, and merge through
the PR. Never push directly to `main` or `master`, and merge before the deadline.

The Quiz 5/6 submission file is **`RAVAO_Q5_Q6.pdf`**. It must contain clickable
links to this repository and the **actual working deployed URL** shown in your
PythonAnywhere Web tab. Submit through the course's required submission area,
not email. A localhost URL or a screenshot does not meet the submission rule.
