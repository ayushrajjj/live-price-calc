"""Streamlit pages wrapper to expose the admin UI as a multipage app page.

This file simply calls admin.main() so you can keep a single deployment
and access the admin UI from the Streamlit page selector.
"""
from admin import main as admin_main

# Call the admin UI. admin.main() already calls set_page_config when run.
admin_main()
