# upwork-helper

Offline helper that reads a job post from a `.txt` file and prints a fit
checklist plus a draft proposal built from a template. Template only: no
Upwork API, no network calls, and it never sends anything. Review and edit
every draft yourself.

Python 3 standard library only.

## Usage

    python3 proposal_helper.py samples/job_data_cleanup.txt
    python3 proposal_helper.py samples/job_quick_bot.txt --name "Your Name" --out draft.txt
    python3 proposal_helper.py job.txt --template my_template.txt

Job post format: `Title:`, `Client:`, `Budget:`, `Skills:` (comma list) header
lines, then `Description:` followed by free text. Custom templates use
`$client`, `$title`, `$title_line`, `$summary`, `$matched_skills`, `$budget_line`, `$freelancer`.

The job post is treated as data. Red flags are checked in the title and the
description, including instructions planted for an assistant and contact
details or links. A title with a red flag is not quoted (`$title` becomes
"your job post"). The draft never copies sentences from the post: `$summary`
is a placeholder for you to fill in your own words. A score under 50 adds a
"consider not applying" note. For the Blade Works 1-5 skill, see
`skills/upwork-proposal/`.

The `samples/` job posts and businesses are made up.

## Tests

    cd upwork-helper && python3 -m unittest
