# Personal Portfolio

A Django portfolio for Mark Angelo Ravao, with personal information, projects,
contact inquiries, and testimonials.

## Run locally

Use Python 3.12, the version used by the automated checks.

1. Create a virtual environment: `python -m venv .venv`.
2. Activate it:
   - macOS/Linux: `source .venv/bin/activate`
   - Windows PowerShell: `.venv\Scripts\Activate.ps1`
3. Install dependencies: `python -m pip install -r requirements.txt`.
4. Apply database migrations: `python manage.py migrate`.
5. Start the development server: `python manage.py runserver`.
6. Open http://127.0.0.1:8000/.

On macOS/Linux, use `python3` for step 1 if `python` is unavailable.

The homepage displays projects stored in the database. Use **Add Project** to
create a project, then return home to see it. If the database has no projects,
the homepage displays an empty state.

To manage personal information and other records through Django admin, run
`python manage.py createsuperuser`, then open `/admin/`.

## Quiz 3 pages

| Page | URL | Implementation |
| --- | --- | --- |
| Homepage | `/` | Function-based view; projects come from the Project model |
| Projects | `/projects/` | Function-based list and detail views |
| Add Project | `/projects/create/` | ProjectForm with a function-based create view |
| Contact | `/inquiry/` | Explicit HTML inputs; InquiryForm validates the POST in a function-based view and saves Inquiry |
| Testimonials | `/testimonies/` | ListView |
| Leave a Testimonial | `/testimonies/create/` | TestimonyForm with a function-based create view |
| Testimonial detail | `/testimonies/<id>/` | Function-based view; unknown IDs return 404 |

## Check the project

Run:

```sh
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test website --verbosity 2
```

Pull requests targeting `quiz3`, `development`, or `main` run these checks on
Ubuntu and Windows. Windows checkout also checks that the current file tree
can be downloaded without the invalid-filename error.

Keep changes on a separate branch and merge through pull requests, following
the course workflow.
