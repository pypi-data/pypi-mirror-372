{
    "name": "Odoo CRON runner patch",
    "summary": """Patch the cron runner to avoid connection reset if database is behind a proxy""",
    "author": "Mangono",
    "website": "https://mangono.fr",
    "category": "Uncategorized",
    "version": "0.0.1",
    "depends": ["base"],
    "auto_install": False,
    "data": [],
    "installable": False,
    "license": "AGPL-3",
    "post_load": "post_load_module",
}
